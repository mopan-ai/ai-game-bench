# Browser-observation protocols

These versioned, data-only protocols describe observable tests of hosted games.
They are **not executable Harbor tasks**, unattended adapters or calibrated AI
judges. `agb run` continues to accept only Harbor packages under `datasets/`.

Each protocol contains a prompt, identity, rubric and evaluation procedure.
A file in `policies/` pins those bytes. The public submission validator checks
records, references and arithmetic; a maintainer must still inspect the evidence.
No submitted game or script is executed by this lane.

The [Web 3D suite v1](web-3d-create-v1/README.md) catalogs six engine-agnostic
creation tasks with exact policy hashes, instructions, rubrics, acceptance steps
and hypothetical pass/fault examples. It reuses racing v2 unchanged and adds
platformer, physics, target-range, escape and simulation methods. These are
method candidates; full gameplay calibration and live comparisons remain gated.

Use the [task catalog](../docs/tasks.md) to choose a version. The
[results index](../reports/README.md#accepted-evidence) links accepted Tetris
evidence and the racing development pilot. Pilot acceptance does not change
frozen method readiness or satisfy full-game calibration gates.

- [Classic Tetris pilot v1](tetris-browser-pilot-v1/evaluation.md): one fresh
  browser creation, normal player input, nine core checks and four UX checks.
  This is a new pilot scale, not comparable to historical website scores.

## Platformer and racing methods

Method definitions were merged in [PR #9](https://github.com/mopan-ai/ai-game-bench/pull/9)
and extended by [measurement v0.2](../docs/measurement.md). The task metadata still
declares `status: proposed`: these are not calibrated live-platform benchmarks.
The original v1 contracts and their acceptance examples remain unchanged.

- [2D platformer v1](platformer-browser-pilot-v1/evaluation.md): pixel-art level,
  movement/jump, solid platforms, coins, loss/win and both restart paths.
  [Acceptance steps and examples](platformer-browser-pilot-v1/acceptance.md).
- [3D racing v1](racing-3d-browser-pilot-v1/evaluation.md): low-poly timed lap,
  driving/camera, boundaries, ordered checkpoints, finish and restart.
  [Acceptance steps and examples](racing-3d-browser-pilot-v1/acceptance.md).

The [platformer v2](platformer-browser-pilot-v2/evaluation.md) and
[racing v2](racing-3d-browser-pilot-v2/evaluation.md) methods add explicit evaluator
configuration and timeout/error accounting while retaining v1 prompt/rubric bytes.

See the [method proposal and Mopan validation plan](../docs/proposals/platformer-racing-pilot.md).
Listing a policy is not evidence that the live-pilot acceptance gates have passed.
Existing Tetris/counter versions and historical results are unchanged.
The [local reference fixtures](../fixtures/calibration/gameplay-v1/README.md)
exercise focused pass/fault probes, not a general or independently calibrated judge.
