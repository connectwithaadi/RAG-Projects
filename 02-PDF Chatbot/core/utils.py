
import re

def clean_text(text: str) -> str:
    """
    Clean extracted PDF text.
    """

    text = re.sub(r'\n+', '\n', text)

    text = re.sub(r'\s+', ' ', text)

    text = text.strip()

    return text

def word_count(text):
    return len(text.split())

def character_count(text):
    return len(text)
