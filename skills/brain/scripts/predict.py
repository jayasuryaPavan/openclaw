#!/usr/bin/env python3
"""
Panda Brain — Prediction CLI

Predict intent, sentiment, and user preference for any message.

Usage:
    python predict.py "hello panda"
    python predict.py "remind me to call mom" --verbose
    echo "em undi" | python predict.py
    python predict.py --learn "hello" --intent GREETING --sentiment POSITIVE

Model: Panda-Brain-v2 (Pure Python, zero dependencies)
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from brain_core import PandaBrain


def main():
    parser = argparse.ArgumentParser(description="Predict intent/sentiment/preference with Panda Brain.")
    parser.add_argument("message", nargs="*", help="Message to analyze")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show all class scores")
    parser.add_argument("--learn", action="store_true", help="Learn from this message (provide labels)")
    parser.add_argument("--intent", help="Intent label for learning")
    parser.add_argument("--sentiment", help="Sentiment label for learning")
    parser.add_argument("--preference", help="Preference label for learning")
    args = parser.parse_args()

    # Get message from args or stdin
    if args.message:
        message = " ".join(args.message)
    elif not sys.stdin.isatty():
        message = sys.stdin.read().strip()
    else:
        parser.print_help()
        sys.exit(1)

    if not message:
        print(json.dumps({"error": "Empty message"}))
        sys.exit(1)

    # Load brain
    brain = PandaBrain()
    if not brain.is_trained():
        print(json.dumps({"error": "Model not trained. Run train.py first."}))
        sys.exit(1)

    brain.load()

    # Online learning mode
    if args.learn:
        success = brain.learn_one(
            message,
            intent=args.intent,
            sentiment=args.sentiment,
            preference=args.preference,
        )
        if success:
            brain.save()
            print(json.dumps({
                "status": "learned",
                "message": message,
                "labels": {
                    "intent": args.intent,
                    "sentiment": args.sentiment,
                    "preference": args.preference,
                },
            }, indent=2))
        else:
            print(json.dumps({"error": "Could not learn — check labels"}))
            sys.exit(1)
        return

    # Prediction mode
    result = brain.predict(message)

    if args.verbose:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        preds = result.get("predictions", {})
        compact = {
            "input": message,
            "intent": preds.get("intent", {}).get("label", "?"),
            "intent_confidence": preds.get("intent", {}).get("confidence", 0),
            "sentiment": preds.get("sentiment", {}).get("label", "?"),
            "sentiment_confidence": preds.get("sentiment", {}).get("confidence", 0),
            "preference": preds.get("preference", {}).get("label", "?"),
            "model": result.get("model", "unknown"),
        }
        print(json.dumps(compact, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
