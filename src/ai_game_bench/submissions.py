"""Offline public-evidence packaging. Never executes uploads, games, URLs or PR code."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import stat
import tomllib
from pathlib import Path, PurePosixPath
from urllib.parse import parse_qsl, urlsplit

from pydantic import ValidationError

from ai_game_bench.submission_models import Event, Policy, Submission, timestamp

MAX_FILE = 2 * 1024 * 1024 - 1
MAX_PACKAGE = 20 * 1024 * 1024
MAX_EVENTS = 10000
TEXT_SUFFIXES = {".json", ".jsonl", ".txt", ".md", ".log"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
TERMINALS = {"delivered", "build_failure", "timeout", "auth_failure", "infrastructure_error"}
CREATION_KINDS = TERMINALS | {
    "session_started",
    "model_selected",
    "prompt_accepted",
    "progress",
    "clarification",
    "followup",
    "repair",
}
EVALUATION_KINDS = {"evaluation_started", "action", "observation", "evaluation_finished"}
SECRET_PATTERNS = (
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})",
    r"\bsk-[A-Za-z0-9_-]{20,}",
    r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b",
    r"(?i)\b(?:authorization|cookie|set-cookie)\s*[:=]\s*\S+",
    r"(?i)\b(?:api[_-]?key|access[_-]?token|password)\s*[\"']?\s*[:=]\s*[\"']?\S+",
    r"/(?:Users|home)/[^/\s]+/",
    r"(?i)[?&](?:token|key|sig|signature|x-amz-signature|x-goog-signature|auth)=[^\s&]+",
)


class InvalidSubmission(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise InvalidSubmission(code, message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def relative_path(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    require(
        not path.is_absolute()
        and path.as_posix() == value
        and all(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", p) for p in path.parts)
        and all(p not in {"jobs", "node_modules", "Cookies", "Login Data"} for p in path.parts),
        "unsafe_path",
        "Use normalized, relative, non-hidden evidence paths; no raw jobs.",
    )
    require(
        path.name.lower() not in {"auth.json", "credentials.json", "cookies", "login data"}
        and "storage-state" not in path.name.lower()
        and "storage_state" not in path.name.lower(),
        "unsafe_path",
        "Credential/session-state files are not public evidence.",
    )
    return path


def read_file(root: Path, name: str) -> bytes:
    path = relative_path(name)
    require(not root.is_symlink(), "symlink", "The package root cannot be a symlink.")
    current = root
    for part in path.parts:
        current = current / part
        require(not current.is_symlink(), "symlink", "Symlinks are not accepted.")
    # Do not block on a FIFO or follow a file swapped to a symlink.
    descriptor = os.open(current, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(descriptor, "rb") as handle:
        info = os.fstat(handle.fileno())
        require(stat.S_ISREG(info.st_mode), "file_type", "Evidence must be regular files.")
        require(info.st_size <= MAX_FILE, "file_size", "Use an external reference for large files.")
        data = handle.read(MAX_FILE + 1)
        require(len(data) <= MAX_FILE, "file_size", "Evidence exceeds the local size limit.")
        return data


def parse_json(data: bytes):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate_key", "Duplicate JSON keys are not accepted.")
            result[key] = value
        return result

    def constant(_):
        raise InvalidSubmission("nonfinite", "NaN/Infinity are not JSON evidence.")

    return json.loads(data, object_pairs_hook=pairs, parse_constant=constant)


def model(model_type, data):
    try:
        return model_type.model_validate(data)
    except ValidationError as exc:
        # Never echo input values: validation may be reporting an accidentally pasted secret.
        paths = [".".join(str(p) for p in e["loc"]) for e in exc.errors()[:10]]
        raise InvalidSubmission("schema", "Invalid/missing fields: " + ", ".join(paths)) from exc


def scan_text(data: bytes) -> None:
    text = data.decode("utf-8")
    require(
        not any(re.search(p, text) for p in SECRET_PATTERNS),
        "sensitive_text",
        "Possible credential or personal path found; inspect locally, redact, then resubmit.",
    )


def public_url(value: str, *, artifact: bool = False) -> None:
    url = urlsplit(value)
    require(
        url.scheme == "https"
        and bool(url.hostname)
        and not url.username
        and not url.password
        and not url.fragment
        and url.port in {None, 443}
        and url.hostname not in {"localhost", "localhost.localdomain"}
        and not url.hostname.endswith((".local", ".localhost", ".internal")),
        "unsafe_url",
        "References must be public HTTPS URLs without credentials or fragments.",
    )
    import ipaddress

    try:
        ip = ipaddress.ip_address(url.hostname)
    except ValueError:
        pass  # No DNS lookup: even public-looking hostnames remain untrusted.
    else:
        require(ip.is_global, "unsafe_url", "Private/local network references are not public.")
    keys = {key.lower() for key, _ in parse_qsl(url.query, keep_blank_values=True)}
    require(
        not url.query or (artifact and keys <= {"build", "version", "v"}),
        "unsafe_url",
        "No signed/tracking query strings; game URLs may pin build/version/v.",
    )


def load_policy(root: Path, policy_id: str):
    require(
        bool(re.fullmatch(r"[a-z0-9][a-z0-9-]{0,79}", policy_id)), "policy", "Invalid policy id."
    )
    raw = read_file(root, f"policies/{policy_id}.json")
    policy = model(Policy, parse_json(raw))
    require(policy.id == policy_id, "policy", "Policy identity does not match filename.")
    require(
        len({c.id for c in policy.criteria}) == len(policy.criteria),
        "policy",
        "Duplicate policy criterion.",
    )
    require(bool(policy.artifact_kinds), "policy", "A policy must define artifact kinds.")
    task_path = relative_path(policy.task.path)
    manual = policy.task.kind == "browser_protocol"
    base = f"{'protocols' if manual else 'datasets'}/{task_path}"
    config = tomllib.loads(read_file(root, f"{base}/task.toml").decode())
    require(config["task"]["version"] == policy.task.version, "policy", "Task version mismatch.")
    for path, expected in (
        ("instruction.md", policy.task.instruction_sha256),
        ("rubric.json" if manual else "tests/rubric.json", policy.task.rubric_sha256),
        ("evaluation.md" if manual else "tests/verify_submission.py", policy.task.verifier_sha256),
    ):
        require(
            digest(read_file(root, f"{base}/{path}")) == expected,
            "policy",
            "Frozen task bytes do not match the trusted policy.",
        )
    if manual:
        require(
            config.get("protocol", {}).get("mode") == "browser_observation",
            "policy",
            "Browser protocols are manual observations, not executable Harbor tasks.",
        )
        rubric = parse_json(read_file(root, f"{base}/rubric.json"))
        require(
            rubric["criteria"] == [c.model_dump() for c in policy.criteria]
            and rubric["total_max"] == policy.total_max,
            "policy",
            "Manual rubric and policy score mapping disagree.",
        )
    if policy.time_score:
        rule = policy.time_score
        ids = {c.id for c in policy.criteria}
        require(
            rule.criterion_id in ids
            and set(rule.required_passes) <= ids - {rule.criterion_id}
            and rule.full_credit_seconds < policy.timeout_seconds,
            "policy",
            "Invalid delivery-time scoring rule.",
        )
    from .measurements import check_policy

    check_policy(policy)
    prompt = read_file(root, f"{base}/instruction.md").decode()
    if policy.prompt_mode == "mopan_block":
        blocks = re.findall(
            r"<!-- MOPAN_PROMPT_START -->(.*?)<!-- MOPAN_PROMPT_END -->", prompt, re.S
        )
        require(len(blocks) == 1, "policy", "Expected exactly one public prompt block.")
        prompt = blocks[0].strip()
    return policy, digest(raw), prompt


def inventory(directory: Path, *, max_entries: int = 600) -> set[str]:
    require(
        directory.is_dir() and not directory.is_symlink(),
        "package",
        "Expected a real package directory.",
    )
    found = set()
    for base, dirs, files in os.walk(directory, followlinks=False):
        for name in dirs + files:
            path = Path(base) / name
            relative = path.relative_to(directory).as_posix()
            relative_path(relative)
            require(not path.is_symlink(), "symlink", "Symlinks are not accepted.")
            found.add(relative)
            require(
                len(found) <= max_entries, "package_size", "Too many files/directories in package."
            )
    return {name for name in found if not (directory / name).is_dir()}


def load_events(data: bytes, role: str, references: set[str]) -> list[Event]:
    lines = data.decode().splitlines()
    require(0 < len(lines) <= MAX_EVENTS, "trajectory", "Empty/oversized trajectory.")
    events = []
    for line in lines:
        parsed = parse_json(line.encode())
        scan_text(
            encode(parsed)
        )  # Also inspect decoded JSON strings, not just their escaped bytes.
        events.append(model(Event, parsed))
    allowed = CREATION_KINDS if role == "creation" else EVALUATION_KINDS
    require(
        [e.seq for e in events] == list(range(1, len(events) + 1)),
        "trajectory",
        "Event sequences must be consecutive from 1.",
    )
    require(all(e.kind in allowed for e in events), "trajectory", "Wrong event type for stream.")
    require(
        all(timestamp(a.at) <= timestamp(b.at) for a, b in zip(events, events[1:], strict=False)),
        "trajectory",
        "Event timestamps must be nondecreasing.",
    )
    require(
        all(set(e.evidence) <= references for e in events),
        "evidence_reference",
        "Event references missing evidence.",
    )
    return events


def check_attempt(attempt, policy, prompt, blobs, references, global_ids):
    measured = policy.schema_version == "public-policy/0.2"
    require(attempt.creation != attempt.evaluation, "trajectory", "Use separate trajectory files.")
    for name in (attempt.creation, attempt.evaluation):
        require(
            name in blobs and name.endswith(".jsonl"),
            "trajectory",
            "Each attempt needs two listed JSONL trajectories.",
        )
    creation = load_events(blobs[attempt.creation], "creation", references)
    evaluation = load_events(blobs[attempt.evaluation], "evaluation", references)
    for event in creation + evaluation:
        require(
            event.id not in global_ids, "trajectory", "Event ids must be unique in the package."
        )
        global_ids.add(event.id)
    require(
        creation[0].kind == "session_started" and creation[-1].kind == attempt.outcome,
        "trajectory",
        "Creation must start a session and end in its declared outcome.",
    )
    require(
        sum(e.kind in TERMINALS for e in creation) == 1,
        "trajectory",
        "Only one terminal event is allowed per attempt.",
    )
    accepted = [e for e in creation if e.kind == "prompt_accepted"]
    require(len(accepted) <= 1, "attempts", "Multiple sends need separately disclosed attempts.")
    if attempt.outcome in {"delivered", "build_failure"} or (
        measured and attempt.outcome == "timeout"
    ):
        require(
            len(accepted) == 1 and bool(accepted[0].evidence),
            "missing_send",
            "Missing accepted-prompt event and its evidence.",
        )
    if accepted:
        require(accepted[0].prompt == prompt, "prompt", "Accepted prompt differs from frozen task.")
        elapsed = (timestamp(creation[-1].at) - timestamp(accepted[0].at)).total_seconds()
        require(
            elapsed <= policy.timeout_seconds
            or attempt.outcome == "timeout"
            or (measured and attempt.outcome in {"auth_failure", "infrastructure_error"}),
            "time_limit",
            "Creation exceeds the declared policy time cap.",
        )
        if measured and attempt.outcome == "timeout":
            require(
                elapsed >= policy.timeout_seconds and bool(creation[-1].evidence),
                "timeout",
                "Generation timeout needs the elapsed budget and terminal observation evidence.",
            )
            require(attempt.artifact is None, "timeout", "Timeout is not a final delivery.")
    require(
        policy.allow_followups or not any(e.kind == "followup" for e in creation),
        "followup_policy",
        "This policy does not allow follow-up inputs.",
    )
    require(
        policy.allow_repairs or not any(e.kind == "repair" for e in creation),
        "repair_policy",
        "This policy does not allow repair inputs.",
    )
    for index, event in enumerate(creation):
        if event.kind == "followup":
            require(
                index > 0 and creation[index - 1].kind == "clarification",
                "followup_policy",
                "Follow-up must follow a logged clarification question.",
            )
    require(
        evaluation[0].kind == "evaluation_started" and evaluation[-1].kind == "evaluation_finished",
        "trajectory",
        "Evaluation needs explicit start and finish events.",
    )
    require(
        timestamp(evaluation[0].at) >= timestamp(creation[-1].at),
        "trajectory",
        "Final-artifact evaluation cannot precede final delivery.",
    )
    if attempt.outcome == "delivered":
        require(attempt.artifact is not None, "artifact", "Delivered outcome needs an artifact.")
    artifact = attempt.artifact
    if artifact:
        require(
            artifact.kind in policy.artifact_kinds, "artifact", "Artifact kind violates policy."
        )
        if artifact.kind == "public_url":
            require(artifact.url is not None, "artifact", "Public URL is missing.")
            public_url(artifact.url, artifact=True)
            require(
                artifact.bundle_sha256 is None,
                "artifact",
                "A remote URL is not a frozen bundle; do not claim a bundle hash.",
            )
        else:
            require(artifact.bundle_sha256 is not None, "artifact", "Bundle hash is missing.")
            require(
                artifact.url is None, "artifact", "Native bundle references do not contain URLs."
            )
        require(
            creation[-1].artifact_id == artifact.id
            and all(e.artifact_id == artifact.id for e in evaluation),
            "artifact_mismatch",
            "Creation/evaluation must identify the same final artifact.",
        )
    else:
        require(
            all(e.artifact_id is None for e in evaluation),
            "artifact_mismatch",
            "Evaluation references an undeclared artifact.",
        )
    expected = {c.id: c for c in policy.criteria}
    verdicts = attempt.result.criteria
    require(
        len(verdicts) == len(expected) and {v.criterion_id for v in verdicts} == set(expected),
        "criteria",
        "Every trusted criterion must appear exactly once.",
    )
    observations = {e.id: e for e in evaluation if e.kind == "observation" and e.evidence}
    unscored_outcomes = {"auth_failure", "infrastructure_error"}
    if not measured:
        unscored_outcomes.add("timeout")
    infra = attempt.outcome in unscored_outcomes
    weighted = 0.0
    for verdict in verdicts:
        criterion = expected[verdict.criterion_id]
        require(
            set(verdict.evidence_events) <= set(observations),
            "evidence_reference",
            "Verdicts must reference evidence-backed evaluation observations.",
        )
        if verdict.status not in {"not_tested", "infra_error"}:
            require(
                bool(verdict.evidence_events), "missing_evidence", "Verdict lacks observations."
            )
        if verdict.status == "infra_error":
            require(verdict.score is None, "score", "Infrastructure errors are not scored zero.")
            infra = True
        else:
            require(
                verdict.score is not None and verdict.score <= criterion.max_score,
                "score",
                "Criterion score is outside the trusted scale.",
            )
            if verdict.status in {"failed", "not_tested"}:
                require(verdict.score == 0, "score", "Failed/not-tested criteria earn zero.")
            elif verdict.status == "passed":
                require(
                    verdict.score == criterion.max_score, "score", "Pass must earn full credit."
                )
            else:
                require(
                    criterion.allow_partial and 0 < verdict.score < criterion.max_score,
                    "score",
                    "This policy does not allow that partial score.",
                )
            weighted += verdict.score / criterion.max_score * criterion.weight
            if policy.id == "tetris-browser-pilot-v1" and criterion.id in {
                "line-score",
                "readability",
                "guidance",
                "feedback",
                "layout",
            }:
                require(
                    verdict.score in {0, 5, 10},
                    "score",
                    "Frozen pilot line-score/UX anchors are 0, 5 or 10.",
                )
        if attempt.outcome == "build_failure":
            require(
                verdict.status in {"failed", "not_tested"},
                "score",
                "A reported build failure cannot earn credit.",
            )
        if measured and attempt.outcome == "timeout":
            require(
                verdict.status == "not_tested",
                "timeout",
                "No final game was delivered: criteria are not_tested, not observed defects.",
            )
        if attempt.outcome in unscored_outcomes:
            require(verdict.status == "infra_error", "score", "Uncompleted evaluation is unscored.")
    total = (
        None
        if infra
        else round(weighted / sum(c.weight for c in policy.criteria) * policy.total_max, 6)
    )
    if policy.time_score and not infra:
        rule = policy.time_score
        by_id = {v.criterion_id: v for v in verdicts}
        timed = by_id[rule.criterion_id]
        eligible = attempt.outcome == "delivered" and all(
            by_id[c].status == "passed" for c in rule.required_passes
        )
        elapsed = (
            (timestamp(creation[-1].at) - timestamp(accepted[0].at)).total_seconds()
            if eligible
            else policy.timeout_seconds
        )
        fraction = max(
            0.0,
            min(
                1.0,
                (policy.timeout_seconds - elapsed)
                / (policy.timeout_seconds - rule.full_credit_seconds),
            ),
        )
        time_score = round(expected[rule.criterion_id].max_score * fraction, 6)
        require(
            timed.score is not None
            and math.isclose(timed.score, time_score, rel_tol=0, abs_tol=0.000001),
            "time_score",
            "Delivery-time credit must match the recorded timeline and playable gates.",
        )
    require(
        (total is None and attempt.result.total is None)
        or (
            total is not None
            and attempt.result.total is not None
            and math.isclose(total, attempt.result.total, rel_tol=0, abs_tol=0.000001)
        ),
        "total",
        "Submitted total does not match trusted-policy recomputation.",
    )
    result = {"attempt": attempt.id, "outcome": attempt.outcome, "recomputed_total": total}
    if measured:
        from .measurements import check_configuration, measure_attempt

        check_configuration(attempt.result, policy.measurement, blobs, references)
        result["measurement"] = measure_attempt(attempt, policy, total)
    else:
        require(
            attempt.result.configuration is None,
            "schema_version",
            "Structured evaluator configuration requires public-submission/0.2.",
        )
    return result


def validate(directory: Path, trusted_root: Path, *, override: dict | None = None) -> dict:
    """Return machine-readable structural findings, never a gameplay PASS or attestation."""
    warnings = [
        "Structure checks do not prove truth, completeness, game quality or independent review.",
        "Secret checks are heuristic; inspect text, images and linked media before upload.",
    ]
    try:
        raw = read_file(directory, "manifest.json") if override is None else encode(override)
        scan_text(raw)
        parsed = parse_json(raw)
        scan_text(encode(parsed))
        submission = model(Submission, parsed)
        require("REPLACE" not in raw.decode(), "draft", "Replace draft placeholders first.")
        policy, policy_hash, prompt = load_policy(trusted_root, submission.policy_id)
        require(
            submission.schema_version.rsplit("/", 1)[1] == policy.schema_version.rsplit("/", 1)[1],
            "schema_version",
            "Manifest and trusted policy schema versions must match; do not relabel old runs.",
        )
        if policy.task.kind == "browser_protocol":
            require(
                submission.source_kind == "browser_observation"
                and all(a.result.mode != "deterministic" for a in submission.attempts),
                "source",
                "Manual browser evidence is not native Harbor/deterministic verification.",
            )
        require(submission.policy_sha256 == policy_hash, "policy", "Trusted policy hash mismatch.")
        pub = submission.publication
        require(
            all(
                (
                    pub.public_release_confirmed,
                    pub.rights_confirmed,
                    pub.sensitive_data_checked,
                    pub.all_attempts_disclosed,
                )
            ),
            "publication",
            "Explicit public release, rights, privacy and attempt attestations required.",
        )
        require(
            len(submission.attempts) <= policy.attempt_limit,
            "attempts",
            "Attempt count exceeds frozen policy; disclose it, do not cherry-pick.",
        )
        require(
            len({a.id for a in submission.attempts}) == len(submission.attempts),
            "attempts",
            "Duplicate attempt ids.",
        )
        require(
            submission.creator.model is not None
            or submission.creator.model_source in {"unknown", "not_applicable"},
            "model",
            "A missing model needs an explicit unknown/not-applicable source.",
        )
        names = [f.path for f in submission.files]
        require(
            len(set(names)) == len(names) and "manifest.json" not in names,
            "file_list",
            "File allowlist has duplicates or includes the manifest itself.",
        )
        require(
            inventory(directory) == set(names) | {"manifest.json"},
            "unlisted_files",
            "Only the manifest and allowlisted evidence may be in the package.",
        )
        blobs = {}
        size = len(raw)
        for entry in submission.files:
            suffix = PurePosixPath(entry.path).suffix.lower()
            require(
                suffix in TEXT_SUFFIXES | IMAGE_SUFFIXES,
                "file_type",
                "Only JSON/JSONL/text and PNG/JPEG/WebP evidence; no executables or archives.",
            )
            data = read_file(directory, entry.path)
            require(
                entry.sha256 == digest(data) and entry.bytes == len(data),
                "file_hash",
                "Evidence hash or size mismatch; do not rewrite reviewed bytes.",
            )
            size += len(data)
            require(
                size <= MAX_PACKAGE,
                "package_size",
                "Package exceeds 20 MiB; use public references.",
            )
            if suffix in TEXT_SUFFIXES:
                scan_text(data)
                if suffix == ".json":
                    scan_text(encode(parse_json(data)))
            else:
                valid = (
                    (suffix == ".png" and data.startswith(b"\x89PNG\r\n\x1a\n"))
                    or (suffix in {".jpg", ".jpeg"} and data.startswith(b"\xff\xd8\xff"))
                    or (suffix == ".webp" and data[:4] == b"RIFF" and data[8:12] == b"WEBP")
                )
                require(valid, "file_type", "Image signature does not match its extension.")
            blobs[entry.path] = data
        external_ids = [e.id for e in submission.external_evidence]
        require(
            len(external_ids) == len(set(external_ids)),
            "evidence_reference",
            "Duplicate external ids.",
        )
        for entry in submission.external_evidence:
            public_url(entry.url)
        if external_ids:
            warnings.append(
                "External bytes were NOT downloaded or verified; maintainer review required."
            )
        references = set(names) | {f"external:{i}" for i in external_ids}
        # Trajectories cannot serve as circular evidence for their own assertions.
        trajectory_names = {p for a in submission.attempts for p in (a.creation, a.evaluation)}
        references -= trajectory_names | set(submission.score_addenda)
        require(
            len(trajectory_names) == 2 * len(submission.attempts),
            "trajectory",
            "Each attempt needs distinct creation and evaluation files.",
        )
        global_ids = set()
        attempts = [
            check_attempt(a, policy, prompt, blobs, references, global_ids)
            for a in submission.attempts
        ]
        for attempt in submission.attempts:
            if attempt.artifact and attempt.artifact.kind == "harbor_bundle":
                require(
                    submission.source_kind == "harbor",
                    "source",
                    "A native Harbor artifact needs native Harbor provenance.",
                )
            if submission.creator.model_source == "visible_ui":
                events = load_events(blobs[attempt.creation], "creation", references)
                sends = [event for event in events if event.kind == "prompt_accepted"]
                if sends:
                    require(
                        any(
                            event.kind == "model_selected"
                            and event.evidence
                            and event.seq < sends[0].seq
                            for event in events
                        ),
                        "model",
                        "Visible model claims need pre-send model-selection evidence.",
                    )
        for cost in submission.costs:
            require(set(cost.evidence) <= references, "cost", "Cost references missing evidence.")
            if cost.kind == "unknown":
                require(
                    cost.amount is None and cost.currency is None,
                    "cost",
                    "Unknown cost is null, not zero.",
                )
            elif cost.kind == "no_model_call":
                require(
                    cost.amount == 0 and cost.currency is not None,
                    "cost",
                    "A no-model-call record must explicitly state zero and currency.",
                )
            else:
                require(
                    cost.amount is not None and cost.currency is not None and bool(cost.evidence),
                    "cost",
                    "Known cost needs amount, currency and public evidence.",
                )
        from .score_addenda import validate_addenda

        addenda = validate_addenda(submission, policy, blobs, references, trusted_root)
        if pub.redactions or pub.capture_gaps:
            warnings.append(
                "Redactions/capture gaps are declared; review whether conclusions remain supported."
            )
        if any(not a.result.creation_context_hidden for a in submission.attempts):
            warnings.append(
                "Evaluation was not blind to creation context; disclose this limitation."
            )
        if submission.kind == "synthetic_example":
            warnings.append("Synthetic format example, not a benchmark result.")
        return {
            "structure_valid": True,
            "review_status": "unverified",
            "id": submission.id,
            "revision": submission.revision,
            "kind": submission.kind,
            "manifest_sha256": digest(raw),
            "attempts": attempts,
            "score_addenda": addenda,
            "errors": [],
            "warnings": warnings,
        }
    except (ValueError, OSError, KeyError, TypeError, RecursionError) as exc:
        message = (
            str(exc) if isinstance(exc, InvalidSubmission) else "Unreadable or malformed evidence."
        )
        return {
            "structure_valid": False,
            "review_status": "needs_changes",
            "attempts": [],
            "errors": [{"code": getattr(exc, "code", "malformed"), "message": message}],
            "warnings": warnings,
        }


def encode(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode()


def initialize(root: Path, output: Path, policy_id: str, submission_id: str) -> dict:
    require(
        bool(re.fullmatch(r"[a-z0-9][a-z0-9-]{0,79}", submission_id)),
        "id",
        "Invalid submission id.",
    )
    policy, policy_hash, _ = load_policy(root, policy_id)
    draft = {
        "schema_version": policy.schema_version.replace("public-policy", "public-submission"),
        "id": submission_id,
        "revision": 1,
        "kind": "result",
        "policy_id": policy.id,
        "policy_sha256": policy_hash,
        "author": "REPLACE",
        "affiliation": "REPLACE (or none)",
        "creator": {
            "platform": "REPLACE",
            "harness_version": None,
            "model": None,
            "model_source": "unknown",
            "effort": None,
        },
        "environment": "REPLACE with runtime/browser versions and conditions",
        "source_kind": "browser_observation"
        if policy.task.kind == "browser_protocol"
        else "harbor",
        "source_ref": "REPLACE with task-scoped run/trial reference",
        "attempts": [
            {
                "id": "attempt-1",
                "outcome": "delivered",
                "artifact": None,
                "creation": "creation.jsonl",
                "evaluation": "evaluation.jsonl",
                "result": {
                    "evaluator": "REPLACE",
                    "model": None,
                    "mode": "human" if policy.task.kind == "browser_protocol" else "deterministic",
                    "creation_context_hidden": False,
                    "criteria": [
                        {
                            "criterion_id": c.id,
                            "status": "not_tested",
                            "score": 0,
                            "reason": "Not evaluated",
                            "evidence_events": [],
                        }
                        for c in policy.criteria
                    ],
                    "total": 0,
                },
            }
        ],
        "files": [
            {"path": name, "sha256": None, "bytes": None}
            for name in ("creation.jsonl", "evaluation.jsonl")
        ],
        "external_evidence": [],
        "costs": [
            {
                "kind": "unknown",
                "component": "creator",
                "amount": None,
                "currency": None,
                "basis": "No supported cost evidence available",
                "evidence": [],
            }
        ],
        "publication": {
            "public_release_confirmed": False,
            "rights_confirmed": False,
            "sensitive_data_checked": False,
            "all_attempts_disclosed": False,
            "license": "REPLACE with the evidence's permitted public license",
            "redactions": [],
            "capture_gaps": [],
            "limitations": [],
        },
    }
    if policy.measurement:
        rule = policy.measurement
        draft["attempts"][0]["result"]["configuration"] = {
            "harness_version": None,
            "effort": None,
            "instructions_file": None,
            "instructions_sha256": None,
            "tools": [],
            "access_mode": rule.allowed_access[0],
            "browser": "REPLACE with actual browser name",
            "browser_version": None,
            "viewport_width": rule.viewport_width,
            "viewport_height": rule.viewport_height,
            "clock": rule.clock,
        }
    output.mkdir(parents=True, exist_ok=False)
    (output / "manifest.json").write_bytes(encode(draft))
    for name in ("creation.jsonl", "evaluation.jsonl"):
        (output / name).write_bytes(b"")
    return {
        "draft": str(output),
        "public_release_confirmed": False,
        "next": "Read docs/submissions.md; record during execution. No browser/model was started.",
    }


def prepare(directory: Path, root: Path, output: Path, *, confirmed: bool) -> dict:
    require(confirmed, "publication", "Inspect the allowlist, then supply --confirm-public.")
    require(
        not output.exists() and not output.is_symlink(), "destination", "Never overwrite a package."
    )
    require(
        not output.resolve().is_relative_to(directory.resolve()),
        "destination",
        "Output must be outside the source package.",
    )
    draft = model(Submission, parse_json(read_file(directory, "manifest.json")))
    require(
        "REPLACE" not in json.dumps(draft.model_dump()),
        "draft",
        "Replace draft placeholders first.",
    )
    snapshots = {}
    for entry in draft.files:
        data = read_file(directory, entry.path)
        require(
            entry.sha256 in {None, digest(data)} and entry.bytes in {None, len(data)},
            "file_hash",
            "Existing evidence hash/size mismatch; do not silently reseal changed data.",
        )
        entry.sha256, entry.bytes = digest(data), len(data)
        snapshots[entry.path] = data
    record = draft.model_dump()
    result = validate(directory, root, override=record)
    require(
        result["structure_valid"],
        result["errors"][0]["code"] if result["errors"] else "invalid",
        result["errors"][0]["message"] if result["errors"] else "Invalid package.",
    )
    # Recheck bytes just before copying; never glob a whole job directory into Git.
    require(
        all(read_file(directory, name) == data for name, data in snapshots.items()),
        "file_hash",
        "Evidence changed during packaging.",
    )
    output.mkdir(parents=True, exist_ok=False)
    for name, data in snapshots.items():
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    (output / "manifest.json").write_bytes(encode(record))
    return {
        **result,
        "prepared": str(output),
        "uploaded": False,
        "files": ["manifest.json", *sorted(snapshots)],
        "next": "Review these exact files, commit only this package to your fork, then open a PR.",
    }


def validate_tree(directory: Path, root: Path) -> dict:
    try:
        files = inventory(directory, max_entries=60201)
        # In trusted-review mode, incoming data cannot erase or rewrite accepted revisions.
        baseline = root / "submissions"
        if baseline.is_dir() and directory.resolve() != baseline.resolve():
            for name in inventory(baseline, max_entries=60201) - {"README.md"}:
                require(
                    name in files and read_file(baseline, name) == read_file(directory, name),
                    "immutable_revision",
                    "Merged evidence is immutable; add a correction revision.",
                )
        manifests = sorted(name for name in files if name.endswith("/manifest.json"))
        require(
            len(manifests) <= 100, "package_size", "Validate at most 100 packages per invocation."
        )
        covered = {"README.md"}
        results = []
        revisions = {}
        for name in manifests:
            parts = PurePosixPath(name).parts
            require(len(parts) == 3, "layout", "Use submissions/<id>/rNNN/manifest.json.")
            parent = str(PurePosixPath(name).parent)
            covered.update(p for p in files if p.startswith(parent + "/"))
            result = validate(directory / parent, root)
            if result["structure_valid"]:
                require(
                    result["id"] == parts[0] and f"r{result['revision']:03}" == parts[1],
                    "layout",
                    "Submission identity/revision must match its directory.",
                )
                require(
                    result["kind"] == "result",
                    "synthetic",
                    "Examples cannot be submitted as results.",
                )
                revisions.setdefault(result["id"], []).append(result["revision"])
                for addendum in result["score_addenda"]:
                    source_path = f"{parts[0]}/r{addendum['source_revision']:03}/manifest.json"
                    require(
                        source_path in files
                        and digest(read_file(directory, source_path))
                        == addendum["source_manifest_sha256"],
                        "immutable_revision",
                        "Addendum must pin the actual earlier manifest.",
                    )
            results.append({"package": parent, **result})
        require(files <= covered, "layout", "Unpackaged files are not accepted under submissions/.")
        require(
            all(sorted(values) == list(range(1, max(values) + 1)) for values in revisions.values()),
            "revision",
            "Keep consecutive revisions from r001; do not hide earlier submissions.",
        )
        return {
            "structure_valid": all(r["structure_valid"] for r in results),
            "packages": results,
            "count": len(results),
            "review_status": "unverified",
        }
    except (ValueError, OSError) as exc:
        return {
            "structure_valid": False,
            "packages": [],
            "count": 0,
            "errors": [
                {
                    "code": getattr(exc, "code", "malformed"),
                    "message": str(exc)
                    if isinstance(exc, InvalidSubmission)
                    else "Invalid submission tree.",
                }
            ],
        }
