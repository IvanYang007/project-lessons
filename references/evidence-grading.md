# Evidence grading

The document's value rests on the reader trusting it. One invented convention destroys
that trust for every other rule. Grade everything, and publish the grade.

## In-repo documents are primary sources

A file the project wrote about itself outranks your inference. `docs/adr/`,
`docs/RECURRING_ISSUES.md`, `KNOWN_ISSUES.md`, a postmortem, a threat model, or a
`CONTRIBUTING.md` that states a rule is an `[observed]` source, exactly like a commit
body. Cite it the same way.

Two consequences:

1. **Grade it, do not trust it.** A prior document records what someone believed when
they wrote it. Check each claim against the history. A claim the history contradicts is
   the single most valuable finding a run can produce — write it, quote both sides.
2. **Do not duplicate it.** If the document already states the rule, `PROJECT_LESSONS.md`
   points at it and adds only the commit hashes and what the document misses. Two copies
   of one rule drift apart, and the reader cannot tell which to follow.

A stale prior document is a specific and useful finding:

```
Rule:   "Always set android:resizeMode=\"none\" on 1x1 widgets."
Source: docs/RECURRING_ISSUES.md
Status: STALE - superseded by <sha>, which removed the 1x1 layout entirely.
```

That is worth more than a new rule, because someone is still reading the old one.

## The three grades

### `[observed]`

The reason is written down by a human, in the repository.

Accept:

- a commit message body that states why
- a `Revert "X"` subject with the original subject still visible
- a PR body, PR review comment, or linked issue title, when retrieved via `gh`
- a `CHANGELOG` entry, `docs/adr/`, or a design note in the tree
- an in-code comment that states the reason (`// must stay: ...`, `SAFETY:`)
- a `git note` attached to the commit

Do not accept:

- a commit *subject* that only names the change (`fix login`) — that is not a reason
- your own paraphrase of a diff

### `[inferred]`

The reason is not written, but the shape of the history makes it hard to read any other
way. The inference must be falsifiable and you must state what would falsify it.

Accept:

- a path added, shipped, reverted, then re-added — the oscillation is in the data
- a library introduced and removed, with no import of it anywhere afterwards
- two files that co-change in 20 of their 22 shared commits — a contract
- a fix commit that rewrites a test the previous commit added
- a file with 9 fix commits out of 12 total

Reject:

- "the team probably cared about performance"
- "this looks like it was rushed"
- anything about intent rather than mechanism

For every `[inferred]` claim, add a **Falsifier** line in your work bundle: what you
would need to see to drop the claim. Example: "Falsifier: a commit showing the two
files changed independently more than twice."

### `[weak]`

One data point, an ambiguous signal, or a signal you could not corroborate.

Accept as `[weak]` and keep:

- a single fix commit with no sibling occurrence
- a removal commit with an empty or vague message
- a convention seen in exactly one file, with no commit backing it
- history younger than the rule you are claiming (a 4-month-old repo cannot show a
  2-year convention)

**Never delete a `[weak]` finding. Label it.** A labelled guess invites the human to
confirm; an unlabelled one becomes a false rule that a future agent obeys.

## Confidence counts, not adjectives

Do not write "usually", "often", "tends to", or "sometimes". Write the count.

| Bad | Good |
| --- | --- |
| Files here are usually colocated | 34 of 36 modules colocate their test (2 exceptions: `src/legacy/`) |
| The team often forgot to update the schema | 5 commits updated a model without a migration (`a1b2c3d`, `e4f5a6b`, ...) |
| Tests are sometimes missing | 11 of 41 fix commits also added a test; 30 did not |

If you cannot produce a count, the claim is `[weak]`.

## When to say "unknown"

Some questions history cannot answer. Say so plainly and move on. Do not fill the gap.

Write it in **Analysis notes**:

- `Unknown: why src/parser was rewritten in 2024-03; the commit message is "refactor"
  and there is no PR text in the local clone.`
- `Unknown: whether the removed feature was unused or unfinish. The revert message is
  "revert" with no body.`
- `Weak: only 2 commits touch src/queue; no pattern can be claimed.`

An honest "unknown" is a useful line in the document. A confident guess is a defect.

## Secret scrubbing — required before writing

Repository text can contain live credentials. Scan before the text reaches a model and
again before it reaches the document.

Patterns to redact, replacing the value with `<REDACTED>`:

```
sk-[A-Za-z0-9]{16,}                     OpenAI-style
sk-ant-[A-Za-z0-9_-]{16,}               Anthropic
ghp_ [gho_ ghs_ ghr_] [A-Za-z0-9]{20,}  GitHub tokens
AKIA[0-9A-Z]{16}                        AWS access key ID
xox[bpras]-[A-Za-z0-9-]{10,}            Slack
AIza[0-9A-Za-z_-]{30,}                  Google API key
-----BEGIN [A-Z ]*PRIVATE KEY----- ... -----END ... PRIVATE KEY-----
eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}   JWT
[A-Za-z0-9_]*(PASSWORD|SECRET|TOKEN|APIKEY|API_KEY|PRIVATE_KEY)[A-Za-z0-9_]*\s*[=:]\s*\S+
```

Two rules:

1. **Err toward redaction.** A redacted diff still carries the lesson.
2. **Never reproduce a `.env` value** in the output, even a plausibly-fake one.

The scrub is a safety net, not a guarantee. If the repo is full of live credentials,
tell the user and stop before writing.
