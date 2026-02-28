#!/usr/bin/env python3
"""
Vision Core - OCR Text Extraction for Panda Chat

Extracts text from images and screenshots. Currently uses a mock engine.
In production, integrate with Tesseract, Google Cloud Vision, or OpenAI Vision.

Usage:
    python ocr_helper.py <image_file>
    python ocr_helper.py <image_file> --raw

Model: Panda-OCR-v1 (Mock — rule-based for dev/testing)
"""

import argparse
import json
import os
import sys
from pathlib import Path


SUPPORTED_FORMATS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp", ".gif", ".heic"}


def mock_ocr(image_path):
    """
    Mock OCR engine.

    In production, replace with:
        import pytesseract
        from PIL import Image
        text = pytesseract.image_to_string(Image.open(image_path))
        return text, "tesseract", 0.9
    """
    filename = os.path.basename(image_path).lower()
    ext = os.path.splitext(filename)[1]

    if "screenshot" in filename or "screen" in filename:
        text = "VS Code - brain_core.py\nFile  Edit  Selection  View  Go  Run  Terminal  Help\ndef train(self, data):\n    # Training logic here"
        engine = "screen-detect"
        confidence = 0.85
    elif "document" in filename or "doc" in filename:
        text = "INVOICE #12345\nDate: 2026-02-23\nAmount: $150.00\nStatus: Paid"
        engine = "doc-scan"
        confidence = 0.92
    elif "chat" in filename or "message" in filename:
        text = "Pandu: em undi bro\nSadist: Bagundi pandu! Cheppu em kavali?"
        engine = "chat-detect"
        confidence = 0.88
    else:
        text = "Sample text extracted from image. [Mock OCR]"
        engine = "generic"
        confidence = 0.75

    return text, engine, confidence


def extract_text(image_path, raw=False):
    """Extract text from an image file."""
    if not os.path.exists(image_path):
        return {"error": f"File not found: {image_path}"}

    ext = os.path.splitext(image_path)[1].lower()
    if ext not in SUPPORTED_FORMATS:
        return {"error": f"Unsupported format '{ext}'. Supported: {', '.join(sorted(SUPPORTED_FORMATS))}"}

    text, engine, confidence = mock_ocr(image_path)

    if raw:
        return {"text": text}

    lines = [l for l in text.split("\n") if l.strip()]
    return {
        "file": image_path,
        "text": text,
        "lines": lines,
        "line_count": len(lines),
        "char_count": len(text),
        "confidence": round(confidence, 2),
        "engine": engine,
        "model": "Panda-OCR-v1 (Mock)",
    }


def main():
    parser = argparse.ArgumentParser(description="Extract text from images.")
    parser.add_argument("image_file", help="Path to the image file")
    parser.add_argument("--raw", action="store_true", help="Output raw text only")
    args = parser.parse_args()

    result = extract_text(args.image_file, raw=args.raw)

    if args.raw and "text" in result:
        print(result["text"])
    else:
        print(json.dumps(result, indent=2))
        if "error" in result:
            sys.exit(1)


if __name__ == "__main__":
    main()
