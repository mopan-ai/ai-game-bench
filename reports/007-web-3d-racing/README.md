# Web 3D racing — development pilot evidence

Contributor: **haot3x / Mopan**. Four creations on November 2–3, 2026;
three selected for the owner-published **Report 007**. This is a contributor
submission awaiting maintainer review, not a calibrated leaderboard result.
The contributor's Mopan affiliation and non-blind remote evaluation are disclosed.

| Creation | Evidence | Report score / 100 | Frozen v2 arithmetic | Core checks | Creation time |
| --- | --- | ---: | ---: | --- | --- |
| Mopan Default, latest generation | [Submission](../../submissions/mopan-racing-20261103/r001/) | 96.2 | 96.2 | 9 / 9 | 12m 03s |
| Wanaka 1.0 Lite | [Submission](../../submissions/wanaka-racing-20261103/r001/) | 89.0 | 89.0 | 9 / 9 | 20m 36s |
| Codex / gpt-6.1-sol / high | [Supplement](supplementary/codex/) | 83.1 | 55.5 | 7 / 9 | 9m 19s |
| Mopan Default, first generation | [Earlier attempt and recheck](supplementary/mopan-first/) | Not selected | 29.0 | 4 / 9 | 15m 01s |

These are reported observations, not independently reproduced outcomes.
The earlier Mopan attempt had input/focus limitations; the later run is a fresh
generation, not a repair. Selecting the later attempt does not demonstrate a
model improvement or an equal-attempt platform ranking.

## Follow a claim

1. Open [results.json](results.json) for all four creations, criterion ratings,
   observations, timings and both scoring versions.
2. Follow `evidence_path` to that creation. `creation.jsonl` and
   `evaluation.jsonl` preserve recorded actions and their timestamps. Remote
   `*-observations.jsonl` files contain the corresponding visible text and
   recorded details; match `event_id` to a trajectory event.
3. `frames/` contains selected **unchanged** screenshots. `*-image-index.json`
   records original hashes and explicitly identifies omitted frames. Missing
   screenshots were not recreated. Native Codex gameplay uses recorded relative
   seconds, not invented wall-clock timestamps.
4. [costs.json](costs.json), [publication.json](publication.json) and
   [source-receipts.json](source-receipts.json) retain cost bases, publication
   limits and hashes of local source records. Source hashes are provenance
   anchors, not proof that inaccessible raw records are authentic.

Mopan and Wanaka use the existing `public-submission/0.2` contract. Validate them:

```bash
uv run agb submission validate submissions/mopan-racing-20261103/r001
uv run agb submission validate submissions/wanaka-racing-20261103/r001
uv run pytest -q tests/test_racing_pilot_public_export.py
```

The ordinary PR checks and Trusted evidence review check structure against
trusted code. They do not watch the games, certify truth, accept protocol
deviations or merge the PR. Maintainers still review evidence and record scope.

## Scoring and comparability

The frozen [racing v2 policy](../../policies/racing-3d-browser-pilot-v2.json)
uses **60 mechanics / 10 experience / 30 time**, with a gameplay gate for time.
[observed-duration-v1.json](observed-duration-v1.json) is a **retrospective,
owner-requested report calculation**, applied to all three selected runs: time
is calculated from recorded duration without that gate. Codex consequently
changes from 55.5 to 83.143281. No gameplay rating or frozen policy was changed.
The addendum's `publication_authorized: false` records its earlier local state;
the owner subsequently authorized this task-scoped export and Report 007.

The remote submission manifests retain frozen-policy totals. The report timing
addendum is not a supported formal `score_addenda` submission and does not become
one by appearing here. Codex's local bundle and the earlier unpublished Mopan
attempt do not meet the policy's `public_url` artifact contract; their records
are supplementary disclosures, not disguised valid submissions.

Codex's two missing mechanics checks (acceleration and braking) receive zero
because the collected evidence did not demonstrate them; this is not proof of
broken physics. Native Codex execution time excludes environment setup, while
remote time starts at observed prompt acceptance. Wanaka's additional 6m 02s
before acceptance is retained in its timing record.

## Replay and cost limits

- [Mopan public game](https://mopan.ai/play/ff754065-db73-4ef8-9749-1c3b4659dc7b):
  anonymous driving/restart smoke checked after grading; full grading used the
  workspace preview. No immutable remote-byte equality proof.
- [Wanaka public player](https://wanaka.games/g/gam_0bEjLvYbpJbNOXn): submitted
  for platform review; the public game remained at 99% loading. Its 89.0 score
  applies to the playable preview, **not** a verified public replay.
- Codex: local artifact file hashes are included; no public playable build or
  large 98 MiB video is uploaded. A separate screenshot-only evaluator was used.
- Costs: Mopan **$0.5839155** and Wanaka **approximately $0.228** are regular
  monthly-plan credit allocations, not cash bills. Codex **$0.514194** is an API
  token-equivalent estimate; its monthly subscription allocation is unknown.
  Costs have zero weight in this racing score. These different bases are not a
  like-for-like cost ranking.

## Disclosure

The owner authorized publication of this round's task-scoped records. Public
text excludes account identifiers, local profile paths, undisclosed Mopan model
identity, system/developer prompts, hidden reasoning and credentials. No raw job
archive or executable game source is included. Screenshot and video omissions
are indexed; the available records are not a complete backend trajectory.
Creation capture gaps reached 66.195s (latest Mopan) and 284.541s (Wanaka).
Page/game viewport differences, transport incidents and prior attempts remain
documented. Unknown evaluator versions remain unknown.

Contributor-authored records: CC BY 4.0. Screenshots are shared as evaluation
evidence; underlying platform artwork and trademarks retain their owners'
rights. The export grants no separate asset or training-data rights.

The [landing report](https://www.aigamebench.com/reports/007-web-3d-racing/report.html)
is an owner-curated display of these records. Website publication and benchmark
maintainer acceptance are separate decisions.
