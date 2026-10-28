# Independent gameplay judge calibration

Calibrate the evaluator against **existing acceptance cases before scoring a
creator**. This is a development check, not a creator leaderboard or a held-out
estimate of judge accuracy. The existing free counter calibration is unchanged.

## What this first cohort checks

The catalog in [`calibration/judge-v1`](../calibration/judge-v1/cases.json) selects
four probes from our existing [platformer/racing acceptance pack](../fixtures/calibration/gameplay-v1/README.md).
Each has a working version and one known fault, each evaluated twice in a fresh
context: **16 sessions, one attempt each, zero Harbor retries**.

| Existing policy | Acceptance item | Focused probe / known fault |
| --- | --- | --- |
| `platformer-browser-pilot-v2` | `jump` | Real ascent/descent/landing vs. a color change |
| `platformer-browser-pilot-v2` | `solid-platforms` | Standing on a raised surface vs. falling through |
| `racing-3d-browser-pilot-v2` | `acceleration` | Scenery-relative motion vs. speedometer-only change |
| `racing-3d-browser-pilot-v2` | `braking` | Braking vs. coasting, matched conditions, without collision |

These are **partial probes**, not complete acceptance of those policies. The
jump probe does not certify raised-platform landing. Tetris scores, production
games, full-game completion, aesthetics and playability are outside this cohort.

## Run locally

Requires Docker, the pinned Harbor environment, Codex CLI **0.165.0**, and an
existing ChatGPT login. The model is explicitly selected; there is no fallback.
Model calls require the operator's authorization. Preparing or reporting makes
no model calls. Use a new output directory for each cohort.

```sh
# Only after authorizing the 16 evaluation sessions:
uv run --locked agb calibration prepare artifacts/judge-cohort \
  --model gpt-6.1-sol --effort high --allow-model-calls

# Harbor owns execution, timeouts, containers, artifacts and retries.
HARBOR_TELEMETRY=0 uv run --locked harbor run \
  --config artifacts/judge-cohort/job.json

uv run --locked agb calibration report jobs/judge-cohort \
  --plan artifacts/judge-cohort/plan.json > artifacts/judge-cohort/report.json
uv run --locked agb view
```

Without `--allow-model-calls`, the generated configuration refuses model runs.
For a free browser/capture preflight, copy the generated job configuration,
select one task, give it a new job name and replace the agent import path with
`ai_game_bench.judge_agent:CaptureSmokeJudge`. It deliberately returns
`not_tested`; its zero reward is expected and is not a game failure. It never
calls a model. Do not include that job in the real calibration report.

A cohort can be split across native jobs (for example, first session then the
remaining 15). Pass all job directories to `calibration report`; duplicate case
IDs, reused context IDs, changed prompts/models/effort/runtime hashes are rejected.
Do not retry a difficult case and silently select the better result.

`./scripts/test-judge-calibration.sh` runs eight free, DOM-assisted regression
checks to confirm the anonymized copies retain the source fixtures' behavior.
It uses the existing authored probes; it is not another independent judge.

## Separation and evidence

- The evaluator receives the focused acceptance instruction, screenshots and
  ordinary mouse/keyboard controls. It receives no creator conversation or
  expected label. Opaque case IDs and identical instructions hide the variant.
- Original fixtures are retained. Derived copies remove variant links and
  select one case. Source, policy, rendered fixture and instruction hashes are
  recorded in the local plan. The answer is supplied to the verifier after play.
- Each browser runs inside Harbor's network-isolated container. The local Codex
  adapter uses an empty temporary working directory and isolated Codex settings.
  Login credentials stay in a private temporary directory outside the repo,
  never inside the game container, and are removed at the end of the session.
- Each probe gets 300 seconds, 60 actions and six starts/restarts. Browser time
  is real time; it continues while the model thinks. This is deliberately shorter
  than the full game policy's evaluation budget. Harbor's 300-second agent timer
  begins after setup; the browser budget begins when the page is ready.
- Native jobs retain model/effort/version, token usage, elapsed time, actions,
  screenshots, video, final verdict and the grader's plain JSON output.
  Subscription marginal charges remain unknown, not zero.

The model runs on the host through Codex; the game runs in Docker. This is not an
OS-isolated adversarial evaluator. The adapter restricts browser tools, instructs
Codex not to use other tools, and the report audits native tool events. A recorded
file/shell/search/other tool use invalidates the measurement. Configuration
warnings are retained; a configuration flag alone is not proof of restricted
access. Raw native logs are local-only and require a separate reviewed export
before publication.

The first local cohort used adapter 0.1.0. Native audits found only browser tool
calls, but three configuration keys were ignored by Codex. Adapter 0.1.1 fixes
those keys, disables host file/image/browser helpers and rejects unexpected tool
starts. Its configuration-only preflight passed; a real model cohort has not
been rerun under 0.1.1. Keep the original runtime hash and result, rather than
transferring the old accuracy claim to a changed adapter.

## Read the result and close the loop

1. Read **correct / valid trials**, false passes / faulty trials, false failures /
   working trials, `not_tested`, invalid measurements and missing trials together.
   `not_tested` earns no correctness credit, even on a faulty fixture.
2. Check repeat agreement separately. A grader can be consistently wrong.
3. Inspect cited frames against the actions and video. The verifier checks
   citation/hash integrity and label agreement, not the meaning of an image.
4. Record whether evidence actually supports the verdict, the failure mechanism
   and the exact native result hash. Keep this review separate from the model's
   original verdict. AI-assisted maintainer inspection is not human consensus.
5. Version any prompt/tool/judge change and rerun an explicitly authorized cohort.
   Keep this development set for regression; add unfamiliar implementations as a
   held-out check before evaluating real creator outputs.

Attach a local review with `calibration report ... --review evidence-review.json`.
The review uses `schema_version: judge-evidence-review/0.1`, `reviewer`, `blind`,
`scope`, and `records` containing `case_id`, `native_result_sha256`, `finding`
(`supported`, `unsupported`, `inconclusive`) and a note. Record the inspected frame
IDs too. Matching result hashes binds the note to a trial; it does not certify the
reviewer's identity. Review findings never overwrite model verdicts or label metrics.

Do not publish "calibrated gameplay verification" based on a structurally valid
report or a small perfect result. An initial useful gate is: all 16 accounted for,
no unexplained access/infrastructure failures, inspected evidence for decisive
verdicts, and an explicit list of checks that still need work. Any false pass or
unsupported pass blocks automatic use of that check on real submissions.
