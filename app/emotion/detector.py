"""
MY AI - Deterministic Emotion & Tone Detector
Rule-based affect analysis with valence-arousal mapping and context tracking.
"""
from typing import Dict, Any, List, Optional
import re
from app.emotion.states import EmotionType, EmotionalState, ConversationMode
from app.brain.parser import TextParser

class EmotionDetector:
    # Affect dictionary mapping tokens to (Emotion, base_valence, base_arousal)
    EMOTION_LEXICON = {
        # Happy / Joy
        "happy": (EmotionType.HAPPY, 0.8, 0.6),
        "glad": (EmotionType.HAPPY, 0.6, 0.4),
        "joyful": (EmotionType.HAPPY, 0.9, 0.7),
        "great": (EmotionType.HAPPY, 0.7, 0.5),
        "wonderful": (EmotionType.HAPPY, 0.9, 0.6),
        "awesome": (EmotionType.HAPPY, 0.8, 0.7),
        "love": (EmotionType.HAPPY, 0.85, 0.6),

        # Sad
        "sad": (EmotionType.SAD, -0.8, 0.3),
        "down": (EmotionType.SAD, -0.6, 0.2),
        "depressed": (EmotionType.SAD, -0.9, 0.2),
        "unhappy": (EmotionType.SAD, -0.7, 0.3),
        "heartbroken": (EmotionType.SAD, -0.95, 0.5),
        "terrible": (EmotionType.SAD, -0.8, 0.5),

        # Angry
        "angry": (EmotionType.ANGRY, -0.8, 0.8),
        "furious": (EmotionType.ANGRY, -0.9, 0.95),
        "mad": (EmotionType.ANGRY, -0.7, 0.75),
        "pissed": (EmotionType.ANGRY, -0.8, 0.85),
        "annoyed": (EmotionType.ANGRY, -0.5, 0.5),
        "hate": (EmotionType.ANGRY, -0.85, 0.8),

        # Stressed
        "stressed": (EmotionType.STRESSED, -0.7, 0.8),
        "overwhelmed": (EmotionType.STRESSED, -0.8, 0.85),
        "anxious": (EmotionType.STRESSED, -0.75, 0.75),
        "pressure": (EmotionType.STRESSED, -0.6, 0.7),

        # Tired
        "tired": (EmotionType.TIRED, -0.3, 0.1),
        "exhausted": (EmotionType.TIRED, -0.5, 0.1),
        "sleepy": (EmotionType.TIRED, -0.2, 0.05),
        "drained": (EmotionType.TIRED, -0.6, 0.1),

        # Excited
        "excited": (EmotionType.EXCITED, 0.85, 0.9),
        "thrilled": (EmotionType.EXCITED, 0.9, 0.9),
        "hyped": (EmotionType.EXCITED, 0.8, 0.85),
        "pumped": (EmotionType.EXCITED, 0.75, 0.8),
    }

    INTENSIFIERS = {"very": 1.3, "so": 1.25, "extremely": 1.5, "super": 1.3, "really": 1.2}
    NEGATIONS = {"not", "never", "no", "barely", "hardly", "isnt", "arent", "wasnt"}

    def detect(self, text: str) -> EmotionalState:
        normalized = TextParser.normalize(text)
        words = normalized.split()

        if not words:
            return EmotionalState(EmotionType.NEUTRAL, 1.0, 0.0, 0.0, ConversationMode.CASUAL)

        scores: Dict[EmotionType, float] = {e: 0.0 for e in EmotionType}
        total_valence = 0.0
        total_arousal = 0.0
        matches = 0

        for i, w in enumerate(words):
            if w in self.EMOTION_LEXICON:
                em_type, v, a = self.EMOTION_LEXICON[w]
                multiplier = 1.0

                # Check preceding word for intensifier
                if i > 0 and words[i - 1] in self.INTENSIFIERS:
                    multiplier *= self.INTENSIFIERS[words[i - 1]]
                # Check preceding word for negation
                if i > 0 and words[i - 1] in self.NEGATIONS:
                    multiplier *= -0.8

                scores[em_type] += abs(multiplier)
                total_valence += v * multiplier
                total_arousal += a * abs(multiplier)
                matches += 1

        if matches == 0:
            return EmotionalState(EmotionType.NEUTRAL, 0.8, 0.0, 0.1, ConversationMode.CASUAL)

        best_emotion = max(scores.items(), key=lambda x: x[1])[0]
        avg_valence = max(-1.0, min(1.0, total_valence / matches))
        avg_arousal = max(0.0, min(1.0, total_arousal / matches))

        # Infer conversational mode
        mode = ConversationMode.CASUAL
        if best_emotion in (EmotionType.SAD, EmotionType.ANGRY):
            mode = ConversationMode.VENTING
        elif best_emotion == EmotionType.STRESSED:
            mode = ConversationMode.CRISIS_SUPPORT if avg_arousal > 0.8 else ConversationMode.VENTING

        return EmotionalState(
            primary_emotion=best_emotion,
            confidence=min(0.95, 0.6 + matches * 0.15),
            valence=avg_valence,
            arousal=avg_arousal,
            conversation_mode=mode
        )
