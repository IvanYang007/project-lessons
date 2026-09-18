# Examples

These are real outputs from running this skill, kept so a future reader can calibrate
what the workflow produces before running it on their own repo.

## Target

[papervault](https://github.com/IvanYang007/papervault) — a Rust desktop PDF search and
preview app (egui/eframe, Tantivy, rusqlite, pdfium-render). At the time of analysis:
66 commits, single author, 23 hours of history. Deliberately a hard case: a brand-new
repository with no PR history, no released versions, and no deleted files.

## Files

| File | What it is |
| --- | --- |
| `papervault-recurrence.md` | Raw output of `scripts/recurrence.py`. R1-R5 plus the fix-ratio table. This is the evidence the document was written from. |
| `papervault-PROJECT_LESSONS.md` | The finished artifact, produced by following `SKILL.md` and `references/output-template.md`. |
| `papervault-project-lessons.json` | The machine-readable mirror: 8 rules, 8 risk areas, 7 couplings, 12 checklist items, each with its evidence hashes. |
| `papervault-coupling.py` | The change-coupling pass, as run (PowerShell 5.1 cannot do the awk two-pointer loop). |

## What the mechanical pass found, in one line each

- 35 of 66 commits are `fix:` (53%).
- Three fix storms of 5, 5, and 6 consecutive fix commits, each inside 1.5 hours.
- `src/indexer/extractors/pdf.rs` has the highest fix density in the repo: 8 fixes in
  9 commits (0.89).
- `src/app.rs` is touched by 33 of 66 commits and appears in 7 coupling pairs at 5+.
- One commit in the whole history admits a repeat in its message: `f19608f`, whose
  subject begins with "also".

## Why this is a useful calibration example

A weaker document would have said "this is a Rust project using egui and Tantivy, write
clean code, and add tests". The mechanical pass instead produced three rules that no one
could have guessed from reading the code:

1. There are two PDF libraries on purpose, and merging them reintroduces a hang
   (`292ee36`).
2. `pdfium` must be owned by one thread — six fixes failed before the structural change
   (`a815c24` → `be40850`).
3. Cleaning the runtime stop path by hand always misses a field (`c777cbf` → `f19608f`).

It also produced an honest negative: the reason `panic = "abort"` was removed is not in
the history, so that lesson is graded `[weak]` and says so.

## Reproduce

```bash
git clone https://github.com/IvanYang007/papervault
cd papervault
git log --no-merges --format="C%H|%ct|%s" --name-only > commits.txt
git log -G'#\[test\]|#\[cfg\(test\)\]|def test_|describe\(|it\(' --format=%H > test-touch.txt
python <path-to-project-lessons>/scripts/recurrence.py commits.txt test-touch.txt
```
