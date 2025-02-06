from typing import List
import logging
from ..models import LanguageEdit
from ..openai import OpenAIService
from ...config import get_settings

logger = logging.getLogger(__name__)

class LanguageEditService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.openai_service = OpenAIService()

    async def generate_edits(
        self,
        essay_text: str,
        user_instructions: str
    ) -> List[LanguageEdit]:
        """Generate language improvement suggestions for the essay."""
        try:
            logger.info("Generating language edits")
            prompt = self._create_prompt(essay_text, user_instructions)
            response = await self.openai_service.generate_chat_completion(prompt)
            
            return [LanguageEdit(**item) for item in response["language_edits"]]
        
        except Exception as e:
            logger.error(f"Error generating language edits: {str(e)}")
            raise

    def _create_prompt(
        self,
        essay_text: str,
        user_instructions: str
    ) -> str:
        """Create the language edits prompt using feedback and RAG context."""
        return f"""
        You are an expert editor specializing in MBA essays. Your task is to improve the clarity, conciseness, and word choices of the user's essay. For each suggested edit, provide a rewritten version of the sentence or section, ready for direct use. Each word/sentence in the essay should deserve its place in the essay and convey meaning that will give admission officers a clear understanding of the user's story, character, values, and emotions.

        ### Context:
        1. **User's Essay:** {essay_text}
        2. **User Instructions:** {user_instructions} (This describes the user's goal for editing, such as improving flow or reducing word count.)

        ### Guidelines:
        1. Identify sentences or sections that can be simplified or clarified while preserving the tone and intent.
        2. Make suggestions for reducing wordiness or improving flow.
        3. Write the "after" version as a complete, ready-to-use improvement.

        Return your response in the following JSON structure:
        {{
            "language_edits": [
                {{
                    "before": "I have always been passionate about leading teams in a variety of professional settings, which has taught me invaluable lessons.",
                    "after": "Leading diverse teams taught me invaluable lessons."
                }}
            ]
        }}""" 