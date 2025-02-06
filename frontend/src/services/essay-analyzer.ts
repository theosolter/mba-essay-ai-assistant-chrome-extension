// IMPORTANT: All type field mappings between frontend and backend are documented in ./type-mappings.ts
import { API_BASE_URL } from '@/config'
import { 
    AnalysisRequest, 
    AnalysisResponse 
} from './models'

export const essayService = {
    analyzeEssay: async (requestData: AnalysisRequest): Promise<AnalysisResponse> => {
        try {
            // Convert frontend camelCase to backend snake_case
            const snakeCaseData = {
                essay_text: requestData.essayText,
                essay_prompt: requestData.essayPrompt,
                user_instructions: requestData.userInstructions,
                school: requestData.school,
            };

            const response = await fetch(`${API_BASE_URL}/api/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(snakeCaseData),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Analysis failed');
            }

            const data = await response.json();
            // Transform snake_case response from Python backend to camelCase for frontend\
            return {
                contentSuggestions: data.content_suggestions.map((suggestion: any) => ({
                    suggestion: suggestion.suggestion,
                    howToApply: suggestion.how_to_apply,
                    originalText: suggestion.original_text,
                    improvedVersion: suggestion.improved_version
                })),
                languageEdits: data.language_edits.map((edit: any) => ({
                    before: edit.before,
                    after: edit.after
                })),
                generalFeedback: data.general_feedback.map((feedback: any) => ({
                    section: feedback.section,
                    feedback: feedback.feedback,
                    suggestion: feedback.suggestion,
                    exampleApplication: feedback.example_application
                }))
            };
        } catch (error) {
            console.error('[Essay Service] Analysis failed:', error);
            throw error;
        }
    },

    checkHealth: async (): Promise<boolean> => {
        try {
            const response = await fetch(`${API_BASE_URL}/health`);
            const data = await response.json();
            return data.status === 'healthy';
        } catch (error) {
            console.error('[Essay Service] Health check failed:', error);
            return false;
        }
    },
};