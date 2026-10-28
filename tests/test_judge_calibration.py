from __future__ import annotations

import asyncio
import hashlib
import importlib.util
import io
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from harbor.models.task.task import Task

from ai_game_bench.calibration import audit_tool_events, prepare, summarize
from ai_game_bench.judge_agent import CodexGameplayJudge, compact_event

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"calibration/judge-v1/{name}.py")
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def test_preparation_is_opaque_balanced_offline_and_harbor_owned(tmp_path):
    output = tmp_path / "plan"
    plan = prepare(ROOT, output, "test-model", "high")
    assert plan["expected_trials"] == len(plan["cases"]) == 16
    assert sum(c["expected_status"] == "failed" for c in plan["cases"]) == 8
    assert len({c["id"] for c in plan["cases"]}) == 16
    config = json.loads((output / "job.json").read_text())
    assert config["n_attempts"] == 1 and config["retry"]["max_retries"] == 0
    assert config["agents"][0]["kwargs"]["allow_model_calls"] is False
    prompts = {}
    for case in plan["cases"]:
        task = output / "tasks" / case["id"]
        Task(task)
        prompt = (task / "instruction.md").read_text()
        key = case["game"], case["criterion"]
        assert prompt == prompts.setdefault(key, prompt)
        for forbidden in ("cosmetic-jump", "decorative-platform", "hud-only-speed", "no-brakes"):
            assert forbidden not in prompt and forbidden not in case["id"]
        html = (task / "environment/fixture/index.html").read_text()
        assert "?game=" not in html and "defect=" not in html
        assert not list((task / "environment").rglob("*answer*"))
        answer = json.loads((task / "tests/answer.json").read_text())
        assert answer["expected_status"] == case["expected_status"]
    with pytest.raises(ValueError, match="new directory"):
        prepare(ROOT, output, "test-model", "high")


def test_model_calls_require_explicit_configuration(tmp_path):
    with pytest.raises(ValueError, match="allow_model_calls"):
        CodexGameplayJudge(logs_dir=tmp_path, model_name="test-model")


@pytest.mark.parametrize("method", ["item/started", "item/completed"])
@pytest.mark.parametrize("kind", ["imageView", "commandExecution", "mcpToolCall"])
def test_disallowed_native_tools_abort_the_evaluator(tmp_path, method, kind):
    async def read():
        return json.dumps({"method": method, "params": {"item": {"type": kind}}}).encode()

    agent = CodexGameplayJudge(logs_dir=tmp_path, model_name="test-model", allow_model_calls=True)
    agent._proc = SimpleNamespace(stdout=SimpleNamespace(readline=read))
    agent._events = io.StringIO()
    with pytest.raises(RuntimeError, match="disallowed tool"):
        asyncio.run(agent._read())


@pytest.mark.parametrize(
    "action",
    [
        {"action": "navigate", "url": "file:///etc/passwd"},
        {"action": "hold", "keys": ["; cat /fixture/game.js"]},
        {"action": "hold", "duration_ms": 999999},
        {"action": "click", "x": -1, "y": 200},
        {"action": "observe", "script": "return window.state"},
        {"action": "wait", "frames": 1000},
        {"action": "hold", "duration_ms": True},
    ],
)
def test_browser_bridge_rejects_non_ui_access_and_unbounded_actions(action):
    with pytest.raises(ValueError):
        module("bridge").validate_action(action)


@pytest.fixture
def evidence(tmp_path):
    digest = hashlib.sha256(b"fixture-image-bytes").hexdigest()
    (tmp_path / "a.png").write_bytes(b"fixture-image-bytes")
    (tmp_path / "b.png").write_bytes(b"fixture-image-bytes")
    trace = {
        "page_errors": [],
        "events": [
            {"id": "frame-1", "kind": "observation", "file": "a.png", "sha256": digest},
            {"id": "action-1", "kind": "action", "action": "hold"},
            {"id": "frame-2", "kind": "observation", "file": "b.png", "sha256": digest},
        ],
    }
    judgement = {
        "status": "failed",
        "reason": "Observed no movement after input.",
        "evidence_ids": ["frame-1", "frame-2"],
    }
    return tmp_path, trace, judgement


def test_fault_detection_and_abstention_are_distinct(evidence):
    path, trace, verdict = evidence
    grade = module("verify").grade
    assert grade(verdict, trace, "failed", path)["correct"]
    verdict["status"] = "not_tested"
    result = grade(verdict, trace, "failed", path)
    assert result["not_tested"] and not result["correct"] and not result["false_pass"]
    verdict["status"] = "passed"
    assert grade(verdict, trace, "failed", path)["false_pass"]


def test_missing_tampered_and_source_paths_cannot_support_verdict(evidence):
    path, trace, verdict = evidence
    verdict["evidence_ids"] = ["invented"]
    with pytest.raises(ValueError, match="nonexistent"):
        module("verify").grade(verdict, trace, "failed", path)
    verdict["evidence_ids"] = ["frame-1", "frame-2"]
    (path / "a.png").write_text("changed")
    with pytest.raises(ValueError, match="hash"):
        module("verify").grade(verdict, trace, "failed", path)
    trace["events"][0]["file"] = "../outside.png"
    with pytest.raises(ValueError, match="outside"):
        module("verify").grade(verdict, trace, "failed", path)


def test_infrastructure_error_is_not_judge_failure(evidence):
    path, trace, verdict = evidence
    trace["page_errors"] = ["Browser crashed"]
    with pytest.raises(RuntimeError, match="Invalid measurement"):
        module("verify").grade(verdict, trace, "failed", path)


def test_report_keeps_missing_and_invalid_trials_visible(tmp_path):
    plan = {
        "kind": "development",
        "model": "test-model",
        "effort": "high",
        "cases": [
            {
                "id": "a",
                "game": "racing",
                "criterion": "braking",
                "variant": "none",
                "expected_status": "passed",
            },
            {
                "id": "b",
                "game": "racing",
                "criterion": "braking",
                "variant": "none",
                "expected_status": "passed",
            },
        ],
    }
    (tmp_path / "plan.json").write_text(json.dumps(plan))
    trial = tmp_path / "job/trial-a"
    trial.mkdir(parents=True)
    (trial.parent / "result.json").write_text("{}")
    (trial / "result.json").write_text(
        json.dumps(
            {
                "task_name": "agb-calibration/a",
                "exception_info": {"exception_type": "AgentTimeoutError"},
            }
        )
    )
    result = summarize(tmp_path / "plan.json", tmp_path / "job")
    assert result["recorded_trials"] == 1 and result["missing_cases"] == ["b"]
    assert result["infrastructure_errors"] == 1 and result["valid_trials"] == 0
    assert result["correct"] == result["false_failures"] == 0


def test_inline_images_are_not_duplicated_in_native_log():
    event = {"imageUrl": "data:image/png;base64,YQ==", "other": "unchanged"}
    result = compact_event(event)
    assert result["other"] == "unchanged" and "inline_image_sha256" in result["imageUrl"]


@pytest.fixture
def report_inputs(tmp_path):
    plan = prepare(ROOT, tmp_path / "plan", "test-model", "high")
    jobs = [tmp_path / "first", tmp_path / "remaining"]
    for job in jobs:
        job.mkdir()
        (job / "result.json").write_text("{}")
    for i, case in enumerate(plan["cases"]):
        trial = jobs[i % 2] / case["id"]
        (trial / "agent").mkdir(parents=True)
        (trial / "verifier").mkdir()
        metadata = {
            "requested_model": "test-model",
            "resolved_model": "test-model",
            "effort": "high",
            "instruction_sha256": case["instruction_sha256"],
            "adapter_sha256": "adapter",
            "codex_version": "version",
            "tool_schema_sha256": "tools",
            "thread_id": f"thread-{i}",
        }
        (trial / "result.json").write_text(
            json.dumps({"task_name": case["id"], "agent_result": {"metadata": metadata}})
        )
        (trial / "agent/judgement.json").write_text(json.dumps({"status": case["expected_status"]}))
        (trial / "agent/codex-events.jsonl").write_text(
            json.dumps(
                {"direction": "receive", "method": "item/tool/call", "params": {"tool": "game_act"}}
            )
            + "\n"
        )
        (trial / "verifier/details.json").write_text(
            json.dumps(
                {
                    "expected_status": case["expected_status"],
                    "observed_status": case["expected_status"],
                    "correct": True,
                    "false_pass": False,
                    "false_failure": False,
                    "not_tested": False,
                }
            )
        )
    return tmp_path / "plan/plan.json", jobs


def test_report_combines_jobs_without_losing_denominators(report_inputs):
    plan, jobs = report_inputs
    report = summarize(plan, jobs)
    assert report["valid_trials"] == report["correct"] == 16
    assert report["repeat_agreements"] == report["repeat_pairs"] == 8
    assert report["working_denominator"] == report["fault_denominator"] == 8
    assert report["independent_threads_recorded"] == 16
    with pytest.raises(ValueError, match="Duplicate trial"):
        summarize(plan, [*jobs, jobs[0]])
    with pytest.raises(ValueError, match="native Harbor"):
        summarize(plan, [jobs[0] / "missing"])


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("resolved_model", "other-model", "model, effort"),
        ("effort", "low", "model, effort"),
        ("instruction_sha256", "other", "model, effort"),
        ("tool_schema_sha256", "new-tools", "different evaluator"),
        ("adapter_sha256", "new-adapter", "different evaluator"),
    ],
)
def test_report_does_not_pool_incompatible_judges(report_inputs, field, value, message):
    plan, jobs = report_inputs
    path = next(jobs[0].glob("*/result.json"))
    native = json.loads(path.read_text())
    native["agent_result"]["metadata"][field] = value
    path.write_text(json.dumps(native))
    with pytest.raises(ValueError, match=message):
        summarize(plan, jobs)


def test_report_rejects_reused_context_and_inconsistent_flags(report_inputs):
    plan, jobs = report_inputs
    paths = sorted(jobs[0].glob("*/result.json"))
    native, other = (json.loads(p.read_text()) for p in paths[:2])
    native["agent_result"]["metadata"]["thread_id"] = other["agent_result"]["metadata"]["thread_id"]
    paths[0].write_text(json.dumps(native))
    with pytest.raises(ValueError, match="reused"):
        summarize(plan, jobs)
    native["agent_result"]["metadata"]["thread_id"] = "fresh-thread"
    paths[0].write_text(json.dumps(native))
    detail_path = paths[0].parent / "verifier/details.json"
    details = json.loads(detail_path.read_text())
    details["correct"] = False
    detail_path.write_text(json.dumps(details))
    with pytest.raises(ValueError, match="flags disagree"):
        summarize(plan, jobs)


def test_access_audit_rejects_native_file_access_and_retains_warnings(tmp_path):
    path = tmp_path / "events.jsonl"
    events = [
        {"method": "item/tool/call", "params": {"tool": "game_act"}},
        {"method": "configWarning", "params": {"message": "Ignored configuration"}},
        {"method": "item/completed", "params": {"item": {"type": "imageView"}}},
    ]
    path.write_text("\n".join(json.dumps({"direction": "receive", **e}) for e in events))
    result = audit_tool_events(path)
    assert not result["valid"] and result["tools_used"] == {"game_act": 1}
    assert result["warnings"] == [{"message": "Ignored configuration"}]
    assert "imageView" in result["issues"][0]


def test_evidence_review_is_bound_to_native_result_without_overriding_verdict(report_inputs):
    plan, jobs = report_inputs
    raw = summarize(plan, jobs)
    first = raw["records"][0]
    review = {
        "schema_version": "judge-evidence-review/0.1",
        "reviewer": "test reviewer",
        "blind": False,
        "scope": "cited screenshots",
        "records": [
            {
                "case_id": first["id"],
                "native_result_sha256": first["native_result_sha256"],
                "finding": "unsupported",
                "note": "Verdict was correct but evidence weak.",
            }
        ],
    }
    path = plan.parent / "review.json"
    path.write_text(json.dumps(review))
    combined = summarize(plan, jobs, path)
    assert combined["correct"] == 16
    assert combined["evidence_review_counts"] == {"unsupported": 1, "not_performed": 15}
    review["records"][0]["native_result_sha256"] = "stale"
    path.write_text(json.dumps(review))
    with pytest.raises(ValueError, match="different native result"):
        summarize(plan, jobs, path)
