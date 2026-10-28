# Architecture and evaluation boundary

```text
agb → Harbor task → agent → submission.json → isolated verifier → Harbor jobs/
                                                                      ↓
                                                                Harbor Viewer
```

`agb` resolves a local task and delegates execution to pinned Harbor 0.22.0.
It does not manage scheduling, retries, account sessions or an alternative result
store. Default run: one attempt, one concurrent trial, zero retries. Telemetry
is disabled for Harbor commands launched by the wrapper.

## Submission and verification

The current task accepts `/workspace/gamebench/submission.json`:

```json
{
  "schema_version": "0.1",
  "kind": "local_directory",
  "entrypoint": "/workspace/game/dist/index.html"
}
```

The verifier consumes that file plus a game directory and rubric, and emits
plain JSON. It does not import Harbor. `tests/test.sh` is the thin Harbor bridge.
The game bundle is frozen and hashed before a separate browser verifier runs.
Do not execute untrusted game/verifier code on a workstation outside a sandbox.

The calibration requires DOM selectors, and uses Playwright DOM interactions.
It is **not** pure-vision computer use and cannot evaluate arbitrary canvas/3D
games or external URLs. A future URL/screenshot track needs a separate task and
verifier version; it must not silently relax this offline contract.

## Score honesty

| Outcome | Reward | Interpretation |
| --- | --- | --- |
| All counter checks pass | `overall=1` | This specific interaction contract passed |
| Missing/invalid submission or broken game | `overall=0` | Scored failure, reason retained |
| Valid `kind: build_failure` | `overall=0` | Creator reported a build failure |
| Browser setup / verifier infrastructure failure | No reward; Harbor exception | Evaluation did not complete |

`artifact_contract`, `runtime_smoke` and `gameplay_interaction` expose the layers.
Do not average these binary gates into a game-quality or model ranking score.
Harbor process exit zero alone does not prove success: `agb inspect` checks both
job and trial records. Nop scoring zero with no exception is a successful
negative calibration.

For comparisons, freeze task, rubric, evaluator, attempts, interaction policy and
runtime conditions. Record creator identity/model/effort as unknown when unseen.
Do not infer backend model identity from a marketing label. Preserve measured
duration, credit valuation, model-cost estimate and actual payment separately.

## Data and publication

`jobs/` is the canonical local Harbor record, excluded from Git. Public report
references and evidence exports do not replace trial JSON. The public export uses
`manifest.json` with schema `public-submission/0.1`; it is distinct from the
game-to-verifier `submission.json` contract above. Existing frozen task bytes are
unchanged. `policies/` pins their identity and the export's score mapping.

`agb submission` creates/checks publication exports, not runs or a second result
database. Browser observations may use the same export once their task/policy is
approved; they are never misrepresented as native Harbor trials. The validator
does not execute submitted code or fetch URLs. Maintainers use a trusted revision
and independently inspect evidence, not contributor-authored checks.

Data-only browser protocols live in `protocols/`, outside executable Harbor
datasets. Their policy pins a manual `evaluation.md` procedure. They support
transparent pilot observations while an unattended adapter/verifier is absent;
they do not create a parallel runtime, job store or automatic judge.

Public submission data is public by default, with pre-upload rights/privacy
confirmation. Credentials, private content and whole raw jobs never enter Git.
No additional training agreement is inferred; reuse follows the declared license.
See [public-data terms](../README.md#public-data-and-privacy-terms).

The proposed [v0.2 measurement contract](measurement.md) adds evaluator metadata,
separate timeout/error semantics and offline selected-set summaries. It uses the
same export path; v0.1 records and frozen task/verifier bytes remain unchanged.
These numeric checks are not an independent gameplay evaluator or a leaderboard.
