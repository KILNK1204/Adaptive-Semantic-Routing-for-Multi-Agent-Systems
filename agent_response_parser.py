"""Centralized parser for agent responses."""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class ParsedAgentResponse:
    agent_name: str
    domain: Optional[str] = None
    task_type: Optional[str] = None
    difficulty: Optional[str] = None
    recommendations: Optional[List[str]] = None
    answer: str = ""
    raw_response: str = ""


def parse_plain_text_response(raw_response: str, agent_name: str = "Agent") -> ParsedAgentResponse:
    lines = raw_response.strip().split('\n')
    
    domain = None
    task_type = None
    difficulty = None
    recommendations = []
    answer_lines = []
    parsing_answer = False
    
    for line in lines:
        line_stripped = line.strip()
        
        if line_stripped.startswith("DOMAIN:"):
            domain = line_stripped.replace("DOMAIN:", "").strip()
        elif line_stripped.startswith("AGENT:"):
            pass
        elif line_stripped.startswith("TASK_TYPE:"):
            task_type = line_stripped.replace("TASK_TYPE:", "").strip()
        elif line_stripped.startswith("DIFFICULTY:"):
            difficulty = line_stripped.replace("DIFFICULTY:", "").strip()
        elif line_stripped.startswith("RECOMMEND:"):
            recommend_str = line_stripped.replace("RECOMMEND:", "").strip()
            if recommend_str.lower() != "none":
                recommendations = [a.strip() for a in recommend_str.split(",")]
        elif line_stripped.startswith("ANSWER:"):
            answer_lines.append(line_stripped.replace("ANSWER:", "").strip())
            parsing_answer = True
        elif parsing_answer or (line_stripped and not line_stripped.startswith(("DOMAIN:", "AGENT:", "TASK_TYPE:", "DIFFICULTY:", "RECOMMEND:", "ANSWER:"))):
            answer_lines.append(line_stripped)
    
    answer = "\n".join(answer_lines).strip()
    
    return ParsedAgentResponse(
        agent_name=agent_name,
        domain=domain,
        task_type=task_type,
        difficulty=difficulty,
        recommendations=recommendations if recommendations else None,
        answer=answer,
        raw_response=raw_response,
    )


def parse_json_response(
    json_data: Dict[str, Any],
    agent_name: str = "Agent"
) -> ParsedAgentResponse:
    return ParsedAgentResponse(
        agent_name=agent_name,
        domain=json_data.get("domain"),
        task_type=json_data.get("task_type"),
        difficulty=json_data.get("difficulty"),
        recommendations=json_data.get("recommend") or None,
        answer=json_data.get("answer", ""),
        raw_response=str(json_data),
    )


def format_agent_output(
    parsed: ParsedAgentResponse,
    latency: float,
    include_task: bool = False,
    include_difficulty: bool = False,
) -> str:
    lines = []
    # Always show domain
    if parsed.domain:
        lines.append(f"[DOMAIN ]: {parsed.domain}")
    
    # Show task and difficulty if requested
    if include_task and parsed.task_type:
        lines.append(f"[TASK   ]: {parsed.task_type}")
    
    if include_difficulty and parsed.difficulty:
        lines.append(f"[LEVEL  ]: {parsed.difficulty}")
    # Show recommendations
    if parsed.recommendations:
        lines.append(f"[RECO   ]: {', '.join(parsed.recommendations)}")
    else:
        lines.append("[RECO   ]: none")
    # Add the answer
    lines.append(f"\nStatsAgent[{parsed.agent_name}]: {parsed.answer}\n")
    lines.append(f"[Latency: {latency:.3f} seconds]")
    
    return "\n".join(lines)


def format_compact_output(
    parsed: ParsedAgentResponse,
    latency: float,
) -> str:
    lines = []
    
    if parsed.domain:
        lines.append(f"[DOMAIN ]: {parsed.domain}")
    
    if parsed.recommendations:
        lines.append(f"[RECO   ]: {', '.join(parsed.recommendations)}")
    else:
        lines.append("[RECO   ]: none")
    
    lines.append(f"\nStatsAgent[{parsed.agent_name}]: {parsed.answer}\n")
    lines.append(f"[Latency: {latency:.3f} seconds]")
    
    return "\n".join(lines)


def format_full_output(
    parsed: ParsedAgentResponse,
    latency: float,
) -> str:
    return format_agent_output(
        parsed,
        latency,
        include_task=True,
        include_difficulty=True,
    )


# Convenience functions

def parse_and_format_plain_text(
    raw_response: str,
    latency: float,
    agent_name: str = "Agent",
    include_task: bool = True,
    include_difficulty: bool = True,
) -> str:
    parsed = parse_plain_text_response(raw_response, agent_name)
    return format_agent_output(parsed, latency, include_task, include_difficulty)


def parse_and_format_json(
    json_data: Dict[str, Any],
    latency: float,
    agent_name: str = "Agent",
    include_task: bool = True,
    include_difficulty: bool = True,
) -> str:
    parsed = parse_json_response(json_data, agent_name)
    return format_agent_output(parsed, latency, include_task, include_difficulty)
