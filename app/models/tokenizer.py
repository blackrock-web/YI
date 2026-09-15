"""
MY AI - In-House Byte-Pair Encoding (BPE) Tokenizer
Built 100% from scratch: subword training, token merging, byte encoding, and vocab persistence.
Zero external tokenizer libraries (no HuggingFace, no tiktoken).
"""
from typing import List, Dict, Tuple, Optional
import json
from pathlib import Path
from collections import defaultdict

class BPETokenizer:
    SPECIAL_TOKENS = ["<|pad|>", "<|unk|>", "<|bos|>", "<|eos|>"]

    def __init__(self):
        self.vocab: Dict[int, str] = {}
        self.inv_vocab: Dict[str, int] = {}
        self.merges: List[Tuple[str, str]] = []
        self._init_base_vocab()

    def _init_base_vocab(self) -> None:
        self.vocab = {}
        self.inv_vocab = {}
        for idx, sp in enumerate(self.SPECIAL_TOKENS):
            self.vocab[idx] = sp
            self.inv_vocab[sp] = idx

        # Add single-character base vocabulary (ASCII printable range)
        curr_idx = len(self.SPECIAL_TOKENS)
        for i in range(32, 127):
            ch = chr(i)
            self.vocab[curr_idx] = ch
            self.inv_vocab[ch] = curr_idx
            curr_idx += 1

    @property
    def vocab_size(self) -> int:
        return len(self.vocab)

    @property
    def pad_token_id(self) -> int:
        return self.inv_vocab["<|pad|>"]

    @property
    def unk_token_id(self) -> int:
        return self.inv_vocab["<|unk|>"]

    @property
    def bos_token_id(self) -> int:
        return self.inv_vocab["<|bos|>"]

    @property
    def eos_token_id(self) -> int:
        return self.inv_vocab["<|eos|>"]

    def _get_stats(self, corpus_words: Dict[Tuple[str, ...], int]) -> Dict[Tuple[str, str], int]:
        pairs = defaultdict(int)
        for word, freq in corpus_words.items():
            for i in range(len(word) - 1):
                pairs[(word[i], word[i + 1])] += freq
        return pairs

    def _merge_vocab(self, pair: Tuple[str, str], corpus_words: Dict[Tuple[str, ...], int]) -> Dict[Tuple[str, ...], int]:
        bigram = pair
        new_words = {}
        for word, freq in corpus_words.items():
            new_word = []
            i = 0
            while i < len(word):
                if i < len(word) - 1 and word[i] == bigram[0] and word[i + 1] == bigram[1]:
                    new_word.append(bigram[0] + bigram[1])
                    i += 2
                else:
                    new_word.append(word[i])
                    i += 1
            new_words[tuple(new_word)] = freq
        return new_words

    def train(self, texts: List[str], target_vocab_size: int = 256) -> None:
        """Learns BPE subword merges from raw text corpus."""
        corpus_words = defaultdict(int)
        for text in texts:
            words = text.strip().split()
            for w in words:
                # Add word boundary suffix
                chars = tuple(list(w) + ["</w>"])
                corpus_words[chars] += 1

        # Add </w> to vocab if not present
        if "</w>" not in self.inv_vocab:
            idx = len(self.vocab)
            self.vocab[idx] = "</w>"
            self.inv_vocab["</w>"] = idx

        self.merges = []
        num_merges = target_vocab_size - len(self.vocab)

        for _ in range(max(0, num_merges)):
            pairs = self._get_stats(corpus_words)
            if not pairs:
                break
            best_pair = max(pairs, key=pairs.get)
            corpus_words = self._merge_vocab(best_pair, corpus_words)
            self.merges.append(best_pair)
            
            merged_token = best_pair[0] + best_pair[1]
            if merged_token not in self.inv_vocab:
                idx = len(self.vocab)
                self.vocab[idx] = merged_token
                self.inv_vocab[merged_token] = idx

    def encode(self, text: str, add_special_tokens: bool = False) -> List[int]:
        tokens: List[int] = []
        if add_special_tokens:
            tokens.append(self.bos_token_id)

        words = text.strip().split()
        for w in words:
            subwords = list(w) + ["</w>"]
            for pair in self.merges:
                bigram = pair
                new_sub = []
                i = 0
                while i < len(subwords):
                    if i < len(subwords) - 1 and subwords[i] == bigram[0] and subwords[i + 1] == bigram[1]:
                        new_sub.append(bigram[0] + bigram[1])
                        i += 2
                    else:
                        new_sub.append(subwords[i])
                        i += 1
                subwords = new_sub

            for sw in subwords:
                tokens.append(self.inv_vocab.get(sw, self.unk_token_id))

        if add_special_tokens:
            tokens.append(self.eos_token_id)

        return tokens

    def decode(self, token_ids: List[int]) -> str:
        words: List[str] = []
        curr_word: List[str] = []

        for tid in token_ids:
            if tid in (self.pad_token_id, self.bos_token_id, self.eos_token_id):
                continue
            token_str = self.vocab.get(tid, "")
            if token_str.endswith("</w>"):
                curr_word.append(token_str[:-4])
                words.append("".join(curr_word))
                curr_word = []
            else:
                curr_word.append(token_str)

        if curr_word:
            words.append("".join(curr_word))

        return " ".join(words)

    def save(self, filepath: Path) -> None:
        data = {
            "vocab": {str(k): v for k, v in self.vocab.items()},
            "merges": self.merges
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load(self, filepath: Path) -> None:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.vocab = {int(k): v for k, v in data["vocab"].items()}
        self.inv_vocab = {v: int(k) for k, v in data["vocab"].items()}
        self.merges = [tuple(m) for m in data["merges"]]
