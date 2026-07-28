#!/usr/bin/env python3
"""Remove singular first-person copy while preserving this site's gas-netback voice."""

from __future__ import annotations

import json
import pathlib
import re


ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
FIRST_PERSON = re.compile(r"\b(i|me|my|myself)\b", re.I)


def owner_question(text: str) -> str:
    replacements = (
        (r"\bI['’]m\b", "you are"),
        (r"\bI['’]ve\b", "you have"),
        (r"\bI['’]d\b", "you would"),
        (r"\bI['’]ll\b", "you will"),
        (r"\bI don['’]t\b", "you do not"),
        (r"\bI can['’]t\b", "you cannot"),
        (r"\bmyself\b", "yourself"),
        (r"\bmy\b", "your"),
        (r"\bme\b", "you"),
        (r"\bI\b", "you"),
    )
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.I)
    text = re.sub(r"^You only own\b", "If you only own", text)
    text = re.sub(r"^You have\b", "If you have", text)
    return text[0].upper() + text[1:] if text else text


def business_narrative(text: str) -> str:
    replacements = (
        (r"\bI['’]m\b", "the gas royalty desk is"),
        (r"\bI['’]ve\b", "the gas royalty desk has"),
        (r"\bI['’]d\b", "the gas royalty desk would"),
        (r"\bI['’]ll\b", "the gas royalty desk will"),
        (r"\bmyself\b", "the gas royalty desk"),
        (r"\bmy\b", "the owner's"),
        (r"\bme\b", "the gas royalty desk"),
        (r"\bI\b", "the gas royalty desk"),
    )
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.I)
    grammar = (
        (r"\bthe gas royalty desk am\b", "the gas royalty desk is"),
        (r"\bthe gas royalty desk have\b", "the gas royalty desk has"),
        (r"\bthe gas royalty desk do\b", "the gas royalty desk does"),
        (r"\bthe gas royalty desk don['’]t\b", "the gas royalty desk does not"),
        (r"\bthe gas royalty desk ask\b", "the gas royalty desk asks"),
        (r"\bthe gas royalty desk need\b", "the gas royalty desk needs"),
        (r"\bthe gas royalty desk work\b", "the gas royalty desk works"),
        (r"\bthe gas royalty desk want\b", "the gas royalty desk wants"),
        (r"\bthe gas royalty desk look\b", "the gas royalty desk looks"),
        (r"\bthe gas royalty desk tell\b", "the gas royalty desk tells"),
        (r"\bthe gas royalty desk value\b", "the gas royalty desk values"),
        (r"\bthe gas royalty desk start\b", "the gas royalty desk starts"),
    )
    for pattern, replacement in grammar:
        text = re.sub(pattern, replacement, text, flags=re.I)
    return text


def rewrite(value, key: str = ""):
    if isinstance(value, dict):
        return {child_key: rewrite(child, child_key) for child_key, child in value.items()}
    if isinstance(value, list):
        return [rewrite(child, key) for child in value]
    if isinstance(value, str):
        return owner_question(value) if key == "question" else business_narrative(value)
    return value


def main() -> None:
    changed = 0
    failures: list[str] = []
    for path in sorted(CONTENT.rglob("*.json")):
        before = path.read_text()
        revised = rewrite(json.loads(before))
        after = json.dumps(revised, indent=2, ensure_ascii=False) + "\n"
        if after != before:
            path.write_text(after)
            changed += 1
        for match in FIRST_PERSON.finditer(after):
            failures.append(f"{path.relative_to(ROOT)}: {match.group(0)}")
    if failures:
        raise SystemExit("Singular first-person copy remains:\n" + "\n".join(failures[:40]))
    print(f"INSTITUTIONAL VOICE: PASS — {changed} content files updated; zero I/me/my/myself")


if __name__ == "__main__":
    main()
