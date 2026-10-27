"""Synthetic, offline tests of measurement arithmetic; never real judge accuracy."""

from __future__ import annotations

import json
import shutil
import socket

import pytest
from test_proposed_game_protocols import (
    ROOT,
    recalculate,
    rewrite_events,
    save,
    synthetic_package,
)

from ai_game_bench import cli
from ai_game_bench import measurements as m
from ai_game_bench import submissions as s

METHODS = ("platformer-browser-pilot-v2", "racing-3d-browser-pilot-v2")


@pytest.fixture(autouse=True)
def offline_only(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Measurements must not call browsers, platforms or models")

    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(socket, "getaddrinfo", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)


def package(tmp_path, method=METHODS[0], seconds=1950, identity="synthetic-run"):
    target, record, policy = synthetic_package(tmp_path, method, seconds)
    record.update(schema_version="public-submission/0.2", id=identity, source_ref=identity)
    data = b"Synthetic public evaluator instructions. No actual game or model was run.\n"
    name = "evaluator-instructions.md"
    (target / name).write_bytes(data)
    record["files"].append({"path": name, "sha256": s.digest(data), "bytes": len(data)})
    record["attempts"][0]["result"].update(
        model="synthetic-judge-version-1",
        configuration={
            "harness_version": "synthetic-harness-1",
            "effort": "synthetic-medium",
            "instructions_file": name,
            "instructions_sha256": s.digest(data),
            "tools": [{"name": "synthetic-input", "version": "1"}],
            "access_mode": "screenshot_only",
            "browser": "synthetic-browser",
            "browser_version": "1",
            "viewport_width": 1280,
            "viewport_height": 800,
            "clock": "realtime",
        },
    )
    save(target, record)
    return target, record, policy


def terminal(target, record, outcome):
    attempt = record["attempts"][0]
    attempt.update(outcome=outcome, artifact=None)
    invalid = outcome in {"auth_failure", "infrastructure_error"}
    for verdict in attempt["result"]["criteria"]:
        verdict.update(
            status="infra_error" if invalid else "not_tested",
            score=None if invalid else 0,
            evidence_events=[],
        )
    attempt["result"]["total"] = None if invalid else 0
    rewrite_events(
        target, record, "creation.jsonl", lambda es: es[-1].update(kind=outcome, artifact_id=None)
    )
    rewrite_events(
        target, record, "evaluation.jsonl", lambda es: [e.update(artifact_id=None) for e in es]
    )


def valid(target):
    report = s.validate(target, ROOT)
    assert report["structure_valid"], report
    assert report["review_status"] == "unverified"
    return report["attempts"][0]


def reject(target, code):
    report = s.validate(target, ROOT)
    assert not report["structure_valid"], report
    assert report["errors"][0]["code"] == code, report


@pytest.mark.parametrize("method", METHODS)
def test_new_versions_preserve_prompts_weights_and_legacy_bytes(method):
    previous = method.replace("-v2", "-v1")
    new, _, prompt = s.load_policy(ROOT, method)
    old, _, old_prompt = s.load_policy(ROOT, previous)
    assert new.schema_version == "public-policy/0.2"
    assert prompt == old_prompt
    assert new.criteria == old.criteria
    assert new.time_score == old.time_score
    assert new.task.rubric_sha256 == old.task.rubric_sha256
    assert new.task.verifier_sha256 != old.task.verifier_sha256
    assert new.measurement.core_criteria == [c.id for c in old.criteria if not c.allow_partial]
    assert new.measurement.evaluation_budget_seconds == 1800
    assert new.measurement.session_limit == 6


@pytest.mark.parametrize("method", METHODS)
@pytest.mark.parametrize("seconds,total", [(30, 100), (300, 100), (1950, 85), (3600, 70)])
def test_delivered_score_unchanged_with_separate_core_success(tmp_path, method, seconds, total):
    target, _, _ = package(tmp_path, method, seconds)
    result = valid(target)
    assert result["recomputed_total"] == total
    assert result["measurement"]["core_success"] is True
    assert result["measurement"]["delivery_success"] is True
    assert result["measurement"]["core_checks"]["passed"] == 9


@pytest.mark.parametrize("method", METHODS)
@pytest.mark.parametrize(
    "outcome", ["timeout", "build_failure", "auth_failure", "infrastructure_error"]
)
def test_non_delivery_and_invalid_measurements_are_different(tmp_path, method, outcome):
    target, record, _ = package(tmp_path, method, 3600)
    terminal(target, record, outcome)
    result = valid(target)
    invalid = outcome in {"auth_failure", "infrastructure_error"}
    assert result["recomputed_total"] == (None if invalid else 0)
    assert result["measurement"]["core_success"] is (None if invalid else False)
    assert result["measurement"]["delivery_success"] is (None if invalid else False)
    assert result["measurement"]["evaluation_completed"] is False


@pytest.mark.parametrize("method", METHODS)
def test_legacy_timeout_remains_unscored(tmp_path, method):
    target, record, _ = synthetic_package(tmp_path, method.replace("-v2", "-v1"))
    terminal(target, record, "timeout")
    result = record["attempts"][0]["result"]
    for verdict in result["criteria"]:
        verdict.update(status="infra_error", score=None)
    result["total"] = None
    save(target, record)
    assert valid(target)["recomputed_total"] is None
    assert "measurement" not in valid(target)


@pytest.mark.parametrize(
    "mutation,code",
    [
        ("early", "timeout"),
        ("no-receipt", "missing_send"),
        ("no-terminal", "timeout"),
        ("fake-failure", "missing_evidence"),
        ("fake-infra", "timeout"),
        ("artifact", "timeout"),
    ],
)
def test_timeout_requires_supported_budget_exhaustion(tmp_path, mutation, code):
    target, record, _ = package(tmp_path, seconds=1200 if mutation == "early" else 3600)
    artifact = record["attempts"][0]["artifact"]
    terminal(target, record, "timeout")
    if mutation == "no-receipt":
        rewrite_events(target, record, "creation.jsonl", lambda es: es[1].update(evidence=[]))
    elif mutation == "no-terminal":
        rewrite_events(target, record, "creation.jsonl", lambda es: es[-1].update(evidence=[]))
    elif mutation == "fake-failure":
        record["attempts"][0]["result"]["criteria"][0]["status"] = "failed"
    elif mutation == "fake-infra":
        record["attempts"][0]["result"]["criteria"][0].update(status="infra_error", score=None)
    elif mutation == "artifact":
        record["attempts"][0]["artifact"] = artifact
    save(target, record)
    reject(target, code)


@pytest.mark.parametrize("status", ["failed", "not_tested"])
def test_high_total_does_not_make_all_core_pass(tmp_path, status):
    target, record, policy = package(tmp_path)
    verdict = next(
        v
        for v in record["attempts"][0]["result"]["criteria"]
        if v["criterion_id"] == "solid-platforms"
    )
    verdict.update(status=status, score=0)
    recalculate(record, policy)
    save(target, record)
    result = valid(target)
    assert result["recomputed_total"] == 77
    assert result["measurement"]["core_success"] is False
    assert result["measurement"]["core_checks"][status] == 1


@pytest.mark.parametrize(
    "change",
    [
        {"access_mode": "instrumented"},
        {"access_mode": "visible_ui"},
        {"clock": "stepped"},
        {"viewport_width": 640},
        {"viewport_height": 720},
        {"instructions_file": None},
        {"instructions_sha256": "0" * 64},
        {"instructions_file": "evaluation.jsonl"},
        {"tools": []},
        {"tools": [{"name": "duplicate", "version": None}] * 2},
    ],
)
def test_configuration_and_access_are_checked(tmp_path, change):
    target, record, _ = package(tmp_path)
    record["attempts"][0]["result"]["configuration"].update(change)
    save(target, record)
    reject(target, "evaluation_configuration")


def test_required_configuration_and_schema_version(tmp_path):
    target, record, _ = package(tmp_path)
    config = record["attempts"][0]["result"].pop("configuration")
    save(target, record)
    reject(target, "evaluation_configuration")
    record["attempts"][0]["result"]["configuration"] = config
    record["schema_version"] = "public-submission/0.1"
    save(target, record)
    reject(target, "schema_version")


@pytest.mark.parametrize("outcome", ["auth_failure", "infrastructure_error"])
def test_late_capture_failure_is_not_forced_into_generation_timeout(tmp_path, outcome):
    target, record, _ = package(tmp_path, seconds=3700)
    terminal(target, record, outcome)
    assert valid(target)["recomputed_total"] is None


def test_human_review_does_not_require_model_or_prompt(tmp_path):
    target, record, _ = package(tmp_path)
    result = record["attempts"][0]["result"]
    result.update(mode="human", model=None)
    result["configuration"].update(
        effort=None,
        harness_version=None,
        instructions_file=None,
        instructions_sha256=None,
        tools=[],
        access_mode="visible_ui",
    )
    save(target, record)
    assert valid(target)["measurement"]["core_success"]


def test_summary_denominators_include_timeout_and_show_exclusions(tmp_path):
    paths = []
    for name in ("pass", "core-fail", "timeout", "build_failure", "auth_failure", "eval-infra"):
        base = tmp_path / name
        base.mkdir()
        target, record, policy = package(
            base,
            seconds=3600 if name == "timeout" else 1950,
            identity="synthetic-" + name.replace("_", "-"),
        )
        if name in {"timeout", "build_failure", "auth_failure"}:
            terminal(target, record, name)
        if name in {"core-fail", "eval-infra"}:
            result = record["attempts"][0]["result"]
            verdict = next(v for v in result["criteria"] if v["criterion_id"] == "solid-platforms")
            if name == "core-fail":
                verdict.update(status="failed", score=0)
                recalculate(record, policy)
            else:
                verdict.update(status="infra_error", score=None)
                result["total"] = None
            save(target, record)
        paths.append(target)
    report = m.summarize(paths, ROOT, expected_attempts=6)
    assert report["review_status"] == "unverified" and len(report["groups"]) == 1
    group = report["groups"][0]
    assert group["recorded_attempts"] == 6
    assert group["delivery"] == {
        "successes": 3,
        "denominator": 5,
        "excluded_measurements": 1,
        "rate": 0.6,
    }
    assert group["core_success"] == {
        "successes": 1,
        "denominator": 4,
        "excluded_measurements": 2,
        "rate": 0.25,
    }
    assert group["total_score"] == {
        "mean": 40.5,
        "scored_attempts": 4,
        "excluded_measurements": 2,
    }
    with pytest.raises(s.InvalidSubmission, match="Selected attempt count"):
        m.summarize(paths[:-1], ROOT, expected_attempts=6)


@pytest.mark.parametrize(
    "field", ["policy", "access", "model", "effort", "blind", "kind", "unknown"]
)
def test_different_measurement_conditions_are_not_pooled(tmp_path, field):
    first, _, _ = package(tmp_path, identity="synthetic-one")
    second_base = tmp_path / "second"
    second_base.mkdir()
    second, record, _ = package(
        second_base, METHODS[1] if field == "policy" else METHODS[0], identity="synthetic-two"
    )
    result = record["attempts"][0]["result"]
    match field:
        case "access":
            result["mode"] = "agent_dom"
            result["configuration"]["access_mode"] = "visible_ui"
        case "model":
            result["model"] = "synthetic-other-model"
        case "effort":
            result["configuration"]["effort"] = "synthetic-high"
        case "blind":
            result["creation_context_hidden"] = True
        case "kind":
            record["kind"] = "result"  # Synthetic unit-test mutation, never a published run.
        case "unknown":
            result["configuration"]["browser_version"] = None
    save(second, record)
    assert len(m.summarize([first, second], ROOT, 2)["groups"]) == 2


@pytest.mark.parametrize("change_id", [False, True])
def test_corrections_and_duplicate_source_runs_are_not_new_attempts(tmp_path, change_id):
    first, record, _ = package(tmp_path)
    second = tmp_path / "duplicate"
    shutil.copytree(first, second)
    record["revision"] = 2
    if change_id:
        record["id"] = "another-submission-same-source"
    save(second, record)
    with pytest.raises(s.InvalidSubmission, match="one revision"):
        m.summarize([first, second], ROOT, 2)


@pytest.mark.parametrize("field", ["model", "effort", "harness_version"])
def test_creator_metadata_corrections_do_not_make_a_new_source_run(tmp_path, field):
    first, record, _ = package(tmp_path)
    second = tmp_path / "corrected-metadata"
    shutil.copytree(first, second)
    record.update(id="corrected-source-description", revision=2)
    record["creator"][field] = "corrected-description"
    save(second, record)
    with pytest.raises(s.InvalidSubmission, match="one revision"):
        m.summarize([first, second], ROOT, 2)


def test_source_ids_are_namespaced_by_platform(tmp_path):
    first, record, _ = package(tmp_path)
    second = tmp_path / "other-platform"
    shutil.copytree(first, second)
    record["id"] = "other-platform-run"
    record["creator"]["platform"] = "other-synthetic-platform"
    save(second, record)
    report = m.summarize([first, second], ROOT, 2)
    assert report["recorded_attempts"] == 2
    assert len(report["groups"]) == 2


def test_legacy_packages_are_not_reinterpreted_by_summary(tmp_path):
    target, _, _ = synthetic_package(tmp_path, METHODS[0].replace("-v2", "-v1"))
    with pytest.raises(s.InvalidSubmission, match="historical v0.1"):
        m.summarize([target], ROOT, 1)


def test_all_invalid_measurements_have_null_rates_not_zero_scores(tmp_path):
    target, record, _ = package(tmp_path)
    terminal(target, record, "infrastructure_error")
    group = m.summarize([target], ROOT, 1)["groups"][0]
    assert group["core_success"] == {
        "successes": 0,
        "denominator": 0,
        "excluded_measurements": 1,
        "rate": None,
    }
    assert group["delivery"]["rate"] is None
    assert group["total_score"]["mean"] is None


def test_identical_unknown_versions_are_not_assumed_comparable(tmp_path):
    paths = []
    for identity in ("synthetic-first", "synthetic-second"):
        directory = tmp_path / identity
        directory.mkdir()
        target, record, _ = package(directory, identity=identity)
        record["attempts"][0]["result"]["configuration"]["browser_version"] = None
        save(target, record)
        paths.append(target)
    groups = m.summarize(paths, ROOT, 2)["groups"]
    assert len(groups) == 2
    assert all(g["configuration_unknowns"] == ["browser_version"] for g in groups)


def test_invalid_package_cannot_enter_summary(tmp_path):
    target, record, _ = package(tmp_path)
    record["attempts"][0]["result"]["total"] = 999
    save(target, record)
    with pytest.raises(s.InvalidSubmission, match="Every selected package must validate"):
        m.summarize([target], ROOT, 1)


@pytest.mark.parametrize(
    "mutation", ["missing-rules", "unknown-core", "duplicate-core", "partial-core"]
)
def test_bad_measurement_rules_are_rejected(tmp_path, mutation):
    for directory in ("protocols", "policies"):
        shutil.copytree(ROOT / directory, tmp_path / directory)
    path = tmp_path / "policies" / f"{METHODS[0]}.json"
    policy = json.loads(path.read_text())
    match mutation:
        case "missing-rules":
            policy.pop("measurement")
        case "unknown-core":
            policy["measurement"]["core_criteria"].append("unknown")
        case "duplicate-core":
            policy["measurement"]["core_criteria"].append("ready")
        case "partial-core":
            policy["measurement"]["core_criteria"].append("readability")
    path.write_bytes(s.encode(policy))
    with pytest.raises(s.InvalidSubmission):
        s.load_policy(tmp_path, METHODS[0])


@pytest.mark.parametrize("method", METHODS)
def test_v2_init_prepare_and_cli_are_offline_and_unapproved(tmp_path, method, capsys):
    draft = tmp_path / "draft"
    s.initialize(ROOT, draft, method, "not-a-run")
    draft_data = json.loads((draft / "manifest.json").read_text())
    assert draft_data["schema_version"] == "public-submission/0.2"
    assert not draft_data["publication"]["public_release_confirmed"]
    assert draft_data["attempts"][0]["result"]["configuration"]["browser_version"] is None
    assert not s.validate(draft, ROOT)["structure_valid"]
    target, _, _ = package(tmp_path, method)
    prepared = tmp_path / "prepared"
    s.prepare(target, ROOT, prepared, confirmed=True)
    assert valid(prepared)["measurement"]["core_success"]
    assert cli.main(["submission", "summarize", str(prepared), "--expected-attempts", "1"]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["groups"][0]["cohort"]["kind"] == "synthetic_example"
    assert cli.main(["submission", "summarize", str(prepared), "--expected-attempts", "2"]) == 2
    assert "attempt count" in capsys.readouterr().err


@pytest.mark.parametrize(
    "name,sha",
    [
        (
            "policies/counter-calibration-v1.json",
            "3e3fb615f6b25562009a8557f8d2cf1e8dc08d301c9b1e948e73e40435a3d975",
        ),
        (
            "policies/tetris-browser-pilot-v1.json",
            "afcc208f35233bb9df8b8e630e39f816a05ce028c91d0bd79cea17ffef4f2ede",
        ),
        (
            "policies/platformer-browser-pilot-v1.json",
            "4e5fb8000b41e19c88de1c3f0e45c35b4dfbfc8d4247b4b5a069df7fc836e68d",
        ),
        (
            "policies/racing-3d-browser-pilot-v1.json",
            "8d61e538ce1467eba19f586fdbe226cacd55f3618c8179db4dd90a7506bddfe5",
        ),
        (
            "scoring/tetris-absolute-v1.json",
            "56d53de71b4d809c4484974cc7a5356461c5742c3cb883eb3bd1db553dc3a278",
        ),
    ],
)
def test_historical_rule_bytes_remain_frozen(name, sha):
    assert s.digest((ROOT / name).read_bytes()) == sha
