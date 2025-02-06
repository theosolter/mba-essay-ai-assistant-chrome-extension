// IMPORTANT: All type field mappings between frontend and backend are documented in ./type-mappings.ts
import { API_BASE_URL } from '@/config'
import { 
    WordCutRequest,
    WordCutResponse 
} from './models'


export const wordCutterService = {
    cutWords: async (requestData: WordCutRequest): Promise<WordCutResponse> => {
        try {
            // Convert frontend camelCase to backend snake_case
            const snakeCaseData = {
                essay_text: requestData.essayText,
                essay_prompt: requestData.essayPrompt,
                user_instructions: requestData.userInstructions,
                school: requestData.school,
                word_limit: requestData.wordLimit
            };

            const response = await fetch(`${API_BASE_URL}/api/cut-words`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(snakeCaseData),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Word reduction failed');
            }

            const data = await response.json();
            // Transform snake_case response from Python backend to camelCase for frontend
            const wordCutResponse: WordCutResponse = {
                totalBeforeWordCount: data.total_before_word_count,
                totalAfterWordCount: data.total_after_word_count,
                totalWordCountDiff: data.total_word_count_diff,
                edits: data.edits.map((edit: any) => ({
                    before: edit.before,
                    after: edit.after,
                    beforeWordCount: edit.before_word_count,
                    afterWordCount: edit.after_word_count,
                    wordCountDiff: edit.word_count_diff,
                    explanation: edit.explanation
                }))
            };
            return wordCutResponse;
        } catch (error) {
            console.error('[Word Cutter Service] Word reduction failed:', error);
            throw error;
        }
    },
}; 