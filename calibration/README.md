# Evaluator calibration

Calibration asks whether an evaluator's decisions agree with known cases and
whether its cited evidence supports those decisions. It measures the evaluator,
not a creator platform's game quality.

[judge-v1/cases.json](judge-v1/cases.json) selects focused platformer/racing
checks from the [authored fixtures](../fixtures/README.md).
The [judge development guide](../docs/judge-calibration.md) describes preparation,
the free preflight, separately authorized model runs and error analysis.

Native trajectories and generated reports stay in ignored local `jobs/` and
`artifacts/`. Publishing a calibration result needs a reviewed export and the
owner's permission. A small development cohort is not held-out validation or a
general game-quality benchmark.

[Current development status](../docs/project-state.md) · [Methodology](../docs/methodology.md#calibrate-the-evaluator)
