from typing import Annotated
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from .....config import get_settings
from ..models import (
    SuggestionFeedback, FeedbackResponse,
    ContentSuggestion, WorkflowState, FeedbackFramework
)
import logging
import asyncio
import json

logger = logging.getLogger(__name__)
settings = get_settings()

class FeedbackAgent:
    """Evaluates content suggestions using a standardized evaluation framework."""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.model_name, 
            temperature=0.5,
            api_key=settings.openai_api_key
        )
        # Minimum score threshold for considering suggestions as high quality
        self.quality_threshold = 8.0
        
        self.feedback_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert MBA admissions officer evaluating a content suggestion.
            Analyze the suggestion using the provided evaluation framework criteria.
            Each criterion must be evaluated thoroughly."""),
            ("human", """Here is the content suggestion to evaluate:
            
            {suggestion}

            Here is the evaluation framework to use:
            {framework}
            
            Analyze the suggestion and provide structured feedback following the exact format specified.
            """)
        ])
        
        self.feedback_chain = self.llm.with_structured_output(
            SuggestionFeedback,
            method="function_calling",
        )

    async def evaluate_suggestions(self, state: WorkflowState) -> WorkflowState:
        """Evaluates all content suggestions in parallel and updates workflow state."""
        try:
            if not state.feedback_framework:
                raise ValueError("Evaluation framework not found in workflow state")
                
            framework = self._format_evaluation_framework(state.feedback_framework)
            
            # Evaluate all suggestions in parallel
            tasks = [
                self.evaluate_single_suggestion(suggestion, framework)
                for suggestion in state.suggestions.suggestions
            ]
            feedback_results = await asyncio.gather(*tasks)
            
            overall_score = sum(f.score for f in feedback_results) / len(feedback_results)
            
            state.feedback = FeedbackResponse(
                suggestion_feedback=feedback_results,
                overall_score=overall_score
            )
            state.iteration += 1
            
            logger.info(
                "Completed suggestion evaluation",
                extra={
                    "iteration": state.iteration,
                    "overall_score": overall_score,
                    "num_suggestions": len(feedback_results)
                }
            )
            return state
            
        except Exception as e:
            logger.error(
                "Failed to evaluate suggestions",
                extra={"error": str(e)},
                exc_info=True
            )
            raise

    async def evaluate_single_suggestion(
        self, 
        suggestion: ContentSuggestion, 
        framework: str
    ) -> SuggestionFeedback:
        """Evaluates a single content suggestion against the given framework."""
        try:
            formatted_prompt = await self.feedback_prompt.ainvoke({
                "framework": framework,
                "suggestion": self._format_suggestion(suggestion)
            })
            
            return await self.feedback_chain.ainvoke(formatted_prompt)
            
        except Exception as e:
            logger.error(
                "Failed to evaluate suggestion",
                extra={"error": str(e), "suggestion": suggestion.suggestion},
                exc_info=True
            )
            raise


    def _route_based_on_feedback(self, state: WorkflowState) -> Annotated[str, "Route"]:
        """Determines whether to continue feedback loop based on quality and iterations."""
        if (state.feedback and state.feedback.overall_score >= self.quality_threshold) or \
           state.iteration >= state.max_iterations:
            logger.info(
                "Workflow complete",
                extra={
                    "reason": "quality_threshold_met" if state.feedback and state.feedback.overall_score >= self.quality_threshold else "max_iterations_reached",
                    "final_score": state.feedback.overall_score if state.feedback else None,
                    "iterations": state.iteration
                }
            )
            return "complete"
            
        return "continue"

    def _format_suggestion(self, suggestion: ContentSuggestion) -> str:
        """Formats a content suggestion into a JSON string."""
        suggestion_dict = {
            "suggestion": suggestion.suggestion,
            "how_to_apply": suggestion.how_to_apply,
            "original_text": suggestion.original_text,
            "improved_version": suggestion.improved_version
        }
        return f"Suggestion:\n{json.dumps(suggestion_dict, indent=2)}"

    def _format_evaluation_framework(self, framework: FeedbackFramework) -> str:
        """Formats the evaluation framework criteria into a readable string."""
        formatted_criteria = []
        for criterion in framework.criteria:
            formatted_criteria.append(
                f"Criterion: {criterion.name}\n"
                f"Description: {criterion.description}\n"
                f"Example Application: {criterion.example_feedback}\n"
            )
        return "\n\n".join(formatted_criteria) 