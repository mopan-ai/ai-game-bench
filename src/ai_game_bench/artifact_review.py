"""Offline arithmetic for a retrospective review, not a gameplay verifier.

Explicit assessment JSON in, recomputed JSON out. No network, browser, runner,
submission approval or historical-score mutation is involved.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

GAMES = {"tetris", "racing", "platformer"}
CAPPED_POLICIES = {"three-game-artifact-review/1.0.0", "three-game-artifact-review/1.1.0"}
FINAL_POLICY = "three-game-final-artifact-review/1.2.0"


def nonempty(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"A nonempty {label} is required")


def validate_policy(policy):
    if policy.get("policy_id") not in CAPPED_POLICIES | {FINAL_POLICY}:
        raise ValueError("Unsupported scoring edition")
    if policy.get("dimensions") != {"mechanics": 50, "experience": 20, "time": 30}:
        raise ValueError("Unsupported scoring edition")
    if set(policy["games"]) != GAMES:
        raise ValueError("The review requires exactly the three supported games")
    for weights in [policy["experience"], *(g["mechanics"] for g in policy["games"].values())]:
        if not weights or any(number(w, "weight") == 0 for w in weights.values()):
            raise ValueError("Criterion weights must be positive")
    for game in policy["games"].values():
        gates = game["time_gates"]
        if not gates or len(gates) != len(set(gates)) or not set(gates) <= set(game["mechanics"]):
            raise ValueError("Time gates must name unique mechanics")
    rules = policy["time"]
    if number(rules["full_credit_seconds"], "full credit") >= number(
        rules["zero_credit_seconds"], "zero credit"
    ):
        raise ValueError("Time curve requires a positive interval")
    number(rules["boundary_max_sampling_gap_seconds"], "sampling gap")
    if (
        policy["policy_id"] == FINAL_POLICY
        and policy.get("generation_cutoff_seconds", 3600) is not None
    ):
        raise ValueError("Final-artifact review has no generation cutoff")


def number(value, label, maximum=None):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise ValueError(f"Invalid {label}")
    if maximum is not None and value > maximum:
        raise ValueError(f"Invalid {label}")
    return value


def evidence(item):
    nonempty(item.get("reason"), "reason")
    refs = item.get("evidence")
    if (
        not isinstance(refs, list)
        or not refs
        or any(not isinstance(x, str) or not x.strip() for x in refs)
    ):
        raise ValueError("Evidence references are required; references are not verified facts")


def criterion(item):
    status = item.get("status")
    if status not in {"observed", "unobserved", "blocked_by_artifact"}:
        raise ValueError("Invalid criterion status")
    if status == "unobserved":
        nonempty(item.get("reason"), "reason")
        if item.get("rating") is not None:
            raise ValueError("An unobserved criterion needs a null rating and reason")
        return 0, 1, False
    evidence(item)
    rating = number(item.get("rating"), "rating", 10)
    if not float(rating).is_integer():
        raise ValueError("Criteria use integer 0–10 ratings")
    if status == "blocked_by_artifact" and (rating != 0 or not item.get("blocked_by")):
        raise ValueError("Artifact dependency needs zero rating and a named blocker")
    return rating / 10, rating / 10, True


def dimension(items, weights, total):
    if set(items) != set(weights):
        raise ValueError("Criterion IDs must exactly match the scoring policy")
    denominator = sum(weights.values())
    low = high = known = 0.0
    for name, weight in weights.items():
        a, b, observed = criterion(items[name])
        contribution = total * weight / denominator
        low += contribution * a
        high += contribution * b
        known += contribution * observed
    return {"points": low, "upper": high, "assessed_weight": known, "max": total}


def time_dimension(row, policy):
    maximum = policy["dimensions"]["time"]
    timing = row["time"]
    evidence(timing)
    duration = timing.get("seconds")
    if duration is not None:
        number(duration, "duration")
    rules = policy["time"]
    cap = rules["zero_credit_seconds"]
    if row["outcome"] == "deadline_boundary":
        last = number(timing.get("last_active_seconds"), "last active")
        first = number(timing.get("first_complete_seconds"), "first complete")
        if not last < cap < first or first - last > rules["boundary_max_sampling_gap_seconds"]:
            raise ValueError("Completion interval does not qualify for boundary adjudication")
        if duration != first or timing.get("post_budget_intervention") is not False:
            raise ValueError("Boundary requires first observed completion and no intervention")
        low = high = 0.0
        known = maximum
    else:
        gates = [row["mechanics"][key] for key in policy["games"][row["game"]]["time_gates"]]
        failed = any(g["status"] != "unobserved" and g["rating"] < 10 for g in gates)
        if failed:
            low = high = 0.0
            known = maximum
        elif duration is None:
            low, high, known = 0.0, maximum, 0
        else:
            potential = maximum * max(
                0, min(1, (cap - duration) / (cap - rules["full_credit_seconds"]))
            )
            uncertain = any(g["status"] == "unobserved" for g in gates)
            low, high = (0.0, potential) if uncertain else (potential, potential)
            known = 0 if uncertain and potential > 0 else maximum
    return {
        "points": low,
        "upper": high,
        "assessed_weight": known,
        "max": maximum,
        "observed_seconds": duration,
    }


def trial(row, policy):
    outcome = row["outcome"]
    result = {key: row[key] for key in ("id", "platform", "game", "outcome")}
    if outcome in {"infrastructure_error", "owner_held", "unmeasured"}:
        evidence(row)
        return result | {
            "points": None,
            "upper": None,
            "eligible_score": None,
            "assessed_weight": 0,
            "dimensions": {},
            "reason": row["reason"],
        }
    if outcome == "generation_timeout":
        if policy["policy_id"] == FINAL_POLICY:
            raise ValueError(
                "No generation cutoff in this edition; use unmeasured for no final artifact"
            )
        evidence(row)
        if number(row["time"]["seconds"], "timeout") < policy["time"]["zero_credit_seconds"]:
            raise ValueError("Timeout needs evidence of an exhausted generation budget")
        if row.get("capture_functioning") is not True:
            raise ValueError("Capture failure is not generation timeout")
        return result | {
            "points": 0.0,
            "upper": 0.0,
            "eligible_score": 0.0,
            "assessed_weight": 100,
            "dimensions": {},
            "reason": row["reason"],
        }
    if outcome not in {"delivered", "deadline_boundary"}:
        raise ValueError("Unknown outcome")
    duration = row["time"].get("seconds")
    if (
        policy["policy_id"] in CAPPED_POLICIES
        and outcome == "delivered"
        and duration is not None
        and number(duration, "duration") > policy["time"]["zero_credit_seconds"]
    ):
        raise ValueError(
            "Late delivery requires boundary adjudication or the final-artifact edition"
        )
    for item in [*row["mechanics"].values(), *row["experience"].values()]:
        if item.get("status") == "blocked_by_artifact":
            blocker = row["mechanics"].get(item.get("blocked_by"), {})
            if blocker.get("status") != "observed" or blocker.get("rating") != 0:
                raise ValueError("Dependency must cite an observed failed mechanic")
    dimensions = {
        "mechanics": dimension(row["mechanics"], policy["games"][row["game"]]["mechanics"], 50),
        "experience": dimension(row["experience"], policy["experience"], 20),
        "time": time_dimension(row, policy),
    }
    low = sum(x["points"] for x in dimensions.values())
    high = sum(x["upper"] for x in dimensions.values())
    known = sum(x["assessed_weight"] for x in dimensions.values())
    return result | {
        "points": low,
        "upper": high,
        "eligible_score": low if math.isclose(known, 100) else None,
        "assessed_weight": known,
        "dimensions": dimensions,
    }


def recompute(assessment, policy_bytes):
    policy = json.loads(policy_bytes)
    validate_policy(policy)
    if (
        assessment.get("policy_id") != policy["policy_id"]
        or assessment.get("policy_sha256") != hashlib.sha256(policy_bytes).hexdigest()
    ):
        raise ValueError("Assessment must pin the exact policy ID and bytes")
    rows = assessment["trials"]
    if not isinstance(rows, list) or not rows:
        raise ValueError("At least one preselected platform is required")
    seen = set()
    sources = set()
    groups = defaultdict(lambda: defaultdict(list))
    calculated = []
    for row in rows:
        for key in ("id", "platform", "game", "source_run_id"):
            nonempty(row.get(key), key)
        if row["id"] in seen or row["game"] not in policy["games"]:
            raise ValueError("Duplicate trial or unknown game")
        source_key = (row["platform"], row["source_run_id"])
        if source_key in sources:
            raise ValueError("One source run cannot count twice")
        seen.add(row["id"])
        sources.add(source_key)
        value = trial(row, policy)
        calculated.append(value)
        groups[row["platform"]][row["game"]].append(value)
    totals = []
    for platform, games in groups.items():
        if set(games) != set(policy["games"]):
            raise ValueError("All three games need explicit rows, including held/invalid tasks")
        invalid = any(r["points"] is None for rs in games.values() for r in rs)
        complete = all(r["eligible_score"] is not None for rs in games.values() for r in rs)

        def mean(field, games=games):
            return sum(sum(r[field] for r in rs) / len(rs) for rs in games.values()) / 3

        low, high = (None, None) if invalid else (mean("points"), mean("upper"))
        totals.append(
            {
                "platform": platform,
                "points": low,
                "upper": high,
                "eligible_score": low if complete else None,
                "status": "invalid_or_held_task"
                if invalid
                else ("complete" if complete else "evidence_lower_bound"),
                "selected_trials": sum(map(len, games.values())),
            }
        )
    return {
        "schema": "three-game-review-result/1",
        "policy_id": policy["policy_id"],
        "policy_sha256": assessment["policy_sha256"],
        "verification": "arithmetic_only_not_gameplay_or_evidence_authenticity",
        "trials": calculated,
        "platforms": totals,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("assessment", type=Path)
    parser.add_argument("--policy", type=Path, required=True)
    args = parser.parse_args()
    result = recompute(json.loads(args.assessment.read_text()), args.policy.read_bytes())
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
