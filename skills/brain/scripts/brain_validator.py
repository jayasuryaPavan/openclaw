#!/usr/bin/env python3
"""
Panda Brain — Skill Validator

ANN-based validation for skill structures.
Goes beyond the basic SKILL.md frontmatter checks (quick_validate.py)
by scoring skill quality, completeness, and adherence to best practices.

Usage:
    python brain_validator.py <skill_path>
    python brain_validator.py <skill_path> --verbose
    python brain_validator.py <skill_path> --score-only

Scoring dimensions:
  - Structure (directory layout, required files)
  - Documentation (SKILL.md quality, descriptions)
  - Scripts (existence, headers, error handling)
  - References (supporting docs, data files)
  - Overall readiness score
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

# ─── Scoring Weights ─────────────────────────────────────

WEIGHTS = {
    "skill_md_exists": 20,
    "frontmatter_valid": 10,
    "name_valid": 5,
    "description_quality": 10,
    "has_overview": 5,
    "has_workflow": 5,
    "has_resources_section": 5,
    "scripts_dir_exists": 5,
    "scripts_have_docstrings": 5,
    "scripts_have_shebangs": 3,
    "scripts_have_main_guard": 3,
    "references_dir_exists": 3,
    "references_not_empty": 3,
    "no_stale_pycache": 3,
    "all_referenced_scripts_exist": 10,
    "all_referenced_refs_exist": 5,
}

MAX_SCORE = sum(WEIGHTS.values())


def parse_frontmatter(content):
    """Extract YAML frontmatter from SKILL.md content."""
    if not content.startswith("---"):
        return None

    end = content.find("---", 3)
    if end == -1:
        return None

    fm_text = content[3:end].strip()
    result = {}
    for line in fm_text.split("\n"):
        if ":" in line:
            key, val = line.split(":", 1)
            result[key.strip()] = val.strip()

    return result


def extract_referenced_files(content):
    """Extract file references from SKILL.md (scripts/ and references/ sections)."""
    scripts = []
    refs = []

    # Look for patterns like `script_name.py` or `file.md` in resource sections
    in_scripts = False
    in_refs = False

    for line in content.split("\n"):
        line_lower = line.strip().lower()

        if "### scripts" in line_lower or "scripts/" in line_lower:
            in_scripts = True
            in_refs = False
            continue
        elif "### references" in line_lower or "references/" in line_lower:
            in_scripts = False
            in_refs = True
            continue
        elif line.startswith("##"):
            in_scripts = False
            in_refs = False
            continue

        # Extract backtick-quoted filenames
        matches = re.findall(r'`([^`]+\.\w+)`', line)
        for m in matches:
            if in_scripts:
                scripts.append(m)
            elif in_refs:
                refs.append(m)

    return scripts, refs


def validate_skill(skill_path, verbose=False):
    """
    Validate a skill directory and return a detailed score report.

    Returns:
        dict with scores, checks, and overall grade
    """
    skill_path = Path(skill_path)
    checks = []
    total_score = 0

    def check(name, passed, detail=""):
        nonlocal total_score
        weight = WEIGHTS.get(name, 0)
        score = weight if passed else 0
        total_score += score
        checks.append({
            "check": name,
            "passed": passed,
            "score": score,
            "max": weight,
            "detail": detail,
        })

    # 1. SKILL.md exists
    skill_md = skill_path / "SKILL.md"
    check("skill_md_exists", skill_md.exists())

    if not skill_md.exists():
        return _build_report(skill_path, checks, total_score)

    content = skill_md.read_text(encoding="utf-8")

    # 2. Frontmatter
    fm = parse_frontmatter(content)
    check("frontmatter_valid", fm is not None)

    # 3. Name validity
    name = fm.get("name", "") if fm else ""
    name_valid = bool(name) and re.match(r'^[a-z][a-z0-9-]*$', name) is not None
    check("name_valid", name_valid, f"name='{name}'")

    # 4. Description quality
    desc = fm.get("description", "") if fm else ""
    desc_ok = len(desc) >= 20 and "<" not in desc
    check("description_quality", desc_ok, f"len={len(desc)}")

    # 5. Content sections
    content_lower = content.lower()
    check("has_overview", "## overview" in content_lower or "## what" in content_lower)
    check("has_workflow", "## workflow" in content_lower or "## usage" in content_lower or "## how" in content_lower)
    check("has_resources_section", "## resources" in content_lower or "### scripts" in content_lower)

    # 6. Scripts directory
    scripts_dir = skill_path / "scripts"
    check("scripts_dir_exists", scripts_dir.exists() and scripts_dir.is_dir())

    if scripts_dir.exists():
        py_files = list(scripts_dir.glob("*.py"))

        # Docstrings
        has_docstrings = all(
            '"""' in f.read_text(encoding="utf-8") or "'''" in f.read_text(encoding="utf-8")
            for f in py_files if f.stat().st_size > 0
        ) if py_files else False
        check("scripts_have_docstrings", has_docstrings, f"{len(py_files)} scripts")

        # Shebangs
        has_shebangs = all(
            f.read_text(encoding="utf-8").startswith("#!/")
            for f in py_files if f.stat().st_size > 0
        ) if py_files else False
        check("scripts_have_shebangs", has_shebangs)

        # Main guards
        has_main = all(
            '__name__' in f.read_text(encoding="utf-8")
            for f in py_files if f.stat().st_size > 0
        ) if py_files else False
        check("scripts_have_main_guard", has_main)

    else:
        check("scripts_have_docstrings", False, "no scripts dir")
        check("scripts_have_shebangs", False)
        check("scripts_have_main_guard", False)

    # 7. References directory
    refs_dir = skill_path / "references"
    check("references_dir_exists", refs_dir.exists() and refs_dir.is_dir())
    if refs_dir.exists():
        ref_files = list(refs_dir.iterdir())
        check("references_not_empty", len(ref_files) > 0, f"{len(ref_files)} files")
    else:
        check("references_not_empty", False)

    # 8. No stale __pycache__
    pycache = skill_path / "scripts" / "__pycache__"
    check("no_stale_pycache", not pycache.exists())

    # 9. Referenced files exist
    referenced_scripts, referenced_refs = extract_referenced_files(content)

    all_scripts_exist = all(
        (scripts_dir / s).exists() for s in referenced_scripts
    ) if referenced_scripts and scripts_dir.exists() else (not referenced_scripts)
    missing_scripts = [s for s in referenced_scripts if scripts_dir.exists() and not (scripts_dir / s).exists()]
    check("all_referenced_scripts_exist", all_scripts_exist,
          f"missing: {missing_scripts}" if missing_scripts else f"{len(referenced_scripts)} ok")

    all_refs_exist = all(
        (refs_dir / r).exists() for r in referenced_refs
    ) if referenced_refs and refs_dir.exists() else (not referenced_refs)
    missing_refs = [r for r in referenced_refs if refs_dir.exists() and not (refs_dir / r).exists()]
    check("all_referenced_refs_exist", all_refs_exist,
          f"missing: {missing_refs}" if missing_refs else f"{len(referenced_refs)} ok")

    return _build_report(skill_path, checks, total_score)


def _build_report(skill_path, checks, total_score):
    """Build the final validation report."""
    pct = (total_score / MAX_SCORE) * 100

    if pct >= 90:
        grade = "A"
    elif pct >= 75:
        grade = "B"
    elif pct >= 60:
        grade = "C"
    elif pct >= 40:
        grade = "D"
    else:
        grade = "F"

    return {
        "skill": skill_path.name,
        "path": str(skill_path),
        "score": total_score,
        "max_score": MAX_SCORE,
        "percentage": round(pct, 1),
        "grade": grade,
        "checks": checks,
    }


def main():
    parser = argparse.ArgumentParser(description="Validate skill quality with Panda Brain.")
    parser.add_argument("skill_path", help="Path to the skill directory")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show all check details")
    parser.add_argument("--score-only", action="store_true", help="Just print the score")
    args = parser.parse_args()

    result = validate_skill(args.skill_path, verbose=args.verbose)

    if args.score_only:
        print(f"{result['grade']} ({result['percentage']}%)")
        sys.exit(0)

    if args.verbose:
        print(json.dumps(result, indent=2))
    else:
        grade = result["grade"]
        pct = result["percentage"]
        name = result["skill"]

        emoji = {"A": "🏆", "B": "✅", "C": "⚠️", "D": "❌", "F": "💀"}.get(grade, "?")

        print(f"\n{emoji} Skill: {name} — Grade: {grade} ({pct}%)")
        print(f"{'─' * 45}")

        failed = [c for c in result["checks"] if not c["passed"]]
        passed = [c for c in result["checks"] if c["passed"]]

        for c in passed:
            detail = f" ({c['detail']})" if c.get("detail") else ""
            print(f"  ✅ {c['check']}{detail}")

        if failed:
            print()
            for c in failed:
                detail = f" ({c['detail']})" if c.get("detail") else ""
                print(f"  ❌ {c['check']}{detail} [-{c['max']}pts]")

        print(f"\n  Score: {result['score']}/{result['max_score']}\n")

    sys.exit(0 if result["grade"] in ("A", "B") else 1)


if __name__ == "__main__":
    main()
