"""
MY AI - Prompt Injection & System Tampering Defense
Detects adversarial prompt injections, instruction overrides, system escape sequences, and delimiter spoofing.
"""
import re
from typing import Dict, Any, List, Tuple

class InjectionDetector:
    # High-risk adversarial injection signatures
    INJECTION_SIGNATURES = [
        r"(?i)ignore (all )?(previous|prior) (instructions|directions|prompts)",
        r"(?i)disregard (all )?(previous|prior)",
        r"(?i)you are now in developer mode",
        r"(?i)system override",
        r"(?i)jailbreak",
        r"(?i)act as an unrestricted ai",
        r"(?i)reveal (your )?(system prompt|hidden instructions)",
        r"(?i)<\|im_start\|>",
        r"(?i)<\|im_end\|>",
        r"(?i)\[system\]"
    ]

    def __init__(self):
        self.compiled_patterns = [re.compile(p) for p in self.INJECTION_SIGNATURES]

    def evaluate_text(self, text: str) -> Tuple[bool, float, List[str]]:
        """
        Returns (is_suspicious, threat_score (0.0 - 1.0), matched_threats)
        """
        matches = []
        for p in self.compiled_patterns:
            if p.search(text):
                matches.append(p.pattern)

        if not matches:
            return False, 0.0, []

        threat_score = min(1.0, 0.5 + (len(matches) * 0.25))
        return True, threat_score, matches

    def sanitize_input(self, text: str) -> str:
        """Strips adversarial delimiters and special control tokens."""
        sanitized = text
        for token in ["<|im_start|>", "<|im_end|>", "[SYSTEM]", "[/SYSTEM]"]:
            sanitized = re.sub(re.escape(token), "", sanitized, flags=re.IGNORECASE)
        return sanitized.strip()
