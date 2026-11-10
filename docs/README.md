# Documentation

Choose what you want to do. For a short project overview, start with the
[repository README](../README.md).

## Get started

- [Start here](getting-started.md) — validate a free example or plan a real-platform run.
- [Task catalog](tasks.md) — task versions, execution paths and available evidence.
- [Platform guides](../platforms/README.md) — account/tool setup and tested workflows.
- [Results index](../reports/README.md) — submissions, review decisions and reports.

## Guides

- [Submit a result](submissions.md) — record, prepare, validate and open a PR.
- [Add a task or policy](adding-tasks.md) — instructions, acceptance criteria and examples.
- [Add a platform](platforms.md) — connection contract and adapter development.
- [Calibrate an evaluator](judge-calibration.md) — known cases, verdicts and evidence review.
- [Run locally](running.md) — Docker, Harbor, verification and troubleshooting.

[Contribution entry points](../CONTRIBUTING.md) · [Public-data terms](public-data.md)

## Reference

| Reference | Purpose |
| --- | --- |
| [Methodology](methodology.md) | Experimental design and what a score can establish |
| [Terminology](terminology.md) | Tasks, trials, trajectories, evaluation and review |
| [Architecture](architecture.md) | System map, contribution roles and directory responsibilities |
| [Measurement v0.2](measurement.md) | Evaluator metadata, timeout/error semantics and summaries |
| [Run policies](../policies/README.md) | Frozen task identity, budgets and score mappings |
| [Historical Tetris scoring](../scoring/README.md) | Fixed-scale comparisons and retrospective addenda |
| [Project state](project-state.md) | Current capabilities, limitations and next gates |

For CLI syntax, run `uv run agb --help`. For exact JSON formats, use
`uv run agb submission schema manifest`, `event`, `policy` or `score-addendum`.
The [submission guide](submissions.md) shows how to use these formats.

## Maintainers

- [Review a submission](reviewing-submissions.md) — inspect an exact revision and record scope.
- [Actions and triggers](contribution-workflow.md) — what runs automatically and what needs a decision.
- [GitHub setup](github-setup.md) — permissions, branch protection and configuration audit.
- [Governance](../GOVERNANCE.md) · [Security](../SECURITY.md)

<details>
<summary>Archive and design history</summary>

These pages explain past decisions; current instructions are linked above.

- [Validation history](history/validation-log.md)
- [Platformer/racing method proposal](proposals/platformer-racing-pilot.md)
- [Contribution automation precedents](research/contribution-automation.md)
- [Public evidence design](research/submission-evidence.md)

Literature-review drafts stay in ignored `local-research/`; they are not public documentation.

</details>
