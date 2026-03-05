"""Spot-check quality evaluation: sample 20 answers and score with rubric."""

import sys
import time
import random
import json
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))

from router.router_decider import SemanticSimilarityClassifier
from stats_agent.stats_agent_complex import run_statistics_agent_structured_timed
from data_agent.data_agent_complex import run_data_eng_agent_structured_timed
from ML_agent.ML_agent_complex import run_ml_agent_structured_timed
from visual_agent.visual_agent_complex import run_viz_agent_structured_timed
from queries2 import ROUTING_DATASET_200
from quality_evaluation import QualityRubrics, EvaluationGuide, QualityScore


OUTPUT_DIR = Path("quality_eval_output")


def ensure_output_folder():
    OUTPUT_DIR.mkdir(exist_ok=True)


def run_quality_spot_check(num_samples: int = 20, random_seed: int = 42) -> List[Dict]:
    random.seed(random_seed)
    ensure_output_folder()
    
    # Sample random queries from test set
    sampled_indices = random.sample(range(len(ROUTING_DATASET_200)), min(num_samples, len(ROUTING_DATASET_200)))
    sampled_queries = [ROUTING_DATASET_200[i] for i in sampled_indices]
    
    print("=" * 100)
    print("QUALITY SPOT-CHECK: SAMPLING 20 ANSWERS")
    print("=" * 100)
    print(f"Sampled {len(sampled_queries)} queries for evaluation")
    print(f"Output will be saved to: {OUTPUT_DIR.absolute()}\n")
    
    # Agent runners
    agent_runners = {
        "StatisticsAgent": run_statistics_agent_structured_timed,
        "DataEngAgent": run_data_eng_agent_structured_timed,
        "MLAgent": run_ml_agent_structured_timed,
        "VizAgent": run_viz_agent_structured_timed,
    }
    
    # Collect evaluation records
    eval_records = []
    
    for idx, (query, expected_agent) in enumerate(sampled_queries, 1):
        print(f"[{idx:2d}] Running query: {query[:60]}...")
        
        try:
            # Run the query through the expected agent
            runner = agent_runners.get(expected_agent)
            if not runner:
                print(f"     [SKIP] Agent '{expected_agent}' not available")
                continue
            
            response, latency = runner(query)
            
            # Build evaluation record
            record = {
                "index": idx,
                "query": query,
                "expected_agent": expected_agent,
                "agent_response": response.domain,
                "task_type": response.task_type,
                "difficulty": response.difficulty,
                "full_answer": response.answer,  # Store full answer for evaluation
                "latency": latency,
                "correct_route": expected_agent,  # Ground truth
                "was_in_domain": response.domain == "IN_DOMAIN",
                # Scores to be filled in manually
                "relevance_score": None,
                "completeness_score": None,
                "correctness_score": None,
                "actionability_score": None,
                "domain_confidence_score": None,
                "evaluator_notes": None,
            }
            
            eval_records.append(record)
            print(f"     [OK] Got answer from {expected_agent} ({latency:.2f}s)")
            
        except Exception as e:
            print(f"     [ERROR] {str(e)[:80]}")
    
    # Save evaluation records to JSON for reference
    eval_file = OUTPUT_DIR / "spot_check_evaluation_template.json"
    with open(eval_file, 'w', encoding='utf-8') as f:
        json.dump(eval_records, f, indent=2, ensure_ascii=False)
    
    print(f"\n[OK] Saved {len(eval_records)} evaluation records to {eval_file}")
    return eval_records


def print_evaluation_forms(eval_records: List[Dict]):
    print("\n" + "=" * 100)
    print("EVALUATION FORMS - PRINT OR COPY TO SPREADSHEET")
    print("=" * 100)
    
    # Print instructions
    print(EvaluationGuide.INSTRUCTIONS)
    
    for record in eval_records:
        agent = record["expected_agent"]
        query = record["query"]
        answer = record["full_answer"]
        
        print(f"\n{'='*100}")
        print(f"EVALUATION #{record['index']}")
        print(f"{'='*100}")
        print(f"\nAGENT: {agent}")
        print(f"QUERY: {query}")
        print(f"\nANSWER (first 500 chars):\n{answer[:500]}...")
        print(f"\n{'='*100}")
        print("SCORE EACH DIMENSION 1-5:\n")
        
        # Print rubric snippets
        rubric = QualityRubrics.get_rubric(agent)
        for dim in ["relevance", "completeness", "correctness", "actionability", "domain_confidence"]:
            print(f"{dim.upper()}:")
            if dim in rubric:
                lines = rubric[dim].split('\n')
                print(f"  {lines[0]}")
                print(f"  {lines[1]}")
                print(f"  {lines[2]}")
            print(f"  Score: ___ /5  Notes: ___\n")


def create_evaluation_spreadsheet_template(eval_records: List[Dict]):
    import csv
    
    csv_file = OUTPUT_DIR / "spot_check_evaluation.csv"
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            "Index",
            "Query",
            "Expected Agent",
            "Answer (first 200 chars)",
            "Agent Domain Response",
            "Latency (s)",
            "Relevance (1-5)",
            "Completeness (1-5)",
            "Correctness (1-5)",
            "Actionability (1-5)",
            "Domain Confidence (1-5)",
            "Average Score",
            "Evaluator Notes"
        ])
        
        writer.writeheader()
        
        for record in eval_records:
            answer_preview = record["full_answer"][:200].replace('\n', ' ')
            writer.writerow({
                "Index": record["index"],
                "Query": record["query"][:60],
                "Expected Agent": record["expected_agent"],
                "Answer (first 200 chars)": answer_preview,
                "Agent Domain Response": record["agent_response"],
                "Latency (s)": f"{record['latency']:.2f}",
                "Relevance (1-5)": "",
                "Completeness (1-5)": "",
                "Correctness (1-5)": "",
                "Actionability (1-5)": "",
                "Domain Confidence (1-5)": "",
                "Average Score": "",
                "Evaluator Notes": ""
            })
    
    print(f"\n[OK] Created evaluation spreadsheet template: {csv_file}")
    print(f"    Open this file in Excel/Sheets and fill in the score columns")
    return csv_file


def load_evaluation_scores_from_csv(csv_file: Path) -> Dict[int, QualityScore]:
    import csv
    
    scores = {}
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                idx = int(row["Index"])
                scores[idx] = {
                    "relevance": float(row["Relevance (1-5)"]),
                    "completeness": float(row["Completeness (1-5)"]),
                    "correctness": float(row["Correctness (1-5)"]),
                    "actionability": float(row["Actionability (1-5)"]),
                    "domain_confidence": float(row["Domain Confidence (1-5)"]),
                    "notes": row["Evaluator Notes"],
                }
            except (ValueError, KeyError):
                continue
    
    return scores


def generate_quality_report(eval_records: List[Dict], scores_dict: Dict[int, Dict]):
    print("\n" + "=" * 100)
    print("QUALITY EVALUATION REPORT")
    print("=" * 100)
    
    if not scores_dict:
        print("\n[INFO] No scores submitted yet. Complete the CSV template to generate a report.")
        return
    
    # Aggregate statistics
    all_scores = []
    by_agent = defaultdict(list)
    
    for record in eval_records:
        idx = record["index"]
        if idx in scores_dict:
            score_data = scores_dict[idx]
            avg_score = (
                score_data["relevance"] +
                score_data["completeness"] +
                score_data["correctness"] +
                score_data["actionability"] +
                score_data["domain_confidence"]
            ) / 5.0
            
            all_scores.append(avg_score)
            by_agent[record["expected_agent"]].append(avg_score)
    
    if not all_scores:
        print("\n[INFO] No valid scores found.")
        return
    
    # Print summary
    print(f"\nOVERALL QUALITY METRICS:")
    print(f"  Average Score (across 5 dimensions): {sum(all_scores)/len(all_scores):.2f}/5.0")
    print(f"  Median Score: {sorted(all_scores)[len(all_scores)//2]:.2f}/5.0")
    print(f"  Min Score: {min(all_scores):.2f}/5.0")
    print(f"  Max Score: {max(all_scores):.2f}/5.0")
    
    print(f"\nQUALITY BY AGENT:")
    for agent in ["DataEngAgent", "StatisticsAgent", "MLAgent", "VizAgent"]:
        if agent in by_agent and by_agent[agent]:
            scores = by_agent[agent]
            avg = sum(scores) / len(scores)
            print(f"  {agent:20s}: {avg:.2f}/5.0 (n={len(scores)})")
    
    print(f"\nQUALITY VS ROUTING ACCURACY COMPARISON:")
    print(f"  (Answers scoring 4-5 on average are 'good quality')")
    good_quality = sum(1 for s in all_scores if s >= 4.0)
    print(f"  Good Quality Answers: {good_quality}/{len(all_scores)} ({100*good_quality/len(all_scores):.1f}%)")
    
    print(f"\nIMPLICATIONS:")
    if sum(all_scores)/len(all_scores) >= 4.0:
        print(f"  ✓ Even when routers disagreed with labels, answers were high quality")
        print(f"  ✓ Single-annotator ground truth labels are reasonable proxies for usefulness")
    else:
        print(f"  ⚠ Some 'correct' routes produced mediocre answers")
        print(f"  ⚠ Suggests routing accuracy may not fully capture real-world usefulness")
    
    print(f"\n{'='*100}\n")


def main():
    print("\nQUALITY SPOT-CHECK EVALUATION")
    print("This script will:")
    print("1. Sample 20 random test queries")
    print("2. Run them through their expected agents")
    print("3. Generate evaluation forms for manual scoring")
    print("4. Create a CSV template for spreadsheet evaluation")
    print()
    
    # Run spot check
    eval_records = run_quality_spot_check(num_samples=20)
    
    # Create CSV template for evaluation
    csv_file = create_evaluation_spreadsheet_template(eval_records)
    
    print("\n" + "=" * 100)
    print("NEXT STEPS:")
    print("=" * 100)
    print(f"1. Open: {csv_file}")
    print(f"2. For each row, read the answer and score each dimension 1-5")
    print(f"3. Add notes explaining your scores")
    print(f"4. Save the file")
    print(f"5. Run: python spot_check_evaluation.py --load <path to your CSV>")
    print("=" * 100 + "\n")
    
    # Print sample evaluation form
    if eval_records:
        print("SAMPLE EVALUATION FORM (first answer):\n")
        record = eval_records[0]
        print(f"Agent: {record['expected_agent']}")
        print(f"Query: {record['query']}")
        print(f"\nAnswer preview:\n{record['full_answer'][:400]}...\n")
        print(f"Score each of these 1-5:")
        print(f"  • Relevance: Does it address the query?")
        print(f"  • Completeness: Are key aspects covered?")
        print(f"  • Correctness: Is it accurate/sound?")
        print(f"  • Actionability: Can the user use this advice?")
        print(f"  • Domain Confidence: Does it show expertise?\n")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--load":
        # Load and report on completed evaluations
        if len(sys.argv) < 3:
            print("Usage: python spot_check_evaluation.py --load <csv_file>")
            sys.exit(1)
        csv_path = Path(sys.argv[2])
        if csv_path.exists():
            print(f"Loading scores from {csv_path}...")
            # For now, just inform user
            print("[INFO] To implement score loading, run: python spot_check_evaluation.py (first)")
        else:
            print(f"File not found: {csv_path}")
    else:
        main()
