"""Invented captures exercise export validation, not gameplay or authenticity."""

import copy
import json
import shutil
from pathlib import Path

import pytest

from ai_game_bench import submissions as s
from ai_game_bench.artifact_review import trial
from ai_game_bench.cli import main
from ai_game_bench.review_packages import SCHEMA, STANDARD, TASK_REFERENCES

ROOT = Path(__file__).resolve().parents[1]


def event(seq, name, at, *, artifact=None):
    return {
        "seq": seq,
        "id": name,
        "at": at,
        "kind": "captured_observation",
        "detail": "Fictional capture for format testing only.",
        "evidence": ["observations.txt"],
        "artifact_id": artifact,
    }


def seal(path, manifest):
    manifest["files"] = [
        {"path": f.name, "sha256": s.digest(f.read_bytes()), "bytes": f.stat().st_size}
        for f in sorted(path.iterdir())
        if f.name != "manifest.json"
    ]
    (path / "manifest.json").write_bytes(s.encode(manifest))


@pytest.fixture
def package(tmp_path):
    path = tmp_path / "draft"
    path.mkdir()
    game = "tetris"
    _, task_hash, prompt = s.load_policy(ROOT, TASK_REFERENCES[game])
    raw = (ROOT / STANDARD).read_bytes()
    policy = json.loads(raw)
    (path / "prompt.txt").write_text(prompt)
    (path / "observations.txt").write_text("Synthetic receipts, never real game evidence.\n")
    creation = [
        event(1, "before", "2026-01-01T00:00:00Z"),
        event(2, "after", "2026-01-01T00:00:01Z"),
        event(3, "final", "2026-01-01T00:05:00Z", artifact="build-1"),
    ]
    evaluation = [event(1, "observed", "2026-01-01T00:05:10Z", artifact="build-1")]
    for name, rows in [("creation.jsonl", creation), ("evaluation.jsonl", evaluation)]:
        (path / name).write_text("".join(json.dumps(row) + "\n" for row in rows))
    assessment = {
        "schema_version": "artifact-review-assessment/1",
        "assessed_at": "2026-01-01T00:06:00Z",
        "mechanics": {},
        "experience": {},
        "time": {
            "seconds": 300.0,
            "started_at": "2026-01-01T00:00:00Z",
            "finished_at": "2026-01-01T00:05:00Z",
            "start_before_event": "before",
            "start_after_event": "after",
            "finish_event": "final",
            "reason": "Synthetic interval",
        },
    }
    for group, names, rating in [
        ("mechanics", policy["games"][game]["mechanics"], 10),
        ("experience", policy["experience"], 8),
    ]:
        assessment[group] = {
            name: {
                "status": "observed",
                "rating": rating,
                "reason": "Synthetic",
                "evidence_events": ["observed"],
            }
            for name in names
        }
    manifest = {
        "schema_version": SCHEMA,
        "id": "synthetic-review",
        "revision": 1,
        "kind": "synthetic_example",
        "author": "Synthetic",
        "affiliation": "None",
        "source_ref": "fictional-run",
        "source_manifest_sha256": "0" * 64,
        "series": {
            "id": "fictional",
            "round_id": "r01",
            "comparator_round_id": None,
            "selection": "One fictional record, not a real trial",
            "change": "None",
        },
        "game": game,
        "outcome": "delivered",
        "scoring_policy_sha256": s.digest(raw),
        "task_reference_sha256": task_hash,
        "prompt_file": "prompt.txt",
        "prompt_sha256": s.digest(prompt.encode()),
        "prompt_trailing_newline_omitted": False,
        "creator": {
            "platform": "synthetic",
            "harness_version": None,
            "model": None,
            "model_source": "unknown",
            "effort": None,
        },
        "environment": "Synthetic",
        "creation_conditions": "Not a creation-policy-compliant run",
        "evaluator": "Synthetic",
        "creation_context_hidden": False,
        "artifact": {
            "id": "build-1",
            "build_version": None,
            "url": None,
            "access": "unpublished",
            "note": "Fictional inaccessible artifact",
        },
        "creation": "creation.jsonl",
        "evaluation": "evaluation.jsonl",
        "assessment": "assessment.json",
        "files": [],
        "external_evidence": [],
        "costs": [
            {
                "kind": "unknown",
                "component": "creator",
                "amount": None,
                "currency": None,
                "basis": "Unknown",
                "evidence": [],
            }
        ],
        "publication": {
            "public_release_confirmed": False,
            "rights_confirmed": False,
            "sensitive_data_checked": False,
            "all_attempts_disclosed": False,
            "license": "CC0-1.0",
            "redactions": [],
            "capture_gaps": [],
            "limitations": ["Fictional data, not gameplay verification"],
        },
    }
    recalculate(path, manifest, assessment)
    return path, manifest, assessment


def recalculate(path, manifest, assessment):
    row = {
        "id": manifest["id"],
        "platform": manifest["creator"]["platform"],
        "game": manifest["game"],
        "outcome": "delivered",
        "time": {
            "seconds": assessment["time"]["seconds"],
            "reason": "Synthetic",
            "evidence": ["final"],
        },
    }
    for group in ["mechanics", "experience"]:
        row[group] = {
            key: dict(item, evidence=item["evidence_events"])
            for key, item in assessment[group].items()
        }
    assessment["computed"] = trial(row, json.loads((ROOT / STANDARD).read_bytes()))
    (path / "assessment.json").write_bytes(s.encode(assessment))
    seal(path, manifest)


def release(manifest):
    for key in [
        "public_release_confirmed",
        "rights_confirmed",
        "sensitive_data_checked",
        "all_attempts_disclosed",
    ]:
        manifest["publication"][key] = True


def test_unapproved_draft_is_checkable_but_cannot_be_released(package, tmp_path):
    path, manifest, _ = package
    before = (path / "manifest.json").read_bytes()
    result = s.validate(path, ROOT, draft=True)
    assert result["draft_valid"] and not result["structure_valid"]
    assert result["publication_ready"] is False
    assert result["retrospective_score"]["points"] == 96
    assert s.validate(path, ROOT)["errors"][0]["code"] == "publication"
    with pytest.raises(s.InvalidSubmission, match="confirmations"):
        s.prepare(path, ROOT, tmp_path / "output", confirmed=True)
    assert not (tmp_path / "output").exists()
    assert (path / "manifest.json").read_bytes() == before
    assert all(
        not manifest["publication"][k] for k in ["public_release_confirmed", "rights_confirmed"]
    )


def test_missing_stability_keeps_lower_bound_without_renormalizing(package):
    path, m, a = package
    a["experience"]["visual_stability"].update(status="unobserved", rating=None, evidence_events=[])
    recalculate(path, m, a)
    result = s.validate(path, ROOT, draft=True)["retrospective_score"]
    assert result["points"] == 92.8 and result["upper"] == 96.8
    assert result["eligible_score"] is None


@pytest.mark.parametrize(
    "fault",
    [
        "time",
        "negative_interval",
        "future_assessment",
        "self_reference",
        "missing_reference",
        "different_artifact",
        "duplicate_id",
        "total",
        "policy",
        "prompt",
        "cost",
        "secret",
        "signed_url",
        "fake_public_access",
        "unlisted",
        "hash",
        "symlink",
        "extra_field",
    ],
)
def test_rejects_inconsistent_or_unsafe_drafts(package, fault):
    path, m, a = package
    if fault == "time":
        a["time"]["seconds"] = 1.0
    if fault == "negative_interval":
        a["time"]["started_at"] = "2026-01-01T00:10:00Z"
    if fault == "future_assessment":
        a["assessed_at"] = "2026-01-01T00:00:00Z"
    if fault == "missing_reference":
        a["mechanics"]["opens"]["evidence_events"] = ["absent"]
    if fault == "total":
        a["computed"]["points"] = 100.0
    if fault == "policy":
        m["scoring_policy_sha256"] = "0" * 64
    if fault == "prompt":
        (path / "prompt.txt").write_text("Wrong prompt")
        m["prompt_sha256"] = s.digest((path / "prompt.txt").read_bytes())
    if fault == "cost":
        m["costs"][0]["amount"] = 0.0
    if fault == "secret":
        e = json.loads((path / "evaluation.jsonl").read_text())
        e["detail"] = "/Users/private/account/data"
        (path / "evaluation.jsonl").write_text(json.dumps(e).replace("/", "\\u002f") + "\n")
    if fault == "signed_url":
        m["artifact"]["url"] = "https://example.org/play?token=private"
    if fault == "fake_public_access":
        m["artifact"]["access"] = "publicly_accessible"
    if fault == "extra_field":
        m["automatically_accepted"] = True
    if fault in {"self_reference", "different_artifact", "duplicate_id"}:
        e = json.loads((path / "evaluation.jsonl").read_text())
        if fault == "self_reference":
            e["evidence"] = ["evaluation.jsonl"]
        if fault == "different_artifact":
            e["artifact_id"] = "another-build"
        if fault == "duplicate_id":
            e["id"] = "before"
        (path / "evaluation.jsonl").write_text(json.dumps(e) + "\n")
    (path / "assessment.json").write_bytes(s.encode(a))
    seal(path, m)
    if fault == "unlisted":
        (path / "extra.txt").write_text("unlisted")
    if fault == "hash":
        (path / "observations.txt").write_text("changed")
    if fault == "symlink":
        original = path / "observations.txt"
        original.rename(path.parent / "outside.txt")
        original.symlink_to(path.parent / "outside.txt")
    result = s.validate(path, ROOT, draft=True)
    assert result["structure_valid"] is False and result["errors"], (fault, result)


def test_prepare_preserves_exact_receipt_and_cannot_overwrite(package, tmp_path):
    path, m, _ = package
    release(m)
    seal(path, m)
    result = s.prepare(path, ROOT, tmp_path / "output", confirmed=True)
    assert result["structure_valid"] and result["review_status"] == "unverified"
    assert result["uploaded"] is False
    raw = (tmp_path / "output/manifest.json").read_bytes()
    assert result["manifest_sha256"] == s.digest(raw)
    with pytest.raises(s.InvalidSubmission, match="Never overwrite"):
        s.prepare(path, ROOT, tmp_path / "output", confirmed=True)


def test_noncanonical_manifest_hash_is_actual_bytes(package):
    path, m, _ = package
    release(m)
    raw = json.dumps(m).encode()
    (path / "manifest.json").write_bytes(raw)
    assert s.validate(path, ROOT)["manifest_sha256"] == s.digest(raw)


def test_new_format_uses_existing_tree_review_and_rejects_rewriting(package, tmp_path):
    path, m, _ = package
    root = tmp_path / "trusted"
    for dirname in ["scoring", "policies", "protocols"]:
        shutil.copytree(ROOT / dirname, root / dirname)
    target = root / "submissions/synthetic-review/r001"
    release(m)
    m["kind"] = "result"  # In-memory synthetic test only, never committed as result data.
    seal(path, m)
    shutil.copytree(path, target)
    result = s.validate_tree(root / "submissions", root)
    assert result["structure_valid"] and result["count"] == 1
    incoming = tmp_path / "incoming"
    shutil.copytree(root / "submissions", incoming)
    (incoming / "synthetic-review/r001/observations.txt").write_text("replacement")
    assert s.validate_tree(incoming, root)["errors"][0]["code"] == "immutable_revision"


def test_cli_draft_exit_does_not_approve(package, capsys):
    path, m, _ = package
    before = copy.deepcopy(m)
    assert main(["--repo", str(ROOT), "submission", "check-draft", str(path)]) == 0
    assert json.loads(capsys.readouterr().out)["publication_ready"] is False
    assert json.loads((path / "manifest.json").read_text()) == before
    assert main(["--repo", str(ROOT), "submission", "validate", str(path)]) == 2


@pytest.mark.parametrize("game", ["racing", "platformer"])
def test_other_tasks_preserve_declared_prompt_newline_omission(package, game):
    path, m, a = package
    _, checksum, prompt = s.load_policy(ROOT, TASK_REFERENCES[game])
    actual = prompt.rstrip("\r\n").encode()
    (path / "prompt.txt").write_bytes(actual)
    m.update(
        game=game,
        task_reference_sha256=checksum,
        prompt_sha256=s.digest(actual),
        prompt_trailing_newline_omitted=True,
    )
    policy = json.loads((ROOT / STANDARD).read_bytes())
    a["mechanics"] = {
        name: {
            "status": "observed",
            "rating": 10,
            "reason": "Synthetic",
            "evidence_events": ["observed"],
        }
        for name in policy["games"][game]["mechanics"]
    }
    recalculate(path, m, a)
    assert s.validate(path, ROOT, draft=True)["draft_valid"]
    m["prompt_trailing_newline_omitted"] = False
    seal(path, m)
    assert s.validate(path, ROOT, draft=True)["errors"][0]["code"] == "prompt"


def test_unknown_timing_is_not_fabricated_or_zero_cost(package):
    path, m, a = package
    for key in a["time"]:
        if key != "reason":
            a["time"][key] = None
    recalculate(path, m, a)
    result = s.validate(path, ROOT, draft=True)
    assert result["draft_valid"]
    assert result["retrospective_score"]["points"] == 66
    assert result["retrospective_score"]["upper"] == 96
    assert result["retrospective_score"]["eligible_score"] is None
