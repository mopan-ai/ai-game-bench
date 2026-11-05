# Task catalog

Choose a task and an exact policy version before recording. **Executable tasks**
run through Harbor; **browser protocols** describe tests an authorized operator
or agent performs with its own tools. Listing a protocol does not make it a
working creator adapter or a calibrated gameplay judge.

## Available methods

| Task | Instructions and evaluation | Policy | Current evidence |
| --- | --- | --- | --- |
| Click counter | [Executable calibration](../datasets/smoke-create-v0.2/create-click-counter-zh-001/) | [counter-calibration-v1](../policies/counter-calibration-v1.json) | Free Oracle/Nop and good/fault fixture checks; binary interaction reward |
| Classic Tetris | [Browser pilot v1](../protocols/tetris-browser-pilot-v1/evaluation.md) | [tetris-browser-pilot-v1](../policies/tetris-browser-pilot-v1.json) | [Accepted affiliated pilots](../reports/README.md#accepted-evidence); no independent generation reproduction |
| 2D platformer | [Browser method v2](../protocols/platformer-browser-pilot-v2/evaluation.md) | [platformer-browser-pilot-v2](../policies/platformer-browser-pilot-v2.json) | Focused [pass/fault fixtures](../fixtures/calibration/gameplay-v1/README.md); no accepted public creator submission |
| 3D racing | [Browser method v2](../protocols/racing-3d-browser-pilot-v2/evaluation.md) | [racing-3d-browser-pilot-v2](../policies/racing-3d-browser-pilot-v2.json) | [Report 007 evidence and review](../reports/README.md#accepted-evidence); accepted as a development pilot |

## Web 3D creation suite

[Web 3D suite v1](../protocols/web-3d-create-v1/README.md) groups six engine-agnostic
browser methods. Its [suite manifest](../protocols/web-3d-create-v1/suite.json)
pins the policies. It is a catalog, not an executable batch runner or one combined
scoring policy.

- [Racing v2](../protocols/racing-3d-browser-pilot-v2/evaluation.md) — driving, camera, boundaries, ordered checkpoints and lap completion.
- [3D platformer v1](../protocols/platformer-3d-browser-pilot-v1/evaluation.md) — spatial movement, jumping, landing and progression.
- [Physics puzzle v1](../protocols/physics-3d-browser-pilot-v1/evaluation.md) — physical interaction and a solvable objective.
- [Target range v1](../protocols/target-range-3d-browser-pilot-v1/evaluation.md) — aiming, hits, feedback and completion.
- [Escape room v1](../protocols/escape-3d-browser-pilot-v1/evaluation.md) — exploration, interactions, puzzle state and escape.
- [Garden simulation v1](../protocols/garden-3d-browser-pilot-v1/evaluation.md) — interacting systems, progression and readable state.

The methods were merged in [PR #17](https://github.com/mopan-ai/ai-game-bench/pull/17).
Their frozen metadata still says `proposed`. Racing evidence was later accepted
with limitations in [PR #18](https://github.com/mopan-ai/ai-game-bench/pull/18#pullrequestreview-5783069282);
this does not certify the suite or satisfy full-game evaluator calibration.
Other local development runs are described in [Project state](project-state.md),
not presented as accepted public submissions.

## Versions and scoring

- `uv run agb tasks` lists executable Harbor tasks only.
- `uv run agb submission policies` lists export policies, including browser methods.
- Earlier platformer/racing versions remain in [protocols/](../protocols/README.md).
  A newer method does not change old results.
- Historical Tetris comparisons use separate [fixed scoring rules](../scoring/README.md).
  Report-only retrospective calculations remain labeled and separate from frozen-policy scores.

[Run locally](running.md) · [Submit a result](submissions.md) · [Add a task](adding-tasks.md)
