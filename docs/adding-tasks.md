# Contribute a task

A task needs a testable contract, not only an attractive prompt. Open a scoped PR
or an Ideas proposal describing the game type, capability and how it is checked.
For v0, favor small deterministic mechanics and authored, redistributable assets.
Use the [methodology](methodology.md) and [common terms](terminology.md) when
describing the capability, experimental unit and limits.

## Task validity review

Before freezing a method, map each requirement to an acceptance step and an
observable pass/fail example. Check that a different valid implementation can
pass, and that a plausible incomplete implementation fails. Review ambiguous or
contradictory requirements before treating disagreements as creator failures.
Reference examples demonstrate behavior; they do not prescribe one code path.
Keep implementation tests separate from creator capability scores.

## Executable task package

Use the counter as a packaging example, not a universal gameplay rubric:

```text
datasets/<dataset-version>/<task-id>/
  instruction.md
  task.toml
  environment/Dockerfile
  solution/solve.sh
  solution/files/...
  tests/Dockerfile
  tests/test.sh
  tests/rubric.json
  tests/verify_submission.py
```

Submit these files plus tests, asset licensing/provenance and a short explanation
of limitations. Keep secret checks and gold answers out of creator instructions.
The legacy `MOPAN_PROMPT_START/END` markers in the counter identify its original
product prompt; they are preserved for identity, not permission to call Mopan.

Acceptance:

1. Harbor can parse the task; environments build on the supported platform.
2. Oracle passes; Nop fails without an infrastructure exception.
3. Deliberately broken fixtures fail for the right reason. Include a false-pass
   trap, not only the happy path.
4. Evidence explains every verdict. Browser/setup errors remain exceptions.
5. Replaying a frozen local artifact gives the same deterministic result.
6. No unlicensed assets, credentials or external paid calls in default checks.

Run `./verify.sh`, browser checks and native Harbor trials locally. For a new
task, use `agb run --task <dataset-version>/<task-id> --agent oracle` and Nop.
CI currently builds/tests the counter; it **does not automatically exercise every
new task**. A task PR must add its free calibration to CI or explain the reviewed
manual gate. Never claim file validation alone verified a game.

Released task files are immutable. For prompt, rubric or verifier changes, add a
new task/dataset version and describe the compatibility break. Regression tests
and new defect fixtures are welcome; do not relabel historical results.

## If the task or policy you need does not exist

1. Define the prompt/input, artifact contract and capability being measured.
2. Define **policy**: attempts, time cap, allowed clarifications/repairs, environment
   and capture requirements. Define **eval**: criteria, evidence, score mapping,
   not-tested and infrastructure-error treatment. Keep criteria platform-neutral.
3. Add the Harbor package above, a versioned file in [policies/](../policies/README.md),
   reference and broken examples, and the corresponding free tests.
4. Submit a method PR with calibration results and limitations. A pilot may inform
   the design, but is not a formal result under rules invented afterward.
5. After method approval/merge, freeze the version and [submit results](submissions.md).

A browser/URL-only task can propose documented human verification, but must define
concrete actions and evidence for every criterion and disclose its manual status.
It must not pretend the offline counter verifier supports remote games. A new
game type need not add an unattended creator adapter in the same PR.

For this manual track use a data-only package under `protocols/<version>/` with
`task.toml`, `instruction.md`, `rubric.json` and `evaluation.md`, and set the
policy's `task.kind` to `browser_protocol`. These packages are deliberately not
listed by `agb tasks` or executable by `agb run`. Test identity/arithmetic and
document the manual gameplay-review gate; do not fake an Oracle gameplay pass.
