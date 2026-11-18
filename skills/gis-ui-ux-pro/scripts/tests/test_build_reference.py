import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import build_reference  # noqa: E402
import core  # noqa: E402

FIX = Path(__file__).parent / "fixtures" / "data"


class TestBuildReference(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.ref = Path(self.tmp.name) / "refs"

    def test_build_writes_both_files(self):
        q, c = build_reference.build(FIX, self.ref)
        self.assertTrue(q.is_file() and c.is_file())

    def test_every_rule_in_quick_reference(self):
        q, _ = build_reference.build(FIX, self.ref)
        text = q.read_text(encoding="utf-8")
        for r in core.load_rows("rule", FIX):
            self.assertIn(r["id"], text)

    def test_checklist_only_rules_with_questions(self):
        _, c = build_reference.build(FIX, self.ref)
        text = c.read_text(encoding="utf-8")
        for r in core.load_rows("rule", FIX):
            self.assertEqual(r["id"] + "," in text, bool(r["checklist"].strip()), r["id"])

    def test_checklist_has_smell_table(self):
        _, c = build_reference.build(FIX, self.ref)
        text = c.read_text(encoding="utf-8")
        self.assertIn("## Smells", text)
        self.assertIn("| Status shown by hue alone | Add a shape or label to the colour | A-01 |", text)

    def test_check_mode_detects_drift(self):
        args = ["--data-dir", str(FIX), "--ref-dir", str(self.ref)]
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            self.assertEqual(build_reference.main(args), 0)
            self.assertEqual(build_reference.main(["--check"] + args), 0)
            q = self.ref / "quick-reference.md"
            q.write_text(q.read_text(encoding="utf-8") + "x\n", encoding="utf-8")
            self.assertEqual(build_reference.main(["--check"] + args), 1)
        self.assertIn("stale: quick-reference.md", err.getvalue())


if __name__ == "__main__":
    unittest.main()
