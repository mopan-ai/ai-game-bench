# Methodology diagrams

Original, editable SVG illustrations for the public documentation. No external
fonts, scripts, remote images or third-party artwork are required. Authored for
this repository under its [Apache-2.0 license](../../LICENSE).

| Figure | Desktop | Narrow display | Text equivalent |
| --- | --- | --- | --- |
| System and contributions | [System map](system-overview.svg) | [Mobile](system-overview-mobile.svg) | [Architecture and contribution points](../../docs/architecture.md) |
| Evaluation design | [Overview](evaluation-overview.svg) | [Mobile](evaluation-overview-mobile.svg) | [Methodology](../../docs/methodology.md) |
| Evaluator validation | [Calibration loop](evaluator-calibration.svg) | [Mobile](evaluator-calibration-mobile.svg) | [Calibration guide](../../docs/judge-calibration.md) |

The overview is a protocol diagram, not a claim of end-to-end automation. In
the calibration figure, the solid loop is development on known cases; the dashed
ochre panel is the **next** validation gate. Color is supplemented by labels and
line styles. These figures contain no measured scores or platform rankings.

The system map is an original game-benchmark composition informed by
[Anthropic's evaluation-component hierarchy](https://www.anthropic.com/research/demystifying-evals-for-ai-agents).
It adds our separate creator/evaluator evidence paths and contribution roles;
the reference artwork is not embedded. C1–C5 are contributor labels, not run
steps. Browser observation and native execution retain separate boundaries.

README uses a `picture` element to select the narrow layout below 600px. Each SVG
also has a title/description, and the embedding image has alternative text. Edit
both layouts together when meaning changes; keep them consistent with the text
and [current state](../../docs/project-state.md).
