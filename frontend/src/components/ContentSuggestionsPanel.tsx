import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ContentSuggestion } from '@/services/models'

interface ContentSuggestionsPanelProps {
    suggestions: ContentSuggestion[];
}

/**
 * Panel component that displays a list of content improvement suggestions for an essay
 */
export function ContentSuggestionsPanel({ suggestions }: ContentSuggestionsPanelProps) {
    return (
        <div className="space-y-4">
            {suggestions.map((suggestion, index) => (
                <Card key={`content-suggestion-${index}`}>
                    <CardHeader>
                        <CardTitle>{suggestion.suggestion}</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div>
                            <h4 className="font-semibold mb-2">How to Apply:</h4>
                            <p className="text-sm">{suggestion.howToApply}</p>
                        </div>
                        <div>
                            <h4 className="font-semibold mb-2">Original Text:</h4>
                            <p className="text-sm">{suggestion.originalText}</p>
                        </div>
                        <div>
                            <h4 className="font-semibold mb-2">Improved Version:</h4>
                            <p className="text-sm italic text-emerald-600">
                                {suggestion.improvedVersion}
                            </p>
                        </div>
                    </CardContent>
                </Card>
            ))}
        </div>
    )
} 