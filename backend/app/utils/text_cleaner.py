def clean_essay_text(essay_text: str, essay_prompt: str) -> str:
    """
    Remove the essay prompt from the essay text if it appears at the beginning.
    This handles cases where users copy both prompt and essay from Google Docs.
    """

    if not essay_text or not essay_prompt:
        return essay_text

    normalized_text = ' '.join(essay_text.strip().split()).lower()
    normalized_prompt = ' '.join(essay_prompt.strip().split()).lower()

    # Check if essay starts with the prompt
    if normalized_text.startswith(normalized_prompt):
        cleaned_text = essay_text[len(essay_prompt):].strip()
        return cleaned_text

    return essay_text 