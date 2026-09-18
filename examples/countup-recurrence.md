# Recurrence signals

Analyzed 176 commits; 35 are fix commits (19%).

Window: 72h. Thresholds: fix-cluster >= 3, fix-storm >= 5.

## R1 - Quick-remedy attribution (fix within 72h of a non-fix commit)

Each fix is attributed to the nearest earlier NON-fix commit it shares a file
with. A commit that needed several follow-up fixes is the signal. Read that
commit's diff to find what it omitted.

| follow-up fixes | earlier commit | span (h) | most-shared files |
| --- | --- | --- | --- |
| 4 | `227b2f372` feat(widgets): implement Zen & Efficient Widget Suit | 1.2-13.8 | `app/src/main/java/com/countup/app/ZenPebbleWidgetReceiver.kt`, `app/src/main/res/xml/zen_pebble_widget_info.xml`, `app/src/main/AndroidManifest.xml`, `app/src/test/java/com/countup/app/ZenHorizonLayoutTest.kt` |
| 3 | `2fa5b4e1a` feat(ui): implement 24 Solar Terms Header with Marce | 4.3-7.5 | `app/src/main/java/com/countup/app/CountUpContent.kt` |
| 2 | `a1539bc2a` feat(arch): modernize MVI architecture, Compose UI e | 0.1-1.7 | `app/src/main/java/com/countup/app/CountUpContent.kt`, `app/src/main/java/com/countup/app/MainActivity.kt`, `app/src/main/java/com/countup/app/CountUpViewModel.kt`, `app/src/test/java/com/countup/app/CountUpViewModelTest.kt` |
| 2 | `7b1c9c36a` release: bump version to 2.9.0 (versionCode 31) and  | 1.0-1.1 | `app/build.gradle.kts` |
| 2 | `662675d61` release: bump version to 2.19.0 (versionCode 41) wit | 10.3-12.8 | `app/build.gradle.kts` |
| 1 | `32f6f3621` feat: multi-item count-up app with zen-paper widget | 0.7 | `.gitignore`, `app/src/main/java/com/ivanyang/countup/DaysSince.kt`, `app/src/main/java/com/ivanyang/countup/MainActivity.kt`, `app/src/main/java/com/ivanyang/countup/CountUpStore.kt` |
| 1 | `5e88e768a` feat(widget): instant in-place reset with home-scree | 0.1 | `app/src/main/java/com/ivanyang/countup/CountUpWidget.kt` |
| 1 | `870b14811` feat(themes): add 17 new classical poetic themes exp | 0.5 | `app/src/main/java/com/countup/app/WidgetBackgroundRenderer.kt` |
| 1 | `e891c9c28` chore(release): bump version to 1.4.0 (versionCode 7 | 0.1 | `app/build.gradle.kts` |
| 1 | `73879e460` docs(playstore): update Play Store screenshots and m | 0.1 | `playstore_package/screenshot_6_home_widget.png`, `playstore_package/screenshot_3_date_picker.png`, `playstore_package/screenshot_3_edit_item.png`, `playstore_package/screenshot_1_main_list.png` |
| 1 | `ca2d64bb1` feat(widget): add Focused Hero Milestone Widget (1x1 | 1.0 | `app/src/main/res/layout/countup_hero_widget_1x1.xml`, `app/src/main/java/com/countup/app/HeroWidgetReceiver.kt`, `app/src/main/res/layout/countup_hero_widget_2x1.xml`, `app/src/main/res/xml/hero_widget_info.xml` |
| 1 | `4bb85ca1b` feat(widget): add Variant D 1x1 dynamic stack layout | 0.3 | `app/src/main/res/xml/hero_widget_info.xml` |
| 1 | `eca8720e3` feat(widget): add safe two-tap direct in-place reset | 24.9 | `app/src/main/res/layout/countup_hero_widget_1x1.xml`, `app/src/main/java/com/countup/app/HeroWidgetReceiver.kt` |
| 1 | `926e6d86c` chore: add .gitattributes and normalize line endings | 1.8 | `app/src/main/AndroidManifest.xml` |
| 1 | `b7bed7864` chore(git): harden against index file lock truncatio | 0.2 | `app/build.gradle.kts`, `app/src/main/res/values-zh-rTW/strings.xml`, `app/src/main/res/values-b+zh+Hant/strings.xml` |
| 1 | `720844563` feat(ui): implement Zen Tactile Hierarchy and lumino | 0.1 | `app/src/main/java/com/countup/app/CountUpContent.kt`, `app/src/main/java/com/countup/app/CountUpDialogs.kt`, `app/src/main/java/com/countup/app/ZenTheme.kt` |
| 1 | `c694773ca` feat(theme): implement automatic twilight dark theme | 0.0 | `app/src/main/java/com/countup/app/CountUpContent.kt`, `app/src/test/java/com/countup/app/ZenThemeTest.kt`, `app/src/main/java/com/countup/app/ZenTheme.kt` |
| 1 | `b0b103e87` feat(cards): preserve custom card identity and settl | 0.0 | `app/src/main/java/com/countup/app/ItemColors.kt`, `app/src/main/java/com/countup/app/CountUpContent.kt` |
| 1 | `405c7c7b3` feat(settings): add in-app ThemeMode setting and syn | 0.5 | `app/src/main/java/com/countup/app/HeroWidgetReceiver.kt`, `app/src/main/java/com/countup/app/CountUpWidget.kt` |
| 1 | `829acc9a6` refactor: prune unused loading_zen resource, dead te | 0.2 | `app/src/test/java/com/countup/app/ZenThemeTest.kt` |
| 1 | `3c271deaf` release: bump version to 2.18.0 (versionCode 40) wit | 1.3 | `app/build.gradle.kts` |
| 1 | `c177ddf2b` refactor(widget): resolve palette with WidgetThemeTo | 3.1 | `app/src/main/java/com/countup/app/ZenPebbleWidgetReceiver.kt` |
| 1 | `a374749c6` docs: document recurring widget issues, root causes, | 1.0 | `app/src/test/java/com/countup/app/WidgetContractInvariantsTest.kt` |
| 1 | `2c488069c` feat(backup): platform-native auto backup & launcher | 17.2 | `app/src/test/java/com/countup/app/WidgetContractInvariantsTest.kt` |
| 1 | `5fa0136b0` feat(reliability): remediate audit findings, harden  | 2.1 | `.github/workflows/ci.yml` |

### The fixes behind the worst offenders

- `227b2f372` 2026-09-07 00:34 feat(widgets): implement Zen & Efficient Widget Suite with reactive updates
  - `3c8663262` +1.2h  fix(release): resolve startup crash by suppressing unused WorkManagerInitial
  - `82e9024d7` +2.8h  fix(review): resolve all code standards review findings
  - `8c6329f40` +13.7h  fix(review): resolve standards review smells with semantic tokens, constants
  - `15cdb44c3` +13.8h  fix(review): localize micro-unit label, fix test assertions, and fix XML com
- `2fa5b4e1a` 2026-09-05 17:24 feat(ui): implement 24 Solar Terms Header with Marcellus hard seal and Noto Seri
  - `a2039e72c` +4.3h  fix(ui): refine solar term typography and sort box background to match canva
  - `148f6275c` +4.5h  fix(ui): remove sort box border and unify dropdown popup background with can
  - `05d0ce338` +7.5h  fix(ui): adjust solar term seal to 12.5sp and whisper states to 11.5sp
- `a1539bc2a` 2026-08-29 20:52 feat(arch): modernize MVI architecture, Compose UI elevation & test suite
  - `45dd6e198` +0.1h  fix(ui): eliminate white corner artifact on DropdownMenu popup
  - `5522dec24` +1.7h  fix(ui): resolve string format parameter for theme toast and add Chinese loc
- `7b1c9c36a` 2026-09-05 03:34 release: bump version to 2.9.0 (versionCode 31) and package release AAB/APK
  - `625f2c387` +1.0h  fix(security,ui): harden credentials, concurrency, widget receivers and expo
  - `edafee3ad` +1.1h  fix(arch): offload startup I/O, decouple widget refresh, and harden receiver
- `662675d61` 2026-09-07 03:51 release: bump version to 2.19.0 (versionCode 41) with verified cold-start stabil
  - `06eb24cbd` +10.3h  fix(widget): fix 1x1 pebble preview shape, rounded corners, and grid drop ta
  - `1cd6e29d1` +12.8h  fix(widget): lock 1x1 pebble resizeMode to none and restore configuration_op
- `32f6f3621` 2026-08-21 03:11 feat: multi-item count-up app with zen-paper widget
  - `c678dd3fd` +0.7h  fix: harden data recovery, lock store writes, and apply review fixes
- `5e88e768a` 2026-08-22 23:32 feat(widget): instant in-place reset with home-screen Toast feedback
  - `58618f707` +0.1h  fix(widget): use applicationContext for Toast in ResetCountReceiver
- `870b14811` 2026-08-29 23:33 feat(themes): add 17 new classical poetic themes expanding the grand collection 
  - `0e7a7463c` +0.5h  fix(widget): implement isotropic vector coordinate system and centerCrop lay

## R2 - Fix storms (>= 5 consecutive fix commits)

A run of fixes with no intervening feature or refactor commit. The work landed
before it was ready. Ask what review or test step was skipped.

None found.

## R3 - Fix-cluster files (>= 3 fix commits)

| fixes | path |
| --- | --- |
| 12 | `app/src/main/java/com/countup/app/CountUpContent.kt` |
| 9 | `app/build.gradle.kts` |
| 7 | `app/src/main/res/xml/zen_pebble_widget_info.xml` |
| 5 | `app/src/main/java/com/countup/app/HeroWidgetReceiver.kt` |
| 5 | `app/src/main/res/xml/hero_widget_info.xml` |
| 5 | `app/src/main/java/com/countup/app/ZenPebbleWidgetReceiver.kt` |
| 4 | `app/src/main/AndroidManifest.xml` |
| 4 | `app/src/main/java/com/countup/app/CountUpViewModel.kt` |
| 4 | `app/src/test/java/com/countup/app/CountUpViewModelTest.kt` |
| 4 | `app/src/main/java/com/countup/app/MainActivity.kt` |
| 4 | `app/src/main/java/com/countup/app/CountUpStore.kt` |
| 3 | `app/src/main/res/values-zh/strings.xml` |
| 3 | `app/src/debug/java/com/countup/app/WidgetHostActivity.kt` |
| 3 | `app/src/main/java/com/countup/app/CountUpWidget.kt` |
| 3 | `app/src/main/res/layout/countup_hero_widget_2x1.xml` |
| 3 | `app/src/main/res/values-zh-rCN/strings.xml` |
| 3 | `app/src/main/res/values-b+zh+Hant/strings.xml` |
| 3 | `app/src/main/res/values-zh-rHK/strings.xml` |
| 3 | `app/src/main/res/values-zh-rTW/strings.xml` |
| 3 | `app/src/main/java/com/countup/app/ZenTheme.kt` |
| 3 | `app/src/main/res/drawable/zen_pebble_widget_preview.xml` |
| 3 | `app/src/main/res/layout/widget_zen_pebble_1x1.xml` |

## R4 - Fix commits that admit a repeat

None found.

## R5 - Fix commits that also changed test code

Two detectors are combined:
  1. the commit touches a separate test file (`test_*`, `*.spec.*`, `tests/`)
  2. the commit's diff adds or removes a test marker (`#[test]`, `def test_`,
     `describe(`, `it(`) - this catches colocated and inline tests

16 of 35 fix commits changed test code (15 by file path, 11 by diff marker).

A low number means fixes ship without a regression test. A non-zero number means
the test was missing or asserted the wrong thing.

- `c678dd3fd` fix: harden data recovery, lock store writes, and apply review fixes
  - `app/src/test/java/com/ivanyang/countup/CountUpItemTest.kt`, `app/src/test/java/com/ivanyang/countup/DateConversionTest.kt`, `app/src/test/java/com/ivanyang/countup/ItemIconsTest.kt`, `app/src/test/java/com/ivanyang/countup/WidgetRowTest.kt`
- `5522dec24` fix(ui): resolve string format parameter for theme toast and add Chine
  - `app/src/test/java/com/countup/app/CountUpViewModelTest.kt`
- `20cd2677f` fix(widget): make 2x1 wide card the exclusive default and only layout 
  - `app/src/test/java/com/countup/app/HeroWidgetTest.kt`
- `b44ae727a` fix(i18n): support Traditional/Simplified Chinese locale switching, di
  - `app/src/test/java/com/countup/app/DaysSinceTest.kt`
- `625f2c387` fix(security,ui): harden credentials, concurrency, widget receivers an
  - `app/src/test/java/com/countup/app/CountUpStoreTest.kt`, `app/src/test/java/com/countup/app/CountUpViewModelTest.kt`
- `edafee3ad` fix(arch): offload startup I/O, decouple widget refresh, and harden re
  - `app/src/test/java/com/countup/app/CountUpViewModelTest.kt`
- `bfc92b580` fix(theme): address review findings - robust Context unwrapping, Abstr
  - `app/src/test/java/com/countup/app/ZenThemeTest.kt`
- `9e3d53f0b` fix(widget,theme): restore 1:1 widget circle parity with app cards and
  - `app/src/test/java/com/countup/app/HeroWidgetTest.kt`, `app/src/test/java/com/countup/app/ItemColorsTest.kt`, `app/src/test/java/com/countup/app/WidgetRowTest.kt`
- `a3230034b` fix(review): address standards & spec review findings - move prototype
  - `app/src/test/java/com/countup/app/CountUpStoreTest.kt`, `app/src/test/java/com/countup/app/ZenThemeTest.kt`
- `b6b4ce0ba` fix(widget): fix 1x1 pebble grid slotting and migrate solar rhythm to 
  - `app/src/test/java/com/countup/app/SolarRhythmWidgetTest.kt`
- `82e9024d7` fix(review): resolve all code standards review findings
  - `app/src/test/java/com/countup/app/SolarRhythmWidgetTest.kt`, `app/src/test/java/com/countup/app/ZenHorizonLayoutTest.kt`
- `15cdb44c3` fix(review): localize micro-unit label, fix test assertions, and fix X
  - `app/src/test/java/com/countup/app/ZenPebbleCompactTest.kt`
- `471e4cc69` fix(widget): universal 1x1 pebble layout for all OEM launchers (Vivo, 
  - `app/src/test/java/com/countup/app/WidgetContractInvariantsTest.kt`
- `433f1d47b` fix(widget): restore auto-launch picker for 1x1 Zen Pebble by removing
  - `app/src/test/java/com/countup/app/WidgetContractInvariantsTest.kt`
- `71b0531e9` fix(review): localize whisper dismiss semantics, improve hit target, p
  - `app/src/test/java/com/countup/app/CountUpViewModelTest.kt`
- `0e7a7463c` fix(widget): implement isotropic vector coordinate system and centerCr (diff marker)

## File activity (fix ratio)

| fix ratio | fixes | total | path |
| --- | --- | --- | --- |
| 1.00 | 3 | 3 | `app/src/main/res/drawable/zen_pebble_widget_preview.xml` |
| 1.00 | 1 | 1 | `app/src/test/java/com/ivanyang/countup/ItemIconsTest.kt` |
| 1.00 | 1 | 1 | `app/src/test/java/com/ivanyang/countup/DateConversionTest.kt` |
| 1.00 | 1 | 1 | `app/src/main/res/drawable/ic_circle_plate.xml` |
| 1.00 | 1 | 1 | `artifacts/prototype_darkmode_strategy.html` |
| 1.00 | 1 | 1 | `app/src/main/res/drawable/widget_solar_badge_bg.xml` |
| 1.00 | 1 | 1 | `app/src/main/res/drawable-v31/widget_zen_bg.xml` |
| 0.88 | 7 | 8 | `app/src/main/res/xml/zen_pebble_widget_info.xml` |
| 0.67 | 2 | 3 | `app/src/test/java/com/countup/app/SolarRhythmWidgetTest.kt` |
| 0.67 | 2 | 3 | `app/src/main/res/xml/zen_horizon_widget_info.xml` |
| 0.62 | 5 | 8 | `app/src/main/res/xml/hero_widget_info.xml` |
| 0.60 | 3 | 5 | `app/src/main/res/layout/widget_zen_pebble_1x1.xml` |
| 0.50 | 1 | 2 | `gradlew` |
| 0.50 | 1 | 2 | `playstore_package/screenshot_6_home_widget.png` |
| 0.50 | 1 | 2 | `playstore_package/screenshot_3_edit_item.png` |
| 0.50 | 1 | 2 | `playstore_package/screenshot_4_date_picker.png` |
| 0.50 | 1 | 2 | `playstore_package/screenshot_2_sort_search.png` |
| 0.50 | 1 | 2 | `playstore_package/screenshot_5_themes_gallery.png` |
| 0.50 | 1 | 2 | `app/src/main/res/values-night/colors.xml` |
| 0.50 | 1 | 2 | `app/src/main/res/xml/locales_config.xml` |
| 0.50 | 1 | 2 | `app/src/main/java/com/countup/app/WidgetMemoryBudgetGate.kt` |
| 0.50 | 1 | 2 | `app/src/main/java/com/countup/app/ZenHorizonTrackRenderer.kt` |
| 0.50 | 1 | 2 | `app/src/main/res/drawable/widget_zen_bg.xml` |
| 0.50 | 1 | 2 | `app/src/main/res/layout/widget_solar_rhythm_2x2.xml` |
| 0.50 | 1 | 2 | `app/src/main/res/layout/widget_solar_rhythm_4x2.xml` |
| 0.43 | 3 | 7 | `app/src/main/res/layout/countup_hero_widget_2x1.xml` |
| 0.40 | 2 | 5 | `app/src/main/res/layout/countup_hero_widget_1x1.xml` |
| 0.40 | 2 | 5 | `app/src/test/java/com/countup/app/WidgetContractInvariantsTest.kt` |
| 0.38 | 3 | 8 | `app/src/debug/java/com/countup/app/WidgetHostActivity.kt` |
| 0.33 | 2 | 6 | `app/src/test/java/com/countup/app/ZenThemeTest.kt` |

