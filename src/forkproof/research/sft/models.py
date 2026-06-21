"""Data models for the SFT / training-data extension."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

TraceSource = Literal["mock", "forkproof_export"]

REQUIRED_FIELDS = (
    "trace_id",
    "task_id",
    "task_prompt",
    "assistant_output",
    "raw_reward",
    "patched_reward",
    "is_hack",
    "is_legit",
)


@dataclass(frozen=True, slots=True)
class TraceRecord:
    """One ForkProof trace row ready for filtering and SFT export."""

    trace_id: str
    task_id: str
    task_prompt: str
    assistant_output: str
    raw_reward: float
    patched_reward: float
    is_hack: bool
    is_legit: bool
    exploit_cluster: str | None = None
    environment_version: str | None = None
    grader_version: str | None = None
    patched_grader_version: str | None = None
    hud_trace_url: str | None = None
    witness_id: str | None = None
    release_proof_id: str | None = None
    needs_review: bool = False
    source: TraceSource = "forkproof_export"

    def to_dict(self) -> dict[str, object]:
        return {
            "trace_id": self.trace_id,
            "task_id": self.task_id,
            "task_prompt": self.task_prompt,
            "assistant_output": self.assistant_output,
            "raw_reward": self.raw_reward,
            "patched_reward": self.patched_reward,
            "is_hack": self.is_hack,
            "is_legit": self.is_legit,
            "exploit_cluster": self.exploit_cluster,
            "environment_version": self.environment_version,
            "grader_version": self.grader_version,
            "patched_grader_version": self.patched_grader_version,
            "hud_trace_url": self.hud_trace_url,
            "witness_id": self.witness_id,
            "release_proof_id": self.release_proof_id,
            "needs_review": self.needs_review,
            "source": self.source,
        }
