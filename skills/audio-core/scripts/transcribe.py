#!/usr/bin/env python3
"""
Audio Core - Voice Message Transcriber for Panda Chat

Transcribes audio files to text. Currently uses a rule-based mock.
In production, swap the mock with Whisper or Google STT.

Usage:
    python transcribe.py <audio_file>
    python transcribe.py <audio_file> --format json
    python transcribe.py <audio_file> --text-only

Model: Whisper-v3 (Mock — rule-based for dev/testing)
"""

import argparse
import json
import os
import sys

# Supported audio extensions (must match audio_formats.md)
SUPPORTED_EXTENSIONS = {".mp3", ".ogg", ".opus", ".wav", ".m4a", ".aac", ".caf", ".webm"}


def get_file_info(audio_path):
    """Get basic file metadata."""
    stat = os.stat(audio_path)
    ext = os.path.splitext(audio_path)[1].lower()
    return {
        "path": audio_path,
        "filename": os.path.basename(audio_path),
        "extension": ext,
        "size_bytes": stat.st_size,
        "size_kb": round(stat.st_size / 1024, 1),
    }


def mock_transcribe(audio_path):
    """
    Mock transcription engine.

    In production, replace this function body with:
        import whisper
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        return result["text"], result.get("language", "en"), 0.95
    """
    filename = os.path.basename(audio_path).lower()
    ext = os.path.splitext(filename)[1]

    # Simulate different transcriptions based on file characteristics
    if "voice" in filename or "voice_note" in filename:
        transcript = "Hi Panda, how are you today?"
        language = "en"
    elif ext in (".ogg", ".opus"):
        # Telegram sends voice as .ogg/.opus
        transcript = "This is a Telegram voice message."
        language = "te-Latn"  # Tenglish
    elif ext == ".caf":
        # iOS voice memos
        transcript = "Voice memo from iPhone."
        language = "en"
    elif ext == ".webm":
        # Browser/web recording
        transcript = "Web recording transcription."
        language = "en"
    else:
        transcript = "Audio content detected."
        language = "en"

    return transcript, language, 0.92


def transcribe(audio_path, text_only=False):
    """Transcribe an audio file and return structured result."""
    # Validate file exists
    if not os.path.exists(audio_path):
        return {"error": f"File not found: {audio_path}"}

    # Validate extension
    ext = os.path.splitext(audio_path)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        return {"error": f"Unsupported format '{ext}'. Supported: {supported}"}

    # Get file info
    file_info = get_file_info(audio_path)

    # Check file size (max 25MB for Whisper)
    max_size = 25 * 1024 * 1024
    if file_info["size_bytes"] > max_size:
        return {"error": f"File too large ({file_info['size_kb']}KB). Max: 25MB"}

    # Transcribe
    transcript, language, confidence = mock_transcribe(audio_path)

    if text_only:
        return {"text": transcript}

    return {
        "file": file_info,
        "transcription": {
            "text": transcript,
            "language": language,
            "confidence": round(confidence, 2),
        },
        "model": "Whisper-v3 (Mock)",
    }


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe audio files to text.",
    )
    parser.add_argument("audio_file", help="Path to the audio file")
    parser.add_argument(
        "--text-only",
        action="store_true",
        help="Output only the transcribed text (no metadata)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="json",
        help="Output format (default: json)",
    )
    args = parser.parse_args()

    result = transcribe(args.audio_file, text_only=args.text_only)

    if args.format == "text" or args.text_only:
        text = result.get("text") or result.get("transcription", {}).get("text")
        if text:
            print(text)
        else:
            print(result.get("error", "Transcription failed"))
            sys.exit(1)
    else:
        print(json.dumps(result, indent=2))
        if "error" in result:
            sys.exit(1)


if __name__ == "__main__":
    main()
