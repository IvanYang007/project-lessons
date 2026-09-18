# project-lessons

A coding-agent skill that reads a repository's **git history** and writes a durable
`PROJECT_LESSONS.md` — the constraints, risk areas, and past mistakes a future agent
needs before it touches the code.

Run it once. Commit the output. Every later session starts with the repo's memory
instead of an empty context window.

## The problem

A coding agent can read every file in a repo and still not know:

- which pattern is a deliberate choice and which is a half-finished migration
- which feature was tried, shipped, and ripped out — and why
- which file breaks every time someone touches it
- which two files always change together, so changing one alone is a bug
- which mistake this project has already made three times

None of that is in the current code. All of it is in the commit history.

## What it produces

`PROJECT_LESSONS.md` at the repo root, plus a machine-readable `project-lessons.json`.
Both are written to the exact contract in the user's spec: executive summary, lessons
learned, project-specific implementation rules, known risk areas, safe-change
checklist, examples from commit history.

Every claim carries an evidence grade and the commit hash behind it:

| Grade | Meaning |
| --- | --- |
| `[observed]` | The reason is written in a commit message, PR body, or linked issue |
| `[inferred]` | Deduced from the shape of the diff, the file set, or the timing |
| `[weak]` | One data point, or an ambiguous signal. Read with care. |

Weak evidence is labelled, not deleted. A labelled guess is useful; an unlabelled one
is a trap.

## Why prescriptive, not narrative

Two 2026 ablations found that repository context files do not measurably improve task
success, and that they raise inference cost by 20%+.

- Gloaguen et al., *Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for
  Coding Agents?* — instructions in context files **are** well followed; repository
  **overviews** are not helpful. ([arXiv:2602.11988](https://arxiv.org/abs/2602.11988))
- Khatri et al., *Do Context Files Help Coding Agents?* — agents fail on feature design,
  pattern selection, and exact wiring, not on missing repository knowledge.
  ([arXiv:2607.27250](https://arxiv.org/abs/2607.27250))

So this skill leads with constraints and do-not-repeats, and pushes narrative history to
the bottom. A commit timeline is not a lesson.

## How it works

Deterministic git analysis first, LLM synthesis second. The LLM never invents a
convention — it only writes up signals the commands found.

```
git history
   |  1. survey      size, age, commit-style, file churn
   |  2. removals    what was added and later deleted, and the reason
   |  3. landmarks   reverts, dropped settings, abandoned subsystems
   |  4. recurrence  quick-remedy attribution, fix storms, fix clusters, same-bug text
   |  5. coupling    file pairs that change together (Tornhill change coupling)
   |  6. density     fix-density per file -> risk map
   v
evidence bundle (Markdown, in .project-lessons-work/)
   |
   v  7. synthesis   LLM writes PROJECT_LESSONS.md from the bundle only
   |
   v  8. gates       BLOCKING checks: every rule cited, graded, and non-generic
```

Recurrence detection is the core of the skill. Six signals, all mechanical:

1. **Quick-remedy attribution** — a `fix:` commit within 72h of an earlier non-fix commit
   that touched one of the same files. The earlier change omitted something. Each fix is
   attributed to exactly one earlier commit, so a burst of fixes reads as *this commit
   needed six follow-up fixes* instead of one giant transitive cluster.
   (Wen et al., *Quick remedy commits and their impact on mining software repositories*,
   EMSE 2022.)
2. **Fix storms** — runs of fix commits with no intervening feature commit. The work
   landed before it was ready. Zero-span runs are labelled `batch`: a rebase or import, not
   a storm.
3. **Fix-cluster files** — one file with three or more `fix:` commits.
4. **Same-bug-again text** — `again`, `still`, `same`, `forgot`, `regression` in fix
   messages.
5. **Fix commits that changed test code** — detected by diff marker, not just by file
   path, so colocated and inline tests are found.
6. **Recurrence by topic** — the noun the fixes keep returning to. This is the only signal
   that survives multi-author, PR-driven history.

Signals 1, 4 and 6 are the ones that find a *repeated* mistake rather than a single bug.
Signal 1 stops working on a repository with real review history: on a 68-contributor
project it could place only 18 of 70 fixes, because a squash-merged fix answers an issue,
not the merge that introduced the problem. Signal 6 plus an explicit keyword probe found
the real cluster.

## Layout

```
SKILL.md                       the skill
references/output-template.md  the exact PROJECT_LESSONS.md contract
references/analysis-playbook.md  full command reference per signal
references/evidence-grading.md   how to grade, and how to scrub secrets
references/prior-art.md          evaluation of the tools and papers below
scripts/recurrence.py          dependency-free R1-R6 detector
scripts/check_output.py        enforces the Phase 7 BLOCKING gates
examples/                      three real generated artifacts, for calibration
```

## Install

pi:

```powershell
# canonical source is this repo; link it where the agent loads skills
New-Item -ItemType Junction `
  -Path "$env:USERPROFILE\.pi\skills\project-lessons" `
  -Target "D:\Github\project-lessons"
```

Claude Code / other agents: copy this directory into `.claude/skills/project-lessons/`
or `.agents/skills/project-lessons/`.

## Use

Say any of:

- "mine the git history and write PROJECT_LESSONS.md"
- "what mistakes has this repo made before?"
- "which files are high-risk here?"
- "refresh the project lessons"
- "write memory for just the testing story" — a scoped run

A scoped run narrows the analysis to a path, a commit class, or a time window and
writes `PROJECT_LESSONS.<scope>.md`, leaving the repository-wide document untouched.
Spoken as a task category rather than as a second audit.

## Safety

- **Read-only on source history.** Only `git log`, `git show`, `git diff`, `git blame`.
- **Secret scrubbing** before any repo text reaches a model — keys, tokens, `.env`
  values, private-key blocks are redacted at the boundary.
- **Bounded cost.** Lockfiles, vendored code, generated files, and minified bundles are
  dropped. Commits are clustered into episodes. Incremental re-runs only pay for new
  commits.
- **Reviewable.** Plain Markdown and JSON in your repo. Read it, diff it, then commit it.

## Prior art and how this differs

Full evaluation in [`references/prior-art.md`](references/prior-art.md).

| Tool | Approach | What this skill takes from it |
| --- | --- | --- |
| [ChrisCooneyUK/git-log-context-harvesting](https://github.com/ChrisCooneyUK/git-log-context-harvesting) | 10-step workflow, derives `CLAUDE.md` from git history | Removed-vs-migrating disambiguation; "no inventions ungrounded in history" |
| [hr23232323/repo-history](https://github.com/hr23232323/repo-history) | Deterministic engine + LLM episodes, writes `.repo-memory/` | Evidence grading `[observed]`/`[inferred]`; guardrails-first ordering; episode clustering |
| [TheaDust/lore](https://github.com/TheaDust/lore) | Markdown-only long-term memory with stable entry IDs and lifecycle tags | Stable IDs, `#stale`/`#superseded-by` lifecycle, mirrors |
| [pedronauck/skills lesson-learned](https://claudeskills.info/skills/pedronauck/skills/lesson-learned/) | Post-hoc lesson extraction from a diff range | Scope selection by branch/range; "one grounded lesson beats seven vague ones" |
| [yagizdo/quiver create-agents-md](https://github.com/yagizdo/quiver/blob/master/skills/create-agents-md/SKILL.md) | High-signal-density `AGENTS.md` | BLOCKING quality gates; dedup against existing docs; imperative voice |
| [adamtornhill/code-maat](https://github.com/adamtornhill/code-maat) | Change coupling and hotspot mining | Coupling and churn math, done in shell so no Java install is needed |
| [matthewp/recall](https://github.com/matthewp/recall) | Git as the reasoning store | Write lessons back into the repo, not into a private database |
| SZZ / RegMiner | Link fixes to bug-introducing commits | Considered and rejected: needs line-level blame archaeology for little extra signal |

What is new here: the recurrence layer. The prior tools collect decisions, landmines,
and hotspots. None of them systematically find a mistake the project made **more than
once**, which is the one class of lesson an agent most needs to not repeat.

## Validation

Run end to end on three real repositories with different shapes. All three artifacts pass
every blocking gate in `scripts/check_output.py`.

| Repo | Shape | What it exercised |
| --- | --- | --- |
| [papervault](examples/papervault-PROJECT_LESSONS.md) | 66 commits, 1 author, 23 hours, Rust | fix storms, quick-remedy attribution, the inline-test detection bug |
| [CountUp-Android](examples/countup-PROJECT_LESSONS.md) | 176 commits, 1 author, 4 weeks, Android | removals, prior-document cross-check, committed-secret scan, coupling |
| [ponytail](examples/ponytail-PROJECT_LESSONS.md) | 210 commits, **68 contributors**, 8 weeks, cross-agent skill package | multi-author PR workflow, topic recurrence, manifest drift, adapter mirrors |

Nine defects were found and fixed by that validation:

1. Quick-remedy pairing flooded on a burst-fix repo, because every fix sat inside the
   window of every other fix. Replaced with attribution to the nearest earlier non-fix
   commit.
2. Test detection by file path reported "0 of 35 fixes touched tests" on a Rust repo that
   keeps its tests inline. A `git log -G` diff marker found 7 of 35.
3. The R1 table's long tail of single-fix rows buried the signal. Rows now require two or
   more follow-up fixes.
4. Nothing probed for a repository that already documents its own recurring faults.
   CountUp carries `docs/RECURRING_ISSUES.md` with 10 defects and a 12-item checklist.
   Phase 0.2 now finds those documents and forbids duplicating them.
5. Nothing scanned for secrets that were deleted but remain in history. CountUp still has
   a keystore password in its pushed history.
6. Nothing enforced the BLOCKING gates. `scripts/check_output.py` now does, and it
   immediately caught two gate failures in the papervault artifact.
7. Every signal was timing-based, so all of them went quiet on a 68-contributor PR-driven
   repository. Signal 6 clusters by topic and is the only one that still found the
   recurring mistake — 25 commits, 36% of all fixes.
8. A run of five fixes at the same timestamp was reported as a "storm". It was a rebase.
   Zero-span runs are now labelled `batch`.
9. SKILL.md numbered the signals differently from the script. Both now use R1-R6.

## Status

Working. The skill, its references, the recurrence detector, and the gate checker are all
in place, validated against single-author and 68-contributor repositories over 23 hours,
4 weeks and 8 weeks of history.

Not yet tested: a repository with a year or more of releases, and any language whose test
layout the R5 detector has not seen (the marker list covers Rust, Python, JS/TS, Go and
Java).

## License

MIT
