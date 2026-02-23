#!/usr/bin/env python3
"""
Audio Core - Voice Quality Checker for Panda Chat

Validates audio files for transcription readiness:
- File existence and format
- File size limits
- Basic integrity checks (non-empty, header validation)

Usage:
    python voice_check.py <audio_file>
    python voice_check.py <audio_file> --verbose
"""

import argparse
import json
import os
import struct
import sys

SUPPORTED_EXTENSIONS = {".mp3", ".ogg", ".opus", ".wav", ".m4a", ".aac", ".caf", ".webm"}

# Magic bytes for common audio formats
MAGIC_BYTES = {
    b"\xff\xfb": "mp3",       # MP3 frame sync
    b"\xff\xf3": "mp3",       # MP3 frame sync (variant)
    b"\xff\xf2": "mp3",       # MP3 frame sync (variant)
    b"ID3":      "mp3",       # MP3 with ID3 tag
    b"OggS":     "ogg/opus",  # OGG container
    b"RIFF":     "wav",       # WAV/RIFF
    b"fLaC":     "flac",      # FLAC
    b"caff":     "caf",       # CAF (Core Audio Format)
}

MAX_SIZE_BYTES = 25 * 1024 * 1024  # 25MB (Whisper limit)
MIN_SIZE_BYTES = 100               # Minimum viable audio file


def check_magic_bytes(filepath):
    """Check file header against known audio magic bytes."""
    try:
        with open(filepath, "rb") as f:
            header = f.read(12)

        if len(header) < 4:
            return None, "File too small to identify"

        # Check each magic signature
        for magic, fmt in MAGIC_BYTES.items():
            if header[:len(magic)] == magic:
                return fmt, None

        # Check for MP4/M4A (ftyp box)
        if header[4:8] == b"ftyp":
            return "m4a/aac", None

        # Check for WebM (EBML header)
        if header[:4] == b"\x1a\x45\xdf\xa3":
            return "webm", None

        return None, "Unknown audio format"

    except IOError as e:
        return None, f"Cannot read file: {e}"


def voice_check(audio_path, verbose=False):
    """
    Validate an audio file for transcription readiness.

    Returns:
        dict with keys: valid (bool), checks (list of check results), file (metadata)
    """
    checks = []
    file_info = {}

    # 1. File existence
    if not os.path.exists(audio_path):
        checks.append({"check": "exists", "passed": False, "detail": "File not found"})
        return {"valid": False, "checks": checks, "file": {"path": audio_path}}

    checks.append({"check": "exists", "passed": True})

    # 2. File metadata
    stat = os.stat(audio_path)
    ext = os.path.splitext(audio_path)[1].lower()
    file_info = {
        "path": audio_path,
        "filename": os.path.basename(audio_path),
        "extension": ext,
        "size_bytes": stat.st_size,
        "size_kb": round(stat.st_size / 1024, 1),
    }

    # 3. Extension check
    if ext in SUPPORTED_EXTENSIONS:
        checks.append({"check": "extension", "passed": True, "detail": ext})
    else:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        checks.append({
            "check": "extension",
            "passed": False,
            "detail": f"'{ext}' not supported. Use: {supported}",
        })

    # 4. Size checks
    if stat.st_size < MIN_SIZE_BYTES:
        checks.append({
            "check": "min_size",
            "passed": False,
            "detail": f"File too small ({stat.st_size} bytes). Minimum: {MIN_SIZE_BYTES} bytes",
        })
    else:
        checks.append({"check": "min_size", "passed": True})

    if stat.st_size > MAX_SIZE_BYTES:
        max_mb = MAX_SIZE_BYTES / (1024 * 1024)
        checks.append({
            "check": "max_size",
            "passed": False,
            "detail": f"File too large ({file_info['size_kb']}KB). Max: {max_mb}MB",
        })
    else:
        checks.append({"check": "max_size", "passed": True})

    # 5. Magic bytes / format integrity
    detected_format, error = check_magic_bytes(audio_path)
    if detected_format:
        checks.append({
            "check": "format_integrity",
            "passed": True,
            "detail": f"Detected: {detected_format}",
        })
    elif error:
        checks.append({
            "check": "format_integrity",
            "passed": False,
            "detail": error,
        })
    else:
        checks.append({
            "check": "format_integrity",
            "passed": False,
            "detail": "Could not verify audio format from file header",
        })

    # Overall verdict
    all_passed = all(c["passed"] for c in checks)

    return {
        "valid": all_passed,
        "checks": checks,
        "file": file_info,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Validate audio files for transcription readiness.",
    )
    parser.add_argument("audio_file", help="Path to the audio file to check")
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed check results",
    )
    args = parser.parse_args()

    result = voice_check(args.audio_file, verbose=args.verbose)

    if args.verbose:
        print(json.dumps(result, indent=2))
    else:
        if result["valid"]:
            print(f"[OK] {result['file'].get('filename', args.audio_file)} — ready for transcription")
        else:
            failed = [c for c in result["checks"] if not c["passed"]]
            print(f"[FAIL] {result['file'].get('filename', args.audio_file)}")
            for c in failed:
                print(f"  ✗ {c['check']}: {c.get('detail', 'failed')}")
            sys.exit(1)


if __name__ == "__main__":
    main()
