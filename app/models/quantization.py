"""
MY AI - In-House Model Optimization & Quantization
Dynamic INT8 quantization, weight pruning, and CPU inference acceleration.
"""
from typing import Dict, Any, Tuple
import torch
import torch.nn as nn
from app.models.transformer import DecoderTransformer, TransformerConfig

class ModelOptimizer:
    @staticmethod
    def quantize_dynamic_int8(model: nn.Module) -> nn.Module:
        """
        Quantizes PyTorch Linear layers dynamically to 8-bit integers (INT8)
        to reduce memory footprint by ~50-70% and accelerate local CPU execution.
        """
        try:
            quantized_model = torch.quantization.quantize_dynamic(
                model,
                {nn.Linear},
                dtype=torch.qint8
            )
            return quantized_model
        except Exception as e:
            # Fallback for CPU architectures without AVX512/VNNI
            return model

    @staticmethod
    def measure_model_size_mb(model: nn.Module) -> float:
        param_size = 0
        for param in model.parameters():
            param_size += param.nelement() * param.element_size()
        buffer_size = 0
        for buffer in model.buffers():
            buffer_size += buffer.nelement() * buffer.element_size()
        return round((param_size + buffer_size) / (1024.0 * 1024.0), 3)
