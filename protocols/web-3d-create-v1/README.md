# Web 3D creation suite v1

Six small, engine-agnostic browser games, each with a complete prompt, policy,
rubric and observable acceptance procedure. **Method candidate:** definitions are
ready for review and local development pilots, not a calibrated leaderboard.
The existing racing v2 contract is reused without changing any of its bytes.

## Tasks and coverage

| Task | Main capability | Style | Instruction / evaluation / rubric |
| --- | --- | --- | --- |
| Timed circuit | Driving, follow camera, boundaries, ordered checkpoints, legal finish | Low-poly | [Prompt](../racing-3d-browser-pilot-v2/instruction.md) · [Eval](../racing-3d-browser-pilot-v2/evaluation.md) · [Rubric](../racing-3d-browser-pilot-v2/rubric.json) |
| Floating islands | Two-axis movement, jumping/height, camera, landing, respawn | Bright toy-like low-poly | [Prompt](../platformer-3d-browser-pilot-v1/instruction.md) · [Eval](../platformer-3d-browser-pilot-v1/evaluation.md) · [Rubric](../platformer-3d-browser-pilot-v1/rubric.json) |
| Marble and crate | Inertia, ramps, contacts, movable objects, pressure-plate state | Tabletop diorama | [Prompt](../physics-3d-browser-pilot-v1/instruction.md) · [Eval](../physics-3d-browser-pilot-v1/evaluation.md) · [Rubric](../physics-3d-browser-pilot-v1/rubric.json) |
| Robot target range | First-person aim, depth/occlusion, hits, ammunition/reload | Neon training arena | [Prompt](../target-range-3d-browser-pilot-v1/instruction.md) · [Eval](../target-range-3d-browser-pilot-v1/evaluation.md) · [Rubric](../target-range-3d-browser-pilot-v1/rubric.json) |
| Room escape | Spatial exploration, proximity/visibility, inventory, ordered locks | Warm wood and metal | [Prompt](../escape-3d-browser-pilot-v1/instruction.md) · [Eval](../escape-3d-browser-pilot-v1/evaluation.md) · [Rubric](../escape-3d-browser-pilot-v1/rubric.json) |
| Small greenhouse | Orbit camera, world picking, placement, economy, timed growth | Pastel miniature | [Prompt](../garden-3d-browser-pilot-v1/instruction.md) · [Eval](../garden-3d-browser-pilot-v1/evaluation.md) · [Rubric](../garden-3d-browser-pilot-v1/rubric.json) |

[suite.json](suite.json) lists exact policy identities and hashes. It is a catalog,
not a new runner configuration. Policies are discoverable with
`uv run agb submission policies`; these data-only protocols are intentionally
absent from `agb tasks` / `agb run`.

3D means observable interactive depth, viewpoint and spatial relationships in a
browser. No engine, rendering API, asset generator, library or source export is
required. A static beautiful scene or flat board does not establish 3D gameplay.
Software projection is allowed if it satisfies the same visible requirements.
These six coverage-selected tasks are a seed set, not all of 3D game development.
Multiplayer, large worlds, mobile gameplay, audio quality and numerical physics/
frame-rate accuracy are outside this version. Genre and style vary together;
results cannot isolate a causal effect of art style or engine choice.

## Shared measurement

| Item | Rule |
| --- | --- |
| Creation | One fresh project, exact Chinese prompt, one attempt, 60 minutes, no repairs |
| Clarifications | Answer actual questions consistently; required Build confirmation is allowed and timed |
| Evaluation | Final game only; visible UI or screenshots with ordinary inputs, real-time clock |
| Budget | 30 minutes, at most six rounds/reloads, scored desktop 1280×800; 390×844 layout check |
| Core | Nine checks, each 0 or 10, weighted to 60 points; all nine needed for core success |
| Experience / visuals | Four criteria, 0–10 with evidence anchors, weighted to 10 points |
| Time | 30 points; only after task-specific main-loop gates pass; ≤5 minutes full credit, 60 minutes zero |
| Missing observations | Zero for that criterion, explicit `not_tested`; no denominator reduction |
| Infrastructure | Null measurement, disclosed/excluded counts; no invented gameplay failure |
| Cost | Record separately with basis, currency and source; no cost score |

The task's pinned `evaluation.md` and policy are authoritative; this summary does
not silently revise racing v2. Compare the same task, exact policy, configuration,
budget and observation route. Report core checks and the 60/10/30 breakdown beside
the total; a fast incomplete game is distinguishable from a completed game.
Equal weights do not make different games equally difficult.

## Contributor path

1. **Method first.** Review the selected task and its `review-cases.json`; racing
   uses the unchanged [v1 examples](../racing-3d-browser-pilot-v1/review-cases.json)
   and [acceptance card](../racing-3d-browser-pilot-v1/acceptance.md). Cases are
   hypothetical examples, not proof a judge works. Follow [adding tasks](../../docs/adding-tasks.md)
   for a method PR. Formal results need a reviewed/merged method first.
2. **Preflight and authorize.** Select platform/model, account/profile, budget,
   runtime, capture route and evaluator before the run. Use the public
   [browser procedure](../../platforms/shared/browser-workflow.md). Platform guides
   are references, not automatic adapters. No private API is needed.
3. **Record and evaluate.** Keep local raw records. Export prompt acceptance,
   all questions, creation progress, final URL/build and a separate gameplay
   trajectory. Every score cites actual observations and supporting media.
4. **Submit public evidence.** Use the existing v0.2 [submission workflow](../../docs/submissions.md).
   Owner-approved task-scoped exports go in a result PR; method files and raw
   jobs are not bundled into it. CI validates structure, not gameplay or truth.
5. **Maintainer review.** Inspect the exact revision, inspect media, replay named
   checks when possible, and state verification scope and limits. A new model
   creation is a separate run; replay is not reproduction of creation.

Start a local, empty export draft (no model call or upload):

```bash
uv run agb submission init .submission-drafts/my-3d-run \
  --id my-3d-run --policy platformer-3d-browser-pilot-v1
uv run agb submission schema event
uv run agb submission schema evaluation-configuration
```

Complete the draft from real evidence; do not turn its initial zeroes/placeholders
into invented observations. After publication approval, use `submission prepare`
and `submission validate` exactly as in the submission guide. `submission summarize`
accepts an explicit set of v0.2 packages and keeps policies/configurations separate.
This suite intentionally has **no cross-game aggregate ranking** yet.

## Local development gate before platform comparisons

Use fresh, isolated development implementations before comparing live platforms.
The initial local pilot uses one Codex / Sol 6.1 generation per task under an
authorized plan; contributors may use other implementations and do not need a
Codex account to contribute a method. Freeze prompt/policy hashes first. Harbor
owns native jobs, workspaces, artifacts and attempts; do not turn `agb` into another
runner or claim the browser protocols already execute unattended. Any temporary
CLI delivery instructions or network/browser differences must be retained and
disclosed. Local builds/localhost URLs and raw jobs remain local, not public result
submissions. This is task-development data, not platform ranking evidence.

For **each task**, record:

- Whether the specification can be built, started and understood; creator failure
  alone does not prove a bad task, and a single success does not prove validity.
- Whether every acceptance step can be reached through ordinary input within the
  budget, especially invalid-order, occlusion, empty-resource and restart paths.
- A criterion-by-criterion record: supporting observations, failures, coverage
  gaps, ambiguous language and tool limitations. No high score from screenshots.
- At least a known-good and a deliberate broken/false-pass example for each
  decisive core rule, with an independent review of the intended label. Text
  examples alone do not satisfy this playable-example gate.
- Where evaluator replay disagrees or cannot complete a check; preserve the first
  run and change the method version before rerunning a changed contract.

Ready for a live pilot means prompt/rubric agreement, feasible acceptance paths,
reviewed good/fault examples and explicit remaining evaluator limitations.
Start the later authorized Mopan/Wanaka comparison on **one agreed task**, then
expand. No live platform run, held-out calibration or publication is implied by
this method package or its passing offline checks.
