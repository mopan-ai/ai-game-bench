# Results index

Follow a result from its task and submitted evidence to the maintainer's decision
and website report. Acceptance applies to the exact reviewed revision and its
stated scope; it does not certify every claim or independently reproduce creation.

## Accepted evidence

| Task / system | Public evidence | Maintainer decision | Report |
| --- | --- | --- | --- |
| [Tetris v1](../protocols/tetris-browser-pilot-v1/evaluation.md) · Mopan Gemini 4 | [Creation r001](../submissions/mopan-gemini4-tetris-20261014/r001/), [cost r002](../submissions/mopan-gemini4-tetris-20261014/r002/), [scoring r003](../submissions/mopan-gemini4-tetris-20261014/r003/) | [PR #4: accepted with limitations](https://github.com/mopan-ai/ai-game-bench/pull/4#issuecomment-6162702189); [limited replay](../reviews/mopan-gemini4-tetris-20261014/20261014/) | [Mopan comparison](https://aigamebench.com/reports/004-mopan-astra-gemini-tetris/report.html) |
| [Tetris v1](../protocols/tetris-browser-pilot-v1/evaluation.md) · Mopan DS V4.1 1017 | [Submission r001](../submissions/mopan-ds-v41-flash-1017-tetris-20261020/r001/) | [PR #10: accepted with limitations](https://github.com/mopan-ai/ai-game-bench/pull/10#pullrequestreview-5661885193) | [Mopan comparison](https://aigamebench.com/reports/004-mopan-astra-gemini-tetris/report.html) |
| [Racing v2](../protocols/racing-3d-browser-pilot-v2/evaluation.md) · Codex / Mopan / Wanaka | [Report 007 export](007-web-3d-racing/), [Mopan r001](../submissions/mopan-racing-20261103/r001/), [Wanaka r001](../submissions/wanaka-racing-20261103/r001/) | [PR #18: accepted as development-pilot evidence](https://github.com/mopan-ai/ai-game-bench/pull/18#pullrequestreview-5783069282), merged 2026-11-05 | [Report 007](https://aigamebench.com/reports/007-web-3d-racing/report.html) |

These are affiliated reviews with disclosed limitations. Gemini 4's three
revisions describe **one creation**. The racing export preserves four creations,
including the earlier Mopan attempt; three were selected for its report. Codex
and that earlier attempt are supplementary records outside the formal public-URL
submission contract.

Report 007 has both frozen-policy and retrospective report calculations. Its
maintainer review did not replay games or rerun generation. Wanaka's evaluated
preview was playable, but its public player was not verified playable in the
submitted observations. Read the linked review before interpreting the comparison.

Historical packages, including Report 007's pending-review fields, retain their
submission-time bytes. **The linked PR decision records subsequent acceptance.**
The two racing packages also retain source-relative links in their copied
instruction snapshots; use the task links above to browse those references.
This index does not rewrite scores, change protocol readiness or grant a verified badge.

## Historical report references

The website owns HTML, charts and playable demos. Each reference below has its
own directory and `reference.json`; a website comparison alone is not an accepted
submission or a result reproduced by this checkout.

| Reference | Scope | Website |
| --- | --- | --- |
| [001](001-tetris-five-platform/reference.json) | Five-platform Tetris comparison | [Report](https://aigamebench.com/reports/001-tetris-five-platform/report.html) |
| [002](002-codex-gpt-6-sol-astra-tetris/reference.json) | Codex model comparison | [Report](https://aigamebench.com/reports/002-codex-gpt-6-sol-astra-tetris/report.html) |
| [003](003-manus-six-platform-tetris/reference.json) | Six-platform Tetris comparison | [Report](https://aigamebench.com/reports/003-manus-six-platform-tetris/report.html) |
| [004](004-mopan-astra-gemini-tetris/reference.json) | Mopan model comparison | [Report](https://aigamebench.com/reports/004-mopan-astra-gemini-tetris/report.html) |
| [007](007-web-3d-racing/reference.json) | Web 3D racing; public evidence linked above | [Report](https://aigamebench.com/reports/007-web-3d-racing/report.html) |

Website pages may evolve or require access. These links do not guarantee anonymous
play or equivalence between a hosted build and the originally evaluated preview.

## Contribute or review

- [Submit a result](../docs/submissions.md) — one task-scoped export and one PR.
- [Review a submission](../docs/reviewing-submissions.md) — record the exact revision and verification scope.
- [Review evidence](../reviews/README.md) — additional reviewer recordings, when collected.

After acceptance, add the package, decision and any report link to this index.
Keep contributor evidence in `submissions/`; use `reviews/` only for new review
material. Preserve existing report exports and reference them instead of copying
trajectories or maintaining another set of scores. Website publication remains
a separate curated change; the submission CLI does not generate or deploy HTML.
