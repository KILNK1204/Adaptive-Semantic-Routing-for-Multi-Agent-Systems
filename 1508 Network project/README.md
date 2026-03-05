# Routing Strategies for Multi-Agent LLM Systems

> Semantic, Performance-Weighted, and LLM Meta-Routing  
> ECE1508 — University of Toronto, December 2025

---

## Overview

This project implements and evaluates three complementary query-routing strategies for a multi-agent LLM system. A central router receives a user query and dispatches it to one of four specialist agents backed by a locally-served LLM (Ollama). The three routing methods are compared on a labeled dataset of 200 queries across four data-science domains.

**Key results (5-trial average on 200 queries):**

| Method | Accuracy | In-Domain Rate | Route Overhead | Total Latency | Quality (5pt) |
|---|---|---|---|---|---|
| Semantic Similarity | 69.0 ± 0.0% | 91.8 ± 0.5% | 11.5 ms | 5.49 s | 4.41 |
| Performance-Weighted | 72.8 ± 1.5% | 94.2 ± 0.8% | 12.0 ms | 6.80 s | 4.50 |
| LLM Meta-Classification | 94.7 ± 0.6% | 99.2 ± 0.2% | 2 410.6 ms | 8.24 s | 4.53 |

---

## System Architecture

```
User Query
    │
    ▼
┌─────────────────────────────────────────────┐
│                   Router                    │
│  ┌────────────┐  ┌────────────┐  ┌───────┐  │
│  │  Semantic  │  │Performance │  │  LLM  │  │
│  │ Similarity │  │  Weighted  │  │ Meta  │  │
│  └────────────┘  └────────────┘  └───────┘  │
└─────────────────────────────────────────────┘
         │              │              │
         ▼              ▼              ▼
  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │Statistics│  │    ML    │  │ DataEng  │  │   Viz    │
  │  Agent   │  │  Agent   │  │  Agent   │  │  Agent   │
  └──────────┘  └──────────┘  └──────────┘  └──────────┘
```

### Specialist Agents

| Agent | Domain |
|---|---|
| **StatisticsAgent** | Hypothesis testing, inference, confidence intervals, regression, power analysis, experimental design |
| **MLAgent** | Model training, deep learning, feature engineering, hyperparameter tuning, cross-validation, model evaluation |
| **DataEngAgent** | SQL, ETL, schema design, data cleaning, warehouse optimization, data pipelines |
| **VizAgent** | Chart selection, dashboard design, exploratory data analysis, visual storytelling |

Each agent returns a structured response with `domain` (IN\_DOMAIN / OUT\_OF\_DOMAIN), `task_type`, `difficulty`, `answer`, and optional metadata (files analyzed, code executed, visualizations generated).

---

## Routing Methods

### Method 1 — Semantic Similarity Baseline

Uses a pre-trained sentence transformer (`all-MiniLM-L6-v2`, 384-d embeddings) to compute cosine similarity between the query and each agent's capability description. No training required; routing overhead is ~11.5 ms per query.

$$\text{score}(q, a) = \frac{\vec{q} \cdot \vec{a}}{\|\vec{q}\|\,\|\vec{a}\|}$$

### Method 2 — Performance-Weighted Adaptive Routing

Extends semantic similarity with learned per-agent statistics: accuracy rate, IN\_DOMAIN rate, and average latency. Statistics are updated via exponential moving average (α = 0.1) after every query — both during pre-training on 100 labelled queries and during the test run itself.

$$S_a(q) = 0.20 \cdot \text{semantic}(q,a) + 0.35 \cdot \text{accuracy}_a + 0.35 \cdot \text{indomain}_a + 0.10 \cdot \text{latency\_score}_a$$

### Method 3 — LLM Meta-Classification

Makes a separate LLM call (Ollama) that sees the agent descriptions and the user query, then outputs the name of the most suitable agent. Captures rich contextual reasoning at the cost of ~2.4 s additional overhead per query.

---

## Project Structure

```
.
├── router/
│   └── router_decider.py          # SemanticSimilarityClassifier, PerformanceWeightedClassifier, LLMMetaClassifier
├── stats_agent/
│   ├── stats_agent_simple.py      # Raw HTTP → Ollama
│   └── stats_agent_complex.py     # LangChain + structured JSON response
├── ML_agent/
│   ├── ML_agent_simple.py
│   └── ML_agent_complex.py
├── data_agent/
│   ├── data_agent_simple.py
│   ├── data_agent_complex.py
│   └── test_data_eng_queries.py   # 10 manual test queries for DataEngAgent
├── visual_agent/
│   ├── visual_agent_simple.py
│   └── visual_agent_complex.py
├── queries.py                     # 100 labelled training queries
├── queries2.py                    # 200 labelled test queries
├── training_data_method2.py       # Pre-trains PerformanceWeightedClassifier
├── test_e2e_learning.py           # E2E test — simple agents
├── test_e2e_learning_complex.py   # E2E test — complex agents + output cleanup
├── agent_response_parser.py       # Shared parser for plain-text and JSON responses
├── quality_evaluation.py          # Rubrics for 4 agents × 5 dimensions
├── spot_check_evaluation.py       # Samples 20 answers and generates scoring CSV
├── analyze_quality.py             # Analyses completed scoring CSV
├── domain_calibration.py          # Holdout P/R/F1 + confusion matrix per routing method
├── generate_visualizations.py     # Bar/scatter charts (accuracy, latency, frontier)
├── generate_results_figures.py    # 9-panel publication figure + quality breakdown
├── generate_accuracy_table.py     # Formatted accuracy table figure
├── test_data.csv                  # Sample dataset for file-reading agent tests
├── paper.tex                      # Full paper (IEEE-style)
└── output/                        # Generated plots, models, and reports (gitignored)
```

---

## Setup

### Prerequisites

- Python 3.11+
- [Ollama](https://ollama.ai) running locally at `http://localhost:11434`
- A compatible model pulled in Ollama (e.g., `llama3.1` or `gpt-oss:20b`)

### Install Python dependencies

```bash
pip install langchain-ollama pydantic sentence-transformers \
            pandas numpy scipy matplotlib seaborn scikit-learn requests
```

### Pull and start the model

```bash
ollama pull llama3.1
ollama serve          # if not already running
```

---

## Usage

### Run a single agent (interactive CLI)

```bash
# Simple agent (raw text output)
python stats_agent/stats_agent_simple.py

# Complex agent (structured JSON: domain, task_type, difficulty, answer)
python stats_agent/stats_agent_complex.py
```

### Run the full end-to-end routing test

```bash
# Uses simple agents — fast
python test_e2e_learning.py

# Uses complex agents with automatic output cleanup
python test_e2e_learning_complex.py
```

Both scripts test all three routing methods on the 200-query dataset and print a comparative summary.

### Run domain calibration (precision / recall / F1)

```bash
python domain_calibration.py
```

### Evaluate answer quality

```bash
# Step 1: Generate CSV template with 20 sampled answers
python spot_check_evaluation.py

# Step 2: Fill in scores in quality_eval_output/spot_check_evaluation.csv

# Step 3: Analyse completed scores
python analyze_quality.py quality_eval_output/spot_check_evaluation_completed.csv
```

### Generate result figures

```bash
python generate_visualizations.py     # accuracy, latency, efficiency frontier
python generate_results_figures.py    # 9-panel comprehensive figure
python generate_accuracy_table.py     # formatted table figure
```

---

## Programmatic API

All agents expose a consistent public API regardless of backend:

```python
# Plain-text response + latency
from stats_agent.stats_agent_simple import run_statistics_agent_timed
answer, latency = run_statistics_agent_timed("What sample size do I need for 80% power?")

# Structured response
from stats_agent.stats_agent_complex import run_statistics_agent_structured_timed
resp, latency = run_statistics_agent_structured_timed("Run a one-sample t-test.")
print(resp.domain)      # "IN_DOMAIN"
print(resp.task_type)   # "one_sample_t_test"
print(resp.difficulty)  # "intro"
print(resp.answer)
```

---

## Key Design Decisions

**Dual-signal routing (Method 2)** combines external accuracy (ground-truth label matching) and internal agent self-assessment (IN\_DOMAIN rate) with equal weight (35% each). These decorrelated signals together improve routing beyond what either achieves alone — agents with high domain confidence but lower external accuracy are down-weighted, and vice versa.

**Sandboxed code execution** — complex agents extract Python code from `<CODE>...</CODE>` tags in the LLM response and execute it in a restricted namespace (`pandas`, `numpy`, `scipy`, `matplotlib` only). `plt.show()`, `open()`, `sqlite3.connect()`, and `joblib.dump()` are intercepted to redirect all outputs to the `output/` folder.

**IN\_DOMAIN classification** — every agent classifies each query as IN\_DOMAIN or OUT\_OF\_DOMAIN and, when out-of-domain, recommends the appropriate specialist (`MLAgent`, `DataEngAgent`, `VizAgent`, `GeneralInfoAgent`). This enables downstream routing correction without an additional LLM call.

---

## Results Summary

- **Method 1** is the ideal baseline: zero-variance, training-free, and only 11.5 ms routing overhead. Suitable for latency-sensitive or resource-constrained deployments.
- **Method 2** provides continuous learning capability — it improves during both the pre-training phase and the live test run — with a modest 24% latency cost for a 3.8 pp accuracy gain.
- **Method 3** achieves near-perfect routing (94.7%) and domain recognition (99.2%), at the cost of roughly 200× routing overhead. Best suited for quality-critical applications where latency budget allows.
- Across all methods, spot-check quality averaged **4.47/5.0** with 90% of answers rated Good or Excellent, indicating agents maintain professional standards even on misrouted queries.

---

## Hardware & Software

| Component | Specification |
|---|---|
| CPU | Intel Core i5-13600K (13th Gen) |
| RAM | 32 GB |
| GPU | NVIDIA GeForce RTX 4070 SUPER |
| OS | Windows 11 |
| Python | 3.11 |
| LLM backend | Ollama (`llama3.1` / `gpt-oss:20b`) |
| Embeddings | `sentence-transformers` (`all-MiniLM-L6-v2`) |

---

## Paper

The full write-up is available in [`paper.tex`](paper.tex).

> **Routing Strategies for Multi-Agent LLM Systems: Semantic, Performance-Weighted, and LLM Meta-Routing**  
> Zhaoheng Li — Department of ECE, University of Toronto — December 2025

---

## License

This project is released for academic purposes. Please cite the accompanying paper if you build on this work.
