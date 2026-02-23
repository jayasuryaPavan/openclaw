#!/usr/bin/env python3
"""
Smart Cache - Pattern Learner for Panda Chat

Learns new patterns and responses from conversations.
Add new entries to the cache so future identical messages get instant responses.

Usage:
    python cache_learn.py add --category greeting --pattern "wassup" --response "Yo pandu! 😎"
    python cache_learn.py add --category greeting --pattern "ey bro"
    python cache_learn.py add-category --name "music" --patterns "play music,song pettu" --responses "Enti song kavali pandu? 🎵"
    python cache_learn.py remove --category greeting --pattern "wassup"
    python cache_learn.py list
    python cache_learn.py list --category greeting
    python cache_learn.py reset-stats
"""

import argparse
import json
import sys
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
    """Save updated cache back to JSON."""
    CACHE_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def cmd_add(args, cache_data):
    """Add a pattern (and optionally a response) to an existing category."""
    categories = cache_data.get("categories", {})

    if args.category not in categories:
        available = ", ".join(sorted(categories.keys()))
        print(f"[ERROR] Category '{args.category}' not found.")
        print(f"   Available: {available}")
        print(f"   Use 'add-category' to create a new one.")
        return False

    cat = categories[args.category]
    pattern = args.pattern.strip().lower()

    # Check for duplicates
    if pattern in [p.lower() for p in cat.get("patterns", [])]:
        print(f"[SKIP] Pattern '{pattern}' already exists in '{args.category}'.")
    else:
        cat.setdefault("patterns", []).append(pattern)
        print(f"[OK] Added pattern '{pattern}' to '{args.category}'.")

    # Add response if provided
    if args.response:
        response = args.response.strip()
        if response in cat.get("responses", []):
            print(f"[SKIP] Response already exists in '{args.category}'.")
        else:
            cat.setdefault("responses", []).append(response)
            print(f"[OK] Added response to '{args.category}'.")

    save_cache(cache_data)
    return True


def cmd_add_category(args, cache_data):
    """Create a new category with initial patterns and responses."""
    categories = cache_data.setdefault("categories", {})

    name = args.name.strip().lower().replace(" ", "_")

    if name in categories:
        print(f"[ERROR] Category '{name}' already exists.")
        return False

    patterns = [p.strip() for p in args.patterns.split(",") if p.strip()]
    responses = [r.strip() for r in args.responses.split(",") if r.strip()] if args.responses else []

    mode = args.mode if args.mode else ("random" if len(responses) > 1 else "first")

    categories[name] = {
        "patterns": patterns,
        "responses": responses,
        "mode": mode,
    }

    save_cache(cache_data)
    print(f"[OK] Created category '{name}' with {len(patterns)} patterns and {len(responses)} responses.")
    return True


def cmd_remove(args, cache_data):
    """Remove a pattern from a category."""
    categories = cache_data.get("categories", {})

    if args.category not in categories:
        print(f"[ERROR] Category '{args.category}' not found.")
        return False

    cat = categories[args.category]
    pattern = args.pattern.strip().lower()
    patterns_lower = [p.lower() for p in cat.get("patterns", [])]

    if pattern not in patterns_lower:
        print(f"[ERROR] Pattern '{pattern}' not found in '{args.category}'.")
        return False

    idx = patterns_lower.index(pattern)
    removed = cat["patterns"].pop(idx)
    save_cache(cache_data)
    print(f"[OK] Removed pattern '{removed}' from '{args.category}'.")
    return True


def cmd_list(args, cache_data):
    """List all categories and their patterns."""
    categories = cache_data.get("categories", {})

    if args.category:
        if args.category not in categories:
            print(f"[ERROR] Category '{args.category}' not found.")
            return False
        cats_to_show = {args.category: categories[args.category]}
    else:
        cats_to_show = categories

    total_patterns = 0
    total_responses = 0

    for name, cat in cats_to_show.items():
        patterns = cat.get("patterns", [])
        responses = cat.get("responses", [])
        mode = cat.get("mode", "random")
        action = cat.get("action", "")
        total_patterns += len(patterns)
        total_responses += len(responses)

        print(f"\n📂 {name} ({mode}){' → ' + action if action else ''}")
        print(f"   Patterns ({len(patterns)}): {', '.join(patterns[:8])}{'...' if len(patterns) > 8 else ''}")
        if responses:
            print(f"   Responses ({len(responses)}): {responses[0][:60]}{'...' if len(responses[0]) > 60 else ''}")
        else:
            print(f"   Responses: (passthrough — sent to LLM)")

    print(f"\n{'─' * 40}")
    print(f"Total: {len(cats_to_show)} categories, {total_patterns} patterns, {total_responses} responses")
    return True


def cmd_reset_stats(args, cache_data):
    """Reset hit/miss statistics."""
    cache_data["stats"] = {
        "total_lookups": 0,
        "cache_hits": 0,
        "cache_misses": 0,
        "last_reset": None,
    }
    save_cache(cache_data)
    print("[OK] Stats reset to zero.")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Learn new patterns and manage the smart cache.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # add
    add_parser = subparsers.add_parser("add", help="Add a pattern to an existing category")
    add_parser.add_argument("--category", "-c", required=True, help="Category name")
    add_parser.add_argument("--pattern", "-p", required=True, help="Pattern text to add")
    add_parser.add_argument("--response", "-r", help="Optional response to add")

    # add-category
    addcat_parser = subparsers.add_parser("add-category", help="Create a new category")
    addcat_parser.add_argument("--name", "-n", required=True, help="Category name")
    addcat_parser.add_argument("--patterns", "-p", required=True, help="Comma-separated patterns")
    addcat_parser.add_argument("--responses", "-r", help="Comma-separated responses")
    addcat_parser.add_argument("--mode", "-m", choices=["random", "first", "passthrough"], help="Response mode")

    # remove
    rm_parser = subparsers.add_parser("remove", help="Remove a pattern from a category")
    rm_parser.add_argument("--category", "-c", required=True, help="Category name")
    rm_parser.add_argument("--pattern", "-p", required=True, help="Pattern to remove")

    # list
    list_parser = subparsers.add_parser("list", help="List all categories")
    list_parser.add_argument("--category", "-c", help="Show only this category")

    # reset-stats
    subparsers.add_parser("reset-stats", help="Reset hit/miss statistics")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Load cache
    cache_data, err = load_cache()
    if not cache_data:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(2)

    # Dispatch command
    commands = {
        "add": cmd_add,
        "add-category": cmd_add_category,
        "remove": cmd_remove,
        "list": cmd_list,
        "reset-stats": cmd_reset_stats,
    }

    handler = commands.get(args.command)
    if handler:
        success = handler(args, cache_data)
        sys.exit(0 if success else 1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
