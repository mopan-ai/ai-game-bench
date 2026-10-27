# 2D platformer browser pilot v2 — proposed

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

## Platformer defaults and checks

Clarification defaults: one short original pixel-art side-scrolling level, arrow
keys or A/D to move and Space to jump, ordinary gravity, no enemies required,
coins that are optional for victory, reachable platforms/pit/goal, local
single-player state and the platform's default stack. Choose an ordinary
beginner-completable level, not a debug/test mode. Do not volunteer these defaults
unless the creator asks; requirements already in the prompt cannot be negotiated away.

Time-credit gates: `ready`, `movement`, `jump`, `goal-win`.
Observe the initial coin count/position before collecting. Plan the available
sessions to cover a loss after collecting, a successful traversal after
restarting, and a new playable round after winning.

| Criterion | Weight | Required observation for 10/10 |
| --- | ---: | --- |
| ready | 4 | Start through normal UI; a visible player responds to input in an actual level. A splash screen or auto-playing animation is insufficient. |
| movement | 6 | On stable ground, move the same player left and right relative to a fixed world feature; stop/release and show input focus. Camera scrolling alone is not player motion. |
| jump | 8 | From stable ground, jump visibly upward, descend and land on a reachable raised platform. Repeat a controlled jump; a sprite animation without elevation is not a jump. |
| solid-platforms | 8 | Stand without falling through for at least 2 seconds on ground and again on a raised platform; approach/land normally. Passing through a solid surface or falling through on landing fails. One-way platforms need not block upward travel. |
| collectibles | 6 | Collect at least two distinct coins: each disappears and increments the visible count by one. Revisit one collected position without restarting: no extra count. Idle count must not rise. If fewer than two exist, the full observation is not demonstrated; do not invent a second coin. |
| fall-loss | 8 | Enter a pit intentionally through normal movement; show falling followed by explicit failure and no continued ordinary active round. Capture the sequence, not only a loss label. |
| goal-win | 8 | Traverse from start to the visible goal with normal input; show explicit victory only after arrival. A start-screen win label or success without traversal is not sufficient. Coins are not a mandatory victory condition. |
| loss-restart | 6 | After collecting a coin and losing in a pit, use restart. Show initial position/count, coins restored, failure cleared and working movement/jump. |
| win-restart | 6 | After winning with at least one collected coin, use restart. Show initial position/count, coins restored, win cleared and responsive controls in a fresh round. |
| readability | 2.5 | Player, solid platforms, pits, coins and goal are distinguishable; coin/state text is readable during play and at loss/win. 5: only some required states are observed or a non-blocking ambiguity remains. 0: no supporting observation or essential geometry/state is unreadable. |
| guidance | 2.5 | Visible move/jump instructions match tested keys, and both loss/win restart controls are discoverable. 5: instructions exist but only part is tested or a restart affordance is unclear. 0: essential controls cannot be discovered or instructions are misleading. |
| feedback | 2.5 | Collect, land, lose and win have perceptible, distinct visible feedback; collected counts correspond to the observed event. 5: some events are clear but others weak/untested. 0: no observed meaningful feedback. No sound-quality claim without captured audio. |
| presentation | 2.5 | Coherent pixel-art presentation across gameplay and terminal states; essential UI is unobstructed at 1280×800 and 390×844. 5: style or one viewport/state is supported, but not all. 0: no supported style/layout evidence or essential UI is blocked. This is not a mobile-playability score. |
| delivery-time | 30 | Recomputed from creation timestamps, with all four time-credit gates passed; use the formula above. |

False-pass traps include cosmetic jumping, auto-incrementing coin counters,
duplicate pickups, decorative platforms, premature victory and restart buttons
that clear only an overlay. A good-looking screenshot cannot pass these checks.

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

[v1 review cases](../platformer-browser-pilot-v1/review-cases.json) and the
[acceptance card](../platformer-browser-pilot-v1/acceptance.md) remain behavioral
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
