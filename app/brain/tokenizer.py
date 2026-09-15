"""
MY AI - Deterministic Tokenizer
Splits text into tokens, preserves indices, extracts n-grams, and provides vocab mapping.
"""
import re
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

@dataclass
class Token:
    text: str
    start: int
    end: int
    is_punct: bool
    is_num: bool

class Tokenizer:
    TOKEN_REGEX = re.compile(r'\w+|[^\w\s]')

    def __init__(self, vocab: Dict[str, int] = None):
        self.vocab = vocab or {}
        self.inv_vocab = {v: k for k, v in self.vocab.items()}

    def tokenize(self, text: str) -> List[str]:
        """Simple whitespace & punctuation tokenization."""
        return [match.group(0) for match in self.TOKEN_REGEX.finditer(text)]

    def tokenize_detailed(self, text: str) -> List[Token]:
        tokens: List[Token] = []
        for match in self.TOKEN_REGEX.finditer(text):
            tok_str = match.group(0)
            is_punct = bool(re.match(r'^[^\w\s]$', tok_str))
            is_num = tok_str.isdigit()
            tokens.append(Token(
                text=tok_str,
                start=match.start(),
                end=match.end(),
                is_punct=is_punct,
                is_num=is_num
            ))
        return tokens

    def get_ngrams(self, tokens: List[str], n: int = 2) -> List[str]:
        if len(tokens) < n:
            return []
        return [" ".join(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]

    def encode(self, tokens: List[str], unk_token: str = "<UNK>", pad_token: str = "<PAD>") -> List[int]:
        unk_idx = self.vocab.get(unk_token, 0)
        return [self.vocab.get(t.lower(), unk_idx) for t in tokens]

    def decode(self, token_ids: List[int]) -> List[str]:
        return [self.inv_vocab.get(idx, "<UNK>") for idx in token_ids]
