"""Small convenience layer over Harbor; no scheduler or alternative result store."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import math
import os
import re
import shlex
import shutil
import subprocess
import sys
import tomllib
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

HARBOR_VERSION = "0.22.0"
DEFAULT_TASK = "smoke-create-v0.2/create-click-counter-zh-001"
PLATFORMS = (
    ("oracle", "Ready", "Free reference solution; calibration only"),
    ("nop", "Ready", "Free empty submission; negative calibration"),
    ("codex", "Not integrated", "Harbor agent exists; public recipe not validated"),
    ("claude-code", "Not integrated", "Harbor agent exists; public recipe not validated"),
    ("mopan", "Not integrated", "Browser creation recipe; no public automation yet"),
    ("astrocade", "Not integrated", "Browser creation recipe; no public automation yet"),
    ("taptap-maker", "Not integrated", "Browser creation recipe; no public automation yet"),
    ("manus", "Not integrated", "Browser task/preview recipe; no public automation yet"),
)
REFERENCE_PLATFORMS = tuple(name for name, _, _ in PLATFORMS if name not in {"oracle", "nop"})


def repository_root(explicit: Path | None = None) -> Path:
    start = (explicit or Path.cwd()).resolve()
    candidates = [start] if explicit else [start, *start.parents]
    for candidate in candidates:
        config = candidate / "pyproject.toml"
        if (
            config.is_file()
            and (candidate / "datasets").is_dir()
            and tomllib.loads(config.read_text()).get("project", {}).get("name") == "ai-game-bench"
        ):
            return candidate
    raise ValueError("Run from the AI Game Bench checkout, or supply --repo PATH.")


def task_directory(root: Path, name: str) -> Path:
    base = (root / "datasets").resolve()
    task = (base / name).resolve()
    if not task.is_relative_to(base) or not (task / "task.toml").is_file():
        raise ValueError("Task must be an existing directory under datasets/; use agb tasks.")
    return task


def harbor_executable() -> str:
    # Prefer the interpreter's environment, avoiding a different global Harbor.
    candidate = Path(sys.executable).parent / "harbor"
    executable = str(candidate) if candidate.is_file() else shutil.which("harbor")
    try:
        installed = importlib.metadata.version("harbor")
    except importlib.metadata.PackageNotFoundError as exc:
        raise ValueError("Harbor is missing. Run uv sync --locked.") from exc
    if not executable or installed != HARBOR_VERSION:
        raise ValueError(f"Harbor {HARBOR_VERSION} is required. Run uv sync --locked.")
    return executable


def run_command(root: Path, task: str, agent: str, job_name: str) -> list[str]:
    if agent not in {"oracle", "nop"}:
        raise ValueError(
            f"{agent} is not integrated in this public preview. "
            "No model call was made. See docs/platforms.md."
        )
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", job_name):
        raise ValueError("Job name must be 1–80 letters, digits, underscores or hyphens.")
    if (root / "jobs" / job_name).exists():
        raise ValueError("Job already exists; select a new name. Historical jobs are immutable.")
    return [
        harbor_executable(),
        "run",
        "-p",
        str(task_directory(root, task)),
        "-a",
        agent,
        "--jobs-dir",
        str(root / "jobs"),
        "--job-name",
        job_name,
        "--n-attempts",
        "1",
        "--n-concurrent",
        "1",
        "--max-retries",
        "0",
    ]


def inspect_job(directory: Path, expect: float | None = None) -> dict:
    """Read native JSON, including per-trial errors: CLI exit alone is insufficient."""
    from harbor.models.job.result import JobResult
    from harbor.models.trial.result import TrialResult

    job = JobResult.model_validate_json((directory / "result.json").read_text())
    stats = job.stats
    if (
        not job.finished_at
        or job.n_total_trials < 1
        or stats.n_completed_trials != job.n_total_trials
        or stats.n_errored_trials
        or stats.n_running_trials
        or stats.n_pending_trials
        or stats.n_cancelled_trials
    ):
        raise ValueError("Job is incomplete or has infrastructure errors; inspect Harbor logs.")
    paths = sorted(directory.glob("*/result.json"))
    if len(paths) != job.n_total_trials:
        raise ValueError("Expected one native trial result for every completed trial.")
    trials = []
    for path in paths:
        trial = TrialResult.model_validate_json(path.read_text())
        if trial.exception_info or not trial.finished_at or not trial.verifier_result:
            raise ValueError(f"{path.parent.name}: missing verification or infrastructure error.")
        rewards = trial.verifier_result.rewards
        if not rewards or "overall" not in rewards or not math.isfinite(rewards["overall"]):
            raise ValueError(f"{path.parent.name}: missing or invalid overall reward.")
        if expect is not None and rewards["overall"] != expect:
            raise ValueError(f"Expected overall={expect}; got {rewards['overall']}.")
        trials.append({"trial": trial.trial_name, "rewards": rewards})
    return {"job": directory.name, "infrastructure_errors": 0, "trials": trials}


def doctor() -> int:
    checks = {"python_3_12": sys.version_info[:2] == (3, 12)}
    try:
        harbor_executable()
        checks["harbor_0_22_0"] = True
    except ValueError:
        checks["harbor_0_22_0"] = False
    try:
        result = subprocess.run(
            ["docker", "info", "--format", "{{.ServerVersion}}"],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        checks["docker_daemon"] = result.returncode == 0 and bool(result.stdout.strip())
    except (OSError, subprocess.TimeoutExpired):
        checks["docker_daemon"] = False
    print(json.dumps({"checks": checks, "model_calls": 0, "account_checks": False}, indent=2))
    return 0 if all(checks.values()) else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AI Game Bench — Harbor-native local preview")
    parser.add_argument("--repo", type=Path, help="Checkout path (default: current checkout)")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("doctor", help="Check Python, Harbor and Docker; no accounts or models")
    commands.add_parser("tasks", help="List local Harbor tasks")
    platforms = commands.add_parser("platforms", help="List capabilities or read a platform recipe")
    platforms.add_argument("platform", nargs="?", choices=REFERENCE_PLATFORMS)
    platforms.add_argument(
        "--json", action="store_true", help="Print reference metadata; no execution"
    )
    run = commands.add_parser("run", help="Run one free Harbor calibration trial")
    run.add_argument("--task", default=DEFAULT_TASK, help="datasets/-relative task path")
    run.add_argument("--agent", default="oracle")
    run.add_argument("--job-name")
    run.add_argument("--dry-run", action="store_true", help="Print command without execution")
    inspect = commands.add_parser("inspect", help="Validate and summarize a native Harbor job")
    inspect.add_argument("job", type=Path, help="Job directory, relative to checkout or absolute")
    inspect.add_argument("--expect", type=float, choices=[0.0, 1.0], help="Calibration assertion")
    view = commands.add_parser("view", help="Open the native Harbor Viewer, bound to localhost")
    view.add_argument("--port", type=int, default=8080)
    submission = commands.add_parser(
        "submission", help="Prepare/check public evidence; never uploads"
    )
    subcommands = submission.add_subparsers(dest="submission_command", required=True)
    subcommands.add_parser("policies", help="List versioned public result policies")
    schema = subcommands.add_parser("schema", help="Print a JSON Schema for agents")
    schema.add_argument(
        "kind",
        choices=["manifest", "event", "policy", "score-addendum", "evaluation-configuration"],
    )
    initialize = subcommands.add_parser("init", help="Create an explicitly unapproved local draft")
    initialize.add_argument("directory", type=Path)
    initialize.add_argument("--id", required=True)
    initialize.add_argument("--policy", required=True)
    validate = subcommands.add_parser("validate", help="Check an evidence package, offline")
    validate.add_argument("directory", type=Path)
    validate_all = subcommands.add_parser(
        "validate-all", help="Check submissions/<id>/rNNN packages"
    )
    validate_all.add_argument("directory", type=Path, nargs="?", default=Path("submissions"))
    summarize = subcommands.add_parser(
        "summarize", help="Summarize explicit v0.2 packages offline; not gameplay verification"
    )
    summarize.add_argument("directories", type=Path, nargs="+")
    summarize.add_argument("--expected-attempts", type=int, required=True)
    prepare = subcommands.add_parser(
        "prepare", help="Copy an allowlisted public package; no Git/network"
    )
    prepare.add_argument("directory", type=Path)
    prepare.add_argument("--output", type=Path, required=True)
    prepare.add_argument("--confirm-public", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "doctor":
            return doctor()
        if args.command == "platforms":
            if args.platform:
                root = repository_root(args.repo)
                directory = root / "platforms" / args.platform
                if args.json:
                    record = json.loads((directory / "integration.json").read_text())
                    print(json.dumps(record, ensure_ascii=False, indent=2))
                else:
                    print((directory / "README.md").read_text())
                return 0
            if args.json:
                raise ValueError("Choose a platform for --json, e.g. agb platforms mopan --json.")
            for name, status, note in PLATFORMS:
                print(f"{name:14} {status:16} {note}")
            print("\nRead a reference: agb platforms <name> (never starts a paid run).")
            return 0
        root = repository_root(args.repo)
        if args.command == "submission":
            from ai_game_bench import submissions
            from ai_game_bench.score_addenda import ScoreAddendum
            from ai_game_bench.submission_models import (
                EvaluationConfiguration,
                Event,
                Policy,
                Submission,
            )

            action = args.submission_command
            if action == "schema":
                record = {
                    "manifest": Submission,
                    "event": Event,
                    "policy": Policy,
                    "score-addendum": ScoreAddendum,
                    "evaluation-configuration": EvaluationConfiguration,
                }[args.kind].model_json_schema()
            elif action == "policies":
                record = []
                for path in sorted((root / "policies").glob("*.json")):
                    policy, checksum, _ = submissions.load_policy(root, path.stem)
                    record.append(
                        {
                            "id": policy.id,
                            "sha256": checksum,
                            "task": policy.task.path,
                            "limitations": policy.limitations,
                        }
                    )
            elif action == "init":
                record = submissions.initialize(root, args.directory, args.policy, args.id)
            elif action == "prepare":
                record = submissions.prepare(
                    args.directory, root, args.output, confirmed=args.confirm_public
                )
            elif action == "validate-all":
                record = submissions.validate_tree(args.directory, root)
            elif action == "summarize":
                from ai_game_bench.measurements import summarize

                record = summarize(args.directories, root, args.expected_attempts)
            else:
                record = submissions.validate(args.directory, root)
            print(json.dumps(record, ensure_ascii=False, indent=2))
            return 2 if isinstance(record, dict) and record.get("structure_valid") is False else 0
        if args.command == "tasks":
            for path in sorted((root / "datasets").glob("*/*/task.toml")):
                config = tomllib.loads(path.read_text())
                print(f"{path.parent.relative_to(root / 'datasets')}  {config['task']['version']}")
            return 0
        if args.command == "inspect":
            print(json.dumps(inspect_job(root / args.job, args.expect), indent=2))
            return 0
        env = {**os.environ, "HARBOR_TELEMETRY": "0"}
        if args.command == "view":
            if not 1024 <= args.port <= 65535:
                raise ValueError("Viewer port must be between 1024 and 65535.")
            return subprocess.run(
                [
                    harbor_executable(),
                    "view",
                    str(root / "jobs"),
                    "--host",
                    "127.0.0.1",
                    "--port",
                    str(args.port),
                ],
                cwd=root,
                env=env,
                check=False,
            ).returncode
        name = args.job_name or (
            f"agb-{args.agent}-{datetime.now(UTC):%Y%m%dT%H%M%S}-{uuid4().hex[:8]}"
        )
        command = run_command(root, args.task, args.agent, name)
        print(f"HARBOR_TELEMETRY=0 {shlex.join(command)}", flush=True)
        if args.dry_run:
            return 0
        result = subprocess.run(command, cwd=root, env=env, check=False)
        if result.returncode:
            return result.returncode
        print(json.dumps(inspect_job(root / "jobs" / name), indent=2))
        return 0
    except (ValueError, OSError) as exc:
        print(f"agb: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
