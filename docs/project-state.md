# Project state

Updated 2026-11-10. This public repository contains the benchmark's methods,
execution entry point and reviewed evidence. The website and private historical
jobs remain in a separate repository. [Methodology](methodology.md) describes the
measurement design; the table below describes implementation, not aspirations.

## Capability matrix

| Surface | Current state | Boundary |
| --- | --- | --- |
| Local execution | Thin `agb` CLI delegates to pinned Harbor 0.22.0 | No additional runner, database or automatic publisher |
| Counter calibration | Runnable free Oracle/Nop task with browser checks | DOM-specific binary interaction contract, not game quality |
| Six creator platforms | Recorded workflows and connection references | No reusable unattended creator adapters |
| Public submissions | Versioned packages, validators and maintainer review | Structural validity does not authenticate observations |
| Classic Tetris | Accepted Gemini 4 and DS V4.1 1017 evidence packages | Affiliated pilots with disclosed gaps; not independently reproduced creation |
| 2D platformer | Merged method definitions, acceptance cards and authored pass/fault fixtures | Protocol still declares `proposed`; no accepted public creator submission |
| 3D racing | Codex / Mopan / Wanaka evidence accepted in PR #18 | Development pilot with non-blind remote evaluation, differing timing bases and public-replay limits; not a calibrated leaderboard result |
| Web 3D creation suite v1 | Six versioned browser methods merged in PR #17 | Five new methods plus unchanged racing v2; proposed metadata retained, no full-game calibration or accepted full-suite comparison |
| Measurement v0.2 | Merged evaluator metadata, timeout semantics and offline summaries | Summarizes declared claims, not independently verified gameplay |
| Three-game retrospective | Versioned 50/20/30 policies and an offline arithmetic helper in [scoring](../scoring/three-game-review-v1.md) | Final-artifact review 1.2 retains disclosed continuations; not a new accepted result or calibrated leaderboard |
| Gameplay judge | Local development implementation and focused calibration | No held-out or full-game quality calibration; see version caveat below |

## Accepted public evidence

The [results index](../reports/README.md#accepted-evidence) is the current catalog
of accepted packages, exact-revision reviews and website reports. It includes the
two Mopan Tetris submissions and the racing development pilot accepted in
[PR #18](https://github.com/mopan-ai/ai-game-bench/pull/18#pullrequestreview-5783069282).
That review covered structure, score/cost arithmetic and sampled evidence; it did
not replay artifacts or rerun generation. Acceptance preserves the disclosed
limitations and does not authenticate unseen model routing or creation history.

The method history includes [PR #9](https://github.com/mopan-ai/ai-game-bench/pull/9)
for platformer/racing proposals and [PR #14](https://github.com/mopan-ai/ai-game-bench/pull/14)
for measurement v0.2. Merged method code is not authorization to call a platform,
claim calibrated gameplay verification or publish a new result.

Trusted structural review and public CI have actual historical successful runs,
including [PR #10 CI](https://github.com/mopan-ai/ai-game-bench/actions/runs/40457773349)
and [trusted validation](https://github.com/mopan-ai/ai-game-bench/actions/runs/40458724927).
These dated receipts do not establish the latest GitHub enforcement state. Local
workflow files and a passing local test are not evidence of an active branch rule.

## Local evaluator development

<details>
<summary>Development cohorts and version limitations</summary>

The [judge calibration](judge-calibration.md) selected four checks from the
existing platformer/racing fixtures: working/faulty variants, two repetitions
each, **16 sessions with no retries**. Codex `gpt-6.1-sol` / high had 16/16 label
agreement, 0/8 false passes, 0/8 false failures and 8/8 repeat agreement, with no
abstentions or native exceptions. Separate non-blind AI evidence inspection
supported all 16 verdicts from selected cited frames and actions; no human review
was performed. This is a small public development set, not held-out accuracy.

The cohort used adapter **0.1.0**. Native events showed only browser-tool use, but
three configuration flags were ignored. Adapter **0.1.1** fixes those flags and
adds tool restrictions; its free configuration preflight passed. No model cohort
has been rerun under 0.1.1, so the earlier result does not transfer to that version.

Native jobs and the HTML/JSON report remain local in ignored `jobs/` and
`artifacts/judge-calibration-20261028/`: 401 screenshots, 16 videos, usage receipts
and separate review notes. No creator was called or historical Tetris score
changed by this cohort. The cohort's raw records remain local; no public result
export is included.

The Web 3D candidate suite also has a separate local development pilot: six fresh
Codex / `gpt-6.1-sol` / high creations delivered browser artifacts, followed by
game-only evaluation contexts. This used temporary Harbor tasks and experimental
local evaluator revisions, not a new public executable suite or working platform
adapters. Tool-dispatch, input-timing and final-report timeout problems were found;
affected sessions and corrected replays are retained separately. Sparse images
also left dynamic checks incomplete. Raw records and the diagnostic report stay
in ignored `jobs/` and `artifacts/web-3d-dev-20261102/`. This pilot does not satisfy
the known-good/fault, unfamiliar-implementation or human-adjudication gates.

</details>

## Next acceptance gates

1. Freeze a candidate evaluator; validate on unfamiliar implementations and
   obtain human adjudication of disputed or decisive evidence.
2. Satisfy the method/evaluator gates before a controlled platformer/racing
   comparison. The accepted racing development pilot supplies preliminary
   evidence, not a substitute for those gates. Keep all attempts and gaps.
3. Have an outside contributor complete submission → trusted checks → review
   using only public instructions. Publication remains a separate decision.
4. Develop a reusable browser recorder/adapter, beginning with a free local mock.

No automatic optimizer, training pipeline, general subjective-quality judge or
representative cross-game leaderboard is implemented.

## Validation history

The local 3D method revision passed **490 fast checks** (46 browser checks
skipped), **13 separate counter browser checks**, and native Oracle/Nop at **1/0**
with no exceptions. The 64 added fast checks cover method identity, submission
compatibility, score gates and invalid-measurement semantics, not gameplay.
The unchanged gameplay fixtures and prior judge cohort were not rerun for this
method revision. These are local observations, not new remote CI results.

[Dated validation snapshots](history/validation-log.md) retain prior counts,
cost/score details, limitations and remote run links. Use that history for audit;
use this page for current scope.
