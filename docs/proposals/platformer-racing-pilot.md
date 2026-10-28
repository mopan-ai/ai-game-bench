# Proposal: 2D platformer and 3D racing

**Historical v1 proposal.** Definitions were merged in
[PR #9](https://github.com/mopan-ai/ai-game-bench/pull/9); follow-on
[measurement v0.2](../measurement.md) was merged in PR #14. Task metadata retains
`status: proposed`, with evaluator calibration and live-pilot gates still open.
The original proposal below documents its design and acceptance plan; its v1
commands are historical. See [current state](../project-state.md) before a run.
This proposal exercises the same public path as an external contributor. Its
author/operator is affiliated with Mopan; it is not independent third-party review.

## What this adds

| Method | Prompt | Evaluation |
| --- | --- | --- |
| `platformer-browser-pilot-v1` | [2D platformer](../../protocols/platformer-browser-pilot-v1/instruction.md) | [Nine core checks, UX and time](../../protocols/platformer-browser-pilot-v1/evaluation.md) |
| `racing-3d-browser-pilot-v1` | [3D racing](../../protocols/racing-3d-browser-pilot-v1/instruction.md) | [Nine core checks, UX and time](../../protocols/racing-3d-browser-pilot-v1/evaluation.md) |

Both are platform-neutral, data-only browser protocols. They reuse the public
submission contract, not a new runner. Each includes a prompt, rubric, evaluation
procedure, pinned policy and hypothetical positive/negative review cases. No
source export or private integration is needed. They are not `agb run` tasks.

The two games cover different capabilities, not just different art styles:

| Capability | 2D platformer | 3D racing |
| --- | --- | --- |
| Input and motion | Bidirectional movement, jump and landing | Acceleration, matched braking and steering |
| Spatial behavior | Ground/platform collision and pit loss | Visible 3D depth, follow camera and both track boundaries |
| Stateful rules | One-time coin collection, goal and loss | Ordered checkpoints, legal lap and frozen final time |
| Recovery | Fresh state after both loss and victory | Fresh car, timer and checkpoint state after finish |
| Presentation | Pixel-art legibility, instructions and feedback | Low-poly legibility, route guidance and feedback |

Every core check has an action sequence and pass/fail examples in its acceptance
card. The fixtures demonstrate selected behaviors only; they are not full-score
reference games or independent human labels.

Proposed weights match the existing browser pilot: core 60, observable experience
and visuals 10, delivery time 30; every item uses 0–10. Cost is reported, not scored.
The prior website/Tetris 40/20/20/20 scores are unchanged and not comparable.
Do not aggregate different games into a leaderboard from one attempt per task.

## Acceptance before running

1. A maintainer reviews the exact method revision, including prompt-to-criterion
   alignment, weights, core gates for time credit and the hypothetical defect cases.
2. Check browser-only feasibility within 30 minutes / six player sessions. Racing
   braking comparisons and invalid-order checkpoint probes are particular review
   risks; do not silently infer passes if the tool cannot demonstrate them.
3. Review the [platformer acceptance card](../../protocols/platformer-browser-pilot-v1/acceptance.md)
   and [racing acceptance card](../../protocols/racing-3d-browser-pilot-v1/acceptance.md).
   Replay the [authored pass/fault fixtures](../../fixtures/calibration/gameplay-v1/README.md)
   twice using `./scripts/test-gameplay-calibration.sh`. Inspect videos, actions,
   false-pass/false-failure counts and coverage limits. These are fixture-specific
   DOM-assisted checks, not complete game or independent AI evaluation.
4. Calibrate the intended evaluator separately on blind game-only cases, retaining
   missing observations, infrastructure errors and repeated-decision agreement.
   Do not expose reference labels or use this package's script results as the
   evaluator's accuracy. `./verify.sh` additionally covers method identity,
   arithmetic, rejection cases and synthetic package export.
5. Submit/approve the method PR before formal results. Record its merge revision
   and policy hashes in the run notes. Passing CI is not method approval.

`review-cases.json` remains hypothetical; the separate local fixtures are authored
behavior examples with actual browser replay evidence, not model-generated games
or accepted platform submissions. Neither establishes independent judge accuracy.
Acceptance may authorize a limited development pilot to test feasibility; label
that result accordingly. If rules change after observing a pilot, make a new
version and rerun before calling it a preregistered/formal result.

## Planned first validation: Mopan / Gemini 4 Argon

After method approval, confirm live-run permission and the exact visible model
label in the owner-selected Chrome profile. Run each task in a new project, once,
with all other settings default, no repair/regeneration and a 60-minute cap each.
The two tasks have independent histories and evidence packages. A missing model,
quota prompt or purchase request blocks that run; do not substitute or buy credits.
This proposal starts no model calls, public-game publishing or uploads.

Use only normal creation/play pages and public documentation. No admin/cost pages,
internal APIs, private scripts, database queries or backend usage supplements.
Visible task credits plus documented public prices may support an explicitly
labelled valuation; otherwise cost stays unknown. UI model labels are not backend
attestation. Respect login/control permission and do not copy session state.

Record during execution: model selection, Send/accepted receipt, progress at most
30 seconds apart when feasible, all follow-ups, capture gaps, final delivery and
game URL/build. Evaluate separately on the game-only surface. If the same operator
knows creation context, disclose non-blind evaluation. Keep task-scoped clips or
action/frame sequences for motion; still screenshots alone are insufficient.

## Contributor commands and submission

From a fork containing the reviewed method revision:

```bash
uv sync --locked
uv run agb submission policies
uv run agb submission init .submission-drafts/platformer-run --id platformer-run --policy platformer-browser-pilot-v1
uv run agb submission init .submission-drafts/racing-run --id racing-run --policy racing-3d-browser-pilot-v1
```

These commands create unapproved local shells with no observed events. The
`source_kind` is `browser_observation`; set evaluation mode to the actual human,
DOM-assisted agent or visual agent route. Never call it deterministic verification.
Fill observations as they occur; do not turn hypothetical examples into run data.

After capture, evaluate all criteria and add reviewed files to each manifest's
allowlist. Use [the public submission guide](../submissions.md) for privacy/rights
review, `prepare`, `validate` and the result PR. Publication requires separate owner
approval. Keep the method proposal separate from result PRs and unrelated changes.

The handoff is two playable artifact references, two creation/evaluation trails,
criterion-level scores with evidence, observed duration, cost basis/unknowns and
a list of method ambiguities. Maintainers use the existing
[untrusted-evidence checklist](../reviewing-submissions.md), inspect claims and
replay core paths where possible. Structural validity is not acceptance.
