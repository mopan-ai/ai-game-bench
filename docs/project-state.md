# Project state

Updated 2026-10-28. This public repository contains the benchmark's methods,
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
| Platformer / 3D racing | Merged method definitions, acceptance cards and authored pass/fault fixtures | Protocols still declare `proposed`; no accepted live creator results |
| Measurement v0.2 | Merged evaluator metadata, timeout semantics and offline summaries | Summarizes declared claims, not independently verified gameplay |
| Gameplay judge | Local development implementation and focused calibration | No held-out or full-game quality calibration; see version caveat below |

## Accepted public evidence

- **Gemini 4 · Tetris:** [PR #4](https://github.com/mopan-ai/ai-game-bench/pull/4),
  [package](../submissions/mopan-gemini4-tetris-20261014/),
  [acceptance scope](https://github.com/mopan-ai/ai-game-bench/pull/4#issuecomment-6162702189),
  [limited artifact replay](../reviews/mopan-gemini4-tetris-20261014/20261014/).
  r001 creation, r002 cost and r003 scoring are revisions of **one attempt**.
- **DS V4.1 1017 · Tetris:** [PR #10](https://github.com/mopan-ai/ai-game-bench/pull/10),
  [package](../submissions/mopan-ds-v41-flash-1017-tetris-20261020/r001/),
  [review scope](https://github.com/mopan-ai/ai-game-bench/pull/10#pullrequestreview-5661885193).
  Evidence inspection and limited replay do not attest original model routing,
  reported cost or the complete creation history.

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

## Next acceptance gates

1. Freeze a candidate evaluator; validate on unfamiliar implementations and
   obtain human adjudication of disputed or decisive evidence.
2. Run a separately authorized platformer/racing creator pilot only after its
   method and evaluator gates are satisfied. Keep all attempts and gaps.
3. Have an outside contributor complete submission → trusted checks → review
   using only public instructions. Publication remains a separate decision.
4. Develop a reusable browser recorder/adapter, beginning with a free local mock.

No automatic optimizer, training pipeline, general subjective-quality judge or
representative cross-game leaderboard is implemented.

## Validation history

The latest runtime validation before this documentation revision passed 426 fast
checks, 13 separate counter browser checks and eight derived-fixture parity
checks; native Oracle/Nop scored 1/0 with no exceptions. Fast tests skipped 46
browser checks. The 32 unchanged original gameplay regression checks were not
repeated in that turn. These are local observations, not new remote CI results.

[Dated validation snapshots](history/validation-log.md) retain prior counts,
cost/score details, limitations and remote run links. Use that history for audit;
use this page for current scope.
