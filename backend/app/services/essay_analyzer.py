from fastapi import HTTPException
from .models import (
    AnalysisResponse,
    AnalysisRequest,
    ContentSuggestion,
    LanguageEdit,
    GeneralFeedbackItem
)
from .rag import RAGContext
from .essay_analyzer_services.language_edit_service import LanguageEditService
from .essay_analyzer_services.general_feedback_service import GeneralFeedbackService
from .essay_analyzer_services.content_suggestion_service.content_suggestion_workflow import ContentSuggestionWorkflow
from ..config import get_settings
import logging

logger = logging.getLogger(__name__)

class EssayAnalyzer:
    def __init__(self) -> None:
        self.settings = get_settings()
        
        # Initialize services
        self.language_edit_service = LanguageEditService()
        self.general_feedback_service = GeneralFeedbackService()
        self.content_suggestion_workflow = ContentSuggestionWorkflow()
        
        logger.info("EssayAnalyzer initialized")

    async def analyze(
        self,
        essay_text: str,
        essay_prompt: str,
        user_instructions: str,
        context: RAGContext,
        school: str
    ) -> AnalysisResponse:
        """
        Analyzes an MBA admission essay and returns detailed feedback.
        
        Processes the essay in parallel to generate content suggestions,
        language improvements, and general feedback using the provided context.
        
        Raises HTTPException if the analysis fails.
        """
        try:
            logger.info(f"Starting essay analysis for {school}")
            
            # Generate all feedback types in parallel for better performance
            content_suggestions_task = self.content_suggestion_workflow.generate_content_suggestions(
                essay_text, essay_prompt, context.model_dump(), user_instructions, school
            )
            
            language_edits_task = self.language_edit_service.generate_edits(
                essay_text, user_instructions
            )
            
            general_feedback_task = self.general_feedback_service.generate_feedback(
                essay_text, essay_prompt, user_instructions, context, school
            )

            # Await all responses
            content_suggestions = await content_suggestions_task
            language_edits = await language_edits_task
            general_feedback = await general_feedback_task

            logger.info("Successfully generated all feedback components")

            return AnalysisResponse(
                content_suggestions=content_suggestions,
                language_edits=language_edits,
                general_feedback=general_feedback
            )

        except Exception as e:
            error_msg = f"Error analyzing essay: {str(e)}"
            logger.error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg) 