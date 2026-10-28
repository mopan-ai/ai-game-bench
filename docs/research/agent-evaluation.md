# Research basis: agent evaluation

Reviewed 2026-10-28. These sources are engineering guidance and research analysis,
not a shared formal standard. The framework in [methodology](../methodology.md)
is our application to observable game creation. It does not adopt any source's
framework as a new dependency or change released scores.

| Source | Date shown by source | Relevant lesson | Application here |
| --- | --- | --- | --- |
| Anthropic — [Demystifying evals for AI agents](https://www.anthropic.com/research/demystifying-evals-for-ai-agents) | 2026-01-09 | Distinguish the task, trial, grader and outcome; calibrate judgments and examine variation across attempts. | [Terminology](../terminology.md); working/faulty fixtures and separate evaluator calibration. |
| LangChain — [How we build evals for Deep Agents](https://www.langchain.com/blog/how-we-build-evals-for-deep-agents) | 2026-03-26 | Target specific behaviors, read traces and keep infrastructure tests separate from capability measurements. | Counter/CI checks are not platform scores; game criteria organize diagnostic evidence. |
| LangChain — [Evaluating AI Agents at the Run, Trace, and Thread Level](https://www.langchain.com/resources/agent-evals) | 2026-06-23 | Inspect state changes and multi-turn behavior; do not require one tool sequence when alternatives are valid. | Keep creation and evaluation trajectories; translate provider units explicitly. |
| Confident AI — [LLM Agent Evaluation Metrics in 2026](https://www.confident-ai.com/blog/llm-agent-evaluation-complete-guide) | Updated 2026-10-15 | End-to-end, trajectory and component views answer different diagnostic questions. | Grade the artifact, then investigate visible process evidence; inaccessible internals remain unknown. |
| OpenAI — [Separating signal from noise in coding evaluations](https://openai.com/index/separating-signal-from-noise-coding-evaluations/) | 2026-07-08 | Task defects can create misleading performance signals: excessive constraints, missing requirements, inadequate tests or contradictions. | Audit prompt-to-check alignment; preserve disputed cases and version any correction. |

## Decisions for this repository

1. **Outcome first, diagnosis alongside.** For a hosted game, the final build is
   playable evidence; a platform's “finished” message is only a creation event.
   Trajectories explain failures without dictating a single implementation path.
2. **Measure the evaluator too.** Existing platformer/racing pass/fault cases
   form a development set. Withhold labels, repeat decisions and audit cited
   observations; reserve unfamiliar implementations for a separate validation gate.
3. **Report the unit and boundary.** One artifact can have multiple reviews and
   revisions. A focused probe cannot establish complete gameplay quality, and a
   passing export checker cannot authenticate recorded actions.
4. **Retain comparable history.** Pin methods and configurations before a trial;
   preserve invalid/missing measurements and revisions. Changing presentation or
   terminology must not silently rescore accepted data.

## What we deliberately do not infer

- These references do not justify a universal quality score, new weights or a
  claim that the present game set represents every game genre.
- A trace is not guaranteed complete. Hosted platforms may expose only UI
  observations; hidden model reasoning and private prompts are not required.
- More repeats of known fixtures do not create a held-out evaluation. A report
  must distinguish fixture regression, label agreement and evidence support.
- We do not add LangSmith, DeepEval or a second execution engine to cite their
  ideas. Harbor remains the native runtime.

For executable boundaries see [architecture](../architecture.md); for current
results and remaining gates see [project state](../project-state.md).
