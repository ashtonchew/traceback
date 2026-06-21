"""SFT / training-data filtering extension."""

from forkproof.research.sft.errors import TraceLoadError, TraceValidationError
from forkproof.research.sft.export import DEFAULT_SYSTEM_PROMPT, export_sft_jsonl
from forkproof.research.sft.filter import FilterResult, filter_traces
from forkproof.research.sft.loader import DEFAULT_MOCK_FIXTURE, load_traces
from forkproof.research.sft.metrics import MetricsSummary, compute_metrics, render_contamination_table
from forkproof.research.sft.models import TraceRecord
from forkproof.research.sft.pipeline import PipelineResult, run_sft_pipeline
from forkproof.research.sft.report import write_phase2_report

__all__ = [
    "DEFAULT_MOCK_FIXTURE",
    "DEFAULT_SYSTEM_PROMPT",
    "FilterResult",
    "MetricsSummary",
    "PipelineResult",
    "TraceLoadError",
    "TraceRecord",
    "TraceValidationError",
    "compute_metrics",
    "export_sft_jsonl",
    "filter_traces",
    "load_traces",
    "render_contamination_table",
    "run_sft_pipeline",
    "write_phase2_report",
]
