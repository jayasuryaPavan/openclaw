"""
quota_reminder.py — Gemini-3-Flash Quota Reset Notifier
========================================================
Runs in the background. Checks the Antigravity API for gemini-3-flash
resetTime, sleeps until that moment, then immediately sends the user
a Telegram message so they can trigger the new 5-hour window.
After notifying, it picks up the NEW reset time and repeats indefinitely.
"""

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
import os

# ── Google OAuth credentials ────────────────────────────────────────────────
CLIENT_ID     = os.environ.get("GOOGLE_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", "")
PROJECT_ID    = os.environ.get("GOOGLE_PROJECT_ID", "logical-skein-mjcf0")

# ── Telegram credentials ─────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID", "")   # Jayasurya's Telegram user ID

# ── Model key to watch ───────────────────────────────────────────────────────
WATCH_MODEL = "gemini-3-flash"

# ── Timings ──────────────────────────────────────────────────────────────────
POLL_INTERVAL_SECONDS  = 60      # check for new reset time every N seconds after notify
PRE_WAKE_SECONDS       = 30      # wake up N seconds early to avoid drift


def log(msg: str) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[quota-reminder {ts}] {msg}", flush=True)


def refresh_access_token() -> str:
    data = urllib.parse.urlencode({
        "client_id":     CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type":    "refresh_token",
    }).encode("utf-8")
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.load(resp)["access_token"]


def fetch_quota(access_token: str) -> dict:
    body = json.dumps({"project": PROJECT_ID}).encode("utf-8")
    req = urllib.request.Request(
        "https://cloudcode-pa.googleapis.com/v1internal:fetchAvailableModels",
        data=body, method="POST",
    )
    req.add_header("Authorization", f"Bearer {access_token}")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "antigravity/0.2.0")
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.load(resp)


def get_flash_reset_time(quota: dict) -> datetime | None:
    """Return the UTC reset datetime for gemini-3-flash, or None."""
    model_info = quota.get("models", {}).get(WATCH_MODEL, {})
    reset_str  = model_info.get("quotaInfo", {}).get("resetTime")
    if not reset_str:
        return None
    # e.g. "2026-02-28T05:05:06Z"
    return datetime.fromisoformat(reset_str.replace("Z", "+00:00"))


def send_telegram(text: str) -> None:
    payload = json.dumps({"chat_id": TELEGRAM_CHAT_ID, "text": text}).encode("utf-8")
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.load(resp)
    if not result.get("ok"):
        log(f"Telegram error: {result}")
    else:
        log("Telegram notification sent successfully.")


def main() -> None:
    log("Starting quota reminder for gemini-3-flash …")

    last_reset_time: datetime | None = None

    while True:
        try:
            token = refresh_access_token()
            quota = fetch_quota(token)
            reset_time = get_flash_reset_time(quota)

            if reset_time is None:
                log(f"{WATCH_MODEL} has no resetTime — quota may be full. Retrying in 5 min.")
                time.sleep(300)
                continue

            log(f"{WATCH_MODEL} resetTime = {reset_time.isoformat()}")

            now_utc = datetime.now(tz=timezone.utc)
            sleep_seconds = (reset_time - now_utc).total_seconds() - PRE_WAKE_SECONDS

            if sleep_seconds > 0:
                log(f"Sleeping {sleep_seconds:.0f}s until ~{reset_time.isoformat()} …")
                time.sleep(sleep_seconds)

            # Double-check we haven't already notified for THIS reset window
            if reset_time == last_reset_time:
                log("Reset time unchanged — user hasn't triggered a new session yet. Polling.")
                time.sleep(POLL_INTERVAL_SECONDS)
                continue

            last_reset_time = reset_time

            # Wait the remaining pre-wake buffer
            remaining = (reset_time - datetime.now(tz=timezone.utc)).total_seconds()
            if remaining > 0:
                time.sleep(remaining)

            # 🔔 Notify the user
            msg = (
                "🔔 Gemini-3-Flash quota reset అయింది పండు!\n"
                "ఒక్క message send చేయి — new 5-hour window start అవుతుంది."
            )
            send_telegram(msg)

        except urllib.error.URLError as exc:
            log(f"Network error: {exc}. Retrying in 2 min.")
            time.sleep(120)
        except Exception as exc:
            log(f"Unexpected error: {exc}. Retrying in 5 min.")
            time.sleep(300)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("Stopped.")
        sys.exit(0)
