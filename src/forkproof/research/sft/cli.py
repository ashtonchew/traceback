"""CLI for the SFT extension pipeline."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from forkproof.research.sft.canonical_pipeline import run_canonical_sft_pipeline
from forkproof.research.sft.loader import DEFAULT_MOCK_FIXTURE
from forkproof.research.sft.pipeline import run_sft_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the ForkProof SFT data-quality pipeline.",
    )
    subparsers = parser.add_subparsers(dest="command")

    mock = subparsers.add_parser("mock", help="Run the development JSONL/mock pipeline.")
    mock.add_argument(
        "--input",
        type=Path,
        default=Path(DEFAULT_MOCK_FIXTURE),
        help="ForkProof trace export JSONL (default: mock fixture)",
    )
    mock.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/sft/mock_run"),
        help="Directory for reports and exported datasets",
    )
    mock.add_argument(
        "--source-label",
        default=None,
        help="Provenance label for reports (default: input filename)",
    )

    canonical = subparsers.add_parser(
        "canonical",
        help="Run the manifest-backed Plan 008 + Plan 005 SFT pipeline.",
    )
    canonical.add_argument("--qabench-report", type=Path, required=True)
    canonical.add_argument("--release-proof", type=Path, required=True)
    canonical.add_argument(
        "--plan-008-manifest",
        type=Path,
        default=Path("docs/plans/evidence/008/MANIFEST.json"),
    )
    canonical.add_argument(
        "--plan-005-manifest",
        type=Path,
        default=Path("docs/plans/evidence/005/MANIFEST.json"),
    )
    canonical.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/forkproof/research/sft/runs/manual"),
    )

    # Backward-compatible root flags keep older mock invocations working.
    parser.add_argument(
        "--input",
        type=Path,
        default=Path(DEFAULT_MOCK_FIXTURE),
        help="ForkProof trace export JSONL (default: mock fixture)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/sft/mock_run"),
        help="Directory for reports and exported datasets",
    )
    parser.add_argument(
        "--source-label",
        default=None,
        help="Provenance label for reports (default: input filename)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "canonical":
        result = run_canonical_sft_pipeline(
            qabench_report_path=args.qabench_report,
            release_proof_path=args.release_proof,
            plan_008_manifest_path=args.plan_008_manifest,
            plan_005_manifest_path=args.plan_005_manifest,
            output_dir=args.output,
        )
        print(f"Wrote canonical pipeline outputs to {result.output_dir}")
        print(f"  raw SFT examples:      {result.raw_sft_examples}")
        print(f"  hardened SFT examples: {result.hardened_sft_examples}")
        print(f"  rejected hack records: {result.rejected_hack_records}")
        print(f"  quarantined records:   {len(result.quarantined)}")
        return 0

    if not args.input.is_file():
        print(f"error: input file not found: {args.input}", file=sys.stderr)
        return 1

    result = run_sft_pipeline(
        args.input,
        args.output,
        source_label=args.source_label,
    )

    print(f"Wrote pipeline outputs to {result.output_dir}")
    print(f"  raw SFT examples:      {result.raw_sft_examples}")
    print(f"  hardened SFT examples: {result.hardened_sft_examples}")
    print(f"  rejected hack records: {result.rejected_hack_records}")
    print(
        "  contamination (raw):   "
        f"{result.metrics.raw_contamination_rate * 100:.1f}%"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
