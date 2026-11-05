# Get started

There are two entry paths: a free local example, or a recorded trial on a real
creation platform. Both use the same public evidence workflow when submitting.

## Try the free example

Install [uv](https://docs.astral.sh/uv/getting-started/installation/).
Use macOS/Linux, or WSL on Windows; the checkout pins Python 3.12.

```bash
git clone https://github.com/mopan-ai/ai-game-bench.git
cd ai-game-bench
uv sync --locked
uv run agb submission validate examples/submissions/synthetic-counter
```

Expected: a valid synthetic evidence package, exit code 0, with review status
`unverified`. The records are invented to demonstrate the format; no game was
created or graded. No Docker, account, model call or upload is needed.
See [what the example contains](../examples/README.md).

To exercise execution too, start Docker and follow [Run locally](running.md).
Oracle should return 1 and Nop 0 for the counter calibration, with no
infrastructure exceptions. These are interaction checks, not game-quality scores.

## Test a real platform

1. Choose a version from the [task catalog](tasks.md). Read its prompt, policy,
   rubric and evaluation procedure; confirm whether it is a proposed method or
   suitable for the comparison you intend. Freeze the rules before generating.
2. Read the [platform guide](../platforms/README.md). Use your authorized account
   and tools; agree model, attempts, time and spending before a paid run. For a
   browser platform, identify the owner-selected profile and control permission.
3. Follow [Submit a result](submissions.md) from recording through PR creation.
   It specifies the trajectories, screenshots, final artifact, cost provenance
   and publication review. Inspect an entry in the [results index](../reports/README.md)
   for a real submission and the maintainer's decision.

The public `agb run` command currently runs the local counter calibration only.
It does not connect hosted platforms, drive an existing browser profile or
record remote runs for you. Browser tool use and local creator CLIs can still
produce evidence under a compatible, approved policy.

Missing a task or platform? [Contribute a method](adding-tasks.md) or
[connection guide](platforms.md). A development pilot must disclose its limits;
it does not become a formal benchmark result merely by passing validation.

## Choose your next step

- [Contributing](../CONTRIBUTING.md) — task, platform, evaluator, result or review.
- [Methodology](methodology.md) — how the measurements fit together.
- [Project state](project-state.md) — what works today and what remains experimental.
- [Documentation](README.md) — all guides and references.
