"""Integrity of the public pilot snapshot, not gameplay verification."""

import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
COLLECTION = ROOT / "reports/007-web-3d-racing"


def read(path):
    return json.loads(path.read_text())


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def test_complete_export_allowlist_and_hashes():
    inventory = read(COLLECTION / "export-manifest.json")
    folders = [
        COLLECTION,
        ROOT / "submissions/mopan-racing-20261103/r001",
        ROOT / "submissions/wanaka-racing-20261103/r001",
    ]
    actual = {
        str(path.relative_to(ROOT))
        for folder in folders
        for path in folder.rglob("*")
        if path.is_file() and path.name != "export-manifest.json"
    }
    assert actual == {entry["path"] for entry in inventory["files"]}
    for entry in inventory["files"]:
        path = ROOT / entry["path"]
        assert path.resolve().is_relative_to(ROOT)
        assert not path.is_symlink()
        blob = path.read_bytes()
        assert len(blob) == entry["bytes"]
        assert hashlib.sha256(blob).hexdigest() == entry["sha256"]
        assert len(blob) <= 2 * 1024 * 1024


def test_selected_scores_recompute_without_hiding_earlier_generation():
    data = read(COLLECTION / "results.json")
    policy = read(ROOT / "policies/racing-3d-browser-pilot-v2.json")
    assert data["total_creation_attempts"] == len(data["results"]) == 4
    assert data["selected_attempts"] == ["mopan", "wanaka", "codex"]
    for run in data["results"]:
        criteria = {c["id"]: c for c in run["criteria"]}
        points = sum(c["weighted_points"] for c in criteria.values())
        assert run["diagnostic_score"]["total"] == pytest.approx(points)
        assert run["official_benchmark_score"] is None
        if not run["selected"]:
            assert run["id"] == "mopan-first"
            assert points == 29
            continue
        seconds = run["timing"].get("agent_execution_seconds")
        if seconds is None:
            seconds = run["timing"]["accepted_to_observed_delivery_seconds"]
        rating = round(10 * max(0, min(1, (3600 - seconds) / 3300)), 6)
        time = round(rating * 3, 6)
        assert criteria["delivery-time"]["weighted_points"] == time
        gated = all(
            criteria[c]["status"] == "passed" for c in policy["time_score"]["required_passes"]
        )
        assert run["frozen_protocol_diagnostic_score"]["total"] == pytest.approx(
            points - time + (time if gated else 0)
        )


@pytest.mark.parametrize("key", ["mopan", "wanaka", "codex", "mopan-first"])
def test_observation_references_and_unchanged_selected_images(key):
    run = next(r for r in read(COLLECTION / "results.json")["results"] if r["id"] == key)
    folder = ROOT / run["evidence_path"]
    events = rows(folder / "evaluation.jsonl")
    ids = {e["id"] for e in events} | {e["id"] for e in rows(folder / "creation.jsonl")}
    for criterion in run["criteria"]:
        if key == "codex":
            assert all(i.removeprefix("codex-") in ids for i in criterion["observation_ids"])
        else:
            assert set(criterion["observation_ids"]) <= ids
    for index in folder.glob("*-image-index.json"):
        for image in read(index):
            if image["path"] is None:
                assert image["omission"]
            else:
                path = folder / image["path"]
                assert hashlib.sha256(path.read_bytes()).hexdigest() == image["source_sha256"]


def test_public_scores_do_not_imply_policy_or_replay_acceptance():
    data = read(COLLECTION / "results.json")
    codex = next(r for r in data["results"] if r["id"] == "codex")
    assert codex["frozen_protocol_diagnostic_score"]["total"] == 55.5
    assert codex["diagnostic_score"]["total"] == 83.143281
    assert codex["artifact"]["public_play_url"] is None
    assert data["public_submission_acceptance"] == "not_yet_reviewed"
    publication = read(COLLECTION / "publication.json")
    assert publication["games"]["wanaka"]["access"] != "anonymous_play_verified_in_chrome_incognito"
