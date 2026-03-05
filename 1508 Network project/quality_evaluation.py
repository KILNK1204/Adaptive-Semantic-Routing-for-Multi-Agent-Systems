"""Quality rubrics for evaluating agent answers across 5 dimensions."""

from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class QualityScore:
    agent: str
    query: str
    relevance: int  # 1-5
    completeness: int  # 1-5
    correctness: int  # 1-5
    actionability: int  # 1-5
    domain_confidence: int  # 1-5
    notes: str  # Free-form explanation
    
    @property
    def average_score(self) -> float:
        return (self.relevance + self.completeness + self.correctness + 
                self.actionability + self.domain_confidence) / 5.0
    
    def summary(self) -> str:
        return f"""
Agent: {self.agent}
Query: {self.query[:60]}...
Scores: R={self.relevance} C={self.completeness} Cor={self.correctness} A={self.actionability} DC={self.domain_confidence}
Average: {self.average_score:.2f}/5.0
Notes: {self.notes}
"""


class QualityRubrics:
    """Rubrics for evaluating each agent type."""
    
    @staticmethod
    def get_dataeng_rubric() -> Dict[str, str]:
        return {
            "relevance": (
                "5: Directly addresses data structure, schema, ETL, or pipeline design\n"
                "4: Mostly on-topic; may have minor tangents\n"
                "3: Addresses the domain but misses the specific ask\n"
                "2: Tangential; mentions data eng concepts but not core request\n"
                "1: Completely off-topic or about a different domain"
            ),
            "completeness": (
                "5: Covers schema design, handling edge cases, validation, and next steps\n"
                "4: Covers main points; minor details missing\n"
                "3: Partial solution; significant gaps (e.g., no error handling)\n"
                "2: Skeleton answer; many key details absent\n"
                "1: Incomplete fragment"
            ),
            "correctness": (
                "5: SQL/schema/design is sound; best practices evident\n"
                "4: Generally correct; minor inefficiencies\n"
                "3: Core idea correct but has flaws (e.g., missing indexes)\n"
                "2: Significant errors (e.g., incorrect JOIN, bad normalization)\n"
                "1: Fundamentally wrong or contradicts SQL/schema rules"
            ),
            "actionability": (
                "5: User can immediately use the SQL/schema/code provided\n"
                "4: Clear enough to execute with minimal adaptation\n"
                "3: Requires some translation/expansion to use\n"
                "2: More of a high-level sketch; significant work to implement\n"
                "1: Too vague or incomplete to act upon"
            ),
            "domain_confidence": (
                "5: Demonstrates deep understanding of ETL, schemas, and best practices\n"
                "4: Shows solid data eng knowledge\n"
                "3: Competent but generic guidance\n"
                "2: Surface-level; some misunderstandings\n"
                "1: Confused about data eng fundamentals"
            )
        }
    
    @staticmethod
    def get_stats_rubric() -> Dict[str, str]:
        return {
            "relevance": (
                "5: Directly addresses hypothesis testing, inference, or experimental design\n"
                "4: Mostly on-topic; may have minor tangents\n"
                "3: Addresses statistics but misses the specific question\n"
                "2: Tangential; mentions stats concepts but not the core ask\n"
                "1: Completely off-topic or not about statistics"
            ),
            "completeness": (
                "5: Covers test selection, assumptions, effect size, confidence intervals, and interpretation\n"
                "4: Covers main elements; minor pieces missing\n"
                "3: Partial analysis; missing key elements (e.g., no confidence interval)\n"
                "2: Skeleton answer; many gaps\n"
                "1: Incomplete fragment"
            ),
            "correctness": (
                "5: Test selection appropriate; assumptions checked; calculations sound\n"
                "4: Generally correct; minor issues with rigor\n"
                "3: Core approach sound but has statistical flaws\n"
                "2: Wrong test or major misinterpretation of assumptions\n"
                "1: Fundamentally violates statistical principles"
            ),
            "actionability": (
                "5: Provides concrete hypothesis, test, and decision rule\n"
                "4: Clear enough to execute with minimal interpretation\n"
                "3: Requires some translation to implement\n"
                "2: Mostly guidance; needs significant work to use\n"
                "1: Too theoretical or vague to apply"
            ),
            "domain_confidence": (
                "5: Demonstrates mastery of hypothesis testing, interpretation, and rigor\n"
                "4: Shows solid statistical knowledge\n"
                "3: Competent but generic guidance\n"
                "2: Surface-level; some statistical misunderstandings\n"
                "1: Confused about statistical principles"
            )
        }
    
    @staticmethod
    def get_ml_rubric() -> Dict[str, str]:
        return {
            "relevance": (
                "5: Directly addresses model selection, training, tuning, or evaluation\n"
                "4: Mostly on-topic; may have minor tangents\n"
                "3: Addresses ML but misses the specific problem\n"
                "2: Tangential; mentions ML concepts but not core request\n"
                "1: Completely off-topic or not about ML"
            ),
            "completeness": (
                "5: Covers model choice, hyperparameters, evaluation metrics, and validation strategy\n"
                "4: Covers main elements; minor details missing\n"
                "3: Partial guidance; missing key elements (e.g., no cross-validation)\n"
                "2: Skeleton answer; many gaps\n"
                "1: Incomplete fragment"
            ),
            "correctness": (
                "5: Model choice justified; hyperparameters reasonable; evaluation rigorous\n"
                "4: Generally sound; minor inefficiencies or suboptimal choices\n"
                "3: Core approach correct but has flaws (e.g., poor feature scaling)\n"
                "2: Wrong algorithm or major misunderstanding of the problem\n"
                "1: Fundamentally flawed approach"
            ),
            "actionability": (
                "5: User can implement the pipeline with provided hyperparameters and metrics\n"
                "4: Clear roadmap; requires minor interpretation\n"
                "3: Requires significant effort to translate into code\n"
                "2: High-level guidance; substantial implementation work needed\n"
                "1: Too abstract to implement"
            ),
            "domain_confidence": (
                "5: Deep understanding of algorithms, hyperparameters, and evaluation practices\n"
                "4: Solid ML knowledge and best practices\n"
                "3: Competent but generic guidance\n"
                "2: Surface-level; some ML misunderstandings\n"
                "1: Confused about ML fundamentals"
            )
        }
    
    @staticmethod
    def get_viz_rubric() -> Dict[str, str]:
        return {
            "relevance": (
                "5: Directly addresses visualization design, chart selection, or dashboard layout\n"
                "4: Mostly on-topic; may have minor tangents\n"
                "3: Addresses visualization but misses the specific ask\n"
                "2: Tangential; mentions viz concepts but not core request\n"
                "1: Completely off-topic or not about visualization"
            ),
            "completeness": (
                "5: Covers chart type, data encoding, design principles, and accessibility\n"
                "4: Covers main design choices; minor details missing\n"
                "3: Partial guidance; missing key considerations (e.g., color accessibility)\n"
                "2: Skeleton answer; many gaps\n"
                "1: Incomplete fragment"
            ),
            "correctness": (
                "5: Chart type justified; encoding is effective; follows best practices\n"
                "4: Generally sound; minor design inefficiencies\n"
                "3: Reasonable choices but has drawbacks (e.g., poor color scheme)\n"
                "2: Chart choice questionable or violates common principles\n"
                "1: Fundamentally poor visualization choice"
            ),
            "actionability": (
                "5: User can create the visualization with clear specifications\n"
                "4: Clear enough to implement with minimal interpretation\n"
                "3: Requires some translation to execute\n"
                "2: Mostly ideas; significant design work needed\n"
                "1: Too vague or abstract to implement"
            ),
            "domain_confidence": (
                "5: Deep understanding of design principles, color theory, and storytelling\n"
                "4: Solid visualization knowledge and best practices\n"
                "3: Competent but generic guidance\n"
                "2: Surface-level; some design misunderstandings\n"
                "1: Confused about visualization principles"
            )
        }
    
    @classmethod
    def get_rubric(cls, agent_name: str) -> Dict[str, str]:
        rubrics = {
            "DataEngAgent": cls.get_dataeng_rubric(),
            "StatisticsAgent": cls.get_stats_rubric(),
            "MLAgent": cls.get_ml_rubric(),
            "VizAgent": cls.get_viz_rubric(),
        }
        return rubrics.get(agent_name, {})
    
    @staticmethod
    def print_rubric(agent_name: str):
        rubric = QualityRubrics.get_rubric(agent_name)
        print(f"\n{'='*80}")
        print(f"QUALITY RUBRIC: {agent_name}")
        print(f"{'='*80}\n")
        
        dimensions = ["relevance", "completeness", "correctness", "actionability", "domain_confidence"]
        for dim in dimensions:
            if dim in rubric:
                print(f"{dim.upper()}:")
                print(rubric[dim])
                print()


class EvaluationGuide:
    """Guidance for conducting manual quality evaluations."""
    
    INSTRUCTIONS = """
QUALITY EVALUATION GUIDE

This guide helps you score agent answers on a 1-5 scale across 5 dimensions.

SCORING GUIDELINES:
  5 = Excellent: Directly addresses the query with depth, clarity, and actionability
  4 = Good: Mostly correct and helpful, minor gaps or inefficiencies
  3 = Adequate: Addresses the topic but has notable gaps or is generic
  2 = Poor: Tangential or has significant errors
  1 = Fail: Off-topic or fundamentally wrong

KEY PRINCIPLES:
  - Score each dimension independently (don't let one bad score affect others)
  - Be generous on correctness if the agent showed understanding but made minor mistakes
  - Penalize actionability if a user couldn't actually execute the advice
  - Look for domain-specific depth (e.g., StatisticsAgent should mention assumptions)

EFFICIENCY TIP:
  - Skim the answer first to get a sense of quality
  - Use the rubric to justify your score, not to overthink
  - If unsure between 3 and 4, pick 3.5 if you need precision
  - Write 1-2 sentence notes explaining the score

WHAT TO LOOK FOR:

DataEngAgent:
  ✓ Good: Provides SQL, schema diagrams, error handling, validation steps
  ✗ Bad: Generic "normalize your data" advice with no specifics

StatisticsAgent:
  ✓ Good: Names the test, states assumptions, provides effect size & CI
  ✗ Bad: "Run a t-test and see if p < 0.05" (oversimplified)

MLAgent:
  ✓ Good: Recommends specific model, hyperparameters, and evaluation metrics
  ✗ Bad: "Use machine learning to solve your problem" (no substance)

VizAgent:
  ✓ Good: Justifies chart type, discusses color/accessibility, explains what to encode
  ✗ Bad: "Make a nice dashboard" (too vague)
"""
    
    @staticmethod
    def print_instructions():
        print(EvaluationGuide.INSTRUCTIONS)


def create_evaluation_template(agent: str, query: str, answer: str) -> str:
    rubric = QualityRubrics.get_rubric(agent)
    
    template = f"""
{'='*80}
EVALUATION FORM
{'='*80}

AGENT: {agent}
QUERY: {query}

ANSWER (first 300 chars):
{answer[:300]}...

{'='*80}
SCORING (1-5 for each):

1. RELEVANCE: Does the answer address the query?
   Scale: {rubric.get('relevance', '').split(chr(10))[0]}
   Score: ___ / 5
   Notes: _______________________________________________

2. COMPLETENESS: Are key aspects covered?
   Scale: {rubric.get('completeness', '').split(chr(10))[0]}
   Score: ___ / 5
   Notes: _______________________________________________

3. CORRECTNESS: Is the information accurate/sound?
   Scale: {rubric.get('correctness', '').split(chr(10))[0]}
   Score: ___ / 5
   Notes: _______________________________________________

4. ACTIONABILITY: Can the user execute the advice?
   Scale: {rubric.get('actionability', '').split(chr(10))[0]}
   Score: ___ / 5
   Notes: _______________________________________________

5. DOMAIN CONFIDENCE: Does it show domain expertise?
   Scale: {rubric.get('domain_confidence', '').split(chr(10))[0]}
   Score: ___ / 5
   Notes: _______________________________________________

OVERALL NOTES:
_________________________________________________________________
_________________________________________________________________

{'='*80}
"""
    return template


if __name__ == "__main__":
    # Example usage
    print(EvaluationGuide.INSTRUCTIONS)
    print("\n\n")
    
    for agent in ["DataEngAgent", "StatisticsAgent", "MLAgent", "VizAgent"]:
        QualityRubrics.print_rubric(agent)
        print("\n")
