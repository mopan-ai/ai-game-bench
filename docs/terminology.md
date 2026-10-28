# Terminology

Use these terms in new documentation and reports. Existing schema keys, task
identities and historical records retain their meaning. This glossary describes
AI Game Bench's conventions; it is not a schema migration or a universal standard.

## Experimental objects

| Term | Meaning here | Repository mapping |
| --- | --- | --- |
| **System under test (SUT)** | The creator configuration: model, agent harness, tools and platform. Comparing platforms does not isolate model quality. | Creator metadata in a public manifest; [platform references](../platforms/README.md) |
| **Task** | A versioned creation request and acceptance contract. | Executable `datasets/` task or data-only `protocols/` package |
| **Evaluation suite** | A declared collection of tasks targeting capabilities. Not the Python test suite. | Currently the counter calibration and separately versioned browser protocols |
| **Protocol / policy** | The allowed interaction, attempts, budgets, evidence requirements and score mapping. | `policies/` pins task, rubric and procedure hashes |
| **Rubric / criterion** | The scoring dimensions / one named acceptance item. | Task `rubric.json` and the policy's criterion IDs |
| **Trial / attempt** | One fresh execution of a task by a declared system. | A Harbor trial, or a browser-observation attempt; these are distinct source kinds |
| **Cohort** | The declared set of trials selected for an analysis. State expected counts and configuration differences. | Offline summary inputs or a local calibration plan |
| **Artifact / outcome** | The delivered build or URL / its observed terminal state and behavior. | Game submission pointer; build reference and evidence in an export |
| **Trajectory** | Time-ordered observable actions and outputs, with gaps disclosed. | `creation.jsonl`, `evaluation.jsonl`; native Harbor records stay local |

## Evaluation roles

| Term | Meaning here | Do not confuse with |
| --- | --- | --- |
| **Creator agent harness** | Enables the model to create a game, such as a CLI scaffold or hosted platform. | Harbor, the evaluation execution infrastructure |
| **Evaluation harness** | Runs and records native evaluation jobs. Harbor owns execution; `agb` resolves and inspects. | An additional `agb` scheduler or database |
| **Gameplay evaluator** | Plays a build under the declared access and test procedure. Can be human or agent-operated. | The creator's self-reported completion |
| **Grader / verifier** | Produces a criterion decision; a code verifier can consume files and emit JSON. | The submission validator, which checks record consistency |
| **Judge calibration** | Measures evaluator decisions against known cases and audits their support. | A creator capability score or proof of broad judge accuracy |
| **Maintainer review** | A decision about the submitted claims, exact revision and stated evidence scope. | Automatic CI success or independent third-party certification |

“Independent evaluation” means separation from creation context and expected
answers **where performed**. Report actual blinding and affiliation separately.
The local screenshot judge is a development experiment; accepted Tetris pilots
disclose affiliated/non-blind review.

## Repeats, replay and publication

- **Artifact replay:** play an existing build again. **Regrading:** reassess it
  under a named evaluator. Neither creates another independent game sample.
- **Generation rerun:** a new creation attempt. It can test reproducibility but
  does not authenticate an earlier submitted trajectory.
- **Revision / addendum:** a preserved correction or supplement to one submission.
  Do not count it as another trial.
- **Evidence package:** a reviewed public export, not a raw job. **Report:** a
  presentation of specified packages and review decisions, not another database.

## Vocabulary across tools

[Anthropic's evaluation terminology](https://www.anthropic.com/research/demystifying-evals-for-ai-agents)
distinguishes tasks, trials, graders and outcomes. We keep those objects separate
and map them to the repository above.

[LangChain's run / trace / thread convention](https://www.langchain.com/resources/agent-evals)
uses *run* for one model/tool invocation, *trace* for a turn and *thread* for a
multi-turn conversation. In this repo, a **Harbor job** groups native trials;
a browser conversation may contain many turns. Do not translate every provider
“run” into a fresh benchmark trial. Prefer the explicit unit over “run” alone.

For grading status, preserve `passed`, `failed`, `not_tested` and `infra_error`
where the contract uses them. A valid evidence package may describe a failed
game; an invalid measurement is not a game failure. [Scoring semantics](measurement.md).
