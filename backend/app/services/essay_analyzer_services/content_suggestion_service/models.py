from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from ...models import ContentSuggestion

class WritingStyleAttribute(BaseModel):
    name: str = Field(description="Name of the writing attribute")
    category: str = Field(description="Category (tone, structure, technique, etc.)")
    description: str = Field(description="Description of the attribute")

class WritingStyleAttributeList(BaseModel):
    attributes: List[WritingStyleAttribute] = Field(description="List of writing attributes")

class WritingStyleApplication(BaseModel):
    attribute: str = Field(description="Name of the writing attribute")
    how_to_apply: str = Field(description="Step-by-step instructions on how to apply this attribute")

class WritingStyleApplicationList(BaseModel):
    applications: List[WritingStyleApplication] = Field(description="How attributes are applied in examples")

class FeedbackCriterion(BaseModel):
    name: str = Field(description="Name of the criterion")
    description: str = Field(description="What this criterion measures")
    example_feedback: str = Field(description="Example of applying this criterion")

class FeedbackFramework(BaseModel):
    criteria: List[FeedbackCriterion] = Field(description="Evaluation criteria")

class ContentSuggestionList(BaseModel):
    suggestions: List[ContentSuggestion]

class SuggestionFeedback(BaseModel):
    feedback: str = Field(description="Specific feedback for this content suggestion")
    score: float = Field(description="Quality score from 1-10 for this suggestion", ge=1, le=10)
    improvement_areas: List[str] = Field(description="Areas where this suggestion could be improved")

class FeedbackResponse(BaseModel):
    suggestion_feedback: List[SuggestionFeedback] = Field(description="Feedback for each content suggestion")
    overall_score: float = Field(description="Average quality score across all suggestions", ge=1, le=10)

class WorkflowState(BaseModel):
    # RAG Context
    rag_context: Dict = Field(default_factory=dict)
    
    # Extraction Results
    writing_style_analysis: Optional[WritingStyleApplicationList] = None
    feedback_framework: Optional[FeedbackFramework] = None
    
    # Iterative State
    suggestions: Optional[ContentSuggestionList] = None
    feedback: Optional[FeedbackResponse] = None
    
    # Request Data
    essay_text: str = ""
    essay_prompt: str = ""
    user_instructions: str = ""
    school_guidelines: str = ""
    
    # Control
    iteration: int = 0
    max_iterations: int = 5