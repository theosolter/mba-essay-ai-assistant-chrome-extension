import { useState, useEffect } from 'react'
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { LoadingState } from './LoadingState'
import { TextSelect } from 'lucide-react'
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ContentSuggestionsPanel } from '@/components/ContentSuggestionsPanel'
import { LanguageEditsPanel } from '@/components/LanguageEditsPanel'
import { GeneralFeedbackPanel } from '@/components/GeneralFeedbackPanel'
import { AnalysisResponse, WordCutResponse } from '@/services/models'
import { essayService } from '@/services/essay-analyzer'
import { wordCutterService } from '@/services/word-cutter'
import { Switch } from "@/components/ui/switch"
import { Input } from "@/components/ui/input"
import { WordCutPanel } from '@/components/WordCutPanel'
import { Collapsible, CollapsibleTrigger, CollapsibleContent } from "@/components/ui/collapsible"

// Constants to avoid magic strings and improve maintainability
// TODO: Move to backend and fetch from there
const SCHOOLS = [
    { value: "Harvard Business School", label: "Harvard Business School" },
    { value: "Stanford GSB", label: "Stanford GSB" },
    { value: "Wharton", label: "Wharton" },
    { value: "Chicago Booth", label: "Chicago Booth" },
    { value: "MIT Sloan", label: "MIT Sloan" },
    { value: "Columbia Business School", label: "Columbia Business School" },
] as const;

export function MbaEssayAssistant() {
    // State management for form inputs
    const [essayPrompt, setEssayPrompt] = useState('')
    const [userInstructions, setUserInstructions] = useState('')
    const [selectedSchool, setSelectedSchool] = useState<string>('')
    const [manualEssayText, setManualEssayText] = useState('')
    const [useManualInput, setUseManualInput] = useState(false)

    // State for UI controls
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [showInstructions, setShowInstructions] = useState(true)
    const [isSignedIn, setIsSignedIn] = useState(false)

    // Analysis results state
    const [analysisResult, setAnalysisResult] = useState<AnalysisResponse | null>(null)

    // Word cutter specific state
    const [cutMode, setCutMode] = useState<'limit' | 'reduce'>('limit')
    const [wordLimit, setWordLimit] = useState<number | null>(null)
    const [wordsToReduce, setWordsToReduce] = useState<number | null>(null)
    const [wordCutResult, setWordCutResult] = useState<WordCutResponse | null>(null)

    useEffect(() => {
        // Initialize authentication state and sidebar
        const initAuth = () => {
            chrome.storage.local.get(['user', 'sidebarEnabled'], (result) => {
                setIsSignedIn(!!result.user);
                if (result.user && !result.sidebarEnabled) {
                    chrome.storage.local.set({ sidebarEnabled: true });
                }
            });
        };

        initAuth();

        // Listen for auth state changes
        const authListener = (changes: { [key: string]: chrome.storage.StorageChange }) => {
            if (changes.user) {
                setIsSignedIn(!!changes.user.newValue);
            }
        };

        chrome.storage.onChanged.addListener(authListener);

        // Cleanup listener on unmount
        return () => {
            chrome.storage.onChanged.removeListener(authListener);
        };
    }, []);

    /**
     * Extracts the Google Doc ID from the current URL
     */
    const getCurrentDocId = (): string | null => {
        const url = new URL(window.location.href);
        const matches = url.pathname.match(/\/document\/d\/([a-zA-Z0-9-_]+)/);
        return matches ? matches[1] : null;
    };

    /**
     * Fetches the essay text from the current Google Doc
     */
    const getCurrentEssayText = async (): Promise<string> => {
        const docId = getCurrentDocId();
        if (!docId) {
            throw new Error('Could not determine document ID');
        }

        return new Promise((resolve, reject) => {
            chrome.runtime.sendMessage(
                { action: 'getEssayContent', docId },
                (response) => {
                    if (response?.success) {
                        resolve(response.content);
                    } else {
                        reject(new Error(response?.error || 'Failed to fetch document content'));
                    }
                }
            );
        });
    };

    /**
     * Validates input and triggers essay analysis
     */
    const handleAnalyze = async () => {
        try {
            setIsLoading(true);
            setError(null);

            // Input validation
            if (!isSignedIn) throw new Error('Please sign in to analyze essays');
            if (!selectedSchool) throw new Error('Please select a school');
            if (!essayPrompt) throw new Error('Please enter an essay prompt');
            if (useManualInput && !manualEssayText) throw new Error('Please enter essay text');

            const textToAnalyze = useManualInput ? manualEssayText : await getCurrentEssayText();

            const result = await essayService.analyzeEssay({
                essayText: textToAnalyze,
                essayPrompt,
                userInstructions: userInstructions || '',
                school: selectedSchool
            });

            setAnalysisResult(result);
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'An unexpected error occurred';
            setError(errorMessage);
        } finally {
            setIsLoading(false);
        }
    };

    /**
     * Calculates the target word limit based on current text and reduction amount
     */
    const calculateWordLimit = (text: string, reduction: number): number => {
        const currentWordCount = text.split(/\s+/).length;
        return currentWordCount - (reduction || 0);
    };

    /**
     * Handles the word cutting operation
     */
    const handleCutWords = async () => {
        try {
            setIsLoading(true);
            setError(null);

            const essayText = useManualInput ? manualEssayText : await getCurrentEssayText();
            if (!essayText) {
                throw new Error("No essay text found. Please enter text manually or select text on the page.");
            }

            const targetWordLimit = cutMode === 'limit' 
                ? wordLimit! 
                : calculateWordLimit(essayText, wordsToReduce!);

            const result = await wordCutterService.cutWords({
                essayText,
                essayPrompt,
                userInstructions,
                school: selectedSchool,
                wordLimit: targetWordLimit
            });

            setWordCutResult(result);
        } catch (error) {
            setError(error instanceof Error ? error.message : 'An error occurred');
        } finally {
            setIsLoading(false);
        }
    };

    if (!isSignedIn) {
        return (
            <div className="w-[500px] h-screen bg-background border-l">
                <div className="w-full p-4">
                    <Alert>
                        <AlertDescription>
                            Please sign in using the extension popup to analyze essays.
                        </AlertDescription>
                    </Alert>
                </div>
            </div>
        );
    }

    return (
        <div className="w-[500px] h-screen bg-background border-l">
            <ScrollArea className="h-full">
                <div className="p-4 space-y-4">
                    <h1 className="text-2xl font-bold">MBA Essay Assistant</h1>
                    
                    {/* Instructions Collapsible */}
                    <Collapsible
                        open={showInstructions}
                        onOpenChange={setShowInstructions}
                    >
                        <CollapsibleTrigger className="w-full">
                            <span>📝 Instructions {showInstructions ? 'Hide' : 'Show'}</span>
                        </CollapsibleTrigger>
                        <CollapsibleContent>
                            <Alert className="mt-2">
                                <AlertDescription className="space-y-3">
                                    <div>
                                        <p className="font-medium mb-1">📄 Document Setup</p>
                                        <ul className="list-disc pl-4 space-y-1 text-sm">
                                            <li>Remove all comments, formatting marks, and non-essay content</li>
                                            <li>If your essay prompt is in the document:
                                                <ul className="list-disc pl-4 mt-1">
                                                    <li>Place it at the very top</li>
                                                    <li>Copy the exact prompt text to the "Essay Prompt" field below</li>
                                                    <li>The analyzer will automatically exclude the prompt from analysis</li>
                                                </ul>
                                            </li>
                                        </ul>
                                    </div>

                                    <div>
                                        <p className="font-medium mb-1">🔍 Analysis Methods</p>
                                        <ul className="list-disc pl-4 space-y-1 text-sm">
                                            <li>Full Document: Click "Analyze Essay" to process entire content</li>
                                            {/* <li>Selected Text: Highlight any section and click "Analyze Selected Text"</li> */}
                                            <li>Manual Input: Toggle the switch to paste text directly</li>
                                        </ul>
                                    </div>

                                    <div>
                                        <p className="font-medium mb-1">✂️ Word Cutter</p>
                                        <ul className="list-disc pl-4 space-y-1 text-sm">
                                            <li>Uses the same text source as the analyzer (full doc/manual)</li>
                                            <li>Set your target word count and click "Cut Words"</li>
                                        </ul>
                                    </div>

                                    <div className="text-sm mt-2 pt-2 border-t">
                                        <strong>Note:</strong> Sign in required for all features
                                    </div>
                                </AlertDescription>
                            </Alert>
                        </CollapsibleContent>
                    </Collapsible>

                    {/* Common Inputs Section */}
                    <div className="space-y-4">
                        <div className="space-y-2">
                            <label htmlFor="school-select" className="text-sm font-medium">
                                School
                            </label>
                            <Select
                                value={selectedSchool}
                                onValueChange={setSelectedSchool}
                            >
                                <SelectTrigger
                                    id="school-select"
                                    className="w-full bg-background"
                                >
                                    <SelectValue
                                        placeholder="Select a school"
                                        className="text-muted-foreground"
                                    />
                                </SelectTrigger>
                                <SelectContent
                                    position="popper"
                                    className="w-[var(--radix-select-trigger-width)] bg-popover z-[9999]"
                                >
                                    <div className="max-h-[200px] overflow-y-auto">
                                        {SCHOOLS.map((school) => (
                                            <SelectItem
                                                key={school.value}
                                                value={school.value}
                                                className="cursor-pointer hover:bg-accent"
                                            >
                                                {school.label}
                                            </SelectItem>
                                        ))}
                                    </div>
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="space-y-2">
                            <label htmlFor="essay-prompt" className="text-sm font-medium">
                                Essay Prompt
                            </label>
                            <Textarea
                                id="essay-prompt"
                                placeholder="Paste your essay prompt here..."
                                value={essayPrompt}
                                onChange={(e) => setEssayPrompt(e.target.value)}
                            />
                        </div>

                        <div className="space-y-2">
                            <div className="flex items-center space-x-2">
                                <label htmlFor="manual-input" className="text-sm font-medium">
                                    Manual Essay Input
                                </label>
                                <Switch
                                    id="manual-input"
                                    checked={useManualInput}
                                    onCheckedChange={setUseManualInput}
                                />
                            </div>
                            {useManualInput && (
                                <Textarea
                                    id="manual-essay"
                                    placeholder="Paste your essay text here..."
                                    value={manualEssayText}
                                    onChange={(e) => setManualEssayText(e.target.value)}
                                    className="min-h-[200px]"
                                />
                            )}
                        </div>

                        <div className="space-y-2">
                            <label htmlFor="user-instructions" className="text-sm font-medium">
                                Additional Instructions (Optional)
                            </label>
                            <Textarea
                                id="user-instructions"
                                placeholder="What specific help do you need? (e.g., 'Focus on leadership examples')"
                                value={userInstructions}
                                onChange={(e) => setUserInstructions(e.target.value)}
                            />
                        </div>
                    </div>

                    {error && (
                        <Alert variant="destructive">
                            <AlertDescription>{error}</AlertDescription>
                        </Alert>
                    )}

                    {/* Main Tabs */}
                    <Tabs defaultValue="analyzer" className="mt-4">
                        <TabsList className="grid w-full grid-cols-2">
                            <TabsTrigger value="analyzer">Essay Analyzer</TabsTrigger>
                            <TabsTrigger value="wordcutter">Word Cutter</TabsTrigger>
                        </TabsList>

                        {/* Essay Analyzer Tab */}
                        <TabsContent value="analyzer" className="space-y-4">
                            <Button
                                onClick={handleAnalyze}
                                className="w-full"
                                disabled={isLoading}
                            >
                                <TextSelect className="mr-2 h-4 w-4" />
                                Analyze Essay
                            </Button>

                            {isLoading ? (
                                <LoadingState />
                            ) : analysisResult && (
                                <Tabs defaultValue="content" className="mt-4">
                                    <TabsList className="grid w-full grid-cols-3">
                                        <TabsTrigger value="feedback">Feedback</TabsTrigger>
                                        <TabsTrigger value="content">Content</TabsTrigger>
                                        <TabsTrigger value="language">Language</TabsTrigger>
                                        
                                    </TabsList>
                                    <TabsContent value="feedback">
                                        <GeneralFeedbackPanel feedback={analysisResult.generalFeedback} />
                                    </TabsContent>
                                    <TabsContent value="content">
                                        <ContentSuggestionsPanel suggestions={analysisResult.contentSuggestions} />
                                    </TabsContent>
                                    <TabsContent value="language">
                                        <LanguageEditsPanel edits={analysisResult.languageEdits} />
                                    </TabsContent>
                                </Tabs>
                            )}
                        </TabsContent>

                        {/* Word Cutter Tab */}
                        <TabsContent value="wordcutter" className="space-y-4">
                            <div className="space-y-4">
                                <div className="flex items-center space-x-2">
                                    <label className="text-sm font-medium">Cut Mode:</label>
                                    <Select
                                        value={cutMode}
                                        onValueChange={(value: 'limit' | 'reduce') => {
                                            setCutMode(value)
                                            // Reset the other value when switching modes
                                            if (value === 'limit') {
                                                setWordsToReduce(null)
                                            } else {
                                                setWordLimit(null)
                                            }
                                        }}
                                    >
                                        <SelectTrigger className="w-[180px]">
                                            <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="limit">Target Word Limit</SelectItem>
                                            <SelectItem value="reduce">Reduce Words By</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>

                                <div className="flex items-center space-x-2">
                                    {cutMode === 'limit' ? (
                                        <Input
                                            type="number"
                                            min="1"
                                            placeholder="Word Limit"
                                            value={wordLimit || ''}
                                            onChange={(e) => {
                                                const value = parseInt(e.target.value);
                                                if (!isNaN(value) && value > 0) {
                                                    setWordLimit(value);
                                                } else {
                                                    setWordLimit(null);
                                                }
                                            }}
                                            className="w-32"
                                        />
                                    ) : (
                                        <Input
                                            type="number"
                                            min="1"
                                            placeholder="Words to cut"
                                            value={wordsToReduce || ''}
                                            onChange={(e) => {
                                                const value = parseInt(e.target.value);
                                                if (!isNaN(value) && value > 0) {
                                                    setWordsToReduce(value);
                                                } else {
                                                    setWordsToReduce(null);
                                                }
                                            }}
                                            className="w-32"
                                        />
                                    )}
                                    <Button
                                        onClick={handleCutWords}
                                        disabled={isLoading || (cutMode === 'limit' ? !wordLimit : !wordsToReduce)}
                                        className="flex-1"
                                    >
                                        Cut Words
                                    </Button>
                                </div>
                            </div>

                            {isLoading ? (
                                <LoadingState />
                            ) : wordCutResult && (
                                <WordCutPanel result={wordCutResult} />
                            )}
                        </TabsContent>
                    </Tabs>
                </div>
            </ScrollArea>
        </div>
    )
}