import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { LanguageEdit } from '@/services/models'

interface LanguageEditsPanelProps {
    edits: LanguageEdit[]
}

/**
 * Displays a list of language edit suggestions with original text and proposed revisions
 */
export function LanguageEditsPanel({ edits }: LanguageEditsPanelProps) {
    return (
        <div className="space-y-4">
            {edits.map((edit, index) => (
                <Card key={`language-edit-${index}`}>
                    <CardHeader>
                        <h4 className="font-semibold mb-2">Original Text:</h4>
                        <p className="text-sm text-muted-foreground">{edit.before}</p>
                    </CardHeader>
                    <CardContent>
                        <h4 className="font-semibold mb-2">Suggested Revision:</h4>
                        <p className="text-sm italic text-emerald-600">{edit.after}</p>
                    </CardContent>
                </Card>
            ))}
        </div>
    )
} 