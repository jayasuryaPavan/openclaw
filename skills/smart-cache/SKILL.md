---
name: smart-cache
description: Local response cache for instant replies to repetitive messages. Use BEFORE sending any message to the LLM — check if the message matches a cached pattern first. Handles greetings, farewells, thanks, status checks, common commands, and playful banter without any API calls. Saves quota and provides instant responses.
---

# Smart Cache

## Overview

The Smart Cache intercepts incoming messages and checks them against a local pattern database. If a match is found, it returns a pre-stored Tenglish response instantly — no LLM API call needed. This dramatically reduces quota usage for the 90%+ of messages that are repetitive.

## When to Use

**ALWAYS** run `cache_lookup.py` before sending a message to the LLM. The flow is:

1. Run `scripts/cache_lookup.py "<message>"`
2. If exit code is **0** (cache hit) → use the cached response, skip LLM
3. If exit code is **1** (cache miss) → send to LLM as normal
4. If the result has `"status": "passthrough"` → needs live data, send to LLM

## Workflow

```
Message received
    ↓
cache_lookup.py "<message>"
    ↓
┌─────────────┐
│ Exit code 0 │ → Cache HIT → Return cached response instantly
│ Exit code 1 │ → Cache MISS → Send to LLM
│   passthru  │ → Known pattern but needs live data → Send to LLM
└─────────────┘
```

## Managing the Cache

### Adding new patterns

When you notice the user repeats a message that always gets the same response:

```bash
# Add a pattern to an existing category
scripts/cache_learn.py add -c greeting -p "wassup bro"

# Add a pattern with a specific response
scripts/cache_learn.py add -c greeting -p "ey pandu" -r "Cheppu pandu! 🐼"

# Create a whole new category
scripts/cache_learn.py add-category -n "music" -p "play music,song pettu" -r "Enti song kavali pandu? 🎵"
```

### Viewing the cache

```bash
scripts/cache_learn.py list                     # All categories
scripts/cache_learn.py list -c greeting         # Just greetings
scripts/cache_lookup.py --stats                 # Hit/miss stats
```

### Removing patterns

```bash
scripts/cache_learn.py remove -c greeting -p "wassup bro"
```

## Proactive Check-In

If the user hasn't texted for 12 hours, Panda will proactively message them on Telegram.

### Setup

```bash
# 1. Auto-discover your Telegram chat ID
scripts/checkin_monitor.py setup

# 2. View the generated Task Scheduler command
scripts/checkin_monitor.py install-schedule
```

### How it works
- `checkin_monitor.py heartbeat` — call on every incoming message to track activity
- `checkin_monitor.py check` — checks inactivity and sends Telegram if > 12h
- Won't send check-ins during sleep hours (11 PM – 7 AM)
- Won't send duplicate check-ins if already sent one since the last message

### Status
```bash
scripts/checkin_monitor.py status
```

## Resources

### scripts/
- `cache_lookup.py`: Fast pattern matcher — run this BEFORE the LLM. Returns cached response or signals miss.
- `cache_learn.py`: Cache management — add/remove patterns, create categories, view stats.
- `checkin_monitor.py`: Proactive check-in — tracks activity and sends Telegram after 12h inactivity.

### references/
- `response_cache.json`: The local pattern database with all cached patterns, responses, and statistics.
- `activity.json`: Activity tracker — last message timestamp, chat ID, check-in config.

