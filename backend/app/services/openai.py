from openai import OpenAI
from ..config import get_settings
from typing import List, Dict, Any
import json
import logging
from openai.types.chat import ChatCompletion

# Set up logging
logger = logging.getLogger(__name__)

class OpenAIService:
    """
    Service class for interacting with OpenAI's API.
    Handles embeddings generation and chat completions with proper error handling.
    """
    
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = OpenAI(api_key=self.settings.openai_api_key)
        logger.info("OpenAIService initialized")

    def generate_embedding(self, text: str) -> List[float]:
        """
        Creates an embedding vector for the given text.
        Returns a list of floats representing the embedding.
        """
        try:
            response = self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            raise Exception(f"Embedding generation failed: {str(e)}")

    async def generate_chat_completion(self, prompt: str) -> Dict[str, Any]:
        """
        Gets a chat completion from OpenAI for the given prompt.
        Returns the response as a parsed JSON dictionary.
        """
        try:
            # Request JSON-formatted response from the API
            response: ChatCompletion = self.client.chat.completions.create(
                model=self.settings.model_name,
                response_format={"type": "json_object"},
                messages=[{"role": "user", "content": prompt}],
                temperature=self.settings.temperature,
                max_tokens=self.settings.max_tokens
            )
            
            # Extract and parse the response content
            result: str = response.choices[0].message.content or "{}"
            return json.loads(result)
            
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse LLM response as JSON: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        except Exception as e:
            error_msg = f"OpenAI API call failed: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
