"""Holdout evaluation of routing precision/recall per agent with confusion matrix."""

import sys
import time
from pathlib import Path
from typing import List, Tuple, Dict
from collections import defaultdict
import json

sys.path.insert(0, str(Path(__file__).parent))

from router.router_decider import (
    SemanticSimilarityClassifier,
    PerformanceWeightedClassifier,
    LLMMetaClassifier
)
from training_data_method2 import train_performance_classifier
from stats_agent.stats_agent_complex import run_statistics_agent_structured_timed
from data_agent.data_agent_complex import run_data_eng_agent_structured_timed
from ML_agent.ML_agent_complex import run_ml_agent_structured_timed
from visual_agent.visual_agent_complex import run_viz_agent_structured_timed
from queries import TRAINING_QUERIES
from queries2 import ROUTING_DATASET_200


# Split queries2 into smaller holdout set
HOLDOUT_SIZE = 50  # Use 50 queries as holdout for calibration


def split_holdout_set(dataset: List[Tuple[str, str]], holdout_size: int = 50) -> Tuple[List, List]:
    holdout = dataset[:holdout_size]
    validation = dataset[holdout_size:]
    return holdout, validation


def run_routing_method(classifier, query: str, expected_agent: str) -> Tuple[str, bool]:
    try:
        # All classifiers have a classify method that returns (agent, confidence)
        predicted, confidence = classifier.classify(query)
        correct = (predicted == expected_agent)
        return predicted, correct
    except Exception as e:
        return "ERROR", False


def compute_metrics(confusion_pairs: List[Tuple[str, str]], agent_names: List[str]) -> Dict:
    """Compute precision, recall, F1 for each agent from (actual, predicted) pairs."""
    metrics = {}
    
    for agent in agent_names:
        # True Positives: correctly predicted as this agent
        tp = sum(1 for actual, pred in confusion_pairs if actual == agent and pred == agent)
        
        # False Positives: incorrectly predicted as this agent (we said agent but it wasn't)
        fp = sum(1 for actual, pred in confusion_pairs if actual != agent and pred == agent)
        
        # False Negatives: should be this agent but predicted differently (we missed it)
        fn = sum(1 for actual, pred in confusion_pairs if actual == agent and pred != agent)
        
        # Precision: of queries we said were this agent, how many actually were?
        # TP / (TP + FP)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        
        # Recall: of all queries that should be this agent, how many did we get right?
        # TP / (TP + FN)
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        
        # F1: harmonic mean of precision and recall
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        metrics[agent] = {
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "precision": precision,
            "recall": recall,
            "f1": f1,
        }
    
    return metrics


def build_confusion_matrix(predictions: List[Tuple[str, str]], agent_names: List[str]) -> Dict:
    matrix = {agent: {other: 0 for other in agent_names} for agent in agent_names}
    
    for actual, predicted in predictions:
        if actual in matrix and predicted in matrix[actual]:
            matrix[actual][predicted] += 1
    
    return matrix


def print_metrics_table(metrics: Dict[str, Dict], method_name: str):
    print(f"\n{method_name}")
    print(f"{'Agent':<20} {'Precision':<12} {'Recall':<12} {'F1':<12} {'TP/FP/FN':<20}")
    print("-" * 76)
    
    for agent in ["DataEngAgent", "StatisticsAgent", "MLAgent", "VizAgent"]:
        if agent in metrics:
            m = metrics[agent]
            precision = m["precision"]
            recall = m["recall"]
            f1 = m["f1"]
            tp_fp_fn = f"{m['tp']}/{m['fp']}/{m['fn']}"
            
            print(f"{agent:<20} {precision:>10.2%}  {recall:>10.2%}  {f1:>10.2%}  {tp_fp_fn:>20}")


def print_confusion_matrix(matrix: Dict, agent_names: List[str], method_name: str):
    print(f"\nCONFUSION MATRIX: {method_name}")
    print(f"(Rows=Actual, Columns=Predicted)\n")
    
    # Header
    print(f"{'Actual':<20}", end="")
    for agent in agent_names:
        print(f"{agent[:10]:<12}", end="")
    print()
    print("-" * (20 + 12 * len(agent_names)))
    
    # Rows
    for actual in agent_names:
        print(f"{actual:<20}", end="")
        for predicted in agent_names:
            count = matrix[actual][predicted]
            print(f"{count:<12}", end="")
        print()


def run_domain_calibration():
    """Main calibration workflow."""
    print("\n" + "=" * 100)
    print("DOMAIN CALIBRATION: HOLDOUT SET EVALUATION")
    print("=" * 100)
    
    # Split dataset
    holdout_queries, validation_queries = split_holdout_set(ROUTING_DATASET_200, holdout_size=50)
    print(f"\nHoldout set size: {len(holdout_queries)}")
    print(f"Validation set size: {len(validation_queries)}")
    print(f"Distribution: {len([q for q, a in holdout_queries if a == 'DataEngAgent'])} DataEng, "
          f"{len([q for q, a in holdout_queries if a == 'StatisticsAgent'])} Stats, "
          f"{len([q for q, a in holdout_queries if a == 'MLAgent'])} ML, "
          f"{len([q for q, a in holdout_queries if a == 'VizAgent'])} Viz")
    
    agent_names = ["DataEngAgent", "StatisticsAgent", "MLAgent", "VizAgent"]
    
    # Initialize classifiers
    print("\n[Initializing routing methods...]")
    semantic = SemanticSimilarityClassifier()
    
    performance = PerformanceWeightedClassifier(semantic)
    agent_runners = {
        "StatisticsAgent": run_statistics_agent_structured_timed,
        "DataEngAgent": run_data_eng_agent_structured_timed,
        "MLAgent": run_ml_agent_structured_timed,
        "VizAgent": run_viz_agent_structured_timed,
    }
    print("[Training Performance-Weighted classifier...]")
    train_performance_classifier(performance, agent_runners)
    
    llm = LLMMetaClassifier()
    # LLMMetaClassifier is stateless, no training needed
    
    print("[OK] All methods initialized and trained\n")
    
    # Evaluate each method on holdout set
    results = {}
    
    for method_name, classifier in [
        ("Semantic Similarity", semantic),
        ("Performance-Weighted", performance),
        ("LLM-Assisted", llm),
    ]:
        print(f"\n{'='*100}")
        print(f"Evaluating: {method_name}")
        print(f"{'='*100}")
        
        confusion_pairs = []
        
        start_time = time.time()
        
        for idx, (query, expected_agent) in enumerate(holdout_queries, 1):
            predicted, was_correct = run_routing_method(classifier, query, expected_agent)
            
            # Store for metrics computation
            confusion_pairs.append((expected_agent, predicted))
            
            # Progress
            if idx % 10 == 0:
                print(f"  [{idx:2d}/{len(holdout_queries)}] processed")
        
        elapsed = time.time() - start_time
        
        # Compute metrics from ALL confusion pairs
        metrics = compute_metrics(confusion_pairs, agent_names)
        confusion_matrix = build_confusion_matrix(confusion_pairs, agent_names)
        
        # Store results
        results[method_name] = {
            "metrics": metrics,
            "confusion_matrix": confusion_matrix,
            "elapsed_time": elapsed,
        }
        
        # Print metrics
        print_metrics_table(metrics, method_name)
        print_confusion_matrix(confusion_matrix, agent_names, method_name)
        
        # Macro-averaged metrics
        precisions = [m["precision"] for m in metrics.values()]
        recalls = [m["recall"] for m in metrics.values()]
        f1_scores = [m["f1"] for m in metrics.values()]
        
        macro_precision = sum(precisions) / len(precisions) if precisions else 0
        macro_recall = sum(recalls) / len(recalls) if recalls else 0
        macro_f1 = sum(f1_scores) / len(f1_scores) if f1_scores else 0
        
        print(f"\nMACRO-AVERAGED METRICS:")
        print(f"  Precision: {macro_precision:.2%}")
        print(f"  Recall:    {macro_recall:.2%}")
        print(f"  F1:        {macro_f1:.2%}")
        print(f"  Time:      {elapsed:.1f}s")
    
    # Comparative analysis
    print(f"\n{'='*100}")
    print("COMPARATIVE ANALYSIS")
    print(f"{'='*100}\n")
    
    print("Method Performance Ranking (by Macro-F1):")
    ranked = sorted(
        results.items(),
        key=lambda x: sum(m["f1"] for m in x[1]["metrics"].values()) / len(x[1]["metrics"]),
        reverse=True
    )
    
    for rank, (method, data) in enumerate(ranked, 1):
        macro_f1 = sum(m["f1"] for m in data["metrics"].values()) / len(data["metrics"])
        print(f"  {rank}. {method:<25} F1={macro_f1:.2%}")
    
    # Per-agent strengths
    print(f"\nPER-AGENT ROUTING DIFFICULTY (macro avg recall):")
    for agent in agent_names:
        recalls = {
            method: data["metrics"][agent]["recall"]
            for method, data in results.items()
        }
        avg_recall = sum(recalls.values()) / len(recalls)
        print(f"  {agent:<20}: {avg_recall:.1%} (easy) → (hard)")
        for method, recall in sorted(recalls.items(), key=lambda x: x[1], reverse=True):
            print(f"    {method:<25}: {recall:.1%}")
    
    # Confusion patterns
    print(f"\nCOMMON MISCLASSIFICATIONS (across all methods):")
    
    confusion_counts = defaultdict(int)
    for method, data in results.items():
        matrix = data["confusion_matrix"]
        for actual in agent_names:
            for predicted in agent_names:
                if actual != predicted:
                    confusion_counts[(actual, predicted)] += matrix[actual][predicted]
    
    sorted_confusions = sorted(confusion_counts.items(), key=lambda x: x[1], reverse=True)
    for (actual, predicted), count in sorted_confusions[:10]:
        total_actual = len([q for q, a in holdout_queries if a == actual])
        pct = 100 * count / (total_actual * len(results)) if total_actual > 0 else 0
        print(f"  {actual} → {predicted}: {count:2d} times ({pct:.1f}% of {actual} queries)")
    
    # Save results to JSON
    output_file = Path("quality_eval_output") / "domain_calibration_results.json"
    output_file.parent.mkdir(exist_ok=True)
    
    # Convert to JSON-serializable format
    json_results = {}
    for method, data in results.items():
        json_results[method] = {
            "metrics": {
                agent: {
                    "tp": m["tp"],
                    "fp": m["fp"],
                    "fn": m["fn"],
                    "precision": m["precision"],
                    "recall": m["recall"],
                    "f1": m["f1"],
                }
                for agent, m in data["metrics"].items()
            },
            "confusion_matrix": data["confusion_matrix"],
            "elapsed_time": data["elapsed_time"],
        }
    
    with open(output_file, 'w') as f:
        json.dump(json_results, f, indent=2)
    
    print(f"\n[OK] Results saved to {output_file}\n")
    
    return results


if __name__ == "__main__":
    run_domain_calibration()
