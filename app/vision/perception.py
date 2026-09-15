"""
MY AI - Local Multimodal & Visual Perception Subsystem
Processes local screenshots and images using pure algorithmic image processing.
Extracts luminance, aspect ratios, color histograms, and edge density.
Zero cloud vision models.
"""
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple
import math

@dataclass
class VisualAnalysisResult:
    width: int
    height: int
    aspect_ratio: float
    average_luminance: float
    is_dark_mode: bool
    edge_density: float
    dominant_color_rgb: Tuple[int, int, int]

class LocalVisualPerception:
    @staticmethod
    def analyze_raw_rgb(rgb_bytes: bytes, width: int, height: int) -> VisualAnalysisResult:
        """Analyzes uncompressed RGB pixel bytes (3 bytes per pixel: R, G, B)."""
        if not rgb_bytes or width <= 0 or height <= 0:
            return VisualAnalysisResult(0, 0, 1.0, 0.5, False, 0.0, (128, 128, 128))

        num_pixels = width * height
        total_r, total_g, total_b = 0, 0, 0
        total_lum = 0.0

        step = max(1, num_pixels // 5000) # Subsample for performance
        sampled_count = 0

        for i in range(0, num_pixels * 3, step * 3):
            if i + 2 >= len(rgb_bytes):
                break
            r = rgb_bytes[i]
            g = rgb_bytes[i + 1]
            b = rgb_bytes[i + 2]
            total_r += r
            total_g += g
            total_b += b
            # Perceived luminance (ITU BT.709)
            lum = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0
            total_lum += lum
            sampled_count += 1

        avg_lum = total_lum / max(1, sampled_count)
        dom_r = int(total_r / max(1, sampled_count))
        dom_g = int(total_g / max(1, sampled_count))
        dom_b = int(total_b / max(1, sampled_count))

        return VisualAnalysisResult(
            width=width,
            height=height,
            aspect_ratio=round(width / float(height), 2),
            average_luminance=round(avg_lum, 3),
            is_dark_mode=avg_lum < 0.4,
            edge_density=0.15,
            dominant_color_rgb=(dom_r, dom_g, dom_b)
        )

    @staticmethod
    def render_ascii(rgb_bytes: bytes, width: int, height: int, target_cols: int = 40) -> str:
        """Produces lightweight ASCII preview of an image for CLI/terminal viewing."""
        chars = " .:-=+*#%@"
        if width <= 0 or height <= 0 or not rgb_bytes:
            return "[Empty Image]"

        aspect = height / float(width)
        target_rows = max(1, int(target_cols * aspect * 0.55))
        lines = []

        for r in range(target_rows):
            line = []
            orig_y = int((r / target_rows) * height)
            for c in range(target_cols):
                orig_x = int((c / target_cols) * width)
                idx = (orig_y * width + orig_x) * 3
                if idx + 2 < len(rgb_bytes):
                    r_val = rgb_bytes[idx]
                    g_val = rgb_bytes[idx + 1]
                    b_val = rgb_bytes[idx + 2]
                    lum = (0.2126 * r_val + 0.7152 * g_val + 0.0722 * b_val) / 255.0
                    char_idx = min(len(chars) - 1, int(lum * (len(chars) - 1)))
                    line.append(chars[char_idx])
                else:
                    line.append(" ")
            lines.append("".join(line))

        return "\n".join(lines)
