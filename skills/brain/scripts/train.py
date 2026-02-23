#!/usr/bin/env python3
"""
Panda Brain — Training Pipeline

Trains the neural network on the default or custom training data.

Usage:
    python train.py                        # Train with defaults
    python train.py --epochs 200           # Custom epoch count
    python train.py --data custom.json     # Custom training data
    python train.py --retrain              # Retrain from scratch

Model: Panda-Brain-v2 (Pure Python, zero dependencies)
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add parent scripts dir to path
sys.path.insert(0, str(Path(__file__).parent))
from brain_core import PandaBrain, DATA_DIR, TRAINING_DATA_FILE, TRAINING_LOG_FILE


def load_training_data(path=None):
    """Load training data from JSON file."""
    if path is None:
        path = TRAINING_DATA_FILE

    path = Path(path)
    if not path.exists():
        return None, f"Training data not found: {path}"

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        samples = data.get("samples", [])
        return samples, None
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON: {e}"


def save_training_log(history, epochs, num_samples):
    """Append training run to the log."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    log = {"runs": []}
    if TRAINING_LOG_FILE.exists():
        try:
            log = json.loads(TRAINING_LOG_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass

    log["runs"].append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "epochs": epochs,
        "samples": num_samples,
        "final_loss": round(history[-1], 6) if history else None,
        "initial_loss": round(history[0], 6) if history else None,
    })

    # Keep last 50 runs
    log["runs"] = log["runs"][-50:]

    TRAINING_LOG_FILE.write_text(
        json.dumps(log, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def main():
    parser = argparse.ArgumentParser(description="Train the Panda Brain neural network.")
    parser.add_argument("--epochs", "-e", type=int, help="Number of training epochs")
    parser.add_argument("--data", "-d", help="Path to custom training data JSON")
    parser.add_argument("--retrain", action="store_true", help="Retrain from scratch (re-init weights)")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress progress output")
    args = parser.parse_args()

    print("\n🧠 Panda Brain — Training Pipeline\n")

    # Load training data
    samples, err = load_training_data(args.data)
    if not samples:
        print(f"[ERROR] {err}")
        sys.exit(1)

    print(f"  📊 Training samples: {len(samples)}")

    # Initialize brain
    brain = PandaBrain()

    # Load existing weights unless retraining
    if not args.retrain and brain.is_trained():
        brain.load()
        print("  📂 Loaded existing model weights (fine-tuning)")
    else:
        print("  🆕 Training from scratch")

    epochs = args.epochs or brain.epochs
    print(f"  ⚡ Epochs: {epochs}")
    print(f"  📐 Architecture: {brain.input_size} → {brain.hidden_size} → {dict(brain.output_heads)}")
    print()

    # Train
    verbose = not args.quiet
    history = brain.train(samples, epochs=epochs, verbose=verbose)

    # Save
    brain.save()
    save_training_log(history, epochs, len(samples))

    print(f"\n  💾 Model saved to: {brain.is_trained() and 'data/weights.json'}")
    print(f"  📝 Training log updated: data/training_log.json")

    # Quick test
    print("\n─── Quick Test ───────────────────────")
    test_messages = [
        "hello panda",
        "nuvvu chala slow",
        "remind me to call ravi",
        "weather ela undi",
    ]
    for msg in test_messages:
        result = brain.predict(msg)
        preds = result["predictions"]
        intent = preds.get("intent", {})
        sentiment = preds.get("sentiment", {})
        print(f"  \"{msg}\"")
        print(f"    → intent: {intent.get('label', '?')} ({intent.get('confidence', 0):.0%})")
        print(f"    → sentiment: {sentiment.get('label', '?')} ({sentiment.get('confidence', 0):.0%})")

    print("\n✅ Brain is ready!\n")


if __name__ == "__main__":
    main()
