from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API Keys
    openai_api_key: str
    pinecone_api_key: str
    cohere_api_key: str
    
    # Pinecone Settings
    pinecone_index_name: str = "mba-essays-assistant"
    
    # LLM Settings
    model_name: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: int = 4096
    
    # Application Settings
    environment: str = "development"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()