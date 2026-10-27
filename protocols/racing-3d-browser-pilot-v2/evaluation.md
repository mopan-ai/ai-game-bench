# 3D racing browser pilot v2 — proposed

Freeze the approved prompt, rubric and policy hash before generation. This is a
**contributor method proposal**, not an approved task or a calibrated game judge.
Use only the public repository and ordinary user interfaces. The method applies
to any compatible game-creation platform; no Mopan-only API, private script,
admin dashboard or privileged usage report is required or permitted.

## Creation policy

- One fresh project, one generation, no prior chat, imported assets, templates,
  custom skills or repair prompts. Native platform defaults remain available.
- Use the run's explicitly authorized model; keep other settings at defaults.
  Record the visible label/source. Hidden backend identity, effort and child-model
  details stay unknown. A requested but unavailable model is a preflight blocker;
  do not silently substitute a model.
- Send exactly `instruction.md` (including its trailing newline when the UI
  preserves it), not this protocol, rubric or defect cases. Do not translate or
  augment it. Record the Send action and the accepted-message receipt separately.
- Answer only actual clarification questions, using the task defaults below.
  A required build confirmation is allowed; unsolicited hints, extensions,
  retries and requests to fix a delivered game are not. Log each question,
  answer, reason and any human intervention.
- At most 60 minutes from accepted prompt to first observed final playable
  delivery. Require a completion signal, no active generation/Stop state and an
  accessible final artifact. Record the last still-working observation and first
  final observation; sampled delivery time is not exact model compute time.
- Capture task-scoped visible progress at least every 30 seconds when the
  connection permits, plus model selection, acceptance, questions, errors and
  delivery. Record actual timestamps and gaps; never backfill missing frames.
- Use only the owner's confirmed browser profile and authorized account.
  No purchases, account-setting changes, public-game publishing, reverse
  engineering, private APIs or admin access. Never switch profiles silently.

## Evaluation boundary and budget

Use only the final game-only surface, this task and the rubric, with ordinary
visible mouse/keyboard actions. DOM may target visible controls; do not inspect
source or hidden game state, invoke game functions, inject inputs through game
internals, or change the clock, RNG, storage or artifact. An unfamiliar control
must be learned from the game, not creator chat. A supplied walkthrough is not
proof of a win.

Use desktop 1280×800 at 100% browser zoom for scored gameplay. Inspect layout at
390×844 separately; mobile controls/playability are not required. Record actual
viewport, device scale, browser, build/version and access requirements. If the
required viewport or ordinary controls cannot be exercised with the available
tool, disclose that limitation rather than changing the game.

Evaluate for at most 30 minutes and six player sessions (initial session plus
at most five restarts). A restart means starting a new round via ordinary game
UI; reloads also consume a session. Pause the clock only for a documented
evaluator/transport outage, never for difficult gameplay. If the budget is
insufficient, record the unobserved criteria as `not_tested`, score zero.
An observed defect is `failed`, also zero; do not merge these reasons.
Do not replace the artifact with a regenerated version.

Capture ordered actions and before/action/after evidence. Timed motion,
deceleration, collision sequences and finish-time stability need a short
task-scoped clip or sufficiently frequent timestamped frames plus an action
trace; one still image cannot establish dynamics or FPS. Record when a criterion
was not observable. Use a credential-free isolated browser for maintainer replay
when the URL allows it; a shared URL is not byte-frozen content.

Evaluation should not receive creation chat, model labels or billing. If the
same agent/operator creates and tests, record `creation_context_hidden: false`
and the affiliation. Separate files or tabs are not independent/blind review.

## Scoring and costs

Core = 60, observable experience/visuals = 10, delivery time = 30. All criterion
ratings use 0–10; core ratings are binary 0/10. The four experience criteria allow
partial credit with 0/5/10 anchors below; intermediate values (at most one decimal)
need an explicit observation-based reason. Anchor judgement and precision are
maintainer-review gates, not automated semantic checks. Do not drop or
renormalize missing criteria. This pilot scale is not the historical website's
40/20/20/20 scale. Equal weights do not make different game difficulties comparable.

The numeric total is `sum(weight × score / 10)`. Time rating is
`round(10 × clamp((3600 − elapsed_seconds) / 3300, 0, 1), 6)`: at most 5 minutes
earns 10, 32.5 minutes earns 5, 60 minutes earns 0. Use accepted prompt to first
observed final delivery, never an intermediate preview or an optimistic midpoint.
The gameplay gates listed below must all pass for any time credit.
Setup, evaluator time and packaging time are separate.

Build failure earns zero. A generation timeout also earns zero: the prompt was
accepted but no final game arrived within 60 minutes under functioning capture.
Record the accepted receipt, elapsed budget and terminal observation. With no
final artifact, criteria are `not_tested` (zero), not fabricated gameplay defects.
A capture/evaluator outage is `infrastructure_error`, never a generation timeout.
Authentication and infrastructure errors have null totals; retain their counts
and exclude them explicitly from valid-measurement denominators. Do not silently
drop any attempt, including timeout, when selecting a comparison.

Record costs but do not score them: user-facing task charges/credits, documented
public-price valuations and any user-visible model usage are separate bases.
Use unknown, not zero, when unavailable; no private backend-cost supplement in
this external-contributor pilot. Public currency conversions need rate, date
and source. Keep creator, operator and evaluator accounting separate.

## Racing defaults and checks

Clarification defaults: one short closed loop, one car, low-poly original assets,
third-person follow camera, arrow keys or WASD, three ordered visible checkpoints,
standing start, one timed lap, no opponents, local single-player state and the
platform's default stack. Use beginner-friendly handling, not simulation-grade
physics or a test/debug mode. Do not volunteer defaults unless asked. Do not
waive ordered checkpoints or boundary protection during clarification.

Time-credit gates: `ready`, `acceleration`, `steering`,
`ordered-checkpoints`, `lap-finish`. Use the session budget for control/boundary
checks, an invalid-order/early-finish attempt, then a legitimate lap and reset.
A completed-looking result screen alone never proves a legitimate lap.

| Criterion | Weight | Required observation for 10/10 |
| --- | ---: | --- |
| ready | 4 | Start a controllable vehicle on a visibly three-dimensional track with depth/perspective and legible timer/progress. A prerecorded scene or flat top-down board is insufficient. This is visible presentation, not an engine/source-code attestation. |
| acceleration | 6 | From rest on a straight, forward input causes increasing world displacement during comparable time intervals. Use fixed landmarks and a clip/sequence; a speedometer alone is insufficient. |
| braking | 6 | In two comparable straight segments, build similar visible speed then compare a brake input interval with a no-brake/coast interval. Show visibly stronger slowing under braking without hitting a barrier or turning. Disclose imperfect matching; a changing HUD alone is insufficient. |
| steering | 8 | While moving, left and right inputs visibly change heading/path and allow turns along the track. A steering-wheel animation without world-path change fails. |
| follow-camera | 6 | On a straight and through a turn, the third-person camera follows the car while keeping car and upcoming track visible. Stationary camera, car leaving frame or orbit unrelated to motion does not pass. |
| track-bounds | 8 | Deliberately contact inner and outer boundaries at moderate speed through normal input. The vehicle is blocked, constrained or visibly returned without preserving shortcut checkpoint/lap gains. Crossing through the infield to skip the route fails; a cosmetic wall is insufficient. |
| ordered-checkpoints | 8 | Observe at least three visible ordered checkpoints and progress. Before a legal lap, attempt an early/wrong-direction finish crossing and an out-of-order/reverse checkpoint crossing: neither may advance invalid progress or finish. Then traverse checkpoints in the correct order and capture each progression. If geometry prevents a probe, record it as not demonstrated, not an inferred pass. |
| lap-finish | 8 | Starting with zero progress, capture one continuous legal traversal through all ordered checkpoints and a correct-direction finish crossing. Final lap time is positive and displayed, result state appears, and the displayed final time remains unchanged for at least 3 seconds. Separate captures may not silently splice sessions or omit checkpoints. |
| restart | 6 | After a valid finish, use visible restart. Show start position, reset checkpoint progress, initial timer state (zero at reset/start), cleared result and responsive controls; timer advances in the new round. Residual checkpoints or prior lap time fails. |
| readability | 2.5 | Car, upcoming track, boundaries, checkpoint order/progress and timer/result are readable during movement and finish. 5: some states are readable or a non-blocking ambiguity remains. 0: essential route/state unreadable or no supporting evidence. |
| guidance | 2.5 | Visible accelerate/brake/steer instructions match observed keys; route direction/checkpoint order and restart are discoverable. 5: only part is tested/clear. 0: essential instructions absent or misleading. |
| feedback | 2.5 | Checkpoint acceptance, boundary contact and valid finish have distinguishable visible feedback, without confusing them with invalid attempts. 5: only some events are supported. 0: no meaningful observed feedback. Do not infer sound or FPS from stills. |
| presentation | 2.5 | Coherent low-poly 3D presentation across driving and finish; essential UI fits 1280×800 and 390×844 without obstruction. 5: style or one viewport/state supported, not all. 0: unsupported style/layout or essential UI blocked. No mobile-playability claim. |
| delivery-time | 30 | Recomputed from creation timestamps, with all five time-credit gates passed; use the formula above. |

Do not reward screenshot polish as proof of physical behavior. Speedometer-only
acceleration, timer-only races, arbitrary finish triggers, skipped checkpoints,
invisible shortcuts and partially reset state are explicit false-pass traps.

## Evidence package and review

Use `public-submission/0.2`, with separate `creation.jsonl` and `evaluation.jsonl`.
Preserve the exact prompt, all attempts/interventions, accepted/final times,
model label/source, final game URL/build/access, criterion observation IDs and
their reviewed screenshot/clip references. Include cost basis, affiliation,
redactions, capture gaps, sampling interval and evaluation/blinding limitations.
Unknown internal tool/model trajectories stay unknown; visible progress is not
a complete backend trace. The artifact ID must be constant throughout evaluation.

Only reviewed, licensed, task-scoped data may enter a public PR. Raw captures,
credentials, personal profile paths, account pages and unrelated chats stay local.
No public-game publishing or evidence upload is authorized by a successful run.
Follow [submission instructions](../../docs/submissions.md) and the existing
size/hash/public-URL rules; no executable game code in evidence packages.

[v1 review cases](../racing-3d-browser-pilot-v1/review-cases.json) and the
[acceptance card](../racing-3d-browser-pilot-v1/acceptance.md) remain behavioral
references. The cases are **authored hypothetical review examples**, not played
games, observations or accepted submissions. They help reviewers agree on passes,
failures and false-pass traps. Free tests check method identity, score arithmetic
and invalid-package rejection, not gameplay judgement. Before acceptance a
maintainer must review the cases and the browser-only feasibility of every core
check. A later real pilot must expose missed/ambiguous checks; revise the method
under a new version before rerunning, never tune the original score afterward.

## v2 measurement contract

Prompt, criteria, weights and time-credit gates are unchanged from v1. Timeout
semantics and required evaluator metadata change, so v1 evidence is not relabeled
or pooled with v2. This remains a proposed method, not permission for a live run.

All nine core criteria must pass for `core_success`; passing only the time-credit
gates is insufficient. Report this binary outcome beside, not instead of, the
weighted score. A build failure or generation timeout counts as unsuccessful for
both delivery and core success. Evaluator errors are invalid measurements, never
game failures.

Record `result.configuration`: evaluator harness version, effort, public evaluator
instructions file/hash, tool names/versions, access mode, browser/version, scored
viewport and clock. The evaluator model is in `result.model`. Unknown versions
remain null, not guessed. Do not publish private provider/system prompts; the
instructions file is the task-specific public evaluation instruction you control.
Human review may have no instruction file or agent tooling; state that route.

Allowed access modes are `screenshot_only` and `visible_ui`; record the actual
route. Source, hidden state and state injection are not permitted. The clock is
real time; the scored viewport is 1280x800. Capture mobile layout separately.
Evaluation budget remains 1800 seconds / six sessions. Those limits are reviewed
from the action trail; metadata validation is not automatic budget enforcement.

Use the [measurement guide](../../docs/measurement.md) to summarize an explicit
set with its expected attempt count. Configuration gaps, invalid measurements,
non-blind review and synthetic data must remain visible. Summary arithmetic does
not certify evidence or calibrate the judge.
