# Versioned run and scoring policies

Task = what to build. Policy = execution limits and permitted interventions.
Eval = what observations justify each score. A policy pins instruction, rubric
and verification-procedure hashes, plus run limits and score mapping. Default
`task.kind: harbor` reads `datasets/`. `browser_protocol` reads data-only manual
procedures in `protocols/`; its `verifier_sha256` pins `evaluation.md`, not an
executable verifier. This does not introduce another runner or claim automatic
verification of browser games.

Use `uv run agb submission schema policy` for the exact format and
`counter-calibration-v1.json` as a packaging example, not a universal game rubric.
This example preserves the counter's original 0/1 meaning. Do not change its bytes
or reinterpret historical Tetris reports using this policy.

To contribute: add a new ID/file, freeze task hashes, define reference/negative
cases and add tests. Run `uv run agb submission policies` and `./verify.sh`.
Check the [task guide](../docs/adding-tasks.md). Maintainers must approve the method
before formal results cite it; CI only checks structure. Changed meaning requires
a new version. Weights cannot be supplied by a result author.

For each attempt, total = `total_max × sum(weight × score / max_score) / sum(weight)`.
Partial credit requires `allow_partial: true` on that criterion; default false
preserves binary tasks such as the existing counter calibration.
Failed/not-tested criteria earn zero with a distinct reason; any infrastructure
error makes the total null. No criterion is silently dropped or renormalized.
Known failures may score zero while the evidence package itself is valid.

The optional delivery-time rule recomputes its criterion from the accepted/final
timestamps and requires specified gameplay checks to pass. Record actual sampled
times; timestamp arithmetic cannot establish capture authenticity.

## Proposed v0.2 browser measurements

The new `platformer-browser-pilot-v2` and `racing-3d-browser-pilot-v2` preserve
their v1 prompts, criteria and weights, but distinguish generation timeout
(zero, unsuccessful delivery) from auth/evaluator infrastructure errors (null).
`measurement` pins core criteria, allowed access, viewport, clock and budgets;
v0.2 manifests require evaluator configuration. These are method proposals,
not authorization for live runs. [Rules and offline summaries](../docs/measurement.md).
All v0.1 contracts, including their null timeout totals, remain unchanged.
