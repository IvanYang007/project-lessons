# Project Lessons — ponytail

> Derived from git history. Last analyzed commit: `2ed6c52` (2026-08-08).
> Range: `8c279cb` .. `2ed6c52` (210 commits, 2026-06-12 .. 2026-08-08).
> 68 contributor emails; 167 of 210 subjects (80%) end with `(#N)` — a squash-merge
> pull-request workflow. Grades: `[observed]` stated in a commit/doc, `[inferred]`
> deduced from diffs, `[weak]` one data point or ambiguous.
>
> **This repository already documents its own rules.** Read
> [`AGENTS.md`](AGENTS.md) and [`docs/agent-portability.md`](docs/agent-portability.md)
> first. This document does **not** restate them; it records what the history adds.

## Executive summary

ponytail is a cross-agent skill package (Claude Code, Codex, Gemini, Copilot, OpenCode,
Qoder, Devin, Hermes, Grok, pi) distributed as 10 version-bearing manifests around one
shared `skills/` and `hooks/` tree. 210 commits, 68 contributors, 8 weeks, 70 fix commits
(34%). The dominant lesson is **cross-platform portability**: 25 commits mention
Windows, PowerShell, CRLF, or portability — **36% of all fixes**. Platform defects are
discovered one contributor machine at a time, and nothing in the repository states the
cross-platform contract as a checklist, so the same class of bug is rediscovered
roughly monthly. The second lesson is **version drift across 10 manifests**: the 4.8.0
release shipped advertising three different versions, and the maintainers' own fix
commit records why the existing pairwise test could not catch it. Third: this
repository's recurrence pattern is **not** detectable by timing. 52 of 70 fixes could
not be attributed to a recent commit, because a PR-driven fix answers an issue, not the
last merge. Read the topic clusters, not the timeline.

**Read this first if you are about to touch:** anything under `hooks/`, `pi-extension/`,
or the manifest set (`.claude-plugin/`, `.codex-plugin/`, `.dev-plugin/`,
`.github/plugin/`, `.qoder-plugin/`, `gemini-extension.json`, `plugin.json`,
`plugin.yaml`, `package.json`, `ponytail-mcp/`).

## Lessons learned from past commits

### L1. Cross-platform breakage is the #1 recurring defect class. 25 commits, 16 fixes. — `[observed]`

- **What happened:** platform defects were found one contributor machine at a time and
  fixed independently. Seven distinct sub-classes, none of them stated as a rule anywhere
  in the repository.
- **Evidence (sub-class → commits):**
  - UTF-8 BOM in JSON parsing → `a3bc7db` (`settings.json`, #148), `9ec4fb8`
    (`config.json`, #478). **The same fix, twice, for two different files.**
  - bash-only constructs under PowerShell → `2b426c6`, `2ba0262` "drop bash-only `exec`"
  - shell-unsafe paths → `147bcfd`, `215777d`, `fb72987`
  - hardcoded interpreter → `3869218`, `5eb1fd8` ("Python command portable ... Windows")
  - CRLF → `1469048`; stdin EOF deadlock → `7e6eca6`
  - cross-platform tests → `515fb4c`, `2b426c6`, `f12f210`
- **Why it recurs:** the repository has a *portability* document but no portability
  *checklist*. `docs/agent-portability.md` describes adapters, not platform hazards. Each
  new contributor on Windows rediscovers BOM, path quoting, or `python3`.
- **The rule:** before you merge anything that reads/writes a file, spawns a process, or
  builds a path: strip a UTF-8 BOM before parsing, quote paths for the host shell, resolve
  the interpreter from `process.execPath`/`sys.executable` rather than a bare name, and
  normalize CRLF. A fix for one of these gets a Windows CI job or a `tests/hooks-windows.test.js`
  case, not just a patch.

### L2. A pairwise agreement check cannot catch collective version drift. — `[observed]`

- **What happened:** the v4.8.0 release shipped with all four plugin manifests still
  reading 4.7.0 and both `package.json` files at the npm-init `0.1.0` default, so the
  project advertised three versions at once (#260, #262).
- **Evidence:** `763e04d`, whose body states it plainly: *"The existing mutual-agreement
  check in `tests/gemini-extension.test.js` could not catch this, because all four
  manifests were stale at 4.7.0 together."* The fix added `scripts/check-versions.js` and
  wired it into CI, asserting every version file shares one pinned `X.Y.Z` **and** that on
  a release-tag run the shared version equals the tag.
- **Why it recurs:** there are now **10** version-bearing files
  (`.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.devin-plugin/plugin.json`,
  `.github/plugin/plugin.json`, `.qoder-plugin/plugin.json`, `plugin.json`, `plugin.yaml`,
  `gemini-extension.json`, `package.json`, `ponytail-mcp/`). Every new adapter adds one.
  `check-versions.js` had to be extended twice for exactly that reason (`7790c37` Devin
  manifest, `83493b9` Qoder hooks), and `c99757a` later bumped the Hermes manifest alone.
- **The rule:** a version bump touches all 10 files, then run `node scripts/check-versions.js`.
  When you add a platform adapter, add its manifest to that guard in the same PR — an
  unguarded manifest is what produced #260. Pin an absolute version; never rely on
  pairwise agreement between manifests, because they can all be wrong together.

### L3. Rules are copied into adapters. Editing the source breaks the copies. — `[observed]`

- **What happened:** hosts that only support project instructions get a *copy* of the rule
  text, kept aligned with `AGENTS.md`. `docs/agent-portability.md` states the adapter rule:
  *"When a host only supports project instructions, keep its copied rule text aligned with
  `AGENTS.md`."* The repository enforces it with `scripts/check-rule-copies.js` in CI.
- **Evidence:** `docs/agent-portability.md` ("Adapter Rule"), `.github/workflows/test.yml`
  runs `node scripts/check-rule-copies.js`, `cf9cbd5` "Revert #82 (Modern Web Guidance
  rung-3) and re-sync mirrors".
- **The rule:** editing `AGENTS.md` or a skill body requires re-syncing the adapter
  mirrors in the same PR. Run `node scripts/check-rule-copies.js` locally; CI runs it for
  you and it will fail on a stale copy.

### L4. In a PR-driven repository, a fix does not follow the commit it repairs. — `[observed]`

- **What happened:** quick-remedy attribution — pairing a fix with a recent commit it
  shares a file with — **failed on 52 of 70 fix commits**. A contributor opens an issue,
  someone fixes it against `main` weeks later, and the fix does not sit near the change
  that caused it.
- **Evidence:** the R1 pass attributed only 3 commits with 2+ follow-up fixes; 52 fixes
  were unattributed, including `1556f10b`, `147bcfd6`, `d6766353`, `084f10fb`, `45f7d2f8`.
  Compare papervault (single author, 23 hours), where 35 of 35 fixes were attributable.
- **Why it matters:** the technique that works on a solo WIP repository is the wrong
  instrument here. Recurrence has to be found by **topic**, not by timing.
- **The rule:** in this repository, run the topic probe (L5) rather than the timing probe
  when you want to know what keeps breaking.

### L5. Recurrence here is topical: portability, manifests, uninstall, statusline. — `[observed]`

- **What happened:** counting the noun a fix keeps returning to found the real clusters.
- **Evidence (topic → fix commits):** `windows`/`powershell`/`portable`/`CRLF` → 25 commits
  (L1); `config` → 7; `guard` → 7; `mode` → 7; `json` → 6; `uninstall` → 5
  (`ae24cd0b`, `25185a4`, `40e50d9`, `ae24cd0`, `4286903a`); `statusline` → 4.
  `tests/hooks.test.js` alone carries 10 fix commits and `tests/uninstall.test.js` 4.
- **Why it recurs:** unigram clustering finds lexically stable topics (a repo name, a
  command). A theme expressed with varied words (`windows`, `powershell`, `CRLF`,
  `portable`, `stdio`) is missed unless you probe it with an explicit keyword set.
- **The rule:** when you want the recovery signal, run both. Unigrams for the obvious
  cluster, then an explicit keyword probe for the theme you suspect:
  `git log -i --grep='windows\|powershell\|cross-platform\|portable\|CRLF\|BOM'`.

### L6. A dependency ordering was reversed and then restored. — `[observed]`

- **What happened:** PR #82 (Modern Web Guidance rung-3) was merged and then reverted, and
  the revert commit names the follow-up work it needed.
- **Evidence:** `cf9cbd5` "Revert #82 (Modern Web Guidance rung-3) and re-sync mirrors
  (#178)".
- **The rule:** `[weak]` — a single revert with no stated reason beyond re-syncing mirrors.
  Do not generalise a policy from it. What it does show is that a rule change to the skill
  body is a cross-adapter change, so a revert drags mirrors with it (L3).

### L7. Uninstall and install-cleanup keep breaking. — `[inferred]`

- **What happened:** `tests/uninstall.test.js` has a fix ratio of 1.00 (4 fixes in 4
  commits) — every commit to that test was a fix. `scripts/uninstall.js` sits at 0.80
  (4 of 5).
- **Evidence:** `ae24cd0b` "add uninstall cleanup script for state outside plugin files",
  `25185a4` "don't destroy combined statuslines on uninstall", `40e50d9` "don't crash
  uninstall on malformed settings.json", `4286903a` "ship scripts/uninstall.js in the npm
  package".
- **The rule:** any change to what install writes must be matched in the uninstall path
  and in `tests/uninstall.test.js` in the same PR. Install/uninstall symmetry is a contract,
  not two scripts.
- **Falsifier:** a `scripts/uninstall.js` change that needed no test change.

### L8. The test suite is the enforcement layer, and it is expected on every fix. — `[observed]`

- **What happened:** 42 of 70 fix commits changed test code (60%) — 36 by test file path,
  27 by diff marker. `tests/hooks-windows.test.js` exists specifically for the platform
  class in L1 and carries 6 fixes at a 0.86 ratio.
- **Evidence:** `515fb4c`, `147bcfd`, `2b426c6`, `7e6eca6`, `1469048`, `c15db8d3`,
  `a3bc7fd`, `9ec4fb8` — each lands its fix with a test change.
- **The rule:** a fix ships with the test that would have caught it. For anything in the
  L1 class, that test goes in `tests/hooks-windows.test.js`.

## Project-specific implementation rules

**Layout** — one shared implementation, thin adapters:

| Path | Owns |
| --- | --- |
| `skills/<name>/SKILL.md` | the authoritative skill bodies |
| `hooks/*.js` | the shared hook implementations |
| `pi-extension/` | the pi adapter, with its own tests |
| `.opencode/plugins/`, `.claude-plugin/`, `.codex-plugin/`, `.devin-plugin/`, `.qoder-plugin/`, `.github/plugin/` | platform manifests and adapters |
| `tests/*.test.js` | the shared suite (`node --test`) |
| `scripts/check-versions.js`, `scripts/check-rule-copies.js` | CI guards |
| `benchmarks/` | LOC and agentic benchmarks |

**Manifests** — 10 files carry a version and must agree (L2). Never bump one alone.

**Adapter rule** — keep adapters thin; point them at `skills/` and `hooks/` rather than
copying logic. Where a host only supports instructions, its copied text must stay aligned
with `AGENTS.md` (L3).

**Portability** — treat every file read, process spawn, and path build as a platform
hazard until proven otherwise (L1). The checklist from L1 is the working rule; there is no
documented one to cite.

**Commit style** — squash-merge with a PR number: `(#N)` on 80% of subjects. Conventional
prefix (`fix:`, `feat:`, `chore:`, `refactor:`, `docs:`) with an optional scope
(`fix(benchmarks):`, `fix(pi-extension):`). Multi-issue commits use two refs
(`(#260, #262) (#270)`). Include a body — `763e04d` is the model: it states the symptom,
the root cause, the fix, and why the existing test could not catch it.

**Testing** — `npm test` (Node's built-in runner), 15 test files, plus two guard scripts
wired into `.github/workflows/test.yml`:

```
run: node scripts/check-rule-copies.js
run: node scripts/check-versions.js
run: npm test
```

The guard scripts are the enforcement layer — the same pattern as an invariant test. A
written rule that is not in one of those three places will regress.

**Migrations in flight** — the adapter set is still growing (Qoder, Devin, Hermes, Grok
added inside the window). Expect a new manifest and a new `check-versions.js` entry
regularly. Do not treat the current adapter list as final.

**Intentional inconsistency** — adapters are deliberately not unified: some are native
plugins, some are copied instruction text (`docs/agent-portability.md`). Do not collapse
them into one mechanism. `[observed]`

## Known risk areas

| Rank | Path | Commits | Fix commits | Ratio | Why |
| --- | --- | --- | --- | --- | --- |
| 1 | `tests/hooks.test.js` | 20 | 10 | 0.50 | the shared hook suite; everything lands here |
| 2 | `hooks/ponytail-activate.js` | 13 | 7 | 0.54 | session activation, BOM, EPIPE, config dir |
| 3 | `pi-extension/index.js` | 14 | 7 | 0.50 | theme access, fs writes, status bar |
| 4 | `tests/hooks-windows.test.js` | 7 | 6 | **0.86** | the Windows class in L1 |
| 5 | `hooks/ponytail-config.js` | 10 | 6 | 0.60 | default-mode writes, config merging |
| 6 | `scripts/uninstall.js` | 5 | 4 | 0.80 | install/uninstall asymmetry (L7) |
| 7 | `tests/uninstall.test.js` | 4 | 4 | **1.00** | every commit here was a fix |
| 8 | `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.github/plugin/plugin.json`, `gemini-extension.json` | 16 / 13 / 9 / 11 | 0 | 0.00 | not buggy — but they are the drift surface (L2) |
| 9 | `docs/agent-portability.md` | 18 | 1 | 0.06 | high churn, low defects: the adapter surface changes often |
| 10 | `README.md` | 73 | — | — | highest churn in the repo; contributor-facing, near-zero risk |

The four manifests tie on rank 8 with zero fix commits. They are listed because their
*count* is the hazard: 10 files must agree, and none of them can fail alone (L2).

### Change couplings — files that must move together

| Pair | Co-changes | Contract |
| --- | --- | --- |
| `hooks/ponytail-instructions.js` + `tests/hooks.test.js` | 10 | hook behaviour and its suite |
| `pi-extension/index.js` + `pi-extension/test/extension.test.js` | 10 | adapter and its suite |
| `hooks/ponytail-config.js` + `tests/hooks.test.js` | 10 | config writes and the shared suite |
| `.opencode/plugins/ponytail.mjs` + `tests/opencode-plugin.test.js` | 9 | adapter and its suite |
| `pi-extension/index.js` + `pi-extension/test/helpers.test.js` | 8 | adapter and its helpers |
| `hooks/ponytail-activate.js` + `tests/hooks.test.js` | 8 | activation and the shared suite |

Every top coupling is **implementation + its own test**. That is the strongest structural
fact about this repository: the test moves with the code, always. Preserve it.

### Removed and abandoned work — do not reintroduce

| Removed | Reason (quoted) | Evidence |
| --- | --- | --- |
| PR #82, Modern Web Guidance rung-3 | "Revert #82 (Modern Web Guidance rung-3) and re-sync mirrors" | `cf9cbd5` |
| `commandWindows` in `hooks.json` | "drop commandWindows from hooks.json for Claude.ai marketplace validation" | `cc37a5d` |
| bash-only `exec` in hooks | "drop bash-only `exec` from hooks so they run under PowerShell" | `2ba0262` |
| `examples/caching.md`, `api-endpoint.md`, `date-picker.md`, `sorting.md`, `web-platform-lookup.md` | no message — example-set pruning | `[weak]` |
| `announce-v4.3.0.png`, `ponytail-v4.3.0.gif`, `assets/benchmark-loc.svg` | no message — release-asset cleanup | `[weak]` |

No path in this repository was deleted more than once, so there is no oscillation to
guard. `[observed]`

**Secret scan:** clean. No secret-shaped path was ever added
(`git log --diff-filter=A --name-only` filtered on credential patterns returns nothing).
`[observed]`

## Safe-change checklist

Before you change anything:

- [ ] `npm install && npm test` — all 15 test files plus both guard scripts must pass.
- [ ] Read [`AGENTS.md`](AGENTS.md) and
      [`docs/agent-portability.md`](docs/agent-portability.md). They are the authoritative
      adapter rules.
- [ ] `git status --porcelain` to confirm a clean tree.

While you change:

- [ ] Reading or writing a file, spawning a process, or building a path: apply all four
      L1 guards (BOM, shell quoting, interpreter resolution, CRLF).
- [ ] Bumping a version: update all 10 manifests, then run
      `node scripts/check-versions.js`.
- [ ] Adding a platform adapter: add its manifest to `check-versions.js` **and** to
      `check-rule-copies.js` in the same PR.
- [ ] Editing `AGENTS.md` or a skill body: run `node scripts/check-rule-copies.js` and
      re-sync the mirrors.
- [ ] Touching install behaviour: change `scripts/uninstall.js` and
      `tests/uninstall.test.js` in the same PR.
- [ ] Every fix ships with the test that would have caught it. Platform fixes go in
      `tests/hooks-windows.test.js`.

Before you call it done:

- [ ] Run all three CI commands locally: `node scripts/check-rule-copies.js`,
      `node scripts/check-versions.js`, `npm test`.
- [ ] Do not merge a change that only edits one adapter's copy of a rule.
- [ ] Do not add a hardcoded interpreter name (`python3`, `bash`) or an unquoted absolute
      path.

## Examples from commit history

### Example 1 — The same BOM bug, fixed twice, for two different files

```
a3bc7db  fix: strip UTF-8 BOM before parsing settings.json in ponytail-activate (#148)
9ec4fb8  fix: strip UTF-8 BOM before parsing config.json (#478)
```

- **What happened:** the identical defect — a UTF-8 BOM breaking `JSON.parse` — was fixed
  once for `settings.json` and again, much later, for `config.json`.
- **Why it repeated:** the first fix patched the call site, not the parse path. A shared
  `readJson()` that strips the BOM would have closed the class.
- **The rule it produced:** L1. Fix the shared function, not the caller.
- **Grade:** `[observed]` — both subjects name the file and the cause.

### Example 2 — Three versions advertised at once, and why the existing test missed it

```
763e04d  fix: align all version manifests to 4.8.1 + guard against drift (#260, #262) (#270)

  "The v4.8.0 release shipped with all four plugin manifests still reading 4.7.0,
   and both package.json files still at the 0.1.0 npm-init default ...
   The existing mutual-agreement check in tests/gemini-extension.test.js could
   not catch this, because all four manifests were stale at 4.7.0 together."
```

- **What broke:** users on Claude, Codex and Gemini were all told 4.7.0 was current.
- **The fix:** bump all six version files, add `scripts/check-versions.js` to CI, and assert
  the shared version equals the release tag on a tag run.
- **Why it is the best commit in the repository:** it states the symptom, the root cause,
  the fix, and the precise reason the previous guard failed. Copy its body format.
- **The rule it produced:** L2.
- **Grade:** `[observed]` — the reasoning is written down.

### Example 3 — The portability class, in date order

```
147bcfd  fix: use PowerShell $env: syntax for Windows hook paths (#26)
515fb4c  fix: make hook compatibility test cross-platform (USERPROFILE for Windows ...)
2b426c6  fix: make shared hooks parse in PowerShell (#265)
7e6eca6  fix: prevent Windows session freeze from stdin EOF deadlock (#477)
...6 more over the next four weeks...
2ba0262  fix: drop bash-only `exec` from hooks so they run under PowerShell (#527, #569)
cc37a5d  fix: drop commandWindows from hooks.json for Claude.ai marketplace validation
```

- **What repeated:** ten separate platform defects over six weeks, each found on one
  contributor's machine, each fixed independently.
- **Why it repeated:** no portability rule was ever written down, so there was nothing to
  check against.
- **The rule it produced:** L1 and L5.
- **Grade:** `[observed]` for the individual facts, `[inferred]` for "no rule existed".
  The falsifier: a portability checklist somewhere in `docs/` that I did not find.

### Example 4 — 52 of 70 fixes could not be tied to a recent commit

```
70 fix commits
 3 attributable to an earlier commit with 2+ follow-up fixes
52 unattributed — no earlier non-fix commit within 72h shares a file
```

- **What happened:** the timing-based recurrence detector went quiet. On a solo WIP
  repository it is the strongest signal; here it found almost nothing.
- **Why:** a squash-merged fix answers an issue, not the merge that introduced the problem.
  Contributors fix `main` weeks later.
- **The rule it produced:** L4 and L5 — switch to the topic probe.
- **Grade:** `[observed]` — the attribution counts are mechanical.

### Example 5 — The revert that had to carry the mirrors with it

```
cf9cbd5  Revert #82 (Modern Web Guidance rung-3) and re-sync mirrors (#178)
```

- **What happened:** a rule change to the skill body was merged, then reverted, and the
  revert also had to re-sync the adapter mirrors.
- **Why it matters:** a rule edit here is a multi-adapter edit, and so is a revert — which
  is why `check-rule-copies.js` exists. See L3.
- **Grade:** `[observed]` for the symmetry; `[weak]` for *why* #82 was reverted.

---

## Analysis notes

- **Coverage:** 202 non-merge commits out of 210 (merge commits excluded from the
  recurrence pass so a squashed PR is counted once); 100% of history;
  2026-06-12 .. 2026-08-08; 68 contributor emails, top author at 77 commits (37%).
- **Prior documents found and how they were used (Phase 0.2):** `AGENTS.md`,
  `docs/agent-portability.md` (18 commits of churn), `docs/platform-native.md`,
  `skills/ponytail/SKILL.md`. Cited, not duplicated.
- **Contradiction found:** none. The prior documents are accurate. What the history adds is
  that `docs/agent-portability.md` covers *adapters* while the actual defect class is
  *platforms* — so the document exists and the lesson was still missing.
- **Not covered:** `*.md` prose, `assets/`, and `benchmarks/*.json` results were excluded
  from churn and coupling so generated and documentation files would not distort the
  counts. `README.md` at 73 commits is reported as context, not as a hazard.
- **Commit weighting was not applied**, although 80% of subjects end with `(#N)` — the
  condition where it helps. With only 70 fix commits and 34% dev-loop subjects, weighting
  would have shrunk the portability cluster below the reporting threshold. Deliberate choice.
- **Recurrence method shift:** R1 (timing) produced 3 usable rows; R6 (topic) plus an
  explicit keyword probe produced the real finding. On a PR-driven repository, trust the
  topic probe.
- **Weak signals:** the `examples/*.md` and `assets/*` deletions have no explanatory commit,
  so their removal reasons are guesses. The two R4 keyword hits (`084f10fb4` "ship the
  missing /ponytail-help command", `39bad58d4` "guard pi before_agent_start") are lexical
  matches on "missing"/"against", not genuine repeats — treated as false positives.
- **Unknowns:** whether a portability checklist exists in a location this run did not
  search; why #82 was reverted; whether the 8 merge commits carried review discussion that
  would upgrade any `[inferred]` rule here to `[observed]`.
- **This is the only target with real multi-author review history**, and it is where the
  method changed most: quick-remedy attribution and `[weak]`-free timelines both stopped
  working here.
