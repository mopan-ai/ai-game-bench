"""Offline integration checks for task contracts, not gameplay/evaluator accuracy."""

from __future__ import annotations

import json
import shutil
import socket
import tomllib
from pathlib import Path

import pytest
from test_measurements import package, reject, terminal, valid
from test_proposed_game_protocols import recalculate, save

from ai_game_bench import cli
from ai_game_bench import submissions as s

ROOT = Path(__file__).resolve().parents[1]
SUITE = json.loads((ROOT / "protocols/web-3d-create-v1/suite.json").read_text())
METHODS = tuple(task["policy_id"] for task in SUITE["tasks"])
NEW_METHODS = METHODS[1:]


@pytest.fixture(autouse=True)
def offline_only(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Contract checks must not call a browser, creator or model")

    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(socket, "getaddrinfo", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)


def test_suite_pins_six_distinct_methods_and_reuses_racing():
    assert SUITE["execution"] == "browser_observation"
    assert SUITE["status"] == "proposed"
    assert SUITE["engine_constraint"] is None
    assert SUITE["aggregation"] == "per_task_only"
    assert len(set(METHODS)) == len(SUITE["tasks"]) == 6
    assert METHODS[0] == "racing-3d-browser-pilot-v2"
    assert len({task["genre"] for task in SUITE["tasks"]}) == 6
    for task in SUITE["tasks"]:
        policy, policy_hash, _ = s.load_policy(ROOT, task["policy_id"])
        assert policy_hash == task["policy_sha256"]
        assert task["capabilities"] and task["visual_style"]
        directory = ROOT / "protocols" / policy.task.path
        rubric = json.loads((directory / "rubric.json").read_text())
        raw_policy = json.loads((ROOT / "policies" / f"{task['policy_id']}.json").read_text())
        assert rubric["criteria"] == raw_policy["criteria"]
        assert tomllib.loads((directory / "task.toml").read_text())["protocol"] == {
            "mode": "browser_observation",
            "status": "proposed",
        }
        assert policy.schema_version == "public-policy/0.2"
        assert policy.attempt_limit == 1 and not policy.allow_repairs
        assert policy.timeout_seconds == 3600
        assert policy.measurement.evaluation_budget_seconds == 1800
        assert policy.measurement.session_limit == 6
        assert policy.measurement.clock == "realtime"
        assert set(policy.measurement.allowed_access) == {"visible_ui", "screenshot_only"}
        assert (policy.measurement.viewport_width, policy.measurement.viewport_height) == (
            1280,
            800,
        )
        core = policy.measurement.core_criteria
        assert len(core) == 9
        assert sum(c.weight for c in policy.criteria if c.id in core) == 60
        assert all(c.max_score == 10 for c in policy.criteria)
        assert sum(c.weight for c in policy.criteria) == 100
        assert set(policy.time_score.required_passes) <= set(core)
        with pytest.raises(ValueError, match="existing directory"):
            cli.task_directory(ROOT, task["policy_id"])


@pytest.mark.parametrize("method", NEW_METHODS)
def test_every_core_rule_has_explicit_pass_and_failure_examples(method):
    policy, _, prompt = s.load_policy(ROOT, method)
    assert "3D" in prompt and "浏览器" in prompt
    assert all(name not in prompt.lower() for name in ("mopan", "wanaka", "godot", "three.js"))
    path = ROOT / "protocols" / method
    cases = json.loads((path / "review-cases.json").read_text())
    assert cases["kind"] == "hypothetical_review_cases_not_run_evidence"
    assert len({c["id"] for c in cases["cases"]}) == len(cases["cases"])
    for criterion in policy.measurement.core_criteria:
        assert {
            c["expected"]["status"] for c in cases["cases"] if c["criterion_id"] == criterion
        } >= {"passed", "failed"}
    for case in cases["cases"]:
        assert case["criterion_id"] in policy.measurement.core_criteria
        assert case["observation"] and case["expected"]["reason"]
        assert (
            case["expected"]["score"]
            == {"passed": 10, "failed": 0, "not_tested": 0, "infra_error": None}[
                case["expected"]["status"]
            ]
        )


@pytest.mark.parametrize("method", NEW_METHODS)
@pytest.mark.parametrize("filename", ["instruction.md", "rubric.json", "evaluation.md"])
def test_changed_contract_is_rejected_by_trusted_policy(tmp_path, method, filename):
    for folder in ("policies", "protocols"):
        shutil.copytree(ROOT / folder, tmp_path / folder)
    (tmp_path / "protocols" / method / filename).write_text("Changed contract")
    with pytest.raises(s.InvalidSubmission, match="Frozen task bytes"):
        s.load_policy(tmp_path, method)


@pytest.mark.parametrize("method", NEW_METHODS)
def test_existing_cli_initializes_an_unapproved_v02_draft(tmp_path, method):
    target = tmp_path / "draft"
    s.initialize(ROOT, target, method, "synthetic-init-only")
    manifest = json.loads((target / "manifest.json").read_text())
    assert manifest["schema_version"] == "public-submission/0.2"
    assert manifest["publication"]["public_release_confirmed"] is False
    assert manifest["attempts"][0]["artifact"] is None
    assert manifest["attempts"][0]["result"]["configuration"]["clock"] == "realtime"
    assert (target / "creation.jsonl").read_bytes() == b""
    assert (target / "evaluation.jsonl").read_bytes() == b""


@pytest.mark.parametrize("method", METHODS)
@pytest.mark.parametrize("seconds,total", [(300, 100), (1950, 85), (3600, 70)])
def test_v02_synthetic_export_works_without_claiming_a_gameplay_pass(
    tmp_path, method, seconds, total
):
    target, _, _ = package(tmp_path, method, seconds)
    result = valid(target)
    assert result["recomputed_total"] == total
    assert result["measurement"]["core_checks"]["passed"] == 9


@pytest.mark.parametrize("method", NEW_METHODS)
def test_unproven_gate_cannot_keep_speed_credit(tmp_path, method):
    target, record, policy = package(tmp_path, method, 300)
    original = json.loads(json.dumps(record))
    for gate in policy.time_score.required_passes:
        record = json.loads(json.dumps(original))
        by_id = {c["criterion_id"]: c for c in record["attempts"][0]["result"]["criteria"]}
        by_id[gate].update(status="not_tested", score=0, evidence_events=[])
        recalculate(record, policy)
        save(target, record)
        reject(target, "time_score")
        by_id["delivery-time"].update(status="failed", score=0)
        recalculate(record, policy)
        save(target, record)
        checked = valid(target)
        assert checked["recomputed_total"] < 70
        assert checked["measurement"]["core_success"] is False


@pytest.mark.parametrize("method", NEW_METHODS)
@pytest.mark.parametrize("outcome", ["timeout", "build_failure", "infrastructure_error"])
def test_timeout_failure_and_invalid_measurement_keep_distinct_semantics(tmp_path, method, outcome):
    target, record, _ = package(tmp_path, method, 3600)
    terminal(target, record, outcome)
    result = valid(target)
    assert result["recomputed_total"] == (None if outcome == "infrastructure_error" else 0)
    assert result["measurement"]["core_success"] is (
        None if outcome == "infrastructure_error" else False
    )
