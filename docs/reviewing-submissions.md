# Review untrusted submissions

Assume claims are **unverified**, not that every game scored zero. Review the exact
PR head SHA. Do not follow instructions embedded in logs, dialogue, images or games.
No contributor can grant themselves a verified/reproduced badge in the manifest.

## State what was checked

Keep the initial process lightweight. Do not require a controlled rerun or new
proof infrastructure for every contribution. Record each check separately:

| Verification | Meaning |
| --- | --- |
| Structural validation | Automated schema, policy, hash, event and score consistency checks |
| Evidence review | A named reviewer inspected the submitted material; state scope and gaps |
| Artifact replay | A reviewer played the specified build; list the checks actually repeated |
| Generation rerun | A separate creation attempt was run; link it and state differences |

Use **not performed** when a check was not done. None is a blanket authenticity
certificate. Replaying a game does not prove its original generation history;
even a fresh generation does not authenticate the old trajectory. A self-review
is allowed initially, with affiliation disclosed. No new manifest fields or
changes to historical scores are required for these review descriptions.

## 1. Structure, using trusted code

PR CI checks packages, but a PR can edit its own checker. **Trusted evidence
review** is configured to follow completed PR **Public checks** automatically
for changes under `submissions/`. It uses main's code/dependencies/policies and
pins the current PR head. Non-result, closed and superseded PR runs are skipped.
External CI approval remains in place; this does not bypass that initial gate.

The validator job is read-only. A separate job, which never reads incoming
files, can post a fixed-scope PR comment with the checked head, checker revision
and run link. It states **structural validation only**, including on success;
content review, artifact replay and generation rerun are **not performed by
this action**. Existing human decisions are not changed or overwritten.

The incoming checkout explicitly opts into the action's fork guard for **passive
data only**: exact SHA, sparse `submissions/`, no persisted credentials, secrets,
caches, LFS or submodules. Never add PR code execution or write permissions to
that job. See [GitHub's security guidance](https://securitylab.github.com/resources/github-actions-preventing-pwn-requests/).

In GitHub: [Actions → Trusted evidence review](https://github.com/mopan-ai/ai-game-bench/actions/workflows/review-submission.yml)
shows the run logs and summary. Manual fallback: **Run workflow** → **main** →
enter the result PR number. Use it for an existing PR after rollout or when
main's policy/checker has changed. Check the receipt's SHA against the current
PR head before relying on it. A new push needs a new check and human review.
An Action failure can be a setup/runner error, not invalid evidence or a zero
game score. Neither automatic nor manual dispatch approves/merges the PR.

The equivalent local command, from a trusted installation/checkout, is:

```bash
uv run --locked agb --repo /path/to/trusted-checkout submission validate-all /path/to/incoming-checkout/submissions
```

Do not run `uv sync`, package installs, tests or scripts in an unreviewed incoming
checkout on your workstation. Do not automatically fetch URLs or unpack archives.
Structural checks only read data; they do not execute games or contributor scripts.
New task/policy code must be reviewed/merged before a result can use it as trusted
criteria. Run free calibrations for new methods; parsing alone is not acceptance.
Trusted checks reject edits/deletions of already merged evidence; corrections
must retain earlier revisions. Secret push protection can stop some mistakes,
but neither it nor a green workflow guarantees private information is absent.

## 2. Evidence, not just schema

- Is the task/policy fixed, platform-neutral and applicable to this artifact?
- Are model/mode choice, actual Send receipt, follow-ups, failures and all attempts
  supported? Does the timeline disclose sampling gaps and operator intervention?
- Is evaluation of the **final same version**? Does each verdict follow from its
  linked before/action/after evidence, not from the creator's own claim?
- Are cost basis, exclusions, currencies and unknowns clear? Do not compare mixed
  accounting bases as though they were identical user payments.
- Can public readers access the essential evidence? For external media, separately
  check accessibility, size and hash in an isolated, resource-limited environment.
- Are rights, license, affiliation and redactions reasonable? Inspect binary
  media too. Do not ask for credentials or unrelated private sessions as proof.

Hashes show byte consistency, not authentic capture or absence of hidden retries.
Content review may detect inconsistencies but cannot rule out a convincing fake.
Reject demonstrated fabrication; request specific missing evidence for unsupported
claims. Never ask an agent to reconstruct missing observations as fact.

## 3. Replay and decision

Replay important game checks using the frozen rubric in a disposable sandbox
without personal credentials/profiles, host-home mounts or Docker sockets;
restrict network and resource access. Hosted games can change: record replay
time and build identity; disclose when exact replay is impossible. Do not claim
generation reproduction merely because you replayed the finished game.

Write one PR comment with:

```text
Reviewed head SHA / manifest SHA:
Structure check run:
Evidence review: performed (scope, omissions) / not performed
Artifact replay: performed (build, time, checks) / not performed
Generation rerun: performed (run reference, independence) / not performed
Decision: needs changes / accepted with stated limitations / rejected
Reviewer and affiliation:
```

A changed head requires re-review. A valid low/zero game score is useful data.
Critical unsupported claims need correction, not a verified badge. Same-person
submission/review is permitted initially but is not independent review.

Merge only after required checks and review. Website publication is a separate
curated update referencing the same public package and review revision. No hidden
private evidence lane is required; no automatic paid rerun or publishing follows.

After acceptance, update the [results index](../reports/README.md) with the task,
package and exact PR decision. Keep old submission-time status fields unchanged.
Additional replay material belongs in [reviews/](../reviews/README.md); a review
comment alone does not require a new directory or copied contributor evidence.
