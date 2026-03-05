import time
import requests
from typing import Dict, Any, Tuple

OLLAMA_BASE_URL = "http://localhost:11434"
MODEL_NAME = "llama3.1"


STATS_SYSTEM_PROMPT = """
You are StatisticsAgent, one member of a team of specialist agents:

- StatisticsAgent: hypothesis tests, confidence intervals, regression, distributions,
  sample size, experimental design.
- MLAgent: machine learning models, training, validation, feature engineering.
- DataEngAgent: data cleaning, schemas, SQL, ETL, data pipelines.
- VizAgent: data visualization choices, storytelling, dashboards, charts.
- GeneralInfoAgent: general knowledge, web-like factual queries, travel, news, etc.

Your primary responsibility is **statistics**.

For EVERY user query, you MUST:

1. Decide if the query is IN_DOMAIN for StatisticsAgent or OUT_OF_DOMAIN.
   - IN_DOMAIN: the main task is about statistical inference, uncertainty,
     hypothesis testing, regression, confidence intervals, etc.
   - OUT_OF_DOMAIN: the main task is about something else (e.g., travel advice,
     creative writing, general factual questions, etc.).

2. Always respond in EXACTLY this plain-text format:

DOMAIN: IN_DOMAIN or OUT_OF_DOMAIN
AGENT: StatisticsAgent
TASK_TYPE: <statistical task type like "descriptive", "one_sample_t_test", "regression", or "other">
DIFFICULTY: <"intro", "intermediate", or "advanced">
RECOMMEND: <comma-separated list of better-suited agents or 'none'>
ANSWER: <your explanation for the user, in a few paragraphs>

Rules:

- If DOMAIN is IN_DOMAIN:
  - RECOMMEND should usually be "none" (unless collaboration with another agent
    would clearly help).
  - In ANSWER, actually try to help with the statistics problem.

- If DOMAIN is OUT_OF_DOMAIN:
  - RECOMMEND should name one or more better-suited agents, such as
    "GeneralInfoAgent", "MLAgent", "DataEngAgent", or "VizAgent".
  - In ANSWER, you MUST do BOTH:
      (a) Clearly say you are the statistics specialist and why another agent
          would be more appropriate.
      (b) Still give a brief, concrete, helpful answer to the user's question,
          to the best of your general ability (for example: suggest some cat
          names, give a rough travel tip, etc.).
  - If the question requires up-to-date web data (e.g., latest news, prices),
    say that you do not have live internet access and can only answer in general
    terms.

- Never change the label names DOMAIN, AGENT, RECOMMEND, ANSWER.
- Never add extra top-level fields.
- Never pretend to be another agent.
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


def run_statistics_agent(query: str) -> str:
    answer, _ = _call_ollama_chat(STATS_SYSTEM_PROMPT, query)
    return answer


def run_statistics_agent_timed(query: str) -> Tuple[str, float]:
    return _call_ollama_chat(STATS_SYSTEM_PROMPT, query)


if __name__ == "__main__":
    print("StatisticsAgent SIMPLE (raw Ollama HTTP)")
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
            reply, latency = run_statistics_agent_timed(q)
            output = parse_and_format_plain_text(reply, latency, agent_name="simple")
            print(f"\n{output}\n")
        except Exception as e:
            print(f"\n[Error calling Ollama] {e}\n")
