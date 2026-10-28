# Measurement v0.2 — proposed

An additive contract for future browser pilots, not a rerun, calibrated judge or
replacement for historical results. The platformer and racing v2 proposals keep
v1 prompt/rubric bytes, 60/10/30 weights and time-credit gates. Their evaluation
procedure and policy have new versions. Maintainers must approve them before a
formal run; no model calls or publication are authorized by these commands.

## Outcomes and denominators

| Outcome | Total | Delivery / all-core success |
| --- | --- | --- |
| Delivered, valid evaluation | Weighted score | Delivery succeeds; all nine core checks must pass for core success |
| Delivered, observed failure or not tested | That criterion earns zero | Not tested and failed remain distinct; no denominator reduction |
| Build failure | Zero | Both unsuccessful |
| Generation reaches its time cap without final delivery | Zero | Both unsuccessful; all criteria `not_tested`, no invented defects |
| Auth/creation infrastructure failure | Null | Invalid measurement; explicitly excluded and counted |
| Delivered, evaluator infrastructure failure | Null | Delivery still succeeds; core measurement invalid and excluded |

Timeout needs accepted-prompt evidence and a terminal observation at/after the
creation budget. A transport/capture outage is not proof of generation timeout.
No interrupted or skipped attempt disappears from the report. A zero score is
not a claim that every unobserved mechanic is broken.

Delivery rate = successful deliveries / valid creation measurements.
Core success rate = deliveries passing **every** core check / valid core
measurements, including generation timeout and build failure. Invalid-measurement
counts accompany both denominators; these are not unconditional success rates
over all planned runs. Report recorded/expected counts too. Mean total includes
scored failures and excludes null measurements with their counts disclosed.

## Evaluator identity and access

`public-submission/0.2` requires `result.configuration`: harness version, effort,
public evaluator instructions file/hash, tool names/versions, actual access mode,
browser/version, scored viewport and clock. Evaluator model and blinding remain
in `result.model` and `creation_context_hidden`. Use explicit nulls for unknowns.
Human evaluation can have no agent instructions/tools. For an agent, include its
task-specific public evaluation instructions in the existing file allowlist;
this does **not** require private provider prompts or hidden reasoning.
For an undelivered attempt this is the intended evaluation configuration, not
evidence that an evaluator ran; `evaluation_completed` remains false.

The v2 game policies allow ordinary visible UI or screenshot-only evaluation,
real-time play and a 1280x800 scored viewport. Instrumented/source-assisted
verification needs a separately reviewed policy and must not share their cohort.
The 1800-second/six-session budget is pinned; actual use, zoom, device scale,
outages and mobile-layout inspection remain trajectory/reviewer checks. The
validator cannot establish that declared access or budget use was truthful.

## Offline summary

```bash
uv run agb submission schema evaluation-configuration
uv run agb submission init .submission-drafts/my-run --id my-run --policy platformer-browser-pilot-v2
# Record and prepare via the existing submission guide; init is not a run.
uv run agb submission summarize submissions/run-a/r001 submissions/run-b/r001 --expected-attempts 2
```

The summary is JSON to stdout; it creates no database, uploads nothing, fetches
no URLs and runs no games. Only v0.2 packages are accepted. The explicit expected
count must match all selected attempts. This checks your declared set, not whether
unsubmitted attempts exist. Select one revision per submission/source run:
corrections and repeated reviews are not independent generation attempts.
Use a stable platform-local run/project ID for `source_ref`. Duplicate detection
uses source kind, platform and that reference; corrected model/effort/version
metadata does not create a new run. It cannot detect aliases for the same source.

Groups separate policy hashes, creators/models, evaluator identity/configuration,
access, environment, blinding and synthetic data. Missing evaluator/browser/tool
versions remain visible and are not pooled into an assumed identical configuration.
These conservative groups are diagnostic summaries, not automatically comparable
rankings. Each contains outcomes, criterion statuses, rates with denominators,
mean total with scored/excluded counts, and manifest hashes. They summarize
submitted claims, **not verified gameplay** or maintainer acceptance.

## Compatibility

All v0.1 policy/task/result bytes and score calculations remain unchanged,
including their null timeout totals. Do not relabel old results v0.2 or fabricate
missing metadata. Historical 40/20/20/20 and pilot 60/10/30 totals stay separate.
Use a fresh authorized run for the new policy; same-build reevaluation belongs
in a separately identified calibration/review report, not a new generation.
