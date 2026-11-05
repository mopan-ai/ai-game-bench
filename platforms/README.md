# Platform support and connection guides

These six directories document the routes used in the historical Tetris pilots.
Agents used browser tools through a consented Chrome connection or invoked local
CLIs. These are **tested workflows, not six working `agb run` plugins**. Account
setup and the orchestration used for those runs are not distributed as reusable
adapters here. The public checkout executes only free Oracle/Nop calibration.

## What “support” means

- **Runnable calibration:** Oracle/Nop execute the free local counter through
  Harbor. They are fixtures, not game-creation platforms.
- **Tested:** a recorded test was performed through agent-operated tool use.
  This does not mean every game passed, a platform is certified, or generation
  was independently reproduced. Human login, authorization and review remain
  separate from the agent's browser/CLI actions.
- **Public execution integration — planned:** none of the six creators is
  enabled in `agb run` yet. The guides do not supply authentication, browser
  control or an automatic recorder. This packaging gap does not make the
  recorded agent tool-use workflow a human-operated test.

| Platform | Status | Execution |
| --- | --- | --- |
| <img src="mopan/logo.png" width="32" height="32" alt=""> &nbsp; [Mopan](mopan/README.md) | Tested | Browser tool use |
| <img src="taptap-maker/logo.svg" width="32" height="32" alt=""> &nbsp; [TapTap Maker](taptap-maker/README.md) | Tested | Browser tool use |
| <img src="astrocade/logo.svg" width="32" height="32" alt=""> &nbsp; [Astrocade](astrocade/README.md) | Tested | Browser tool use |
| <img src="manus/logo.svg" width="32" height="32" alt=""> &nbsp; [Manus](manus/README.md) | Tested | Browser tool use |
| <img src="codex/logo.png" width="32" height="32" alt=""> &nbsp; [Codex](codex/README.md) | Tested | CLI |
| <img src="claude-code/logo.png" width="32" height="32" alt=""> &nbsp; [Claude Code](claude-code/README.md) | Tested | CLI |

[Logo sources and attribution](LOGOS.md). Platform listing does not imply endorsement.

The [results index](../reports/README.md#accepted-evidence) links accepted Tetris
packages and the Codex / Mopan / Wanaka racing development pilot to their review
decisions. Wanaka has pilot evidence but no platform guide yet. Accepted evidence
retains its review limits; historical website reports alone are not accepted
submissions. Neither kind establishes current account availability.

**Requirements:** CLI routes need your local CLI/provider account. Browser
references use an owner-selected, logged-in Chrome profile with explicit control
permission; this repo does not connect it for you. Submission packaging itself
needs neither a browser nor Docker. The free calibration uses Docker/Chromium.
For another browser/control tool, disclose the actual environment and check policy
compatibility; a historical Chrome procedure does not validate that alternative.

One common entry point, with no login, browser control or model spending:

```bash
uv run agb platforms
uv run agb platforms mopan
uv run agb platforms claude-code --json
```

Each directory has `integration.json` (route, setup/evidence fields, historical
report references and explicit readiness) and `README.md` (the actual procedure,
delivery checks and platform-specific pitfalls). These files are documentation
inputs, never executable imports. Do not embed credentials, private project IDs,
current prices or personal Chrome paths. A cost belongs to a **run**, not to a
platform plugin: the same platform can use different models/plans over time.

To submit now, choose an applicable [task/policy](../docs/submissions.md) before
recording. Use your authorized account and tools, record evidence and open a PR.
New platforms may use the same evidence contract when compatible; new tasks/policies
need method review first. A public `agb run` adapter is not required to submit
a separately operated run. Disclose the actual automation and human interventions;
unknown model/effort/cost stays unknown.

Shared material:

- [CLI procedure](shared/cli-workflow.md)
- [Browser procedure](shared/browser-workflow.md)
- [Record template](shared/record.example.json) — blank fields, no historical data

## Turn a reference into an executable integration

Contribute a Harbor agent/configuration, not a second runner. Keep platform-specific
setup and observation logic in its own directory/module and reuse the common
submission/evidence contract. Do not introduce a dynamic plugin loader that runs
arbitrary code just to list platforms.

1. Add credential-free contract/fake-site tests for setup, submission, follow-ups,
   final delivery, timeout and access failure.
2. Produce the artifact handoff required by a compatible task. The current frozen
   DOM counter does **not** accept a remote URL or assess Tetris.
3. Document account setup without exporting login state. Obtain separate approval
   for a bounded live smoke; record actual versions and all attempts.
4. After maintainer review, wire the adapter through Harbor and update the CLI's
   supported execution path. Changing `public_execution_supported` alone must not
   enable execution. Keep historical reports labeled historical.

See [platform contract](../docs/platforms.md) and
[contribution checks](../docs/contribution-workflow.md).
