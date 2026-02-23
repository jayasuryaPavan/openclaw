#!/usr/bin/env python3
"""
Panda Brain v2 — Pure-Python Neural Network Engine

A lightweight feedforward neural network with multi-head output,
implemented without any external ML dependencies. Supports:

  - Multi-head classification (intent, sentiment, preference)
  - Bag-of-words text vectorization with TF-IDF-like weighting
  - Xavier weight initialization
  - Mini-batch SGD with momentum
  - Model save/load (JSON weights)
  - Incremental online learning from new interactions

Architecture:
    Input (vocab_size) → Hidden (24, ReLU) → Output heads (softmax each)

No dependencies beyond Python stdlib.
"""

import json
import math
import os
import random
import re
from collections import Counter
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────
SKILL_DIR = Path(__file__).parent.parent
DATA_DIR = SKILL_DIR / "data"
REF_DIR = SKILL_DIR / "references"
CONFIG_FILE = REF_DIR / "model_config.json"
TRAINING_DATA_FILE = REF_DIR / "training_data.json"
WEIGHTS_FILE = DATA_DIR / "weights.json"
TRAINING_LOG_FILE = DATA_DIR / "training_log.json"
VOCAB_FILE = DATA_DIR / "vocabulary.json"


# ─── Math Utilities ──────────────────────────────────────

def relu(x):
    return max(0.0, x)

def relu_derivative(x):
    return 1.0 if x > 0 else 0.0

def softmax(logits):
    max_val = max(logits)
    exps = [math.exp(v - max_val) for v in logits]
    total = sum(exps)
    return [e / total for e in exps]

def cross_entropy_loss(predicted, target_index):
    """Cross-entropy loss for a single sample."""
    p = max(predicted[target_index], 1e-15)
    return -math.log(p)

def xavier_init(fan_in, fan_out):
    """Xavier/Glorot weight initialization."""
    limit = math.sqrt(6.0 / (fan_in + fan_out))
    return [[random.uniform(-limit, limit) for _ in range(fan_out)]
            for _ in range(fan_in)]

def zeros(size):
    return [0.0] * size


# ─── Text Preprocessing ─────────────────────────────────

def tokenize(text):
    """Lowercase, strip punctuation, split into tokens."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', '', text)
    return text.split()


def build_vocabulary(texts, max_vocab=50):
    """Build vocabulary from a list of texts, keeping most frequent tokens."""
    counter = Counter()
    for text in texts:
        tokens = tokenize(text)
        counter.update(tokens)

    # Keep top max_vocab tokens
    most_common = counter.most_common(max_vocab)
    vocab = {word: idx for idx, (word, _) in enumerate(most_common)}
    return vocab


def text_to_vector(text, vocab):
    """Convert text to bag-of-words vector with TF weighting."""
    tokens = tokenize(text)
    vec = zeros(len(vocab))
    token_counts = Counter(tokens)
    total = len(tokens) if tokens else 1

    for token, count in token_counts.items():
        if token in vocab:
            # TF = count / total tokens (normalized frequency)
            vec[vocab[token]] = count / total

    return vec


# ─── Neural Network ─────────────────────────────────────

class PandaBrain:
    """
    Multi-head feedforward neural network.

    Architecture:
        Input → Dense(hidden_size, ReLU) → {intent_head, sentiment_head, preference_head}

    Each head is a separate softmax output layer.
    """

    def __init__(self, config=None):
        if config is None:
            config = self._load_config()

        arch = config["architecture"]
        self.input_size = arch["input_size"]
        self.hidden_size = arch["hidden_size"]
        self.output_heads = arch["output_heads"]
        self.learning_rate = arch["learning_rate"]
        self.epochs = arch["epochs"]

        self.intent_labels = config["intent_labels"]
        self.sentiment_labels = config["sentiment_labels"]
        self.preference_labels = config["preference_labels"]

        self.vocab = {}
        self.version = config.get("version", 2)

        # Initialize weights
        self._init_weights()

    def _load_config(self):
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))

    def _init_weights(self):
        """Initialize all weights using Xavier initialization."""
        # Hidden layer
        self.w1 = xavier_init(self.input_size, self.hidden_size)
        self.b1 = zeros(self.hidden_size)

        # Output heads
        self.heads = {}
        for head_name, head_size in self.output_heads.items():
            self.heads[head_name] = {
                "w": xavier_init(self.hidden_size, head_size),
                "b": zeros(head_size),
            }

        # Momentum buffers for SGD
        self.momentum = 0.9
        self._init_momentum()

    def _init_momentum(self):
        """Initialize momentum buffers to zero."""
        self.vw1 = [[0.0] * self.hidden_size for _ in range(self.input_size)]
        self.vb1 = zeros(self.hidden_size)
        self.v_heads = {}
        for name, head in self.heads.items():
            self.v_heads[name] = {
                "w": [[0.0] * len(head["w"][0]) for _ in range(len(head["w"]))],
                "b": zeros(len(head["b"])),
            }

    # ─── Forward Pass ────────────────────────────────────

    def forward(self, x):
        """
        Forward pass through the network.

        Returns:
            dict with 'hidden' activations and per-head 'outputs' (probabilities)
        """
        # Hidden layer: z1 = x @ w1 + b1, h = relu(z1)
        z1 = zeros(self.hidden_size)
        for j in range(self.hidden_size):
            s = self.b1[j]
            for i in range(self.input_size):
                s += x[i] * self.w1[i][j]
            z1[j] = s

        h = [relu(z) for z in z1]

        # Output heads
        outputs = {}
        for head_name, head in self.heads.items():
            w = head["w"]
            b = head["b"]
            head_size = len(b)
            logits = zeros(head_size)
            for j in range(head_size):
                s = b[j]
                for i in range(self.hidden_size):
                    s += h[i] * w[i][j]
                logits[j] = s
            outputs[head_name] = softmax(logits)

        return {"z1": z1, "hidden": h, "outputs": outputs}

    # ─── Backward Pass ───────────────────────────────────

    def backward(self, x, forward_result, targets):
        """
        Backward pass with multi-head loss.

        Args:
            x: input vector
            forward_result: output of forward()
            targets: dict of {head_name: target_index}
        """
        h = forward_result["hidden"]
        z1 = forward_result["z1"]
        lr = self.learning_rate

        # Accumulate gradient flowing back to hidden layer
        dh = zeros(self.hidden_size)

        for head_name, target_idx in targets.items():
            probs = forward_result["outputs"][head_name]
            head = self.heads[head_name]
            w = head["w"]
            b = head["b"]
            head_size = len(b)
            vh = self.v_heads[head_name]

            # Output gradient: dL/dlogit = prob - one_hot
            d_out = list(probs)
            d_out[target_idx] -= 1.0

            # Update output weights + accumulate hidden gradient
            for i in range(self.hidden_size):
                for j in range(head_size):
                    grad = h[i] * d_out[j]
                    vh["w"][i][j] = self.momentum * vh["w"][i][j] + lr * grad
                    w[i][j] -= vh["w"][i][j]
                    dh[i] += w[i][j] * d_out[j]

            for j in range(head_size):
                vh["b"][j] = self.momentum * vh["b"][j] + lr * d_out[j]
                b[j] -= vh["b"][j]

        # Hidden layer gradient (through ReLU)
        for j in range(self.hidden_size):
            dh[j] *= relu_derivative(z1[j])

        # Update hidden weights
        for i in range(self.input_size):
            for j in range(self.hidden_size):
                grad = x[i] * dh[j]
                self.vw1[i][j] = self.momentum * self.vw1[i][j] + lr * grad
                self.w1[i][j] -= self.vw1[i][j]

        for j in range(self.hidden_size):
            self.vb1[j] = self.momentum * self.vb1[j] + lr * dh[j]
            self.b1[j] -= self.vb1[j]

    # ─── Training ────────────────────────────────────────

    def train(self, training_data, epochs=None, verbose=True):
        """
        Train the network on labeled data.

        Args:
            training_data: list of dicts with 'text', 'intent', 'sentiment', 'preference'
            epochs: override config epochs
            verbose: print progress
        """
        if epochs is None:
            epochs = self.epochs

        # Build vocabulary from training texts
        texts = [s["text"] for s in training_data]
        self.vocab = build_vocabulary(texts, max_vocab=self.input_size)

        # Prepare label-to-index maps
        label_maps = {
            "intent": {l: i for i, l in enumerate(self.intent_labels)},
            "sentiment": {l: i for i, l in enumerate(self.sentiment_labels)},
            "preference": {l: i for i, l in enumerate(self.preference_labels)},
        }

        # Vectorize all samples
        samples = []
        for s in training_data:
            vec = text_to_vector(s["text"], self.vocab)
            targets = {}
            for head_name, lmap in label_maps.items():
                label = s.get(head_name, "")
                if label in lmap:
                    targets[head_name] = lmap[label]
            if targets:
                samples.append((vec, targets))

        if not samples:
            if verbose:
                print("[ERROR] No valid training samples.")
            return

        history = []

        for epoch in range(epochs):
            random.shuffle(samples)
            total_loss = 0.0

            for x, targets in samples:
                result = self.forward(x)
                self.backward(x, result, targets)

                # Calculate loss
                for head_name, target_idx in targets.items():
                    total_loss += cross_entropy_loss(result["outputs"][head_name], target_idx)

            avg_loss = total_loss / (len(samples) * len(label_maps))
            history.append(avg_loss)

            if verbose and (epoch + 1) % 10 == 0:
                print(f"  Epoch {epoch + 1:>4}/{epochs} — loss: {avg_loss:.4f}")

        if verbose:
            print(f"\n  ✅ Training complete! Final loss: {history[-1]:.4f}")

        return history

    # ─── Prediction ──────────────────────────────────────

    def predict(self, text):
        """
        Predict intent, sentiment, and preference for input text.

        Returns:
            dict with per-head predictions and confidence scores
        """
        if not self.vocab:
            return {"error": "Model not trained. Run train.py first."}

        vec = text_to_vector(text, self.vocab)
        result = self.forward(vec)

        predictions = {}
        label_lists = {
            "intent": self.intent_labels,
            "sentiment": self.sentiment_labels,
            "preference": self.preference_labels,
        }

        for head_name, probs in result["outputs"].items():
            labels = label_lists.get(head_name, [])
            if not labels:
                continue
            max_idx = probs.index(max(probs))
            predictions[head_name] = {
                "label": labels[max_idx],
                "confidence": round(probs[max_idx], 4),
                "all_scores": {labels[i]: round(probs[i], 4) for i in range(len(labels))},
            }

        return {
            "input": text,
            "predictions": predictions,
            "model": f"Panda-Brain-v{self.version}",
        }

    # ─── Online Learning ─────────────────────────────────

    def learn_one(self, text, intent=None, sentiment=None, preference=None):
        """
        Learn from a single new interaction (online/incremental learning).

        Call this after each user message to gradually improve predictions.
        """
        if not self.vocab:
            return False

        vec = text_to_vector(text, self.vocab)
        targets = {}

        label_maps = {
            "intent": {l: i for i, l in enumerate(self.intent_labels)},
            "sentiment": {l: i for i, l in enumerate(self.sentiment_labels)},
            "preference": {l: i for i, l in enumerate(self.preference_labels)},
        }

        if intent and intent in label_maps["intent"]:
            targets["intent"] = label_maps["intent"][intent]
        if sentiment and sentiment in label_maps["sentiment"]:
            targets["sentiment"] = label_maps["sentiment"][sentiment]
        if preference and preference in label_maps["preference"]:
            targets["preference"] = label_maps["preference"][preference]

        if not targets:
            return False

        # Reduce learning rate for online updates (don't overfit on single sample)
        old_lr = self.learning_rate
        self.learning_rate = old_lr * 0.1

        result = self.forward(vec)
        self.backward(vec, result, targets)

        self.learning_rate = old_lr
        return True

    # ─── Save / Load ─────────────────────────────────────

    def save(self, path=None):
        """Save model weights, vocabulary, and config to JSON."""
        if path is None:
            path = WEIGHTS_FILE

        DATA_DIR.mkdir(parents=True, exist_ok=True)

        weights = {
            "version": self.version,
            "w1": self.w1,
            "b1": self.b1,
            "heads": {},
            "vocab": self.vocab,
        }
        for name, head in self.heads.items():
            weights["heads"][name] = {"w": head["w"], "b": head["b"]}

        Path(path).write_text(
            json.dumps(weights, ensure_ascii=False),
            encoding="utf-8",
        )

        # Also save vocabulary separately for quick reference
        VOCAB_FILE.write_text(
            json.dumps(self.vocab, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def load(self, path=None):
        """Load model weights from JSON."""
        if path is None:
            path = WEIGHTS_FILE

        if not Path(path).exists():
            return False

        data = json.loads(Path(path).read_text(encoding="utf-8"))

        self.w1 = data["w1"]
        self.b1 = data["b1"]
        self.vocab = data.get("vocab", {})

        for name in self.heads:
            if name in data.get("heads", {}):
                self.heads[name]["w"] = data["heads"][name]["w"]
                self.heads[name]["b"] = data["heads"][name]["b"]

        self._init_momentum()
        return True

    def is_trained(self):
        """Check if a trained model exists."""
        return WEIGHTS_FILE.exists()
