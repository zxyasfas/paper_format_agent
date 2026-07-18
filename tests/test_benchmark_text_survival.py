from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "benchmark_text_survival",
    Path(__file__).resolve().parents[1] / "tools" / "benchmark_text_survival.py",
)
benchmark = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(benchmark)


class TallyTests(unittest.TestCase):
    def test_duplicate_authored_strings_are_not_double_counted(self):
        results = benchmark.tally({"a": ["same", "same"]}, ["same"])
        self.assertEqual(results["a"]["exact"], 1)
        self.assertEqual(results["a"]["guard_equivalent"], 0)
        self.assertEqual(results["a"]["lost"], ["same"])

    def test_exact_match_consumes_the_output_before_normalization(self):
        # "• item" normalizes to "item"; the single output line must not
        # satisfy both authored strings
        results = benchmark.tally({"a": ["• item"], "b": ["item"]}, ["item"])
        self.assertEqual(results["b"]["exact"], 1)
        self.assertEqual(results["a"]["exact"], 0)
        self.assertEqual(results["a"]["guard_equivalent"], 0)
        self.assertEqual(results["a"]["lost"], ["• item"])

    def test_guard_equivalent_match_uses_leftover_outputs_only(self):
        results = benchmark.tally({"a": ["• 要点"]}, ["要点"])
        self.assertEqual(results["a"]["exact"], 0)
        self.assertEqual(results["a"]["guard_equivalent"], 1)
        self.assertEqual(results["a"]["lost"], [])


if __name__ == "__main__":
    unittest.main()
