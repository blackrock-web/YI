"""
Tests for Phase 15 (In-House ML Models), Phase 16 (Decoder Transformer), and Phase 17 (Local Training)
Verifies custom BPE tokenizer, neural intent classifier, emotion model, and causal transformer LM from scratch.
"""
import unittest
import tempfile
import torch
from pathlib import Path
from app.models.tokenizer import BPETokenizer
from app.models.intent_model import IntentModelManager
from app.models.emotion_model import EmotionModelManager
from app.models.transformer import DecoderTransformer, TransformerConfig
from app.models.training import ModelTrainer
from app.brain.intents import Intent
from app.emotion.states import EmotionType

class TestInHouseMLModels(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.tokenizer = BPETokenizer()
        corpus = [
            "hello my ai assistant",
            "create a new task for tomorrow",
            "what is the current time and date",
            "remember my favorite game is minecraft",
            "i am very happy today",
            "i feel sad and stressed"
        ]
        self.tokenizer.train(corpus, target_vocab_size=160)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_bpe_tokenizer(self):
        text = "hello my ai"
        encoded = self.tokenizer.encode(text)
        self.assertGreater(len(encoded), 0)
        decoded = self.tokenizer.decode(encoded)
        self.assertEqual(decoded.strip(), text.strip())

        # Test save & load
        save_path = Path(self.temp_dir.name) / "tokenizer.json"
        self.tokenizer.save(save_path)
        loaded_tok = BPETokenizer()
        loaded_tok.load(save_path)
        self.assertEqual(loaded_tok.vocab_size, self.tokenizer.vocab_size)

    def test_intent_classifier_nn(self):
        manager = IntentModelManager(self.tokenizer)
        data = [
            ("hello assistant", Intent.GREETING),
            ("hi there", Intent.GREETING),
            ("create a task", Intent.CREATE_TASK),
            ("add new task", Intent.CREATE_TASK),
            ("what time is it", Intent.ASK_TIME),
        ]
        loss = manager.train_on_corpus(data, epochs=12)
        self.assertIsInstance(loss, float)

        # Predict
        intent, conf = manager.predict("hello assistant")
        self.assertEqual(intent, Intent.GREETING)
        self.assertGreater(conf, 0.4)

    def test_emotion_classifier_nn(self):
        manager = EmotionModelManager(self.tokenizer)
        data = [
            ("i am feeling joyful and great", EmotionType.HAPPY),
            ("today was awesome", EmotionType.HAPPY),
            ("i am so sad and heartbroken", EmotionType.SAD),
            ("feeling down", EmotionType.SAD),
        ]
        loss = manager.train_on_corpus(data, epochs=12)
        self.assertIsInstance(loss, float)

        pred_emotion, conf = manager.predict("feeling joyful and great")
        self.assertEqual(pred_emotion, EmotionType.HAPPY)
        self.assertGreater(conf, 0.3)

    def test_decoder_transformer_lm(self):
        config = TransformerConfig(
            vocab_size=self.tokenizer.vocab_size,
            block_size=32,
            n_layer=2,
            n_head=2,
            n_embd=32
        )
        model = DecoderTransformer(config)

        # Test forward pass with input sequence
        batch_tokens = torch.tensor([[self.tokenizer.encode("hello my ai")]], dtype=torch.long)
        if batch_tokens.dim() == 3:
            batch_tokens = batch_tokens.squeeze(0)
            
        logits, loss = model(batch_tokens, targets=batch_tokens)
        self.assertIsNotNone(loss)
        self.assertEqual(logits.shape[-1], config.vocab_size)

        # Test autoregressive generation
        gen_tokens = model.generate(batch_tokens, max_new_tokens=5, temperature=1.0)
        self.assertEqual(gen_tokens.shape[1], batch_tokens.shape[1] + 5)

        # Test checkpoint saving & loading
        trainer = ModelTrainer(model, self.tokenizer)
        ckpt_path = Path(self.temp_dir.name) / "transformer_ckpt.pt"
        trainer.save_checkpoint(ckpt_path)
        self.assertTrue(ckpt_path.exists())

        loaded_model = ModelTrainer.load_checkpoint(ckpt_path)
        self.assertEqual(loaded_model.config.n_layer, 2)
        self.assertEqual(loaded_model.config.n_embd, 32)

if __name__ == "__main__":
    unittest.main()
