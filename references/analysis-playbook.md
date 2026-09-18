# Analysis playbook

Complete command reference, one section per signal. All commands are read-only.

Set `N` for "how far back to look". Default: 500 commits, or the full history if
shorter. Long histories: prefer `--since` over `-n` so the window is time-based and
comparable across phases.

```bash
git rev-list --count HEAD                 # is the repo longer than N?
git log --oneline -n 500 > /dev/null      # sanity check
```

Shell legend: **P** = POSIX / Git Bash / macOS / Linux. **W** = Windows PowerShell 5.1.

---

## 0. Preflight

```bash
git rev-parse --show-toplevel
git rev-parse --short HEAD
git log -1 --format=%cI
git log --reverse --format=%cI | head -1
git rev-list --count --all
git ls-files | wc -l
git status --porcelain
git remote -v
```

Windows:

```powershell
git rev-parse --show-toplevel
(git rev-list --count --all); (git ls-files).Count; (git status --porcelain).Count
```

If a `PROJECT_LESSONS.md` exists, this is a refresh. Read its recorded head sha from
`project-lessons.json`.

---

## 0.2 Prior documentation

Run this before any synthesis. A repo that already documents its own decisions and
recurring faults will otherwise be duplicated, and the copy will drift.

```bash
git ls-files | rg -i 'recurring|known.?issues|lessons|troubleshoot|postmortem|decisions?\.md|code.?review|threat|invariants|contributing|architecture|security'
git ls-files -- '*/adr/*' '*/decisions/*' '.scratch/*' '*/issues/*'
```

Also check the default agent-instruction files, which are often the densest prior source:

```bash
ls -a | rg -i 'agents\.md|claude\.md|gemini\.md|cursorrules|windsurfrules|copilot-instructions'
```

For each file found, record: what it claims, which claim has a commit behind it, which
claim the history contradicts, and which claim a later commit made stale.

A worked example of why this matters: `countUp` carried `docs/RECURRING_ISSUES.md` with
10 documented defects, their root causes, hard invariants, and a 12-item pre-commit
checklist. The correct output for that repo cites that document, grades each of its
claims against the history, and reports the one claim the history contradicts — not a
fresh 300-line rewrite of it.

---

## 1. Survey

### 1.1 Commit subjects (used many times later)

```bash
git log --no-merges --format="C%H|%ct|%s" --name-only > .project-lessons-work/commits.txt
```

`C` is the record marker. The script in `scripts/recurrence.py` parses this exact shape.

### 1.2 Commit-style convention

```bash
# P
git log --pretty=format:"%s" | grep -oE "^[a-zA-Z]+(\([^)]*\))?!?:" | sort | uniq -c | sort -rn | head -15
# W
git log --pretty=format:"%s" | Select-String -Pattern '^[a-zA-Z]+(\([^)]*\))?!?:' -AllMatches |
  ForEach-Object { $_.Matches.Value } | Group-Object | Sort-Object Count -Descending |
  Select-Object -First 15 Count, Name
```

Also check whether bodies exist and how long they are:

```bash
git log --format="%H %b" --no-merges | grep -c "^[0-9a-f]\{7,\} $"   # empty bodies
```

### 1.3 Churn

```bash
# P
git log --pretty=format: --name-only | grep -v '^$' | sort | uniq -c | sort -rn | head -30
# W
git log --pretty=format: --name-only | Where-Object { $_ } | Group-Object |
  Sort-Object Count -Descending | Select-Object -First 30 Count, Name
```

**Optional refinement — weight commits by significance.** Raw churn treats a typo fix and
a reviewed, squashed feature merge as equal. If the repository uses squash-merge pull
requests, weight them so a hotspot reflects durability rather than editing volume
(technique from `code-archaeologist`):

| Commit shape | Weight | Detection |
| --- | --- | --- |
| Squashed PR merge | 1.0 | subject ends `(#<n>)`, or `Merge pull request #<n>` |
| Regular commit | 0.5 | default |
| Dev-loop / WIP | 0.1 | `wip`, `tmp`, `debug`, `typo`, `oops`, `revert`, or `fixup!` in the subject |

```bash
# how many commits look like squashed PR merges
git log --pretty=format:"%s" | rg -c '\(#[0-9]+\)$'
# how many look like dev-loop noise
git log --pretty=format:"%s" | rg -ci '\b(wip|tmp|debug|typo|oops|fixup!)\b'
```

Apply this **only when the condition holds**, and state in Analysis notes whether you
did. On a single-author repository built in one session (papervault: 53% of commits are
`fix:`), the fixes are the real work and weighting them down would delete the signal.
Weighting is a correction for review-process noise, not a general improvement.

### 1.4 Bus factor

```bash
git shortlog -sn --no-merges | head -20
git log --format="%an" | sort | uniq -c | sort -rn | head -10
```

One author above 80% is a bus factor of one. Note it: the document's authority depends
on whether anyone else can confirm it.

### 1.5 Age and lanes

```bash
git log --date=format:%Y-%m --format=%ad | sort | uniq -c    # commits per month
git tag --sort=-creatordate | head -10                        # release cadence
git log --merges --oneline | head -10                         # PR workflow?
```

---

## 2. Removals and abandoned work

### 2.0 Committed secrets (run this first)

A deleted credential is still in the packfile. Deleting a file in a later commit does not
remove it from history; only `git filter-repo` or a fresh repository does.

```bash
# every path ever ADDED, filtered to secret-shaped names
git log --pretty=format: --diff-filter=A --name-only \
  | rg -v '^$' | sort -u \
  | rg -i 'passw|secret|credential|\.env|token|apikey|api[_-]?key|\.pem|\.jks|\.keystore|id_rsa|\.pfx|key\.txt'
```

For each hit:

```bash
git log --all --oneline -- "<path>"                    # added, then removed
git rev-list --all --objects | rg --fixed-strings "<path>"   # still reachable?
git remote -v                                          # any remote to leak to?
```

Record path, adding commit, removing commit, reachability, and remote presence.
**Never read or print the value.** Read the commit only far enough to confirm it exists.

Report template:

```
CREDENTIAL IN HISTORY
  path:            keystore/keystore-pass.txt
  added:           32f6f36   (initial commit)
  removed:         625f2c3   (later commit; file no longer in tree)
  still reachable: yes - blob present in `git rev-list --all --objects`
  remote:          none configured, so not yet exposed
  action:          rotate the credential, then purge history before any public push
```

Never attempt the purge yourself. That is the owner's decision, and a botched
`filter-repo` run destroys the repository.

**Note:** a committed keystore is not always an active exposure. Check whether the file
still exists in the tree, whether `.gitignore` covers it, and whether a remote exists.
All three answers belong in the report.

### 2.1 Every deleted path, by deletion count

```bash
git log --pretty=format:"C%H" --name-only --diff-filter=D | grep -v '^C' | grep -v '^$' |
  sort | uniq -c | sort -rn | head -40
```

### 2.2 Removal-shaped commits

```bash
git log --oneline --grep='revert\|drop\|remove\|delete\|undo\|rollback\|strip\|deprecate' -i | head -40
git log --oneline --grep='^Revert ' | head -30
```

### 2.3 Reconstruct a lifecycle

```bash
git log --oneline --follow -- "src/notifications"
git log --diff-filter=A --format="%h %cI %s" -- "<path>"   # when added
git log --diff-filter=D --format="%h %cI %s" -- "<path>"   # when deleted
git log --diff-filter=D -1 --format=%H -- "<path>" | xargs -I{} git show -s --format="%H%n%s%n%n%b" {}
```

### 2.4 Dependency churn (libraries tried and dropped)

```bash
# P
git log --pretty=format: --name-only -- '*lock*' '*package.json' '*requirements*.txt' '*Cargo.toml' '*go.mod' |
  grep -v '^$' | sort -u
git log --oneline -S'"winston"' -- package.json | head     # when a dep entered or left
```

`git log -S"<string>"` is the strongest tool in this phase: it finds the exact commits
that added or removed a named thing.

### 2.5 Files that oscillate (added, deleted, added)

```bash
git log --pretty=format:"C%H" --name-status | awk '
  /^C/ { sha=substr($0,2,9); next }
  $1=="A" { adds[$2]++; last_add[$2]=sha }
  $1=="D" { dels[$2]++ ; if (last_add[$2]!="") osc[$2]++ }'
```

Simpler and usually enough:

```bash
git log --pretty=format:"C%H" --name-only --diff-filter=D | grep -v '^C' | grep -v '^$' |
  sort | uniq -c | sort -rn | head -20
```

Any path appearing in 2 or more deletion commits oscillated. Read both arcs.

---

## 3. Recurrence

### 3.1 Generate the dump and run the script

```bash
git log --no-merges --format="C%H|%ct|%s" --name-only > .project-lessons-work/commits.txt
# commits whose DIFF adds or removes a test marker (catches colocated/inline tests)
git log -G'#\[test\]|#\[cfg\(test\)\]|def test_|describe\(|it\(' --format=%H \
  > .project-lessons-work/test-touch.txt
python scripts/recurrence.py .project-lessons-work/commits.txt \
  .project-lessons-work/test-touch.txt > .project-lessons-work/03-recurrence.md
```

The script emits R1 (quick-remedy attribution), R2 (fix storms, with zero-span runs
labelled `batch`), R3 (fix-cluster files), R4 (repeat-admitting messages), R5 (fix +
test), R6 (recurrence by topic), and a fix-ratio table.

### 3.2 Topic probes beat unigrams for themes spread across synonyms

R6 clusters subject tokens. That finds lexically stable topics. It undersells a theme
expressed with varied words.

Worked example: on a 68-contributor repository, R6 reported `windows` in 5 fix commits.
An explicit probe on the same history found **25 commits** (36% of all fixes), because
the theme appeared as `windows`, `powershell`, `CRLF`, `portable`, `$env:`,
`USERPROFILE` and `python3` across different commits. On the same repository, R1
quick-remedy attribution could place only 18 of 70 fixes, because a squash-merged fix
answers an issue, not the merge that introduced the problem.

```bash
# build the keyword set from symptoms you noticed in R3 and R5, then probe
git log --oneline -i --grep='<symptom1>\|<symptom2>\|<symptom3>' | wc -l
git log --oneline -i --grep='<symptom1>\|<symptom2>\|<symptom3>' | head -40
```

Run **both** and report both. If the probe finds far more than the unigram count, say so
— that gap is itself the finding: the team has one problem expressed many ways.

Seed probes for defect classes that are library-agnostic:

| Class | Probe |
| --- | --- |
| Platform | `windows\|powershell\|cross-platform\|portable\|CRLF\|BOM\|USERPROFILE` |
| Environment | `env\|config dir\|XDG\|HOME\|CI only\|local only\|works on my` |
| Concurrency | `race\|deadlock\|hang\|freeze\|timeout\|flaky` |
| Data | `migrat\|schema\|backfill\|corrupt\|orphan\|encoding` |
| Dependency | `version\|drift\|align\|manifest\|lockfile` |
| Shell | `exec\|spawn\|quoting\|path separator\|interpreter` |

**Why R5 needs the second file.** Detecting tests by path alone misses colocated and
inline tests - Rust `#[cfg(test)] mod tests`, Go `*_test.go` in the same package,
Python `def test_` inside a module, Jest `describe()` inside a component file. Passing
the `-G` marker list fixes that. Validated on a Rust repo: path-only reported 0 of 35
fix commits as test-touching; the diff marker found 7 of 35.

### 3.3 Git `--grep` uses BRE, not ERE

`git log --grep` treats the pattern as basic regular expression, where `|` is a
**literal** pipe. Two correct forms:

```bash
git log --grep='revert\|drop\|remove' -i        # escape the alternation
git log -E --grep='revert|drop|remove' -i      # or request extended regex
```

`--grep='a|b'` silently matches the literal text `a|b` and returns nothing. `-G` and
`-S` behave the same way.

### 3.4 Thresholds

| Signal | Threshold | Why |
| --- | --- | --- |
| R1 quick-remedy window | 72 hours | Wen et al. use "quick"; wider windows drift into unrelated work |
| R1 shared files | >= 1 | Shared file is the evidence the earlier change is implicated |
| R3 fix-cluster | >= 3 fix commits | Two is common; three separates a pattern |
| R4 text match | one hit is enough to read | The message itself is the admission |

Tune the window for the project: a repo with one commit a week needs a wider window.
State the window you used in the output.

### 3.5 Manual reading of R4 hits

For each repeat-admitting fix:

```bash
git show <sha>                    # the fix
git show <sha>^                   # the state before
git log -1 --format=%s $(git log --format=%H -1 --before=<date> -- <file>)   # what came before
```

Answer only one question: **what did the author know the second time that they did not
know the first time?** Write that as the rule.

### 3.6 Recurrence by symptom, not by file

A recurring *class* of bug matters more than the same file twice. Group R1 and R4 hits
by symptom words in the message — `ordering`, `null`, `timeout`, `race`, `cache`,
`encoding`, `path`, `permission`, `retry`, `id`. Ten files with the same symptom is one
lesson, not ten.

---

## 4. Coupling and hotspots

### 4.1 Change coupling

```bash
git log --no-merges --pretty=format:"C%H" --name-only | awk '
  /^C/ { if (n>1) for(i=1;i<=n;i++) for(j=i+1;j<=n;j++) print a[i]" + "a[j];
         delete a; n=0; next }
  NF   { a[++n]=$0 }
  END  { if (n>1) for(i=1;i<=n;i++) for(j=i+1;j<=n;j++) print a[i]" + "a[j] }' |
  sort | uniq -c | sort -rn | head -40
```

On Windows PowerShell 5.1 this loop is easier in Python. Use the same dump the
recurrence script reads:

```python
import subprocess
from collections import Counter

raw = subprocess.run(["git", "log", "--no-merges", "--pretty=format:C%H",
                      "--name-only"], capture_output=True, text=True).stdout
pairs, cur = Counter(), []
for line in raw.splitlines():
    if line.startswith("C") and len(line) >= 40:
        s = sorted(set(cur))
        for i in range(len(s)):
            for j in range(i + 1, len(s)):
                pairs[(s[i], s[j])] += 1
        cur = []
    elif line.strip():
        cur.append(line.strip())
for (a, b), n in pairs.most_common(30):
    if n >= 3:
        print(f"{n:3d}  {a}  +  {b}")
```

Filter before reporting:

- drop pairs where one file is a test of the other
- drop barrel/index files and type-only files
- drop generated and vendored paths
- keep count >= 3

### 4.2 Hotspot score

Tornhill's hotspot = churn x complexity. Complexity is hard without a language tool, so
use a proxy and say so:

```
hotspot = churn_commits * log2(1 + lines_added_to_file)
```

```bash
git log --numstat --pretty=format:"C%H" -- <path> | awk '
  /^C/ {next} NF==3 {a+=$1; d+=$2} END {print "added="a, "deleted="d}'
```

### 4.3 Risk map inputs

```bash
git log --pretty=format:"C%H" --name-only --grep='^fix\|^hotfix\|^bugfix' -i |
  grep -v '^C' | grep -v '^$' | sort | uniq -c | sort -rn | head -25   # fix density
git log --pretty=format:"C%H" --name-only | grep -v '^C' | grep -v '^$' |
  sort | uniq -c | sort -rn | head -25                                 # churn
```

Combine: `risk = churn_rank + 2*fix_count + coupling_degree`, then weight by recency
(commits in the last 90 days count double). Rank, keep the top 10.

### 4.4 Ownership

```bash
git log --format="%an" -- <path> | sort | uniq -c | sort -rn | head -3
```

A high-risk file with one author and no recent commits is a knowledge risk. Say so.

---

## 5. Conventions and boundaries

### 5.1 What the tooling already enforces — read this before writing rules

```bash
ls -a | grep -E "^\.(eslintrc|prettierrc|editorconfig|ruff|flake8|rubocop|clang-format|swiftlint)"
cat .editorconfig 2>/dev/null
ls .github/workflows/ .gitlab-ci.yml Jenkinsfile 2>/dev/null
```

Anything these enforce is **not** a lesson. Do not restate it.

### 5.2 Intentional inconsistency

Compare the same job across modules. Run one probe per concern:

```bash
# error shape
rg -n "throw new|Result<|Either<|\.unwrap\(\)|if err != nil" --glob '!*test*' -c | head
# validation
rg -n "safeParse|z\.object|validate\(|typeof .* !==|Schema\(" -c | head
# identifiers
rg -n "parseInt\(|Number\(|parseId\(|UUID\(|strconv\.Atoi" -c | head
# logging
rg -n "console\.log|logger\.|log\.info|println!|fmt\.Print" -c | head
```

Then disambiguate with history:

```bash
git log --oneline -S"parseId" | head          # when a helper spread, and where
git log --oneline -i --grep='migrat\|only used in\|for now\|to follow' | head -20
```

### 5.3 In-code decision markers

```bash
rg -n "TODO|FIXME|HACK|XXX|NOTE|DEPRECATED|SAFETY:" --glob '!*.md' --glob '!node_modules' |
  head -60
rg -n "do not remove|must stay|intentional|workaround" --glob '!*.md' | head -30
```

Each TODO is a deferred decision. Check whether the history already resolved it.

### 5.4 Architectural boundaries

Derive, do not assume:

```bash
# modules nobody imports from outside their own directory
rg -n "^import .* from '\.\./" src --only-matching | sort | uniq -c | sort -rn | head
# thin wrappers that exist for a reason
git log --oneline --follow -- <wrapper-path> | head
git log --format="%h %s" -S"<wrapper-name>" | head
```

A module with no outside importers and a rename history is a boundary. A wrapper with a
one-line body and a commit explaining why it exists is a boundary.

### 5.5 Testing strategy

```bash
cat package.json 2>/dev/null | rg -A5 '"scripts"'
cat Makefile pytest.ini tox.ini Cargo.toml 2>/dev/null | rg -i "test"
ls -d tests test spec __tests__ 2>/dev/null
git log --oneline -n 300 --name-only -- '*test*' '*spec*' | head -40
```

Then derive the *expected* shape of a test by reading two or three:

```bash
git show $(git log -1 --format=%H -- '*test*') --stat
```

And check whether fixes ship with tests, from Phase 3 R5.

**Invariant tests.** The strongest portable testing pattern found in the field: a test
that reads a configuration file and asserts a required value. It converts a written rule
into a red build.

```bash
rg -n 'readText\(\)|getResourceAsStream|read_to_string|open\(.*\.xml|readFileSync' --glob '*test*' --glob '*Test*' --glob '*spec*'
```

When found, name the file and the invariants it locks, and make "add the invariant to
that test" a checklist item. Example: `WidgetContractInvariantsTest` asserted
`resizeMode="none"`, the presence of `reconfigurable`, the absence of
`configuration_optional`, and a corner radius cap — every one of which was a recurring
OEM-launcher defect.

### 5.6 GitHub "why" — optional, high value

When the origin is GitHub and `gh` is authenticated:

```bash
gh auth status
gh pr list --state merged --limit 50 --json number,title,body,mergeCommit
gh pr view <n> --json body,comments
gh issue view <n> --json title,body
```

A PR body upgrades a claim from `[inferred]` to `[observed]`. Bot comments must be
filtered. Redact the same way as everything else.

Fallback when `gh` is missing or offline: commits only, and every claim that would have
needed a PR reason stays `[inferred]`.

---

## 6. Guard rails for the analysis itself

| Guard | Reason |
| --- | --- |
| Never analyze more than ~60 episodes | Cost grows linearly; signal does not |
| Never read a whole file blob into the bundle | Too many tokens; use `--stat` and hunks |
| Always exclude lockfiles and generated paths first | They dominate churn and mean nothing |
| Always scope a refresh to `head..HEAD` | Re-deriving costs a full run and drops review effort |
| Always state the analysis window | A rule from 800 commits ago may be stale |
| Always keep the raw bundles | A human can then audit any rule |
