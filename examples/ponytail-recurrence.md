# Recurrence signals

Analyzed 202 commits; 70 are fix commits (34%).

Window: 72h. Thresholds: fix-cluster >= 3, fix-storm >= 5.

## R1 - Quick-remedy attribution (fix within 72h of a non-fix commit)

Each fix is attributed to the nearest earlier NON-fix commit it shares a file
with. A commit that needed several follow-up fixes is the signal. Read that
commit's diff to find what it omitted.

Only commits that drew TWO OR MORE follow-up fixes are listed. A commit that drew
exactly one is ordinary course-correction, not a signal.

| follow-up fixes | earlier commit | span (h) | most-shared files |
| --- | --- | --- | --- |
| 4 | `d5f4ffdd6` pi-extension: make startup notification opt-out via  | 5.0-14.6 | `pi-extension/index.js`, `pi-extension/test/helpers.test.js` |
| 3 | `1715abcca` feat(hooks): opt-in agent-type scoping for SubagentS | 0.7-8.4 | `tests/hooks.test.js` |
| 2 | `8c279cbfb` feat: add pi extension (#1) | 7.8-54.1 | `pi-extension/test/helpers.test.js`, `hooks/ponytail-instructions.js`, `hooks/ponytail-config.js`, `hooks/ponytail-activate.js` |

9 further commits drew exactly one follow-up fix (not listed).

### The fixes behind the worst offenders

- `d5f4ffdd6` 2026-07-09 10:29 pi-extension: make startup notification opt-out via quietStartup (#308)
  - `6165b7011` +5.0h  fix(pi-extension): guard theme access with try-catch for pi-web compatibilit
  - `8555a0a58` +5.2h  fix: catch fs errors when writing default mode in pi-extension (#559)
  - `b6c04480c` +14.4h  fix: narrow the ponytail: marker to real corner-cuts, keep the prefix (#120)
  - `0cdd11fe0` +14.6h  fix: stop filterSkillBodyForMode from swallowing rule bullets that start wit
- `1715abcca` 2026-07-09 15:23 feat(hooks): opt-in agent-type scoping for SubagentStart injection (#… (#522)
  - `33c00d3d7` +0.7h  fix: Codex CLI SessionStart additionalContext at top level (#505) (#508)
  - `3465b1a3c` +7.9h  Fix Codex hook output schema (#573) (#574)
  - `65db9025a` +8.4h  fix: reject review as a default mode in pi-extension and config (#576)
- `8c279cbfb` 2026-06-12 15:55 feat: add pi extension (#1)
  - `c15db8d3c` +7.8h  fix: stop mode filter stripping rule bullets with a colon
  - `01578c0cd` +54.1h  fix: honor CLAUDE_CONFIG_DIR in hooks (#37)

### Unattributed fixes (52)

No earlier non-fix commit inside the window shares a file. Usually a fix
storm (see R2) or a fix for code older than the window.

- `1556f10bc` 2026-06-12 23:53 fix: use CLAUDE_PLUGIN_ROOT in hooks.json, drop duplicate manifest hooks
- `6abc9f0ac` 2026-06-13 03:33 fix(examples): keep response schema in API example, do not leak ORM fields
- `147bcfd62` 2026-06-14 15:39 fix: use PowerShell $env: syntax for Windows hook paths (#26)
- `d67663532` 2026-06-15 09:23 fix: hooks degrade gracefully when node is not on PATH (#57)
- `084f10fb4` 2026-06-15 14:32 fix: ship the missing /ponytail-help command on Claude Code and OpenCode (#6
- `45f7d2f83` 2026-06-17 02:35 Fix/examples issue 127 (#131)
- `53fd1e850` 2026-06-18 20:50 fix: only deactivate on a standalone "stop ponytail" / "normal mode" (#162)
- `55b7cb192` 2026-06-18 20:50 fix: resolve test failure on Node.js < 20.11.0 by using new URL (#157)
- `a3bc7db72` 2026-06-18 20:50 fix: strip UTF-8 BOM before parsing settings.json in ponytail-activate (#148
- `c30854118` 2026-06-18 20:50 fix: guard final writeHookOutput against stdout EPIPE in ponytail-activate (
- `795ec0ee3` 2026-06-18 20:50 fix: statusline reads flag from CLAUDE_CONFIG_DIR, not just ~/.claude (#34 f
- `70df716a0` 2026-06-18 22:24 Fix path for .env file in README (#104)
- `25be875fa` 2026-06-18 22:24 Fix markdown formatting in ponytail-debt.md (#142)
- `a28e5ec12` 2026-06-18 22:24 fix: register skills directory via config hook so opencode discovers ponytai
- `b0c5820bb` 2026-06-18 22:26 Fix scope ambiguity in ponytail-audit and ponytail-review Boundaries (#163)

## R2 - Fix storms (>= 5 consecutive fix commits)

A run of fixes with no intervening feature or refactor commit. The work landed
before it was ready. Ask what review or test step was skipped.

A run whose span is ~0h is NOT a storm: it is a rebase, a squash import or a batch
landing. Those are labelled `batch` and carry no process signal.

- **5 consecutive fixes, batch** (span 0.00h, so this is a rewrite or import, not a storm): `53fd1e850` .. `795ec0ee3`
- **5 consecutive fixes** over 64.9h: `5eb1fd8b7` .. `763e04dee` (2026-06-20 23:36)
  - first: fix: make Python command portable in robustness-audit.js (fixes Windows) (#209
  - last:  fix: align all version manifests to 4.8.1 + guard against drift (#260, #262) (
- **5 consecutive fixes** over 0.5h: `7eda70d30` .. `25185a445` (2026-07-01 22:06)
  - first: fix: exec lifecycle hook commands (#474)
  - last:  fix: don't destroy combined statuslines on uninstall (#479)
- **11 consecutive fixes** over 9.7h: `8555a0a58` .. `f12f210eb` (2026-07-09 15:43)
  - first: fix: catch fs errors when writing default mode in pi-extension (#559)
  - last:  fix(benchmarks): kill timed-out agent cells cross-platform (#225)

## R3 - Fix-cluster files (>= 3 fix commits)

| fixes | path |
| --- | --- |
| 10 | `tests/hooks.test.js` |
| 7 | `hooks/ponytail-activate.js` |
| 7 | `pi-extension/index.js` |
| 6 | `tests/hooks-windows.test.js` |
| 6 | `hooks/ponytail-config.js` |
| 5 | `pi-extension/test/helpers.test.js` |
| 5 | `.opencode/plugins/ponytail.mjs` |
| 4 | `hooks/ponytail-instructions.js` |
| 4 | `hooks/ponytail-runtime.js` |
| 4 | `scripts/uninstall.js` |
| 4 | `tests/uninstall.test.js` |
| 3 | `.github/workflows/test.yml` |
| 3 | `benchmarks/benchmark-local.py` |
| 3 | `benchmarks/loc.js` |
| 3 | `benchmarks/agentic/run.py` |
| 3 | `hooks/ponytail-mode-tracker.js` |
| 3 | `pi-extension/test/extension.test.js` |
| 3 | `tests/opencode-plugin.test.js` |

## R4 - Fix commits that admit a repeat

None found.

## R5 - Fix commits that also changed test code

Two detectors are combined:
  1. the commit touches a separate test file (`test_*`, `*.spec.*`, `tests/`)
  2. the commit's diff adds or removes a test marker (`#[test]`, `def test_`,
     `describe(`, `it(`) - this catches colocated and inline tests

42 of 70 fix commits changed test code (36 by file path, 27 by diff marker).

A low number means fixes ship without a regression test. A non-zero number means
the test was missing or asserted the wrong thing.

- `515fb4c5a` fix: make hook compatibility test cross-platform (USERPROFILE for Wind
  - `tests/hooks.test.js`
- `c15db8d3c` fix: stop mode filter stripping rule bullets with a colon
  - `pi-extension/test/helpers.test.js`
- `147bcfd62` fix: use PowerShell $env: syntax for Windows hook paths (#26)
  - `tests/hooks-windows.test.js`
- `01578c0cd` fix: honor CLAUDE_CONFIG_DIR in hooks (#37)
  - `tests/hooks.test.js`
- `084f10fb4` fix: ship the missing /ponytail-help command on Claude Code and OpenCo
  - `tests/commands.test.js`
- `53fd1e850` fix: only deactivate on a standalone "stop ponytail" / "normal mode" (
  - `pi-extension/test/extension.test.js`, `tests/hooks.test.js`
- `55b7cb192` fix: resolve test failure on Node.js < 20.11.0 by using new URL (#157)
  - `pi-extension/test/helpers.test.js`
- `215777d83` fix: don't embed shell-unsafe install paths in statusline setup nudge 
  - `tests/hooks.test.js`
- `ae24cd00b` fix: add uninstall cleanup script for state outside plugin files (#226
  - `tests/uninstall.test.js`
- `c8b12b638` fix(pi-extension): guard status bar render when ui has no theme (#279)
  - `pi-extension/test/extension.test.js`
- `2b426c6ac` fix: make shared hooks parse in PowerShell (#265)
  - `tests/hooks-windows.test.js`
- `8d154e6c2` fix(benchmarks): strip block comments before counting LOC (#232)
  - `benchmarks/loc.test.js`
- `85cc1d993` fix: copilot-plugin test checks all 6 command files (#393)
  - `tests/copilot-plugin.test.js`
- `7eda70d30` fix: exec lifecycle hook commands (#474)
  - `tests/hooks-windows.test.js`
- `7e6eca6e2` fix: prevent Windows session freeze from stdin EOF deadlock (#477)
  - `tests/hooks-windows.test.js`
- `25185a445` fix: don't destroy combined statuslines on uninstall (#479)
  - `tests/uninstall.test.js`
- `40e50d9e0` fix: don't crash uninstall on malformed settings.json (#481)
  - `tests/uninstall.test.js`
- `39bad58d4` fix: guard pi before_agent_start against bad event and missing systemP
  - `pi-extension/test/extension.test.js`
- `4286903a7` fix: ship scripts/uninstall.js in the npm package (#538)
  - `tests/package.test.js`
- `146904825` fix: handle CRLF in loc.js fence regex and remove dead codeOf (#339) (
  - `benchmarks/loc.test.js`
- `3869218b1` fix: hermes test hardcoding python3 (fails on Windows) (#513)
  - `tests/hermes-plugin.test.js`
- `988428d51` fix: writeDefaultMode merges config instead of overwriting (#490) (#51
  - `tests/hooks.test.js`
- `f790cebb5` fix: statusline setup nudge honors CLAUDE_CONFIG_DIR (#338)
  - `tests/hooks.test.js`
- `a3e0169c3` fix: ignore invalid opencode mode arguments (#302)
  - `tests/opencode-plugin.test.js`
- `6d0c11103` Fix ponytail test coverage and metadata (#503)
  - `tests/correctness.test.js`, `tests/hermes-plugin.test.js`, `tests/package-scripts.test.js`

## R6 - Recurrence by topic (what the fixes keep coming back to)

Counts a subject token across DISTINCT fix commits. This is the signal that still
works when the repository is multi-author and PR-driven and R1 goes quiet.

| fix commits | topic | earliest fix |
| --- | --- | --- |
| 14 | `ponytail` | `084f10fb4` fix: ship the missing /ponytail-help command on Clau |
| 8 | `plugin` | `1556f10bc` fix: use CLAUDE_PLUGIN_ROOT in hooks.json, drop dupl |
| 7 | `claude` | `1556f10bc` fix: use CLAUDE_PLUGIN_ROOT in hooks.json, drop dupl |
| 7 | `config` | `01578c0cd` fix: honor CLAUDE_CONFIG_DIR in hooks (#37) |
| 7 | `guard` | `c30854118` fix: guard final writeHookOutput against stdout EPIP |
| 7 | `mode` | `c15db8d3c` fix: stop mode filter stripping rule bullets with a  |
| 6 | `hooks` | `1556f10bc` fix: use CLAUDE_PLUGIN_ROOT in hooks.json, drop dupl |
| 6 | `json` | `1556f10bc` fix: use CLAUDE_PLUGIN_ROOT in hooks.json, drop dupl |
| 6 | `opencode` | `084f10fb4` fix: ship the missing /ponytail-help command on Clau |
| 5 | `benchmarks` | `2e6a93765` fix(benchmarks): count unfenced code, ASCII-safe out |
| 5 | `extension` | `c8b12b638` fix(pi-extension): guard status bar render when ui h |
| 5 | `hook` | `515fb4c5a` fix: make hook compatibility test cross-platform (US |
| 5 | `uninstall` | `ae24cd00b` fix: add uninstall cleanup script for state outside  |
| 5 | `windows` | `515fb4c5a` fix: make hook compatibility test cross-platform (US |
| 4 | `against` | `c30854118` fix: guard final writeHookOutput against stdout EPIP |
| 4 | `dir` | `01578c0cd` fix: honor CLAUDE_CONFIG_DIR in hooks (#37) |
| 4 | `don` | `0403c4dd5` Fix for #168: Don't write output on SessionStart for |
| 4 | `drop` | `1556f10bc` fix: use CLAUDE_PLUGIN_ROOT in hooks.json, drop dupl |
| 4 | `statusline` | `795ec0ee3` fix: statusline reads flag from CLAUDE_CONFIG_DIR, n |
| 4 | `stop` | `c15db8d3c` fix: stop mode filter stripping rule bullets with a  |
| 3 | `all` | `99139a25d` fix: pin all four safety carve-outs in the rule-drif |
| 3 | `audit` | `b0c5820bb` Fix scope ambiguity in ponytail-audit and ponytail-r |
| 3 | `code` | `2e6a93765` fix(benchmarks): count unfenced code, ASCII-safe out |
| 3 | `command` | `084f10fb4` fix: ship the missing /ponytail-help command on Clau |
| 3 | `copilot` | `0403c4dd5` Fix for #168: Don't write output on SessionStart for |

Read the top cluster end to end. A topic in 5+ fixes is one lesson, not five bugs.

### Every fix commit mentioning `ponytail`

- `084f10fb4` 2026-06-15 14:32 fix: ship the missing /ponytail-help command on Claude Code and OpenCode (#62)
- `53fd1e850` 2026-06-18 20:50 fix: only deactivate on a standalone "stop ponytail" / "normal mode" (#162)
- `a3bc7db72` 2026-06-18 20:50 fix: strip UTF-8 BOM before parsing settings.json in ponytail-activate (#148) 
- `c30854118` 2026-06-18 20:50 fix: guard final writeHookOutput against stdout EPIPE in ponytail-activate (#1
- `25be875fa` 2026-06-18 22:24 Fix markdown formatting in ponytail-debt.md (#142)
- `a28e5ec12` 2026-06-18 22:24 fix: register skills directory via config hook so opencode discovers ponytail 
- `b0c5820bb` 2026-06-18 22:26 Fix scope ambiguity in ponytail-audit and ponytail-review Boundaries (#163)
- `10a375b83` 2026-06-19 00:01 fix: regenerate .openclaw ponytail skill mirror (fixes red CI) (#177)
- `bd6176a9b` 2026-06-19 00:20 fix: drop em dashes from ponytail-audit/review scope wording (#163) (#179)
- `b8f6fbe92` 2026-07-01 22:10 fix: handle stdin error in ponytail-mode-tracker to avoid uncaught crash (#147
- `fb72987fb` 2026-07-09 01:13 fix(benchmarks): make agentic fixture path portable via PONYTAIL_TMPL (#206)
- `72274181e` 2026-07-09 01:29 fix(pi-extension): list ponytail modes (#237)
- `6d0c11103` 2026-07-09 01:35 Fix ponytail test coverage and metadata (#503)
- `b6c04480c` 2026-07-10 00:52 fix: narrow the ponytail: marker to real corner-cuts, keep the prefix (#120) (

## File activity (fix ratio)

| fix ratio | fixes | total | path |
| --- | --- | --- | --- |
| 1.00 | 4 | 4 | `tests/uninstall.test.js` |
| 1.00 | 3 | 3 | `.github/workflows/test.yml` |
| 1.00 | 2 | 2 | `benchmarks/loc.test.js` |
| 1.00 | 1 | 1 | `tests/commands.test.js` |
| 1.00 | 1 | 1 | `benchmarks/generate-examples.mjs` |
| 1.00 | 1 | 1 | `tests/package.test.js` |
| 1.00 | 1 | 1 | `tests/package-scripts.test.js` |
| 1.00 | 1 | 1 | `.opencode/plugins/ponytail-frontmatter.cjs` |
| 0.86 | 6 | 7 | `tests/hooks-windows.test.js` |
| 0.80 | 4 | 5 | `scripts/uninstall.js` |
| 0.75 | 3 | 4 | `benchmarks/loc.js` |
| 0.75 | 3 | 4 | `benchmarks/benchmark-local.py` |
| 0.75 | 3 | 4 | `benchmarks/agentic/run.py` |
| 0.67 | 4 | 6 | `hooks/ponytail-instructions.js` |
| 0.67 | 2 | 3 | `tests/hermes-plugin.test.js` |
| 0.62 | 5 | 8 | `pi-extension/test/helpers.test.js` |
| 0.62 | 5 | 8 | `.opencode/plugins/ponytail.mjs` |
| 0.60 | 6 | 10 | `hooks/ponytail-config.js` |
| 0.60 | 3 | 5 | `tests/opencode-plugin.test.js` |
| 0.54 | 7 | 13 | `hooks/ponytail-activate.js` |
| 0.50 | 10 | 20 | `tests/hooks.test.js` |
| 0.50 | 7 | 14 | `pi-extension/index.js` |
| 0.50 | 4 | 8 | `hooks/ponytail-runtime.js` |
| 0.50 | 2 | 4 | `benchmarks/correctness.js` |
| 0.50 | 2 | 4 | `benchmarks/agentic/tasks.py` |
| 0.50 | 1 | 2 | `tests/correctness.test.js` |
| 0.50 | 1 | 2 | `benchmarks/behavior.js` |
| 0.50 | 1 | 2 | `tests/copilot-plugin.test.js` |
| 0.50 | 1 | 2 | `commands/ponytail-help.toml` |
| 0.50 | 1 | 2 | `benchmarks/robustness-audit.js` |

