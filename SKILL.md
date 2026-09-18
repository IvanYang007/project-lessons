---
name: project-lessons
description: Analyze a repository's git commit history and write a durable, evidence-linked PROJECT_LESSONS.md that future coding agents load before changing code. Use when the user says "mine the git history", "what mistakes has this repo made", "create project memory", "write project lessons", "what should I know before changing this repo", "which files are high-risk here", "learn from the commit history", "refresh the project lessons", or wants a safe-change checklist derived from past commits. Also use before a large refactor or when onboarding an agent to a long-lived repository.
version: 1.0.0
---

# Project Lessons

Turn commit history into constraints a future agent can act on.

A commit timeline is not a lesson. The output is a small number of **prescriptive
rules**, each tied to a commit hash and graded for evidence strength.

## Non-negotiables

1. **Read-only.** Run only `git log`, `git show`, `git diff`, `git blame`,
   `git shortlog`, `git tag`, `git ls-files`, `git check-ignore`, `git rev-list`.
   Never `checkout`, `reset`, `clean`, `stash`, or write into `.git/`. If the tree is
   dirty, leave it dirty. **Never rewrite history** — if a credential was committed,
   report it and stop.
2. **No invention.** Every rule you write must trace to a commit hash, a file path,
   or an in-code marker. If you cannot cite it, do not write it.
3. **No generic advice.** "Write tests", "keep functions small", and "avoid
   duplication" are banned. If the bullet could be pasted into another repo
   unchanged, delete it.
4. **Grade every claim.** `[observed]`, `[inferred]`, or `[weak]`. See
   `references/evidence-grading.md`. Weak evidence is labelled, never hidden.
5. **Prescriptive over narrative.** Two 2026 ablations found repository *overviews*
   do not improve agent accuracy, while *instructions* are followed.
   ([arXiv:2602.11988](https://arxiv.org/abs/2602.11988),
   [arXiv:2607.27250](https://arxiv.org/abs/2607.27250)) Lead with rules; keep the
   story short and at the end.
6. **Bounded cost.** Never LLM-analyze every commit. Filter noise, cluster into
   episodes, cap the bundles you read.

## When to stop instead

- Fewer than ~30 commits, or less than ~3 months of history: the signal is too thin.
  Say so and stop. Do not pad the document.
- Single-author repo with all commits in one day: same.
- The user wants API docs or a README: that is a different job.

## Scoped runs — memory for one category of task

The default run produces one document for the whole repository. When the caller asks for
memory about a *category* of work - "everything about migrations", "the testing story",
"what to know before touching the parser" - narrow the analysis instead of writing a
second generic document.

Pass a scope as one of:

| Scope | How to narrow |
| --- | --- |
| Path or subsystem | append `-- <path>` to every command in Phases 1-5, and to the `scripts/recurrence.py` dump |
| Message class | add `--grep` / `-G` to restrict to `fix:`, `refactor:`, `perf:`, or `test` history |
| Time window | add `--since` / `<sha>..HEAD` |
| Task intent | filter the evidence bundle by the files a task would touch, then keep only rules whose `paths` intersect |

Rules for a scoped run:

- Keep the same six-section contract. A scoped document is a smaller PROJECT_LESSONS.md,
  not a different shape.
- Write to `PROJECT_LESSONS.<scope>.md` and set `"scope"` in `project-lessons.json`.
  Never overwrite the repository-wide document with a scoped one.
- Add the paths you excluded to Analysis notes. A scoped document that does not say what
  it left out reads as if it covered everything.
- Prefer many small scoped runs only when the caller asks for them. One good
  repository-wide document beats five narrow ones nobody reads.
- A scoped run is cheap: reuse the repository-wide dump and filter it, rather than
  re-walking the git log.

## Workflow

Run phases in order. Each phase produces evidence; only Phase 6 writes prose.

Create a work directory first: `.project-lessons-work/`. Keep every bundle there.
Add it to `.gitignore`. Delete it at the end, or when `--keep-work` is set.

**Shell note.** Aggregations below are given in POSIX and in PowerShell. Use the pair
that matches the host. `rg` is available on Windows; `grep` is not on the PATH.

---

### Phase 0 — Preflight

```bash
git rev-parse --is-inside-work-tree
git log --oneline | wc -l                       # commit count
git log -1 --format=%cI                         # newest commit date
git log --reverse --format=%cI | head -1        # oldest commit date
git ls-files | wc -l                            # tracked files
git status --porcelain | head                  # dirty tree?
git log --merges --oneline | head -5           # PR-merge workflow?
git remote -v                                  # GitHub origin? gh usable?
```

If an existing `PROJECT_LESSONS.md` is present, read it and switch to the **refresh
workflow** at the end of this file.

Record, in one paragraph, what this repo is and what it is built with. Read the entry
point and one representative module. If the shape of the code contradicts the history,
trust the code and re-read the history.

### Phase 0.2 — Read what the repo already wrote down

Do this before any synthesis. Many repositories already document their own decisions and
recurring faults. A document that duplicates them is worse than useless: it drifts from
them, and the next reader cannot tell which one to trust.

```bash
git ls-files | rg -i 'recurring|known.?issues|lessons|troubleshoot|postmortem|decisions?\.md|code.?review|threat|invariants'
git ls-files -- '*/adr/*' '*/decisions/*' '.scratch/*' '*SECURITY*' '*CONTRIBUTING*' '*ARCHITECTURE*'
```

Read every file found and write `.project-lessons-work/00-prior-docs.md` with, per file:
what it claims, which claims have a commit behind them, which claims the history
contradicts, and which claims are stale because a later commit fixed the thing.

Then hold this table for the rest of the run:

| Situation | What to write |
| --- | --- |
| The repo documents a rule the history confirms | Cite the document as `[observed]`, add the hashes, and **point at it instead of restating it** |
| The repo documents a rule the history contradicts | Write the contradiction and quote both sides. This is the highest-value finding a run can produce |
| The repo documents a rule a later commit fixed | Mark it stale and cite the fix |
| The repo documents nothing | Proceed normally |

Never copy a prior document into `PROJECT_LESSONS.md`. Link to it and add only what it
is missing.

**Noise filter.** Exclude from every later analysis:

```
lockfiles           package-lock.json  yarn.lock  poetry.lock  Cargo.lock  Gemfile.lock
generated           dist/ build/ target/ out/ .next/ coverage/ *.min.js *.map
vendored            node_modules/ vendor/ third_party/ .venv/
docs-only           *.md  LICENSE  .github/ISSUE_TEMPLATE/
```

```bash
git log --pretty=format: --name-only -- . \
  ':(exclude)*.lock' ':(exclude)*.md' ':(exclude)dist/*' ':(exclude)build/*' \
  ':(exclude)target/*' ':(exclude)node_modules/*' ':(exclude)*.min.js' \
  | sort -u > .project-lessons-work/tracked-noise-filtered.txt
```

If the repo is on GitHub and `gh` is authenticated, pull the *why* later from PR
bodies and linked issues. Commits say what changed; pull requests say why.

---

### Phase 1 — Survey: shape, style, churn

```bash
git log --pretty=format:"%s" > .project-lessons-work/subjects.txt
git shortlog -sn --all | head -20               # authors, bus factor
git log --oneline --reverse | head -20          # how it started
git log --oneline | head -50                    # current surface
```

Commit-style convention:

```bash
# POSIX
git log --pretty=format:"%s" | grep -oE "^[a-zA-Z]+(\([^)]*\))?!?:" | sort | uniq -c | sort -rn | head
# PowerShell
git log --pretty=format:"%s" | Select-String -Pattern '^[a-zA-Z]+(\([^)]*\))?!?:' -AllMatches |
  ForEach-Object { $_.Matches.Value } | Group-Object | Sort-Object Count -Descending |
  Select-Object -First 10 Count, Name
```

Churn (the first risk signal):

```bash
# POSIX
git log --pretty=format: --name-only | grep -v '^$' | sort | uniq -c | sort -rn | head -30
# PowerShell
git log --pretty=format: --name-only | Where-Object { $_ } | Group-Object |
  Sort-Object Count -Descending | Select-Object -First 30 Count, Name
```

Write `.project-lessons-work/01-survey.md`: size, age, languages, entry point,
top-20 churn files, commit-style, bus factor.

---

### Phase 2 — Removals, abandoned work, and committed secrets

This is the highest-value phase. A removed feature, a dropped library, and a deleted
subsystem each carry a reason the code no longer shows. A deleted credential is worse.

**Run the secret scan first.** A path that was ever committed still lives in the packfile
after deletion, and a public push publishes it.

```bash
# every path ever added, filtered to secret-shaped names
# POSIX
git log --pretty=format: --diff-filter=A --name-only \
  | grep -v '^$' | sort -u \
  | grep -iE 'passw|secret|credential|\.env|token|apikey|api[_-]?key|\.pem|\.jks|\.keystore|id_rsa|\.pfx|key\.txt'

# is a specific suspect still reachable in history?
git log --all --oneline -- "<path>"
git rev-list --all --objects | rg --fixed-strings "<path>"
```

On Windows use `rg -i` in place of the final `grep -iE`.

When a secret-shaped path was ever committed:

1. **Do not print the value, in the work bundle or in the output.** Read the commit only
   to establish that it happened.
2. Record: path, the commit that added it, the commit that removed it, and whether any
   remote exists. Then check exposure:
   ```bash
   git remote -v
   git log --oneline origin/HEAD -- "<path>" 2>/dev/null
   ```
3. Write the finding as a BLOCKING item in the output under Known risk areas, with the
   action "rotate the credential and purge it from history before any public push".
4. **Never rewrite history yourself.** Report it and stop at the report. A history rewrite
   is the owner's decision.

**Why this belongs in this skill.** Deleting a file from a later commit does not remove
it from history. Only `git filter-repo` or a fresh repository does.

```bash
# every path ever deleted
git log --pretty=format: --diff-filter=D --name-only | grep -v '^$' | sort | uniq -c | sort -rn | head -40
# removal / revert commits, with messages
git log --oneline --grep='revert\|drop\|remove\|delete\|undo\|rollback' -i | head -40
# reversions by git itself
git log --oneline --grep='^Revert ' | head -30
```

For every cluster of removals, reconstruct the lifecycle: added, grew, removed.

```bash
git log --oneline --follow -- "<path>"
git log -1 --format="%H%n%cI%n%s%n%n%b" $(git log --diff-filter=D --format=%H -- "<path>" | head -1)
```

**Disambiguate before calling anything a mistake.**

| Evidence | Verdict |
| --- | --- |
| Commit says "revert", "too heavy", "leaked", "did not work", "rollback" | `[observed]` — record the quoted reason |
| Path re-added later, same name or near-identical content | `[inferred]` — oscillation, record both directions |
| Path deleted once, no message, no successor | `[weak]` — cleanup, not a lesson |
| Library removed and never returned | `[observed]`/`[inferred]` — a dependency boundary |

Write `.project-lessons-work/02-removals.md`. Quote commit messages verbatim; a
quoted author beats a paraphrase.

---

### Phase 3 — Recurrence: the mistakes this repo made twice

This is what separates a lessons document from a changelog. Six signals, numbered to
match `scripts/recurrence.py` exactly.

**R1 — Quick-remedy attribution.** A `fix:` commit inside 72 hours of an earlier commit
that touched one of the same files means the earlier change omitted something.
(Wen et al., *Quick remedy commits and their impact on mining software repositories*,
EMSE 2022.)

**Attribute each fix to exactly one earlier commit — the nearest preceding *non-fix*
commit it shares a file with.** Do not emit every matching pair. On a repo with a burst
of fixes, every fix sits inside the window of every other fix and pairwise output
collapses into one meaningless transitive cluster. Grouping by the earlier commit keeps
one row per story: *this commit needed six follow-up fixes*.

Only rows with **two or more** follow-up fixes are reported. A commit that drew exactly
one is ordinary course-correction.

**R1 fails on multi-author, PR-driven repositories.** Validated on a 68-contributor
project: 52 of 70 fixes could not be attributed to any recent commit, because a
squash-merged fix answers an *issue*, not the merge that introduced the problem. When R1
goes quiet on a repository with real review history, that is the finding — switch to R6.

**R2 — Fix storms.** Consecutive fix commits with no intervening feature or refactor
commit. The work landed before it was ready; ask what review or test step was skipped.

A run whose span is ~0h is not a storm: it is a rebase, a squash import or a batch
landing, and it carries no process signal. The script labels those `batch`.

**R3 — Fix-cluster files.** One file with three or more `fix:` commits. This is the
single best predictor of "this will break again".

```bash
git log --oneline --grep='^fix\|^bugfix\|^hotfix' -i --name-only \
  | grep -v '^[0-9a-f]\{7,\} ' | grep -v '^$' | sort | uniq -c | sort -rn | head -25
```

Remember that `--grep` is BRE: escape the alternation, or pass `-E` before `--grep`.

**R4 — Same-bug-again text.** Fix commits that admit a repeat. Read every hit, then
answer: *what did the author know the second time that they did not know the first
time?* That answer is the lesson. Write it as an imperative rule.

Expect false positives. `missing` and `also` were removed from the pattern because they
matched "ship the missing feature" and "also fix X" — lexical, not a repeat. Treat a
lone hit as `[weak]`.

**R5 — Fix commits that also change test code.** The test did not exist, or asserted
the wrong thing. This is a testing-strategy lesson, and the ratio is a testing-culture
measurement: 16 of 35 in one repo, 42 of 70 in a well-tested one, 0 of 35 in a repo
whose tests were all `#[cfg(test)]` modules the path detector could not see.

Detecting tests by path alone misses colocated and inline tests, so pass the diff-marker
list as well. Never report a "no tests" conclusion from the file-path detector alone.

**R6 — Recurrence by topic.** Count the NOUN the fixes keep returning to. This is the
signal that survives multi-author, PR-driven history, where R1 does not.

```bash
# unigrams: finds the lexically stable clusters (script R6)
# explicit keyword probe: finds a theme spread across synonyms
# POSIX
git log --oneline -i --grep='windows\|powershell\|cross-platform\|portable\|CRLF\|BOM'
```

**Both are needed.** On a 68-contributor project, unigram clustering reported `windows`
in 5 fixes. An explicit probe on the same history found **25 commits** — 36% of all
fixes — because the theme was expressed as `windows`, `powershell`, `CRLF`, `portable`,
`$env:`, `USERPROFILE` and `python3` in different commits.

Build the keyword set from the symptoms you notice while reading R3 and R5, not from a
generic list. The clusters that matter are the ones specific to this repository.

Do not report the repository's own name as a topic. Every path contains it, so it will
rank first and mean nothing.

**Repeated-removal paths** (a path added and deleted more than once) belong to Phase 2,
not here: `git log --pretty=format:"C%H" --name-only --diff-filter=D | grep -v '^C'`.

Run the whole set:

```bash
git log --no-merges --format="C%H|%ct|%s" --name-only > .project-lessons-work/commits.txt
git log -G'#\[test\]|#\[cfg\(test\)\]|def test_|describe\(|it\(' --format=%H \
  > .project-lessons-work/test-touch.txt
python scripts/recurrence.py .project-lessons-work/commits.txt \
  .project-lessons-work/test-touch.txt > .project-lessons-work/03-recurrence.md
```

Full command reference: `references/analysis-playbook.md`. Read it before Phase 1.

Write `.project-lessons-work/03-recurrence.md`. Every entry: signal, commits, files,
the rule that follows.

---

### Phase 4 — Coupling and the risk map

**Change coupling** (Tornhill, *Your Code as a Crime Scene*): two files that change in
the same commit far more often than chance means a hidden contract. Change one alone
and you break the other — and the tests may not notice.

```bash
# co-change pairs from the last N commits
git log --no-merges --pretty=format:"C%H" --name-only | awk '
  /^C/ { if (n>1) for(i=1;i<=n;i++) for(j=i+1;j<=n;j++) print a[i]" + "a[j];
        delete a; n=0; next }
  NF  { a[++n]=$0 }
  END { if (n>1) for(i=1;i<=n;i++) for(j=i+1;j<=n;j++) print a[i]" + "a[j] }' \
  | sort | uniq -c | sort -rn | head -30
```

Report couplings that appear **3 or more times** with a support ratio. Skip pairs that
are obviously mechanical (a file plus its own test, an index plus a barrel file, a
types file plus anything).

**Risk map.** Score each file on four axes and keep the top 10:

```
risk = churn_rank + 2*fix_density + coupling_degree + recency_weight
fix_density = fix commits touching the file / commits touching the file
```

A file that is both hot and fix-heavy is where an agent will break something.
A file that is high-churn and fix-light is probably just active.

Write `.project-lessons-work/04-risk.md`: the ranked table, each coupling pair, and the
counts behind each score so a reader can re-derive it.

---

### Phase 5 — Conventions, boundaries, and testing

**Conventions that are already enforced by tooling are not lessons.** Check the linter,
formatter, and CI config first; do not restate what the tool blocks. Record only
conventions that a tool does not enforce and a newcomer would get wrong.

Look for **intentional inconsistency** — the same job done in different shapes:

- error returns: exception vs result type vs sentinel
- validation: schema parser vs hand-written checks
- identifiers: typed helper vs inline cast
- state: class vs closure vs plain object
- logging: structured vs interpolated

For each, the history decides:

| History says | Verdict | Agent instruction |
| --- | --- | --- |
| "migrate X to Y, others to follow" | migration in flight | Follow Y in files you already touch. Do not sweep. |
| "only used in the Z module for now" | deliberate | Match the local shape. Do not unify. |
| Two shapes, no commit, both old | `[weak]` | Say nothing, or flag as unresolved |
| One shape, 12 committers, 2 years | stable | State it as a rule |

**Architectural boundaries.** Derive them from what breaks when crossed: files that
always change together, modules with no inbound imports, thin wrappers that exist for a
reason, layers nobody bypasses. Derive, do not assume the textbook layering.

Look for in-code markers that carry a decision:

```bash
rg -n "TODO|FIXME|HACK|XXX|NOTE|DEPRECATED" --glob '!*.md' --glob '!node_modules'
rg -n "@deprecated|SAFETY:|workaround|do not remove|must stay" --glob '!*.md'
```

A TODO with a reason is a deferred decision. A TODO with no owner and no date is noise.

**Testing strategy.** Derive what the project expects, not what the textbook says:

- test runner and command, from config and CI
- test layout: colocated vs mirrored tree vs `tests/`
- the shape of a test in this repo: arrange style, fixture style, assertion library
- what is covered: unit, integration, golden/snapshot, e2e
- what is deliberately not covered
- whether fixes are expected to ship with a test (use Phase 3 R5 as evidence)
- **invariant tests**: does the project assert its own configuration? Look for tests that
  read a manifest, XML, gradle, or config file and assert a value
  (`rg -n 'readText\(\)|getResourceAsStream|File\(' --glob '*test*'`). This is a strong,
  portable pattern: it turns a written rule into a red test.

If a fix commit rewrote a test, say so — that is evidence a test was missing.

Write `.project-lessons-work/05-conventions.md`.

**Consolidate with Phase 0.2.** Do not write a rule that a prior document already
carries. Cite the document and spend the rule budget on what it misses.

---

### Phase 6 — Synthesize PROJECT_LESSONS.md

Read `references/output-template.md` and use it exactly. Do not invent sections.

Write to `<repo-root>/PROJECT_LESSONS.md`. Also write
`<repo-root>/project-lessons.json` with the same content as records, so a tool can
query it:

```json
{
  "schema": "project-lessons/v1",
  "repository": "<name>",
  "scope": "repository",
  "generated_from": { "head": "<sha>", "commits_analyzed": 0, "date_range": ["", ""] },
  "rules": [ { "id": "PL-001", "text": "", "grade": "observed",
               "evidence": ["<sha>"], "paths": [], "phase": "recurrence" } ],
  "risk_areas": [ { "path": "", "score": 0, "why": "", "evidence": ["<sha>"] } ],
  "couplings": [ { "pair": ["a", "b"], "count": 0 } ],
  "checklist": [ { "id": "PL-C1", "text": "", "evidence": ["<sha>"] } ]
}
```

Rules of writing:

- Imperative voice. "Run X", "Never Y", "Copy the shape from `src/a.ts`".
- One rule per line. No hedging: no "consider", "might", "you may want to".
- Cite the hash inline. `Route order matters: literal paths before `:id` (a1b2c3d).`
- Quote the author when the author said it best.
- Rank by consequence. A rule that prevents a broken build outranks a naming rule.
- Cap at 40 rules. If you have more, you have not synthesized.
- If a whole section has no evidence, write the section header and say
  `No evidence in the analyzed history.` Do not fill it.

---

## Phase 7 — Quality gates

Run the checker first. It enforces the BLOCKING list below mechanically:

```bash
python scripts/check_output.py PROJECT_LESSONS.md project-lessons.json .
```

Exit code 0 means every blocking gate passed. Fix everything it reports as BLOCKING. The
prose list below is the same contract in human-readable form — keep it for the cases a
regex cannot judge.

Run every check. Fix, then re-check. Do not deliver with a failing gate.

**BLOCKING**

- [ ] Every rule cites a commit hash, path, or in-code marker.
- [ ] Every rule has a grade: `[observed]`, `[inferred]`, or `[weak]`.
- [ ] No generic advice. Test each bullet: could it appear in an unrelated repo
      unchanged? Delete it.
- [ ] No restatement of what a linter, formatter, or CI job already enforces.
- [ ] No restatement of a prior in-repo document (Phase 0.2). Cite it instead.
- [ ] All six required sections exist.
- [ ] Every risk-area path exists in the current tree (or is labelled removed).
- [ ] All commands used were read-only.
- [ ] No secret reached the document. Re-scan the output for keys and tokens.
- [ ] If any secret-shaped path was ever committed, it is reported with rotation
      required, and the value is not quoted anywhere.
- [ ] Total length is 80-400 lines. Under 80, you under-analyzed. Over 400, you
      transcribed instead of synthesizing.
- [ ] Safe-change checklist has 5-12 items, each verifiable by running something.

**WARNING**

- [ ] More than 40 rules.
- [ ] Any lesson with only `[weak]` evidence in the Executive summary.
- [ ] Coupling pairs with count < 3.
- [ ] "Examples from commit history" is a timeline instead of 5-10 chosen cases.

Report the result in a short block: rules written, risk areas, coupling pairs,
gates passed, gates failed.

---

## Refresh workflow

If `PROJECT_LESSONS.md` already exists:

1. Read it. Note the `generated_from.head` sha in `project-lessons.json`, or the last
   commit that touched the Markdown file.
2. Scope every command in Phases 1-5 to that range:
   ```bash
   git log <sha>..HEAD -- ...
   ```
   If the sha no longer exists (rebase, force-push), fall back to
   `git log --since="<date the file was last modified>"` and say so in the output.
3. For each finding, choose one action:
   - **updates** an existing rule whose evidence grew
   - **graduates** a `[weak]`/`[inferred]` rule to `[observed]`
   - **contradicts** an existing rule — the rule changed; rewrite it and quote both
     sides
   - **retires** a rule that the new commits made obsolete
   - **adds** a new rule
4. Show the user a diff. Never overwrite without showing the change.
5. Bump `generated_from.head` and append the new hashes to the evidence lists.

Do not re-derive the whole document on a refresh. It costs the same as a first run
and throws away human review effort.

## Common failure modes

| Failure | Fix |
| --- | --- |
| A changelog with lessons bolted on | Every entry must end in an instruction |
| Confident rules from one commit | Downgrade to `[weak]` and say so |
| "Follow the existing patterns" | Name the file to copy and the pattern to copy |
| Analysing every commit | Filter noise, cluster into episodes, cap at 60 bundles |
| Treating a partial migration as a bug | Check the history; it is usually deliberate |
| Restating the linter | Read the lint config first, then write only what it cannot enforce |
| Inventing textbook architecture | Derive boundaries from coupling and removals |
| Secrets in the output | Scrub before writing; re-scan after |
| Rule that says "be careful with X" | Name the failure, the symptom, and the guard |
| Duplicating `docs/RECURRING_ISSUES.md` or an ADR | Cite it, add the hashes, spend the budget elsewhere |
| "No secrets found" without checking deleted paths | Deleted paths stay in history. Run the Phase 2 scan |
| Quoting a leaked credential to "prove" the finding | Never print the value. The path and the two commits are the proof |

## References

- `references/output-template.md` — the exact document contract
- `references/analysis-playbook.md` — full command reference per signal
- `references/evidence-grading.md` — how to grade, and when to say "unknown"
- `references/prior-art.md` — evaluation of the tools and papers this skill draws on
- `scripts/check_output.py` — the Phase 7 gate checker

## Scoped output naming

| Run | Document | `scope` in JSON |
| --- | --- | --- |
| Whole repository | `PROJECT_LESSONS.md` | `repository` |
| One subsystem | `PROJECT_LESSONS.<subsystem>.md` | the path |
| One commit class | `PROJECT_LESSONS.<class>.md` | e.g. `fix-history` |
