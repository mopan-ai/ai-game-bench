# Run locally

Use the repository checkout, uv, Python 3.12 and a running Docker daemon.
macOS with Docker Desktop is the initial local target; CI targets Ubuntu Linux.
For an introduction without Docker or model calls, [validate the free example](getting-started.md#try-the-free-example).

```bash
uv sync --locked
uv run agb doctor
./verify.sh
./scripts/test-browser.sh
./scripts/run-smoke.sh
```

- `verify.sh`: fast unit, contract and repository checks. Browser tests explicitly
  skip here; this command alone is not browser/E2E validation.
- `test-browser.sh`: actual Chromium on authored good/broken fixtures, in a
  read-only container with no external network. No model account needed.
- `run-smoke.sh`: real Harbor Oracle and Nop trials, then asserts expected
  rewards and zero infrastructure errors from native job and trial JSON.

All are free of model usage. Docker/pip downloads still use bandwidth and disk.

## Single run and evidence

```bash
uv run agb run --agent oracle --job-name local-demo --dry-run
uv run agb run --agent oracle --job-name local-demo
uv run agb inspect jobs/local-demo --expect 1
uv run agb view --port 8080
```

The wrapper refuses an existing job name. Within a trial, inspect `result.json`
and `verifier/`: reward, details, actions, screenshots, trace and frozen game
bundle. Nop has no game to screenshot. The viewer serves existing Harbor records,
not a new dashboard. Its first frontend build may require Node/npm and internet.

`agb platforms` distinguishes implemented calibration agents from planned
platform integrations. Selecting an unintegrated agent fails before any model
call. This preview does not configure or test your paid accounts.

## Common failures

- Doctor's Docker check fails: start Docker Desktop and check `docker info`.
- Package/version check fails: run `uv sync --locked`, not a global Harbor.
- Browser image cannot download: check Docker networking/disk space. That is an
  environment error, not a game score.
- A job has exceptions or no rewards: inspect `job.log` and trial logs. Do not
  rewrite the result to zero; fix the environment and run a new job.
- Port busy: choose `agb view --port 8081`. Viewer remains localhost-only.

## Proposed gameplay examples

For the proposed platformer/racing methods, see the
[acceptance cards and local behavior fixtures](../fixtures/calibration/gameplay-v1/README.md).
`./scripts/test-gameplay-calibration.sh` replays focused pass/fault checks in an
isolated browser and retains local video/actions/JSON. It calls no model and is
not an independent game judge or a creator-platform benchmark run.

## Publishing boundary

Never attach raw `jobs/` to a public issue. Share a scrubbed summary and the
minimum authorized evidence. No setup command sends cookies, starts remote
creation, deploys a site, or pushes to GitHub.
