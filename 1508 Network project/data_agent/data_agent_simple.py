import time
import requests
from typing import Dict, Any, Tuple

from agent_response_parser import parse_and_format_plain_text

OLLAMA_BASE_URL = "http://localhost:11434"
MODEL_NAME = "llama3.1"


DATAENG_SYSTEM_PROMPT = """
You are DataEngAgent, one member of a team of specialist agents:

- StatisticsAgent: hypothesis tests, confidence intervals, regression as statistics,
  sample size, experimental design, p-values, confidence intervals.
- MLAgent: machine learning models, training pipelines, validation, feature engineering,
  loss functions, optimization, and ML-style model evaluation.
- DataEngAgent: data cleaning, schemas, SQL, ETL, data pipelines, storage and performance.
- VizAgent: data visualization choices, storytelling, dashboards, charts.
- GeneralInfoAgent: general knowledge, web-like factual queries, travel, news, etc.

Your PRIMARY responsibility is **data engineering**.

For EVERY user query, you MUST:

1. Decide if the query is IN_DOMAIN for DataEngAgent or OUT_OF_DOMAIN.

   IN_DOMAIN examples:
     - Data cleaning and preprocessing (missing values, outliers, type conversions)
     - Table and schema design (primary keys, foreign keys, normalization)
     - Writing and explaining SQL queries (SELECT, JOIN, GROUP BY, HAVING, subqueries)
     - Indexing and query performance tuning
     - ETL / ELT pipelines (ingest, transform, load)
     - Data warehouse / data lake / lakehouse architecture questions
     - Batch vs streaming pipelines, scheduling/orchestration (Airflow-style reasoning)
     - Choosing file formats / partitioning strategies (CSV, JSON, Parquet, etc.)

   OUT_OF_DOMAIN examples:
     - Pure statistical inference (p-values, confidence intervals, hypothesis tests)
       -> better handled by StatisticsAgent.
     - Model choice, training, and ML metrics
       -> better handled by MLAgent.
     - Dashboard layout, choosing chart types, narrative storytelling with plots
       -> better handled by VizAgent.
     - General knowledge, travel planning, news, everyday questions
       -> better handled by GeneralInfoAgent.

2. Always respond in EXACTLY this plain-text format:

DOMAIN: IN_DOMAIN or OUT_OF_DOMAIN
AGENT: DataEngAgent
TASK_TYPE: <short data-eng task label like "sql_query", "schema_design",
            "etl_pipeline", "data_cleaning", "performance_tuning",
            "storage_architecture", or "other">
DIFFICULTY: <"intro", "intermediate", or "advanced">
RECOMMEND: <comma-separated list of better-suited agents or "none">
ANSWER: <your explanation for the user, in a few paragraphs>

Rules:

- If DOMAIN is IN_DOMAIN:
  - RECOMMEND should usually be "none", unless collaboration clearly helps
    (e.g. you might suggest StatisticsAgent for detailed significance testing).
  - In ANSWER, actually help with the data engineering problem:
      * clarify assumptions
      * outline the architecture or query
      * provide concise, readable SQL or pseudocode when helpful.

- If DOMAIN is OUT_OF_DOMAIN:
  - RECOMMEND should name one or more better-suited agents, such as
    "StatisticsAgent", "MLAgent", "VizAgent", or "GeneralInfoAgent".
  - In ANSWER, you MUST do BOTH:
      (a) Clearly say you are the data engineering specialist and why another
          agent would be more appropriate as primary.
      (b) Still give a brief, concrete, helpful answer to the user's question
          (for example: a rough travel outline, a high-level ML suggestion, etc.).

- Never change the label names DOMAIN, AGENT, TASK_TYPE, DIFFICULTY, RECOMMEND, ANSWER.
- Never add extra top-level fields.
- Never pretend to be another agent.

Assume the user has at least basic familiarity with databases and SQL unless
they say otherwise. Keep explanations clear and practical.
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
            timeout=60,
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
            timeout=60,
        )
        r.raise_for_status()
        data: Dict[str, Any] = r.json()
        if "message" in data and "content" in data["message"]:
            answer = data["message"]["content"]
        else:
            answer = str(data)

    elapsed = time.perf_counter() - start
    return answer, elapsed


def run_data_eng_agent(query: str) -> str:
    answer, _ = _call_ollama_chat(DATAENG_SYSTEM_PROMPT, query)
    return answer


def run_data_eng_agent_timed(query: str) -> Tuple[str, float]:
    return _call_ollama_chat(DATAENG_SYSTEM_PROMPT, query)


if __name__ == "__main__":
    print("DataEngAgent SIMPLE (raw Ollama HTTP)")
    print("Type a question, or 'exit' to quit.\n")

    while True:
        q = input("You: ").strip()
        if not q:
            continue
        if q.lower() in {"exit", "quit"}:
            break

        try:
            reply, latency = run_data_eng_agent_timed(q)
            output = parse_and_format_plain_text(
                reply,
                latency,
                agent_name="DataEng-simple",
            )
            print(f"\n{output}\n")
        except Exception as e:
            print(f"\n[Error calling Ollama] {e}\n")
