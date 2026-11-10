"""Synthetic arithmetic regressions, not evidence of calibrated game judging."""

import copy
import hashlib
import json
import socket
from pathlib import Path

import pytest

from ai_game_bench.artifact_review import recompute

POLICY = (Path(__file__).resolve().parents[1] / "scoring/three-game-review-v1.json").read_bytes()
RULES = json.loads(POLICY)


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Arithmetic must not open a network connection")

    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)


def fixture():
    observed = {
        "rating": 10,
        "status": "observed",
        "reason": "Synthetic only",
        "evidence": ["synthetic:observation"],
    }
    return {
        "policy_id": RULES["policy_id"],
        "policy_sha256": hashlib.sha256(POLICY).hexdigest(),
        "trials": [
            {
                "id": game,
                "platform": "synthetic",
                "source_run_id": game,
                "game": game,
                "outcome": "delivered",
                "mechanics": {k: copy.deepcopy(observed) for k in cfg["mechanics"]},
                "experience": {k: copy.deepcopy(observed) for k in RULES["experience"]},
                "time": {"seconds": 300, "reason": "Synthetic receipt", "evidence": ["synthetic"]},
            }
            for game, cfg in RULES["games"].items()
        ],
    }


def test_all_complete_uses_exact_task_macro_average():
    data = fixture()
    data["trials"][1]["time"]["seconds"] = 1950
    result = recompute(data, POLICY)
    assert [x["points"] for x in result["trials"]] == pytest.approx([100, 85, 100])
    assert result["platforms"][0]["eligible_score"] == pytest.approx(95)


def test_missing_quality_never_renormalizes_or_becomes_observed_failure():
    data = fixture()
    data["trials"][0]["experience"]["visual_stability"].update(
        status="unobserved", rating=None, reason="No temporal evidence"
    )
    result = recompute(data, POLICY)
    row = result["trials"][0]
    assert (row["points"], row["upper"], row["eligible_score"]) == (96, 100, None)
    assert result["platforms"][0]["points"] == pytest.approx(296 / 3)
    assert result["platforms"][0]["eligible_score"] is None


@pytest.mark.parametrize("outcome", ["infrastructure_error", "owner_held", "unmeasured"])
def test_invalid_task_blocks_total_without_score_zero(outcome):
    data = fixture()
    data["trials"][1].update(
        outcome=outcome, reason="Synthetic access issue", evidence=["synthetic"]
    )
    result = recompute(data, POLICY)
    assert result["trials"][1]["points"] is None
    assert result["platforms"][0]["points"] is None


def test_timeout_kept_in_denominator_and_not_best_of():
    data = fixture()
    timeout = copy.deepcopy(data["trials"][1])
    timeout.update(
        id="racing-second",
        source_run_id="racing-second",
        outcome="generation_timeout",
        capture_functioning=True,
        reason="No delivery",
        evidence=["synthetic"],
    )
    timeout["time"]["seconds"] = 3600
    data["trials"].append(timeout)
    result = recompute(data, POLICY)
    assert result["platforms"][0]["eligible_score"] == pytest.approx((100 + 50 + 100) / 3)
    timeout["capture_functioning"] = False
    with pytest.raises(ValueError, match="Capture failure"):
        recompute(data, POLICY)


def test_missing_gate_preserves_time_measurement_without_awarding_unsupported_points():
    data = fixture()
    row = data["trials"][1]
    row["time"]["seconds"] = 559.239
    row["mechanics"]["acceleration"].update(status="unobserved", rating=None)
    timed = recompute(data, POLICY)["trials"][1]["dimensions"]["time"]
    assert timed["observed_seconds"] == 559.239
    assert timed["points"] == 0 and timed["upper"] == pytest.approx(27.643281818)


def test_proven_blocker_differs_from_missing_gate():
    data = fixture()
    row = data["trials"][0]
    row["mechanics"]["line_clear"]["rating"] = 0
    row["mechanics"]["line_clear_score"].update(
        status="blocked_by_artifact", rating=0, blocked_by="line_clear"
    )
    result = recompute(data, POLICY)["trials"][0]
    assert result["dimensions"]["time"]["upper"] == 0
    assert result["eligible_score"] is not None
    row["mechanics"]["line_clear_score"]["blocked_by"] = "rotate"
    with pytest.raises(ValueError, match="observed failed"):
        recompute(data, POLICY)


def test_boundary_preserves_quality_but_no_time_credit():
    data = fixture()
    row = data["trials"][1]
    row["outcome"] = "deadline_boundary"
    row["time"].update(
        seconds=3602.478,
        last_active_seconds=3575.588,
        first_complete_seconds=3602.478,
        post_budget_intervention=False,
    )
    assert recompute(data, POLICY)["trials"][1]["eligible_score"] == 70
    row["time"]["last_active_seconds"] = 3500
    with pytest.raises(ValueError, match="interval"):
        recompute(data, POLICY)


@pytest.mark.parametrize("mutation", ["missing-game", "duplicate", "same-source", "hash"])
def test_bad_selection_and_policy_pins_rejected(mutation):
    data = fixture()
    if mutation == "missing-game":
        data["trials"].pop()
    elif mutation == "duplicate":
        data["trials"].append(copy.deepcopy(data["trials"][0]))
    elif mutation == "same-source":
        data["trials"][1]["source_run_id"] = data["trials"][0]["source_run_id"]
    else:
        data["policy_sha256"] = "0" * 64
    with pytest.raises(ValueError):
        recompute(data, POLICY)


@pytest.mark.parametrize("rating", [-1, 11, True, float("nan"), 8.5])
def test_invalid_ratings_rejected(rating):
    data = fixture()
    data["trials"][0]["mechanics"]["opens"]["rating"] = rating
    with pytest.raises(ValueError):
        recompute(data, POLICY)


def test_inputs_not_modified():
    data = fixture()
    original = copy.deepcopy(data)
    recompute(data, POLICY)
    assert data == original


def test_delivery_revision_credits_measured_time_without_implying_mechanics_pass():
    path = Path(__file__).resolve().parents[1] / "scoring/three-game-review-v1.1.json"
    revised = path.read_bytes()
    data = fixture()
    data.update(
        policy_id=json.loads(revised)["policy_id"],
        policy_sha256=hashlib.sha256(revised).hexdigest(),
    )
    row = data["trials"][1]
    row["time"]["seconds"] = 559.239
    row["mechanics"]["acceleration"].update(status="unobserved", rating=None)
    result = recompute(data, revised)["trials"][1]
    assert result["dimensions"]["time"]["points"] == pytest.approx(27.643281818)
    assert result["eligible_score"] is None
    # A failed basic delivery remains gated; this is not a per-platform exception.
    row["mechanics"]["ready"]["rating"] = 0
    assert recompute(data, revised)["trials"][1]["dimensions"]["time"]["points"] == 0


def final_fixture():
    path = (
        Path(__file__).resolve().parents[1] / "scoring/three-game-final-artifact-review-v1.2.json"
    )
    policy = path.read_bytes()
    data = fixture()
    data.update(
        policy_id=json.loads(policy)["policy_id"], policy_sha256=hashlib.sha256(policy).hexdigest()
    )
    return data, policy


def test_completed_continuation_retains_quality_with_zero_speed_in_final_edition():
    data, policy = final_fixture()
    data["trials"][1]["time"]["seconds"] = 4513.594
    result = recompute(data, policy)
    assert result["trials"][1]["eligible_score"] == 70
    assert result["trials"][1]["dimensions"]["time"]["points"] == 0
    assert result["platforms"][0]["eligible_score"] == 90
    # The unchanged capped edition must not silently admit that continuation.
    data.update(policy_id=RULES["policy_id"], policy_sha256=hashlib.sha256(POLICY).hexdigest())
    with pytest.raises(ValueError, match="Late delivery"):
        recompute(data, POLICY)


def test_uncapped_edition_cannot_invent_a_generation_timeout():
    data, policy = final_fixture()
    data["trials"][1]["outcome"] = "generation_timeout"
    with pytest.raises(ValueError, match="No generation cutoff"):
        recompute(data, policy)


@pytest.mark.parametrize("mutation", ["weight", "games", "gate", "time", "version"])
def test_malformed_policy_is_rejected_even_with_matching_hash(mutation):
    data, policy_bytes = final_fixture()
    policy = json.loads(policy_bytes)
    if mutation == "weight":
        policy["experience"]["feedback"] = -1
    elif mutation == "games":
        policy["games"].pop("tetris")
    elif mutation == "gate":
        policy["games"]["racing"]["time_gates"] = ["invented"]
    elif mutation == "time":
        policy["time"]["full_credit_seconds"] = 3600
    else:
        policy["policy_id"] = "unreviewed/99"
    changed = json.dumps(policy).encode()
    data.update(policy_id=policy["policy_id"], policy_sha256=hashlib.sha256(changed).hexdigest())
    with pytest.raises(ValueError):
        recompute(data, changed)


def test_final_policy_bytes_match_the_published_review_reference():
    _, policy = final_fixture()
    assert (
        hashlib.sha256(policy).hexdigest()
        == "c5422cd415a855540b76cbc39e93a34196953852e9d55f0ee80dcc34f0086c20"
    )
