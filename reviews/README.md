# Evidence reviews

Gameplay evaluation scores an artifact. **Evidence review** examines whether a
submission supports its claims, and records what was and was not verified.

The maintainer decision belongs in the submission's PR, pinned to the reviewed
head and manifest hashes. This directory holds additional reviewer-generated
material, such as a replay trajectory and screenshots. A comment-only review
does not need an empty directory or a copy of the contributor's evidence.

## Available review evidence

[Mopan Gemini 4 / Tetris, 2026-10-14](mopan-gemini4-tetris-20261014/20261014/README.md)
contains an affiliated evidence review and limited artifact replay. It records
the operations, supported checks and omissions; it is not independent generation
reproduction.

For all accepted submissions, including PR-only review decisions, use the
[results index](../reports/README.md#accepted-evidence).

## Record a review

Follow the [maintainer checklist](../docs/reviewing-submissions.md). State
structural validation, evidence inspection, artifact replay and generation rerun
separately. Mark unperformed checks explicitly; disclose reviewer affiliation and
AI assistance. Later replay evidence stays separate from the creator's original
evaluation budget and must not overwrite the submitted trajectory.

[Public submissions](../submissions/README.md) · [Actions and triggers](../docs/contribution-workflow.md)
