from typing import List
from pydantic import BaseModel
from .openai import OpenAIService
from .pinecone import PineconeService
from .cohere import CohereService
from .cache import CacheService, CacheOptions

class RAGContext(BaseModel):
    """
    Represents the context retrieved from the RAG system.
    
    Attributes:
        relevant_examples: List of dictionaries containing essay text and feedback pairs
        guidelines: List of school-specific essay writing guidelines
    """
    relevant_examples: List[dict] = []
    guidelines: List[str] = []

# TODO: Clean up all guidelines and add school-specific guidelines for Wharton, Booth, Sloan, Columbia, and other top schools
SCHOOL_GUIDELINES = {
    "Harvard Business School": [
        """Emphasis on More
With the wording "what more would you like us to know" (italics ours), the admissions committee is
indirectly acknowledging all the information it already has about you, thanks to the other parts of
your application: your resume, extracurricular activities, recommendations, responses to short-
answer questions, academic transcripts, and GMAT/GRE score. You should therefore think first
about what these elements collectively convey about who you are as an individual and a candidate,
so you can identify which aspects of your profile still need to be presented or could benefit from
more detail. In more colloquial terms, we would say that the admissions committee has the "black
and white"; this is your chance to give them the "color."

In other words, your essay is an opportunity to add a sense of your personality and spirit to
the more "flat" statistics and facts—this your opportunity to share your values. Your essay
also provides a place for you to flesh out aspects of your candidacy that might be mentioned
elsewhere but that might need—or would be enhanced in some way by—additional explication.

For example, if one of your short-answer responses informs the school of a certain fact, and a
profoundly important story lurks behind that fact that you feel effectively expresses a key part of
your personality or life experience, you can indeed use this story as part of or the central focus of
your essay. In this case, "more" does not strictly mean "thus far unmentioned" but rather "as yet
undeveloped." By the time the admissions officer is done reading your essay, they should have a far
more comprehensive understanding of who you are. Indeed, your image should be "developed.""",
    ],
    
    "Stanford GSB": [
        """What Truly Matters?
A prompt like "What matters?" can be vexing to many applicants because it is simultaneously open-
ended and limiting. Part of the challenge is that multiple people can naturally feel truly passionate
about the same values, such as health, family, faith, and education. And because these values are
so common, writing a compelling essay on one of them that will stand out to an admissions reader
and position you as a unique individual can be extremely difficult. When an idea is so ubiquitous,
descending into cliché becomes all too easy. At the same time, writing your essay on a theme the
admissions committee has never read about before is likely impossible. Basically, the odds are slim
that you will break new ground with your chosen topic.

The key to an effective and memorable GSB essay, then, is authenticity. You must identify what is
truly of primary importance in your life and share the experiences and examples from your past that
support that theme. Your stories are unique to you, and they are what will set your essay apart, not
the specific topic itself but rather your presentation of how that topic has manifested in your life.
And if you have selected a theme that genuinely applies to you, you should naturally have multiple
supporting examples to offer. For example, you cannot write a convincing essay about "making a
difference" if your volunteer experiences have been only sporadic. However, if you have truly had an
impact on your community through your efforts and/or have exhibited a longstanding commitment
to a cause or person, then you should have plenty of evidentiary anecdotes to support this claim,
and the topic would come across as genuine rather than cliché. So, focus less on trying to choose
the "right" subject for your essay and more on identifying one that is personal and authentic to you.
If you write powerfully about your topic and connect it directly to your experiences and values, your
essay will have its best chance at being a winner.""",

        """Ideally, the experiences and values you share in this essay will be deeply personal and authentic,
and if so, the fundamental theme you are trying to elucidate will naturally reveal itself. This means
you would not need to open your essay by directly stating, "What matters most to me is..." or
conclude your essay with "The reason this matters is...." If you feel that making such a declaration
is necessary for the admissions committee to understand your intent and message, take this as a
sign that your essay's content might not sufficiently convey your theme and that you need to devote
more time to developing it before submitting. If you share relevant stories and examples of how
you have had an impact on your community, for example, the admissions reader will not be left
wondering, "What is important to this applicant?" Similarly, if you have explained the motivation
behind the actions you have taken and decisions you have made, the "and why?" element of
the school's question will also be readily apparent. Of course, we are not saying that you will be
rejected from the applicant pool if you write, "What matters most to me is..." in your essay, but we
can assure you that doing so is often unnecessary, even if you feel obligated to.

As we have noted, the open-ended nature of the two schools' essay questions is what makes
them so analogous. A prompt such as "Discuss your greatest professional accomplishment" or
"Tell us about a team failure" would limit your topic and the range of anecdotes from which you
could choose. But with "What matters?" and "What more?", you are challenged to share stories
and experiences that showcase your values and provide a broader understanding of who you are
as a person. We recommend that before ultimately submitting your essay for either school, you
read it out loud so you can "hear" yourself and get a better sense of whether you have successfully
communicated your values and personality in your draft.""",
    ],
    
    "Wharton": [
        "Highlight professional achievements",
        "Show team leadership experience", 
        "Connect experiences to future goals"
    ],
    
    "Chicago Booth": [
        "Demonstrate analytical thinking",
        "Show diverse perspectives",
        "Connect experiences to Booth's values"
    ],
    
    "MIT Sloan": [
        "Focus on innovation and problem-solving",
        "Show quantitative achievements",
        "Demonstrate leadership and collaboration"
    ],
    
    "Columbia Business School": [
        "Show why Columbia and NYC",
        "Demonstrate leadership and teamwork",
        "Connect past experiences to future goals"
    ]
}

# Default guidelines for schools not in the predefined list
DEFAULT_GUIDELINES = [
    "Focus on personal growth and leadership",
    "Use specific examples to illustrate points", 
    "Maintain a clear narrative structure"
]


class RAGService:
    """Retrieves relevant context for essay analysis using RAG architecture"""
    
    def __init__(self):
        self.openai = OpenAIService()
        self.pinecone = PineconeService()
        self.cohere = CohereService()
        self.cache = CacheService(
            CacheOptions(
                max_size=1000,
                ttl=31536000  # Cache for 1 year in seconds
            )
        )

    def _get_cache_key(self, prefix: str, value: str) -> str:
        """Generates a cache key from prefix and value"""
        return f"{prefix}:{value}"

    async def get_relevant_context(self, essay_text: str, essay_prompt: str, school: str) -> RAGContext:
        """
        Gets relevant examples and guidelines for essay analysis.
        
        Returns context containing similar essays and school-specific guidelines.
        """
        query = f"Essay Content: {essay_text}"
        
        context_cache_key = self._get_cache_key(f'context:{school}', query)
        cached_context = self.cache.get(context_cache_key)
        if cached_context:
            return RAGContext(**cached_context)

        embedding_cache_key = self._get_cache_key('embedding', query)
        query_embedding = self.cache.get(embedding_cache_key)
        
        if not query_embedding:
            query_embedding = self.openai.generate_embedding(query)
            self.cache.set(embedding_cache_key, query_embedding)

        # Search for similar essays filtered by school
        search_results = self.pinecone.search_similar_essays(
            query_embedding=query_embedding,
            school=school
        )

        # Rerank results for better relevance
        reranked_results = await self.cohere.rerank_results(query, search_results)

        relevant_examples = [
            {"essay": result.essay, "feedback": result.feedback} 
            for result in reranked_results
        ]

        context = RAGContext(
            relevant_examples=relevant_examples,
            guidelines=SCHOOL_GUIDELINES.get(school, DEFAULT_GUIDELINES)
        )
        
        self.cache.set(context_cache_key, context.dict())

        return context