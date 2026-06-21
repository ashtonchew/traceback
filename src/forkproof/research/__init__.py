"""Plan 007 research contracts.

The research slice is intentionally isolated from the core ForkProof path. It
models depth-two scheduling, candidate selection, capability gates, and report
records without becoming a dependency of forkpoints, witnesses, controls, or
releases.
"""

from .capability import CapabilityOutcome, classify_capability_gate
from .models import (
    CapabilityGateRecord,
    ChildCandidate,
    DepthTwoRunRecord,
    FlatComparisonReport,
    ResearchSkip,
    ResearchLineage,
    SchedulerConfig,
    SchedulerDecision,
    StopEvent,
    TransferTrainingReport,
)
from .scheduler import ResearchScheduler
from .selection import select_promising_child

__all__ = [
    "CapabilityGateRecord",
    "CapabilityOutcome",
    "ChildCandidate",
    "DepthTwoRunRecord",
    "FlatComparisonReport",
    "ResearchScheduler",
    "ResearchSkip",
    "ResearchLineage",
    "SchedulerConfig",
    "SchedulerDecision",
    "StopEvent",
    "TransferTrainingReport",
    "classify_capability_gate",
    "select_promising_child",
]
