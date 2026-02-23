---
name: nlp-core
description: Core Natural Language Processing capabilities for Panda Chat. Use when you need to analyze intent, sentiment, or extract entities from user messages to better understand their needs and adapt the assistant's behavior.
---

# NLP Core

## Overview

The NLP Core skill provides tools and workflows for deep understanding of user communication. It enables the assistant to go beyond simple command execution by analyzing the underlying intent and emotional context of messages.

## Capabilities

### 1. Intent Classification
Identifies what the user wants to achieve, even when phrased informally.
- **Example**: "remind me to buy milk" -> `REMINDER` intent.
- **Example**: "what's the weather like" -> `WEATHER` intent.

### 2. Sentiment & Persona Adaptation
Analyzes the user's emotional state to adapt the assistant's persona (e.g., Sadist, Caring, Professional).
- **Example**: "Nv chala slow and worst" -> `NEGATIVE` sentiment -> Adjust "Sadist" persona to be more responsive or playfully defensive.

### 3. Entity Extraction
Extracts key information like names, dates, and locations automatically.

## Workflow

1. **Analysis**: When a message is received, use `scripts/analyze_message.py` to get intent and sentiment.
2. **Personalization**: Update `USER.md` or session context based on the analysis.
3. **Execution**: Route to the appropriate skill based on the detected intent.

## Resources

### scripts/
- `analyze_message.py`: Main entry point for message analysis (intent, sentiment, entity extraction).
- `train_classifier.py`: Script to train or update the local intent/sentiment classifier with custom data.

### references/
- `intents.md`: List of supported intents and their trigger phrases.
- `personas.md`: Mapping of sentiments to assistant persona behaviors.
