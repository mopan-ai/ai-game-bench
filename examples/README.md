# Examples

Start here to learn the evidence format without creating a game or spending money.
Examples are teaching data, not benchmark submissions.

## Synthetic counter package

[synthetic-counter/manifest.json](submissions/synthetic-counter/manifest.json)
is a complete invented package with creation/evaluation events and allowlisted
evidence. From the repository root:

```bash
uv run agb submission validate examples/submissions/synthetic-counter
```

Expected: exit 0, structure valid and review status `unverified`. A valid invented
example is not an observed game result. Never submit it as your own trial.
To create an empty draft for real observations, follow [Submit a result](../docs/submissions.md).

## Where to look next

| Looking for | Location |
| --- | --- |
| A real submission and its acceptance decision | [Results index](../reports/README.md) |
| Known working and faulty games for testing evaluators | [Fixtures](../fixtures/README.md) |
| A plan for measuring an evaluator's accuracy | [Calibration](../calibration/README.md) |
| Reviewer-generated replay evidence | [Reviews](../reviews/README.md) |

The files in `examples/` do not replace any of these records.
