import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { GeneralFeedbackItem } from '@/services/models'

interface GeneralFeedbackPanelProps {
    feedback: GeneralFeedbackItem[];
}

/**
 * Displays a list of feedback items with sections, suggestions, and examples
 */
export function GeneralFeedbackPanel({ feedback }: GeneralFeedbackPanelProps) {
    return (
        <div className="space-y-4">
            {feedback.map((feedbackItem, index) => (
                <Card key={index}>
                    <CardHeader>
                        <CardTitle>{feedbackItem.section}</CardTitle>
                        <CardDescription>{feedbackItem.feedback}</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div>
                            <h4 className="font-semibold mb-2">Suggestion:</h4>
                            <p className="text-sm">{feedbackItem.suggestion}</p>
                        </div>
                        <div>
                            <h4 className="font-semibold mb-2">Example Application:</h4>
                            <p className="text-sm italic text-emerald-600">{feedbackItem.exampleApplication}</p>
                        </div>
                    </CardContent>
                </Card>
            ))}
        </div>
    )
} 