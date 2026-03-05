# Multi-Agent Router/Decider Architecture

## Overview

The **Router/Decider** is the orchestration layer that coordinates all 5 specialist agents:
1. **StatisticsAgent** - Statistical inference, hypothesis testing, confidence intervals
2. **MLAgent** - Machine learning, model training, evaluation
3. **DataEngAgent** - Data engineering, SQL, ETL, schemas
4. **VizAgent** - Data visualization, charts, dashboards
5. **GeneralInfoAgent** - General knowledge, travel, news, etc.

The router's responsibility:
- **Classify** incoming user queries into agent domains
- **Route** queries to the most appropriate agent(s)
- **Orchestrate** multi-agent workflows (sequential handoffs, parallel dispatch)
- **Follow recommendations** - if an agent recommends another agent, route accordingly
- **Synthesize** responses - combine outputs from multiple agents when needed
- **Handle failures** - gracefully degrade and suggest alternatives

---

## 1. Query Routing Logic

### 1.1 Classification Pipeline

Each user query flows through a **classification cascade**:

```
User Query
    ↓
[Pre-process & extract metadata]
    ↓
[Query to Classifier LLM or rule-based detector]
    ↓
[PRIMARY_AGENT, PRIMARY_DOMAIN, CONFIDENCE, SECONDARY_AGENTS]
    ↓
[Route to PRIMARY_AGENT]
    ↓
[Agent processes & returns response with DOMAIN, RECOMMEND fields]
    ↓
[Router checks RECOMMEND field]
    ↓
[IF RECOMMEND is non-empty, dispatch follow-up queries to those agents]
    ↓
[Synthesize final response]
```

### 1.2 Agent Selection Heuristics

**Rule-based quick classification** (before calling LLM):

```python
Query contains: "hypothesis test", "t-test", "ANOVA", "confidence interval", "p-value"
    → DEFAULT: StatisticsAgent
    
Query contains: "train model", "random forest", "neural network", "cross-validation", "hyperparameter"
    → DEFAULT: MLAgent
    
Query contains: "SQL", "database", "schema", "ETL", "data pipeline", "clean data"
    → DEFAULT: DataEngAgent
    
Query contains: "plot", "chart", "dashboard", "visualize", "histogram", "scatter"
    → DEFAULT: VizAgent
    
Query contains: "travel", "news", "recipe", "weather", "how to"
    → DEFAULT: GeneralInfoAgent
    
NO MATCH → Use LLM classifier
```

**LLM-based fallback**:
If heuristics don't match, call a lightweight classifier LLM:
- Prompt: "Classify this query into ONE of: Statistics, ML, DataEng, Visualization, General"
- Returns: Agent name + confidence score

---

## 2. Router/Decider Implementation

### 2.1 Core Components

#### RouterDecider Class

```python
class RouterDecider:
    """Orchestrates all agents, routes queries, synthesizes responses."""
    
    def __init__(self):
        self.agents = {
            "StatisticsAgent": run_statistics_agent_structured_timed,
            "MLAgent": run_ml_agent_structured_timed,
            "DataEngAgent": run_data_eng_agent_structured_timed,
            "VizAgent": run_viz_agent_structured_timed,
            "GeneralInfoAgent": run_general_info_agent_structured_timed,  # TODO: Implement
        }
        self.classifier = LLMClassifier()  # Lightweight domain classifier
        self.conversation_history = []  # Track multi-turn workflows
        
    def route(
        self,
        query: str,
        files: Optional[List[str]] = None,
        prefer_agent: Optional[str] = None,  # User hint
        depth: int = 0,  # Prevent infinite loops
    ) -> RoutingResponse:
        """
        Main entry point. Routes query to appropriate agent(s).
        
        Args:
            query: User input
            files: Optional file paths to analyze
            prefer_agent: If user specifies agent name, use it
            depth: Current recursion depth (prevent infinite loops)
        
        Returns:
            RoutingResponse with agent responses, routing trace, recommendations
        """
```

#### RoutingResponse Schema

```python
class RoutingResponse(BaseModel):
    """Result of router's decision and agent dispatch."""
    
    primary_agent: str
    primary_response: AgentResponse  # Unified response schema
    
    secondary_agents: List[str] = []
    secondary_responses: Dict[str, AgentResponse] = {}
    
    routing_trace: List[str]  # Log of routing decisions
    follow_up_recommended: bool
    follow_up_agents: List[str] = []
    
    final_synthesis: str  # Merged answer if multiple agents used
    
    total_latency: float
    agent_latencies: Dict[str, float]
```

#### UnifiedAgentResponse (Wrapper)

All agent responses are normalized to this schema:

```python
class UnifiedAgentResponse(BaseModel):
    """Normalized response format from any agent."""
    
    agent_name: str
    domain: str  # "IN_DOMAIN", "OUT_OF_DOMAIN"
    task_type: str
    difficulty: str
    answer: str
    
    # Optional fields from complex/enhanced agents
    recommend: List[str] = []
    files_analyzed: List[str] = []
    code_executions: List[dict] = []
    visualizations: List[str] = []
```

### 2.2 Routing Decision Tree

```
Input: User Query + Optional Files

Step 1: Quick Heuristic Classification
   - Check keywords → potential agent
   - Store candidate with score

Step 2: Verify with Structured Response
   - Call candidate agent with query
   - Agent returns DOMAIN and RECOMMEND fields
   
Step 3: Evaluate Recommendation
   IF agent DOMAIN == "IN_DOMAIN":
       PRIMARY_RESPONSE = agent's answer
       Check RECOMMEND field:
           IF RECOMMEND is non-empty:
               → Follow-up dispatch (secondary agents)
       ELSE:
           → Return primary response as final
   
   ELSE (agent DOMAIN == "OUT_OF_DOMAIN"):
       → Agent should have recommended better agent(s)
       → Route to RECOMMEND[0] as primary
       → Log as routing correction

Step 4: Multi-Agent Synthesis (if secondary agents called)
   - Collect all secondary responses
   - Use synthesis prompt to merge insights
   - Return unified final answer

Step 5: Return RoutingResponse
```

---

## 3. Multi-Agent Workflows

### 3.1 Sequential Handoff

**Scenario**: Stats question that needs visualization

```
User: "Test if my data is normal, then show me a histogram"

Router decision:
  1. Route to StatisticsAgent → normality test + recommendation to VizAgent
  2. StatisticsAgent returns RECOMMEND: ["VizAgent"]
  3. Router extracts data insights from Stats response
  4. Router routes to VizAgent: "Here's the data, make a histogram"
  5. VizAgent creates plot
  6. Router synthesizes: "Normality test shows p-value=0.02 (NOT normal). 
     Histogram shows [description]. Recommendation: consider log transformation."
```

### 3.2 Parallel Dispatch

**Scenario**: Complex analysis needing multiple perspectives

```
User: "Build a predictive model for customer churn, then validate 
       the approach statistically and design a dashboard"

Router decision:
  1. Route to MLAgent (primary)
  2. MLAgent returns RECOMMEND: ["StatisticsAgent", "VizAgent"]
  3. Router dispatches in parallel:
     - StatisticsAgent: validate model's statistical assumptions
     - VizAgent: design dashboard for results
  4. Collect all responses
  5. Synthesize: "ML approach is [method]. Statistical validation: [results]. 
     Dashboard layout: [design]. Recommendation: [combined insights]"
```

### 3.3 Clarification & Routing Correction

**Scenario**: User asks something ambiguous, agent recommends different agent

```
User: "How should I approach feature selection?"

Router decision:
  1. Heuristic hints: MLAgent (keywords: "feature")
  2. Route to MLAgent
  3. MLAgent returns DOMAIN: "OUT_OF_DOMAIN", RECOMMEND: ["DataEngAgent"]
  4. Router logs correction: "Reclassified as DataEng"
  5. Route to DataEngAgent
  6. Return DataEngAgent's response with note: 
     "Routed to DataEngAgent (initial guess was MLAgent, corrected based on feedback)"
```

---

## 4. Response Synthesis

When multiple agents provide insights, router **synthesizes** via:

### 4.1 Synthesis Strategy

**Template**:
```
Primary Agent ({agent_name}):
{primary_answer}

Supporting Perspectives:
  • {secondary_agent_1}: {key_insight_1}
  • {secondary_agent_2}: {key_insight_2}

Integrated Recommendation:
{merged_guidance}
```

**Example**:
```
Primary Agent (MLAgent):
Random Forest with 10-fold CV achieves 82% accuracy. Feature importance 
shows credit_utilization, payment_history, account_age are top 3.

Supporting Perspectives:
  • StatisticsAgent: Feature importance differences are significant (p<0.05) 
    via permutation test. Model assumptions: moderate multicollinearity detected.
  • VizAgent: Dashboard shows importance rankings with confidence bands, 
    ROC curve, and confusion matrix for stakeholder review.

Integrated Recommendation:
1. Use the Random Forest model as-is (statistical validation confirms validity)
2. Present feature rankings with uncertainty bands to stakeholders
3. Monitor for drift; consider ensemble with logistic regression as fallback
4. Review confusion matrix to understand misclassification patterns
```

---

## 5. Failover & Error Handling

### 5.1 Agent Failure Scenarios

| Scenario | Handling |
|----------|----------|
| Agent times out | Log, try recommended agent or GeneralInfoAgent |
| Agent crashes | Return graceful error + suggestion to try different agent |
| Agent returns malformed response | Use regex fallback parser, log error |
| Circular recommendations (A→B→A) | Detect cycle, break at depth limit |

### 5.2 Depth Limit (Prevent Infinite Loops)

```python
MAX_ROUTING_DEPTH = 3  # Prevent A→B→C→A chains

if depth >= MAX_ROUTING_DEPTH:
    return current_response_as_final()
```

---

## 6. Integration Points

### 6.1 File Handling

Router **aggregates** file information across agents:

```
User provides: ["data.csv", "model.pkl"]

Router:
  1. Detects file types → suggests agents that can read them
  2. Passes files to primary agent
  3. If secondary agents called, passes relevant files
  4. Collects all file metadata in RoutingResponse.files_analyzed
```

### 6.2 Conversation History

Router maintains **conversation context**:

```python
self.conversation_history = [
    {
        "turn": 1,
        "query": "Train a model",
        "primary_agent": "MLAgent",
        "routed_to": ["MLAgent", "StatisticsAgent"],
        "final_answer": "..."
    },
    {
        "turn": 2,
        "query": "Now visualize it",
        "context": "From previous turn: model was Random Forest",
        "primary_agent": "VizAgent",
        "routed_to": ["VizAgent"],
    }
]
```

Enables context-aware routing in follow-up queries.

---

## 7. Metrics & Observability

Router tracks:

```python
routing_metrics = {
    "total_queries": 100,
    "queries_by_agent": {
        "StatisticsAgent": 25,
        "MLAgent": 35,
        "DataEngAgent": 20,
        "VizAgent": 15,
        "GeneralInfoAgent": 5,
    },
    "primary_correct_rate": 0.87,  # % where primary agent matched DOMAIN
    "multi_agent_percentage": 0.12,  # % needing secondary agents
    "avg_routing_depth": 1.3,
    "timeouts": 2,
    "errors": 1,
}
```

---

## 8. User Experience

### 8.1 CLI Interface

```
=== Multi-Agent Router ===

User: Analyze customer churn data - train a model and validate it statistically

[Router] Analyzing query...
[Router] Primary agent: MLAgent (78% confidence)
[Router] Routing to MLAgent...

[MLAgent] Processing request...
✓ MLAgent complete (2.34s)
  Domain: IN_DOMAIN
  Task: classification
  Recommendations: StatisticsAgent

[Router] Following recommendation: StatisticsAgent
[Router] Routing to StatisticsAgent...

[StatisticsAgent] Processing request...
✓ StatisticsAgent complete (1.87s)
  Domain: IN_DOMAIN
  Task: model_evaluation
  Recommendations: none

[Router] Synthesizing responses...

=== Final Answer ===

Primary Agent (MLAgent):
[model training details...]

Supporting Analysis (StatisticsAgent):
[statistical validation...]

Integrated Recommendation:
[merged insights...]

[Total Latency: 4.21s across 2 agents]
```

### 8.2 Routing Transparency

Every response includes:
- Which agent(s) were called
- Why they were selected
- How responses were synthesized
- Routing depth and any corrections made

---

## 9. Future Extensions

- **LLM-based synthesis** - Use gpt-oss:20b to intelligently merge agent responses
- **Learned routing** - Track which agents succeed for which query patterns
- **Agent confidence scoring** - Weight responses by agent's confidence in domain
- **Custom agent registration** - Allow plugins to register new specialist agents
- **Cost optimization** - Route to cheaper agents first, escalate if needed
- **User feedback loop** - Track which agent recommendations users found helpful

---

## 10. Implementation Checklist

- [ ] Define unified response schema (UnifiedAgentResponse)
- [ ] Implement RouterDecider class with core routing logic
- [ ] Add LLMClassifier for heuristic backup
- [ ] Create agent adapters (normalize each agent's response format)
- [ ] Implement synthesis engine (merge multi-agent outputs)
- [ ] Add conversation history tracking
- [ ] Implement failover logic and depth limits
- [ ] Create CLI interface with routing transparency
- [ ] Add metrics and observability
- [ ] Write comprehensive test suite
- [ ] Document routing decisions and examples
- [ ] Integrate with existing agent APIs (no agent changes needed)

