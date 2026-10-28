# Contributing

Start with one scoped PR. No invitation or prior Discussion is required.
The [system map](docs/architecture.md#contribution-points) shows where task authors,
platform integrators, evaluator authors, result contributors and reviewers fit.

- **Result:** follow [the submission guide](docs/submissions.md) to record,
  package and submit your evidence. Failed games are useful data too.
- **Task / policy / eval:** follow [adding tasks](docs/adding-tasks.md).
  Discuss large changes in [Ideas](https://github.com/mopan-ai/ai-game-bench/discussions/categories/ideas);
  small scoped PRs are welcome directly.
- **Platform:** follow [the integration contract](docs/platforms.md), with free
  mocked tests before an authorized real run.
- **Verifier fix:** include a minimal wrong verdict and regression test.
  Changing scoring meaning requires a new version.

Use your own authorized accounts. Before pushing, read the
[public-data terms](README.md#public-data-and-privacy-terms): submit only reviewed,
task-scoped material you have permission to share. Include all attempts, evidence
gaps, affiliation and AI assistance. Keep credentials and raw jobs local.

Run `./verify.sh`; runtime changes also need the free browser and Harbor smoke
checks. State what ran and any limitations. Correct accepted results with a new
revision, never by overwriting their records.

Mopan maintainers review and merge; passing CI is not evidence approval or
automatic website publication. Proposals do not trigger paid runs.
Result PRs receive an automatic **structural validation only** receipt after
Public checks. Maintainers separately state whether they reviewed evidence,
replayed the artifact or reran creation; unperformed checks are explicit.
[Review process](docs/contribution-workflow.md) · [Governance](GOVERNANCE.md)

## Agent handoff

Copy this into your agent and specify the task and platform you want to test:

> Read AGENTS.md, then docs/submissions.md and the selected platform guide.
> First identify the frozen task, policy, scoring version and what this checkout
> can actually run. If a task or policy is missing, propose it using
> docs/adding-tasks.md before a formal run; do not invent an official score.
> Confirm the account/browser profile, model and spending limits with me before
> any real-platform run. Record all attempts, prompt receipts, follow-ups,
> timings and final artifact identity in creation.jsonl. Evaluate the final game
> separately and record actions, observations and evidence in evaluation.jsonl.
> Keep unknowns, failures, interventions and capture gaps explicit. Never upload
> credentials, profiles or whole raw jobs. Prepare and validate only a reviewed,
> task-scoped public package. Show me its exact file list, license/affiliation,
> limitations and validation result; wait for my approval before pushing or
> opening a PR. Structural validation is not evidence approval.

This is a checklist for your agent, not an unattended runner or a grant of
account, spending or publication permission.
