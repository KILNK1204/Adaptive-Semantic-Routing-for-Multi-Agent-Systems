"""End-to-end learning test using complex agent models with output management."""

import sys
import time
import shutil
import json
import random
from pathlib import Path
from typing import Tuple, Dict, List, Any
from collections import defaultdict

# Set random seed for reproducibility
random.seed(72)

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from router.router_decider import (
    SemanticSimilarityClassifier,
    PerformanceWeightedClassifier,
    LLMMetaClassifier,
)

from stats_agent.stats_agent_complex import run_statistics_agent_structured_timed
from data_agent.data_agent_complex import run_data_eng_agent_structured_timed
from ML_agent.ML_agent_complex import run_ml_agent_structured_timed
from visual_agent.visual_agent_complex import run_viz_agent_structured_timed
from training_data_method2 import train_performance_classifier
from queries import TRAINING_QUERIES
from queries2 import ROUTING_DATASET_200


# Test queries from queries2.py (200 queries)
# Training queries from queries.py (100 training queries for Method 2)


OUTPUT_DIR = Path("output")


def clean_output_folder():
    try:
        # Close matplotlib figures to prevent TclError
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend
        import matplotlib.pyplot as plt
        plt.close('all')
    except Exception:
        pass
    
    if OUTPUT_DIR.exists():
        try:
            for item in OUTPUT_DIR.iterdir():
                try:
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
                except (OSError, PermissionError, FileNotFoundError):
                    pass
        except Exception as e:
            pass


def ensure_output_folder():
    OUTPUT_DIR.mkdir(exist_ok=True)


def get_output_files() -> List[str]:
    if not OUTPUT_DIR.exists():
        return []
    return [str(f) for f in OUTPUT_DIR.iterdir() if f.is_file()]


class RouterWithLearning:
    
    def __init__(self, routing_method: str = "semantic"):
        self.routing_method = routing_method
        self.learned_weights = defaultdict(lambda: defaultdict(float))
        self.query_count = 0
        
        self.semantic_classifier = SemanticSimilarityClassifier()
        self.performance_classifier = PerformanceWeightedClassifier(
            semantic_classifier=self.semantic_classifier,
            learning_rate=0.1
        )
        self.llm_classifier = LLMMetaClassifier()
        
        if routing_method == "performance":
            self.classifier = self.performance_classifier
        elif routing_method == "llm":
            self.classifier = self.llm_classifier
        else:
            self.classifier = self.semantic_classifier
    
    def route_and_learn(
        self, 
        query: str, 
        expected_agent: str
    ) -> Tuple[str, str, Dict[str, Any]]:
        # Get routing result
        import time as time_module
        routing_start = time_module.time()
        classify_result = self.classifier.classify(query)
        if isinstance(classify_result, tuple):
            routed_agent, score = classify_result
        else:
            routed_agent = classify_result
        routing_latency = time_module.time() - routing_start
        
        self.query_count += 1
        
        # Call the appropriate complex agent (no directory change needed)
        try:
            if routed_agent == "StatisticsAgent":
                response, latency = run_statistics_agent_structured_timed(query)
            elif routed_agent == "MLAgent":
                response, latency = run_ml_agent_structured_timed(query)
            elif routed_agent == "DataEngAgent":
                response, latency = run_data_eng_agent_structured_timed(query)
            elif routed_agent == "VizAgent":
                response, latency = run_viz_agent_structured_timed(query)
            else:
                # Fallback to stats if unknown
                response, latency = run_statistics_agent_structured_timed(query)
        except Exception as e:
            # Graceful degradation if agent fails - create a minimal response object
            print(f"  [Agent error: {str(e)[:80]}]")
            
            # Create a simple object that mimics the response structure
            class ErrorResponse:
                def __init__(self, agent_name):
                    self.domain = "OUT_OF_DOMAIN"
                    self.agent = agent_name
                    self.task_type = "error"
                    self.difficulty = "intro"
                    self.answer = f"Agent encountered error"
                    self.recommend = []
                    self.files_analyzed = []
                    self.code_executions = []
            
            response = ErrorResponse(routed_agent)
            latency = 0.0
        
        actual_domain = response.domain
        
        # Learning: update weights based on actual domain response
        if actual_domain == "IN_DOMAIN":
            # Positive reinforcement: agent was good for this query
            self.learned_weights[routed_agent][query[:50]] += 1.0
        else:
            # Negative reinforcement: agent failed on this query
            self.learned_weights[routed_agent][query[:50]] -= 0.5
        
        # Update performance classifier (if using performance-weighted routing)
        if self.routing_method == "performance":
            was_in_domain = (actual_domain == "IN_DOMAIN")
        # Accuracy: check if routed agent matched expected agent
            was_accurate = (routed_agent == expected_agent) if expected_agent else False
            latency_signal = latency if was_accurate else latency * 1.5
            self.classifier.record_result(routed_agent, was_in_domain, was_accurate, latency_signal)
        
        # Capture output files
        output_files = get_output_files()
        
        # Build response dictionary
        response_dict = {
            "domain": response.domain,
            "task_type": response.task_type,
            "difficulty": response.difficulty,
            "answer": response.answer[:200] + "..." if len(response.answer) > 200 else response.answer,
            "recommend": response.recommend,
            "files_analyzed": [
                {
                    "path": f.file_path,
                    "type": f.file_type,
                    "size": f.size_bytes
                } for f in response.files_analyzed
            ] if hasattr(response, 'files_analyzed') and response.files_analyzed else [],
            "code_executions": [
                {
                    "success": e.success,
                    "error": e.error[:100] if e.error else None
                } for e in response.code_executions
            ] if hasattr(response, 'code_executions') and response.code_executions else [],
            "routing_latency": routing_latency,
            "agent_latency": latency,
            "total_latency": routing_latency + latency,
            "output_files": output_files,
        }
        
        return routed_agent, actual_domain, response_dict


def main():
    """Run E2E learning test with complex agents."""
    
    ensure_output_folder()
    
    # Use the new test dataset from queries2.py (200 queries)
    TEST_QUERIES = ROUTING_DATASET_200
    
    print("=" * 100)
    print("END-TO-END LEARNING TEST: COMPLEX AGENTS WITH OUTPUT MANAGEMENT")
    print("=" * 100)
    print(f"Total test queries: {len(TEST_QUERIES)}")
    print(f"Training queries (for Method 2): {len(TRAINING_QUERIES)}")
    print(f"Output directory: {OUTPUT_DIR.absolute()}")
    print()
    
    results = {}
    
    for method in ["semantic", "performance", "llm"]:
        print(f"\n{'='*100}")
        print(f"Testing: {method.upper()} ROUTING")
        print(f"{'='*100}")
        
        router = RouterWithLearning(routing_method=method)
        
        # Train the performance-weighted classifier if this is the performance method
        if method == "performance":
            print("\nPre-training performance-weighted classifier with training data...")
            agent_runners = {
                "StatisticsAgent": run_statistics_agent_structured_timed,
                "DataEngAgent": run_data_eng_agent_structured_timed,
                "MLAgent": run_ml_agent_structured_timed,
                "VizAgent": run_viz_agent_structured_timed,
            }
            training_stats = train_performance_classifier(router.classifier, agent_runners)
            print(f"Pre-training complete!\n")
        
        method_results = {
            "stats": {
                "correct_routes": 0,
                "in_domain_rate": 0,
                "total_queries": 0,
                "total_latency": 0,
            },
            "queries": []
        }
        
        in_domain_count = 0
        total_latency = 0
        
        for idx, (query, expected_agent) in enumerate(TEST_QUERIES, 1):
            # Clean output folder before each query
            clean_output_folder()
            
            routed_agent, actual_domain, response = router.route_and_learn(query, expected_agent)
            
            is_correct = (routed_agent == expected_agent)
            if is_correct:
                method_results["stats"]["correct_routes"] += 1
            
            if actual_domain == "IN_DOMAIN":
                in_domain_count += 1
            
            total_latency += response["total_latency"]
            
            query_result = {
                "query": query[:60] + "..." if len(query) > 60 else query,
                "expected_agent": expected_agent,
                "routed_agent": routed_agent,
                "correct": is_correct,
                "domain": actual_domain,
                "task_type": response["task_type"],
                "difficulty": response["difficulty"],
                "routing_latency": response["routing_latency"],
                "agent_latency": response["agent_latency"],
                "total_latency": response["total_latency"],
                "generated_files": len(response["output_files"]),
            }
            method_results["queries"].append(query_result)
            
            # Progress indicator
            if idx % 20 == 0:
                print(f"  Progress: {idx}/{len(TEST_QUERIES)} queries | "
                      f"Correct: {method_results['stats']['correct_routes']}/{idx} | "
                      f"In-Domain: {in_domain_count}/{idx} | "
                      f"Avg Total Latency: {total_latency/idx:.2f}s")
        
        # Final stats
        method_results["stats"]["total_queries"] = len(TEST_QUERIES)
        method_results["stats"]["in_domain_rate"] = (in_domain_count / len(TEST_QUERIES)) * 100
        method_results["stats"]["total_latency"] = total_latency
        method_results["stats"]["avg_latency"] = total_latency / len(TEST_QUERIES)
        
        results[method] = method_results
        
        # Print summary
        print(f"\n{method.upper()} ROUTING RESULTS:")
        print(f"  Correct routes: {method_results['stats']['correct_routes']}/{len(TEST_QUERIES)}")
        print(f"  Accuracy: {(method_results['stats']['correct_routes']/len(TEST_QUERIES))*100:.1f}%")
        print(f"  In-Domain Rate: {method_results['stats']['in_domain_rate']:.1f}%")
        print(f"  Total Latency: {total_latency:.1f}s")
        print(f"  Avg Total Latency: {method_results['stats']['avg_latency']:.2f}s per query")
    
    # Three-way comparison
    print("\n" + "=" * 100)
    print("THREE-METHOD COMPARISON")
    print("=" * 100)
    
    # Check which methods completed
    completed_methods = list(results.keys())
    print(f"\nCompleted methods: {', '.join(completed_methods)}")
    
    if len(completed_methods) < 3:
        print(f"Note: Only {len(completed_methods)}/3 methods completed due to errors.\n")
    
    # Skip comparison if not all methods are available
    if "semantic" not in results or "performance" not in results or "llm" not in results:
        print("Skipping full three-method comparison (not all methods completed).")
        if "performance" in results:
            perf_correct = results["performance"]["stats"]["correct_routes"]
            print(f"\nPerformance-weighted routing accuracy: {perf_correct}/200 ({(perf_correct/200)*100:.1f}%)")
        if "semantic" in results:
            sem_correct = results["semantic"]["stats"]["correct_routes"]
            print(f"Semantic routing accuracy: {sem_correct}/200 ({(sem_correct/200)*100:.1f}%)")
        return
    
    semantic_correct = results["semantic"]["stats"]["correct_routes"]
    perf_correct = results["performance"]["stats"]["correct_routes"]
    llm_correct = results["llm"]["stats"]["correct_routes"]
    
    print(f"\nRouting Accuracy:")
    print(f"  Semantic:           {semantic_correct} correct ({(semantic_correct/len(TEST_QUERIES))*100:.1f}%)")
    print(f"  Performance-weighted: {perf_correct} correct ({(perf_correct/len(TEST_QUERIES))*100:.1f}%)")
    print(f"  LLM-assisted:       {llm_correct} correct ({(llm_correct/len(TEST_QUERIES))*100:.1f}%)")
    
    print(f"\nRelative Performance vs Semantic Baseline:")
    print(f"  Performance-weighted: {perf_correct - semantic_correct:+d} routes")
    print(f"  LLM-assisted:         {llm_correct - semantic_correct:+d} routes")
    print(f"  LLM vs Performance:   {llm_correct - perf_correct:+d} routes")
    
    print(f"\nIn-Domain Rates (agent said IN_DOMAIN):")
    print(f"  Semantic:           {results['semantic']['stats']['in_domain_rate']:.1f}%")
    print(f"  Performance-weighted: {results['performance']['stats']['in_domain_rate']:.1f}%")
    print(f"  LLM-assisted:       {results['llm']['stats']['in_domain_rate']:.1f}%")
    
    print(f"\nLatency Analysis Breakdown:")
    
    # Calculate average routing latencies
    semantic_routing_latency = sum(q.get('routing_latency', 0) for q in results['semantic']['queries']) / len(results['semantic']['queries'])
    perf_routing_latency = sum(q.get('routing_latency', 0) for q in results['performance']['queries']) / len(results['performance']['queries'])
    llm_routing_latency = sum(q.get('routing_latency', 0) for q in results['llm']['queries']) / len(results['llm']['queries'])
    
    semantic_agent_latency = sum(q.get('agent_latency', 0) for q in results['semantic']['queries']) / len(results['semantic']['queries'])
    perf_agent_latency = sum(q.get('agent_latency', 0) for q in results['performance']['queries']) / len(results['performance']['queries'])
    llm_agent_latency = sum(q.get('agent_latency', 0) for q in results['llm']['queries']) / len(results['llm']['queries'])
    
    print(f"\n  Routing Classification Time (Router Overhead):")
    print(f"    Semantic:             {semantic_routing_latency*1000:.1f}ms")
    print(f"    Performance-weighted: {perf_routing_latency*1000:.1f}ms")
    print(f"    LLM-assisted:         {llm_routing_latency*1000:.1f}ms")
    
    print(f"\n  Agent Execution Time (Query Processing):")
    print(f"    Semantic:             {semantic_agent_latency:.2f}s")
    print(f"    Performance-weighted: {perf_agent_latency:.2f}s")
    print(f"    LLM-assisted:         {llm_agent_latency:.2f}s")
    
    print(f"\n  Total End-to-End Time Per Query:")
    print(f"    Semantic:             {results['semantic']['stats']['avg_latency']:.2f}s")
    print(f"    Performance-weighted: {results['performance']['stats']['avg_latency']:.2f}s")
    print(f"    LLM-assisted:         {results['llm']['stats']['avg_latency']:.2f}s")
    
    # Final cleanup
    print(f"\nFinal cleanup: Removing all output files...")
    clean_output_folder()
    print(f"[OK] Output folder cleaned")
    
    


if __name__ == "__main__":
    main()
