from typing import Dict
import json
import logging
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from .....config import get_settings
from ..models import (
    ContentSuggestionList,
    WritingStyleApplicationList,
    WorkflowState
)

# Configure logging
logger = logging.getLogger(__name__)
settings = get_settings()

class ContentSuggestionAgent:
    """Generates and refines content suggestions for MBA essays using LLMs."""
    
    def __init__(self):
        logger.info("Initializing ContentSuggestionAgent")
        
        self.llm = ChatOpenAI(
            model=settings.model_name,
            temperature=0.7,
            api_key=settings.openai_api_key
        )

        self.initial_chain = self.llm.with_structured_output(
            ContentSuggestionList,
            method="function_calling"
        )
        self.refinement_chain = self.llm.with_structured_output(
            ContentSuggestionList,
            method="function_calling"
        )

        self.initial_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an experienced MBA admissions essay coach. Your role is to provide 
            highly specific, expert-level content suggestions that improve the structure, clarity, 
            and effectiveness of the user's MBA application essay. Focus on concrete improvements 
            to specific sections of text."""),

            ("human", """Analyze the following MBA essay and generate 5-6 specific content suggestions 
            to enhance its impact. For each suggestion, identify a specific section of text to improve 
            and provide a rewritten version.

            **Essay Prompt:** {prompt}
            **Essay Text:** {text}
            **User Instructions:** {user_instructions}
            **School Guidelines:** {school_guidelines}
            
            **Writing Style Attributes & Best Practices:**  
            {writing_style_attributes}

            **Task:**
            1. For each suggestion:
               - Select a specific paragraph or section from the essay that needs improvement
               - Provide a clear suggestion for improving that specific section
               - Give step-by-step guidance on implementing the improvement
               - Rewrite that section to demonstrate the improvement while maintaining the author's voice

            2. Ensure each rewritten section:
               - Directly implements the suggested improvement
               - Maintains consistency with the surrounding text
               - Follows the writing style attributes
               - Preserves the author's core message and voice
               - Is not overly verbose and does not use words that are unnecessarily complex (the message of the essay should be easy to read and understand)""")
        ])

        self.refinement_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert MBA admissions essay coach. Refine suggestions
            based on feedback while maintaining alignment with writing style techniques."""),
            
            ("human", """Previous Suggestions with Feedback:
            {previous_suggestions}
            
            {writing_style_attributes}
            
            Refine each suggestion to address its feedback while maintaining effective
            writing style techniques and patterns.""")
        ])

    async def generate_initial_suggestions(self, state: WorkflowState) -> WorkflowState:
        """Generates content suggestions based on the essay and writing style attributes."""
        logger.debug("Generating initial suggestions", extra={
            "essay_length": len(state.essay_text),
            "prompt_length": len(state.essay_prompt)
        })
        
        formatted_prompt = await self.initial_prompt.ainvoke({
            "prompt": state.essay_prompt,
            "text": state.essay_text,
            "user_instructions": state.user_instructions,
            "school_guidelines": state.school_guidelines,
            "writing_style_attributes": self._format_writing_style_attributes(
                state.writing_style_analysis.applications
            )
        })
        
        response = await self.initial_chain.ainvoke(formatted_prompt)
        state.suggestions = response
        return state

    async def refine_suggestions(self, state: WorkflowState) -> WorkflowState:
        """Updates existing suggestions based on feedback."""
        if not state.feedback:
            logger.debug("No feedback provided for refinement, skipping")
            return state
            
        formatted_prompt = await self.refinement_prompt.ainvoke({
            "previous_suggestions": self._format_suggestions_with_feedback(
                state.suggestions,
                state.feedback
            ),
            "writing_style_attributes": self._format_writing_style_attributes(
                state.writing_style_analysis.applications
            )
        })
        
        response = await self.refinement_chain.ainvoke(formatted_prompt)
        state.suggestions = response
        return state

    def _format_writing_style_attributes(self, applications: WritingStyleApplicationList) -> str:
        """Formats writing style attributes into a structured string."""
        return (
            "\n\nWriting Style Attributes applications in successful essays:\n" +
            "\n\n".join([
                f"Attribute: {application.attribute}\n"
                f"How to Apply: {application.how_to_apply}\n"
                for application in applications
            ])
        )

    def _format_suggestions_with_feedback(
        self,
        suggestions: ContentSuggestionList,
        feedback: Dict
    ) -> str:
        """Combines suggestions and feedback into a formatted string."""
        formatted_items = []
        
        for idx, (suggestion, feedback_item) in enumerate(
            zip(suggestions.suggestions, feedback.suggestion_feedback), 1
        ):
            suggestion_dict = {
                "suggestion": suggestion.suggestion,
                "example_inspiration": suggestion.example_inspiration,
                "how_to_apply": suggestion.how_to_apply,
                "example_application": suggestion.example_application
            }
            
            formatted_items.append(
                f"Suggestion {idx}:\n"
                f"{json.dumps(suggestion_dict, indent=2)}\n\n"
                f"Feedback for this suggestion:\n"
                f"Score: {feedback_item.score}\n"
                f"Feedback: {feedback_item.feedback}\n"
                f"Areas for Improvement:\n" + 
                "\n".join(f"- {area}" for area in feedback_item.improvement_areas)
            )
        
        return "\n\n" + "="*50 + "\n\n".join(formatted_items) 