# Project Lessons — CountUp-Android

> Derived from git history. Last analyzed commit: `f03baa6`-era head (2026-09-16).
> Range: `32f6f36` .. HEAD (176 commits, 2026-08-20 .. 2026-09-16).
> Grades: `[observed]` stated in a commit/doc, `[inferred]` deduced from diffs,
> `[weak]` one data point or ambiguous.
>
> **This repository already documents its own recurring faults.**
> Read [`docs/RECURRING_ISSUES.md`](docs/RECURRING_ISSUES.md) first. It contains 10
> defects with root causes, hard invariants, and a 12-item pre-commit checklist. This
> document does **not** restate it. It records what the history adds to it.

## Executive summary

CountUp is a zero-permission Android app (Kotlin, Jetpack Compose, RemoteViews
home-screen widgets, rusqlite-free JSON store) with 176 commits from one author over
four weeks, of which 35 are fixes (19%). The dominant lesson is not about widgets or
Compose: it is that **a written guardrail does not enforce itself**. The repository wrote
down "never use `configuration_optional`" at 12:46 on 2026-09-07 while the working tree
was already violating it — the offending commit is four minutes *older* than the
document — and the code stayed wrong for two more days. It was only fixed when the rule
became an assertion in `WidgetContractInvariantsTest` (`433f1d4`). Three further risks:
one `keystore/keystore-pass.txt` is still reachable in pushed history (see below); every
user-facing string must land in six locale files or the build keeps a half-translated UI;
and four widget receiver families duplicate each other's navigation logic.

**Read this first if you are about to touch:** `app/src/main/res/xml/*_widget_info.xml`,
`docs/RECURRING_ISSUES.md`, or `CountUpContent.kt`.

> **SECURITY — ACTION REQUIRED.** `keystore/keystore-pass.txt` was committed in the
> initial commit `32f6f36` (2026-08-20) and removed in `625f2c3` (2026-09-05). The blob
> is **still reachable in history and is pushed to `origin/main`**
> (`IvanYang007/CountUp-Android`, private). Removal from the tree did not remove it from
> the packfile. Rotate the release signing key and purge history with `git-filter-repo`
> **before this repository is ever made public**. The repository already tracks this as
> `.scratch/codebase-hardening/issues/04-keystore-password-scrub.md`. The value is
> deliberately not reproduced here.

## Lessons learned from past commits

### L1. A written rule is not enforcement. Convert it to an invariant test. — `[observed]`

- **What happened:** `docs/RECURRING_ISSUES.md` item 1 states "DO NOT include
  `configuration_optional` in `android:widgetFeatures` for any widget requiring initial
  card selection." The document was written at **2026-09-07 12:46** (`a374749`). The
  commit that added `configuration_optional` is **2026-09-07 12:42** (`1cd6e29`) — four
  minutes earlier. So the rule was written down while the tree already broke it, and the
  tree stayed broken for two more days.
- **Evidence:** `1cd6e29` (added `widgetFeatures="reconfigurable|configuration_optional"`),
  `a374749` (wrote the rule), `471e4cc` (test touched, still no assertion),
  `2c48806` (test touched, still no assertion), `433f1d4` (removed the flag **and** added
  `!xmlContent.contains("configuration_optional")`), `f03baa6` (doc update).
- **Why it recurs:** the invariant lives in a document and in a comment, not in the build.
  A document cannot fail a build.
- **The rule:** when `docs/RECURRING_ISSUES.md` gains a hard invariant, add the matching
  assertion to `WidgetContractInvariantsTest` in the same commit. A doc-only change is not
  a fix.

### L2. Do not trust the comment in `*_widget_info.xml`. It has stated the opposite rule. — `[observed]`

- **What happened:** the same file carried two contradictory explanations with equal
  confidence. Before `1cd6e29` the comment read: *"resizeMode="horizontal|vertical" is
  required by launcher drop engines to accept targeted single-cell placement without
  cancelling"*. `1cd6e29` replaced it with: *"resizeMode="none" and configuration_optional
  ensure 1x1 pebble drops precisely onto desired cell."* Both are now in history, and the
  second is half wrong — `configuration_optional` does the opposite of what it claims.
- **Evidence:** `1cd6e29` (comment rewrite), `433f1d4` (removes `configuration_optional`
  and reverts the intent), current `zen_pebble_widget_info.xml` comment.
- **Why it recurs:** when one invariant is fixed by hand, the neighbouring one regresses
  in the same edit. `1cd6e29` corrected `resizeMode` and broke `widgetFeatures` in a single
  diff.
- **The rule:** the authoritative source for widget XML invariants is
  `WidgetContractInvariantsTest`, not the XML comment. When you touch `resizeMode` or
  `widgetFeatures`, assert **both** before and after.

### L3. Every user-facing string lands in six locale files, or the UI half-translates. — `[inferred]`

- **What happened:** `values/strings.xml` and `values-zh/strings.xml` co-change in **36**
  commits — the highest coupling in the repository. The other four locale files follow.
- **Evidence:** `b44ae72` "fix(i18n): support Traditional/Simplified Chinese locale
  switching, di...", `values-zh/strings.xml` 38 commits, `values-zh-rCN`, `values-zh-rHK`,
  `values-zh-rTW`, `values-b+zh+Hant` all present.
- **Falsifier:** a commit that adds an English string and deliberately leaves a locale
  untranslated (a documented fallback policy would explain it).
- **The rule:** adding a string means adding it to `values/`, `values-zh/`,
  `values-zh-rCN/`, `values-zh-rHK/`, `values-zh-rTW/` and `values-b+zh+Hant/`. Check
  `locales_config.xml` when the locale set changes.

### L4. There are four widget receivers with the same navigation logic. Do not add a fifth copy. — `[observed]`

- **What happened:** the receivers co-change heavily — `HeroWidgetReceiver` with
  `ZenHorizonWidgetReceiver` 12 times, `SolarRhythmWidget` with `ZenPebbleWidgetReceiver`
  11, `HeroWidgetReceiver` with `ZenPebbleWidgetReceiver` 10, `HeroWidgetReceiver` with
  `SolarRhythmWidget` 9. Two refactors already tried to break this up.
- **Evidence:** `d16e8b6` "refactor(contract): extract `WidgetNavigationContract`, remove
  deprecated token aliases, and decouple peer receivers", `146c008` "refactor(review):
  resolve peer receiver coupling, remove middle man, and eliminate magic numbers",
  `CountUpContract.kt` (22 commits defining the contracts).
- **The rule:** route widget commands through `CountUpContract` / `WidgetNavigationContract`.
  Never call a sibling receiver's pending-intent helper directly.

### L5. Version bumps and release commits draw follow-up fixes. — `[inferred]`

- **What happened:** `app/build.gradle.kts` is the second-heaviest file (44 commits, 9 of
  them fixes) and `release:` is the most common commit prefix (15). Two release commits
  drew repairs within a day.
- **Evidence:** `7b1c9c3` "release: bump version to 2.9.0..." drew `625f2c3` (+1.0h) and
  `edafee3a` (+1.1h); `662675d` "release: bump version to 2.19.0..." drew `06eb24c`
  (+10.3h) and `1cd6e29` (+12.8h).
- **The rule:** a release commit is not a bookkeeping commit here. Run
  `./gradlew assembleRelease` and install the release APK before tagging, not after.

### L6. The Hero 1x1 layout oscillated four times. Treat it as unresolved. — `[observed]`

- **What happened:** `countup_hero_widget_1x1.xml` was added, deleted, re-added, and
  deleted again across five commits.
- **Evidence:** `ca2d64b` **A** → `2214b71` **D** → `4bb85ca` **A** → `eca8720` **M** →
  `20cd267` **D** ("make 2x1 wide card the exclusive default and only layout for Hero
  widget").
- **The rule:** do not resurrect a 1x1 Hero layout without reading `20cd267` first. It was
  removed as a deliberate product decision, not as cleanup.

### L7. Landing a whole widget family in one commit drew four follow-up fixes. — `[inferred]`

- **What happened:** `227b2f37` "feat(widgets): implement Zen & Efficient Widget Suite
  with reactive updates" was followed by 4 fixes inside 14 hours, touching
  `ZenPebbleWidgetReceiver.kt`, `zen_pebble_widget_info.xml`, `AndroidManifest.xml` and
  `ZenHorizonLayoutTest.kt`.
- **Evidence:** `227b2f37`, then `3c86632` (+1.2h), `82e9024` (+2.8h), `8c6329f` (+13.7h),
  `15cdb44` (+13.8h).
- **The rule:** one widget family per commit. The manifest, the provider XML, the receiver,
  the configure activity and the layout are five testable units, not one.
- **Falsifier:** a similarly sized widget commit that needed no follow-up fixes.

### L8. `CountUpContent.kt` and `CountUpViewModel.kt` always move with their tests. — `[observed]`

- **What happened:** `CountUpContent.kt` + `CountUpViewModelTest.kt` co-change 18 times;
  `CountUpViewModel.kt` + `CountUpViewModelTest.kt` 17 times. 16 of 35 fix commits also
  changed test code. This is the opposite of "fixes ship untested" — tests are expected.
- **Evidence:** `a129cf0`, `5522dec2`, `edafee3a`, `bfc92b5`, `a3230034`, `82e9024` all
  land a fix with the matching test change.
- **The rule:** change `CountUpViewModel.kt` and `CountUpViewModelTest.kt` together. The
  project expects it, and it is the cheapest habit to keep.

## Project-specific implementation rules

**Layout and scope** — a single-module Compose app:

| Path | Owns |
| --- | --- |
| `CountUpContent.kt` | Compose UI tree |
| `CountUpViewModel.kt` | MVI state and intents |
| `CountUpContract.kt` | UI/VM contracts and widget command tokens |
| `WidgetNavigationContract.kt` | shared pending-intent construction |
| `CountUpStore.kt` | JSON persistence |
| `*WidgetReceiver.kt`, `*Widget.kt` | the four widget families |
| `WidgetContractInvariantsTest.kt` | **the enforcement layer for widget XML** |

**Plans and specs** — non-trivial work gets a document first, following an existing
shape: `docs/spec-<slug>.md` and `docs/brainstorms/<slug>.md`. Nine specs already exist.
Add to that convention rather than inventing a new one. `[observed]`

**Widget XML** — the invariants in [`docs/RECURRING_ISSUES.md`](docs/RECURRING_ISSUES.md)
items 1, 2, 7 and 8 are authoritative. Every one of them is asserted in
`WidgetContractInvariantsTest`. Read the test, not the XML comment (L2).

**Localization** — six locale files per string (L3). `locales_config.xml` is the registry.

**Errors and security** — exported configure activities validate `appWidgetId` against
`AppWidgetManager.INVALID_APPWIDGET_ID` and never echo caller extras into pending intents
(`RECURRING_ISSUES.md` item 7). Zero microphone permission; speech goes through
`<queries>`, never `RECORD_AUDIO` (item 8). `[observed]`

**Commit style** — Conventional Commits with a required scope for feature/fix work:
`release:` 15, `feat(ui):` 12, `feat:` 12, `fix(widget):` 11, `chore(release):` 9,
`feat(widget):` 8, `fix(ui):` 6, `refactor(widget):` 6. Use `fix(widget):` and
`fix(ui):` rather than a bare `fix:`.

**Testing** — `./gradlew testDebugUnitTest`, driven by `.github/workflows/ci.yml`. 43 test
files; the project's own count is 402 unit and contract tests. Three habits are visible
and expected:
1. a fix lands with the test change (L8);
2. contracts are tested by name (`CountUpContractAndFlowTest`, `DatePickerContractTest`,
   `WidgetContractInvariantsTest`);
3. **configuration is asserted, not just documented** — `WidgetContractInvariantsTest`
   reads the XML and asserts required and forbidden attribute values. This is the habit
   that actually stopped the `configuration_optional` regression (L1).

**Migrations in flight** — none detected. `CountUpRepository.kt` with
`FakeCountUpRepository.kt` (9 co-changes) is a settled seam, not a migration.

**Intentional inconsistencies** — one: the widget families duplicate navigation logic on
purpose, because each launcher entry point needs its own `RemoteViews` path. `d16e8b6`
and `146c008` reduced the duplication to shared contracts without merging the receivers.
Do not collapse them into one receiver. `[inferred]`

## Known risk areas

| Rank | Path | Commits | Fix commits | Why |
| --- | --- | --- | --- | --- |
| 1 | `app/build.gradle.kts` | 44 | 9 | release plumbing; the paste target for signing and R8 settings |
| 2 | `CountUpContent.kt` | 42 | 12 | heaviest fix count in the repo |
| 3 | `app/src/main/res/xml/zen_pebble_widget_info.xml` | 8 | 7 | **ratio 0.88** — the OEM-launcher knife fight (L1, L2) |
| 4 | `HeroWidgetReceiver.kt` | 32 | 5 | duplicated navigation logic (L4) |
| 5 | `CountUpWidget.kt` | 28 | 3 | same |
| 6 | `CountUpStore.kt` | 26 | 4 | JSON store, orphaned bindings on delete |
| 7 | `app/src/main/AndroidManifest.xml` | 21 | 4 | provider removal, `<queries>`, permissions |
| 8 | `CountUpViewModel.kt` | 20 | 4 | state transitions; must move with its test (L8) |
| 9 | `app/src/main/res/values/strings.xml` | 51 | 1 | highest churn, low fix density — it is a **contract**, not a risk |

`app/src/main/res/values/strings.xml` ranks first by churn and near-last by fix density.
It is listed as a contract because it must change with its five siblings (L3), not because
it breaks.

### Change couplings — files that must move together

| Pair | Co-changes | Contract |
| --- | --- | --- |
| `app/src/main/res/values/strings.xml` + `app/src/main/res/values-zh/strings.xml` | 36 | localization (L3) |
| `app/src/main/java/com/countup/app/CountUpContent.kt` + `app/src/main/res/values/strings.xml` | 27 | UI text is user-facing text |
| `app/src/main/java/com/countup/app/CountUpContent.kt` + `app/src/test/java/com/countup/app/CountUpViewModelTest.kt` | 18 | UI change implies test change (L8) |
| `app/src/main/java/com/countup/app/CountUpContent.kt` + `app/src/main/java/com/countup/app/CountUpViewModel.kt` | 18 | view and state |
| `app/src/main/java/com/countup/app/HeroWidgetReceiver.kt` + `app/src/main/java/com/countup/app/ZenHorizonWidgetReceiver.kt` | 12 | widget family (L4) |
| `app/src/main/java/com/countup/app/SolarRhythmWidget.kt` + `app/src/main/java/com/countup/app/ZenPebbleWidgetReceiver.kt` | 11 | widget family (L4) |
| `app/src/main/java/com/countup/app/CountUpItem.kt` + `app/src/main/java/com/countup/app/CountUpStore.kt` | 10 | model and persistence |

### Removed and abandoned work — do not reintroduce

| Removed | When | Reason (quoted) | Evidence |
| --- | --- | --- | --- |
| `keystore/keystore-pass.txt` | 2026-09-05 | "fix(security,ui): harden credentials..." — **still in history** | `32f6f36` add, `625f2c3` delete |
| `countup_hero_widget_1x1.xml` | 2026-09-01 | "make 2x1 wide card the exclusive default and only layout for Hero widget" | `20cd267` |
| `configuration_optional` | 2026-09-09 | "restore auto-launch picker ... by removing configuration_optional" | `433f1d4` |
| `ic_refresh_dark.xml`, `ic_solid_circle.xml`, `ic_eye_open.xml`, `ic_eye_closed.xml`, `ic_circle_olive.xml`, `ic_circle_mustard.xml`, `ic_solid_circle_dark.xml` | 2026-08..09 | icon-set consolidation; no message | `[weak]` |
| `values/plurals.xml`, `values-zh/plurals.xml` | 2026-08..09 | superseded by `strings.xml` entries; no message | `[weak]` |

## Safe-change checklist

Before you change anything:

- [ ] Run `./gradlew testDebugUnitTest`; the project expects 402 passing unit and contract
      tests. It must be green before you start.
- [ ] Read [`docs/RECURRING_ISSUES.md`](docs/RECURRING_ISSUES.md). It is the authoritative
      list of widget defects and their invariants.
- [ ] `git status --porcelain` to confirm a clean tree.

While you change:

- [ ] Touching `resizeMode` or `widgetFeatures` on any `*_widget_info.xml`: assert
      **both** invariants, not just the one you are fixing (L2).
- [ ] Adding a user-facing string: add it to all six locale files (L3).
- [ ] Touching one widget receiver: check its siblings. Route commands through
      `CountUpContract` / `WidgetNavigationContract` (L4).
- [ ] Touching `CountUpViewModel.kt`: change `CountUpViewModelTest.kt` too (L8).
- [ ] Adding an invariant to `docs/RECURRING_ISSUES.md`: add the assertion to
      `WidgetContractInvariantsTest` **in the same commit** (L1).
- [ ] One widget family per commit; do not land a whole suite (L7).

Before you call it done:

- [ ] Run `./gradlew testDebugUnitTest` and `./gradlew assembleRelease`. Debug-only
      verification has missed R8 and reflection breakage here (`RECURRING_ISSUES.md` item 3).
- [ ] Never commit anything under `keystore/`, and do not make this repository public
      until the history is scrubbed and the release key rotated. The password file is
      already in history once.
- [ ] Do not add `android.permission.RECORD_AUDIO` or any microphone permission.

## Examples from commit history

### Example 1 — The guardrail document was written after the violation, and fixed it nothing

```
2026-09-06 23:11  b6b4ce0  fix(widget): fix 1x1 pebble grid slotting...
2026-09-07 10:10  06eb24c  fix(widget): fix 1x1 pebble preview shape...
2026-09-07 12:42  1cd6e29  fix(widget): lock 1x1 pebble resizeMode to none and
                           restore configuration_optional for targeted drag placement
2026-09-07 12:46  a374749  docs: document recurring widget issues, root causes,
                           and prevention guardrails      <-- the rule is written here
2026-09-09 11:15  433f1d4  fix(widget): restore auto-launch picker for 1x1 Zen Pebble
                           by removing configuration_optional   <-- the rule is enforced
```

- **What changed:** `1cd6e29` set `resizeMode="none"` (correct) and simultaneously set
  `widgetFeatures="reconfigurable|configuration_optional"` (forbidden). Its diff also
  rewrote the XML comment to claim the forbidden flag *helps*.
- **What broke:** 1x1 widget drops stopped launching the configure activity, so users got
  an unconfigured widget with fallback data.
- **The fix:** `433f1d4` removed the flag **and** added the negated assertion to
  `WidgetContractInvariantsTest`. That is the commit that made it stick.
- **What the history proves:** the document was written four minutes after the offending
  commit, and the code stayed wrong for two days. The document is not what fixed it.
- **The rule it produced:** L1, L2.
- **Grade:** `[observed]` — every timestamp and diff is in the history.

### Example 2 — A credential committed in the initial commit

```
32f6f36  feat: multi-item count-up app with zen-paper widget
         ... keystore/keystore-pass.txt  (added)
625f2c3  fix(security,ui): harden credentials, concurrency, widget receivers
         ... keystore/keystore-pass.txt  (deleted)
```

- **What changed:** a release keystore password file was committed in the repository's
  first commit and removed two weeks later.
- **What is still true:** the blob is reachable in `git rev-list --all --objects`, and
  both commits are on `origin/main`. Deleting the file in a later commit does not remove
  it from the packfile.
- **The fix on record:** `.scratch/codebase-hardening/issues/04-keystore-password-scrub.md`
  plans a `git-filter-repo` purge and a fresh signing key, marked ready-for-agent.
- **The rule it produced:** the security block in the Executive summary, and the
  "never commit `keystore/`" checklist item. See L6 in Known risk areas.
- **Grade:** `[observed]`

### Example 3 — Fixing one invariant broke the adjacent one

```
1cd6e29  -android:resizeMode="horizontal|vertical"      (wrong, per the doc)
         -android:widgetFeatures="reconfigurable"
         +android:resizeMode="none"                     (right)
         +android:widgetFeatures="reconfigurable|configuration_optional"   (wrong)
```

- **What happened:** one hand-edit corrected one attribute and regressed the next.
- **Why it matters:** this is the mechanism behind a 0.88 fix ratio on
  `zen_pebble_widget_info.xml`. Hand-editing paired attributes always risks the pair.
- **The rule it produced:** assert both before and after (L2).
- **Grade:** `[observed]`

### Example 4 — A widget suite landed whole, and drew four fixes

```
227b2f37  feat(widgets): implement Zen & Efficient Widget Suite with reactive updates
3c8662    +1.2h  fix(release): resolve startup crash by suppressing unused WorkManager...
82e9024   +2.8h  fix(review): resolve all code standards review findings
8c6329f   +13.7h fix(review): resolve standards review smells with semantic tokens...
15cdb44   +13.8h fix(review): localize micro-unit label, fix test assertions, and fix XML...
```

- **What changed:** a whole widget suite in one commit.
- **What broke:** the manifest, provider XML, receivers and layouts all needed repair
  inside 14 hours. Two fixes are labelled `fix(review)`, so a review caught them late.
- **The rule it produced:** L7.
- **Grade:** `[inferred]` — the follow-ups are in the data; "one commit caused it" is a
  reading.

### Example 5 — The Hero 1x1 layout, added and killed twice

```
ca2d64b  A  feat(widget): add Focused Hero Milestone Widget (1x1 Compact Stamp & 2x1 Poetic Card)
2214b71  D  fix(widget): enforce 2x1 default sizing and optimize typography layout
4bb85ca  A  feat(widget): add Variant D 1x1 dynamic stack layout with responsive sizing
eca8720  M  feat(widget): add safe two-tap direct in-place reset on Hero Milestone widget
20cd267  D  fix(widget): make 2x1 wide card the exclusive default and only layout for Hero
```

- **What repeated:** a 1x1 Hero layout shipped, was removed, returned, and was removed
  again — the only oscillating path in the repository.
- **Why it repeated:** "1x1 for compact widgets" is an attractive idea that has now lost
  twice, the second time on an explicit product decision.
- **The rule it produced:** L6.
- **Grade:** `[observed]` for the arc, `[inferred]` for the design rationale.

---

## Analysis notes

- **Coverage:** 176 commits, 100% of history; 2026-08-20 .. 2026-09-16; one author.
- **Prior documents found and how they were used (Phase 0.2):**
  `docs/RECURRING_ISSUES.md` (10 defects — cited, not duplicated),
  `docs/CREDENTIAL_ROTATION.md`, `.scratch/codebase-hardening/issues/01..06`,
  `docs/CODE_REVIEW_2026-09-13.md`, `docs/CODE_REVIEW_ASSESSMENT_2026-09-13.md`,
  `docs/spec-*.md` (9 files), `docs/brainstorms/*`, `TECH_HANDOFF.md`.
- **Contradiction found:** none between the prior documents and history. The prior
  documents are accurate. What the history adds is **timing** — that the rule was written
  while already violated, and that documentation alone did not stop the regression.
- **Not covered:** `*.md`, `app/build/`, `playstore_package/*.png` and generated
  resources were excluded from churn and coupling so documentation and asset commits would
  not distort the counts.
- **Weak signals:** the removed icon and plurals files have no explanatory commit, so their
  removal reasons are guesses. The single `revert:` commit (`cb21440`) is the only direct
  revert; everything else was forward-fixed.
- **Unknowns:** whether the release signing key was ever rotated after `625f2c3`; the
  history cannot show a key rotation. Whether the two `fix(review)` bursts came from a
  human or an automated reviewer.
- **Counter-evidence to a common assumption:** fix density is low here (19%) and fixes
  usually ship with tests (16 of 35). The recurring-fault problem in this repository is
  **configuration drift in XML and manifests**, not missing tests.
