# Examples

Two real outputs from running this skill, kept so a reader can calibrate what the
workflow produces before running it on their own repository.

Both pass every blocking gate:

```bash
python scripts/check_output.py examples/papervault-PROJECT_LESSONS.md \
  examples/papervault-project-lessons.json /path/to/papervault
python scripts/check_output.py examples/countup-PROJECT_LESSONS.md \
  examples/countup-project-lessons.json /path/to/countUp
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
