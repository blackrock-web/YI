"""
MY AI - In-House Neural Intent Classifier
PyTorch Feed-Forward Deep Learning Network with Subword Embeddings.
Built from scratch without external inference SDKs.
"""
import torch
import torch.nn as nn
import torch.optim as optim
from typing import List, Dict, Tuple, Optional
from app.models.tokenizer import BPETokenizer
from app.brain.intents import Intent

class IntentClassifierNN(nn.Module):
    def __init__(self, vocab_size: int, embed_dim: int = 64, hidden_dim: int = 128, num_classes: int = 20):
        super().__init__()
        self.embedding = nn.EmbeddingBag(vocab_size, embed_dim, mode="mean")
        self.fc1 = nn.Linear(embed_dim, hidden_dim)
        self.relu = nn.ReLU()
        self.norm = nn.LayerNorm(hidden_dim)
        self.dropout = nn.Dropout(0.2)
        self.fc2 = nn.Linear(hidden_dim, num_classes)
        self.log_softmax = nn.LogSoftmax(dim=1)

    def forward(self, text_tokens: torch.Tensor, offsets: torch.Tensor) -> torch.Tensor:
        embedded = self.embedding(text_tokens, offsets)
        x = self.fc1(embedded)
        x = self.norm(x)
        x = self.relu(x)
        x = self.dropout(x)
        logits = self.fc2(x)
        return self.log_softmax(logits)

class IntentModelManager:
    INTENT_LABELS = [
        Intent.GREETING,
        Intent.GOODBYE,
        Intent.ASK_NAME,
        Intent.ASK_TIME,
        Intent.ASK_DATE,
        Intent.ASK_CAPABILITIES,
        Intent.CREATE_TASK,
        Intent.SHOW_TASKS,
        Intent.COMPLETE_TASK,
        Intent.CREATE_REMINDER,
        Intent.SHOW_SCHEDULE,
        Intent.REMEMBER,
        Intent.SEARCH_MEMORY,
        Intent.USER_HAPPY,
        Intent.USER_SAD,
        Intent.USER_STRESSED,
        Intent.OPEN_APPLICATION,
        Intent.CLOSE_APPLICATION
    ]

    def __init__(self, tokenizer: Optional[BPETokenizer] = None):
        self.tokenizer = tokenizer or BPETokenizer()
        self.label_to_idx = {intent: i for i, intent in enumerate(self.INTENT_LABELS)}
        self.idx_to_label = {i: intent for i, intent in enumerate(self.INTENT_LABELS)}
        self.model = IntentClassifierNN(
            vocab_size=max(256, self.tokenizer.vocab_size + 50),
            embed_dim=48,
            hidden_dim=64,
            num_classes=len(self.INTENT_LABELS)
        )

    def train_on_corpus(self, training_data: List[Tuple[str, Intent]], epochs: int = 15) -> float:
        """Trains neural intent classifier on local paired examples."""
        self.model.train()
        optimizer = optim.AdamW(self.model.parameters(), lr=0.01, weight_decay=1e-4)
        criterion = nn.NLLLoss()

        total_loss = 0.0
        for _ in range(epochs):
            total_loss = 0.0
            for text, intent in training_data:
                if intent not in self.label_to_idx:
                    continue
                label_idx = self.label_to_idx[intent]
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

    def predict(self, text: str) -> Tuple[Intent, float]:
        self.model.eval()
        tokens = self.tokenizer.encode(text)
        if not tokens:
            return Intent.UNKNOWN, 0.0

        token_tensor = torch.tensor(tokens, dtype=torch.long)
        offset_tensor = torch.tensor([0], dtype=torch.long)

        with torch.no_grad():
            log_probs = self.model(token_tensor, offset_tensor)
            probs = torch.exp(log_probs)
            top_prob, top_idx = torch.max(probs, dim=1)
            
            idx = top_idx.item()
            confidence = float(top_prob.item())
            intent = self.idx_to_label.get(idx, Intent.UNKNOWN)
            return intent, confidence
