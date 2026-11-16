import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEARCH = str(HERE.parent / "search.py")
FIX = str(HERE / "fixtures" / "data")


def run(*args, env=None):
    e = dict(os.environ, **(env or {}))
    return subprocess.run([sys.executable, SEARCH, *args, "--data-dir", FIX],
                          capture_output=True, text=True, encoding="utf-8", env=e)


class TestSearchCli(unittest.TestCase):
    def test_missing_data_dir_is_usage_error(self):
        r = subprocess.run([sys.executable, SEARCH, "flood", "--data-dir", "/nonexistent/nowhere"],
                           capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 2)
        self.assertIn("--data-dir not found", r.stderr)
        self.assertNotIn("Traceback", r.stderr)

    def test_markdown_output_has_result_heading(self):
        r = run("map dominant sidebar")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("### Result 1", r.stdout)

    def test_json_output_parses(self):
        r = run("map dominant sidebar", "--json")
        self.assertIsInstance(json.loads(r.stdout)["hits"], list)

    def test_explicit_domain_shown(self):
        r = run("color", "-d", "palette")
        self.assertIn("Domain: palette", r.stdout)

    def test_no_match_exits_zero_with_suggestions(self):
        r = run("zzzz qqqq")
        self.assertEqual(r.returncode, 0)
        self.assertIn("No matches", r.stdout)
        self.assertIn("Try:", r.stdout)

    def test_stopword_only_query(self):
        r = run("the and of")
        self.assertEqual(r.returncode, 0)
        self.assertIn("No matches", r.stdout)

    def test_ascii_console_does_not_crash(self):
        r = run("map dominant sidebar", "-d", "rule", env={"PYTHONIOENCODING": "ascii"})
        self.assertEqual(r.returncode, 0)
        self.assertNotIn("UnicodeEncodeError", r.stderr)
        self.assertIn("###", r.stdout)
        self.assertIn("→", r.stdout)

    def test_invalid_domain_rc2(self):
        self.assertEqual(run("x", "-d", "foo").returncode, 2)

    def test_n_out_of_range_rc2(self):
        self.assertEqual(run("x", "-n", "50").returncode, 2)

    def test_direction_domain_search(self):
        r = run("night operations status", "-d", "direction")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("night-ops", r.stdout)

    def test_intensity_requires_blueprint(self):
        r = run("flood", "--intensity", "bold")
        self.assertEqual(r.returncode, 2)
        self.assertIn("--intensity", r.stderr)
        self.assertNotIn("Traceback", r.stderr)

    def test_direction_requires_blueprint(self):
        r = run("flood", "--direction", "night-ops")
        self.assertEqual(r.returncode, 2)
        self.assertIn("--direction", r.stderr)
        self.assertNotIn("Traceback", r.stderr)

    @unittest.expectedFailure  # Task 5 removes this decorator
    def test_unknown_direction_exit_2(self):
        r = run("flood river gauge", "--blueprint", "--direction", "nope")
        self.assertEqual(r.returncode, 2)
        self.assertIn("Unknown direction 'nope'", r.stderr)
        self.assertIn("night-ops", r.stderr)


if __name__ == "__main__":
    unittest.main()
