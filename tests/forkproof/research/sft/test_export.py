"""Tests for SFT export and pipeline (Phase 3)."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from forkproof.research.sft import DEFAULT_MOCK_FIXTURE, load_traces
from forkproof.research.sft.cli import main as cli_main
from forkproof.research.sft.export import (
    DEFAULT_SYSTEM_PROMPT,
    export_metadata,
    export_rejected_hacks_audit,
    export_sft_jsonl,
    trace_to_fireworks_example,
    validate_fireworks_example,
)
from forkproof.research.sft.filter import filter_traces
from forkproof.research.sft.pipeline import run_sft_pipeline
from mock_expectations import MOCK_METRICS

REPO_ROOT = Path(__file__).resolve().parents[4]
MOCK_FIXTURE = REPO_ROOT / DEFAULT_MOCK_FIXTURE


class ExportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.traces = load_traces(MOCK_FIXTURE)
        self.filtered = filter_traces(self.traces)

    def test_fireworks_example_shape(self) -> None:
        example = trace_to_fireworks_example(self.traces[0])
        validate_fireworks_example(example)
        roles = [message["role"] for message in example["messages"]]  # type: ignore[index]
        self.assertEqual(roles, ["system", "user", "assistant"])

    def test_export_sft_jsonl_uses_shared_system_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "raw.jsonl"
            count = export_sft_jsonl(self.filtered.raw_sft, path, source_filter="raw_sft")
            self.assertEqual(count, MOCK_METRICS["raw_reward_one_admitted"])

            lines = path.read_text(encoding="utf-8").strip().splitlines()
            prompts = {
                json.loads(line)["messages"][0]["content"]
                for line in lines
            }
            self.assertEqual(prompts, {DEFAULT_SYSTEM_PROMPT})

    def test_hardened_export_meets_fireworks_minimum(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "hardened.jsonl"
            count = export_sft_jsonl(
                self.filtered.hardened_sft,
                path,
                source_filter="hardened_sft",
            )
            self.assertGreaterEqual(count, 3)
            self.assertEqual(count, MOCK_METRICS["hardened_reward_one_admitted"])

    def test_metadata_sidecar_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "metadata.jsonl"
            export_metadata(self.filtered.hardened_sft, path, source_filter="hardened_sft")
            row = json.loads(path.read_text(encoding="utf-8").strip().splitlines()[0])
            self.assertEqual(row["source_filter"], "hardened_sft")
            self.assertIn("trace_id", row)
            self.assertIn("raw_reward", row)
            self.assertIn("patched_reward", row)
            self.assertIn("is_hack", row)
            self.assertIn("is_legit", row)

    def test_rejected_hacks_audit_is_not_positive_sft(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rejected.jsonl"
            count = export_rejected_hacks_audit(self.filtered.rejected_hacks, path)
            self.assertEqual(count, MOCK_METRICS["rejected_hack_records"])
            row = json.loads(path.read_text(encoding="utf-8").strip().splitlines()[0])
            self.assertEqual(row["weight"], 0)
            self.assertNotIn("messages", row)

    def test_raw_export_includes_stress_only_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "raw.jsonl"
            export_sft_jsonl(self.filtered.raw_sft, path, source_filter="raw_sft")
            assistants = [
                json.loads(line)["messages"][-1]["content"].lower()
                for line in path.read_text(encoding="utf-8").strip().splitlines()
            ]
            joined = "\n".join(assistants)
            self.assertIn("patched verifier still returns reward 1", joined)
            self.assertIn("classification pending qa review", joined)

    def test_hardened_export_excludes_known_hacks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "hardened.jsonl"
            export_sft_jsonl(self.filtered.hardened_sft, path, source_filter="hardened_sft")
            assistants = [
                json.loads(line)["messages"][-1]["content"].lower()
                for line in path.read_text(encoding="utf-8").strip().splitlines()
            ]
            joined = "\n".join(assistants)
            self.assertNotIn("setuptools pytest plugin", joined)
            self.assertNotIn("conftest.py hooks", joined)
            self.assertIn("logparser.parse", joined)


class PipelineTests(unittest.TestCase):
    def test_run_sft_pipeline_writes_all_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            result = run_sft_pipeline(MOCK_FIXTURE, out)

            expected_files = [
                "contamination_table.md",
                "exploit_clusters.json",
                "contamination_chart.svg",
                "WRITEUP.md",
                "metrics.json",
                "raw_verifier_sft.jsonl",
                "hardened_verifier_sft.jsonl",
                "raw_verifier_sft.metadata.jsonl",
                "hardened_verifier_sft.metadata.jsonl",
                "rejected_hacks_audit.jsonl",
                "run_manifest.json",
            ]
            for name in expected_files:
                self.assertTrue((out / name).is_file(), msg=name)

            self.assertEqual(result.raw_sft_examples, MOCK_METRICS["raw_reward_one_admitted"])
            self.assertEqual(result.hardened_sft_examples, MOCK_METRICS["hardened_reward_one_admitted"])
            self.assertEqual(result.rejected_hack_records, MOCK_METRICS["rejected_hack_records"])

            manifest = json.loads((out / "run_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(
                manifest["export_counts"]["hardened_sft_examples"],
                MOCK_METRICS["hardened_reward_one_admitted"],
            )

    def test_cli_runs_successfully(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            code = cli_main(["--input", str(MOCK_FIXTURE), "--output", str(out)])
            self.assertEqual(code, 0)
            self.assertTrue((out / "hardened_verifier_sft.jsonl").is_file())


if __name__ == "__main__":
    unittest.main()
