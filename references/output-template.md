# Output template — `PROJECT_LESSONS.md`

Use this structure exactly. Do not add, rename, or reorder the six required sections.
Do not delete a section because it is empty — write the header and the sentence
`No evidence in the analyzed history.`

Replace every `<...>` placeholder. Delete every comment line.

---

```markdown
# Project Lessons — <repo-name>

> Derived from git history. Last analyzed commit: `<sha>` (<date>).
> Range: `<first-sha>` .. `<sha>` (<N> commits, <start-date> .. <end-date>).
> Grades: `[observed]` stated in a commit/PR, `[inferred]` deduced from diffs,
> `[weak]` one data point or ambiguous.

## Executive summary

<3-6 sentences. What this repo is, how old it is, and the three to five things a coding
agent must know before its first change. Name the highest-risk module. Name the one
mistake this project has made more than once. State the single most important
constraint. No bullet list, no history tour.>

**Read this first if you are about to touch:** `<highest-risk path>` (see Known risk areas).

## Lessons learned from past commits

<Order by consequence, most costly first. 8-20 entries. Each entry:>

### L<n>. <Imperative one-line rule> — `[grade]`

- **What happened:** <the concrete past failure, in one or two sentences. Name files.>
- **Evidence:** `<sha>` <subject>, `<sha>` <subject>
- **Why it recurs:** <the mechanism that makes this repeatable — a shared helper, a
  copy-paste site, an ordering requirement, a missing test>
- **The rule:** <the instruction for next time. One sentence, imperative.>

<Only include a "Why it recurs" line when the recurrence is real. For a one-off, write
"One-off" — do not manufacture a pattern.>

## Project-specific implementation rules

<The stable conventions. Only rules a tool does not already enforce. Group with bold
labels, not sub-headings. Every rule imperative and specific to this repo.>

**Layout** — <where new code goes, and the exact file to copy as a template>

**Naming** — <the project's vocabulary table>

| Concept | Use this word | Never use | Evidence |
| --- | --- | --- | --- |
| <concept> | `<word>` | `<word>` | `<sha>` |

**Errors** — <how failures are returned, and where the shared helper lives>

**Validation** — <the shape used, and the files that intentionally differ>

**State and data access** — <the pattern, and the layer that must not be bypassed>

**Migrations in flight** — <what is mid-migration, and the instruction to not sweep>

| Area | Old shape | New shape | Status | Evidence |
| --- | --- | --- | --- | --- |

**Intentional inconsistencies** — <the same job done differently on purpose>

| Area | Shape A (where) | Shape B (where) | Why it is intentional | Evidence |
| --- | --- | --- | --- | --- |

**Commit and branch style** — <prefixes observed, tense, message length>

**Testing** — <runner, command, layout, fixture style, what is not covered, and whether
a fix must ship a test>

## Known risk areas

<A ranked table, then one short entry per top area.>

| Rank | Path | Risk | Churn | Fix commits | Couplings | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `<path>` | <score> | <n> | <n> | <n> | `<sha>`, `<sha>` |

<Then, for each of the top areas:>

### `<path>` — <one-line reason it is dangerous>

- **Failure mode:** <what actually broke here before>
- **Guard:** <the check or test that catches it>
- **Evidence:** `<sha>` <subject>

### Change couplings — files that must move together

| Pair | Co-changes | What the hidden contract is | Evidence |
| --- | --- | --- | --- |

<Only pairs with count >= 3. Write "No coupling above threshold." if none.>

### Removed and abandoned work — do not reintroduce

| Removed | When | Reason (quoted) | Evidence |
| --- | --- | --- | --- |

<Quote the author. A quoted reason is worth more than a paraphrase.>

## Safe-change checklist

<5-12 items. Each item must be verifiable by running something or looking at
something. Include the exact command where one exists.>

Before you change anything:

- [ ] Run `<build command>` and `<test command>`; both must pass before you start.
- [ ] Confirm the tree is clean: `git status --porcelain`.
- [ ] Read `<entry point>` and `<highest-risk path>`.

While you change:

- [ ] <boundary that must not be crossed>
- [ ] <coupling: if you touch `<a>`, check `<b>`>
- [ ] <migration rule: match the new shape only in files you already touch>
- [ ] <test rule: add a regression test named after the failure you are preventing>

Before you call it done:

- [ ] Run `<test command>`; every test that passed before still passes.
- [ ] Run `<lint/format command>`.
- [ ] Re-check the couplings in Known risk areas for the files you touched.
- [ ] If you removed an abstraction, confirm the removal reason from the "Removed and
      abandoned work" table first.

## Examples from commit history

<5-10 chosen cases. Chosen, not exhaustive. Each example shows the full arc: what
changed, what broke, what the fix taught. This section is where a reader builds trust in
the rules above.>

### Example 1 — <short title> (e.g. "Route order shadowing")

```
<sha>  <subject>
<sha>  <subject>
```

- **What changed:** <one sentence>
- **What broke:** <the symptom observed>
- **The fix:** <what the fix did>
- **The rule it produced:** see L<n>
- **Grade:** `[grade]`

### Example 2 — <short title — a reverted approach>

```
<sha>  add <thing>
<sha>  <thing>: <reason it failed>
<sha>  revert <thing>
```

- **What was tried:** <one sentence>
- **Why it failed:** <quoted from the commit>
- **The rule it produced:** see L<n>

### Example 3 — <short title — a repeated mistake>

```
<sha>  <first occurrence>
<sha>  fix <same bug, first time>
<sha>  fix <same bug, second time>
```

- **What repeated:** <one sentence>
- **Why it repeated:** <the mechanism>
- **The rule it produced:** see L<n>

---

## Analysis notes

<Optional, short. Say what you could not determine and why. State which signals were
thin. This section is required when any lesson rests on `[weak]` evidence.>

- **Coverage:** <N> commits analyzed, <N> files, <date range>.
- **Not covered:** <paths excluded as generated or vendored>.
- **Weak signals:** <what you could not confirm>.
- **Unknowns:** <questions the history cannot answer, e.g. "no PR text available,
  so the reason for the 2024 rewrite of `<module>` is unknown">.
```

---

## Placement rules

| Rule | Value |
| --- | --- |
| Rules cap | 40. More means the synthesis failed. |
| Lessons cap | 20 entries in "Lessons learned". |
| Examples cap | 10 in "Examples from commit history". |
| Total document | 80-400 lines. |
| Section order | Fixed. Do not reorder. |
| Machine-readable mirror | `project-lessons.json`, same content, schema `project-lessons/v1`. |
| Location | Repository root. |
| Scoped run | `PROJECT_LESSONS.<scope>.md`; set `"scope"` in the JSON. Never overwrite the repository-wide file. |

## Mapping from the analysis to the sections

Every analysis phase must land somewhere. Check this before delivering.

| Analysis output | Goes to |
| --- | --- |
| Stable patterns and conventions | Project-specific implementation rules |
| Mistakes and how to avoid them | Lessons learned from past commits |
| High-risk files and modules | Known risk areas (ranked table) |
| Change couplings | Known risk areas (couplings table) |
| Removed and abandoned work | Known risk areas (removed table) |
| Testing strategy the project expects | Project-specific implementation rules -> Testing |
| Architectural boundaries | Project-specific implementation rules + Safe-change checklist |
| Pre-change checklist | Safe-change checklist |
| Best 5-10 commit arcs | Examples from commit history |
| Confidence and gaps | Analysis notes |
