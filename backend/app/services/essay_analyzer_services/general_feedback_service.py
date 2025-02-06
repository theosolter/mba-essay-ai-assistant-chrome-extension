from typing import List
import logging
from ..openai import OpenAIService
from ..rag import RAGContext
from ...config import get_settings
from ..models import GeneralFeedbackItem

logger = logging.getLogger(__name__)

class GeneralFeedbackService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.openai_service = OpenAIService()

    async def generate_feedback(
        self,
        essay_text: str,
        essay_prompt: str,
        user_instructions: str,
        context: RAGContext,
        school: str
    ) -> List[GeneralFeedbackItem]:
        """Generate general feedback for the essay."""
        try:
            logger.info("Generating general feedback")
            prompt = self._create_prompt(
                essay_text, essay_prompt, user_instructions, context, school
            )
            response = await self.openai_service.generate_chat_completion(prompt)
            
            return [GeneralFeedbackItem(**item) for item in response["general_feedback"]]
        
        except Exception as e:
            logger.error(f"Error generating general feedback: {str(e)}")
            raise

    def _create_prompt(
        self,
        essay_text: str,
        essay_prompt: str,
        user_instructions: str,
        context: RAGContext,
        school: str
    ) -> str:
        """Create the general feedback prompt using feedback and RAG context."""
        return f"""
        You are a professional MBA admissions coach. Your task is to provide detailed, actionable feedback on the user's essay, highlighting strengths and areas for improvement. Use the provided context, including school guidelines, user instructions, and expert feedback, to guide your analysis.

        ### Context:
        1. **School:** {school}
        2. **Essay Prompt:** {essay_prompt}
        3. **User's Essay:** {essay_text}
        4. **User Instructions:** {user_instructions} (This describes the user's goal for improvement, such as exploring emotional depth or enhancing storytelling.)
        5. **School Guidelines:** {context.guidelines}
        6. **RAG Context (Examples and Feedback):**
        {context.relevant_examples}

        ### Guidelines:
        1. Highlight the essay's strengths in storytelling, structure, and alignment with the prompt.
        2. Identify weaknesses and provide specific, actionable feedback for improvement.
        3. For each piece of feedback:
           - Provide a **detailed explanation** of the issue.
           - Offer a **suggestion** to address the issue.
           - Write a **fully written example application**, showing how the feedback can be applied directly.

        Return your response in the following JSON structure:
        {{
            "general_feedback": [
                {{
                    "section": "Introduction",
                    "feedback": "The introduction is engaging, but it could use a more vivid anecdote to immediately draw the reader in.",
                    "suggestion": "Start with a moment of action or tension that sets the stage for the essay.",
                    "example_application": "The phone call came late at night: a lung donor had been found. My family and I grabbed our go bags, rushing to the hospital, hearts pounding with hope and fear. In that moment, I had no idea how much this experience would shape my perspective on resilience and leadership."
                }}
            ]
        }}""" 