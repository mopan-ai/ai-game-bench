"""Task-scoped retrospective evidence: offline data checks, never a new runner.

This format preserves the 1.2 artifact-review arithmetic without claiming the
source trial followed a browser-pilot creation policy. Old exports are unchanged.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field, field_validator

from . import artifact_review as arithmetic
from .submission_models import (
    ID,
    Cost,
    Creator,
    ExternalEvidence,
    File,
    Hash,
    Number,
    Publication,
    Record,
    Text,
    timestamp,
)

SCHEMA = "artifact-review-package/1"
STANDARD = "scoring/three-game-final-artifact-review-v1.2.json"
TASK_REFERENCES = {
    "tetris": "tetris-browser-pilot-v1",
    "racing": "racing-3d-browser-pilot-v2",
    "platformer": "platformer-browser-pilot-v2",
}


class CaptureEvent(Record):
    """A normalized captured record; missing lifecycle events are not invented."""

    seq: Annotated[int, Field(ge=1)]
    id: Text
    at: Text
    kind: Text
    detail: Text
    evidence: list[Text]
    artifact_id: ID | None

    @field_validator("at")
    @classmethod
    def timezone_required(cls, value):
        timestamp(value)
        return value


class Rating(Record):
    rating: Annotated[int, Field(ge=0, le=10)] | None
    status: Literal["observed", "unobserved", "blocked_by_artifact"]
    reason: Text
    evidence_events: list[Text]
    blocked_by: Text | None = None


class Timing(Record):
    seconds: Number | None
    started_at: Text | None
    finished_at: Text | None
    start_before_event: Text | None
    start_after_event: Text | None
    finish_event: Text | None
    reason: Text


class Assessment(Record):
    schema_version: Literal["artifact-review-assessment/1"]
    assessed_at: Text
    mechanics: dict[Text, Rating]
    experience: dict[Text, Rating]
    time: Timing
    computed: dict


class ReviewArtifact(Record):
    id: ID
    build_version: Text | None
    url: Text | None
    access: Literal["unpublished", "not_checked", "login_required", "publicly_accessible"]
    note: Text


class Series(Record):
    id: ID
    round_id: ID
    comparator_round_id: ID | None
    selection: Text
    change: Text


class ReviewPackage(Record):
    schema_version: Literal["artifact-review-package/1"]
    id: ID
    revision: Annotated[int, Field(ge=1, le=999)]
    kind: Literal["result", "synthetic_example"]
    author: Text
    affiliation: Text
    source_ref: Text
    source_manifest_sha256: Hash
    series: Series
    game: Literal["tetris", "racing", "platformer"]
    outcome: Literal["delivered"]
    scoring_policy_sha256: Hash
    task_reference_sha256: Hash
    prompt_file: Text
    prompt_sha256: Hash
    prompt_trailing_newline_omitted: bool
    creator: Creator
    environment: Text
    creation_conditions: Text
    evaluator: Text
    creation_context_hidden: bool
    artifact: ReviewArtifact
    creation: Text
    evaluation: Text
    assessment: Text
    files: Annotated[list[File], Field(min_length=4, max_length=300)]
    external_evidence: Annotated[list[ExternalEvidence], Field(max_length=100)]
    costs: Annotated[list[Cost], Field(min_length=1, max_length=50)]
    publication: Publication


def capture_events(data, references, artifact_id, *, evaluation):
    from . import submissions as s

    lines = data.decode().splitlines()
    s.require(0 < len(lines) <= s.MAX_EVENTS, "trajectory", "Empty/oversized trajectory.")
    events = [s.model(CaptureEvent, s.parse_json(line.encode())) for line in lines]
    s.require(
        [e.seq for e in events] == list(range(1, len(events) + 1))
        and len({e.id for e in events}) == len(events),
        "trajectory",
        "Capture sequences and IDs must be unique and consecutive.",
    )
    s.require(
        all(timestamp(a.at) <= timestamp(b.at) for a, b in zip(events, events[1:], strict=False)),
        "trajectory",
        "Capture timestamps must be nondecreasing.",
    )
    for e in events:
        s.require(set(e.evidence) <= references, "evidence_reference", "Missing capture evidence.")
        s.require(
            e.artifact_id == artifact_id if evaluation else e.artifact_id in {None, artifact_id},
            "artifact_mismatch",
            "Evaluation must identify the declared final artifact.",
        )
    return {e.id: e for e in events}


def calculate(package, assessment, creation, evaluation, standard):
    from . import submissions as s

    assessed_at = timestamp(assessment.assessed_at)
    s.require(
        assessed_at >= max(timestamp(e.at) for e in evaluation.values()),
        "assessment_time",
        "Assessment cannot precede its evidence.",
    )
    row = {"id": package.id, "platform": package.creator.platform, "game": package.game}
    row["outcome"] = "delivered"
    for group in ("mechanics", "experience"):
        row[group] = {}
        for name, value in getattr(assessment, group).items():
            refs = value.evidence_events
            s.require(
                set(refs) <= set(evaluation)
                and all(evaluation[r].evidence for r in refs)
                and (value.status == "unobserved" or bool(refs)),
                "evidence_reference",
                "Ratings need evidence-backed evaluation capture IDs.",
            )
            row[group][name] = value.model_dump(exclude={"evidence_events"}) | {"evidence": refs}
    timing = assessment.time
    anchors = [timing.start_before_event, timing.start_after_event, timing.finish_event]
    if timing.seconds is None:
        s.require(
            timing.started_at is None and timing.finished_at is None and not any(anchors),
            "time",
            "Unknown timing must not invent anchors.",
        )
    else:
        s.require(
            timing.started_at is not None
            and timing.finished_at is not None
            and all(a in creation and creation[a].evidence for a in anchors),
            "time",
            "Known timing needs evidence-backed creation anchors.",
        )
        start, end = timestamp(timing.started_at), timestamp(timing.finished_at)
        before, after, final = (creation[a] for a in anchors)
        s.require(
            timestamp(before.at) <= start <= timestamp(after.at) <= end
            and end == timestamp(final.at)
            and min(timestamp(e.at) for e in evaluation.values()) >= end
            and math.isclose(
                (end - start).total_seconds(), timing.seconds, abs_tol=1e-6, rel_tol=0
            ),
            "time",
            "Duration must match recorded boundaries and precede final-artifact evaluation.",
        )
    row["time"] = {
        "seconds": timing.seconds,
        "reason": timing.reason,
        "evidence": [a for a in anchors if a] or ["unknown timing explicitly declared"],
    }
    return arithmetic.trial(row, standard)


def validate_package(directory: Path, root: Path, parsed: dict, *, draft=False):
    """Uses the existing public file/URL/secret limits; never fetches a URL."""
    from . import submissions as s

    p = s.model(ReviewPackage, parsed)
    s.require("REPLACE" not in s.encode(parsed).decode(), "draft", "Replace draft placeholders.")
    raw_standard = s.read_file(root, STANDARD)
    standard = s.parse_json(raw_standard)
    arithmetic.validate_policy(standard)
    s.require(s.digest(raw_standard) == p.scoring_policy_sha256, "policy", "Wrong scoring hash.")
    _, reference_hash, reference_prompt = s.load_policy(root, TASK_REFERENCES[p.game])
    s.require(reference_hash == p.task_reference_sha256, "policy", "Wrong task reference hash.")
    names = [f.path for f in p.files]
    s.require(
        len(set(names)) == len(names)
        and "manifest.json" not in names
        and s.inventory(directory) == set(names) | {"manifest.json"},
        "file_list",
        "Only the manifest and unique allowlisted evidence are accepted.",
    )
    blobs = {}
    size = len(s.encode(parsed))
    for f in p.files:
        suffix = Path(f.path).suffix.lower()
        s.require(suffix in s.TEXT_SUFFIXES | s.IMAGE_SUFFIXES, "file_type", "Unsupported file.")
        data = s.read_file(directory, f.path)
        s.require(
            f.sha256 == s.digest(data) and f.bytes == len(data), "file_hash", "Hash/size mismatch."
        )
        if suffix in s.TEXT_SUFFIXES:
            s.scan_text(data)
            if suffix == ".json":
                s.scan_text(s.encode(s.parse_json(data)))
            elif suffix == ".jsonl":
                for line in data.splitlines():
                    s.scan_text(s.encode(s.parse_json(line)))
        else:
            signature_ok = (
                (suffix == ".png" and data.startswith(b"\x89PNG\r\n\x1a\n"))
                or (suffix in {".jpg", ".jpeg"} and data.startswith(b"\xff\xd8\xff"))
                or (suffix == ".webp" and data[:4] == b"RIFF" and data[8:12] == b"WEBP")
            )
            s.require(signature_ok, "file_type", "Image signature does not match its extension.")
        blobs[f.path] = data
        size += len(data)
        s.require(size <= s.MAX_PACKAGE, "package_size", "Use smaller task-scoped exports.")
    s.require(size <= s.MAX_PACKAGE, "package_size", "Use smaller task-scoped exports.")
    external_ids = [e.id for e in p.external_evidence]
    s.require(
        len(set(external_ids)) == len(external_ids), "evidence_reference", "Duplicate external ID."
    )
    for e in p.external_evidence:
        s.public_url(e.url)
    special = {p.prompt_file, p.creation, p.evaluation, p.assessment}
    s.require(
        len(special) == 4
        and special <= set(blobs)
        and p.creation.endswith(".jsonl")
        and p.evaluation.endswith(".jsonl")
        and p.assessment.endswith(".json"),
        "file_list",
        "Prompt, two capture streams and assessment need distinct allowlisted files.",
    )
    actual_prompt = blobs[p.prompt_file]
    expected_prompt = (
        reference_prompt.rstrip("\r\n") if p.prompt_trailing_newline_omitted else reference_prompt
    )
    s.require(
        s.digest(actual_prompt) == p.prompt_sha256 and actual_prompt.decode() == expected_prompt,
        "prompt",
        "Preserve actual prompt bytes; only a declared trailing-newline omission is supported.",
    )
    references = set(blobs) - {p.creation, p.evaluation, p.assessment}
    references |= {f"external:{i}" for i in external_ids}
    creation = capture_events(blobs[p.creation], references, p.artifact.id, evaluation=False)
    evaluation = capture_events(blobs[p.evaluation], references, p.artifact.id, evaluation=True)
    s.require(not set(creation) & set(evaluation), "trajectory", "Capture IDs must be distinct.")
    if p.artifact.url is not None:
        s.public_url(p.artifact.url, artifact=True)
    s.require(
        p.artifact.access != "publicly_accessible" or p.artifact.url is not None,
        "artifact",
        "A public-access claim needs a URL; this check does not replay it.",
    )
    for cost in p.costs:
        s.require(set(cost.evidence) <= references, "cost", "Missing cost evidence.")
        if cost.kind == "unknown":
            s.require(
                cost.amount is None and cost.currency is None, "cost", "Unknown cost is null."
            )
        elif cost.kind == "no_model_call":
            s.require(
                cost.amount == 0 and cost.currency is not None,
                "cost",
                "No-model cost must be zero.",
            )
        else:
            s.require(
                cost.amount is not None and cost.currency is not None and cost.evidence,
                "cost",
                "Known cost needs a basis and public evidence.",
            )
    assessment = s.model(Assessment, s.parse_json(blobs[p.assessment]))
    computed = calculate(p, assessment, creation, evaluation, standard)
    s.require(computed == assessment.computed, "total", "Retrospective arithmetic mismatch.")
    confirmed = all(
        getattr(p.publication, k)
        for k in (
            "public_release_confirmed",
            "rights_confirmed",
            "sensitive_data_checked",
            "all_attempts_disclosed",
        )
    )
    if not draft:
        s.require(
            confirmed,
            "publication",
            "Explicit release, rights, privacy and attempt confirmations required.",
        )
    return {
        "structure_valid": not draft,
        **({"draft_valid": True, "publication_ready": False} if draft else {}),
        "review_status": "unverified",
        "id": p.id,
        "revision": p.revision,
        "kind": p.kind,
        "manifest_sha256": s.digest(s.encode(parsed)),
        "evaluation_kind": "retrospective_artifact_review_not_creation_policy_compliance",
        "attempts": [],
        "score_addenda": [],
        "retrospective_score": computed,
        "errors": [],
        "warnings": [
            "Checks do not authenticate evidence, replay games or approve results.",
            "Task references identify prompts, not source-run creation-policy compliance.",
            "Inspect images, rights, all attempts, timing and affiliation before acceptance.",
            "Missing public game URLs limit replay; this format permits evidence-only reviews.",
            *(
                ["Draft check only: publication confirmations were not asserted or changed."]
                if draft
                else []
            ),
        ],
    }
