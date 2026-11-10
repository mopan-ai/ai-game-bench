# Scoring policies

For a separate cross-game retrospective, see
[three-game final-artifact review 1.2](three-game-review-v1.md). It keeps historical
results intact and does not replace the submission validator or create an
accepted leaderboard. Its offline arithmetic helper accepts explicitly reviewed
ratings; it does not play games or authenticate evidence.

Use [tetris-absolute-v1.json](tetris-absolute-v1.json), policy
`tetris-absolute/1.0.0`, for historical-scale comparisons. These are the existing
owner-approved numeric rules, exported unchanged, not weights fitted to Gemini 4.
Different creation dates, clarifications, models and evaluation provenance still
limit comparisons. A common score is not a controlled A/B test.

For a new formal comparison, maintainers approve and freeze **both** creation
policy and scoring policy (including hashes) before generation. Submitters do not
choose weights or alter an approved version. Changed rules need a new version.
The browser pilot retains its original 60/10/30 score.

## Fixed dimensions

Every rating is 0–10; contributions sum to 100. Experience anchors and per-item
guides are in the JSON. No cohort-relative normalization.

| Dimension | Contribution | Evidence required |
| --- | ---: | --- |
| Mechanics | 40 | Nine checks below; demonstrated pass = 10, observed fail or not demonstrated = 0, with distinct reasons |
| Experience | 20 | Controls 4, information 4, board 4, consistency 4, feedback 2, flow 2; integer 0–10 with per-item observations |
| Delivery time | 20 | `20 × max(0, 1 − seconds/3600)`; accepted prompt to first observed final accessible artifact, not model compute time; no 5-minute grace |
| User cost | 20 | Actual charge, credit valuation or documented subscription allocation; never provider/model estimates |

Mechanics: **opens (4)** playable board; **gravity_next (5)** idle descent and new
piece after locking; **move_bounds (5)** left/right and both boundaries;
**rotate (4)** visible asymmetric-piece rotation; **stack (5)** floor and stack
locking; **line_clear (7)** completed row removal/collapse;
**line_clear_score (4)** same-clear score increase isolated from drop points;
**top_out (3)** explicit loss and normal placement stops;
**restart_reset (3)** after nonzero score, clear board/current score and working input.
A single-line clear can establish historical line scoring. Multi-line evidence
is welcome but was not a new retroactive pass requirement.

Cost uses linear interpolation between CNY→percent points:
`0→100, 5→90, 20→70, 50→40, 100→0`; multiply by 0.2. USD display needs a documented
exchange rate, not a different curve. Subscription fees need a disclosed per-run
allocation, not a claim of zero. The export supports charge/credit rows; document
an allocation explicitly in an actual-charge row's basis and evidence.

Missing experience/time/user cost is unallocated. Mechanics not demonstrated
remain zero with their full weight. Show **P** (earned points), **W** (allocated
weight), provisional total `100×P/W`, evidence coverage and full-score bounds
`[P, P+100−W]`. Do not present partial coverage as complete. Infrastructure errors
are unscored. These are missing-data bounds, not confidence intervals.

## Retrospective addendum, not a rewritten run

For an existing `tetris-browser-pilot-v1` run, append an `rNNN` package with an
allowlisted JSON file named in manifest `score_addenda`. Its schema is
`tetris-absolute-assessment/1` (see `ScoreAddendum` in
`src/ai_game_bench/score_addenda.py`). Pin the scoring JSON SHA-256, attempt,
assessment timestamp and `retrospective_operator_evidence_review` provenance.
Supply all nine mechanics and six experience items, each reason and original
evaluation observation IDs. Unknown user cost has null index/rate, not zero.
Run `agb submission schema score-addendum` for the complete machine-readable shape.

Keep original manifest results and trajectory bytes. New judgements do not invent
observations or backdate evidence. Later reviewer replay belongs in a separate
dated review, not in the original evaluation budget. `agb submission validate
<package>` recomputes the addendum: original-event timing, cost basis, coverage and
total. It neither plays the game nor certifies ratings. Review claimed passes.
Embed the original public manifest in the allowlist and pin its revision/hash in
the addendum. Original identity, results and evidence must match (only README and
recording-notes summaries may change). `validate-all` additionally binds that hash
to the actual earlier package, preventing a fabricated replacement source record.

This additive format handles this Tetris pilot only. It does not turn a pilot into
a preregistered formal benchmark, create a runner or change frozen prompt/rubric
bytes. Future game types need their own approved method.
