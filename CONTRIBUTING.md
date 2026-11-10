# Contributing

Start with one scoped PR. No invitation or prior Discussion is required.
New to the checkout? [Get started](docs/getting-started.md).

| I want to contribute | Follow |
| --- | --- |
| A game-creation result | [Record, package and submit evidence](docs/submissions.md) |
| A task, rubric or policy | [Define and validate a task](docs/adding-tasks.md) |
| A platform guide or adapter | [Platform integration contract](docs/platforms.md) |
| An evaluator improvement | [Calibration and evidence-supported corrections](docs/judge-calibration.md) |
| A review or artifact replay | [Maintainer review checklist](docs/reviewing-submissions.md) |

Discuss large changes in [Ideas](https://github.com/mopan-ai/ai-game-bench/discussions/categories/ideas);
small scoped PRs are welcome directly. Failed games are useful data too. For a
verifier fix, include a minimal wrong verdict and a regression check; changed
scoring meaning requires a new version.

Use your own authorized accounts. Before pushing, read the
[public-data terms](docs/public-data.md): submit only reviewed,
task-scoped material you have permission to share. Include all attempts, evidence
gaps, affiliation and AI assistance. Keep credentials and raw jobs local.

Run `./verify.sh`; runtime changes also need the free browser and Harbor smoke
checks. State what ran and any limitations. Correct accepted results with a new
revision, never by overwriting their records.

Mopan maintainers review and merge; passing CI is not evidence approval or
automatic website publication. [Actions and triggers](docs/contribution-workflow.md)
explains automated checks; [Governance](GOVERNANCE.md) defines decision authority.

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
