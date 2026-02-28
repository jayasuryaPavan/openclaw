---
name: vision-core
description: Visual recognition and image processing for Panda Chat. Use when the user wants to analyze images, screenshots, or requires object detection capabilities.
---

# Vision Core

## Overview

Vision Core enables Panda Chat to "see" and interpret visual data. It works with screenshots and uploaded images to extract text (OCR) and identify objects.

## Capabilities

### 1. Image Classification
Identifies the primary content of an image.
- **Trigger**: "What is this image?", "Describe the screen".
- **Tool**: `scripts/analyze_image.py`.

### 2. OCR (Optical Character Recognition)
Extracts text from images or screenshots.
- **Trigger**: "Read the text on the screen", "What does this document say?".
- **Tool**: `scripts/ocr_helper.py`.

## Workflow

1. **Capture**: Use `desktop/screenshot.py` or receive an image from the user.
2. **Analysis**: Use `scripts/analyze_image.py` for high-level description or `scripts/ocr_helper.py` for text.
3. **Brain Update**: Pass visual insights to the brain core if learning is required.

## Resources

### scripts/
- `analyze_image.py`: Visual content analysis.
- `ocr_helper.py`: Text extraction utility.

### references/
- `vision_models.md`: List of supported vision models and their strengths.
