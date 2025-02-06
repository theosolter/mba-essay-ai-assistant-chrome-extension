/**
 * IMPORTANT: All type field mappings between frontend and backend must be kept in sync.
 * If you modify types in this file, make corresponding changes in:
 * backend/app/services/essay_analyzer_services/models.py
 */


// Base types
export interface BaseEssayRequest {
    essayText: string;
    essayPrompt: string;
    userInstructions: string;
    school: string;
}

// Essay Analysis types
export interface ContentSuggestion {
    suggestion: string;
    howToApply: string;
    sectionToImprove: string;
    improvedVersion: string;
}

export interface LanguageEdit {
    before: string;
    after: string;
}

export interface GeneralFeedbackItem {
    section: string;
    feedback: string;
    suggestion: string;
    exampleApplication: string;
}

export interface AnalysisResponse {
    contentSuggestions: ContentSuggestion[];
    languageEdits: LanguageEdit[];
    generalFeedback: GeneralFeedbackItem[];
}

export interface AnalysisRequest extends BaseEssayRequest {}

// Word Cutter types
export interface WordCutEdit {
    before: string;
    after: string;
    beforeWordCount: number;
    afterWordCount: number;
    wordCountDiff: number;
    explanation: string;
}

export interface WordCutResponse {
    totalBeforeWordCount: number;
    totalAfterWordCount: number;
    totalWordCountDiff: number;
    edits: WordCutEdit[];
}

export interface WordCutRequest extends BaseEssayRequest {
    wordLimit: number;
} 