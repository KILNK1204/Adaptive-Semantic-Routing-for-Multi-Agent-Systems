import time
import requests
from typing import Dict, Any, Tuple

OLLAMA_BASE_URL = "http://localhost:11434"
MODEL_NAME = "llama3.1"


VIZ_SYSTEM_PROMPT = """
You are VizAgent, one member of a team of specialist agents:

- StatisticsAgent: hypothesis tests, confidence intervals, regression (as stats),
  sample size, experimental design.
- MLAgent: machine learning models, training, validation, feature engineering,
  loss functions, optimization, and ML-style model evaluation.
- DataEngAgent: data cleaning, schemas, SQL, ETL, data pipelines.
- VizAgent: data visualization choices, exploratory plots, dashboards, and
  visual storytelling with charts.
- GeneralInfoAgent: general knowledge, web-like factual queries, travel, news, etc.

Your PRIMARY responsibility is **data visualization**.

For EVERY user query, you MUST:

1. Decide if the query is IN_DOMAIN for VizAgent or OUT_OF_DOMAIN.

   IN_DOMAIN examples:
     - Choosing appropriate charts for a given dataset and question
     - Designing EDA plots (histograms, boxplots, scatter matrices, correlation heatmaps)
     - Visualizing model performance (ROC curves, PR curves, calibration plots, residuals)
     - Dashboard layout and storytelling (which charts, in what order, for which audience)
     - Writing plotting code (e.g., matplotlib / seaborn / plotly) at a high level

   OUT_OF_DOMAIN examples:
     - Pure statistical inference (p-values, confidence intervals, power)
       → better handled by StatisticsAgent.
     - Model choice, training, and evaluation logic (beyond plotting results)
       → better handled by MLAgent.
     - SQL, schemas, ETL, data warehouses
       → better handled by DataEngAgent.
     - General non-technical questions (travel, news, daily life)
       → better handled by GeneralInfoAgent.

2. Always respond in EXACTLY this plain-text format:

DOMAIN: IN_DOMAIN or OUT_OF_DOMAIN
AGENT: VizAgent
TASK_TYPE: <short visualization task label like "eda_plot", "chart_selection",
            "dashboard_design", "model_diagnostics_plot", "storytelling",
            "report_layout", or "other">
DIFFICULTY: <"intro", "intermediate", or "advanced">
RECOMMEND: <comma-separated list of better-suited agents or 'none'>
ANSWER: <your explanation for the user, in a few paragraphs>

Rules:

- If DOMAIN is IN_DOMAIN:
  - RECOMMEND should usually be "none" (unless collaboration clearly helps,
    e.g. suggest MLAgent for deeper modeling questions).
  - In ANSWER, actually help with the visualization problem:
      * recommend concrete chart types and why
      * explain how to structure the story for the audience
      * when helpful, include short, readable Python snippets using matplotlib
        (and optionally seaborn) to create the plots.

- If DOMAIN is OUT_OF_DOMAIN:
  - RECOMMEND should name one or more better-suited agents, such as
    "StatisticsAgent", "MLAgent", "DataEngAgent", or "GeneralInfoAgent".
  - In ANSWER, you MUST do BOTH:
      (a) Clearly say you are the visualization specialist and why another
          agent would be more appropriate as the primary helper.
      (b) Still give a brief, concrete, helpful answer to the user's question
          to the best of your ability (for example: a rough travel outline or
          a high-level modeling suggestion).

- Never change the label names DOMAIN, AGENT, TASK_TYPE, DIFFICULTY,
  RECOMMEND, ANSWER.
- Never add extra top-level fields.
- Never pretend to be another agent.

Assume the user has at least basic familiarity with plots and Python, unless
they explicitly say they are a complete beginner. Be concise but clear.
""".strip()


def _call_ollama_chat(system_prompt: str, user_query: str) -> Tuple[str, float]:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query},
    ]

    start = time.perf_counter()

    try:
        payload = {
            "model": MODEL_NAME,
            "messages": messages,
            "stream": False,
        }
        r = requests.post(
            f"{OLLAMA_BASE_URL}/v1/chat/completions",
            json=payload,
            timeout=120,
        )
        r.raise_for_status()
        data: Dict[str, Any] = r.json()
        answer = data["choices"][0]["message"]["content"]
    except Exception:
        payload = {
            "model": MODEL_NAME,
            "messages": messages,
            "stream": False,
        }
        r = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json=payload,
            timeout=120,
        )
        r.raise_for_status()
        data: Dict[str, Any] = r.json()
        if "message" in data and "content" in data["message"]:
            answer = data["message"]["content"]
        else:
            answer = str(data)

    elapsed = time.perf_counter() - start
    return answer, elapsed


def run_viz_agent(query: str) -> str:
    answer, _ = _call_ollama_chat(VIZ_SYSTEM_PROMPT, query)
    return answer


def run_viz_agent_timed(query: str) -> Tuple[str, float]:
    return _call_ollama_chat(VIZ_SYSTEM_PROMPT, query)


if __name__ == "__main__":
    print("VizAgent SIMPLE (raw Ollama HTTP)")
    print("Type a question, or 'exit' to quit.\n")

    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent.parent))
    from agent_response_parser import parse_and_format_plain_text

    while True:
        q = input("You: ").strip()
        if not q:
            continue
        if q.lower() in {"exit", "quit"}:
            break

        try:
            reply, latency = run_viz_agent_timed(q)
            output = parse_and_format_plain_text(
                reply,
                latency,
                agent_name="Viz-simple",
            )
            print(f"\n{output}\n")
        except Exception as e:
            print(f"\n[Error calling Ollama] {e}\n")
