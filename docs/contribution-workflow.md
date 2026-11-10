# Actions and contribution workflow

This page describes automation and handoffs. For what to submit, use
[Contributing](../CONTRIBUTING.md); for the evidence checklist and decision format,
use [Review a submission](reviewing-submissions.md).

## GitHub Actions

| Trigger | Workflow | Effect |
| --- | --- | --- |
| PR opened/updated, push main | Public checks | Ruff/pytest, submission/policy validation, package build, free browser and Oracle/Nop calibration |
| Maintainer manual dispatch | Public checks | Repeat the same free checks |
| PR Public checks completes; submission files changed | Trusted evidence review | Validate current PR-head data with main's code/policies; post a structural-only receipt |
| Maintainer manual dispatch with a PR number | Trusted evidence review | Repeat for the current head, including existing PRs after rollout |
| Issue / Discussion | None | Conversation only; no model, upload, merge or deployment |

Open [Public checks](https://github.com/mopan-ai/ai-game-bench/actions/workflows/checks.yml)
or [Trusted evidence review](https://github.com/mopan-ai/ai-game-bench/actions/workflows/review-submission.yml)
to inspect actual runs. If an external PR is waiting for workflow approval, a
maintainer must inspect its workflow/code changes and approve the run first.
The contributor does not need to supply repository secrets or model keys.

The trusted review workflow uses a reviewed main revision, not PR code. It reads
incoming submissions as data, never installs their dependencies or executes their
scripts. External media is not downloaded. Old-head, closed and non-result PRs
are skipped. A policy/checker change on main does not automatically revisit all
open results; dispatch those explicitly when needed.
A new policy must be merged before formal submissions can pass this independent
structural check. The initial bootstrap PR cannot be checked by a main-branch
validator that does not exist yet; use the reviewed local revision first.

Checks run on GitHub-hosted runners with read-only permissions. Only the isolated
receipt job has `pull-requests: write`, to post a comment; it checks out main only,
reads no evidence/artifacts, and cannot write repository contents. Outside
contributors' Public checks require maintainer approval. PR CI itself is not a
tamper-proof judge: inspect changes to checks/workflows before approving.
No auto-merge, paid runs, raw-job upload or landing deployment.
Maintainer-funded reruns require separate approval of the task, revision,
platform, attempts, time and spending.

## Result PR: who does what?

1. **Contributor:** prepare/validate the public package, check privacy/rights and
   submit the PR. Fix structural errors without hiding failed game attempts.
2. **Maintainer:** approve external CI when safe. Trusted evidence review then
   follows automatically for result PRs; inspect its exact-head receipt (manual
   dispatch remains available). Both required Public checks must also pass.
3. **Maintainer:** follow the [evidence review checklist](reviewing-submissions.md)
   and comment on the exact head. Changed evidence needs a new review.
4. **Maintainer:** merge the accepted revision and update the
   [results index](../reports/README.md). Website publication, if selected, is a
   separate curated change in the landing repository.

Structural validation, evidence review, artifact replay and generation rerun
are separate claims. The review checklist defines how to record them.
[GitHub configuration](github-setup.md) documents settings to check; a local
workflow file is not proof that branch protection is currently enforced.
