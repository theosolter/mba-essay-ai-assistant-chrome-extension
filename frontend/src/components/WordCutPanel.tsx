import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { WordCutResponse, WordCutEdit } from '@/services/models'

interface WordCutPanelProps {
    result: WordCutResponse;
}

/**
 * WordCutPanel displays the results of text editing operations, showing word count changes
 * and detailed edit suggestions.
 */
export function WordCutPanel({ result }: WordCutPanelProps) {
    // Helper function to format word count differences with consistent +/- signs
    const formatWordDiff = (diff: number) => {
        const sign = diff > 0 ? '-' : '+'
        return `${sign}${Math.abs(diff)}`
    }

    return (
        <div className="space-y-4">
            {/* Summary card showing overall word count changes */}
            <Card>
                <CardHeader>
                    <CardTitle>Word Count Summary</CardTitle>
                    <CardDescription>
                        Original: {result.totalBeforeWordCount} words →{' '}
                        New: {result.totalAfterWordCount} words{' '}
                        ({formatWordDiff(result.totalWordCountDiff)} words)
                    </CardDescription>
                </CardHeader>
            </Card>
            
            {/* Individual edit suggestions */}
            {result.edits.map((edit, index) => (
                <Card key={index}>
                    <CardHeader>
                        <CardTitle>Edit {index + 1}</CardTitle>
                        <CardDescription>
                            {edit.beforeWordCount} → {edit.afterWordCount} words ({formatWordDiff(edit.wordCountDiff)} words)
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div>
                            <h4 className="font-semibold mb-2">Original Text:</h4>
                            <p className="text-sm text-muted-foreground">{edit.before}</p>
                        </div>
                        <div>
                            <h4 className="font-semibold mb-2">Revised Text:</h4>
                            <p className="text-sm italic text-emerald-600">{edit.after}</p>
                        </div>
                        <div>
                            <h4 className="font-semibold mb-2">Explanation:</h4>
                            <p className="text-sm">{edit.explanation}</p>
                        </div>
                    </CardContent>
                </Card>
            ))}
        </div>
    )
} 