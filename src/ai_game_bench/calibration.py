"""Prepare native Harbor tasks and summarize their results, without running agents."""

from __future__ import annotations

import hashlib
import json
import random
import secrets
import shutil
from collections import Counter, defaultdict
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit_tool_events(path: Path):
    """Audit observed access, not the availability of every Codex built-in tool."""
    if not path.is_file():
        return {"valid": False, "issues": ["Missing native evaluator event log"]}
    tools, warnings, issues = Counter(), [], []
    allowed_items = {
        "userMessage",
        "reasoning",
        "agentMessage",
        "dynamicToolCall",
        "contextCompaction",
    }
    for line in path.read_text().splitlines():
        event = json.loads(line)
        if event.get("direction") != "receive":
            continue
        method, params = event.get("method"), event.get("params") or {}
        if method == "item/tool/call":
            name = params.get("tool", "unknown")
            tools[name] += 1
            if name not in {"game_observe", "game_act"}:
                issues.append("Unexpected tool: " + name)
        if method == "item/completed" and params.get("item", {}).get("type") not in allowed_items:
            issues.append("Unexpected completed item: " + str(params.get("item", {}).get("type")))
        if method in {"warning", "configWarning"}:
            warnings.append(params)
    if not tools:
        issues.append("No browser tool calls recorded")
    return {
        "valid": not issues,
        "tools_used": dict(tools),
        "warnings": warnings,
        "issues": issues,
        "scope": "Observed tool use only; not a proof of OS-level model isolation",
    }


def prepare(root: Path, output: Path, model: str, effort: str, *, allow_model_calls=False):
    from harbor.models.job.config import JobConfig

    if output.exists():
        raise ValueError("Use a new directory; calibration records are not overwritten.")
    source = root / "calibration/judge-v1"
    catalog = json.loads((source / "cases.json").read_text())
    fixtures = root / catalog["fixture"]
    output.mkdir(parents=True)
    instruction = (source / "instruction.md").read_text()
    entries = []
    fixture_hashes = {p.name: sha(p) for p in fixtures.iterdir() if p.is_file()}
    method_hashes = {p.name: sha(p) for p in source.iterdir() if p.is_file()}
    for pair in catalog["pairs"]:
        policy_path = root / "policies" / (pair["policy"] + ".json")
        policy = json.loads(policy_path.read_text())
        assert any(c["id"] == pair["criterion"] for c in policy["criteria"])
        for variant in ("none", pair["fault"]):
            for repetition in (1, 2):
                ident = "case-" + secrets.token_hex(6)
                task = output / "tasks" / ident
                for name in ("environment/fixture", "tests", "solution"):
                    (task / name).mkdir(parents=True)
                prompt = instruction + "\nBehavior to evaluate:\n" + pair["probe"] + "\n"
                (task / "instruction.md").write_text(prompt)
                html = (fixtures / "index.html").read_text()
                html = html.replace(
                    '<nav><a href="?game=platformer">Platformer</a>'
                    '<a href="?game=racing">3D racing</a></nav>',
                    "",
                )
                html = html.replace("Game behavior calibration · local reference", "Game")
                html = html.replace(
                    "Hand-authored test fixture, not a creator-platform result "
                    "or a quality benchmark.",
                    "",
                )
                js = (fixtures / "game.js").read_text()
                js = js.replace(
                    "const game = params.get('game') === 'racing' ? 'racing' : 'platformer';",
                    f"const game = {json.dumps(pair['game'])};",
                )
                js = js.replace(
                    "const defect = params.get('defect') || 'none';",
                    f"const defect = {json.dumps(variant)};",
                )
                js = js.replace("Platformer reference", "Platformer").replace(
                    "3D racing reference", "3D racing"
                )
                (task / "environment/fixture/index.html").write_text(html)
                (task / "environment/fixture/game.js").write_text(js)
                shutil.copyfile(source / "bridge.py", task / "environment/bridge.py")
                (task / "environment/Dockerfile").write_text(
                    "FROM mcr.microsoft.com/playwright/python:v1.62.0-noble\n"
                    "RUN pip install --no-cache-dir playwright==1.62.0 pytest==8.4.2\n"
                    "COPY fixture /fixture\nCOPY bridge.py /opt/bridge.py\nWORKDIR /workspace\n"
                )
                (task / "task.toml").write_text(
                    'schema_version = "1.4"\nartifacts = ["/workspace/judgement.json"]\n'
                    f'[task]\nname = "agb-calibration/{ident}"\nversion = "0.1.0"\n'
                    "[agent]\ntimeout_sec = 300.0\n"
                    '[verifier]\ntimeout_sec = 30.0\nenvironment_mode = "shared"\n'
                    'network_mode = "no-network"\n'
                    '[environment]\nnetwork_mode = "no-network"\nbuild_timeout_sec = 600.0\n'
                    'os = "linux"\ncpus = 2\nmemory_mb = 2048\nstorage_mb = 4096\n'
                )
                expected = "passed" if variant == "none" else "failed"
                (task / "tests/answer.json").write_text(json.dumps({"expected_status": expected}))
                shutil.copyfile(source / "verify.py", task / "tests/verify.py")
                (task / "tests/test.sh").write_text(
                    "#!/bin/bash\nset -euo pipefail\npython /tests/verify.py\n"
                )
                (task / "solution/solve.sh").write_text(
                    "#!/bin/bash\n# No game-solving oracle: this task evaluates a judge.\nexit 1\n"
                )
                entries.append(
                    {
                        "id": ident,
                        "game": pair["game"],
                        "criterion": pair["criterion"],
                        "variant": variant,
                        "repetition": repetition,
                        "expected_status": expected,
                        "policy": pair["policy"],
                        "policy_sha256": sha(policy_path),
                        "probe": pair["probe"],
                        "instruction_sha256": sha(task / "instruction.md"),
                        "rendered_fixture_sha256": {
                            name: sha(task / "environment/fixture" / name)
                            for name in ("index.html", "game.js")
                        },
                    }
                )
    random.SystemRandom().shuffle(entries)
    config = JobConfig.model_validate(
        {
            "job_name": output.name,
            "jobs_dir": str(root / "jobs"),
            "n_attempts": 1,
            "n_concurrent_trials": 1,
            "retry": {"max_retries": 0},
            "agents": [
                {
                    "import_path": "ai_game_bench.judge_agent:CodexGameplayJudge",
                    "model_name": model,
                    "kwargs": {"effort": effort, "allow_model_calls": allow_model_calls},
                }
            ],
            "tasks": [{"path": str((output / "tasks" / row["id"]).resolve())} for row in entries],
        }
    )
    manifest = {
        "schema_version": catalog["version"],
        "kind": catalog["kind"],
        "model": model,
        "effort": effort,
        "expected_trials": 16,
        "fixture_hashes": fixture_hashes,
        "method_hashes": method_hashes,
        "cases": entries,
        "scope": "4 focused checks x 2 labels x 2 fresh trials; no game score",
    }
    (output / "plan.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (output / "job.json").write_text(config.model_dump_json(indent=2) + "\n")
    return manifest


def summarize(plan_path: Path, jobs: Path | list[Path], review_path: Path | None = None):
    """Join declared native jobs without dropping abstentions, errors or duplicates."""
    plan = json.loads(plan_path.read_text())
    cases = {c["id"]: c for c in plan["cases"]}
    if len(cases) != len(plan["cases"]):
        raise ValueError("Duplicate case in calibration plan")
    jobs = [jobs] if isinstance(jobs, Path) else jobs
    if not jobs or any(not (job / "result.json").is_file() for job in jobs):
        raise ValueError("Every input must be a native Harbor job directory")
    records = {}
    identities, threads = set(), set()
    for path in sorted(p for job in jobs for p in job.glob("*/result.json")):
        native = json.loads(path.read_text())
        ident = native.get("task_name", "").rsplit("/", 1)[-1]
        if ident not in cases:
            raise ValueError("Job has an unexpected task")
        if ident in records:
            raise ValueError("Duplicate trial; use one declared attempt per opaque case")
        case = cases[ident]
        detail_path = path.parent / "verifier/details.json"
        detail = json.loads(detail_path.read_text()) if detail_path.exists() else None
        context = native.get("agent_result") or {}
        judgement_path = path.parent / "agent/judgement.json"
        judgement = json.loads(judgement_path.read_text()) if judgement_path.exists() else None
        error = native.get("exception_info")
        metadata = context.get("metadata") or {}
        if detail and not error:
            if (
                metadata.get("requested_model") != plan["model"]
                or metadata.get("resolved_model") != plan["model"]
                or metadata.get("effort") != plan["effort"]
                or metadata.get("instruction_sha256") != case["instruction_sha256"]
            ):
                raise ValueError("Evaluator model, effort or instruction differs from the plan")
            identity = tuple(
                metadata.get(k) for k in ("adapter_sha256", "codex_version", "tool_schema_sha256")
            )
            if not all(identity) or not metadata.get("thread_id"):
                raise ValueError("Missing evaluator identity or fresh-context receipt")
            identities.add(identity)
            if metadata["thread_id"] in threads:
                raise ValueError("Calibration trials reused an evaluator thread")
            threads.add(metadata["thread_id"])
            if (
                detail.get("expected_status") != case["expected_status"]
                or not judgement
                or detail.get("observed_status") != judgement["status"]
            ):
                raise ValueError("Native verdict/label does not match the declared case")
            status = judgement["status"]
            flags = {
                "correct": status == case["expected_status"],
                "false_pass": case["expected_status"] == "failed" and status == "passed",
                "false_failure": case["expected_status"] == "passed" and status == "failed",
                "not_tested": status == "not_tested",
            }
            if any(detail.get(k) != v for k, v in flags.items()):
                raise ValueError("Native calibration flags disagree with the verdict")
        access = audit_tool_events(path.parent / "agent/codex-events.jsonl")
        invalid = (
            bool(error)
            or not detail
            or bool(metadata.get("capture_close_error"))
            or not access["valid"]
        )
        records[ident] = {
            **case,
            "trial_dir": str(path.parent),
            "details": detail,
            "judgement": judgement,
            "native_result_sha256": sha(path),
            "invalid_measurement": invalid,
            "infrastructure_error": bool(error) or bool(metadata.get("capture_close_error")),
            "exception_type": error.get("exception_type") if error else None,
            "access_audit": access,
            "usage": context,
            "review": {"status": "not_performed", "finding": None},
        }
    if len(identities) > 1:
        raise ValueError("Do not pool different evaluator runtime/tool versions")
    review_metadata = None
    if review_path:
        review = json.loads(review_path.read_text())
        if review.get("schema_version") != "judge-evidence-review/0.1":
            raise ValueError("Unsupported evidence review format")
        review_metadata = {k: review.get(k) for k in ("reviewer", "blind", "scope")}
        seen = set()
        for entry in review["records"]:
            ident = entry["case_id"]
            if ident in seen or ident not in records:
                raise ValueError("Evidence review has a duplicate or unknown case")
            seen.add(ident)
            if entry["native_result_sha256"] != records[ident]["native_result_sha256"]:
                raise ValueError("Evidence review is for a different native result")
            if entry["finding"] not in {"supported", "unsupported", "inconclusive"}:
                raise ValueError("Unknown evidence review finding")
            records[ident]["review"] = {"status": "recorded", **entry}
    missing = sorted(set(cases) - set(records))
    valid = [r for r in records.values() if not r["invalid_measurement"]]
    counts = Counter(r["details"]["observed_status"] for r in valid)
    repeats = defaultdict(list)
    for r in valid:
        repeats[(r["game"], r["criterion"], r["variant"])].append(r["details"]["observed_status"])
    paired = [v for v in repeats.values() if len(v) == 2]
    by_check = []
    for game, criterion in sorted({(c["game"], c["criterion"]) for c in cases.values()}):
        selected = [r for r in valid if (r["game"], r["criterion"]) == (game, criterion)]
        by_check.append(
            {
                "game": game,
                "criterion": criterion,
                "expected_trials": sum(
                    (c["game"], c["criterion"]) == (game, criterion) for c in cases.values()
                ),
                "valid_trials": len(selected),
                **{
                    name: sum(r["details"][name] for r in selected)
                    for name in ("correct", "false_pass", "false_failure", "not_tested")
                },
            }
        )
    return {
        "schema_version": "judge-calibration-report/0.1",
        "kind": plan["kind"],
        "model": plan["model"],
        "effort": plan["effort"],
        "plan_sha256": sha(plan_path),
        "native_jobs": [str(j) for j in jobs],
        "runtime_identities": [list(i) for i in sorted(identities)],
        "independent_threads_recorded": len(threads),
        "expected_trials": len(cases),
        "recorded_trials": len(records),
        "missing_cases": missing,
        "valid_trials": len(valid),
        "invalid_measurements": len(records) - len(valid),
        "infrastructure_errors": sum(r["infrastructure_error"] for r in records.values()),
        "status_counts": dict(counts),
        "correct": sum(r["details"]["correct"] for r in valid),
        "false_passes": sum(r["details"]["false_pass"] for r in valid),
        "fault_denominator": sum(r["expected_status"] == "failed" for r in valid),
        "false_failures": sum(r["details"]["false_failure"] for r in valid),
        "working_denominator": sum(r["expected_status"] == "passed" for r in valid),
        "not_tested": counts["not_tested"],
        "repeat_pairs": len(paired),
        "repeat_agreements": sum(v[0] == v[1] for v in paired),
        "by_check": by_check,
        "usage": {
            key: sum((r["usage"].get(key) or 0) for r in records.values())
            for key in ("n_input_tokens", "n_cache_tokens", "n_output_tokens")
        },
        "cost_usd": None,
        "cost_basis": "ChatGPT subscription; per-session charge unavailable, not zero",
        "evidence_review": review_metadata,
        "evidence_review_counts": dict(
            Counter(r["review"].get("finding") or "not_performed" for r in records.values())
        ),
        "records": list(records.values()),
        "limitations": [
            "Public authored examples; not a held-out generalization test.",
            "Agreement can be consistently wrong; inspect correctness and coverage separately.",
            "Evidence reference integrity is automated; evidence meaning needs review.",
            "No full game quality, creator ranking, Tetris rescoring or live generation.",
        ],
    }
