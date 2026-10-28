"""Files in, JSON out. Checks a judge's claim against a separately held label."""

import hashlib
import json
from pathlib import Path


def grade(judgement, trace, expected, evidence_root):
    statuses = {"passed", "failed", "not_tested", "infra_error"}
    if (
        set(judgement) != {"status", "reason", "evidence_ids"}
        or judgement["status"] not in statuses
    ):
        raise ValueError("Malformed judgement")
    if not isinstance(judgement["reason"], str) or not judgement["reason"].strip():
        raise ValueError("Missing verdict explanation")
    ids = judgement["evidence_ids"]
    if not isinstance(ids, list) or not all(isinstance(x, str) for x in ids):
        raise ValueError("Invalid evidence references")
    frames = {e["id"]: e for e in trace["events"] if e["kind"] == "observation"}
    if not set(ids) <= frames.keys():
        raise ValueError("Verdict cites nonexistent observations")
    for ident in ids:
        event = frames[ident]
        path = (evidence_root / event["file"]).resolve()
        if path.parent != evidence_root.resolve():
            raise ValueError("Evidence path outside capture directory")
        if hashlib.sha256(path.read_bytes()).hexdigest() != event["sha256"]:
            raise ValueError("Screenshot hash mismatch")
    status = judgement["status"]
    if status in {"passed", "failed"} and (
        len(set(ids)) < 2
        or not any(e["kind"] == "action" and e["action"] != "observe" for e in trace["events"])
    ):
        raise ValueError("A decisive verdict needs action and before/after evidence")
    if trace["page_errors"] or status == "infra_error":
        raise RuntimeError("Invalid measurement: browser/evaluator infrastructure error")
    return {
        "schema_version": "judge-check/0.1",
        "expected_status": expected,
        "observed_status": status,
        "correct": status == expected,
        "false_pass": expected == "failed" and status == "passed",
        "false_failure": expected == "passed" and status == "failed",
        "not_tested": status == "not_tested",
        "evidence_references_valid": True,
        "evidence_semantics_reviewed": False,
        "scope": "focused fixture probe, not full criterion or game-quality score",
    }


if __name__ == "__main__":
    root = Path("/logs/agent/gameplay")
    result = grade(
        json.loads(Path("/workspace/judgement.json").read_text()),
        json.loads((root / "events.json").read_text()),
        json.loads(Path("/tests/answer.json").read_text())["expected_status"],
        root,
    )
    print(json.dumps(result, indent=2))
    output = Path("/logs/verifier")
    output.mkdir(parents=True, exist_ok=True)
    (output / "details.json").write_text(json.dumps(result, indent=2) + "\n")
    (output / "reward.json").write_text(
        json.dumps({"judgement_correct": int(result["correct"])}) + "\n"
    )
