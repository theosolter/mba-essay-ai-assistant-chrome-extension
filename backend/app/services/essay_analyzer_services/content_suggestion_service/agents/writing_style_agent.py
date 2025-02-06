from typing import Dict, List
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from .....config import get_settings
from ..models import (
    WorkflowState,
    WritingStyleAttributeList,
    WritingStyleApplicationList
)
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

class WritingStyleExtractionAgent:
    """Analyzes writing style in essays by:
    1. Extracting style attributes (tone, structure, techniques)
    2. Derives a step-by-step explanation of how these attributes are applied in sample essays so that a writer can apply them to their own essay.
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.model_name, 
            temperature=0.2,
            api_key=settings.openai_api_key
        )
        
        self._initialize_prompts()
        
        self.attributes_chain = self.llm.with_structured_output(
            WritingStyleAttributeList,
            method="function_calling"
        )
        self.analysis_chain = self.llm.with_structured_output(
            WritingStyleApplicationList,
            method="function_calling"
        )

    def _initialize_prompts(self):
        """Sets up prompts for attribute extraction and essay analysis"""
        self.attributes_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert in analyzing writing style."),
            ("human", """Generate a list of tone attributes, writing style, writing techniques, 
            word choices, and structural elements that define a piece of writing.
            Consider things like:
            - Pace and flow
            - Emotional tone and mood
            - Structural organization
            - Literary devices and symbolism
            - Author's voice and perspective
            - Sentence variety and length
            - Persuasive techniques
            - Word choices

            Respond with a structured list of attributes and their descriptions.""")
        ])
        
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an MBA essay expert with deep knowledge of writing techniques.
            You are highly opinionated and take an active stance on evaluating writing quality."""),
            ("human", """Below is a list of writing attributes:
            {attributes}

            Analyze the following successful MBA essay examples and identify where these
            attributes are applied. For each attribute, provide:
            1. A step-by-step explanation of how the essay applies this attribute and how a writer can apply it to their own essay.

            Successful MBA Essays:
            {essays}
            
            Ensure NO CONTENT of the example essays is copied in the output.
            """)
        ])

    async def extract_writing_style(self, state: WorkflowState) -> WorkflowState:
        """Extracts writing style attributes and analyzes how they're used in sample essays"""
        try:
            logger.debug("Generating writing style attributes")
            attributes_prompt = await self.attributes_prompt.ainvoke({})
            attributes = await self.attributes_chain.ainvoke(attributes_prompt)
            
            logger.debug("Analyzing essays with generated attributes")
            analysis_prompt = await self.analysis_prompt.ainvoke({
                "attributes": self._format_attributes(attributes),
                "essays": self._format_rag_context_essays(state.rag_context)
            })
            analysis = await self.analysis_chain.ainvoke(analysis_prompt) 
            
            state.writing_style_analysis = analysis
            return state
            
        except Exception as e:
            logger.error(f"Error in writing style extraction: {str(e)}")
            raise

    def _format_attributes(self, attributes: WritingStyleAttributeList) -> str:
        """Formats writing attributes for prompt input"""
        return "\n\n".join([
            f"Attribute: {attr.name}\n"
            f"Category: {attr.category}\n"
            f"Description: {attr.description}"
            for attr in attributes.attributes
        ])

    def _format_rag_context_essays(self, context: Dict[str, List[Dict[str, str]]]) -> str:
        """Formats RAG context essays for prompt input"""
        if not context.get('relevant_examples'):
            logger.warning("No relevant examples found in RAG context")
            return ""
            
        return "\n\n".join([
            f"Example Essay: {example['essay']}"
            for example in context['relevant_examples']
        ]) 