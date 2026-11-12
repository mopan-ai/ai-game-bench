# Submit a retrospective artifact review

Use this **proposed export format** when reviewing an already delivered Tetris,
3D racing or 2D platformer artifact with the existing
[50/20/30 scoring edition](../scoring/three-game-review-v1.md). It preserves the
ratings and their evidence without pretending the source run followed a different
creation policy. Maintainers must review/merge this support before its result PRs.

`artifact-review-package/1` is a task-scoped evidence envelope, not a runner,
creation protocol, calibrated judge or acceptance decision. Existing
`public-submission/0.1` and `0.2`, their scores and frozen contracts stay unchanged.
This first edition covers **delivered artifacts only**. Failed/incomplete trials
remain in their original records; do not drop them to claim a complete series.

## Prepare one package per task

Keep the draft outside tracked directories until its exact files are approved.
The schemas are available to humans and agents through the same CLI:

```bash
uv run agb submission schema review-manifest
uv run agb submission schema review-assessment
uv run agb submission schema review-event
uv run agb submission check-draft /path/to/review-draft
```

The manifest pins the scoring bytes, prompt reference, actual prompt bytes,
source-manifest hash, series/round identity and final artifact. Capture streams
contain actual recorded timestamps, actions and observations; do not fabricate
missing lifecycle events to fit an export. Normalize field representation in a
dated derivative and retain a local original-to-export mapping. The prompt
reference identifies content only, **not compliance with that policy's scoring
or generation conditions**. A declared omission of trailing line endings is
supported; other prompt changes require a new method.

The assessment contains 0–10 ratings, reasons and evaluation capture IDs. Known
ratings require captures with allowlisted supporting files. Missing evidence
stays null; the calculator retains its full weight in the score bounds, without
renormalizing. A result with missing evidence has no complete eligible score.

Timing retains the actual send time, the surrounding before/after observations,
and the first final observation. The validator checks the interval against those
anchors and recalculates the unchanged 1.2 score. It cannot decide whether a
screenshot really depicts a final artifact. Disclose preview/final ambiguity,
capture cadence, interruptions and later confirmation separately.

List costs with their evidence and basis: credit valuation, model estimate or
cash payment. They are separate from the 50/20/30 score. Never invent missing
token usage or claim a subscription allocation was the account's actual bill.

A hosted build may be unpublished or require login. Record that explicitly and
leave its public URL null when unavailable; never reuse another build's link.
Evidence-only acceptance is possible with stated replay limits. The validator
does not publish a game, download an artifact or verify anonymous access.

## Approval, PR and review

`check-draft` reports `draft_valid`, with `structure_valid: false` and
`publication_ready: false`. It does not set consent flags or produce an accepted
submission. It is not a privacy review; inspect all text and pixels.

After owner approval of the exact files, rights and limitations, set the four
publication confirmations and follow the normal [submission guide](submissions.md):

```bash
uv run agb submission prepare /path/to/review-draft \
  --output submissions/my-review/r001 --confirm-public
uv run agb submission validate submissions/my-review/r001
uv run agb submission validate-all
```

The existing file limits, allowlist, secret checks, immutability rules, fork PR
flow and **Trusted evidence review** apply. No separate upload service or new
workflow is introduced. Only trusted main's version can validate a new format.

A maintainer separately records evidence inspection, artifact replay and
generation rerun as performed with scope or not performed. Same-person review
must disclose affiliation/self-review. A passing Action is structural validation,
not approval, authenticated capture or independent reproduction. Website curation
then references the accepted packages and exact review revision.

## Continue a system-upgrade series

Before each new run, pin a comparator, prompts, scoring/evaluator versions,
attempt count, generation/evaluation limits, viewport, settings and cost basis.
Record the model and Agent change; distinguish owner-supplied labels from visible
provider records. Use fresh contexts and separate workspaces; retain all attempts.

Add a new round ID and package per task; corrections use `r002`, not rewritten
`r001`. Compare per-task results, then average all prespecified trials within each
task and equally across all three tasks. Missing/invalid tasks block a complete
series result. Do not use the `summarize` v0.2 creation-policy command to combine
these retrospective scores. Keep the selected-set calculation and public source
references separate; one trial per task does not establish statistical significance.

For a formal prospective experiment, obtain approval of the creation and
evaluation protocol **before** generation. This export format alone does not
establish that approval or retroactively preregister earlier runs.
