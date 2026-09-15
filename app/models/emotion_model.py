"""
MY AI - In-House Neural Emotion Classifier
PyTorch Neural Network for affect & sentiment recognition from subword tokens.
"""
import torch
import torch.nn as nn
import torch.optim as optim
from typing import List, Dict, Tuple, Optional
from app.models.tokenizer import BPETokenizer
from app.emotion.states import EmotionType

class EmotionClassifierNN(nn.Module):
    def __init__(self, vocab_size: int, embed_dim: int = 48, hidden_dim: int = 64, num_emotions: int = 7):
        super().__init__()
        self.embedding = nn.EmbeddingBag(vocab_size, embed_dim, mode="mean")
        self.fc1 = nn.Linear(embed_dim, hidden_dim)
        self.relu = nn.ReLU()
        self.norm = nn.LayerNorm(hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, num_emotions)
        self.log_softmax = nn.LogSoftmax(dim=1)

    def forward(self, text_tokens: torch.Tensor, offsets: torch.Tensor) -> torch.Tensor:
        embedded = self.embedding(text_tokens, offsets)
        x = self.fc1(embedded)
        x = self.norm(x)
        x = self.relu(x)
        logits = self.fc2(x)
        return self.log_softmax(logits)

class EmotionModelManager:
    EMOTION_LABELS = [
        EmotionType.NEUTRAL,
        EmotionType.HAPPY,
        EmotionType.SAD,
        EmotionType.ANGRY,
        EmotionType.STRESSED,
        EmotionType.TIRED,
        EmotionType.EXCITED
    ]

    def __init__(self, tokenizer: Optional[BPETokenizer] = None):
        self.tokenizer = tokenizer or BPETokenizer()
        self.label_to_idx = {em: i for i, em in enumerate(self.EMOTION_LABELS)}
        self.idx_to_label = {i: em for i, em in enumerate(self.EMOTION_LABELS)}
        self.model = EmotionClassifierNN(
            vocab_size=max(256, self.tokenizer.vocab_size + 50),
            embed_dim=48,
            hidden_dim=64,
            num_emotions=len(self.EMOTION_LABELS)
        )

    def train_on_corpus(self, training_data: List[Tuple[str, EmotionType]], epochs: int = 15) -> float:
        self.model.train()
        optimizer = optim.AdamW(self.model.parameters(), lr=0.01, weight_decay=1e-4)
        criterion = nn.NLLLoss()

        total_loss = 0.0
        for _ in range(epochs):
            total_loss = 0.0
            for text, emotion in training_data:
                if emotion not in self.label_to_idx:
                    continue
                label_idx = self.label_to_idx[emotion]
                tokens = self.tokenizer.encode(text)
                if not tokens:
                    tokens = [self.tokenizer.unk_token_id]

                token_tensor = torch.tensor(tokens, dtype=torch.long)
                offset_tensor = torch.tensor([0], dtype=torch.long)
                target_tensor = torch.tensor([label_idx], dtype=torch.long)

                optimizer.zero_grad()
                output = self.model(token_tensor, offset_tensor)
                loss = criterion(output, target_tensor)
                loss.backward()
                optimizer.step()
                total_loss += loss.item()

        return total_loss / max(1, len(training_data))

    def predict(self, text: str) -> Tuple[EmotionType, float]:
        self.model.eval()
        tokens = self.tokenizer.encode(text)
        if not tokens:
            return EmotionType.NEUTRAL, 0.0

        token_tensor = torch.tensor(tokens, dtype=torch.long)
        offset_tensor = torch.tensor([0], dtype=torch.long)

        with torch.no_grad():
            log_probs = self.model(token_tensor, offset_tensor)
            probs = torch.exp(log_probs)
            top_prob, top_idx = torch.max(probs, dim=1)
            
            idx = top_idx.item()
            confidence = float(top_prob.item())
            emotion = self.idx_to_label.get(idx, EmotionType.NEUTRAL)
            return emotion, confidence
