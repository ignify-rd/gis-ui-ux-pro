import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = str(HERE.parent / "layout_check.py")
PAGE = (HERE / "fixtures" / "layout.html").as_uri()


@unittest.skipUnless(importlib.util.find_spec("playwright"), "playwright not installed")
class TestLayoutCheck(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        r = subprocess.run([sys.executable, SCRIPT, PAGE, "--sizes", "1280x800", "--wait", "0", "--json"],
                           capture_output=True, text=True, encoding="utf-8")
        cls.code = r.returncode
        cls.rep = json.loads(r.stdout)[0]
        cls.msgs = [(f["rule"], f["message"], f["element"]) for f in cls.rep["findings"]]

    def has(self, rule, text):
        return any(r == rule and text in m for r, m, _ in self.msgs)

    def test_exit_code_on_findings(self):
        self.assertEqual(self.code, 1)

    def test_map_share(self):
        self.assertEqual(self.rep["map"]["width"], 880)

    def test_attribution_covered(self):
        self.assertTrue(self.has("C01", "covered by #alert"), self.msgs)

    def test_control_covered_by_chat(self):
        self.assertTrue(self.has("L11", "Map control is covered by #chat"), self.msgs)

    def test_panels_overlap(self):
        self.assertTrue(self.has("L11", "Overlaps #legend"), self.msgs)

    def test_small_and_cut_text(self):
        self.assertTrue(self.has("type", "9px"), self.msgs)
        self.assertTrue(self.has("D10", "a very long"), self.msgs)

    def test_map_internals_not_reported_as_panels(self):
        self.assertFalse(any("maplibregl" in e for r, m, e in self.msgs if m.startswith("Overlaps")), self.msgs)

    def test_small_parts_and_library_text_ignored(self):
        self.assertFalse(any("thumb" in m + e for r, m, e in self.msgs), self.msgs)
        self.assertFalse(any("5 km" in m for r, m, e in self.msgs), self.msgs)

    def test_repeated_message_counted_once(self):
        tiny = [f for f in self.rep["findings"] if "tiny label" in f["message"]]
        self.assertEqual([f["count"] for f in tiny], [2])


if __name__ == "__main__":
    unittest.main()
