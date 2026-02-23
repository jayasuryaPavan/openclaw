#!/usr/bin/env python3
"""
NLP Core - Message Analyzer for Panda Chat
Analyzes messages for intent, sentiment, and named entities.

Usage:
    python analyze_message.py "your message here"
    echo "your message" | python analyze_message.py

Model: Panda-NLP-v2 (Rule-Based + Pattern Matching)
"""

import json
import re
import sys


# --- Sentiment Analysis ---

NEGATIVE_WORDS = {
    # English
    "slow", "worst", "bad", "hate", "stupid", "boring", "ugly", "terrible",
    "awful", "useless", "broken", "annoying", "frustrating", "wrong",
    # Tenglish (Telugu in English script)
    "ra", "chala", "mottam", "paniki", "radu", "pani", "kaadu",
    "cheskodam", "ledu", "waste", "mosam", "donga", "bokka",
}

POSITIVE_WORDS = {
    # English
    "good", "great", "love", "fast", "smart", "awesome", "perfect",
    "amazing", "excellent", "brilliant", "cool", "nice", "best",
    # Tenglish
    "buddi", "pandu", "bagundi", "baaga", "super", "manchi",
    "nachindi", "ishtam", "thankyou", "thanks", "bro", "anna",
    "masthu", "thop", "sakkagundi",
}

NEGATIVE_PHRASES = [
    "chala slow", "pani kaadu", "paniki radu", "bokka la",
    "worst ga", "mottam waste",
]

POSITIVE_PHRASES = [
    "chala bagundi", "super ga", "baaga chesav", "masthu undhi",
    "thop bro", "sakka gundi",
]


def get_sentiment(text):
    """Analyze sentiment using word/phrase matching with confidence scoring."""
    text_lower = text.lower()
    score = 0

    # Check phrases first (higher weight)
    for phrase in NEGATIVE_PHRASES:
        if phrase in text_lower:
            score -= 2

    for phrase in POSITIVE_PHRASES:
        if phrase in text_lower:
            score += 2

    # Then check individual words
    for word in text_lower.split():
        clean_word = re.sub(r'[^\w]', '', word)
        if clean_word in NEGATIVE_WORDS:
            score -= 1
        elif clean_word in POSITIVE_WORDS:
            score += 1

    if score < 0:
        confidence = min(abs(score) * 0.15 + 0.5, 1.0)
        return "NEGATIVE", round(confidence, 2)
    elif score > 0:
        confidence = min(abs(score) * 0.15 + 0.5, 1.0)
        return "POSITIVE", round(confidence, 2)
    else:
        return "NEUTRAL", 0.5


# --- Intent Classification ---

INTENT_PATTERNS = {
    "REMINDER":       r'\b(remind|remember|reminder|gurthu\s*pettu|gurthu\s*cheppu)\b',
    "WEATHER":        r'\b(weather|temp|temperature|varshaam|vaanam|rain)\b',
    "SEARCH":         r'\b(search|find|who\s+is|google|cheppu\s+evaru|ento)\b',
    "HELP":           r'\b(help|assist|chey|cheyyi|em\s+cheyali|how\s+to)\b',
    "GREETING":       r'\b(hi|hello|hey|hii|namaste|em\s*undi|ela\s*unnav)\b',
    "NLP_DISCUSSION": r'\b(neural|network|nlp|machine\s*learning|ai|model|train)\b',
    "EMAIL_CHECK":    r'\b(email|mail|inbox|gmail)\b',
    "CALENDAR_ADD":   r'\b(calendar|schedule|event|meeting)\b',
    "TASK_UPDATE":    r'\b(task|todo|update|status)\b',
}


def get_intent(text):
    """Classify the intent of a message using regex pattern matching."""
    text_lower = text.lower()

    for intent, pattern in INTENT_PATTERNS.items():
        if re.search(pattern, text_lower):
            return intent, 0.85

    return "UNKNOWN", 0.0


# --- Entity Extraction ---

ENTITY_PATTERNS = {
    "TIME": r'\b(\d{1,2}:\d{2}\s*(?:am|pm)?|\d{1,2}\s*(?:am|pm)|morning|evening|night|tomorrow|today|yesterday|repu|ninna|ipudu)\b',
    "DATE": r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|monday|tuesday|wednesday|thursday|friday|saturday|sunday|jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\b',
    "NUMBER": r'\b(\d+(?:\.\d+)?)\b',
    "URL": r'(https?://\S+)',
}


def extract_entities(text):
    """Extract named entities (time, date, numbers, URLs) from text."""
    entities = []
    text_lower = text.lower()

    for entity_type, pattern in ENTITY_PATTERNS.items():
        matches = re.finditer(pattern, text_lower)
        for match in matches:
            entities.append({
                "type": entity_type,
                "value": match.group(1) if match.lastindex else match.group(0),
                "start": match.start(),
                "end": match.end(),
            })

    # Deduplicate by position
    seen = set()
    unique_entities = []
    for entity in entities:
        key = (entity["start"], entity["end"])
        if key not in seen:
            seen.add(key)
            unique_entities.append(entity)

    return unique_entities


# --- Main ---

def analyze(message):
    """Run full NLP analysis on a message."""
    clean_text = re.sub(r'[^\w\s]', '', message.lower())

    sentiment_label, sentiment_conf = get_sentiment(message)
    intent_label, intent_conf = get_intent(message)
    entities = extract_entities(message)

    return {
        "text": message,
        "analysis": {
            "sentiment": {
                "label": sentiment_label,
                "confidence": sentiment_conf,
            },
            "intent": {
                "label": intent_label,
                "confidence": intent_conf,
            },
            "entities": entities,
        },
        "model": "Panda-NLP-v2 (Rule-Based)",
    }


def main():
    # Support both CLI args and stdin
    if len(sys.argv) >= 2:
        message = " ".join(sys.argv[1:])
    elif not sys.stdin.isatty():
        message = sys.stdin.read().strip()
    else:
        print(json.dumps({"error": "No message provided. Usage: python analyze_message.py \"your message\""}))
        sys.exit(1)

    if not message:
        print(json.dumps({"error": "Empty message"}))
        sys.exit(1)

    result = analyze(message)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
