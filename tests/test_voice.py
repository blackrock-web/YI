"""
Tests for Phase 8 (Voice Input) & Phase 9 (Voice Output)
Verifies audio feature extraction, speech detection, local TTS waveform synthesis, and WAV formatting.
"""
import unittest
import wave
import io
import struct
from app.voice.listener import VoiceListener
from app.voice.speaker import VoiceSpeaker, VoiceProfile

class TestVoiceSystem(unittest.TestCase):
    def setUp(self):
        self.listener = VoiceListener(sample_rate=16000)
        self.speaker = VoiceSpeaker(profile=VoiceProfile(name="Aura"), sample_rate=16000)

    def test_voice_activity_detection(self):
        # Generate silent buffer
        silence = struct.pack("<1600h", *([0] * 1600))
        silent_feats = self.listener.extract_features(silence)
        self.assertFalse(silent_feats.is_speech)
        self.assertAlmostEqual(silent_feats.rms_energy, 0.0)

        # Generate loud tone
        tone = struct.pack("<1600h", *([15000 if i % 2 == 0 else -15000 for i in range(1600)]))
        tone_feats = self.listener.extract_features(tone)
        self.assertTrue(tone_feats.is_speech)
        self.assertGreater(tone_feats.rms_energy, 0.1)

    def test_speech_synthesis(self):
        text = "Hello, I am MY AI."
        wav_bytes = self.speaker.synthesize_wav(text)
        self.assertGreater(len(wav_bytes), 100)

        # Verify WAV validity by opening with standard python wave module
        with wave.open(io.BytesIO(wav_bytes), "rb") as wav_file:
            self.assertEqual(wav_file.getnchannels(), 1)
            self.assertEqual(wav_file.getsampwidth(), 2)
            self.assertEqual(wav_file.getframerate(), 16000)
            frames = wav_file.getnframes()
            self.assertGreater(frames, 0)

        res = self.speaker.speak(text)
        self.assertEqual(res["status"], "synthesized")
        self.assertEqual(res["voice_name"], "Aura")

if __name__ == "__main__":
    unittest.main()
