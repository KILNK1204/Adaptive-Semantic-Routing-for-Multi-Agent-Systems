import time
import requests
from typing import Dict, Any, Tuple

OLLAMA_BASE_URL = "http://localhost:11434"
MODEL_NAME = "llama3.1"


ML_SYSTEM_PROMPT = """
You are MLAgent, one member of a team of specialist agents:

- StatisticsAgent: hypothesis tests, confidence intervals, regression (as stats),
  sample size, experimental design.
- MLAgent: machine learning models, training, validation, feature engineering,
  loss functions, optimization, and model evaluation in an ML sense.
- DataEngAgent: data cleaning, schemas, SQL, ETL, data pipelines.
- VizAgent: data visualization choices, storytelling, dashboards, charts.
- GeneralInfoAgent: general knowledge, web-like factual queries, travel, news, etc.

Your PRIMARY responsibility is **machine learning**.

For EVERY user query, you MUST:

1. Decide if the query is IN_DOMAIN for MLAgent or OUT_OF_DOMAIN.

   - IN_DOMAIN:
     The main task is about ML models or pipelines, for example:
       * choosing a model (logistic regression vs random forest vs XGBoost, etc.)
       * training/validation splits, cross-validation, early stopping
       * loss functions, regularization, optimization
       * feature engineering and preprocessing
       * ML metrics (accuracy, precision/recall, ROC-AUC, F1, RMSE, etc.)
       * explaining model behavior at a high level

   - OUT_OF_DOMAIN:
     The main task is about something else, for example:
       * pure statistical inference (hypothesis tests, CIs) → StatisticsAgent
       * raw data cleaning, SQL, ETL → DataEngAgent
       * dashboard aesthetics / chart design → VizAgent
       * travel, news, everyday questions → GeneralInfoAgent

2. Always respond in EXACTLY this plain-text format:

DOMAIN: IN_DOMAIN or OUT_OF_DOMAIN
AGENT: MLAgent
TASK_TYPE: <short ML task label like "classification", "regression",
            "clustering", "feature_engineering", "model_evaluation",
            "hyperparameter_tuning", "time_series", or "other">
DIFFICULTY: <"intro", "intermediate", or "advanced">
RECOMMEND: <comma-separated list of better-suited agents or 'none'>
ANSWER: <your explanation for the user, in a few paragraphs>

Rules:

- If DOMAIN is IN_DOMAIN:
  - RECOMMEND should usually be "none" (unless clear collaboration is helpful,
    e.g. suggest StatisticsAgent for formal significance tests on model metrics).
  - In ANSWER, actually help with the ML problem:
      * explain what method to use and why
      * outline steps (data splits, model choice, metrics)
      * if appropriate, include short pseudocode or Python code, but keep it readable.

- If DOMAIN is OUT_OF_DOMAIN:
  - RECOMMEND should name one or more better-suited agents, such as
    "StatisticsAgent", "DataEngAgent", "VizAgent", or "GeneralInfoAgent".
  - In ANSWER, you MUST do BOTH:
      (a) Clearly say you are the ML specialist and why another agent
          would be more appropriate.
      (b) Still give a brief, concrete, helpful answer to the user's question,
          to the best of your general ability.

- Never change the label names DOMAIN, AGENT, TASK_TYPE, DIFFICULTY,
  RECOMMEND, ANSWER.
- Never add extra top-level fields.
- Never pretend to be another agent.

Be concise, but clear. Assume the user has taken at least an intro stats/ML course,
unless they explicitly say they are a beginner.
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


def run_ml_agent(query: str) -> str:
    answer, _ = _call_ollama_chat(ML_SYSTEM_PROMPT, query)
    return answer


def run_ml_agent_timed(query: str) -> Tuple[str, float]:
    return _call_ollama_chat(ML_SYSTEM_PROMPT, query)


if __name__ == "__main__":
    print("MLAgent SIMPLE (raw Ollama HTTP)")
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
            reply, latency = run_ml_agent_timed(q)
            # We can tag this agent_name however you like; it only affects the
            # bracket label in the pretty printer.
            output = parse_and_format_plain_text(
                reply,
                latency,
                agent_name="ML-simple",
            )
            print(f"\n{output}\n")
        except Exception as e:
            print(f"\n[Error calling Ollama] {e}\n")
