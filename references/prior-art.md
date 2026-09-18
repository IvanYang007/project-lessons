# Prior art evaluation

What already exists for "mine git history, produce project memory for coding agents",
scored against the eight things this job needs, and what this skill takes from each.

## How to read this

**My reading depth is stated per row.** A row marked *README only* means I did not read
the implementation. Treat those scores as weaker evidence. This is the same standard the
skill applies to commit history: grade the claim.

- *Full* — read the skill definition or the whole README.
- *Partial* — read part of the README or a documentation summary.
- *Summary* — a search-result summary only. Least reliable.

## Scoring dimensions (0-2 each, max 16)

| # | Dimension | Question |
| --- | --- | --- |
| E | Evidence discipline | Does it cite sources and grade confidence, or does it assert? |
| R | Recurrence detection | Does it find a mistake the project made *more than once*? |
| S | Specificity enforcement | Does it actively block generic advice? |
| C | Cost control | Does it bound token spend and skip noise? |
| D | Durability | Does the output survive sessions as a committed file? |
| F | Currency / refresh | Does it handle its own staleness incrementally? |
| P | Portability | Does it work across agents and operating systems? |
| M | Machine readability | Can a tool or MCP server consume the output? |

## Candidates

### Skills and agents

| Project | E | R | S | C | D | F | P | M | Total | Reading |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [hr23232323/repo-history](https://github.com/hr23232323/repo-history) | 2 | 1 | 2 | 2 | 2 | 2 | 1 | 2 | **14** | Full |
| [TheaDust/lore](https://github.com/TheaDust/lore) | 1 | 0 | 1 | 1 | 2 | 2 | 2 | 1 | **10** | Partial |
| [riponcm/projectmem](https://github.com/riponcm/projectmem) | 0 | 2 | 1 | 1 | 1 | 2 | 1 | 2 | **10** | Summary |
| [ChrisCooneyUK/git-log-context-harvesting](https://github.com/ChrisCooneyUK/git-log-context-harvesting) | 1 | 0 | 2 | 1 | 2 | 2 | 1 | 0 | **9** | Full |
| [yagizdo/quiver create-agents-md](https://github.com/yagizdo/quiver/blob/master/skills/create-agents-md/SKILL.md) | 0 | 0 | 2 | 2 | 2 | 1 | 2 | 0 | **9** | Full |
| [KyaniteLabs/devarch-framework](https://github.com/KyaniteLabs/devarch-framework) | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 2 | **8** | Partial |
| [matthewp/recall](https://github.com/matthewp/recall) | 1 | 0 | 1 | 2 | 2 | 0 | 1 | 0 | **7** | Full |
| [pedronauck/skills lesson-learned](https://claudeskills.info/skills/pedronauck/skills/lesson-learned/) | 1 | 0 | 2 | 2 | 0 | 0 | 1 | 0 | **6** | Full |
| [udaybandaru/code-archaeologist](https://github.com/udaybandaru/code-archaeologist) | ? | ? | ? | ? | ? | ? | ? | ? | n/a | Not read |
| [hozakar/project-memory](https://github.com/hozakar/project-memory) | 0 | 0 | 1 | 1 | 2 | 1 | 1 | 0 | **6** | Summary |
| [velantrian/agents-remember](https://github.com/velantrian/agents-remember) | 1 | 0 | 1 | 1 | 2 | 2 | 1 | 2 | **10** | Summary |
| [QuantisDevelopment/git-memory](https://github.com/bandtincorporated8/git-memory) | 0 | 0 | 0 | 1 | 1 | 1 | 1 | 2 | **6** | Summary |
| [OJPalenzuela/agents-generator](https://github.com/OJPalenzuela/agents-generator) | 0 | 0 | 1 | 1 | 2 | 0 | 2 | 0 | **6** | Summary |
| [yan-yanko Rainman](https://yan-yanko.github.io/rainman/) | 0 | 2 | 1 | 1 | 1 | 2 | 1 | 1 | **9** | Summary |

### Tools and methods

| Tool / method | E | R | S | C | D | F | P | M | Total | Reading |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [adamtornhill/code-maat](https://github.com/adamtornhill/code-maat) | 2 | 0 | 2 | 2 | 0 | 0 | 1 | 2 | **9** | Summary |
| SZZ algorithm and variants | 2 | 1 | 1 | 0 | 1 | 0 | 1 | 2 | **8** | Summary |
| [RegMiner](http://linyun.info/publications/fse22demo.pdf) | 2 | 1 | 1 | 0 | 1 | 0 | 1 | 2 | **8** | Summary |
| Quick remedy commits (Wen et al., EMSE 2022) | 2 | 2 | 1 | 1 | 1 | 0 | 1 | 1 | **9** | Partial |

### Research on whether the output helps at all

| Paper | Finding | Relevance |
| --- | --- | --- |
| [Gloaguen et al., *Evaluating AGENTS.md* (arXiv:2602.11988)](https://arxiv.org/abs/2602.11988) | Context files do **not** generally improve task success; inference cost rises 20%+. Instructions **are** followed; repository **overviews** are not helpful. Conclusion: useful for specifying non-standard practices, and any attempt to improve performance must be evaluated. | Decides the document's shape: prescriptive through, narrative last. |
| [Khatri et al., *Do Context Files Help Coding Agents?* (arXiv:2607.27250)](https://arxiv.org/abs/2607.27250) | 288 runs, 2 agents, 3 repos. Context strategy does not measurably move correctness (equivalent within 10-15 pp). Failures are **implementation-skill** failures — feature design, pattern selection, exact wiring — not missing repo knowledge. | A document of *knowledge* is not enough. It must state the wiring decisions an agent would otherwise get wrong. |

Both abstracts are read in full. Neither result is used to argue this skill *raises*
success rates — that is unproven. They are used to argue the document should be
prescriptive rather than narrative, which is what they do support.

## What each candidate does well

**repo-history** is the strongest existing work and the closest to this skill.
Its contributions:

- evidence grades `[observed]` vs `[inferred]` on every claim, with the receipts
- guardrails-first ordering, explicitly justified by the ablation result
- a deterministic engine with the LLM sandwiched between file handoffs, so the model
  cannot drift and the rerun is cheap
- episode clustering instead of per-commit analysis; reverts always get their own episode
- secret scrubbing at the LLM boundary
- an MCP server so the memory is queryable, not just readable
- incremental re-runs via `--since <sha>`, with an explicit check that the recorded sha
  still exists after a rebase

Its limits: it needs `uv` plus Claude Code, the LLM step is agent-locked, and its
landmine detection is built from reverts and removed abstractions — it does not pair a
fix with the commit it repaired.

**git-log-context-harvesting** contributes the single best disambiguation rule in the
field: *is this inconsistency an in-flight migration or a deliberate choice?* Its answer
is to read the commit that introduced the inconsistency, and to write "don't
blanket-finish" for migrations. It also states the failure mode that matters most —
"inventing conventions that don't exist in the history" — and its rule that every stated
convention must map back to a commit, a comment, or a structural pattern.

Its limits: no confidence grading, so a one-commit guess reads the same as a
twelve-commit rule; no cap on the analysis; Claude-specific file target; no
machine-readable output.

**lore** contributes durable identity management: stable entry IDs
(`LAYER-YYYY-MM-DD-hash`), lifecycle tags `#added / #verified / #stale`,
`#superseded-by` links, and deterministic mirrors into `CLAUDE.md` / `AGENTS.md` /
`.cursorrules`. Current-state queries exclude stale and superseded entries. This is the
only candidate that treats memory as having a lifecycle rather than being rewritten
wholesale.

**projectmem** and **Rainman** both target recurrence directly, by recording attempts and
failures as they happen and warning before a repeat. That is the right *goal* but the
wrong *source*: they depend on the agent writing memory during a session. This skill
derives recurrence from history that already exists, which needs no discipline from
anyone.

**quiver create-agents-md** contributes the quality gates. Its BLOCKING list is the
sharpest in the field: *if you could paste the bullet into any repo, delete it*; do not
restate the linter; no hedging language; omit empty sections rather than pad them; line
budget with a warning threshold.

**lesson-learned** contributes the scale discipline: pick the single dominant lesson,
add at most two more, always reference specific files and lines, and say honestly when
the changes are trivial and there is no lesson.

**Code Maat** and *Your Code as a Crime Scene* contribute the two mechanical analyses
that carry most of the risk signal: **change coupling** (files that change together
reveal hidden contracts) and **hotspots** (churn x complexity). Both are cheap to
reimplement in shell, which removes the JVM dependency.

**Quick remedy commits** (Wen et al., EMSE 2022) contribute the best cheap proxy for
recurrence I found: commits that quickly repair an omission in a previous commit. SZZ
does this more precisely but needs line-level blame archaeology, and its own literature
reports low precision and "ghost commits" it cannot trace. For a skill, a 72-hour
file-overlap pairing gets most of the signal at a fraction of the cost.

## Gaps in the field — the case for this skill

1. **Nobody makes recurrence a first-class, history-derived signal.** Every tool looks
   at reverts, landmines, decisions, and hotspots. None asks "which mistake did this
   project make twice, and three times?" — which is the one lesson an agent most needs,
   because it is the one that will happen again. projectmem targets recurrence but only
   from what the agent chose to record.
2. **Grading is rare.** Only repo-history grades confidence, and it grades
   observed-vs-inferred — it does not have a third `[weak]` tier for "one data point".
   Everything else presents a guess and a fact in the same voice.
3. **Most output is narrative, which the evidence says does not help.** The ablations
   are clear: overviews do not move accuracy, instructions do. Documents still lead with
   architecture tours.
4. **No evidence-derived pre-change checklist.** Checklists exist in `AGENTS.md`
   generators, but they are written from config files, not from what actually broke.
5. **Testing expectations are never derived from history.** A tool can see that 30 of 41
   fix commits shipped without a test, or that 4 fixes had to rewrite a test. Nobody
   reports that, and it is exactly what tells an agent whether a test is expected.
6. **Portability is an afterthought.** The best tools bind the analysis to one agent
   (Claude Code) or one runtime (`uv`, JVM). A plain Markdown skill plus `git` works
   everywhere, and `git` is the only dependency that is guaranteed present.

## What this skill takes, and what it changes

Taken:

| From | Taken |
| --- | --- |
| repo-history | `[observed]` / `[inferred]` grading; guardrails-first ordering; episode clustering; secret scrubbing; incremental `--since` refresh with a sha-existence check |
| git-log-context-harvesting | migration-vs-deliberate disambiguation; the "every rule maps back to a commit" constraint; refresh shows a diff rather than a rewrite |
| lore | stable rule IDs (`PL-nnn` / `PL-Cn`) and a JSON mirror |
| quiver create-agents-md | BLOCKING quality gates; the paste-test for generic advice; do not restate the linter; omit rather than pad |
| lesson-learned | cap the lessons; cite files and hashes; say when there is no lesson |
| Code Maat / Tornhill | change coupling and hotspot scoring, reimplemented in shell and Python |
| Wen et al. | quick-remedy pairing as the recurrence signal |
| Removed from SZZ / RegMiner | line-level bug-introducing attribution — rejected as too costly for the signal gained |

Changed:

- Added a third grade, `[weak]`, and a rule that weak findings are labelled rather than
  dropped. The user's own spec demands "if evidence is weak, say so"; a two-tier grade
  cannot express that.
- Added four mechanical recurrence signals (R1-R5 in Phase 3) and grouped them by
  *symptom* rather than by file, so ten files with the same failure is one lesson.
- Added an evidence-derived testing-strategy section, built from fix-and-test
  co-change plus the runner and layout actually in the repo.
- Made the safe-change checklist mandatory, capped at 5-12 items, and required each item
  to be checkable by running something.
- Made portability a hard requirement: Markdown plus `git`, with a dependency-free
  Python helper, and no agent-specific path assumed.

## Honest limits of this evaluation

- I did not read `udaybandaru/code-archaeologist`, so it is unscored. Its README claims
  ten analysis capabilities and fourteen architecture patterns, which would place it
  near repo-history if the claims hold.
- Rows marked *Summary* are scored from search-result summaries, not source. Their
  scores may be wrong in either direction.
- No candidate was run end to end by me. The scores measure described design, not
  measured output quality.
- Neither ablation proves this skill works. It is a design argument, not a result. The
  honest claim is: the document is shaped so that the parts shown to be followed are
  kept and the parts shown not to help are compressed.
