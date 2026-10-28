# Submit public evidence — for humans and agents

**Read the [public-data terms](../README.md#public-data-and-privacy-terms) first.**
Everything pushed to a public fork is already public. No private workspace is
needed. These commands prepare/check files; they do not run a creator or upload.

## 1. Choose a frozen task and policy

Fork the repository and clone **your fork**. Install with `uv sync --locked`.
The current tools target macOS/Linux (use WSL on Windows).

```bash
uv run agb submission policies
uv run agb submission init .submission-drafts/my-run --id my-run --policy counter-calibration-v1
```

The counter policy is a free calibration. The separate
[Tetris browser protocol](../protocols/tetris-browser-pilot-v1/evaluation.md) is a
manual pilot, not an automatic Harbor run. If a task/policy is absent, [propose it](adding-tasks.md)
before a formal run. Development pilots must be labeled as such; do not retrofit
a rubric after seeing results. Platform references are not executable adapters.

For historical Tetris comparisons, read the [fixed 40/20/20/20 scoring rules](../scoring/README.md).
Freeze these alongside the creation method before new runs. Existing pilot data
can receive an explicitly retrospective score addendum, never a rewritten score.

Proposed platformer/racing v2 methods use `public-submission/0.2`: evaluator
configuration, separate generation-timeout semantics and explicit-set summaries.
See [measurement rules](measurement.md). They require method approval and fresh
runs; never relabel historical submissions. Existing v0.1 workflows still work.

`init` creates an unapproved draft with empty trajectories. It does not fabricate
evidence, approve publication or connect a browser. Read the policy's limits.
For agents, schemas are available without network calls:

```bash
uv run agb submission schema manifest
uv run agb submission schema event
uv run agb submission schema policy
```

## 2. Record during execution, not from memory afterward

Use the exact policy prompt and your own authorized account/environment. Keep
original Harbor records local; export only task-scoped observations. For browser
runs follow [the browser guide](../platforms/shared/browser-workflow.md), including
owner-selected profile and explicit model/spending permission. Recording is
currently the operator/agent's responsibility; there is no automatic recorder.
Harbor may print an `upload` suggestion after a run; that is not approval to share
raw jobs. Use the reviewed public-package workflow below instead.

The draft contains `manifest.json`, `creation.jsonl` and `evaluation.jsonl`.
Add scrubbed files to its explicit `files` allowlist; hashes/sizes may initially
be null. Complete every manifest field; `null` means unknown, not free usage.

Each JSONL event has `seq`, unique `id`, timezone-aware `at`, `kind`, `detail`,
`evidence`, and optionally `artifact_id`/`prompt`. Number each stream from 1.
Evidence names are allowlisted local files or `external:<id>` references.

| Stream | Required record |
| --- | --- |
| Creation | `session_started`; model/mode choice; `prompt_accepted` with the exact prompt and receipt evidence; progress, every clarification/follow-up/repair; one terminal outcome |
| Evaluation | `evaluation_started`; actual actions and evidence-backed observations; `evaluation_finished`; the same final `artifact_id` throughout |

Terminal outcomes are `delivered`, `build_failure`, `timeout`, `auth_failure` or
`infrastructure_error`. Log every attempt separately, including failures. Policy
violations require disclosure/correction, not deleting the inconvenient attempt.
Keep model identity/effort unknown when not exposed. Record browser/runtime,
versions, account tier if safe, and operator interventions in the manifest/events.

Evaluation receives task + final game, not creation chat or billing; disclose
when this separation was impossible. Each criterion references evaluation
observation IDs, which point to supporting screenshots/logs/clips. A creator's
"done" is not a gameplay observation. Native verifier exports may summarize its
actions and observations with references to scrubbed verifier logs.

Use a build/version where exposed; a remote URL is not frozen bytes. A native
bundle is identified by its hash and task-scoped Harbor run/trial reference.
Separate estimated cost, credit valuation and actual charges, with sources and
currency/rate/date in `basis`; record creator/operator/evaluator separately when
available. Do not label missing subscription allocation as zero.

Small JSON/JSONL/text and PNG/JPEG/WebP files go in the package (each under 2 MiB,
package at most 20 MiB). Larger clips/bundles use stable, publicly accessible
HTTPS references with size/hash. No signed links or account cookies. The local
validator deliberately does not download external files; reviewers must check
them separately in an isolated environment. No raw jobs, archives or executable
game code are copied into the public package.

The [complete synthetic example](../examples/submissions/synthetic-counter/manifest.json)
shows every field. Its observations are invented; never relabel it as a real run.

## 3. Review and prepare the public package

Review text, images and linked media. Declare license/rights, affiliation,
redactions, capture gaps and limitations. Set the four `publication` confirmations
only after the owner approves public release; an agent must not assume consent.

```bash
uv run agb submission prepare .submission-drafts/my-run --output submissions/my-run/r001 --confirm-public
uv run agb submission validate submissions/my-run/r001
uv run agb submission validate-all
```

`prepare` hashes new allowlisted files, rejects changed existing hashes, validates
the package and copies only its allowlist. It never overwrites a destination or
uploads. It prints the exact file list. Unlisted files, unsafe paths and common
secret patterns are rejected. Scans cannot establish privacy or truth.

Exit 0 means **structure valid, still unverified**; exit 2 means fix the reported
problem. Failed games can be valid submissions. Infrastructure errors have null
scores; not-tested criteria have zero with an explicit reason. Recomputed totals
use the trusted policy, not contributor-supplied weights.

## 4. Upload through one ordinary GitHub PR

After explicit publication approval, run these in **your fork**, not the upstream
maintainer checkout. Verify `origin` first. Never use `git add .` for evidence.

```bash
git remote -v
git switch -c submission/my-run
git add -- submissions/my-run/r001
git diff --cached --stat
git diff --cached --check
git commit -m "Add evidence submission my-run r001"
git push -u origin submission/my-run
gh pr create --repo mopan-ai/ai-game-bench --base main --title "Result: my-run r001" --body "Public evidence: submissions/my-run/r001. Please review the exact head revision."
```

Inspect staged files before commit/push. GitHub authentication is yours; never
include it in evidence. Confirm the PR contains the expected commit/files and
retain its URL plus the validator's manifest hash. A local commit is not upload.
Discussion is optional for sharing results, not a second required form.

Before merge, fix the PR and rerun checks; changes invalidate prior review. After
merge, corrections add `r002`, etc., and explain changes in the PR. Keep earlier
revisions. Maintainers [review evidence](reviewing-submissions.md); acceptance is
not independent reproduction or automatic website publication.
