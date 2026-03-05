"""Load completed evaluation CSV and generate quality analysis report."""

import sys
import csv
from pathlib import Path
from collections import defaultdict
from statistics import mean, median, stdev


def load_evaluation_csv(csv_path: Path) -> list:
    records = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Parse scores, skip if empty
            try:
                rel = float(row.get("Relevance (1-5)", "").strip()) if row.get("Relevance (1-5)", "").strip() else None
                comp = float(row.get("Completeness (1-5)", "").strip()) if row.get("Completeness (1-5)", "").strip() else None
                corr = float(row.get("Correctness (1-5)", "").strip()) if row.get("Correctness (1-5)", "").strip() else None
                act = float(row.get("Actionability (1-5)", "").strip()) if row.get("Actionability (1-5)", "").strip() else None
                dom = float(row.get("Domain Confidence (1-5)", "").strip()) if row.get("Domain Confidence (1-5)", "").strip() else None
                
                # Only include if at least one score is filled
                if any(s is not None for s in [rel, comp, corr, act, dom]):
                    record = {
                        "index": int(row.get("Index", 0)),
                        "agent": row.get("Expected Agent", "Unknown"),
                        "relevance": rel,
                        "completeness": comp,
                        "correctness": corr,
                        "actionability": act,
                        "domain_confidence": dom,
                        "notes": row.get("Evaluator Notes", "").strip(),
                    }
                    
                    # Calculate average of non-None scores
                    scores = [s for s in [rel, comp, corr, act, dom] if s is not None]
                    if scores:
                        record["average"] = mean(scores)
                        records.append(record)
            except (ValueError, TypeError):
                continue
    
    return records


def analyze_scores(records: list) -> dict:
    if not records:
        return {}
    
    all_averages = [r["average"] for r in records if "average" in r]
    
    # By agent
    by_agent = defaultdict(list)
    for r in records:
        by_agent[r["agent"]].append(r["average"])
    
    # By dimension (only non-None values)
    by_dimension = {
        "relevance": [],
        "completeness": [],
        "correctness": [],
        "actionability": [],
        "domain_confidence": []
    }
    
    for r in records:
        if r.get("relevance"):
            by_dimension["relevance"].append(r["relevance"])
        if r.get("completeness"):
            by_dimension["completeness"].append(r["completeness"])
        if r.get("correctness"):
            by_dimension["correctness"].append(r["correctness"])
        if r.get("actionability"):
            by_dimension["actionability"].append(r["actionability"])
        if r.get("domain_confidence"):
            by_dimension["domain_confidence"].append(r["domain_confidence"])
    
    # Quality buckets
    excellent = sum(1 for a in all_averages if a >= 4.5)
    good = sum(1 for a in all_averages if 4.0 <= a < 4.5)
    acceptable = sum(1 for a in all_averages if 3.0 <= a < 4.0)
    poor = sum(1 for a in all_averages if a < 3.0)
    
    return {
        "total_evaluated": len(records),
        "overall_average": mean(all_averages) if all_averages else 0,
        "overall_median": median(all_averages) if all_averages else 0,
        "overall_stdev": stdev(all_averages) if len(all_averages) > 1 else 0,
        "by_agent": {
            agent: {
                "average": mean(scores),
                "median": median(scores),
                "count": len(scores),
            }
            for agent, scores in by_agent.items() if scores
        },
        "by_dimension": {
            dim: {
                "average": mean(scores) if scores else 0,
                "count": len(scores),
            }
            for dim, scores in by_dimension.items()
        },
        "quality_distribution": {
            "excellent_45_5": excellent,
            "good_40_45": good,
            "acceptable_30_40": acceptable,
            "poor_below_30": poor,
        },
        "records": records,
    }


def print_report(analysis: dict):
    print("\n" + "=" * 100)
    print("QUALITY EVALUATION ANALYSIS REPORT")
    print("=" * 100)
    
    if not analysis:
        print("No completed evaluations found.")
        return
    
    print(f"\nEVALUATED: {analysis['total_evaluated']} answers")
    
    print(f"\nOVERALL QUALITY METRICS:")
    print(f"  Average Score:        {analysis['overall_average']:.2f}/5.0")
    print(f"  Median Score:         {analysis['overall_median']:.2f}/5.0")
    if analysis['overall_stdev'] > 0:
        print(f"  Std Deviation:        {analysis['overall_stdev']:.2f}")
    
    print(f"\nQUALITY DISTRIBUTION:")
    dist = analysis['quality_distribution']
    total = analysis['total_evaluated']
    print(f"  Excellent (4.5-5.0):  {dist['excellent_45_5']:2d}/{total} ({100*dist['excellent_45_5']/total:.1f}%)")
    print(f"  Good (4.0-4.5):       {dist['good_40_45']:2d}/{total} ({100*dist['good_40_45']/total:.1f}%)")
    print(f"  Acceptable (3.0-4.0): {dist['acceptable_30_40']:2d}/{total} ({100*dist['acceptable_30_40']/total:.1f}%)")
    print(f"  Poor (<3.0):          {dist['poor_below_30']:2d}/{total} ({100*dist['poor_below_30']/total:.1f}%)")
    
    print(f"\nQUALITY BY AGENT:")
    for agent in ["DataEngAgent", "StatisticsAgent", "MLAgent", "VizAgent"]:
        if agent in analysis['by_agent']:
            stats = analysis['by_agent'][agent]
            print(f"  {agent:20s}: {stats['average']:.2f}/5.0 (n={stats['count']}, median={stats['median']:.2f})")
    
    print(f"\nQUALITY BY DIMENSION (average across all answers):")
    for dim in ["relevance", "completeness", "correctness", "actionability", "domain_confidence"]:
        stats = analysis['by_dimension'][dim]
        dim_name = dim.replace("_", " ").title()
        if stats['count'] > 0:
            print(f"  {dim_name:20s}: {stats['average']:.2f}/5.0 (n={stats['count']})")
    
    print(f"\n" + "=" * 100)
    print("INTERPRETATION:")
    print("=" * 100)
    
    avg = analysis['overall_average']
    if avg >= 4.5:
        print("✓ EXCELLENT: Agents consistently produce high-quality answers")
        print("  → Strong correlation between routing accuracy and answer quality")
    elif avg >= 4.0:
        print("✓ GOOD: Most answers are useful and professionally sound")
        print("  → Routing accuracy is a reasonable proxy for quality")
    elif avg >= 3.0:
        print("⚠ ACCEPTABLE: Answers are somewhat useful with gaps")
        print("  → Some routing methods may produce mediocre answers despite correct routing")
    else:
        print("✗ POOR: Many answers lack completeness or correctness")
        print("  → Routing accuracy alone doesn't guarantee useful answers")
    
    # Agent-specific insights
    print(f"\nAGENT INSIGHTS:")
    agents_by_quality = sorted(
        analysis['by_agent'].items(),
        key=lambda x: x[1]['average'],
        reverse=True
    )
    if agents_by_quality:
        best_agent = agents_by_quality[0]
        worst_agent = agents_by_quality[-1]
        print(f"  Best performing:  {best_agent[0]:20s} ({best_agent[1]['average']:.2f}/5.0)")
        print(f"  Weakest area:      {worst_agent[0]:20s} ({worst_agent[1]['average']:.2f}/5.0)")
    
    # Dimension insights
    print(f"\nDIMENSION INSIGHTS:")
    dims_by_quality = sorted(
        analysis['by_dimension'].items(),
        key=lambda x: x[1]['average'],
        reverse=True
    )
    for dim, stats in dims_by_quality[:2]:
        if stats['count'] > 0:
            dim_name = dim.replace("_", " ").title()
            print(f"  Strongest:  {dim_name:20s} ({stats['average']:.2f}/5.0)")
    
    for dim, stats in dims_by_quality[-2:]:
        if stats['count'] > 0:
            dim_name = dim.replace("_", " ").title()
            print(f"  Weakest:    {dim_name:20s} ({stats['average']:.2f}/5.0)")
    
    print(f"\n" + "=" * 100 + "\n")


def print_sample_answers(analysis: dict, num_samples: int = 3):
    print("\nSAMPLE EVALUATED ANSWERS:\n")
    
    # Show best, worst, and middle
    records = sorted(analysis['records'], key=lambda r: r.get('average', 0))
    
    samples = []
    if records:
        # Worst
        if len(records) > 0:
            samples.append(("LOWEST QUALITY", records[0]))
        # Best
        if len(records) > 0:
            samples.append(("HIGHEST QUALITY", records[-1]))
        # Middle
        if len(records) > 2:
            samples.append(("MIDDLE QUALITY", records[len(records)//2]))
    
    for label, record in samples:
        print(f"{'='*100}")
        print(f"{label} - {record['agent']} (Score: {record['average']:.2f}/5.0)")
        print(f"{'='*100}")
        print(f"Index: {record['index']}")
        print(f"Dimensions: Rel={record.get('relevance', '?'):.1f}, Comp={record.get('completeness', '?'):.1f}, "
              f"Corr={record.get('correctness', '?'):.1f}, Act={record.get('actionability', '?'):.1f}, "
              f"Dom={record.get('domain_confidence', '?'):.1f}")
        if record['notes']:
            print(f"Notes: {record['notes']}")
        print()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("No CSV file provided.")
        print("\nTo generate a CSV for evaluation, run:")
        print("  python spot_check_evaluation.py")
        print("\nThen fill in the scores and run:")
        print("  python analyze_quality.py quality_eval_output/spot_check_evaluation.csv")
        sys.exit(1)
    
    csv_path = Path(sys.argv[1])
    
    if not csv_path.exists():
        print(f"Error: File not found: {csv_path}")
        sys.exit(1)
    
    print(f"Loading evaluations from: {csv_path}")
    
    records = load_evaluation_csv(csv_path)
    
    if not records:
        print("No completed evaluations found in CSV.")
        print("Make sure you've filled in the score columns (1-5) for at least some rows.")
        sys.exit(1)
    
    print(f"Loaded {len(records)} completed evaluations.\n")
    
    analysis = analyze_scores(records)
    
    print_report(analysis)
    print_sample_answers(analysis)


if __name__ == "__main__":
    main()
