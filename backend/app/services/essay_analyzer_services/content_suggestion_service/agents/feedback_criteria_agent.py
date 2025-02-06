from typing import Dict, List
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from .....config import get_settings
from ..models import FeedbackFramework, WorkflowState
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

class FeedbackCriteriaExtractionAgent:
    """Analyzes expert MBA essay feedback to extract structured evaluation criteria."""
    
    def __init__(self):
        self.llm: ChatOpenAI = ChatOpenAI(
            model=settings.model_name, 
            temperature=0.2,
            api_key=settings.openai_api_key
        )
        
        self.criteria_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert in MBA essay evaluation with a keen eye for detail. 
            Your responses must be in valid JSON format matching the specified schema.
            Ensure all strings are properly escaped and JSON is well-formed."""),
            ("human", """Below are excerpts from expert feedback on MBA essays:
            {feedback}

            Analyze this feedback to identify common evaluation criteria. For each criterion, provide:
            1. **Name**: The designation of the criterion.
            2. **Description**: What the criterion assesses in an essay.
            3. **Example Feedback**: Generate a concrete example of feedback that demonstrates how this criterion should be applied.

            Ensure your analysis is thorough and captures the nuances of effective MBA essay evaluation.

            For the output, make sure all quotes and special characters are properly escaped and that NO CONTENT of the essays the example feedback analyzes is exposed.
            """)
        ])
    
        self.criteria_chain = (
            self.llm
            .with_structured_output(
                FeedbackFramework,
                method="function_calling")
        )

    async def extract_feedback_framework(self, state: WorkflowState) -> WorkflowState:
        """Extracts feedback criteria from RAG context and returns updated workflow state."""
        try:
            prompt = await self.criteria_prompt.ainvoke({
                "feedback": self._format_rag_context_feedback(state.rag_context)
            })
            
            try:
                criteria_response = await self.criteria_chain.ainvoke(prompt)
                
                if not criteria_response or not criteria_response.criteria:
                    raise ValueError("Invalid feedback framework generated: empty criteria")

                logger.info("Successfully extracted feedback framework", extra={
                    "num_criteria": len(criteria_response.criteria),
                    "criteria_names": [c.name for c in criteria_response.criteria]
                })
                
                state.feedback_framework = criteria_response
                return state
                
            except Exception as parsing_error:
                logger.error("Failed to parse LLM output", extra={
                    "error": str(parsing_error),
                    "error_type": type(parsing_error).__name__
                })
                raise ValueError(f"Failed to generate valid feedback framework: {str(parsing_error)}")
                
        except Exception as e:
            logger.error("Failed to extract feedback framework", extra={
                "error": str(e),
                "rag_context_size": len(state.rag_context.get('relevant_examples', []))
            })
            raise RuntimeError(f"Failed to extract feedback framework: {str(e)}") from e

    def _format_rag_context_feedback(self, context: Dict[str, List[Dict[str, str]]]) -> str:
        """Formats RAG context examples into a string for the prompt."""
        if not context or not context.get('relevant_examples'):
            logger.warning("Empty RAG context provided")
            return ""
            
        return "\n\n".join([
            f"Example Feedback: {example['feedback']}"
            for example in context['relevant_examples']
            if example.get('feedback')
        ]) 