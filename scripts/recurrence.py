#!/usr/bin/env python3
r"""Mechanical recurrence signals from git history.

Reads a pre-generated git log dump so it stays read-only, offline, and dependency-free.

    git log --no-merges --format="C%H|%ct|%s" --name-only > commits.txt
    git log -G'#\[test\]|#\[cfg\(test\)\]|def test_|describe\(|it\(' --format=%H > test-touch.txt
    python scripts/recurrence.py commits.txt test-touch.txt > 03-recurrence.md

Signals:
  R1 quick-remedy attribution  each fix attributed to the nearest earlier non-fix
                               commit it shares a file with, inside WINDOW_HOURS
  R2 fix storms                runs of consecutive fix commits (a review burst)
  R3 fix-cluster files         files touched by >= MIN_FIXES fix commits
  R4 repeat-admitting messages fix subjects that say "again", "still", "regression"
  R5 fix plus test             fix commits that also rewrite a test
  risk table                   fix ratio per file

Why attribution and not pairing: on a repo with a burst of fixes, every fix is inside
the window of every other fix, so pairwise output collapses into one meaningless
transitive cluster. Attributing each fix to exactly one earlier non-fix commit keeps
one row per story.
"""

import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

WINDOW_HOURS = 72
MIN_FIXES = 3
MIN_STORM = 5
MAX_ROWS = 25

FIX_RE = re.compile(r"^(fix|bugfix|hotfix)\b", re.I)
REPEAT_RE = re.compile(
    r"\b(again|still|same|also|forgot|forgotten|missing|regression|"
    r"once more|second time|repeat|reoccur|back to)\b",
    re.I,
)
TEST_RE = re.compile(r"(^|/)(tests?|spec|__tests__)/|(test_|_test|\.test\.|\.spec\.)", re.I)
NOISE_RE = re.compile(
    r"(^|/)(node_modules|vendor|dist|build|target|coverage|\.venv)/"
    r"|\.(lock|min\.js|map)$"
    r"|\.(md|txt|json)$",
    re.I,
)


def read_dump(path):
    """Read the dump regardless of encoding.

    PowerShell 5.1 `>` writes UTF-16LE, which silently produces zero parsed commits if
    the reader assumes UTF-8. Git Bash and POSIX shells write UTF-8.
    """
    with open(path, "rb") as fh:
        raw = fh.read()
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        text = raw.decode("utf-16", errors="replace")
    else:
        text = raw.decode("utf-8", errors="replace")
    return text.replace("\x00", "")


def parse(path):
    """Parse a `git log --format=C<sha>|<ct>|<subject> --name-only` dump."""
    commits = []
    cur = None
    for line in read_dump(path).splitlines():
        if line.startswith("C") and "|" in line:
            parts = line[1:].split("|", 2)
            if len(parts) == 3 and re.fullmatch(r"[0-9a-f]{7,40}", parts[0]):
                if cur:
                    commits.append(cur)
                cur = {"sha": parts[0], "ts": int(parts[1]), "subj": parts[2], "files": []}
                continue
        if line.strip() and cur is not None and not NOISE_RE.search(line):
            cur["files"].append(line.strip())
    if cur:
        commits.append(cur)
    return commits


def when(ts):
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d %H:%M")


def r1_attribution(w, commits, fixes):
    window = WINDOW_HOURS * 3600
    w(f"## R1 - Quick-remedy attribution (fix within {WINDOW_HOURS}h of a non-fix commit)")
    w("")
    w("Each fix is attributed to the nearest earlier NON-fix commit it shares a file")
    w("with. A commit that needed several follow-up fixes is the signal. Read that")
    w("commit's diff to find what it omitted.")
    w("")
    repairs = defaultdict(list)
    orphan_fixes = []
    for b in fixes:
        if not b["files"]:
            orphan_fixes.append(b)
            continue
        bset = set(b["files"])
        best = None
        for a in commits:
            if a["ts"] >= b["ts"] or b["ts"] - a["ts"] > window:
                continue
            if FIX_RE.match(a["subj"]):
                continue
            if bset & set(a["files"]):
                best = a  # keep walking: commits are sorted, so last hit is nearest
        if best is None:
            orphan_fixes.append(b)
        else:
            repairs[best["sha"]].append((b, bset & set(best["files"])))

    by_sha = {c["sha"]: c for c in commits}
    rows = sorted(repairs.items(), key=lambda kv: (-len(kv[1]), by_sha[kv[0]]["ts"]))
    if not rows:
        w("No fix was attributable to an earlier non-fix commit. The history has no")
        w("'landed a change, then repaired it' pattern.")
        w("")
        return
    w("| follow-up fixes | earlier commit | span (h) | most-shared files |")
    w("| --- | --- | --- | --- |")
    for sha, items in rows[:MAX_ROWS]:
        a = by_sha[sha]
        hours = sorted((b["ts"] - a["ts"]) / 3600 for b, _ in items)
        span = f"{hours[0]:.1f}" if len(hours) == 1 else f"{hours[0]:.1f}-{hours[-1]:.1f}"
        hot = Counter()
        for _, shared in items:
            hot.update(shared)
        top = ", ".join(f"`{p}`" for p, _ in hot.most_common(4))
        w(f"| {len(items)} | `{sha[:9]}` {a['subj'][:52]} | {span} | {top} |")
    w("")
    w("### The fixes behind the worst offenders")
    w("")
    for sha, items in rows[:8]:
        a = by_sha[sha]
        w(f"- `{sha[:9]}` {when(a['ts'])} {a['subj'][:80]}")
        for b, _ in items[:10]:
            w(f"  - `{b['sha'][:9]}` +{(b['ts'] - a['ts']) / 3600:.1f}h  {b['subj'][:76]}")
    if orphan_fixes:
        w("")
        w(f"### Unattributed fixes ({len(orphan_fixes)})")
        w("")
        w("No earlier non-fix commit inside the window shares a file. Usually a fix")
        w("storm (see R2) or a fix for code older than the window.")
        w("")
        for b in orphan_fixes[:15]:
            w(f"- `{b['sha'][:9]}` {when(b['ts'])} {b['subj'][:76]}")
    w("")


def r2_fix_storms(w, commits, fixes):
    fix_shas = {c["sha"] for c in fixes}
    w(f"## R2 - Fix storms (>= {MIN_STORM} consecutive fix commits)")
    w("")
    w("A run of fixes with no intervening feature or refactor commit. The work landed")
    w("before it was ready. Ask what review or test step was skipped.")
    w("")
    runs = []
    run = []
    for c in commits:
        if c["sha"] in fix_shas:
            run.append(c)
        else:
            if len(run) >= MIN_STORM:
                runs.append(run)
            run = []
    if len(run) >= MIN_STORM:
        runs.append(run)
    if not runs:
        w("None found.")
        w("")
        return
    for run in runs:
        span = (run[-1]["ts"] - run[0]["ts"]) / 3600
        w(f"- **{len(run)} consecutive fixes** over {span:.1f}h: "
          f"`{run[0]['sha'][:9]}` .. `{run[-1]['sha'][:9]}` ({when(run[0]['ts'])})")
        w(f"  - first: {run[0]['subj'][:78]}")
        w(f"  - last:  {run[-1]['subj'][:78]}")
    w("")


def r3_fix_clusters(w, fixes):
    w(f"## R3 - Fix-cluster files (>= {MIN_FIXES} fix commits)")
    w("")
    counts = Counter()
    for c in fixes:
        counts.update(set(c["files"]))
    clusters = [(p, n) for p, n in counts.most_common() if n >= MIN_FIXES]
    if not clusters:
        w(f"No file has {MIN_FIXES} or more fix commits.")
        w("")
        return
    w("| fixes | path |")
    w("| --- | --- |")
    for p, n in clusters[:30]:
        w(f"| {n} | `{p}` |")
    w("")


def r4_repeats(w, fixes):
    w("## R4 - Fix commits that admit a repeat")
    w("")
    repeats = [c for c in fixes if REPEAT_RE.search(c["subj"])]
    if not repeats:
        w("None found.")
        w("")
        return
    for c in repeats:
        w(f"- `{c['sha'][:9]}` ({when(c['ts'])}) {c['subj']}")
    w("")


def r5_fix_plus_test(w, fixes, test_touch):
    w("## R5 - Fix commits that also changed test code")
    w("")
    w("Two detectors are combined:")
    w("  1. the commit touches a separate test file (`test_*`, `*.spec.*`, `tests/`)")
    w("  2. the commit's diff adds or removes a test marker (`#[test]`, `def test_`,")
    w("     `describe(`, `it(`) - this catches colocated and inline tests")
    w("")
    if not fixes:
        w("No fix commits.")
        w("")
        return
    by_file = [c for c in fixes if any(TEST_RE.search(f) for f in c["files"])]
    by_diff = [c for c in fixes if c["sha"] in test_touch]
    combined = {c["sha"]: c for c in by_file + by_diff}
    w(f"{len(combined)} of {len(fixes)} fix commits changed test code "
      f"({len(by_file)} by file path, {len(by_diff)} by diff marker).")
    w("")
    if not test_touch and not by_file:
        w("No test markers supplied and no test paths matched. This is only reliable if")
        w("you passed the `git log -G` marker file described in the analysis playbook.")
        w("")
    w("A low number means fixes ship without a regression test. A non-zero number means")
    w("the test was missing or asserted the wrong thing.")
    w("")
    for sha, c in list(combined.items())[:25]:
        tests = [f for f in c["files"] if TEST_RE.search(f)]
        marker = " (diff marker)" if sha in test_touch and not tests else ""
        w(f"- `{sha[:9]}` {c['subj'][:70]}{marker}")
        if tests:
            w(f"  - {', '.join('`' + f + '`' for f in tests[:4])}")
    w("")


def risk_table(w, commits, fixes):
    w("## File activity (fix ratio)")
    w("")
    counts = Counter()
    for c in fixes:
        counts.update(set(c["files"]))
    total = Counter()
    for c in commits:
        total.update(set(c["files"]))
    rows = [(counts[p] / t, counts[p], t, p) for p, t in total.items() if counts.get(p)]
    rows.sort(key=lambda r: (-r[0], -r[1]))
    w("| fix ratio | fixes | total | path |")
    w("| --- | --- | --- | --- |")
    for ratio, f, t, p in rows[:30]:
        w(f"| {ratio:.2f} | {f} | {t} | `{p}` |")
    w("")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # pragma: no cover - older interpreters
        pass
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    commits = parse(sys.argv[1])
    test_touch = set()
    if len(sys.argv) == 3:
        test_touch = {
            line.strip()
            for line in read_dump(sys.argv[2]).splitlines()
            if re.fullmatch(r"[0-9a-f]{7,40}", line.strip())
        }
    if not commits:
        sys.exit(
            f"No commits parsed from {sys.argv[1]}. Regenerate the dump with:\n"
            '  git log --no-merges --format="C%H|%ct|%s" --name-only'
        )
    commits.sort(key=lambda c: c["ts"])
    fixes = [c for c in commits if FIX_RE.match(c["subj"])]

    out = []
    w = out.append
    w("# Recurrence signals")
    w("")
    w(f"Analyzed {len(commits)} commits; {len(fixes)} are fix commits "
      f"({100 * len(fixes) // max(len(commits), 1)}%).")
    w("")
    w(f"Window: {WINDOW_HOURS}h. Thresholds: fix-cluster >= {MIN_FIXES}, "
      f"fix-storm >= {MIN_STORM}.")
    w("")
    r1_attribution(w, commits, fixes)
    r2_fix_storms(w, commits, fixes)
    r3_fix_clusters(w, fixes)
    r4_repeats(w, fixes)
    r5_fix_plus_test(w, fixes, test_touch)
    risk_table(w, commits, fixes)
    print("\n".join(out))


if __name__ == "__main__":
    main()
