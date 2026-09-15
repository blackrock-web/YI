"""
MY AI - Local Training & Fine-Tuning Engine
Trains the custom Decoder Transformer and neural classifiers locally with PyTorch.
Features AdamW optimizer, loss monitoring, checkpoint saving and loading.
Zero cloud compute required.
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
import torch
import torch.optim as optim
from app.models.transformer import DecoderTransformer, TransformerConfig
from app.models.tokenizer import BPETokenizer
from app.logging_config import logger

class ModelTrainer:
    def __init__(self, model: DecoderTransformer, tokenizer: BPETokenizer):
        self.model = model
        self.tokenizer = tokenizer

    def train_epoch(self, token_batches: List[torch.Tensor], lr: float = 3e-4) -> float:
        """Runs one training epoch over token sequences with AdamW optimizer."""
        self.model.train()
        optimizer = optim.AdamW(self.model.parameters(), lr=lr, weight_decay=1e-2)
        total_loss = 0.0

        for batch in token_batches:
            if batch.size(1) < 2:
                continue
            inputs = batch[:, :-1]
            targets = batch[:, 1:]

            optimizer.zero_grad()
            _, loss = self.model(inputs, targets=targets)
            if loss is not None:
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                optimizer.step()
                total_loss += loss.item()

        return total_loss / max(1, len(token_batches))

    def save_checkpoint(self, filepath: Path) -> None:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        torch.save({
            "config": {
                "vocab_size": self.model.config.vocab_size,
                "block_size": self.model.config.block_size,
                "n_layer": self.model.config.n_layer,
                "n_head": self.model.config.n_head,
                "n_embd": self.model.config.n_embd,
                "dropout": self.model.config.dropout,
                "bias": self.model.config.bias
            },
            "state_dict": self.model.state_dict()
        }, str(filepath))

    @staticmethod
    def load_checkpoint(filepath: Path) -> DecoderTransformer:
        try:
            checkpoint = torch.load(str(filepath), map_location="cpu", weights_only=False)
        except TypeError:
            checkpoint = torch.load(str(filepath), map_location="cpu")
        cfg_dict = checkpoint["config"]
        config = TransformerConfig(**cfg_dict) if isinstance(cfg_dict, dict) else cfg_dict
        model = DecoderTransformer(config)
        model.load_state_dict(checkpoint["state_dict"])
        return model
