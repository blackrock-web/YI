"""
MY AI - Text Parser & Normalizer
Deterministic text cleaning, contraction expansion, and normalization.
"""
import re
from typing import Dict, List

CONTRACTIONS: Dict[str, str] = {
    "i'm": "i am",
    "you're": "you are",
    "he's": "he is",
    "she's": "she is",
    "it's": "it is",
    "we're": "we are",
    "they're": "they are",
    "i've": "i have",
    "you've": "you have",
    "we've": "we have",
    "they've": "they have",
    "i'd": "i would",
    "you'd": "you would",
    "he'd": "he would",
    "she'd": "she would",
    "we'd": "we would",
    "they'd": "they would",
    "i'll": "i will",
    "you'll": "you will",
    "he'll": "he will",
    "she'll": "she will",
    "we'll": "we will",
    "they'll": "they will",
    "isn't": "is not",
    "aren't": "are not",
    "wasn't": "was not",
    "weren't": "were not",
    "haven't": "have not",
    "hasn't": "has not",
    "hadn't": "had not",
    "won't": "will not",
    "wouldn't": "would not",
    "don't": "do not",
    "doesn't": "does not",
    "didn't": "did not",
    "can't": "cannot",
    "couldn't": "could not",
    "shouldn't": "should not",
    "mightn't": "might not",
    "mustn't": "must not",
    "what's": "what is",
    "where's": "where is",
    "who's": "who is",
    "how's": "how is",
    "let's": "let us",
}

class TextParser:
    @staticmethod
    def expand_contractions(text: str) -> str:
        words = text.split()
        expanded = []
        for word in words:
            lower = word.lower()
            if lower in CONTRACTIONS:
                expanded.append(CONTRACTIONS[lower])
            else:
                expanded.append(word)
        return " ".join(expanded)

    @staticmethod
    def normalize(text: str, keep_case: bool = False) -> str:
        if not text:
            return ""
        # Expand contractions first
        clean = TextParser.expand_contractions(text)
        if not keep_case:
            clean = clean.lower()
        # Remove multiple spaces and trim
        clean = re.sub(r'\s+', ' ', clean).strip()
        return clean

    @staticmethod
    def strip_punctuation(text: str) -> str:
        # Keep alphanumeric, spaces, and hyphens/underscores
        return re.sub(r'[^\w\s-]', '', text)

    @staticmethod
    def extract_quoted_strings(text: str) -> List[str]:
        return re.findall(r'["\'](.*?)["\']', text)
