"""Load and verify canonical ForkProof artifacts for research training paths."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from forkproof.research.canonical.errors import CanonicalInputError


JsonObject = dict[str, Any]


@dataclass(frozen=True, slots=True)
class LoadedArtifact:
    """A parsed JSON artifact with its path and content digest."""

    path: Path
    digest: str
    data: JsonObject


def _require_object(data: Any, *, label: str) -> JsonObject:
    if not isinstance(data, dict):
        raise CanonicalInputError(f"{label} must be a JSON object")
    return data


def _read_json(path: str | Path, *, label: str) -> LoadedArtifact:
    resolved = Path(path)
    if not resolved.is_file():
        raise CanonicalInputError(f"{label} not found: {resolved}")
    raw = resolved.read_bytes()
    try:
        data = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise CanonicalInputError(f"{label} is invalid JSON: {exc.msg}") from exc
    return LoadedArtifact(
        path=resolved,
        digest=hashlib.sha256(raw).hexdigest(),
        data=_require_object(data, label=label),
    )


def assert_manifest_complete(manifest_path: str | Path, *, plan_id: str) -> LoadedArtifact:
    """Load a plan manifest and require it to represent completed evidence."""
    artifact = _read_json(manifest_path, label=f"Plan {plan_id} manifest")
    data = artifact.data
    observed_plan = str(data.get("plan_id") or "")
    if observed_plan != plan_id:
        raise CanonicalInputError(
            f"expected Plan {plan_id} manifest, got plan_id={observed_plan!r}"
        )
    if data.get("status") != "complete":
        raise CanonicalInputError(
            f"Plan {plan_id} manifest is not complete: status={data.get('status')!r}"
        )
    return artifact


def load_qabench_report(path: str | Path) -> LoadedArtifact:
    """Load the Plan 008 qabench report artifact."""
    artifact = _read_json(path, label="qabench report")
    trajectories = artifact.data.get("trajectories")
    if not isinstance(trajectories, list):
        raise CanonicalInputError("qabench report must include trajectories[]")
    return artifact


def load_release_proof(path: str | Path) -> LoadedArtifact:
    """Load a Plan 005 ReleaseProof artifact."""
    artifact = _read_json(path, label="ReleaseProof")
    required = (
        "schema_version",
        "release_proof_id",
        "proof_set_id",
        "environment_v1",
        "grader_v1_digest",
        "environment_v2",
        "grader_v2_digest",
        "patch_ref",
        "fixer_run_ref",
        "v1_results",
        "v2_results",
        "witnesses_killed",
        "controls_preserved",
        "gate_status",
        "trace_links",
        "created_at",
        "content_digest",
    )
    missing = [field for field in required if field not in artifact.data]
    if missing:
        raise CanonicalInputError(
            "ReleaseProof missing required fields: " + ", ".join(sorted(missing))
        )
    if not isinstance(artifact.data["v1_results"], list):
        raise CanonicalInputError("ReleaseProof v1_results must be a list")
    if not isinstance(artifact.data["v2_results"], list):
        raise CanonicalInputError("ReleaseProof v2_results must be a list")
    if not isinstance(artifact.data["trace_links"], list):
        raise CanonicalInputError("ReleaseProof trace_links must be a list")
    if not (
        isinstance(artifact.data.get("published_environment_ref"), str)
        or isinstance(artifact.data.get("release_candidate_ref"), str)
    ):
        raise CanonicalInputError(
            "ReleaseProof must include published_environment_ref or release_candidate_ref"
        )
    return artifact
