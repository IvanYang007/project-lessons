# Recurrence signals

Analyzed 66 commits; 35 are fix commits (53%).

Window: 72h. Thresholds: fix-cluster >= 3, fix-storm >= 5.

## R1 - Quick-remedy attribution (fix within 72h of a non-fix commit)

Each fix is attributed to the nearest earlier NON-fix commit it shares a file
with. A commit that needed several follow-up fixes is the signal. Read that
commit's diff to find what it omitted.

| follow-up fixes | earlier commit | span (h) | most-shared files |
| --- | --- | --- | --- |
| 6 | `7a2229c4a` debug: add pipeline tracing for first-launch indexin | 0.1-1.0 | `src/app.rs`, `src/indexer/pipeline.rs`, `src/runtime.rs` |
| 5 | `9a709f6a9` perf: pre-allocate search result vector with capacit | 0.6-2.1 | `src/search/engine.rs`, `src/app.rs`, `src/tags/store.rs` |
| 5 | `deb279185` feat: file browser panel, recursive subfolder indexi | 0.1-8.6 | `src/app.rs`, `src/watcher/watcher.rs`, `Cargo.toml` |
| 5 | `a815c24c0` debug: pinpoint bind_to_library hang with eprintln b | 2.5-4.2 | `src/preview/pdf_render.rs` |
| 4 | `68b62f9ff` feat: wire main.rs threads + tag panel UI (U13 compl | 0.4-1.2 | `src/tags/store.rs`, `src/app.rs`, `src/main.rs` |
| 3 | `8dd1fd854` feat: implementation — all 13 units scaffolded, 19/2 | 0.3-14.9 | `src/search/engine.rs`, `src/indexer/extractors/pdf.rs`, `src/preview/pdf_render.rs` |
| 2 | `c0968c114` debug: add eprintln traces for renderer thread exist | 3.7-3.9 | `src/runtime.rs` |
| 1 | `353e7fb5d` feat(runtime): add FolderRuntime with per-folder ind | 0.1 | `src/app.rs` |
| 1 | `ddb4f3a44` feat: atomic config save, debug console, license met | 0.2 | `src/main.rs` |
| 1 | `1c982174c` perf: release profile, reduce allocs in search hot p | 0.2 | `src/app.rs` |
| 1 | `ac6ad1f28` chore: fix clippy warnings — empty if, map_or -> is_ | 0.1 | `src/app.rs` |
| 1 | `b6eeaf039` perf: faster startup, eager pdfium init, PDF zoom | 0.0 | `src/app.rs` |

### The fixes behind the worst offenders

- `7a2229c4a` 2026-07-21 14:22 debug: add pipeline tracing for first-launch indexing investigation
  - `1a338088f` +0.1h  fix: warn when no extractor available for a file, add pdfium.dll
  - `c21ee3f2d` +0.2h  fix: stop old FolderRuntime on background thread to prevent UI freeze
  - `a590a4f39` +0.3h  fix: async folder switch — stop old runtime on background thread
  - `074479aee` +0.4h  fix: propagate background thread errors to UI, clean first-launch path
  - `c777cbf29` +0.9h  fix: clear old channel clones before stopping runtime
  - `f19608f88` +1.0h  fix: also clear watcher_shutdown_tx and watcher_shutdown_flag before stop
- `9a709f6a9` 2026-07-21 10:46 perf: pre-allocate search result vector with capacity
  - `6e1698d19` +0.6h  fix: resolve P0 issues — tag sync, shutdown, snippets, folder picker, reconc
  - `bd6ce2eda` +0.8h  fix: wire reconcile() startup + thread join on exit (P0-2, P0-3)
  - `7d467afae` +1.0h  fix: remove dead_code annotation from reconcile (now called from main.rs)
  - `c92e47e4c` +1.3h  fix: hide console window with windows_subsystem attribute
  - `634cc70cf` +2.1h  fix: search engine init failure & TextEdit focus on Windows
- `deb279185` 2026-07-21 15:54 feat: file browser panel, recursive subfolder indexing, layout restructure
  - `23132098d` +0.1h  fix: browse_file should not overwrite search_results, extract load_text_prev
  - `cb9264f05` +0.2h  fix: handle Mutex poisoning, replace fragile unwrap with expect
  - `4ee4ee71e` +0.5h  fix: file browser preview, PDF page nav, search result font size
  - `173f70a94` +1.2h  fix: PDF render pipeline, graceful degradation, search result font
  - `fd8400130` +8.6h  fix: remove panic=abort from release profile
- `a815c24c0` 2026-07-21 17:58 debug: pinpoint bind_to_library hang with eprintln before/after
  - `f22d42f04` +2.5h  fix: enable thread_safe feature for pdfium-render — root cause of PDF render
  - `7eca89370` +3.0h  fix: serialize FPDF_InitLibrary() across threads with global Mutex
  - `dc77133a2` +3.1h  fix: PDF rendering now works — serialized FPDF_InitLibrary, clean debug outp
  - `1b0992451` +3.5h  fix: shrink lock scope, add render coalescing
  - `292ee368a` +4.2h  fix: switch indexer to pure-Rust pdf-extract, remove pdfium_lock
- `68b62f9ff` 2026-07-21 02:53 feat: wire main.rs threads + tag panel UI (U13 complete)
  - `bd50c5459` +0.4h  fix: resolve all High/Medium code review findings
  - `8f78d741f` +0.9h  fix: High-severity bugs — config, tag dup, total_hits overflow
  - `f0da89862` +1.1h  fix: Medium-severity issues — foreign keys, old-hash cleanup, write order
  - `42c9df91b` +1.2h  fix: bounds check in assign_tag_to_selected
- `8dd1fd854` 2026-07-21 02:26 feat: implementation — all 13 units scaffolded, 19/24 tests pass
  - `a129cf0d0` +0.3h  fix: resolve search engine test failures — tokenizer registration + reader r
  - `d54a8e1bd` +0.5h  fix: pdfium tests gracefully skip when DLL unavailable
  - `5b49c4700` +14.9h  fix: correct pdfium.dll (Chromium 7543), step-level renderer diagnostics
- `c0968c114` 2026-07-21 17:48 debug: add eprintln traces for renderer thread existence (U1-U4)
  - `be408500f` +3.7h  fix: pre-init pdfium on main thread before spawning worker threads
  - `6cdcbe8af` +3.9h  fix: keep pre-init Pdfium alive with mem::forget
- `353e7fb5d` 2026-07-21 13:32 feat(runtime): add FolderRuntime with per-folder indexes and graceful shutdown
  - `097aaabbd` +0.1h  fix: correctness fixes — unicode safety, render identity, selection, progres

## R2 - Fix storms (>= 5 consecutive fix commits)

A run of fixes with no intervening feature or refactor commit. The work landed
before it was ready. Ask what review or test step was skipped.

- **5 consecutive fixes** over 1.1h: `d54a8e1bd` .. `42c9df91b` (2026-07-21 02:55)
  - first: fix: pdfium tests gracefully skip when DLL unavailable
  - last:  fix: bounds check in assign_tag_to_selected
- **5 consecutive fixes** over 1.5h: `6e1698d19` .. `634cc70cf` (2026-07-21 11:24)
  - first: fix: resolve P0 issues — tag sync, shutdown, snippets, folder picker, reconcil
  - last:  fix: search engine init failure & TextEdit focus on Windows
- **6 consecutive fixes** over 0.9h: `1a338088f` .. `f19608f88` (2026-07-21 14:31)
  - first: fix: warn when no extractor available for a file, add pdfium.dll
  - last:  fix: also clear watcher_shutdown_tx and watcher_shutdown_flag before stop

## R3 - Fix-cluster files (>= 3 fix commits)

| fixes | path |
| --- | --- |
| 22 | `src/app.rs` |
| 11 | `src/preview/pdf_render.rs` |
| 10 | `src/indexer/pipeline.rs` |
| 10 | `src/main.rs` |
| 9 | `src/search/engine.rs` |
| 8 | `src/indexer/extractors/pdf.rs` |
| 7 | `src/tags/store.rs` |
| 6 | `src/runtime.rs` |
| 5 | `src/watcher/watcher.rs` |
| 4 | `src/search/query.rs` |
| 4 | `Cargo.toml` |
| 3 | `src/preview/highlight.rs` |
| 3 | `src/indexer/extractors/mod.rs` |
| 3 | `src/indexer/extractors/text.rs` |
| 3 | `src/search/schema.rs` |

## R4 - Fix commits that admit a repeat

- `f19608f88` (2026-07-21 15:24) fix: also clear watcher_shutdown_tx and watcher_shutdown_flag before stop

## R5 - Fix commits that also changed test code

Two detectors are combined:
  1. the commit touches a separate test file (`test_*`, `*.spec.*`, `tests/`)
  2. the commit's diff adds or removes a test marker (`#[test]`, `def test_`,
     `describe(`, `it(`) - this catches colocated and inline tests

7 of 35 fix commits changed test code (0 by file path, 7 by diff marker).

A low number means fixes ship without a regression test. A non-zero number means
the test was missing or asserted the wrong thing.

- `a129cf0d0` fix: resolve search engine test failures — tokenizer registration + re (diff marker)
- `d54a8e1bd` fix: pdfium tests gracefully skip when DLL unavailable (diff marker)
- `bd50c5459` fix: resolve all High/Medium code review findings (diff marker)
- `8f78d741f` fix: High-severity bugs — config, tag dup, total_hits overflow (diff marker)
- `6e1698d19` fix: resolve P0 issues — tag sync, shutdown, snippets, folder picker,  (diff marker)
- `097aaabbd` fix: correctness fixes — unicode safety, render identity, selection, p (diff marker)
- `b6588d812` fix: code review findings — stale selection, silent tag failure, chann (diff marker)

## File activity (fix ratio)

| fix ratio | fixes | total | path |
| --- | --- | --- | --- |
| 0.89 | 8 | 9 | `src/indexer/extractors/pdf.rs` |
| 0.80 | 4 | 5 | `src/search/query.rs` |
| 0.75 | 3 | 4 | `src/preview/highlight.rs` |
| 0.75 | 3 | 4 | `src/search/schema.rs` |
| 0.75 | 3 | 4 | `src/indexer/extractors/mod.rs` |
| 0.75 | 3 | 4 | `src/indexer/extractors/text.rs` |
| 0.71 | 10 | 14 | `src/indexer/pipeline.rs` |
| 0.69 | 9 | 13 | `src/search/engine.rs` |
| 0.67 | 22 | 33 | `src/app.rs` |
| 0.67 | 2 | 3 | `src/error.rs` |
| 0.65 | 11 | 17 | `src/preview/pdf_render.rs` |
| 0.62 | 10 | 16 | `src/main.rs` |
| 0.62 | 5 | 8 | `src/watcher/watcher.rs` |
| 0.60 | 6 | 10 | `src/runtime.rs` |
| 0.58 | 7 | 12 | `src/tags/store.rs` |
| 0.50 | 4 | 8 | `Cargo.toml` |
| 0.50 | 2 | 4 | `src/config.rs` |
| 0.50 | 1 | 2 | `src/tags/model.rs` |
| 0.50 | 1 | 2 | `src/watcher/mod.rs` |

