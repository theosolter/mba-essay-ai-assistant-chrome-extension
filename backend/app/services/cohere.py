from cohere import Client
from ..config import get_settings
from typing import List
from .pinecone import MBAEssaySearchResult

class CohereService:
    RELEVANCE_THRESHOLD = 0.3

    def __init__(self):
        self.settings = get_settings()
        self.client = Client(api_key=self.settings.cohere_api_key)

    async def rerank_results(
        self,
        query: str,
        results: List[MBAEssaySearchResult]
    ) -> List[MBAEssaySearchResult]:
        """Reranks search results by relevance using Cohere and filters low-scoring matches."""
        if not results:
            return results

        documents = [
            f"School: {result.school}\nPrompt: {result.prompt}\nEssay: {result.essay}\nFeedback: {result.feedback}"
            for result in results
        ]
        
        reranked_results = self.client.rerank(
            model="rerank-v3.5",
            query=query,
            documents=documents,
            top_n=6
        )

        filtered_results = []
        for reranked in reranked_results.results:
            print(f"Reranked score: {reranked}")
            if reranked.relevance_score >= self.RELEVANCE_THRESHOLD:
                original_result = results[reranked.index]
                filtered_results.append(MBAEssaySearchResult(
                    score=reranked.relevance_score,
                    essay=original_result.essay,
                    prompt=original_result.prompt,
                    school=original_result.school,
                    feedback=original_result.feedback
                ))
                
        return filtered_results
