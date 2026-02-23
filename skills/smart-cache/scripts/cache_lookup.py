#!/usr/bin/env python3
"""
Smart Cache - Fast Pattern Matcher for Panda Chat

Checks incoming messages against the local response cache BEFORE hitting the LLM.
Returns a cached response instantly if matched, or signals a cache miss.

Usage:
    python cache_lookup.py "hello panda"
    python cache_lookup.py "check email" --stats
    echo "em undi" | python cache_lookup.py

Exit codes:
    0 = cache hit (response printed as JSON)
    1 = cache miss (should be sent to LLM)
    2 = error

Model: Local pattern matching (zero API calls)
"""

import json
import random
import re
import sys
import time
from difflib import SequenceMatcher
from pathlib import Path

CACHE_FILE = Path(__file__).parent.parent / "references" / "response_cache.json"


def load_cache():
    """Load the response cache from JSON."""
    if not CACHE_FILE.exists():
        return None, f"Cache file not found: {CACHE_FILE}"
    try:
        data = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        return data, None
    except json.JSONDecodeError as e:
        return None, f"Invalid cache JSON: {e}"


def save_cache(data):
    """Save updated cache (stats, learned entries) back to JSON."""
    try:
        CACHE_FILE.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    except IOError as e:
        print(f"Warning: Could not save cache stats: {e}", file=sys.stderr)


def normalize(text):
    """Normalize text for matching: lowercase, strip punctuation, collapse whitespace."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text


def fuzzy_score(a, b):
    """Calculate similarity ratio between two strings."""
    return SequenceMatcher(None, a, b).ratio()


def lookup(message, cache_data):
    """
    Look up a message in the cache.

    Returns:
        (hit, result) where hit is True/False and result is the response dict
    """
    normalized = normalize(message)
    settings = cache_data.get("settings", {})
    fuzzy_threshold = settings.get("fuzzy_threshold", 0.8)
    categories = cache_data.get("categories", {})

    best_match = None
    best_score = 0.0
    best_category = None

    for cat_name, cat_data in categories.items():
        patterns = cat_data.get("patterns", [])
        mode = cat_data.get("mode", "random")

        # Passthrough categories never cache — always send to LLM
        if mode == "passthrough":
            # But still check if match, to report it as a known-but-uncacheable pattern
            for pattern in patterns:
                norm_pattern = normalize(pattern)
                if normalized == norm_pattern or norm_pattern in normalized:
                    return False, {
                        "status": "passthrough",
                        "category": cat_name,
                        "reason": cat_data.get("note", "Needs live data"),
                        "matched_pattern": pattern,
                    }
            continue

        responses = cat_data.get("responses", [])
        if not responses:
            continue

        for pattern in patterns:
            norm_pattern = normalize(pattern)

            # Exact match
            if normalized == norm_pattern:
                score = 1.0
            # Substring match (pattern is inside the message)
            elif norm_pattern in normalized:
                # Weight by how much of the message the pattern covers
                score = len(norm_pattern) / max(len(normalized), 1) * 0.95
            # Fuzzy match
            else:
                score = fuzzy_score(normalized, norm_pattern)

            if score > best_score:
                best_score = score
                best_match = pattern
                best_category = cat_name

    # Check if we have a good enough match
    if best_score >= fuzzy_threshold and best_category:
        cat_data = categories[best_category]
        responses = cat_data.get("responses", [])
        mode = cat_data.get("mode", "random")

        if mode == "random":
            response_text = random.choice(responses)
        else:
            response_text = responses[0]

        result = {
            "status": "hit",
            "category": best_category,
            "response": response_text,
            "confidence": round(best_score, 3),
            "matched_pattern": best_match,
        }

        # Include action if present
        action = cat_data.get("action")
        if action:
            result["action"] = action

        return True, result

    # Cache miss
    return False, {
        "status": "miss",
        "best_category": best_category,
        "best_score": round(best_score, 3) if best_score > 0 else 0,
        "best_pattern": best_match,
    }


def update_stats(cache_data, hit):
    """Update cache hit/miss statistics."""
    stats = cache_data.get("stats", {})
    stats["total_lookups"] = stats.get("total_lookups", 0) + 1
    if hit:
        stats["cache_hits"] = stats.get("cache_hits", 0) + 1
    else:
        stats["cache_misses"] = stats.get("cache_misses", 0) + 1
    cache_data["stats"] = stats


def print_stats(cache_data):
    """Print cache statistics."""
    stats = cache_data.get("stats", {})
    total = stats.get("total_lookups", 0)
    hits = stats.get("cache_hits", 0)
    misses = stats.get("cache_misses", 0)
    hit_rate = (hits / total * 100) if total > 0 else 0

    categories = cache_data.get("categories", {})
    total_patterns = sum(len(c.get("patterns", [])) for c in categories.values())
    total_responses = sum(len(c.get("responses", [])) for c in categories.values())

    print(f"\n📊 Smart Cache Stats")
    print(f"{'─' * 35}")
    print(f"  Categories:    {len(categories)}")
    print(f"  Patterns:      {total_patterns}")
    print(f"  Responses:     {total_responses}")
    print(f"{'─' * 35}")
    print(f"  Total lookups: {total}")
    print(f"  Cache hits:    {hits}")
    print(f"  Cache misses:  {misses}")
    print(f"  Hit rate:      {hit_rate:.1f}%")
    print(f"{'─' * 35}")


def main():
    # Get message from args or stdin
    show_stats = "--stats" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--stats"]

    if args:
        message = " ".join(args)
    elif not sys.stdin.isatty():
        message = sys.stdin.read().strip()
    else:
        if show_stats:
            cache_data, err = load_cache()
            if cache_data:
                print_stats(cache_data)
            else:
                print(f"Error: {err}", file=sys.stderr)
            sys.exit(0)

        print(json.dumps({"error": "No message. Usage: python cache_lookup.py \"your message\""}))
        sys.exit(2)

    # Load cache
    cache_data, err = load_cache()
    if not cache_data:
        print(json.dumps({"error": err}))
        sys.exit(2)

    # Perform lookup
    hit, result = lookup(message, cache_data)
    result["input"] = message

    # Update stats
    if cache_data.get("settings", {}).get("stats_enabled", True):
        update_stats(cache_data, hit)
        save_cache(cache_data)

    # Print stats if requested
    if show_stats:
        print_stats(cache_data)

    # Output result
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Exit code: 0 = hit, 1 = miss/passthrough
    sys.exit(0 if hit else 1)


if __name__ == "__main__":
    main()
