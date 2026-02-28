#!/usr/bin/env python3
"""
Panda Brain — Vision Module

Specialized neural network for visual feature processing.
Works with image metadata (dimensions, color channels, file type)
to classify images and extract high-level features.

Capabilities:
  - Image type classification (screenshot, photo, document, meme, etc.)
  - Content category prediction (tech, nature, text, UI, face)
  - Quality assessment (resolution, aspect ratio scoring)

Usage:
    from brain_vision import VisionBrain
    vb = VisionBrain()
    vb.load()
    result = vb.analyze_image_meta(width=1920, height=1080, channels=3, ext=".png", size_kb=450)

No heavy vision dependencies — uses metadata-based heuristics + a small
feedforward net for classification. For actual pixel analysis, pair with
the vision-core skill's OCR/captioning tools.
"""

import json
import math
import random
from pathlib import Path

# Reuse core math utils
import sys
sys.path.insert(0, str(Path(__file__).parent))
from brain_core import relu, softmax, xavier_init, zeros, PandaBrain

DATA_DIR = Path(__file__).parent.parent / "data"
VISION_WEIGHTS_FILE = DATA_DIR / "vision_weights.json"

# ─── Image Type Labels ──────────────────────────────────

IMAGE_TYPES = ["screenshot", "photo", "document", "meme", "icon", "diagram", "unknown"]
CONTENT_CATEGORIES = ["tech", "nature", "text", "ui", "face", "general"]
QUALITY_LEVELS = ["low", "medium", "high"]

# ─── Feature Extraction ─────────────────────────────────

KNOWN_EXTENSIONS = {
    ".png": 0, ".jpg": 1, ".jpeg": 1, ".gif": 2, ".webp": 3,
    ".bmp": 4, ".svg": 5, ".tiff": 6, ".ico": 7, ".heic": 8,
}

COMMON_RESOLUTIONS = {
    (1920, 1080): "fhd",
    (2560, 1440): "qhd",
    (3840, 2160): "4k",
    (1280, 720): "hd",
    (800, 600): "svga",
    (1366, 768): "laptop",
    (375, 812): "iphone",
    (1170, 2532): "iphone_retina",
    (1440, 3200): "android_qhd",
}


def extract_features(width, height, channels=3, ext=".png", size_kb=100):
    """
    Extract a feature vector from image metadata.

    Features (12-dimensional):
      [0] width (normalized to 0-1 by /4000)
      [1] height (normalized)
      [2] aspect ratio
      [3] total pixels (normalized, log scale)
      [4] channels (1=gray, 3=rgb, 4=rgba)
      [5] file extension index
      [6] file size (normalized, log scale)
      [7] is_landscape (0 or 1)
      [8] is_square-ish (0 or 1)
      [9] is_common_resolution (0 or 1)
      [10] is_retina/hidpi (0 or 1)
      [11] is_mobile_aspect (0 or 1)
    """
    features = zeros(12)

    features[0] = min(width / 4000.0, 1.0)
    features[1] = min(height / 4000.0, 1.0)
    features[2] = (width / max(height, 1)) if height > 0 else 1.0
    features[3] = math.log1p(width * height) / 20.0  # normalize log of megapixels
    features[4] = channels / 4.0
    features[5] = KNOWN_EXTENSIONS.get(ext.lower(), 8) / 8.0
    features[6] = math.log1p(size_kb) / 15.0
    features[7] = 1.0 if width > height else 0.0
    features[8] = 1.0 if 0.9 <= (width / max(height, 1)) <= 1.1 else 0.0
    features[9] = 1.0 if (width, height) in COMMON_RESOLUTIONS else 0.0
    features[10] = 1.0 if width >= 2560 or height >= 2560 else 0.0
    features[11] = 1.0 if (height / max(width, 1)) >= 1.8 else 0.0  # tall = mobile

    return features


# ─── Vision Neural Network ──────────────────────────────

class VisionBrain:
    """
    Small feedforward network for image metadata classification.

    Architecture: 12 → 8 → {image_type(7), content(6), quality(3)}
    """

    INPUT_SIZE = 12
    HIDDEN_SIZE = 8

    def __init__(self):
        self.w1 = xavier_init(self.INPUT_SIZE, self.HIDDEN_SIZE)
        self.b1 = zeros(self.HIDDEN_SIZE)

        self.heads = {
            "image_type": {
                "w": xavier_init(self.HIDDEN_SIZE, len(IMAGE_TYPES)),
                "b": zeros(len(IMAGE_TYPES)),
            },
            "content": {
                "w": xavier_init(self.HIDDEN_SIZE, len(CONTENT_CATEGORIES)),
                "b": zeros(len(CONTENT_CATEGORIES)),
            },
            "quality": {
                "w": xavier_init(self.HIDDEN_SIZE, len(QUALITY_LEVELS)),
                "b": zeros(len(QUALITY_LEVELS)),
            },
        }

    def forward(self, features):
        """Forward pass through the vision network."""
        # Hidden layer
        h = zeros(self.HIDDEN_SIZE)
        for j in range(self.HIDDEN_SIZE):
            s = self.b1[j]
            for i in range(self.INPUT_SIZE):
                s += features[i] * self.w1[i][j]
            h[j] = relu(s)

        # Output heads
        outputs = {}
        for head_name, head in self.heads.items():
            w, b = head["w"], head["b"]
            head_size = len(b)
            logits = zeros(head_size)
            for j in range(head_size):
                s = b[j]
                for i in range(self.HIDDEN_SIZE):
                    s += h[i] * w[i][j]
                logits[j] = s
            outputs[head_name] = softmax(logits)

        return outputs

    def analyze_image_meta(self, width, height, channels=3, ext=".png", size_kb=100):
        """
        Analyze an image by its metadata.

        Returns dict with image_type, content category, and quality predictions.
        """
        features = extract_features(width, height, channels, ext, size_kb)
        outputs = self.forward(features)

        # Also apply heuristic rules to boost accuracy
        result = {}

        # Image type
        type_labels = IMAGE_TYPES
        type_probs = outputs["image_type"]
        type_idx = type_probs.index(max(type_probs))

        # Heuristic overrides
        if (width, height) in COMMON_RESOLUTIONS:
            res = COMMON_RESOLUTIONS[(width, height)]
            if res in ("fhd", "qhd", "4k", "laptop"):
                type_idx = type_labels.index("screenshot")
            elif res in ("iphone", "iphone_retina", "android_qhd"):
                type_idx = type_labels.index("photo")

        if ext.lower() == ".ico":
            type_idx = type_labels.index("icon")
        elif ext.lower() == ".svg":
            type_idx = type_labels.index("diagram")

        result["image_type"] = {
            "label": type_labels[type_idx],
            "confidence": round(type_probs[type_idx], 4),
        }

        # Content category
        cat_labels = CONTENT_CATEGORIES
        cat_probs = outputs["content"]
        cat_idx = cat_probs.index(max(cat_probs))
        result["content"] = {
            "label": cat_labels[cat_idx],
            "confidence": round(cat_probs[cat_idx], 4),
        }

        # Quality
        q_labels = QUALITY_LEVELS
        total_pixels = width * height
        if total_pixels >= 2073600:  # >= 1080p
            quality = "high"
        elif total_pixels >= 307200:  # >= 640x480
            quality = "medium"
        else:
            quality = "low"

        result["quality"] = {
            "label": quality,
            "resolution": f"{width}x{height}",
            "megapixels": round(total_pixels / 1_000_000, 2),
        }

        result["features"] = {
            "aspect_ratio": round(width / max(height, 1), 2),
            "is_landscape": width > height,
            "is_mobile": (height / max(width, 1)) >= 1.8,
            "is_retina": width >= 2560 or height >= 2560,
            "extension": ext,
            "size_kb": size_kb,
        }

        return result

    def save(self):
        """Save vision weights."""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        weights = {
            "w1": self.w1, "b1": self.b1,
            "heads": {n: {"w": h["w"], "b": h["b"]} for n, h in self.heads.items()},
        }
        VISION_WEIGHTS_FILE.write_text(json.dumps(weights), encoding="utf-8")

    def load(self):
        """Load vision weights if available."""
        if not VISION_WEIGHTS_FILE.exists():
            return False
        data = json.loads(VISION_WEIGHTS_FILE.read_text(encoding="utf-8"))
        self.w1 = data["w1"]
        self.b1 = data["b1"]
        for name in self.heads:
            if name in data.get("heads", {}):
                self.heads[name]["w"] = data["heads"][name]["w"]
                self.heads[name]["b"] = data["heads"][name]["b"]
        return True


# ─── CLI ─────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Analyze image metadata with Panda Brain Vision.")
    parser.add_argument("--width", "-W", type=int, required=True, help="Image width in pixels")
    parser.add_argument("--height", "-H", type=int, required=True, help="Image height in pixels")
    parser.add_argument("--channels", "-c", type=int, default=3, help="Color channels (1=gray, 3=rgb, 4=rgba)")
    parser.add_argument("--ext", "-e", default=".png", help="File extension")
    parser.add_argument("--size", "-s", type=float, default=100, help="File size in KB")
    args = parser.parse_args()

    vb = VisionBrain()
    vb.load()

    result = vb.analyze_image_meta(args.width, args.height, args.channels, args.ext, args.size)
    print(json.dumps(result, indent=2))
