# Project Lessons — papervault

> Derived from git history. Last analyzed commit: `b24ef97` (2026-07-21).
> Range: `9d89c9d` .. `b24ef97` (66 commits, 2026-07-20 21:27 .. 2026-07-21 20:35).
> Grades: `[observed]` stated in a commit/PR, `[inferred]` deduced from diffs,
> `[weak]` one data point or ambiguous.

## Executive summary

papervault is a single-binary Rust desktop PDF search and preview app (egui/eframe,
Tantivy, rusqlite, pdfium-render) built in one 23-hour session on 2026-07-20/21: 66
commits, of which **35 are `fix:` commits (53%)**. The whole feature set landed first
and was then repaired in three bursts. `src/app.rs` is the god object — 33 of 66
commits touch it, 22 of those are fixes. Three lessons dominate: (**1**) a PDF text
path and a PDF render path exist on purpose and must not be merged; (**2**) `pdfium`
must be owned by exactly one thread — every attempt to share it hung the process;
(**3**) anything built inside `src/app.rs` will be fixed repeatedly, because that file
has no boundary. There is **no CI and no dedicated test file**; 49 tests live inline in
9 `#[cfg(test)]` modules, and only 7 of 35 fixes changed test code. Read this before
your first edit to `src/app.rs`, `src/preview/pdf_render.rs`, or
`src/indexer/extractors/pdf.rs`.

**Read this first if you are about to touch:** `src/app.rs` (see Known risk areas).

## Lessons learned from past commits

### L1. `pdfium` must be owned by exactly one thread. Never share it. — `[observed]`

- **What happened:** the renderer hung on `Pdfium::bind_to_library` when pdfium was
  initialized or used from more than one thread. A sequence of fixes tried to make
  sharing work — a feature flag, a global mutex, a narrower lock — before the code was
  restructured so the renderer thread owns the binding outright.
- **Evidence:** `a815c24` "debug: pinpoint bind_to_library hang with eprintln
  before/after", `f22d42f` "fix: enable thread_safe feature for pdfium-render — root
  cause of PDF render...", `7eca893` "fix: serialize FPDF_InitLibrary() across threads
  with global Mutex", `1b09924` "fix: shrink lock scope, add render coalescing",
  `be40850` "fix: pre-init pdfium on main thread before spawning worker threads",
  `6cdcbe8` "fix: keep pre-init Pdfium alive with mem::forget"
- **Why it recurs:** the fix is a *structural* constraint, not a call-site fix. Any new
  code that reaches for a `Pdfium` handle reintroduces the hang.
- **The rule:** never add a second `Pdfium` instance or pass a handle across threads.
  `PdfRenderer` owns it privately and the comment at `src/preview/pdf_render.rs:24`
  states the reason — keep that comment. If you need pdfium elsewhere, send a message to
  the renderer thread instead.

### L2. There are two PDF paths on purpose. Do not merge them. — `[observed]`

- **What happened:** `pdfium` was moved out of the indexing path and replaced with the
  pure-Rust `pdf-extract` crate. The removal is named for the lock it deleted, which
  shows the motive was L1, not "one PDF library is cleaner".
- **Evidence:** `292ee36` "fix: switch indexer to pure-Rust pdf-extract, remove
  pdfium_lock"; `Cargo.toml` currently lists **both** `pdfium-render = "0.8"` and
  `pdf-extract = "0.9"`.
- **The rule:** text extraction uses `pdf-extract` (`src/indexer/extractors/pdf.rs`);
  rasterising a page uses `pdfium-render` (`src/preview/pdf_render.rs`). Do not unify
  them. Consolidating back onto pdfium reintroduces L1; removing pdfium breaks preview.

### L3. Do not add fields to a runtime stop path one at a time. — `[observed]`

- **What happened:** `c777cbf` cleared "old channel clones" before stopping the folder
  runtime. Fifty minutes later `f19608f` had to add the two shutdown fields that the
  first commit missed — its own subject starts with "also".
- **Evidence:** `c777cbf` "fix: clear old channel clones before stopping runtime"
  (`src/app.rs`, `src/runtime.rs`), then `f19608f` "fix: also clear watcher_shutdown_tx
  and watcher_shutdown_flag before stop" (`src/app.rs` only)
- **Why it recurs:** the shutdown fields live in more than one struct, so a grep for one
  name finds the others and a hand-written clear list always misses one. This is the only
  commit in the history whose message admits a repeat.
- **The rule:** when you change what a runtime stop clears, enumerate every field of
  `FolderRuntime` and the watcher before writing the list, and clear them in one commit.

### L4. Trace before you fix. Five bugs were solved this way. — `[observed]`

- **What happened:** every difficult bug in this repo was preceded by a `debug:`
  commit that added tracing, not a fix attempt. The pdfium saga is the clearest case:
  `c0968c1` traces thread existence, `a815c24` pinpoints the hang, and only then do the
  fixes land.
- **Evidence:** `c0968c1`, `86fc6d3`, `a815c24`, `8e6fdf8`, `7a2229c` — 5 of 66 commits
  use the `debug:` prefix.
- **The rule:** for a bug you cannot reproduce from reading the code, land a `debug:`
  commit that adds tracing first. Fixing before tracing is what produced three fix
  storms (L5).

### L5. Land one unit at a time. Three fix storms happened from landing whole subsystems. — `[inferred]`

- **What happened:** three runs of 5, 5, and 6 consecutive fix commits, each inside
  1.5 hours, with no intervening feature commit.
- **Evidence:** 5 fixes `d54a8e1`..`42c9df9` over 1.1h; 5 fixes `6e1698d`..`634cc70`
  over 1.5h; 6 fixes `1a33808`..`f19608f` over 0.9h. The two feature commits that
  preceded them are `8dd1fd8` "feat: implementation — all 13 units scaffolded, 19/24
  tests pass" and `68b62f9` "feat: wire main.rs threads + tag panel UI (U13 complete)".
- **Why it recurs:** `8dd1fd8` drew 3 follow-up fixes inside 15 hours
  (`search/engine.rs`, `indexer/extractors/pdf.rs`, `preview/pdf_render.rs`), and
  `68b62f9` drew 4 inside 1.2 hours (`tags/store.rs`, `app.rs`, `main.rs`). A commit
  that lands 13 units, or that re-wires every thread, cannot be reviewed or bisected.
- **The rule:** one implementation unit per commit. The unit list already exists in
  `docs/plans/2026-01-15-001-feat-pdf-search-viewer-plan.md` — use it as the commit
  sequence.

### L6. Do not set `panic = "abort"` in the release profile. — `[observed]`

- **What happened:** a `perf:` commit added `panic = "abort"`; a later `fix:` added it
  back out eight hours later.
- **Evidence:** `1c98217` "perf: release profile, reduce allocs in search hot path,
  HashSet tag filters", then `fd84001` "fix: remove panic=abort from release profile".
  `Cargo.toml` now has `[profile.release] lto = true` and no `panic` key.
- **Why it recurs:** `panic = "abort"` is a standard release-profile line, so it is
  easy to add again from muscle memory. It cost this project a fix.
- **The rule:** `[profile.release]` stays as `lto = true` only. Do not add
  `panic = "abort"`.

### L7. `src/app.rs` has no boundary, so it is fixed constantly. — `[inferred]`

- **What happened:** `src/app.rs` appears in 7 distinct coupling pairs at 5 or more
  co-changes, more than any other file. That is not a set of contracts; it is one file
  reachable from everywhere.
- **Evidence:** 33 of 66 commits touch `src/app.rs`; 22 of those are fixes (ratio
  0.67). Couplings: `app.rs + main.rs` 12, `app.rs + tags/store.rs` 11,
  `app.rs + indexer/pipeline.rs` 11, `app.rs + search/engine.rs` 10,
  `app.rs + preview/pdf_render.rs` 9.
- **Falsifier:** if a later commit shows `app.rs` changes that do not ripple, the
  "no boundary" reading is wrong.
- **The rule:** put new state and new event handling in the module that owns the data
  (`src/tags/store.rs`, `src/indexer/pipeline.rs`, `src/runtime.rs`), and let `app.rs`
  only dispatch. Adding a subsystem inside `app.rs` has never worked here.

### L8. Only 7 of 35 fix commits changed a test. — `[inferred]`

- **What happened:** fixes land without a regression test roughly 80% of the time.
- **Evidence:** 35 fix commits; 0 touch a separate test file; 7 change test code inside
  a module (`a129cf0`, `d54a8e1`, `bd50c54`, `8f78d74`, `6e1698d`, `097aaab`, `b6588d8`).
  `d54a8e1` "pdfium tests gracefully skip when DLL unavailable" is the pattern worth
  copying.
- **The rule:** a fix for a reoccurring failure gets a test in the same commit. The
  tests already have a home — the inline `#[cfg(test)] mod tests` block in the file
  that owns the bug.

## Project-specific implementation rules

**Layout** — the modules are fixed and small. Put code where the data lives:

| Directory | Owns |
| --- | --- |
| `src/indexer/` | Tantivy index, extractors, pipeline, stages |
| `src/search/` | query building, schema, engine |
| `src/tags/` | tag model and rusqlite store |
| `src/preview/` | syntax highlighting and PDF rasterisation |
| `src/watcher/` | `notify` file watching |
| `src/runtime.rs` | `FolderRuntime` — per-folder indexes and shutdown |
| `src/app.rs` | egui state and dispatch **only** |
| `docs/plans/` | one dated plan per non-trivial change |

**Plans** — every non-trivial change gets a plan file before code:
`docs/plans/YYYY-MM-DD-NNN-<type>-<slug>-plan.md`. Five exist for 2026-07-21 alone,
including `-006-fix-pdfium-lock-scope-plan.md` and `-007-pure-rust-extraction-plan.md`.
Follow the numbering. `[observed]` — every `debug:` and multi-fix sequence has one.

**Errors** — `anyhow::Result` with `.context(...)`. Do not `unwrap()` or `expect()` on
anything that touches the filesystem, the DLL, or a channel; replace a fragile `unwrap`
with `expect` only if you add the invariant to the message. `[inferred]` — `cb9264f`
"fix: handle Mutex poisoning, replace fragile unwrap with expect".

**Threads** — background work goes over `crossbeam::channel`. The renderer is a
dedicated thread; the UI never calls pdfium. `[observed]` — `src/preview/pdf_render.rs`
documents "Runs on a dedicated thread, receives render requests and sends back RGBA
bitmaps".

**Shutdown** — any new thread or channel must be added to the shutdown path of
`FolderRuntime` **and** the app's stop routine in the same commit. See L3.

**Commit style** — Conventional Commits, lowercase, with an em-dash detail clause:
`fix: <thing> — <detail>`. Observed prefixes: `fix:` 35, `docs:` 8, `debug:` 5,
`feat:` 4, `perf:` 3, `chore:` 2, `refactor:` 1, plus scoped `feat(search):`,
`feat(runtime):`. Use `debug:` for a tracing-only commit — it is a real convention here,
not noise.

**Testing** — `cargo test`. There is no CI and no `tests/` directory. Tests are inline
`#[cfg(test)] mod tests` blocks in the module under test: 9 blocks, 49 `#[test]`
functions, densest in `src/search/engine.rs` (9) and `src/tags/store.rs` (7). Follow
that shape: a new test goes in the owning module, not a new file. Tests that need the
DLL must skip gracefully rather than fail (`d54a8e1` is the template). `docs/test-plan.md`
is the intended scope; treat it as aspirational, not as coverage.

**Migrations in flight** — none identified. The history is 23 hours old and every
subsystem settled before the last commit.

**Intentional inconsistencies** — one, and it matters:

| Area | Shape A | Shape B | Why it is intentional | Evidence |
| --- | --- | --- | --- | --- |
| PDF reading | `pdf-extract` (indexing text) | `pdfium-render` (rasterising pages) | pdfium cannot be shared across threads, so the indexer was moved off it | `292ee36` |

## Known risk areas

| Rank | Path | Commits | Fix commits | Fix ratio | Why |
| --- | --- | --- | --- | --- | --- |
| 1 | `src/app.rs` | 33 | 22 | 0.67 | god object, no boundary (L7) |
| 2 | `src/preview/pdf_render.rs` | 17 | 11 | 0.65 | pdfium threading (L1) |
| 3 | `src/indexer/extractors/pdf.rs` | 9 | 8 | **0.89** | highest fix density in the repo |
| 4 | `src/indexer/pipeline.rs` | 14 | 10 | 0.71 | indexing orchestration |
| 5 | `src/main.rs` | 16 | 10 | 0.62 | thread wiring and startup order |
| 6 | `src/search/engine.rs` | 13 | 9 | 0.69 | tokenizer/reader registration |
| 7 | `src/tags/store.rs` | 12 | 7 | 0.58 | rusqlite schema and key handling |
| 8 | `Cargo.toml` | 8 | 4 | 0.50 | profile and DLL-adjacent settings (L6) |

### `src/preview/pdf_render.rs` — pdfium ownership

- **Failure mode:** the process hangs, with no panic and no error, inside
  `bind_to_library` or on the first render. Seen twice (`a815c24`, `c0968c1`).
- **Guard:** the `Pdfium` handle stays private to the renderer thread. Do not add a
  Mutex, do not re-init, do not move the binding.
- **Evidence:** `a815c24`, `7eca893`, `be40850`, `6cdcbe8`

### `src/indexer/extractors/pdf.rs` — 8 fixes in 9 commits

- **Failure mode:** extraction silently returns nothing, or panics on a malformed PDF.
  `1a33808` "fix: warn when no extractor available for a file" shows the silent path.
- **Guard:** always emit a warning when an extractor is missing rather than returning
  empty. `pdf-extract` is a different crate from `pdfium-render`; do not swap them (L2).
- **Evidence:** `1a33808`, `d54a8e1`, `292ee36`

### `src/app.rs` — everything

- **Failure mode:** a change to app state breaks selection, search results, or the
  preview, because all three are read from the same struct.
- **Guard:** `097aaab` "fix: correctness fixes — unicode safety, render identity,
  selection, progress" is the shape of the failure. Add a test for the state transition
  you touch.
- **Evidence:** 22 fix commits; `2313209` "fix: browse_file should not overwrite
  search_results".

### Change couplings — files that must move together

| Pair | Co-changes | Reading |
| --- | --- | --- |
| `src/app.rs` + `src/main.rs` | 12 | mechanical: `main.rs` wires `app.rs`. Informational only. |
| `src/app.rs` + `src/tags/store.rs` | 11 | real: tag UI and tag store change together |
| `src/app.rs` + `src/indexer/pipeline.rs` | 11 | real: progress reporting is split across both |
| `src/indexer/extractors/pdf.rs` + `src/preview/pdf_render.rs` | 7 | real: the two PDF paths must agree on file handling |
| `src/main.rs` + `src/watcher/watcher.rs` | 6 | real: shutdown wiring (L3) |

The `app.rs` pairs are the symptom in L7, not a contract to preserve. The last three
rows are contracts: touch one side and check the other.

### Removed and abandoned work — do not reintroduce

| Removed | When | Reason (quoted) | Evidence |
| --- | --- | --- | --- |
| `panic = "abort"` in the release profile | 2026-07-21 | "fix: remove panic=abort from release profile" | `fd84001` |
| pdfium in the indexing path | 2026-07-21 | "switch indexer to pure-Rust pdf-extract, remove pdfium_lock" | `292ee36` |
| A global pdfium `Mutex` | 2026-07-21 | "shrink lock scope", then removal with the indexer switch | `1b09924`, `292ee36` |

No path was ever deleted from this repository (`--diff-filter=D` returns nothing), so
there is no removed file to guard. Three *settings and mechanisms* were removed as
above. `[observed]`

## Safe-change checklist

Before you change anything:

- [ ] Run `cargo test`; it must pass before you start. There is no CI, so this is the
      only gate.
- [ ] Run `cargo build --release` if you touched `Cargo.toml` or thread wiring, and set
      a 30-second timeout. The pdfium hang produces no output, so a build that never
      returns has not crashed — it has deadlocked (L1).
- [ ] Confirm the tree is clean: `git status --porcelain`.
- [ ] Read `src/preview/pdf_render.rs` lines 1-100 if your change is anywhere near PDF
      handling.

While you change:

- [ ] One implementation unit per commit. Use the unit list in
      `docs/plans/2026-01-15-001-feat-pdf-search-viewer-plan.md`, and add a plan file in
      `docs/plans/` for anything non-trivial.
- [ ] Do not add a second `Pdfium` handle, a `Mutex` around one, or a cross-thread
      handle, and do not merge the text-extraction path with the render path.
      `pdf-extract` indexes; `pdfium-render` rasterises. Send a message to the renderer
      thread instead.
- [ ] If you add a thread, a channel, or a shutdown field, extend the runtime stop path
      in the **same** commit, enumerating every field (L3).
- [ ] Put new state in the module that owns the data. Do not add a subsystem to
      `src/app.rs`.
- [ ] For a bug you cannot reproduce by reading, land a `debug:` commit with tracing
      first (L4).

Before you call it done:

- [ ] Run `cargo test`. Every test that passed before still passes. If you fixed a
      failure that had happened before, add a `#[test]` in the owning module's
      `#[cfg(test)] mod tests` block.
- [ ] If you touched one side of a coupling pair, check the other side.
- [ ] Do not edit `[profile.release]` beyond `lto = true`.

## Examples from commit history

### Example 1 — The pdfium hang, and the five attempts before the right fix

```
a815c24  debug: pinpoint bind_to_library hang with eprintln before/after
f22d42f  fix: enable thread_safe feature for pdfium-render — root cause of PDF render...
7eca893  fix: serialize FPDF_InitLibrary() across threads with global Mutex
dc77133  fix: PDF rendering now works — serialized FPDF_InitLibrary, clean debug outp...
1b09924  fix: shrink lock scope, add render coalescing
be40850  fix: pre-init pdfium on main thread before spawning worker threads
6cdcbe8  fix: keep pre-init Pdfium alive with mem::forget
292ee36  fix: switch indexer to pure-Rust pdf-extract, remove pdfium_lock
```

- **What changed:** pdfium initialisation moved from per-call to pre-init on the main
  thread, then a global mutex, then narrower locking, and finally the indexer was moved
  off pdfium entirely.
- **What broke:** the renderer thread hung with no error while binding the library.
- **The fix:** the renderer thread owns the binding. `src/preview/pdf_render.rs:24`
  records the reason: "No Mutex needed since there is only one renderer thread."
- **The rule it produced:** see L1 and L2.
- **Grade:** `[observed]` — the sequence and the reason are both in the messages.

### Example 2 — A fix that needed a second fix, fifty minutes later

```
c777cbf  fix: clear old channel clones before stopping runtime
f19608f  fix: also clear watcher_shutdown_tx and watcher_shutdown_flag before stop
```

- **What repeated:** clearing part of the shutdown state, then having to come back for
  the rest. `f19608f` is the only commit in the repo whose message admits it ("also").
- **Why it repeated:** the fields live in more than one struct, so a hand-written clear
  list misses one.
- **The rule it produced:** see L3.
- **Grade:** `[observed]` for the fact, `[inferred]` for the mechanism.

### Example 3 — A performance setting reverted eight hours later

```
1c98217  perf: release profile, reduce allocs in search hot path, HashSet tag filters
fd84001  fix: remove panic=abort from release profile
```

- **What was tried:** adding `panic = "abort"` to `[profile.release]` alongside `lto`.
- **Why it failed:** it was removed by a `fix:` commit with no body. `[weak]` — the
  history does not say why. Most likely it aborted on a recoverable panic, but that is
  a guess.
- **The rule it produced:** see L6. The rule stands on the removal, not the reason.
- **Grade:** `[observed]` for the removal, `[weak]` for the cause.

### Example 4 — Three fix storms in one day

```
8dd1fd8  feat: implementation — all 13 units scaffolded, 19/24 tests pass
   → 3 fixes, span 0.3h-14.9h (a129cf0, d54a8e1, 5b49c47)
   → then 5 consecutive fixes (d54a8e1 .. 42c9df9, 1.1h)
68b62f9  feat: wire main.rs threads + tag panel UI (U13 complete)
   → 4 fixes, span 0.4h-1.2h (bd50c54, 8f78d74, f0da898, 42c9df9)
7a2229c  debug: add pipeline tracing for first-launch indexing investigation
   → 6 fixes, span 0.1h-1.0h (1a33808 .. f19608f)
```

- **What changed:** 13 units and a thread-wiring change landed as single commits, inside a
  23-hour session where commits were minutes apart.
- **What broke:** both feature commits drew multi-file repair within hours —
  `8dd1fd8` on `search/engine.rs`, `indexer/extractors/pdf.rs` and
  `preview/pdf_render.rs`; `68b62f9` on `tags/store.rs`, `app.rs` and `main.rs`. Storm 1
  follows `8dd1fd8` (02:26 → 02:55), storm 2 follows `9a709f6` "perf: pre-allocate search
  result vector with capacity" (10:46 → 11:24), storm 3 follows `7a2229c` (14:22 →
  14:31).
- **The rule it produced:** see L5.
- **Grade:** `[inferred]` — the storms are in the data; the causal link to commit size
  is a reading, and the falsifier is a similarly sized commit that needed no fixes.

### Example 5 — The only test-aware fix that is worth copying

```
d54a8e1  fix: pdfium tests gracefully skip when DLL unavailable
```

- **What changed:** tests that need `pdfium.dll` skip instead of failing when the DLL
  is absent.
- **Why it matters:** the DLL is not in the repository, so a hard failure would make
  `cargo test` red on any clean machine and the team would stop running it.
- **The rule it produced:** see the Testing rule in Project-specific implementation
  rules.
- **Grade:** `[observed]`

---

## Analysis notes

- **Coverage:** 66 commits, 100% of history; 33 distinct paths under `src/` plus
  `Cargo.toml`. Analysis window was the entire repo, so no rule here is truncated by a
  window.
- **Not covered:** `*.md`, `Cargo.lock`, and `docs/` were excluded from churn and
  coupling so that documentation commits would not distort the counts. `docs/plans/` was
  then read directly for the planning convention.
- **Weak signals:**
  - The reason for the `panic = "abort"` removal is unknown; only the removal is
    evidence (Example 3).
  - No path was ever deleted, so there is no "removed feature" lesson. Any claim about
    abandoned features would be invented.
  - Couplings were counted over all 66 commits. With a corpus this small, a pair at
    count 5 is three events away from being noise.
- **Unknowns:**
  - The repository is 23 hours old and single-author. **None of these rules has survived
    a second developer or a second month.** Treat every rule as a hypothesis about
    intent, not as a settled convention.
  - `docs/test-plan.md` describes intended coverage. Nothing in the history shows it
    being followed, so its contents were not converted into rules.
- **Thin history warning:** a lessons document for a one-day repository is worth
  exactly what its commits say. The recurrence signals (R1, R2, R4) are the only
  findings here that would not be visible from reading the code alone.
