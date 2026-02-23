#!/usr/bin/env python3
"""
Smart Cache - Proactive Check-In Monitor for Panda Chat

Monitors user activity and sends a Telegram message if the user
hasn't texted for a configurable period (default: 12 hours).

Usage:
    python checkin_monitor.py check              # Check and send if inactive
    python checkin_monitor.py heartbeat          # Record activity (call on every message)
    python checkin_monitor.py status             # Show current activity status
    python checkin_monitor.py setup              # Auto-discover Telegram chat ID
    python checkin_monitor.py install-schedule   # Install Windows Task Scheduler job

Configuration is in references/activity.json:
    - inactivity_hours: hours before sending check-in (default: 12)
    - sleep_hours: don't disturb window (default: 11 PM - 7 AM)
    - chat_id: Telegram chat ID (auto-discovered or manual)
"""

import argparse
import json
import os
import random
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

# Paths
SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
ACTIVITY_FILE = SKILL_DIR / "references" / "activity.json"
OPENCLAW_CONFIG = SKILL_DIR.parent.parent / "openclaw.json"


def load_activity():
    """Load activity tracker."""
    if not ACTIVITY_FILE.exists():
        return None, "activity.json not found"
    try:
        return json.loads(ACTIVITY_FILE.read_text(encoding="utf-8")), None
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON: {e}"


def save_activity(data):
    """Save activity tracker."""
    ACTIVITY_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def get_bot_token():
    """Extract bot token from config files or environment."""
    # 1. Check environment variable
    env_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if env_token:
        return env_token, None

    # 2. Check secrets.json (primary location)
    secrets_file = SKILL_DIR.parent.parent / "secrets.json"
    if secrets_file.exists():
        try:
            secrets = json.loads(secrets_file.read_text(encoding="utf-8"))
            # Look in channels.telegram.botToken
            token = secrets.get("channels", {}).get("telegram", {}).get("botToken")
            if not token:
                # Also check flat structure
                token = secrets.get("telegram", {}).get("botToken")
            if token:
                return token, None
        except json.JSONDecodeError:
            pass

    # 3. Fall back to openclaw.json
    if OPENCLAW_CONFIG.exists():
        try:
            config = json.loads(OPENCLAW_CONFIG.read_text(encoding="utf-8"))
            token = config.get("channels", {}).get("telegram", {}).get("botToken")
            if token:
                return token, None
        except json.JSONDecodeError:
            pass

    return None, "No bot token found. Set TELEGRAM_BOT_TOKEN env var or add botToken to secrets.json"


def telegram_api(token, method, params=None):
    """Call Telegram Bot API."""
    url = f"https://api.telegram.org/bot{token}/{method}"
    if params:
        import urllib.parse
        query = urllib.parse.urlencode(params)
        url = f"{url}?{query}"

    req = Request(url, headers={"User-Agent": "PandaChat/1.0"})
    try:
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data, None
    except URLError as e:
        return None, f"Telegram API error: {e}"
    except json.JSONDecodeError as e:
        return None, f"Invalid Telegram response: {e}"


def now_iso():
    """Current UTC time as ISO string."""
    return datetime.now(timezone.utc).isoformat()


def parse_iso(iso_str):
    """Parse ISO datetime string to datetime object."""
    if not iso_str:
        return None
    try:
        return datetime.fromisoformat(iso_str)
    except (ValueError, TypeError):
        return None


def is_sleep_hours(sleep_config):
    """Check if current local time is within sleep hours."""
    if not sleep_config:
        return False
    now = datetime.now()
    hour = now.hour
    start = sleep_config.get("start", 23)
    end = sleep_config.get("end", 7)

    if start > end:
        # Crosses midnight: e.g., 23-7
        return hour >= start or hour < end
    else:
        return start <= hour < end


# --- Commands ---

def cmd_heartbeat(args, activity):
    """Record that the user sent a message (call on every incoming message)."""
    activity["last_message_at"] = now_iso()
    save_activity(activity)
    print(f"[OK] Activity recorded at {activity['last_message_at']}")
    return True


def cmd_check(args, activity):
    """Check if user has been inactive and send check-in if needed."""
    token, err = get_bot_token()
    if not token:
        print(f"[ERROR] {err}")
        return False

    chat_id = activity.get("chat_id")
    if not chat_id:
        print("[ERROR] No chat_id configured. Run 'setup' first.")
        return False

    inactivity_hours = activity.get("inactivity_hours", 12)
    last_message = parse_iso(activity.get("last_message_at"))
    last_checkin = parse_iso(activity.get("last_checkin_at"))

    # If no message recorded yet, skip
    if not last_message:
        print("[INFO] No activity recorded yet. Skipping check.")
        return True

    # Calculate hours since last message
    now = datetime.now(timezone.utc)
    hours_inactive = (now - last_message).total_seconds() / 3600

    print(f"[INFO] Last message: {last_message.isoformat()}")
    print(f"[INFO] Hours inactive: {hours_inactive:.1f} / {inactivity_hours}")

    if hours_inactive < inactivity_hours:
        print(f"[OK] User is active (within {inactivity_hours}h window). No check-in needed.")
        return True

    # Don't disturb during sleep hours
    sleep_config = activity.get("sleep_hours")
    if is_sleep_hours(sleep_config):
        print("[INFO] Sleep hours — skipping check-in. Will try again later.")
        return True

    # Don't send another check-in if we already sent one since the last message
    if last_checkin:
        if last_checkin > last_message:
            print("[INFO] Already sent a check-in since last message. Skipping.")
            return True

    # Send check-in message
    messages = activity.get("checkin_messages", [])
    if not messages:
        print("[ERROR] No check-in messages configured.")
        return False

    msg = random.choice(messages)
    print(f"[SENDING] Check-in to chat {chat_id}: {msg}")

    result, err = telegram_api(token, "sendMessage", {
        "chat_id": chat_id,
        "text": msg,
    })

    if err:
        print(f"[ERROR] Failed to send: {err}")
        return False

    if result and result.get("ok"):
        activity["last_checkin_at"] = now_iso()
        save_activity(activity)
        print("[OK] Check-in sent successfully!")
        return True
    else:
        error_desc = result.get("description", "Unknown error") if result else "No response"
        print(f"[ERROR] Telegram error: {error_desc}")
        return False


def cmd_status(args, activity):
    """Show current activity status."""
    last_message = parse_iso(activity.get("last_message_at"))
    last_checkin = parse_iso(activity.get("last_checkin_at"))
    chat_id = activity.get("chat_id")
    inactivity_hours = activity.get("inactivity_hours", 12)

    print(f"\n🐼 Panda Chat Check-In Status")
    print(f"{'─' * 40}")
    print(f"  Chat ID:          {chat_id or 'Not set (run setup)'}")
    print(f"  Inactivity limit: {inactivity_hours} hours")

    if last_message:
        now = datetime.now(timezone.utc)
        hours_ago = (now - last_message).total_seconds() / 3600
        print(f"  Last message:     {hours_ago:.1f}h ago")
        remaining = max(0, inactivity_hours - hours_ago)
        if remaining > 0:
            print(f"  Check-in in:      {remaining:.1f}h")
        else:
            print(f"  Check-in:         ⚠️ OVERDUE by {abs(remaining):.1f}h")
    else:
        print(f"  Last message:     Never recorded")

    if last_checkin:
        now = datetime.now(timezone.utc)
        checkin_ago = (now - last_checkin).total_seconds() / 3600
        print(f"  Last check-in:    {checkin_ago:.1f}h ago")
    else:
        print(f"  Last check-in:    Never sent")

    sleep = activity.get("sleep_hours", {})
    in_sleep = is_sleep_hours(sleep)
    print(f"  Sleep window:     {sleep.get('start', '?')}:00 - {sleep.get('end', '?')}:00 {'(NOW)' if in_sleep else ''}")
    print(f"{'─' * 40}\n")
    return True


def cmd_setup(args, activity):
    """Auto-discover Telegram chat ID from recent messages."""
    token, err = get_bot_token()
    if not token:
        print(f"[ERROR] {err}")
        return False

    print("Discovering your Telegram chat ID...")
    print("(Make sure you've sent at least one message to the bot)\n")

    result, err = telegram_api(token, "getUpdates", {"limit": 10})
    if err:
        print(f"[ERROR] {err}")
        return False

    if not result or not result.get("ok"):
        print("[ERROR] Could not fetch updates from Telegram.")
        return False

    updates = result.get("result", [])
    if not updates:
        print("[ERROR] No recent messages found.")
        print("   → Send a message to your Panda bot on Telegram first, then run setup again.")
        return False

    # Find the most recent DM chat ID
    for update in reversed(updates):
        msg = update.get("message", {})
        chat = msg.get("chat", {})
        chat_type = chat.get("type", "")

        if chat_type == "private":
            chat_id = chat.get("id")
            first_name = chat.get("first_name", "")
            username = chat.get("username", "")
            print(f"[OK] Found your chat!")
            print(f"   Name: {first_name}")
            print(f"   Username: @{username}")
            print(f"   Chat ID: {chat_id}")

            activity["chat_id"] = chat_id
            save_activity(activity)
            print(f"\n[OK] Chat ID saved to activity.json!")
            return True

    print("[ERROR] No private chat found. Send a DM to the bot first.")
    return False


def cmd_install_schedule(args, activity):
    """Generate a Windows Task Scheduler command to run check every hour."""
    script_path = Path(__file__).resolve()
    python_path = sys.executable

    print("To set up automatic check-ins, run this PowerShell command as Administrator:\n")

    cmd = (
        f'$action = New-ScheduledTaskAction -Execute "{python_path}" '
        f'-Argument \'"{script_path}" check\'\n'
        f'$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) '
        f'-RepetitionInterval (New-TimeSpan -Hours 1)\n'
        f'$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries '
        f'-DontStopIfGoingOnBatteries -StartWhenAvailable\n'
        f'Register-ScheduledTask -TaskName "PandaChatCheckIn" '
        f'-Action $action -Trigger $trigger -Settings $settings '
        f'-Description "Panda Chat proactive check-in monitor"'
    )

    print(cmd)
    print("\nThis will check every hour and send a Telegram message after 12h of silence.")
    print("To remove: Unregister-ScheduledTask -TaskName 'PandaChatCheckIn' -Confirm:$false")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Panda Chat proactive check-in monitor.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    subparsers.add_parser("check", help="Check inactivity and send check-in if needed")
    subparsers.add_parser("heartbeat", help="Record user activity (call on every message)")
    subparsers.add_parser("status", help="Show current activity status")
    subparsers.add_parser("setup", help="Auto-discover Telegram chat ID")
    subparsers.add_parser("install-schedule", help="Show Windows Task Scheduler setup command")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    activity, err = load_activity()
    if not activity:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(2)

    commands = {
        "check": cmd_check,
        "heartbeat": cmd_heartbeat,
        "status": cmd_status,
        "setup": cmd_setup,
        "install-schedule": cmd_install_schedule,
    }

    handler = commands.get(args.command)
    if handler:
        success = handler(args, activity)
        sys.exit(0 if success else 1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
