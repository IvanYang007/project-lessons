#!/usr/bin/env python3
r"""Check a PROJECT_LESSONS.md against the BLOCKING gates in SKILL.md Phase 7.

    python scripts/check_output.py PROJECT_LESSONS.md [project-lessons.json]

Exit code 0 = every gate passed. 1 = at least one BLOCKING gate failed.

The gates are described in prose in SKILL.md. This makes them enforceable, so a run
cannot report success while violating its own contract. Deliberately regex-based: a
Markdown document does not need a parser, it needs a tripwire.
"""

import json
import re
import sys

REQUIRED_SECTIONS = [
    "Executive summary",
    "Lessons learned from past commits",
    "Project-specific implementation rules",
    "Known risk areas",
    "Safe-change checklist",
    "Examples from commit history",
]

# Generic advice that could be pasted into any repository unchanged.
BANNED = [
    r"\bwrite clean code\b",
    r"\bfollow best practices\b",
    r"\bbe careful\b",
    r"\bkeep functions small\b",
    r"\bavoid duplication\b",
    r"\bmake sure (?:the )?code is (?:good|quality)\b",
    r"\bconsider (?:using|adding|refactoring)\b",
    r"\byou (?:may|might) want to\b",
    r"\btry to\b",
    r"\bwhere possible\b",
]

SECRETS = [
    (r"sk-[A-Za-z0-9]{20,}", "OpenAI-style key"),
    (r"sk-ant-[A-Za-z0-9_-]{20,}", "Anthropic key"),
    (r"gh[pousr]_[A-Za-z0-9]{20,}", "GitHub token"),
    (r"AKIA[0-9A-Z]{16}", "AWS access key id"),
    (r"xox[bpras]-[A-Za-z0-9-]{10,}", "Slack token"),
    (r"AIza[0-9A-Za-z_-]{30,}", "Google API key"),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "private key block"),
    (r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}", "JWT"),
]

HASH_RE = re.compile(r"\b[0-9a-f]{7,40}\b")
GRADE_RE = re.compile(r"\[(observed|inferred|weak)\]")
LESSON_RE = re.compile(r"^###\s+L\d+\.", re.M)
CHECK_RE = re.compile(r"^- \[[ x]\]", re.M)


def check_sections(text, fails, warns):
    found = [s for s in REQUIRED_SECTIONS if re.search(r"^##\s+" + re.escape(s) + r"\s*$", text, re.M)]
    missing = [s for s in REQUIRED_SECTIONS if s not in found]
    if missing:
        fails.append(f"missing required section(s): {', '.join(missing)}")
    positions = [text.find(f"## {s}") for s in found]
    if positions != sorted(positions):
        warns.append("required sections are out of the documented order")


def check_lessons(text, fails, warns):
    bodies = re.split(r"^###\s+L\d+\.", text, flags=re.M)[1:]
    if not bodies:
        warns.append("no '### L<n>.' lesson entries found")
        return
    for i, body in enumerate(bodies, 1):
        head = body.split("\n", 1)[0]
        if not GRADE_RE.search(head):
            fails.append(f"L{i} has no [observed]/[inferred]/[weak] grade in its heading")
        if not HASH_RE.search(body):
            fails.append(f"L{i} cites no commit hash")
    if len(bodies) > 20:
        warns.append(f"{len(bodies)} lessons exceeds the cap of 20")


def check_banned(text, fails, warns):
    hits = []
    for pat in BANNED:
        for m in re.finditer(pat, text, re.I):
            line = text[: m.start()].count("\n") + 1
            hits.append(f"line {line}: '{m.group(0)}'")
    if hits:
        for h in hits[:10]:
            fails.append(f"banned generic phrasing - {h}")
        if len(hits) > 10:
            fails.append(f"... and {len(hits) - 10} more generic phrases")


def check_secrets(text, fails, warns):
    for pat, label in SECRETS:
        if re.search(pat, text):
            fails.append(f"possible {label} in the document - redact before delivering")


def check_size(text, fails, warns):
    lines = text.count("\n") + 1
    if lines < 80:
        fails.append(f"{lines} lines - under 80 means the analysis is too thin")
    elif lines > 400:
        fails.append(f"{lines} lines - over 400 means transcription, not synthesis")
    elif lines > 340:
        warns.append(f"{lines} lines - approaching the 400 cap")


def check_checklist(text, fails, warns):
    items = CHECK_RE.findall(text)
    n = len(items)
    if n < 5:
        fails.append(f"safe-change checklist has {n} items; the gate requires 5-12")
    elif n > 12:
        fails.append(f"safe-change checklist has {n} items; the gate caps it at 12")


def check_risk_paths(text, fails, warns, repo_root):
    """Every path named in a risk table should exist, or be labelled removed."""
    import os

    if not repo_root or not os.path.isdir(repo_root):
        warns.append("repo root not supplied; skipped the risk-path existence check")
        return
    section = re.search(r"## Known risk areas(.*?)(?=\n## )", text, re.S)
    if not section:
        return
    removed = re.search(r"### Removed and abandoned work(.*?)(?=\n### |\n## )", text, re.S)
    removed_text = removed.group(1) if removed else ""
    missing = []
    for path in set(re.findall(r"`([\w./+-]+/[\w./+-]+)`", section.group(1))):
        if path in removed_text or path.startswith(("docs/", ".scratch/")):
            continue
        if not os.path.exists(os.path.join(repo_root, path)):
            missing.append(path)
    if missing:
        warns.append(f"risk-area path(s) not in the tree: {', '.join(sorted(missing)[:5])}")


def check_json(path, text, fails, warns):
    if not path:
        warns.append("no JSON mirror supplied; --json gate not checked")
        return
    try:
        data = json.load(open(path, encoding="utf-8"))
    except Exception as exc:
        fails.append(f"JSON mirror unreadable: {exc}")
        return
    if data.get("schema") != "project-lessons/v1":
        fails.append("JSON mirror schema is not 'project-lessons/v1'")
    ids = [r.get("id") for r in data.get("rules", [])]
    if len(ids) != len(set(ids)):
        fails.append("JSON rule ids are not unique")
    bad = [r.get("id") for r in data.get("rules", []) if not r.get("evidence")]
    if bad:
        fails.append(f"JSON rule(s) with no evidence hashes: {', '.join(map(str, bad))}")
    bad = [r.get("id") for r in data.get("rules", []) if r.get("grade") not in ("observed", "inferred", "weak")]
    if bad:
        fails.append(f"JSON rule(s) with a bad grade: {', '.join(map(str, bad))}")
    n = len(data.get("checklist", []))
    if not 5 <= n <= 12:
        fails.append(f"JSON checklist has {n} items; the gate requires 5-12")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    md = sys.argv[1]
    js = sys.argv[2] if len(sys.argv) > 2 else None
    repo_root = sys.argv[3] if len(sys.argv) > 3 else None
    text = open(md, encoding="utf-8", errors="replace").read()

    fails, warns = [], []
    check_sections(text, fails, warns)
    check_lessons(text, fails, warns)
    check_banned(text, fails, warns)
    check_secrets(text, fails, warns)
    check_size(text, fails, warns)
    check_checklist(text, fails, warns)
    check_risk_paths(text, fails, warns, repo_root)
    check_json(js, text, fails, warns)

    print(f"checking {md}")
    print(f"  lines: {text.count(chr(10)) + 1}")
    print(f"  lessons: {len(LESSON_RE.findall(text))}, "
          f"checklist: {len(CHECK_RE.findall(text))}")
    if warns:
        print("\nWARNING")
        for w in warns:
            print(f"  - {w}")
    if fails:
        print("\nBLOCKING")
        for f in fails:
            print(f"  - {f}")
        print(f"\nFAIL: {len(fails)} blocking gate(s)")
        return 1
    print("\nPASS: all blocking gates")
    return 0


if __name__ == "__main__":
    sys.exit(main())
