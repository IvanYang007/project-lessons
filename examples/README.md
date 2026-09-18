# Examples

Three real outputs from running this skill, kept so a reader can calibrate what the
workflow produces before running it on their own repository.

All three pass every blocking gate:

```bash
for r in papervault countup ponytail; do
  python scripts/check_output.py examples/$r-PROJECT_LESSONS.md \
    examples/$r-project-lessons.json /path/to/$r
done
```

## Target 1 — papervault

A Rust desktop PDF search and preview app (egui/eframe, Tantivy, rusqlite,
pdfium-render). 66 commits, one author, 23 hours of history. Deliberately a hard case: a
brand-new repository with no PR history, no releases, and no deleted files.

| File | What it is |
| --- | --- |
| `papervault-recurrence.md` | Raw output of `scripts/recurrence.py`. The evidence the document was written from. |
| `papervault-PROJECT_LESSONS.md` | The finished artifact. |
| `papervault-project-lessons.json` | The machine-readable mirror. |
| `papervault-coupling.py` | The change-coupling pass (PowerShell 5.1 cannot do the awk two-pointer loop). |

What the mechanical pass found:

- 35 of 66 commits are `fix:` (53%).
- Three fix storms of 5, 5 and 6 consecutive fix commits, each inside 1.5 hours.
- `src/indexer/extractors/pdf.rs`: 8 fixes in 9 commits (0.89), the highest fix density.
- One commit in the whole history admits a repeat in its message: `f19608f`, whose subject
  begins with "also".

Three rules no one could have guessed from reading the code:

1. There are two PDF libraries on purpose, and merging them reintroduces a hang
   (`292ee36`).
2. `pdfium` must be owned by one thread — six fixes failed before the structural change
   (`a815c24` → `be40850`).
3. Cleaning the runtime stop path by hand always misses a field (`c777cbf` → `f19608f`).

Plus an honest negative: the reason `panic = "abort"` was removed is not in the history, so
that lesson is graded `[weak]` and says so.

## Target 2 — CountUp-Android

A zero-permission Android app (Kotlin, Jetpack Compose, RemoteViews widgets). 176 commits,
one author, four weeks. This target exercised what papervault could not: deletions, a
repository that already documents its own faults, and a committed secret.

| File | What it is |
| --- | --- |
| `countup-recurrence.md` | Raw output of `scripts/recurrence.py`. |
| `countup-PROJECT_LESSONS.md` | The finished artifact. |
| `countup-project-lessons.json` | The machine-readable mirror. |
| `countup-coupling.py` | The change-coupling pass. |

The headline finding, which only exists because Phase 0.2 cross-checks prior documents
against history:

```
2026-09-07 12:42  1cd6e29  added widgetFeatures="reconfigurable|configuration_optional"
2026-09-07 12:46  a374749  wrote the rule "DO NOT include configuration_optional"
2026-09-09 11:15  433f1d4  removed the flag AND added the test assertion
```

The guardrail document was written **four minutes after** the commit that violated it, and
the code stayed wrong for two more days. Documentation did not stop the regression; the
`WidgetContractInvariantsTest` assertion did. That is the single most useful sentence in
either artifact.

The Phase 2 secret scan also fired: `keystore/keystore-pass.txt` was committed in the
initial commit `32f6f36`, deleted in `625f2c3`, and is still reachable on `origin/main`.

## Target 3 — ponytail

The upstream `DietrichGebert/ponytail` cross-agent skill package. 210 commits, **68
contributor emails**, 8 weeks, 80% squash-merged pull requests. This is the only target
with real multi-author review history, and it is where the method changed most.

| File | What it is |
| --- | --- |
| `ponytail-recurrence.md` | Raw output of `scripts/recurrence.py`, including R6. |
| `ponytail-PROJECT_LESSONS.md` | The finished artifact. |
| `ponytail-project-lessons.json` | The machine-readable mirror. |

What changed because of this target:

- **Quick-remedy attribution stopped working.** Only 18 of 70 fixes could be attributed to
  a recent commit, because a squash-merged fix answers an issue, not the merge that
  introduced the problem. On the two single-author repos it placed 35 of 35.
- **Topic clustering found the real recurrence.** R6 reported `windows` in 5 fixes. An
  explicit keyword probe on the same history found **25 commits — 36% of all fixes** —
  because the theme appeared as `windows`, `powershell`, `CRLF`, `portable`, `$env:`,
  `USERPROFILE` and `python3` across different commits.
- **A five-fix run at one timestamp was reported as a storm.** It was a rebase. Zero-span
  runs are now labelled `batch`.

The headline rules it produced:

1. Cross-platform portability is the #1 recurring defect class. Seven sub-classes, none of
   them written down anywhere: BOM in JSON (fixed twice, for two files), bash-only `exec`
   under PowerShell, shell-unsafe paths, hardcoded `python3`, CRLF, stdin EOF deadlock.
2. A pairwise manifest-agreement test cannot catch collective version drift — the
   maintainers say so in `763e04d`, after the 4.8.0 release advertised three versions at
   once. Pin an absolute version and compare it to the tag.
3. Editing `AGENTS.md` breaks the adapter mirrors, which is why
   `scripts/check-rule-copies.js` exists.

## Reproduce

```bash
git clone https://github.com/IvanYang007/papervault        # or CountUp-Android
cd papervault
git log --no-merges --format="C%H|%ct|%s" --name-only > commits.txt
git log -G'#\[test\]|#\[cfg\(test\)\]|def test_|describe\(|it\(' --format=%H > test-touch.txt
python <path-to-project-lessons>/scripts/recurrence.py commits.txt test-touch.txt
python <path-to-project-lessons>/scripts/check_output.py PROJECT_LESSONS.md \
  project-lessons.json .
```
