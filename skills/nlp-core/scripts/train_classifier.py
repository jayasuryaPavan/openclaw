#!/usr/bin/env python3
"""
NLP Core - Intent/Sentiment Classifier Trainer for Panda Chat

Trains or updates the local rule-based classifier with custom training data.
Training data is stored as JSON and used to expand the pattern vocabulary.

Usage:
    python train_classifier.py                        # Train with default data
    python train_classifier.py --data training.json   # Train with custom data
    python train_classifier.py --export model.json    # Export current patterns

Training data format (JSON):
    {
        "intents": [
            {"text": "remind me to call", "intent": "REMINDER"},
            {"text": "weather ela undi", "intent": "WEATHER"}
        ],
        "sentiments": [
            {"text": "chala bagundi", "sentiment": "POSITIVE"},
            {"text": "worst ga undi", "sentiment": "NEGATIVE"}
        ]
    }

Model: Panda-NLP-v2 (Rule-Based + Pattern Matching)
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

# Default training examples for bootstrapping
DEFAULT_TRAINING_DATA = {
    "intents": [
        {"text": "remind me to buy milk", "intent": "REMINDER"},
        {"text": "gurthu pettu repu call cheyali", "intent": "REMINDER"},
        {"text": "remember to send email", "intent": "REMINDER"},
        {"text": "what's the weather like", "intent": "WEATHER"},
        {"text": "varshaam vastunda", "intent": "WEATHER"},
        {"text": "is it raining today", "intent": "WEATHER"},
        {"text": "search for AI news", "intent": "SEARCH"},
        {"text": "who is Dhoni", "intent": "SEARCH"},
        {"text": "google chey idi", "intent": "SEARCH"},
        {"text": "hi there", "intent": "GREETING"},
        {"text": "hello panda", "intent": "GREETING"},
        {"text": "em undi bro", "intent": "GREETING"},
        {"text": "help me with this", "intent": "HELP"},
        {"text": "em cheyali idi", "intent": "HELP"},
        {"text": "neural network gurinchi cheppu", "intent": "NLP_DISCUSSION"},
        {"text": "check my email", "intent": "EMAIL_CHECK"},
        {"text": "schedule a meeting tomorrow", "intent": "CALENDAR_ADD"},
        {"text": "update my task status", "intent": "TASK_UPDATE"},
    ],
    "sentiments": [
        {"text": "chala bagundi", "sentiment": "POSITIVE"},
        {"text": "super ga chesav", "sentiment": "POSITIVE"},
        {"text": "masthu undhi bro", "sentiment": "POSITIVE"},
        {"text": "thanks anna", "sentiment": "POSITIVE"},
        {"text": "great job", "sentiment": "POSITIVE"},
        {"text": "nv chala slow", "sentiment": "NEGATIVE"},
        {"text": "worst ga undi", "sentiment": "NEGATIVE"},
        {"text": "pani kaadu idi", "sentiment": "NEGATIVE"},
        {"text": "bokka la undi", "sentiment": "NEGATIVE"},
        {"text": "this is terrible", "sentiment": "NEGATIVE"},
        {"text": "okay fine", "sentiment": "NEUTRAL"},
        {"text": "alright", "sentiment": "NEUTRAL"},
    ],
}

MODEL_FILE = Path(__file__).parent / "model_patterns.json"


def tokenize(text):
    """Simple whitespace tokenizer with cleaning."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', '', text)
    return [w for w in text.split() if len(w) > 1]


def extract_vocabulary(training_data):
    """Extract word frequencies per intent/sentiment from training data."""
    intent_vocab = defaultdict(Counter)
    sentiment_vocab = defaultdict(Counter)

    for item in training_data.get("intents", []):
        tokens = tokenize(item["text"])
        intent_vocab[item["intent"]].update(tokens)

    for item in training_data.get("sentiments", []):
        tokens = tokenize(item["text"])
        sentiment_vocab[item["sentiment"]].update(tokens)

    return intent_vocab, sentiment_vocab


def build_patterns(intent_vocab, sentiment_vocab):
    """Build pattern model from extracted vocabulary."""
    # For each intent, pick the most distinctive words (appear in that intent
    # much more frequently than in others)
    all_intent_words = Counter()
    for words in intent_vocab.values():
        all_intent_words.update(words)

    intent_patterns = {}
    for intent, words in intent_vocab.items():
        # Words that appear mostly in this intent
        distinctive = []
        for word, count in words.most_common(10):
            total = all_intent_words[word]
            if count / total >= 0.5:  # Word appears >= 50% of the time in this intent
                distinctive.append(word)
        if distinctive:
            intent_patterns[intent] = distinctive

    # For sentiment, just collect the words
    sentiment_words = {
        "POSITIVE": list(sentiment_vocab.get("POSITIVE", {}).keys()),
        "NEGATIVE": list(sentiment_vocab.get("NEGATIVE", {}).keys()),
    }

    return {
        "intent_patterns": intent_patterns,
        "sentiment_words": sentiment_words,
        "training_samples": {
            "intents": sum(1 for _ in intent_vocab.values()),
            "sentiments": sum(1 for _ in sentiment_vocab.values()),
        },
    }


def train(training_data, output_path=None):
    """Train the classifier and save the model patterns."""
    print("=" * 50)
    print("  Panda NLP Classifier Trainer v2")
    print("=" * 50)

    n_intents = len(training_data.get("intents", []))
    n_sentiments = len(training_data.get("sentiments", []))
    print(f"\nTraining data:")
    print(f"  Intent examples:    {n_intents}")
    print(f"  Sentiment examples: {n_sentiments}")

    if n_intents == 0 and n_sentiments == 0:
        print("\n[ERROR] No training data provided.")
        return False

    print("\nExtracting vocabulary...")
    intent_vocab, sentiment_vocab = extract_vocabulary(training_data)

    intent_categories = len(intent_vocab)
    sentiment_categories = len(sentiment_vocab)
    print(f"  Intent categories:    {intent_categories}")
    print(f"  Sentiment categories: {sentiment_categories}")

    print("\nBuilding patterns...")
    model = build_patterns(intent_vocab, sentiment_vocab)

    # Print summary
    print("\nIntent patterns learned:")
    for intent, words in model["intent_patterns"].items():
        print(f"  {intent}: {', '.join(words[:5])}{'...' if len(words) > 5 else ''}")

    print(f"\nSentiment vocabulary:")
    pos_words = model["sentiment_words"].get("POSITIVE", [])
    neg_words = model["sentiment_words"].get("NEGATIVE", [])
    print(f"  Positive words: {len(pos_words)} ({', '.join(pos_words[:5])}...)")
    print(f"  Negative words: {len(neg_words)} ({', '.join(neg_words[:5])}...)")

    # Save model
    save_path = Path(output_path) if output_path else MODEL_FILE
    save_path.write_text(json.dumps(model, indent=2))
    print(f"\n[OK] Model saved to: {save_path}")
    print(f"     File size: {save_path.stat().st_size} bytes")

    print("\n" + "=" * 50)
    print("  Training complete!")
    print("=" * 50)
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Train or update the Panda NLP classifier.",
    )
    parser.add_argument(
        "--data",
        help="Path to training data JSON file (uses defaults if not provided)",
    )
    parser.add_argument(
        "--export",
        help="Export current patterns to a JSON file",
    )
    args = parser.parse_args()

    # Export mode
    if args.export:
        if MODEL_FILE.exists():
            model = json.loads(MODEL_FILE.read_text())
            export_path = Path(args.export)
            export_path.write_text(json.dumps(model, indent=2))
            print(f"[OK] Exported model to: {export_path}")
        else:
            print("[ERROR] No trained model found. Run training first.")
            sys.exit(1)
        return

    # Training mode
    if args.data:
        data_path = Path(args.data)
        if not data_path.exists():
            print(f"[ERROR] Training data file not found: {data_path}")
            sys.exit(1)
        try:
            training_data = json.loads(data_path.read_text())
        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid JSON in training data: {e}")
            sys.exit(1)
    else:
        print("No custom training data provided, using defaults.\n")
        training_data = DEFAULT_TRAINING_DATA

    success = train(training_data)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
