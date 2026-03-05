"""Multi-agent router for coordinating specialist agents."""

import time
import re
from typing import Dict, List, Optional, Tuple, Any, Literal
from dataclasses import dataclass, field
from enum import Enum
import sys
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from pydantic import BaseModel, Field
import numpy as np
from sentence_transformers import SentenceTransformer

from stats_agent.stats_agent_complex import run_statistics_agent_structured_timed, StatsAgentResponse
from ML_agent.ML_agent_complex import run_ml_agent_structured_timed, MLAgentResponse
from data_agent.data_agent_complex import run_data_eng_agent_structured_timed
from visual_agent.visual_agent_complex import run_viz_agent_structured_timed, VizAgentResponse


# ============================================================================
# Response Schemas
# ============================================================================

class UnifiedAgentResponse(BaseModel):
    
    agent_name: str = Field(..., description="Name of responding agent")
    domain: Literal["IN_DOMAIN", "OUT_OF_DOMAIN"]
    task_type: str
    difficulty: Literal["intro", "intermediate", "advanced"]
    answer: str
    recommend: List[str] = Field(default_factory=list, description="Recommended agents for follow-up")
    files_analyzed: List[str] = Field(default_factory=list)
    code_executions: List[dict] = Field(default_factory=list)
    visualizations: List[str] = Field(default_factory=list)
    latency: float = 0.0


class RoutingTrace(BaseModel):
    
    step: int
    action: str  # "classify", "route", "follow_up", "synthesize"
    agent: str
    reasoning: str
    timestamp: float


class RoutingResponse(BaseModel):
    
    primary_agent: str
    primary_response: UnifiedAgentResponse
    
    secondary_agents: List[str] = Field(default_factory=list)
    secondary_responses: Dict[str, UnifiedAgentResponse] = Field(default_factory=dict)
    
    routing_trace: List[RoutingTrace] = Field(default_factory=list)
    
    # Multi-agent synthesis
    final_synthesis: str
    was_multi_agent: bool
    
    # Metadata
    total_latency: float = 0.0
    agent_latencies: Dict[str, float] = Field(default_factory=dict)
    conversation_id: Optional[str] = None


class RoutingMetrics(BaseModel):
    
    total_queries: int = 0
    queries_by_agent: Dict[str, int] = Field(default_factory=dict)
    primary_correct_rate: float = 0.0  # % where primary domain matched
    multi_agent_percentage: float = 0.0
    avg_routing_depth: float = 0.0
    max_routing_depth: int = 0
    timeouts: int = 0
    errors: int = 0
    total_latency: float = 0.0


# ============================================================================
# Semantic Similarity Classifier
# ============================================================================

class SemanticSimilarityClassifier:
    """Routes queries using semantic similarity to agent capability descriptions."""
    
    AGENT_DESCRIPTIONS = {
        "StatisticsAgent": (
            "Statistical inference, hypothesis testing, confidence intervals, "
            "regression analysis, distribution testing, sample size calculation, "
            "experimental design, p-values, significance testing, bayesian analysis, "
            "power analysis, correlation analysis, anova, chi-square tests"
        ),
        "MLAgent": (
            "Machine learning model training, deep learning, neural networks, "
            "random forests, decision trees, gradient descent, hyperparameter tuning, "
            "cross-validation, feature engineering, model evaluation, overfitting, "
            "clustering, classification, regression, ensemble methods, svm, optimization"
        ),
        "DataEngAgent": (
            "Data engineering, SQL databases, schema design, ETL pipelines, "
            "data cleaning, data warehousing, data lakes, performance tuning, "
            "database optimization, data migration, data integration, normalization, "
            "indexing, query optimization, data quality"
        ),
        "VizAgent": (
            "Data visualization, creating plots and charts, dashboard design, "
            "histograms, scatter plots, heatmaps, line charts, bar charts, "
            "pie charts, exploratory data analysis, infographics, storytelling, "
            "visual communication, chart selection, design aesthetics"
        ),
    }
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        print(f"[SemanticClassifier] Loading embedding model: {model_name}...", flush=True)
        self.model = SentenceTransformer(model_name)
        
        # Encode agent descriptions once
        self.agent_embeddings = {}
        for agent, description in self.AGENT_DESCRIPTIONS.items():
            embedding = self.model.encode(description, convert_to_numpy=True)
            self.agent_embeddings[agent] = embedding
        
        print(f"[SemanticClassifier] Ready. {len(self.agent_embeddings)} agents loaded.", flush=True)
    
    def classify(self, query: str) -> Tuple[str, float]:
        # Encode the query
        query_embedding = self.model.encode(query, convert_to_numpy=True)
        
        similarities = {}
        for agent, agent_embedding in self.agent_embeddings.items():
            similarity = float(
                np.dot(query_embedding, agent_embedding) / 
                (np.linalg.norm(query_embedding) * np.linalg.norm(agent_embedding))
            )
            similarities[agent] = similarity
        
        best_agent = max(similarities, key=similarities.get)
        best_score = similarities[best_agent]
        
        return (best_agent, best_score)


# ============================================================================
# Performance-Weighted Adaptive Classifier
# ============================================================================

class PerformanceWeightedClassifier:
    """Combines semantic similarity with adaptive performance weighting."""
    
    def __init__(self, semantic_classifier: SemanticSimilarityClassifier, learning_rate: float = 0.1):
        self.semantic_classifier = semantic_classifier
        self.learning_rate = learning_rate
        # Track performance metrics per agent
        self.agent_stats = {
            agent: {
                "in_domain_count": 0,
                "total_count": 0,
                "in_domain_rate": 0.5,
                "accuracy_count": 0,
                "accuracy_rate": 0.5,
                "combined_score": 0.5,
                "avg_latency": 0.0,
                "total_latency": 0.0,
            }
            for agent in semantic_classifier.AGENT_DESCRIPTIONS.keys()
        }
    
    def classify(self, query: str) -> Tuple[str, float]:
        query_embedding = self.semantic_classifier.model.encode(query, convert_to_numpy=True)
        similarities = {}
        
        for agent, agent_embedding in self.semantic_classifier.agent_embeddings.items():
            similarity = float(
                np.dot(query_embedding, agent_embedding) / 
                (np.linalg.norm(query_embedding) * np.linalg.norm(agent_embedding))
            )
            similarities[agent] = similarity
        
        # Weight by agent performance history
        weighted_scores = {}
        for agent, semantic_score in similarities.items():
            accuracy_rate = self.agent_stats[agent]["accuracy_rate"]
            in_domain_rate = self.agent_stats[agent]["in_domain_rate"]
            latency_score = 1.0 / (1.0 + self.agent_stats[agent]["avg_latency"])
            
            # 20% semantic + 35% accuracy + 35% in_domain + 10% latency
            weighted_score = (
                semantic_score * 0.20 +
                (accuracy_rate * 0.35) +
                (in_domain_rate * 0.35) +
                (latency_score * 0.10)
            )
            weighted_scores[agent] = weighted_score
        
        best_agent = max(weighted_scores, key=weighted_scores.get)
        best_score = weighted_scores[best_agent]
        
        return (best_agent, best_score)
    
    def record_result(self, agent: str, was_in_domain: bool, was_accurate: bool, latency: float) -> None:
        if agent not in self.agent_stats:
            return
        
        stats = self.agent_stats[agent]
        
        stats["total_count"] += 1
        
        if was_in_domain:
            stats["in_domain_count"] += 1
        
        if was_accurate:
            stats["accuracy_count"] += 1
        
        # Update IN_DOMAIN rate (exponential moving average)
        in_domain_rate = stats["in_domain_count"] / stats["total_count"]
        stats["in_domain_rate"] = (
            stats["in_domain_rate"] * (1 - self.learning_rate) +
            in_domain_rate * self.learning_rate
        )
        
        # Update accuracy rate (exponential moving average)
        accuracy_rate = stats["accuracy_count"] / stats["total_count"]
        stats["accuracy_rate"] = (
            stats["accuracy_rate"] * (1 - self.learning_rate) +
            accuracy_rate * self.learning_rate
        )
        
        # Combined score: 50% IN_DOMAIN + 50% accuracy
        stats["combined_score"] = (
            (stats["in_domain_rate"] + stats["accuracy_rate"]) / 2.0
        )
        
        # Update latency (exponential moving average)
        stats["total_latency"] += latency
        stats["avg_latency"] = (
            stats["avg_latency"] * (1 - self.learning_rate) +
            latency * self.learning_rate
        )
    
    def get_stats(self) -> Dict[str, Dict]:
        return self.agent_stats
    
    def reset_stats(self) -> None:
        for agent in self.agent_stats:
            self.agent_stats[agent] = {
                "in_domain_count": 0,
                "total_count": 0,
                "in_domain_rate": 0.5,
                "accuracy_count": 0,
                "accuracy_rate": 0.5,
                "combined_score": 0.5,
                "avg_latency": 0.0,
                "total_latency": 0.0,
            }


# ============================================================================
# LLM-Assisted Meta-Routing Classifier
# ============================================================================

class LLMMetaClassifier:
    """Uses an LLM to select the best agent for a query."""
    
    def __init__(self, model_name: str = "llama3.1", ollama_url: str = "http://localhost:11434"):
        import requests
        
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.requests = requests
        
        self.agent_descriptions = {
            "StatisticsAgent": (
                "Handles statistical inference, hypothesis testing, confidence intervals, "
                "regression analysis, distribution testing, sample size calculation, "
                "experimental design, p-values, significance testing, bayesian analysis"
            ),
            "MLAgent": (
                "Handles machine learning model training, deep learning, neural networks, "
                "random forests, decision trees, hyperparameter tuning, cross-validation, "
                "feature engineering, model evaluation, clustering, classification"
            ),
            "DataEngAgent": (
                "Handles data engineering, SQL databases, schema design, ETL pipelines, "
                "data cleaning, data warehousing, data lakes, performance tuning, "
                "database optimization, data migration, data integration"
            ),
            "VizAgent": (
                "Handles data visualization, creating plots and charts, dashboard design, "
                "histograms, scatter plots, heatmaps, line charts, pie charts, "
                "exploratory data analysis, infographics, storytelling"
            ),
        }
        
        print(f"[LLMMetaClassifier] Using model: {model_name}", flush=True)
        self._verify_ollama_connection()
    
    def _verify_ollama_connection(self) -> bool:
        try:
            response = self.requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                print(f"[LLMMetaClassifier] Connected to Ollama at {self.ollama_url}", flush=True)
                return True
        except Exception as e:
            print(f"[LLMMetaClassifier] Warning: Could not connect to Ollama: {e}", flush=True)
        return False
    
    def classify(self, query: str) -> Tuple[str, float]:
        system_prompt = f"""You are an intelligent router that selects the best agent for user queries.

Available agents:
"""
        for agent_name, description in self.agent_descriptions.items():
            system_prompt += f"\n- {agent_name}: {description}"
        
        system_prompt += """

You MUST respond with ONLY the agent name (no explanation, no extra text).
Choose the single best agent for the query. Respond with just the agent name."""
        
        try:
            response = self.requests.post(
                f"{self.ollama_url}/v1/chat/completions",
                json={
                    "model": self.model_name,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": query}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 50,
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                agent_choice = result["choices"][0]["message"]["content"].strip()
                
                valid_agents = list(self.agent_descriptions.keys())
                
                if agent_choice in valid_agents:
                    return (agent_choice, 0.9)
                
                # Normalize for matching
                normalized_choice = agent_choice.replace(" ", "").lower()
                
                for valid_agent in valid_agents:
                    if normalized_choice == valid_agent.lower():
                        return (valid_agent, 0.9)
                    
                    if valid_agent.lower() in normalized_choice:
                        return (valid_agent, 0.85)
                    
                    if normalized_choice in valid_agent.lower():
                        return (valid_agent, 0.8)
                
                # Fallback: partial character matching
                best_match = None
                best_score = 0
                for valid_agent in valid_agents:
                    # Count matching characters as a simple heuristic
                    matching_chars = sum(1 for c in normalized_choice if c in valid_agent.lower())
                    score = matching_chars / max(len(normalized_choice), len(valid_agent))
                    if score > best_score:
                        best_score = score
                        best_match = valid_agent
                
                if best_match and best_score > 0.5:
                    return (best_match, 0.7)
                
                return (valid_agents[0], 0.5)
            else:
                print(f"[LLMMetaClassifier] Ollama error: {response.status_code}")
                return ("StatisticsAgent", 0.5)
        
        except Exception as e:
            print(f"[LLMMetaClassifier] Error calling Ollama: {e}")
            return ("StatisticsAgent", 0.5)  # Safe fallback


# ============================================================================
# Response Adapters
# ============================================================================

def _adapt_stats_response(resp: StatsAgentResponse, latency: float) -> UnifiedAgentResponse:
    return UnifiedAgentResponse(
        agent_name="StatisticsAgent",
        domain=resp.domain,
        task_type=resp.task_type,
        difficulty=resp.difficulty,
        answer=resp.answer,
        recommend=resp.recommend,
        files_analyzed=getattr(resp, 'files_analyzed', []),
        code_executions=getattr(resp, 'code_executions', []),
        visualizations=getattr(resp, 'visualizations', []),
        latency=latency,
    )


def _adapt_ml_response(resp: MLAgentResponse, latency: float) -> UnifiedAgentResponse:
    return UnifiedAgentResponse(
        agent_name="MLAgent",
        domain=resp.domain,
        task_type=resp.task_type,
        difficulty=resp.difficulty,
        answer=resp.answer,
        recommend=resp.recommend,
        files_analyzed=getattr(resp, 'files_analyzed', []),
        code_executions=getattr(resp, 'code_executions', []),
        visualizations=getattr(resp, 'visualizations', []),
        latency=latency,
    )


def _adapt_viz_response(resp: VizAgentResponse, latency: float) -> UnifiedAgentResponse:
    return UnifiedAgentResponse(
        agent_name="VizAgent",
        domain=resp.domain,
        task_type=resp.task_type,
        difficulty=resp.difficulty,
        answer=resp.answer,
        recommend=resp.recommend,
        files_analyzed=getattr(resp, 'files_analyzed', []),
        code_executions=getattr(resp, 'code_executions', []),
        visualizations=getattr(resp, 'visualizations', []),
        latency=latency,
    )


def _adapt_generic_response(agent_name: str, resp: Any, latency: float) -> UnifiedAgentResponse:
    return UnifiedAgentResponse(
        agent_name=agent_name,
        domain=getattr(resp, 'domain', 'OUT_OF_DOMAIN'),
        task_type=getattr(resp, 'task_type', 'unknown'),
        difficulty=getattr(resp, 'difficulty', 'intermediate'),
        answer=getattr(resp, 'answer', str(resp)),
        recommend=getattr(resp, 'recommend', []),
        files_analyzed=getattr(resp, 'files_analyzed', []),
        code_executions=getattr(resp, 'code_executions', []),
        visualizations=getattr(resp, 'visualizations', []),
        latency=latency,
    )


# ============================================================================
# Response Synthesis
# ============================================================================

def _synthesize_responses(
    primary: UnifiedAgentResponse,
    secondary: Dict[str, UnifiedAgentResponse]
) -> str:
    if not secondary:
        return primary.answer
    
    lines = []
    lines.append("=== Integrated Response ===\n")
    
    lines.append(f"Primary Agent ({primary.agent_name}):")
    lines.append(primary.answer)
    lines.append("")
    
    if secondary:
        lines.append("Supporting Perspectives:")
        for agent_name, response in secondary.items():
            # Extract key insight from answer (first 2 sentences)
            sentences = response.answer.split(". ")
            key_insight = ". ".join(sentences[:2]) + "." if sentences else response.answer[:100]
            lines.append(f"  • {agent_name}: {key_insight}")
        lines.append("")
    
    lines.append("Integrated Recommendation:")
    if primary.domain == "IN_DOMAIN":
        lines.append("1. Follow the primary agent's guidance for the main line of reasoning.")
    else:
        lines.append("1. Treat the primary agent as a triage step; rely more heavily on in-domain supporting agents.")

    if secondary:
        lines.append(f"2. Incorporate supporting perspectives from {', '.join(secondary.keys())}.")
        lines.append("3. Use agreement or disagreement between agents to gauge confidence in the conclusion.")

    
    return "\n".join(lines)


# ============================================================================
# Main Router Class
# ============================================================================

class RouterDecider:
    """Multi-agent orchestrator with configurable routing methods."""
    
    def __init__(self, max_depth: int = 3, routing_method: str = "semantic"):
        self.max_depth = max_depth
        self.routing_method = routing_method
        self.conversation_history = []
        self.metrics = RoutingMetrics()
        
        # Agent dispatch table
        self.agent_dispatch = {
            "StatisticsAgent": self._dispatch_stats,
            "MLAgent": self._dispatch_ml,
            "DataEngAgent": self._dispatch_data_eng,
            "VizAgent": self._dispatch_viz,
        }
        
        # Initialize semantic classifier
        self.semantic_classifier = SemanticSimilarityClassifier()
        
        self.performance_classifier = PerformanceWeightedClassifier(
            self.semantic_classifier,
            learning_rate=0.15
        )
        
        self.llm_classifier = None
        
        if routing_method == "performance":
            self.classifier = self.performance_classifier
        elif routing_method == "llm":
            self.llm_classifier = LLMMetaClassifier()
            self.classifier = self.llm_classifier
        else:  # semantic (default)
            self.classifier = self.semantic_classifier
    
    def route(
        self,
        query: str,
        files: Optional[List[str]] = None,
        prefer_agent: Optional[str] = None,
        depth: int = 0,
    ) -> RoutingResponse:
        start_time = time.time()
        trace = []
        
        # Check depth limit
        if depth >= self.max_depth:
            return self._error_response(
                f"Max routing depth ({self.max_depth}) reached. Query too complex.",
                trace,
                start_time
            )
        # Step 1: Classify/select primary agent
        if prefer_agent and prefer_agent in self.agent_dispatch:
            primary_agent = prefer_agent
            trace.append(RoutingTrace(
                step=1,
                action="classify",
                agent=primary_agent,
                reasoning=f"User specified agent: {prefer_agent}",
                timestamp=time.time()
            ))
        else:
            primary_agent, score = self.classifier.classify(query)
            if not primary_agent:
                primary_agent = "VizAgent"

            if self.routing_method == "semantic":
                reason = f"Semantic similarity routing (similarity: {score:.3f})"
            elif self.routing_method == "performance":
                reason = f"Performance-weighted routing (score: {score:.3f})"
            elif self.routing_method == "llm":
                reason = f"LLM meta-routing (confidence: {score:.3f})"
            else:
                reason = f"Routing via {self.routing_method} (score: {score:.3f})"

            trace.append(RoutingTrace(
                step=1,
                action="classify",
                agent=primary_agent,
                reasoning=reason,
                timestamp=time.time()
            ))

        
        # Step 2: Dispatch to primary agent
        trace.append(RoutingTrace(
            step=2,
            action="route",
            agent=primary_agent,
            reasoning=f"Routing primary query to {primary_agent}",
            timestamp=time.time()
        ))
        
        try:
            primary_response, primary_latency = self._dispatch_agent(
                primary_agent, query, files
            )
        except Exception as e:
            return self._error_response(
                f"Error calling {primary_agent}: {str(e)}",
                trace,
                start_time
            )
        
        agent_latencies = {primary_agent: primary_latency}
        # Step 3: Check recommendations
        secondary_agents = []
        secondary_responses = {}
        
        if primary_response.recommend and len(primary_response.recommend) > 0:
            trace.append(RoutingTrace(
                step=3,
                action="follow_up",
                agent="Router",
                reasoning=f"Primary agent recommends: {', '.join(primary_response.recommend)}",
                timestamp=time.time()
            ))
            
            # Dispatch to recommended agents
            for rec_agent in primary_response.recommend:
                if rec_agent in self.agent_dispatch and rec_agent != primary_agent:
                    secondary_agents.append(rec_agent)
                    try:
                        sec_response, sec_latency = self._dispatch_agent(
                            rec_agent, query, files
                        )
                        secondary_responses[rec_agent] = sec_response
                        agent_latencies[rec_agent] = sec_latency
                    except Exception as e:
                        print(f"[Warning] Secondary agent {rec_agent} failed: {e}")
        
        # Step 4: Synthesize if multi-agent
        final_synthesis = primary_response.answer
        was_multi_agent = len(secondary_responses) > 0
        
        if was_multi_agent:
            trace.append(RoutingTrace(
                step=4,
                action="synthesize",
                agent="Router",
                reasoning=f"Synthesizing responses from {primary_agent} + {list(secondary_responses.keys())}",
                timestamp=time.time()
            ))
            final_synthesis = _synthesize_responses(primary_response, secondary_responses)
        
        # Step 5: Update metrics
        self.metrics.total_queries += 1
        self.metrics.queries_by_agent[primary_agent] = \
            self.metrics.queries_by_agent.get(primary_agent, 0) + 1
        
        if primary_response.domain == "IN_DOMAIN":
            self.metrics.primary_correct_rate = (
                self.metrics.primary_correct_rate * 0.95 + 0.05
            )
        else:
            self.metrics.primary_correct_rate = (
                self.metrics.primary_correct_rate * 0.95
            )
        
        if was_multi_agent:
            self.metrics.multi_agent_percentage = (
                (self.metrics.multi_agent_percentage * (self.metrics.total_queries - 1) +
                 1.0) / self.metrics.total_queries
            )
        
        # Step 6: Record performance for adaptive routing
        if self.routing_method == "performance" and isinstance(self.classifier, PerformanceWeightedClassifier):
            was_in_domain = primary_response.domain == "IN_DOMAIN"
            self.classifier.record_result(primary_agent, was_in_domain, primary_latency)
        
        # Build final response
        total_latency = time.time() - start_time
        
        response = RoutingResponse(
            primary_agent=primary_agent,
            primary_response=primary_response,
            secondary_agents=secondary_agents,
            secondary_responses=secondary_responses,
            routing_trace=trace,
            final_synthesis=final_synthesis,
            was_multi_agent=was_multi_agent,
            total_latency=total_latency,
            agent_latencies=agent_latencies,
        )
        
        # Store in conversation history
        self.conversation_history.append({
            "query": query,
            "response": response,
            "timestamp": time.time(),
        })
        
        return response
    
    def _dispatch_agent(
        self,
        agent_name: str,
        query: str,
        files: Optional[List[str]] = None
    ) -> Tuple[UnifiedAgentResponse, float]:
        dispatch_fn = self.agent_dispatch.get(agent_name)
        if not dispatch_fn:
            raise ValueError(f"Unknown agent: {agent_name}")
        
        return dispatch_fn(query, files)
    
    def _dispatch_stats(
        self, query: str, files: Optional[List[str]] = None
    ) -> Tuple[UnifiedAgentResponse, float]:
        resp, latency = run_statistics_agent_structured_timed(query, file_paths=files)
        return _adapt_stats_response(resp, latency), latency
    
    def _dispatch_ml(
        self, query: str, files: Optional[List[str]] = None
    ) -> Tuple[UnifiedAgentResponse, float]:
        resp, latency = run_ml_agent_structured_timed(query, file_paths=files)
        return _adapt_ml_response(resp, latency), latency
    
    def _dispatch_data_eng(
        self, query: str, files: Optional[List[str]] = None
    ) -> Tuple[UnifiedAgentResponse, float]:
        resp, latency = run_data_eng_agent_structured_timed(query, file_paths=files)
        return _adapt_generic_response("DataEngAgent", resp, latency), latency
    
    def _dispatch_viz(
        self, query: str, files: Optional[List[str]] = None
    ) -> Tuple[UnifiedAgentResponse, float]:
        resp, latency = run_viz_agent_structured_timed(query, file_paths=files)
        return _adapt_viz_response(resp, latency), latency
    
    def _error_response(
        self,
        error_msg: str,
        trace: List[RoutingTrace],
        start_time: float
    ) -> RoutingResponse:
        self.metrics.errors += 1
        
        return RoutingResponse(
            primary_agent="ERROR",
            primary_response=UnifiedAgentResponse(
                agent_name="Router",
                domain="OUT_OF_DOMAIN",
                task_type="error",
                difficulty="intro",
                answer=f"Router Error: {error_msg}",
                recommend=[],
            ),
            routing_trace=trace,
            final_synthesis=f"Router Error: {error_msg}",
            was_multi_agent=False,
            total_latency=time.time() - start_time,
        )
    
    def get_metrics(self) -> RoutingMetrics:
        return self.metrics
    
    def reset_metrics(self):
        self.metrics = RoutingMetrics()
    
    def get_performance_stats(self) -> Dict[str, Dict]:
        if isinstance(self.classifier, PerformanceWeightedClassifier):
            return self.classifier.get_stats()
        return {}
    
    def reset_performance_stats(self):
        if isinstance(self.classifier, PerformanceWeightedClassifier):
            self.classifier.reset_stats()


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    print("=" * 70)
    print("  Multi-Agent Router / Decider System")
    print("=" * 70)
    print("\nUsage:")
    print("  Your query")
    print("  FILE: path/to/file.csv Your query (with file)")
    print("  @agent_name Your query (prefer specific agent)")
    print("  metrics (show routing metrics)")
    print("  perf_stats (show performance stats - performance routing only)")
    print("  method semantic|performance|llm (switch routing method)")
    print("  exit/quit (leave)\n")
    
    router = RouterDecider(routing_method="semantic")
    print(f"[Router] Using routing method: {router.routing_method}\n")
    
    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        
        if user_input.lower() in {"exit", "quit"}:
            print("\nGoodbye!")
            break
        
        # Handle method switching
        if user_input.lower().startswith("method"):
            parts = user_input.split()
            if len(parts) >= 2:
                new_method = parts[1].lower()
                if new_method in {"semantic", "performance", "llm"}:
                    router.routing_method = new_method
                    if new_method == "performance":
                        router.classifier = router.performance_classifier
                    elif new_method == "llm":
                        if router.llm_classifier is None:
                            print("[Router] Initializing LLM meta-classifier...")
                            router.llm_classifier = LLMMetaClassifier()
                        router.classifier = router.llm_classifier
                    else:  # semantic
                        router.classifier = router.semantic_classifier
                    print(f"[Router] Switched to {new_method} routing method.\n")
                else:
                    print("[Error] Unknown method. Use 'semantic', 'performance', or 'llm'.\n")
            else:
                print(f"[Router] Current method: {router.routing_method}\n")
            continue
        
        if user_input.lower() == "metrics":
            metrics = router.get_metrics()
            print(f"\n[Routing Metrics]")
            print(f"  Total queries: {metrics.total_queries}")
            print(f"  Queries by agent: {dict(metrics.queries_by_agent)}")
            print(f"  Primary correct rate: {metrics.primary_correct_rate:.1%}")
            print(f"  Multi-agent %: {metrics.multi_agent_percentage:.1%}")
            print(f"  Errors: {metrics.errors}\n")
            continue
        
        if user_input.lower() == "perf_stats":
            perf_stats = router.get_performance_stats()
            if perf_stats:
                print(f"\n[Performance Statistics]")
                for agent, stats in perf_stats.items():
                    print(f"  {agent}:")
                    print(f"    In-domain matches: {stats['in_domain_count']}/{stats['total_count']}")
                    print(f"    Success rate: {stats['success_rate']:.2%}")
                    print(f"    Avg latency: {stats['avg_latency']:.3f}s")
                print()
            else:
                print("[Info] Performance stats only available with 'performance' routing method.\n")
            continue
        
        # Parse FILE: and @agent prefixes
        file_pattern = r'FILE:\s*([\S]+)'
        file_matches = re.findall(file_pattern, user_input)
        files = file_matches if file_matches else None
        
        prefer_agent = None
        agent_pattern = r'^@(\w+)\s+'
        agent_match = re.match(agent_pattern, user_input)
        if agent_match:
            prefer_agent = agent_match.group(1)
            user_input = re.sub(agent_pattern, '', user_input).strip()
        
        # Remove FILE: prefixes
        query = re.sub(file_pattern, '', user_input).strip()
        
        if not query:
            print("[Error] No query provided.\n")
            continue
        
        try:
            # Route the query
            print(f"\n[Router] Processing query...", end="", flush=True)
            response = router.route(query, files=files, prefer_agent=prefer_agent)
            
            # Display response
            print(f"\r[Router] Routing complete.               \n")
            
            print(f"[Primary Agent]: {response.primary_agent}")
            print(f"[Domain]: {response.primary_response.domain}")
            print(f"[Task Type]: {response.primary_response.task_type}")
            print(f"[Difficulty]: {response.primary_response.difficulty}")
            
            if response.secondary_agents:
                print(f"[Secondary Agents]: {', '.join(response.secondary_agents)}")
            
            print(f"\n[Answer]:\n{response.final_synthesis}\n")
            
            # Show routing trace
            print(f"[Routing Trace] ({len(response.routing_trace)} steps):")
            for trace in response.routing_trace:
                print(f"  Step {trace.step}: {trace.action.upper()} → {trace.agent}")
                print(f"    Reason: {trace.reasoning}")
            
            print(f"\n[Latency]: {response.total_latency:.3f}s")
            if response.agent_latencies:
                for agent, latency in response.agent_latencies.items():
                    print(f"  {agent}: {latency:.3f}s")
            
            print()
        
        except Exception as e:
            print(f"\n[Error] {str(e)}\n")


if __name__ == "__main__":
    main()
