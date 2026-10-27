"""Versioned, offline measurements of submitted claims; never a gameplay judge."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from .submission_models import Submission
from .submissions import digest, encode, model, parse_json, read_file, require, validate


def check_policy(policy):
    rules = policy.measurement
    require(
        (rules is not None) == (policy.schema_version == "public-policy/0.2"),
        "policy",
        "Only v0.2 policies require measurement rules; v0.1 meaning is frozen.",
    )
    if rules is None:
        return
    criteria = {c.id: c for c in policy.criteria}
    require(
        len(set(rules.core_criteria)) == len(rules.core_criteria)
        and set(rules.core_criteria) <= set(criteria)
        and all(not criteria[key].allow_partial for key in rules.core_criteria)
        and len(set(rules.allowed_access)) == len(rules.allowed_access),
        "policy",
        "Core checks must be distinct binary criteria; access modes must be distinct.",
    )
    if policy.time_score:
        require(
            policy.time_score.criterion_id not in rules.core_criteria
            and set(policy.time_score.required_passes) <= set(rules.core_criteria),
            "policy",
            "Time-credit gates must be core checks, not the time criterion itself.",
        )


def check_configuration(result, rules, blobs, references):
    cfg = result.configuration
    require(cfg is not None, "evaluation_configuration", "v0.2 needs evaluator configuration.")
    require(
        cfg.access_mode in rules.allowed_access
        and cfg.clock == rules.clock
        and (cfg.viewport_width, cfg.viewport_height)
        == (rules.viewport_width, rules.viewport_height),
        "evaluation_configuration",
        "Access, clock and scored viewport must match the frozen policy.",
    )
    require(
        result.mode != "agent_visual" or cfg.access_mode == "screenshot_only",
        "evaluation_configuration",
        "A visual-only agent cannot claim DOM/instrumented access.",
    )
    require(
        result.mode != "agent_dom" or cfg.access_mode != "screenshot_only",
        "evaluation_configuration",
        "DOM-assisted evaluation must disclose visible_ui or instrumented access.",
    )
    require(
        len({tool.name for tool in cfg.tools}) == len(cfg.tools),
        "evaluation_configuration",
        "Evaluator tool names must be unique.",
    )
    agent = result.mode in {"agent_dom", "agent_visual"}
    require(
        not agent or (bool(cfg.tools) and cfg.instructions_file is not None),
        "evaluation_configuration",
        "Agent evaluation needs its tool configuration and public evaluation instructions.",
    )
    if cfg.instructions_file is None:
        require(
            cfg.instructions_sha256 is None,
            "evaluation_configuration",
            "Instructions hash needs a matching allowlisted file.",
        )
    else:
        require(
            cfg.instructions_file in references
            and cfg.instructions_file in blobs
            and Path(cfg.instructions_file).suffix in {".md", ".txt", ".json"}
            and digest(blobs[cfg.instructions_file]) == cfg.instructions_sha256,
            "evaluation_configuration",
            "Public evaluator instructions must be allowlisted, non-trajectory text with its hash.",
        )


def measure_attempt(attempt, policy, total):
    by_id = {v.criterion_id: v for v in attempt.result.criteria}
    statuses = Counter(by_id[key].status for key in policy.measurement.core_criteria)
    generation_valid = attempt.outcome not in {"auth_failure", "infrastructure_error"}
    scored = total is not None
    return {
        "schema_version": "attempt-measurement/1",
        "delivery_success": attempt.outcome == "delivered" if generation_valid else None,
        "core_success": (
            attempt.outcome == "delivered"
            and statuses["passed"] == len(policy.measurement.core_criteria)
            if scored
            else None
        ),
        "evaluation_completed": attempt.outcome == "delivered" and scored,
        "core_checks": {
            "total": len(policy.measurement.core_criteria),
            **{
                status: statuses[status]
                for status in ("passed", "failed", "not_tested", "infra_error")
            },
        },
    }


def configuration_gaps(result):
    cfg = result.configuration
    gaps = []
    if cfg.browser_version is None:
        gaps.append("browser_version")
    if result.mode in {"agent_dom", "agent_visual"}:
        for name, value in (
            ("model", result.model),
            ("harness_version", cfg.harness_version),
            ("effort", cfg.effort),
        ):
            if value is None:
                gaps.append(name)
        gaps.extend(f"tool:{t.name}:version" for t in cfg.tools if t.version is None)
    return gaps


def rate(values):
    known = [value for value in values if value is not None]
    return {
        "successes": sum(known),
        "denominator": len(known),
        "excluded_measurements": len(values) - len(known),
        "rate": sum(known) / len(known) if known else None,
    }


def summarize(directories: list[Path], trusted_root: Path, expected_attempts: int):
    """Explicit selected-set summary, not a registry, ranking or independent review."""
    require(0 < len(directories) <= 100, "summary", "Select 1–100 packages explicitly.")
    require(0 < expected_attempts <= 10000, "summary", "Declare a positive expected attempt count.")
    groups = {}
    submission_ids, source_ids = set(), set()
    count = 0
    for directory in directories:
        # Bind the validation result and subsequent measurement to the same manifest bytes.
        raw = read_file(directory, "manifest.json")
        record = model(Submission, parse_json(raw))
        checked = validate(directory, trusted_root)
        require(
            checked["structure_valid"] and checked["manifest_sha256"] == digest(raw),
            "summary",
            "Every selected package must validate, with an unchanged manifest.",
        )
        require(
            record.schema_version == "public-submission/0.2",
            "summary",
            "Summaries require v0.2 packages; historical v0.1 results are not reinterpreted.",
        )
        # Model/effort/version corrections describe the same source run. They must
        # not turn a repeated review or revision into another generation attempt.
        source = (
            record.source_kind,
            record.creator.platform.strip().casefold(),
            record.source_ref.strip(),
        )
        require(
            record.id not in submission_ids and source not in source_ids,
            "duplicate_run",
            "Select one revision per submission/source run; revisions are not new attempts.",
        )
        submission_ids.add(record.id)
        source_ids.add(source)
        for attempt, result in zip(record.attempts, checked["attempts"], strict=True):
            count += 1
            cfg = attempt.result.configuration.model_dump()
            cfg.pop("instructions_file")  # File location is not an evaluator setting; hash is.
            cfg["tools"] = sorted(cfg["tools"], key=lambda tool: tool["name"])
            cohort = {
                "policy_id": record.policy_id,
                "policy_sha256": record.policy_sha256,
                "kind": record.kind,
                "creator": record.creator.model_dump(),
                "evaluator": attempt.result.evaluator,
                "evaluator_model": attempt.result.model,
                "evaluation_mode": attempt.result.mode,
                "creation_context_hidden": attempt.result.creation_context_hidden,
                "configuration": cfg,
                "environment": record.environment,
            }
            gaps = configuration_gaps(attempt.result)
            # Unknown versions do not establish a common evaluator configuration.
            key = digest(encode(cohort)) + (f":{record.id}:{attempt.id}" if gaps else "")
            group = groups.setdefault(
                key, {"cohort": cohort, "configuration_unknowns": gaps, "attempts": []}
            )
            group["attempts"].append(
                {
                    "submission": record.id,
                    "revision": record.revision,
                    "manifest_sha256": checked["manifest_sha256"],
                    **result,
                }
            )
    require(
        count == expected_attempts,
        "missing_attempts",
        "Selected attempt count differs from expected; include failed/invalid runs, not just wins.",
    )
    output = []
    for key, group in sorted(groups.items()):
        attempts = group["attempts"]
        scores = [a["recomputed_total"] for a in attempts if a["recomputed_total"] is not None]
        output.append(
            {
                "group_id": key,
                **group,
                "recorded_attempts": len(attempts),
                "outcomes": dict(sorted(Counter(a["outcome"] for a in attempts).items())),
                "delivery": rate([a["measurement"]["delivery_success"] for a in attempts]),
                "core_success": rate([a["measurement"]["core_success"] for a in attempts]),
                "total_score": {
                    "mean": sum(scores) / len(scores) if scores else None,
                    "scored_attempts": len(scores),
                    "excluded_measurements": len(attempts) - len(scores),
                },
            }
        )
    return {
        "schema_version": "submission-summary/1",
        "review_status": "unverified",
        "expected_attempts": expected_attempts,
        "recorded_attempts": count,
        "groups": output,
        "limitations": [
            "Arithmetic on submitted claims, not gameplay verification or maintainer acceptance.",
            "Only the selected set is summarized; hidden/missing runs cannot be detected.",
            "Rates exclude and count measurement errors; exclusions are never passes.",
            "Different policies, permissions or evaluator configurations are not pooled or ranked.",
            "Same-build reevaluations belong in calibration reports, not generation counts.",
        ],
    }
