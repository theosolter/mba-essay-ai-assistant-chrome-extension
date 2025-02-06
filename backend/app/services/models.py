from pydantic import BaseModel, Field
from typing import List

"""
IMPORTANT: All type field mappings between frontend and backend must be kept in sync.
If you modify types in this file, make corresponding changes in:
frontend/src/services/models.ts
"""
# Essay Analyzer Service Models
class LanguageEdit(BaseModel):
    before: str
    after: str

class GeneralFeedbackItem(BaseModel):
    section: str
    feedback: str
    suggestion: str
    example_application: str

class ContentSuggestion(BaseModel):
    suggestion: str = Field(
        description="The specific suggestion for improving this section of the essay"
    )
    how_to_apply: str = Field(
        description="Clear step-by-step instructions on how to implement this suggestion"
    )
    original_text: str = Field(
        description="The specific section of text from the essay that needs improvement"
    )
    improved_version: str = Field(
        description="A rewritten version of the original text that implements the suggestion"
    )

class AnalysisResponse(BaseModel):
    content_suggestions: List[ContentSuggestion]
    language_edits: List[LanguageEdit]
    general_feedback: List[GeneralFeedbackItem]

class AnalysisRequest(BaseModel):
    essay_text: str
    essay_prompt: str
    user_instructions: str
    school: str 

# Word Cutter Service Models
class WordCutEdit(BaseModel):
    before: str
    after: str
    before_word_count: int
    after_word_count: int
    word_count_diff: int
    explanation: str

class WordCutResponse(BaseModel):
    total_before_word_count: int
    total_after_word_count: int
    total_word_count_diff: int
    edits: List[WordCutEdit]

class WordCutRequest(BaseModel):
    essay_text: str
    essay_prompt: str
    user_instructions: str
    school: str
    word_limit: int