from typing import Dict, List
from langgraph.graph import StateGraph, END
import logging
from .agents.writing_style_agent import WritingStyleExtractionAgent
from .agents.feedback_criteria_agent import FeedbackCriteriaExtractionAgent
from .agents.content_suggestion_agent import ContentSuggestionAgent
from .agents.feedback_agent import FeedbackAgent
from .models import WorkflowState
from ...models import ContentSuggestion

logger = logging.getLogger(__name__)

class ContentSuggestionWorkflow:
    def __init__(self):
        try:
            self.writing_style_agent = WritingStyleExtractionAgent()
            self.feedback_criteria_agent = FeedbackCriteriaExtractionAgent()
            self.content_agent = ContentSuggestionAgent()
            self.feedback_agent = FeedbackAgent()
            
            self.workflow = StateGraph(WorkflowState)
            
            self.workflow.add_node("extract_writing_style", self.writing_style_agent.extract_writing_style)
            self.workflow.add_node("extract_feedback_criteria", self.feedback_criteria_agent.extract_feedback_framework)
            self.workflow.add_node("generate_suggestions", self.content_agent.generate_initial_suggestions)
            self.workflow.add_node("refine_suggestions", self.content_agent.refine_suggestions)
            self.workflow.add_node("evaluate_suggestions", self.feedback_agent.evaluate_suggestions)
            
            # Configure workflow edges
            # Start with writing style extraction
            self.workflow.set_entry_point("extract_writing_style")

            # Connect extractors
            self.workflow.add_edge("extract_writing_style", "extract_feedback_criteria")

            # After sync, proceed with main workflow
            self.workflow.add_edge("extract_feedback_criteria", "generate_suggestions")
            self.workflow.add_edge("generate_suggestions", "evaluate_suggestions")
            
            self.workflow.add_conditional_edges(
                "evaluate_suggestions",
                self.feedback_agent._route_based_on_feedback,
                {
                    "continue": "refine_suggestions",
                    "complete": END
                }
            )
            
            self.workflow.add_edge("refine_suggestions", "evaluate_suggestions")
            
            self.chain = self.workflow.compile()
            
        except Exception as e:
            logger.error("Error initializing workflow", extra={"error": str(e)})
            raise

    async def generate_content_suggestions(
        self,
        essay_text: str,
        essay_prompt: str,
        rag_context: Dict[str, List[Dict[str, str]]],
        user_instructions: str = "",
        school_guidelines: str = "",
        max_iterations: int = 5,
        quality_threshold: float = 8.0
    ) -> List[ContentSuggestion]:
        """
        Generates and refines content suggestions for improving an essay.
        
        Uses an iterative process to analyze the essay style, generate suggestions,
        and refine them based on feedback until quality threshold is met or max iterations reached.
        """
        try:
            self.feedback_agent.quality_threshold = quality_threshold
            
            initial_state = WorkflowState(
                essay_text=essay_text,
                essay_prompt=essay_prompt,
                rag_context=rag_context,
                user_instructions=user_instructions,
                school_guidelines=school_guidelines,
                max_iterations=max_iterations
            )

            final_state = await self.chain.ainvoke(initial_state)

            return final_state["suggestions"].suggestions
            
        except Exception as e:
            logger.error("Workflow failed", extra={
                "error": str(e),
                "error_type": type(e).__name__
            })
            raise RuntimeError(f"Failed to analyze essay: {str(e)}") from e

def extract_writing_style(state: WorkflowState) -> WorkflowState:
    """Gets writing style patterns from the essay"""
    agent = WritingStyleExtractionAgent()
    state.writing_style_analysis = agent.analyze_writing_style(
        state.essay_text,
        state.rag_context
    )
    return state

def extract_evaluation_criteria(state: WorkflowState) -> WorkflowState:
    """Extracts evaluation criteria from feedback examples"""
    agent = FeedbackCriteriaExtractionAgent()
    state.feedback_framework = agent.extract_criteria(
        state.rag_context
    )
    return state 