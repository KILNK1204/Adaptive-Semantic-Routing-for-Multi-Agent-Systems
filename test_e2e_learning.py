"""End-to-end routing test with actual agent feedback and learning."""

import sys
import io
import random

# Fix encoding for Windows console
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Set random seed for reproducibility
random.seed(42)

from router.router_decider import (
    SemanticSimilarityClassifier,
    PerformanceWeightedClassifier,
    LLMMetaClassifier,
)

# Import simple agents
from stats_agent.stats_agent_simple import run_statistics_agent_timed
from ML_agent.ML_agent_simple import run_ml_agent_timed
from data_agent.data_agent_simple import run_data_eng_agent_timed
from visual_agent.visual_agent_simple import run_viz_agent_timed

# Import training and test queries
from queries import TRAINING_QUERIES
from queries2 import ROUTING_DATASET_200

# Legacy complex queries (now using external query sets)
COMPLEX_QUERIES = [
    # Data Engineering + Stats + ML queries (primary: DataEngAgent)
    ("Load my CSV file, validate the data quality, check for missing values", "DataEngAgent"),
    ("Import the Excel file, clean the data, and remove duplicates", "DataEngAgent"),
    ("Read the database table, normalize the schema, optimize performance", "DataEngAgent"),
    ("Create a data pipeline to extract, transform, and load the data", "DataEngAgent"),
    ("Design a SQL schema for customer data storage and optimization", "DataEngAgent"),
    
    # Data + Stats + Viz queries (primary: DataEngAgent or StatsAgent - starts with data)
    ("Load my dataset, analyze distributions statistically, and visualize results", "DataEngAgent"),
    ("Read the data file, perform outlier detection, plot the findings", "DataEngAgent"),
    ("Import the CSV, check for normality, create visualizations", "DataEngAgent"),
    ("Process the raw data, calculate summary statistics, make charts", "DataEngAgent"),
    ("ETL the data, compute correlations, visualize heatmaps", "DataEngAgent"),
    
    # Stats + Viz queries (primary: StatsAgent)
    ("Is this data normally distributed? Create a histogram to show it", "StatisticsAgent"),
    ("Perform a hypothesis test and visualize the p-value results", "StatisticsAgent"),
    ("Calculate confidence intervals and plot them on a chart", "StatisticsAgent"),
    ("Test for statistical significance and create a visualization", "StatisticsAgent"),
    ("Run regression analysis and plot the fitted line", "StatisticsAgent"),
    
    # ML + Viz queries (primary: MLAgent)
    ("Train a model and visualize the feature importance", "MLAgent"),
    ("Build a neural network and create performance graphs", "MLAgent"),
    ("Create a random forest and plot the decision trees", "MLAgent"),
    ("Train a classifier and visualize the confusion matrix", "MLAgent"),
    ("Develop an ensemble model and plot accuracy curves", "MLAgent"),
    
    # Complex: Data + Stats + Viz + ML (primary: DataEngAgent - starts with data prep)
    ("Load the data, clean it, analyze it statistically, visualize patterns, train a model", "DataEngAgent"),
    ("Import CSV, validate schema, check distributions, plot results, build predictor", "DataEngAgent"),
    ("Read database, normalize schema, calculate stats, create dashboard, ML pipeline", "DataEngAgent"),
    ("ETL the dataset, remove outliers, test hypotheses, visualize, predict outcomes", "DataEngAgent"),
    ("Ingest data, quality check, statistical analysis, charting, machine learning", "DataEngAgent"),
    
    # Complex: Stats + ML (primary: StatisticsAgent - starts with analysis)
    ("Test if the features are significant, then use them in a model", "StatisticsAgent"),
    ("Perform correlation analysis, then build a regression model", "StatisticsAgent"),
    ("Check normality assumptions, then train a neural network", "StatisticsAgent"),
    ("Calculate sample size, then train a classifier", "StatisticsAgent"),
    ("Power analysis for the experiment, then ML model", "StatisticsAgent"),
    
    # Complex: Stats + Viz + ML (primary: StatisticsAgent - starts with stats)
    ("Analyze the data statistically, visualize findings, train a model", "StatisticsAgent"),
    ("Test hypotheses, create charts, build prediction model", "StatisticsAgent"),
    ("Statistical inference, visualization, machine learning pipeline", "StatisticsAgent"),
    ("Compute statistics, plot distributions, train classifier", "StatisticsAgent"),
    ("Regression analysis, visual representation, predictive model", "StatisticsAgent"),
    
    # Misleading: Asking for viz but needs data prep first
    ("Show me a beautiful dashboard of my raw data", "DataEngAgent"),
    ("Create a visualization after processing the raw file", "DataEngAgent"),
    ("Make charts from this messy dataset", "DataEngAgent"),
    ("Visualize the results after cleaning the data", "DataEngAgent"),
    ("Plot the findings from the database query", "DataEngAgent"),
    
    # Misleading: Asking for ML but needs stats first
    ("Train a model on this small sample", "StatisticsAgent"),
    ("Build a predictor and tell me if it's valid statistically", "StatisticsAgent"),
    ("Create a machine learning solution that respects statistical assumptions", "StatisticsAgent"),
    ("Develop a model that passes statistical tests", "StatisticsAgent"),
    ("ML pipeline with statistical validation", "StatisticsAgent"),
    
    # Clear Stats queries
    ("Test if means are equal across groups", "StatisticsAgent"),
    ("Calculate confidence interval for the proportion", "StatisticsAgent"),
    ("Perform ANOVA on the experimental data", "StatisticsAgent"),
    ("Chi-square test for independence", "StatisticsAgent"),
    ("Bayesian inference on posterior distribution", "StatisticsAgent"),
    ("T-test for paired samples", "StatisticsAgent"),
    ("Power analysis for sample size determination", "StatisticsAgent"),
    ("Correlation analysis between variables", "StatisticsAgent"),
    ("Linear regression with residual diagnostics", "StatisticsAgent"),
    ("Distribution fitting and goodness-of-fit test", "StatisticsAgent"),
    
    # Clear ML queries
    ("Train a random forest classifier on the features", "MLAgent"),
    ("Build a deep neural network for image classification", "MLAgent"),
    ("Implement gradient boosting for regression", "MLAgent"),
    ("Support vector machine for binary classification", "MLAgent"),
    ("K-means clustering on the feature space", "MLAgent"),
    ("Decision tree with cross-validation", "MLAgent"),
    ("Ensemble methods combining multiple models", "MLAgent"),
    ("Hyperparameter tuning for the model", "MLAgent"),
    ("Feature engineering for better predictions", "MLAgent"),
    ("Model evaluation and performance metrics", "MLAgent"),
    
    # Clear Viz queries
    ("Create a line chart of sales over time", "VizAgent"),
    ("Make a pie chart showing market share", "VizAgent"),
    ("Plot a scatter diagram with regression line", "VizAgent"),
    ("Design a dashboard with multiple KPIs", "VizAgent"),
    ("Bar chart comparing categories", "VizAgent"),
    ("Heatmap of correlation matrix", "VizAgent"),
    ("Histogram of distribution", "VizAgent"),
    ("Box plot for outlier detection", "VizAgent"),
    ("Network graph visualization", "VizAgent"),
    ("Interactive visualization dashboard", "VizAgent"),
    
    # Clear Data Eng queries
    ("Create a fact table in the warehouse", "DataEngAgent"),
    ("Design a normalized database schema", "DataEngAgent"),
    ("Write SQL queries for data extraction", "DataEngAgent"),
    ("Build an ETL pipeline for daily updates", "DataEngAgent"),
    ("Optimize slow database queries", "DataEngAgent"),
    ("Implement data quality checks", "DataEngAgent"),
    ("Set up data partitioning for performance", "DataEngAgent"),
    ("Create index on frequently queried columns", "DataEngAgent"),
    ("Design a data migration strategy", "DataEngAgent"),
    ("Build a real-time data streaming pipeline", "DataEngAgent"),
    
    # Ambiguous: Could be multiple agents
    ("Analyze this data for me", "DataEngAgent"),
    ("What insights can you find?", "StatisticsAgent"),
    ("Help me understand the patterns", "StatisticsAgent"),
    ("Build something predictive", "MLAgent"),
    ("Make it look good", "VizAgent"),
    ("Is the data good quality?", "DataEngAgent"),
    ("What's the main finding?", "StatisticsAgent"),
    ("Can you predict the future?", "MLAgent"),
    
    # Complex with multiple clear goals but different starting points
    ("First validate the data, then analyze it statistically", "DataEngAgent"),
    ("First train a model, then visualize the results", "MLAgent"),
    ("First test hypotheses, then build a dashboard", "StatisticsAgent"),
    ("First clean the dataset, then do statistical analysis", "DataEngAgent"),
    ("First engineer features, then train a classifier", "MLAgent"),
    
    # Tricky: Mentions final goal but process suggests different primary
    ("I want a machine learning model. First, validate the data quality", "DataEngAgent"),
    ("I need predictions. First, test statistical assumptions", "StatisticsAgent"),
    ("I want visualizations. First, clean and prepare the data", "DataEngAgent"),
    ("I need a dashboard. First, do ETL on the raw data", "DataEngAgent"),
    ("I want statistical insights. First, load the data properly", "DataEngAgent"),
    
    # Edge cases
    ("The data is messy, has outliers, wrong schema, missing values - fix it all", "DataEngAgent"),
    ("The model is underfitting, overfitting, slow - optimize everything", "MLAgent"),
    ("The statistics are unclear, distributions unknown, assumptions violated - test all", "StatisticsAgent"),
    ("The visualizations are ugly, confusing, incomplete - redesign all", "VizAgent"),
    ("Everything is broken - start from data cleaning", "DataEngAgent"),
]

# 20 long, realistic multi-agent queries with clear primary agent
LONG_COMPLEX_QUERIES = [
    # DataEng-first: data cleaning, schema, ETL as primary
    (
        "Before you do any fancy statistics or machine learning, start by connecting to the production database, exploring every table for missing values, impossible dates, duplicate customer IDs, and broken foreign keys, then design a cleaned staging schema that downstream analytical and modeling agents can safely depend on.",
        "DataEngAgent",
    ),
    (
        "Take this messy CSV export from the marketing team, infer a reasonable schema, fix obviously broken date and currency formats, deduplicate customers across regions, and only after that should anyone attempt hypothesis tests, predictive models, or sophisticated visualizations on top of the cleaned dataset.",
        "DataEngAgent",
    ),
    (
        "Given our S3 bucket full of quarterly parquet files generated by different engineering teams, build a repeatable ETL pipeline that merges them, enforces consistent column types, applies data quality checks on key revenue fields, and produces a warehouse fact table that statistics and visualization specialists can safely consume later.",
        "DataEngAgent",
    ),
    (
        "Starting from the raw IoT event logs, validate the JSON schema, quarantine malformed records into a separate table, standardize timestamps and device identifiers, and then expose an aggregated dataset at hourly and daily grain so a statistics agent can test trends and a machine learning agent can eventually build forecasting models.",
        "DataEngAgent",
    ),
    (
        "For this historical survey project with dozens of free-text and categorical fields, focus first on data engineering by normalizing response categories, handling missing demographics in a principled way, building lookup tables for codes, and documenting everything clearly before any statistics, dashboards, or machine learning experiments are attempted.",
        "DataEngAgent",
    ),
    
    # Statistics-first: assume data is clean, stats primary
    (
        "Using the clean experiment dataset that the data engineering team already prepared, start by formulating the appropriate null and alternative hypotheses, run a power analysis to confirm whether the sample size is adequate, perform the necessary significance tests, and only then advise whether building more complex predictive models makes sense.",
        "StatisticsAgent",
    ),
    (
        "For this multi-variant A/B test with seasonality and several correlated metrics, begin with exploratory data analysis, construct confidence intervals for key outcomes, adjust for multiple comparisons, visualize the distributions, and after we understand statistical significance we can decide whether longer-term machine learning models are even warranted.",
        "StatisticsAgent",
    ),
    (
        "Given weekly revenue numbers across product lines and regions, first fit an appropriate regression or time-series model, check residual diagnostics carefully, test for autocorrelation and heteroscedasticity, compute prediction intervals, and only once those statistical checks pass should any downstream forecasting dashboards or automated ML pipelines be trusted.",
        "StatisticsAgent",
    ),
    (
        "On this clinical trial dataset, verify randomization quality and baseline balance between treatment arms, handle missing outcomes using statistically sound methods, compute effect sizes with confidence intervals, and only after drawing rigorous statistical conclusions should any summary visualizations or machine learning models be created for stakeholders.",
        "StatisticsAgent",
    ),
    (
        "Before anyone trains a fancy classifier on this customer churn dataset, carefully analyze feature distributions, handle class imbalance using appropriate statistical techniques, compute correlations and variance inflation factors, test simple baseline models, and then provide a recommendation on whether more complicated machine learning architectures will meaningfully improve performance.",
        "StatisticsAgent",
    ),
    
    # ML-first: assume data and stats done, ML primary
    (
        "Assuming the dataset has already been cleaned, joined, and validated by data engineers, design a robust machine learning pipeline that includes feature engineering, model selection between gradient boosting and neural networks, hyperparameter tuning with cross-validation, and then generate a few concise plots that help non-experts interpret the final model.",
        "MLAgent",
    ),
    (
        "For this image classification problem, focus on building and training a convolutional neural network with appropriate data augmentation, compare it against a simpler baseline such as logistic regression on precomputed embeddings, and only afterwards request any additional statistical summaries or dashboards needed to communicate the results to product managers.",
        "MLAgent",
    ),
    (
        "We already trust the existing warehouse tables and basic descriptive statistics, so concentrate on training an ensemble of models for customer churn prediction, evaluate them using robust cross-validation, calibrate the predicted probabilities, and only at the end produce a handful of high-level visualizations suitable for the leadership slide deck.",
        "MLAgent",
    ),
    (
        "Given a multivariate time-series of sensor readings from our factory machines, build and compare forecasting models using both classical approaches and deep learning architectures, tune their hyperparameters, select the best model based on out-of-sample performance, and then prepare a small set of plots showing typical successes and failure modes.",
        "MLAgent",
    ),
    (
        "For this recommendation system project, prioritize constructing meaningful user and item features, choose between matrix factorization and a modern deep learning approach, run offline evaluation with ranking metrics such as NDCG, perform limited hyperparameter search, and then summarize the behavior of the best model with a couple of targeted visualizations.",
        "MLAgent",
    ),
    
    # Viz-first: visualization primary, others delegated
    (
        "For the quarterly executive review, design an interactive dashboard that highlights revenue trends, regional breakdowns, and product performance, making sure the visuals are clear, color-blind friendly, and easy to filter, while assuming that any heavy aggregation or statistical computation has already been handled by upstream agents.",
        "VizAgent",
    ),
    (
        "I need a visually compelling story for our customer journey, so build a set of linked visualizations that show drop-off at each funnel stage, highlight important user segments, and support drill-down, delegating any additional data cleaning or rigorous statistical checks to other agents only when new data issues become obvious.",
        "VizAgent",
    ),
    (
        "Using the existing clean warehouse tables, create a suite of charts that exposes seasonality, anomalies, and correlations in our core metrics, favoring clarity and interpretability over complex modeling, and only ask for help from statistics or machine learning agents if simple visual explanations clearly fail to answer stakeholder questions.",
        "VizAgent",
    ),
    (
        "We are preparing a public-facing analytics portal for non-technical users, so focus on building smooth, responsive visualizations with intuitive tooltips, annotations, and filters, and assume that the underlying data models, data quality checks, and formal hypothesis tests have already been completed by the appropriate backend specialists.",
        "VizAgent",
    ),
    (
        "For this internal operations dashboard, prioritize concise, information-dense visualizations that surface bottlenecks, SLA violations, and queue lengths in near real time, wiring them to metrics that the data platform already exposes, and leave any heavy modeling or deep statistical analysis to specialized agents once the visuals reveal concrete problems.",
        "VizAgent",
    ),
]

# Use external test queries (200 queries from queries2.py)
# Falls back to combined legacy queries if not using external dataset
TEST_QUERIES = ROUTING_DATASET_200

class RouterWithLearning:

    def __init__(self, routing_method="semantic"):
        self.semantic_classifier = SemanticSimilarityClassifier()
        self.performance_classifier = PerformanceWeightedClassifier(
            self.semantic_classifier, 
            learning_rate=0.2
        )
        self.llm_classifier = LLMMetaClassifier()
        
        self.routing_method = routing_method
        if routing_method == "performance":
            self.classifier = self.performance_classifier
        elif routing_method == "llm":
            self.classifier = self.llm_classifier
        else:
            self.classifier = self.semantic_classifier
        
        # Agent dispatch
        self.agent_dispatch = {
            "StatisticsAgent": run_statistics_agent_timed,
            "MLAgent": run_ml_agent_timed,
            "DataEngAgent": run_data_eng_agent_timed,
            "VizAgent": run_viz_agent_timed,
        }
        
        # Track statistics
        self.routing_decisions = []
        self.agent_feedback = []
    
    def route_and_learn(self, query, expected_agent=None):
        # Step 1: Classify query
        routed_agent, confidence = self.classifier.classify(query)
        
        # Step 2: Send to agent
        try:
            agent_func = self.agent_dispatch[routed_agent]
            response_str, latency = agent_func(query)
        except Exception as e:
            print(f"[Error] Agent {routed_agent} failed: {e}")
            return (routed_agent, "ERROR", None)
        
        # Extract domain from response
        actual_domain = "UNKNOWN"
        for line in response_str.split('\n'):
            if line.startswith('DOMAIN:'):
                actual_domain = line.split(':', 1)[1].strip()
                break
        
        # Learn from feedback (performance-weighted only)
        if self.routing_method == "performance":
            was_in_domain = (actual_domain == "IN_DOMAIN")
            # Accuracy: check if routed agent matched expected agent
            was_accurate = (routed_agent == expected_agent) if expected_agent else False
            latency_signal = latency if was_accurate else latency * 1.5
            self.performance_classifier.record_result(routed_agent, was_in_domain, was_accurate, latency_signal)
        
        # Track results
        was_correct_route = (routed_agent == expected_agent) if expected_agent else None
        actual_in_domain = (actual_domain == "IN_DOMAIN")
        
        self.routing_decisions.append({
            "query": query,
            "expected_agent": expected_agent,
            "routed_agent": routed_agent,
            "was_correct_route": was_correct_route,
            "actual_domain": actual_domain,
            "actual_in_domain": actual_in_domain,
            "confidence": confidence,
            "latency": latency,
        })
        
        return (routed_agent, actual_domain, response_str)
    
    def get_stats(self):
        total = len(self.routing_decisions)
        if total == 0:
            return None
        
        correct_routes = sum(1 for d in self.routing_decisions if d["was_correct_route"])
        in_domain_count = sum(1 for d in self.routing_decisions if d["actual_in_domain"])
        
        stats = {
            "total_queries": total,
            "correct_routes": correct_routes,
            "correct_route_rate": correct_routes / total if total > 0 else 0,
            "in_domain_count": in_domain_count,
            "in_domain_rate": in_domain_count / total if total > 0 else 0,
            "avg_latency": sum(d["latency"] for d in self.routing_decisions) / total,
            "avg_confidence": sum(d["confidence"] for d in self.routing_decisions) / total,
        }
        return stats

# Run test
print("=" * 100)
print("END-TO-END ROUTING TEST WITH ACTUAL AGENT FEEDBACK")
print("120 Complex Multi-Goal Queries + Simple Agent Learning")
print("=" * 100)

print("\nInitializing router with actual agents (simple versions)...")
print("Note: Using simple agents (llama3.1) for speed\n")

# Test all three routing methods
results = {}

for method in ["semantic", "performance", "llm"]:
    print(f"\n{'='*100}")
    print(f"Testing: {method.upper()} ROUTING WITH ACTUAL AGENT FEEDBACK")
    print(f"Total queries: {len(TEST_QUERIES)}")
    print(f"{'='*100}\n")
    
    router = RouterWithLearning(routing_method=method)
    
    for idx, (query, expected_agent) in enumerate(TEST_QUERIES, 1):
        # Truncate query for display
        display_query = query[:50] + "..." if len(query) > 50 else query
        
        # Route and learn
        routed_agent, actual_domain, response = router.route_and_learn(query, expected_agent)
        
        # Determine routing success
        was_correct = (routed_agent == expected_agent)
        route_status = "✓" if was_correct else "✗"
        
        # Determine agent success  
        agent_status = "IN" if actual_domain == "IN_DOMAIN" else "OUT"
        
        # Show progress every 20 queries
        if idx % 20 == 0:
            stats_so_far = router.get_stats()
            route_acc = 100 * stats_so_far['correct_route_rate']
            domain_rate = 100 * stats_so_far['in_domain_rate']
            print(f"  [{idx:3d}/{len(TEST_QUERIES)}] Route accuracy: {route_acc:5.1f}%, In-domain: {domain_rate:5.1f}%")
    
    # Get statistics
    stats = router.get_stats()
    results[method] = {
        "router": router,
        "stats": stats
    }
    
    print(f"\n  Final stats for {method}:")
    print(f"    Routing Accuracy: {stats['correct_routes']}/{stats['total_queries']} ({100*stats['correct_route_rate']:.1f}%)")
    print(f"    In-Domain Rate: {stats['in_domain_count']}/{stats['total_queries']} ({100*stats['in_domain_rate']:.1f}%)")

# Print final comparison
print("\n" + "=" * 100)
print("FINAL RESULTS - THREE ROUTING METHODS COMPARED")
print("=" * 100)

for method in ["semantic", "performance", "llm"]:
    stats = results[method]["stats"]
    print(f"\n{method.upper()} ROUTING:")
    print(f"  Routing Accuracy: {stats['correct_routes']}/{stats['total_queries']} " 
          f"({100*stats['correct_route_rate']:.1f}%)")
    print(f"  Agent In-Domain Rate: {stats['in_domain_count']}/{stats['total_queries']} "
          f"({100*stats['in_domain_rate']:.1f}%)")
    print(f"  Average Latency: {stats['avg_latency']:.3f}s")
    print(f"  Average Confidence: {stats['avg_confidence']:.3f}")

# Show comparative improvements
semantic_correct = results["semantic"]["stats"]["correct_routes"]
perf_correct = results["performance"]["stats"]["correct_routes"]
llm_correct = results["llm"]["stats"]["correct_routes"]

print(f"\nCOMPARATIVE ANALYSIS:")
print(f"  Performance-weighted vs Semantic:  {perf_correct - semantic_correct:+d} routes")
print(f"  LLM-assisted vs Semantic:          {llm_correct - semantic_correct:+d} routes")
print(f"  LLM-assisted vs Performance-weighted: {llm_correct - perf_correct:+d} routes")

if results["performance"]["router"].routing_method == "performance":
    perf_stats = results["performance"]["router"].performance_classifier.get_stats()
    print(f"\nPERFORMANCE CLASSIFIER LEARNING STATE:")
    print(f"(Agent success rates learned from real agent domain responses)\n")
    for agent, stats_dict in sorted(perf_stats.items()):
        print(f"  {agent}:")
        print(f"    Success rate: {stats_dict['success_rate']:.2%}")
        print(f"    Total routed: {stats_dict['total_count']}")
        print(f"    In-domain: {stats_dict['in_domain_count']}")
        print(f"    Avg latency: {stats_dict['avg_latency']:.3f}s")

print("\n" + "=" * 100)
print("KEY INSIGHTS")
print("=" * 100)
print("""
- Router classifies each query, calls the actual agent, learns from domain response
- All queries are IN-DOMAIN (data, stats, ML, or viz)
- Semantic: Fast embedding-based baseline
- Performance-weighted: Adaptive learning from agent feedback
- LLM-assisted: Uses reasoning about query intent
""")

print("=" * 100)
print("TEST COMPLETE - Learning based on REAL agent domain responses")
print("=" * 100)
