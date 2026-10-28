"""Public export contracts, not replacements for native Harbor trial records."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Text = Annotated[str, Field(min_length=1, max_length=16000)]
ID = Annotated[str, Field(pattern=r"^[a-z0-9][a-z0-9-]{0,79}$")]
Hash = Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]
Number = Annotated[float, Field(ge=0, allow_inf_nan=False)]


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Task(Record):
    kind: Literal["harbor", "browser_protocol"] = "harbor"
    path: Text
    version: Text
    instruction_sha256: Hash
    rubric_sha256: Hash
    verifier_sha256: Hash


class Criterion(Record):
    id: ID
    description: Text
    max_score: Annotated[float, Field(gt=0, allow_inf_nan=False)]
    weight: Annotated[float, Field(gt=0, allow_inf_nan=False)]
    allow_partial: bool = False


class TimeScore(Record):
    criterion_id: ID
    full_credit_seconds: Annotated[int, Field(ge=0)]
    required_passes: Annotated[list[ID], Field(min_length=1)]


AccessMode = Literal["screenshot_only", "visible_ui", "instrumented"]


class MeasurementRules(Record):
    core_criteria: Annotated[list[ID], Field(min_length=1)]
    allowed_access: Annotated[list[AccessMode], Field(min_length=1)]
    evaluation_budget_seconds: Annotated[int, Field(gt=0, le=86400)]
    session_limit: Annotated[int, Field(gt=0, le=100)]
    viewport_width: Annotated[int, Field(gt=0)]
    viewport_height: Annotated[int, Field(gt=0)]
    clock: Literal["realtime", "stepped"]


class Policy(Record):
    schema_version: Literal["public-policy/0.1", "public-policy/0.2"]
    id: ID
    task: Task
    prompt_mode: Literal["full_instruction", "mopan_block"]
    attempt_limit: Annotated[int, Field(ge=1, le=100)]
    timeout_seconds: Annotated[int, Field(ge=1, le=86400)]
    allow_followups: bool
    allow_repairs: bool
    artifact_kinds: list[Literal["public_url", "harbor_bundle"]]
    criteria: Annotated[list[Criterion], Field(min_length=1, max_length=100)]
    total_max: Annotated[float, Field(gt=0, allow_inf_nan=False)]
    time_score: TimeScore | None = None
    limitations: Annotated[list[Text], Field(min_length=1)]
    measurement: MeasurementRules | None = None


class File(Record):
    path: Text
    sha256: Hash | None
    bytes: Annotated[int, Field(ge=0)] | None


class ExternalEvidence(Record):
    id: ID
    url: Text
    sha256: Hash
    bytes: Annotated[int, Field(gt=0)]
    description: Text


class Event(Record):
    seq: Annotated[int, Field(ge=1)]
    id: ID
    at: Text
    kind: Literal[
        "session_started",
        "model_selected",
        "prompt_accepted",
        "progress",
        "clarification",
        "followup",
        "repair",
        "delivered",
        "build_failure",
        "timeout",
        "auth_failure",
        "infrastructure_error",
        "evaluation_started",
        "action",
        "observation",
        "evaluation_finished",
    ]
    detail: Text
    evidence: list[Text]
    artifact_id: ID | None = None
    prompt: Text | None = None

    @field_validator("at")
    @classmethod
    def timezone_required(cls, value: str) -> str:
        timestamp(value)
        return value


def timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Timestamp must include a timezone")
    return parsed


class Artifact(Record):
    id: ID
    kind: Literal["public_url", "harbor_bundle"]
    url: Text | None
    build_version: Text | None
    bundle_sha256: Hash | None
    access: Text


class Verdict(Record):
    criterion_id: ID
    status: Literal["passed", "partial", "failed", "not_tested", "infra_error"]
    score: Number | None
    reason: Text
    evidence_events: list[ID]


class ToolConfiguration(Record):
    name: Text
    version: Text | None


class EvaluationConfiguration(Record):
    harness_version: Text | None
    effort: Text | None
    instructions_file: Text | None
    instructions_sha256: Hash | None
    tools: Annotated[list[ToolConfiguration], Field(max_length=50)]
    access_mode: AccessMode
    browser: Text
    browser_version: Text | None
    viewport_width: Annotated[int, Field(gt=0)]
    viewport_height: Annotated[int, Field(gt=0)]
    clock: Literal["realtime", "stepped"]


class Evaluation(Record):
    evaluator: Text
    model: Text | None
    mode: Literal["deterministic", "human", "agent_dom", "agent_visual"]
    creation_context_hidden: bool
    criteria: list[Verdict]
    total: Number | None
    configuration: EvaluationConfiguration | None = None


class Attempt(Record):
    id: ID
    outcome: Literal[
        "delivered", "build_failure", "timeout", "auth_failure", "infrastructure_error"
    ]
    creation: Text
    evaluation: Text
    artifact: Artifact | None
    result: Evaluation


class Creator(Record):
    platform: Text
    harness_version: Text | None
    model: Text | None
    model_source: Literal["visible_ui", "provider_record", "unknown", "not_applicable"]
    effort: Text | None


class Cost(Record):
    kind: Literal["unknown", "model_estimate", "credit_value", "actual_charge", "no_model_call"]
    component: Literal["creator", "operator", "evaluator"]
    amount: Number | None
    currency: Annotated[str, Field(pattern=r"^[A-Z]{3}$")] | None
    basis: Text
    evidence: list[Text]


class Publication(Record):
    public_release_confirmed: bool
    rights_confirmed: bool
    sensitive_data_checked: bool
    all_attempts_disclosed: bool
    license: Text
    redactions: list[Text]
    capture_gaps: list[Text]
    limitations: list[Text]


class Submission(Record):
    schema_version: Literal["public-submission/0.1", "public-submission/0.2"]
    id: ID
    revision: Annotated[int, Field(ge=1, le=999)]
    kind: Literal["result", "synthetic_example"]
    policy_id: ID
    policy_sha256: Hash
    author: Text
    affiliation: Text
    creator: Creator
    environment: Text
    source_kind: Literal["harbor", "browser_observation"]
    source_ref: Text
    attempts: Annotated[list[Attempt], Field(min_length=1, max_length=100)]
    files: Annotated[list[File], Field(min_length=2, max_length=300)]
    external_evidence: Annotated[list[ExternalEvidence], Field(max_length=100)]
    costs: Annotated[list[Cost], Field(min_length=1, max_length=50)]
    publication: Publication
    score_addenda: Annotated[list[Text], Field(max_length=10)] = []
