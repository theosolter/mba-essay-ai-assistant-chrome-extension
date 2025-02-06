import json
import asyncio
import hashlib
from pathlib import Path
from ..services.openai import OpenAIService
from ..services.pinecone import PineconeService, MBAEssayEmbedding
from ..config import get_settings

async def process_essays():
    """
    Processes MBA essays by generating embeddings and storing them in Pinecone.
    Handles each essay individually and continues processing if one fails.
    """
    settings = get_settings()
    openai = OpenAIService()
    pinecone = PineconeService()

    essays_path = Path(__file__).parent.parent.parent / 'data/mba_essays_data.json'
    with open(essays_path, 'r', encoding='utf-8') as f:
        essays_data = json.load(f)

    for i, essay_data in enumerate(essays_data):
        try:
            essay_text = essay_data['essay'].strip()
            embedding = openai.generate_embedding(essay_text)
            
            essay_embedding = MBAEssayEmbedding(
                id=generate_unique_id(essay_data['school'], essay_data['prompt'], essay_text),
                values=embedding,
                metadata={
                    'essay': essay_text,
                    'prompt': essay_data['prompt'],
                    'school': essay_data['school'],
                    'feedback': essay_data['feedback'] if 'feedback' in essay_data else ''
                }
            )
            
            pinecone.store_essay_embedding(essay_embedding)
            await asyncio.sleep(0.2)
            
        except Exception as error:
            print(f'Error processing essay {i+1}: {str(error)}')
            continue

def generate_unique_id(school, prompt, content):
    """
    Creates a unique identifier for an essay using its school, prompt and content.
    Returns a SHA-256 hash of the combined fields.
    """
    combined = f"{school}|{prompt}|{content}"
    return hashlib.sha256(combined.encode('utf-8')).hexdigest()

if __name__ == '__main__':
    asyncio.run(process_essays())
