"""
MY AI - Emotion States & Dimensional Sentiment Model
Circumplex Model of Affect (Valence & Arousal) and Discrete Emotion States.
"""
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional

class EmotionType(str, Enum):
    NEUTRAL = "NEUTRAL"
    HAPPY = "HAPPY"
    SAD = "SAD"
    ANGRY = "ANGRY"
    STRESSED = "STRESSED"
    TIRED = "TIRED"
    EXCITED = "EXCITED"

class ConversationMode(str, Enum):
    CASUAL = "CASUAL"
    FOCUSED_WORK = "FOCUSED_WORK"
    VENTING = "VENTING"
    CRISIS_SUPPORT = "CRISIS_SUPPORT"

@dataclass
class EmotionalState:
    primary_emotion: EmotionType
    confidence: float
    valence: float   # -1.0 (unpleasant) to +1.0 (pleasant)
    arousal: float   # 0.0 (calm/passive) to +1.0 (highly activated/intense)
    conversation_mode: ConversationMode = ConversationMode.CASUAL

    def to_dict(self) -> Dict[str, Any]:
        return {
            "primary_emotion": self.primary_emotion.value,
            "confidence": self.confidence,
            "valence": round(self.valence, 2),
            "arousal": round(self.arousal, 2),
            "conversation_mode": self.conversation_mode.value
        }
