from typing import List
from pydantic import BaseModel
from fastapi import HTTPException
from .openai import OpenAIService
from ..utils.text_cleaner import clean_essay_text
import logging
from .models import WordCutResponse, WordCutRequest

logger = logging.getLogger(__name__)

class WordCutter:
    def __init__(self):
        self.openai_service = OpenAIService()

    def _create_word_cut_prompt(
        self,
        essay_text: str,
        word_limit: int,
    ) -> str:
        """
        Creates a prompt for the OpenAI API to cut words from an essay.
        """
        current_word_count = len(essay_text.split())
        words_to_cut = current_word_count - word_limit

        return f"""
        You are an expert MBA essay editor specializing in concise, impactful writing. Your task is to help reduce the word count of the user's essay while preserving its meaning, emotional impact, and overall structure. Follow a systematic approach to editing, beginning with small, non-disruptive edits and progressing to larger cuts only if necessary.

        ### Current Essay Information:
        - Current Word Count: {current_word_count}
        - Target Word Count: {word_limit}
        - Words to Cut: {words_to_cut}

        ### Essay Context:
        - **User's Essay:** {essay_text}

        ### Editing Guidelines:
        1. **Approach to Cutting Words:**
        - Think of editing as a sculptor refining a marble block: focus on removing redundancies while keeping the "core shape" of the essay intact.
        - Begin with simple edits like removing filler words, shortening lists, and using contractions.
        - Progressively look for larger edits, such as eliminating throat-clearing introductions or unnecessary clauses, only if smaller edits do not meet the word limit.
        - Avoid over-editing. Take the mindset of "killing your darlings" when necessary, but ensure the integrity of the essay is preserved.

        2. **Small Edits (Easy Wins):**
        - **Remove Filler Words:** Identify and remove unnecessary words like "very," "really," "finally," "as well," "in general," and "I think."
        - **Shorten Lists:** Condense lists or phrases with redundant items (e.g., "team collaboration and teamwork" → "team collaboration").
        - **Use Contractions:** Replace phrases like "do not" with "don't" and "it is" with "it's" to save space.
        - **Eliminate "Been" Usage:** Simplify sentences containing "has been" or "had been" (e.g., "It had been my dream" → "It was my dream").
        - **Consolidate Verb Strings:** Combine consecutive verbs or phrases to simplify meaning (e.g., "I would like to join" → "I'd join").

        3. **Moderate Edits:**
        - **Throat Clearing:** Look for long introductions or paragraphs that could begin with the second sentence without losing context or meaning.
        - **Cut Unnecessary Clauses:** Identify descriptive phrases separated by commas that can be removed without altering the main point (e.g., "As I've often told my friends and family, I love storytelling" → "I love storytelling").
        - **Simplify Sentences:** Rephrase overly complex sentences while retaining their core message.

        4. **Bigger Cuts (Last Resort):**
        - Identify entire sentences or paragraphs that are repetitive, redundant, or fail to add unique value to the essay. Remove these only if smaller edits cannot meet the word count.

        5. **Ensure Preservation of Key Elements:**
        - Retain and highlight the applicant's **key stories** and **examples.**
        - Emphasize their **character traits**, **values**, and **emotional impact.**
        - Take a step back and reflect on what is the goal of each sentence/paragraph. Don't cut words that are key to conveying the message.

        6. **Output Structure:**
        Return your edits in the following structured JSON format:
        {{
            "edits": [
                {{
                    "before": "Original sentence from the user's essay.",
                    "after": "Concise version of the sentence.",
                    "before_word_count": 0,
                    "after_word_count": 0,
                    "word_count_diff": 0,
                    "explanation": "Brief explanation of the edit and why it was made."
                }},
                ...
            ]
        }}

        IMPORTANT: For each edit, ensure that word_count_diff accurately reflects the difference between before_word_count and after_word_count.

        ### Additional Tips for Effective Edits:
        - **Read the Essay Aloud:** If a sentence is hard to read without stumbling, simplify it.
        - **Be Intentional with Every Word:** Each word or sentence should deserve its place. Aim to convey meaning efficiently.
        - **Iterative Review:** Edit in stages. Perform a first pass for easy wins, then follow up with moderate edits. Return the edits in order from smallest to largest.
        """

    async def cut_words(
        self,
        essay_text: str,
        essay_prompt: str,
        word_limit: int,
    ) -> WordCutResponse:
        """
        Reduces essay word count while preserving meaning.
        Throws HTTPException if word cutting fails.
        """
        try:
            cleaned_essay_text = clean_essay_text(essay_text, essay_prompt)
            
            prompt = self._create_word_cut_prompt(
                essay_text=cleaned_essay_text,
                word_limit=word_limit,
            )
            
            openai_response = await self.openai_service.generate_chat_completion(prompt)
            
            total_word_count_diff = sum(edit["word_count_diff"] for edit in openai_response["edits"])
            total_before_word_count = len(cleaned_essay_text.split())
            total_after_word_count = total_before_word_count - total_word_count_diff
            
            response_data = {
                "total_word_count_diff": total_word_count_diff,
                "total_after_word_count": total_after_word_count,
                "total_before_word_count": total_before_word_count,
                "edits": openai_response["edits"]
            }
            
            return WordCutResponse(**response_data)
            
        except Exception as e:
            error_msg = f"Failed to cut words: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=error_msg
            ) 