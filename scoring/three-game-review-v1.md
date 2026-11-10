# Three-game artifact review v1

**Active revision: [final-artifact review 1.2](three-game-final-artifact-review-v1.2.json)**.
This retrospective edition uses 50 mechanics / 20 experience / 30 time across
Tetris, 3D Racing and 2D Platformer. It reviews existing final artifacts; it is
not a creation policy, calibrated judge or controlled fresh-run comparison.

| Version | Time and delivery rule |
| --- | --- |
| [1.0](three-game-review-v1.json) | Historical draft: delivery-speed credit required the listed core gameplay checks. |
| [1.1](three-game-review-v1.1.json) | Basic playability alone gates speed credit; 60-minute creation cutoff with bounded deadline adjudication. |
| [1.2](three-game-final-artifact-review-v1.2.json) | Same weights and speed curve; explicitly disclosed completed continuations may earn quality points after 60 minutes, with zero time points. |

The revisions were made during retrospective review. Version 1.1 corrects a
delivery-time gate that conflated speed with advanced mechanics. Version 1.2
includes final-artifact quality after the owner-authorized Kimi continuation;
it does not relabel that continuation as an uninterrupted attempt. Historical
capped results, prompts, rubrics and trajectories stay unchanged. Pin the exact
version and bytes; do not mix these totals with historical report totals.

Selection, source hashes, dates, model/settings, interventions and evaluator
differences must accompany assessments. Keep records of failed/invalid attempts
and explain owner-selected retries. This arithmetic utility neither validates
those selection claims nor uploads or accepts submissions.

## Score and selection

Use [the versioned scoring definition](three-game-final-artifact-review-v1.2.json): mechanics 50,
experience 20, delivery time 30. Each criterion is 0–10. Normalize each game's
mechanics weights to 50; do not normalize away missing criteria. Cost is reported
separately with its original basis, never converted into score.

Preselect the source run for every platform/game before replay; retain failed and
invalid attempts. Multiple models/versions must be named, never selected by score.
This edition compares the selected platform artifacts, not one fixed underlying
model across time. Three-task macro average = (Tetris + racing + platformer) / 3.
With repeated generations, first average all preselected trials for each task.
Incomplete/invalid tasks block an eligible total. A verified-points lower bound
may be shown separately; no partial-task average or cohort-relative scaling.

## Observable checks

Platformer and racing retain their existing core behavioral requirements.
Platformer explicitly requires **both loss and win reset**. Tetris uses the
historical nine mechanics: one visibly completed line and its isolated score
increase suffice; extra multi-line, hard-drop or hold features are not required.
Supplementary review can establish a less demanding common criterion from a
documented partial old result, but must cite the actual observation and explain
the mapping. Do not convert a reported pass fraction into a new quality rating.

The five experience criteria each contribute four points:

| Criterion | Review |
| --- | --- |
| Guidance | Discoverable movement/actions and loss/win reset controls; verify the advertised keys. |
| Readability | Distinguishable player/objects/hazards, readable counters and terminal states. |
| Feedback | Visible responses to input, progress, failure/success and reset. Audio is optional unless requested. |
| Presentation | Coherent requested style and unobstructed desktop/mobile layout; no engine preference. |
| Visual stability | Inspect idle and movement sequences for unintended disappearing sprites, flicker or camera jitter. Intentional coin rotation/pulsing alone is not a failure. |

Anchors: 0 = demonstrated unusable/absent; 5 = usable with a clear limitation;
8 = clear and consistent over the required observed states; 10 = unusually
polished with explicit multi-state support. Intermediate integer ratings need
a reason. Missing evidence is null, not an invented 0/10 verdict. Old 0/5/10
ratings cannot automatically receive the same experience rating under these
anchors. Reinspect their supporting material. A screenshot sequence cannot
exclude flicker faster than its sampling rate; unsupported stability remains null.
Capture a short continuous clip when available. Record cadence and limitations
otherwise; don't assert FPS from wall-clock screenshot intervals.

## Supplementary replay

Review existing final artifacts through ordinary visible browser controls only.
Do not read source/hidden state, inject game state, repair or regenerate. Record
actual viewport, version/build where visible, input actions and before/after
evidence. Intended desktop is 1280×800, mobile layout 390×844 at 100% zoom.
No hidden engine preference. Disclose access/blinding/environment differences.

Allow at most 30 minutes and six **traversal attempts** per supplementary review.
The terminal reset needed to verify `win-restart` or `loss-restart` is part of that
test: it may start a new round solely to confirm initial state and responsive
movement/jump. It does not grant another traversal attempt. Finish all checks or
record a precise gap. Document transport/input failures; never silently subtract
lost attempts or blame the game for failed tool input. The new budget does not
retroactively alter the original six-session evaluation.

## Time and invalid measurements

Time rating = 10 × clamp((3600 − observed_seconds) / 3300, 0, 1), with the game's
listed playable-loop gates. A proven game blocker closes the relevant dependent
checks at zero with reason `blocked_by_artifact`, without claiming each downstream
feature was independently tested. Missing gate evidence leaves a lower bound.

In 1.2, a completed final artifact retains observed quality regardless of delivery
duration. Time credit is zero at or beyond 60 minutes. Disclose stopped intervals,
resume messages and both wall/active durations; active spans are not backend
compute time. A missing final artifact is unmeasured, not an invented timeout.
Auth, quota, transport and evaluator infrastructure errors also remain null.

The archived 1.0/1.1 editions retain their creation cutoff. They accept a completed
artifact first seen just after the deadline only when the observation interval
straddles the cutoff by at most 30 seconds and no post-budget intervention occurred.
That boundary case receives zero time credit. A recorded generation timeout
under functioning capture earns zero in the capped editions only.

Use separate assessment and review files with source hashes and evidence refs.
Only complete valid assessments receive an eligible score/rank. Missing evidence
can be resolved by a dated replay, not by claiming it was observed earlier.

## Offline calculation

```bash
uv run python -m ai_game_bench.artifact_review assessment.json \
  --policy scoring/three-game-final-artifact-review-v1.2.json > scores.json
```

This reads the assessment and writes plain JSON to stdout. The assessment pins the policy ID and SHA-256. Include all three games
for each platform, even held or invalid tasks. Each trial names a unique source
run and records `mechanics`, `experience`, `time`, and `outcome`; criteria contain
`rating`, `status`, `reason`, and evidence references. The synthetic fixtures in
[the arithmetic tests](../tests/test_artifact_review.py) illustrate this format.

This is a local review utility, not a public submission schema. It validates
arithmetic and declared references, not file authenticity or observed behavior.
Output bounds represent missing evidence, not statistical confidence intervals.
The measured duration remains visible even when gameplay gates prevent awarding
time points; historical duration-only addenda are preserved separately.

For public result contributions, follow [the submission guide](../docs/submissions.md).
Do not place raw review workspaces or private source records in Git. Publishing
this policy and calculator does not accept any new platform result. Human evidence
review and separately authorized, task-scoped exports are still required.
