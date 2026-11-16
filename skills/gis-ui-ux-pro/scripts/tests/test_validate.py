import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import validate_data  # noqa: E402

FIX = Path(__file__).parent / "fixtures" / "data"


class TestValidate(unittest.TestCase):
    def mutated(self, rel, old, new):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        d = Path(tmp.name) / "data"
        shutil.copytree(FIX, d)
        p = d / rel
        text = p.read_text(encoding="utf-8-sig")
        self.assertIn(old, text)
        p.write_text(text.replace(old, new, 1), encoding="utf-8", newline="")
        return d

    def one_error(self, d, needle):
        errs = validate_data.validate(d)
        self.assertEqual(len(errs), 1, errs)
        self.assertIn(needle, errs[0])

    def test_fixtures_valid(self):
        self.assertEqual(validate_data.validate(FIX), [])

    def test_missing_column(self):
        d = self.mutated("palettes.csv", ",cvd_safe,", ",cvd,")
        errs = validate_data.validate(d)
        self.assertEqual(len(errs), 1, errs)
        self.assertIn("palettes.csv", errs[0])
        self.assertIn("cvd_safe", errs[0])

    def test_duplicate_id(self):
        d = self.mutated("widgets.csv", "W-02,", "W-01,")
        self.one_error(d, "W-01")

    def test_bad_severity(self):
        d = self.mutated("rules.csv", ",critical,", ",urgent,")
        self.one_error(d, "A-01")
        d = self.mutated("stacks/mapbox-maplibre.csv", ",medium,", ",meh,")
        self.one_error(d, "MB-02")

    def test_stack_category_unchecked(self):
        d = self.mutated("stacks/mapbox-maplibre.csv", ",layers,", ",controls,")
        self.assertEqual(validate_data.validate(d), [])

    def test_ragged_row_reports_not_raises(self):
        d = self.mutated("rules.csv", "T-01,temporal,Time slider shows range,time slider range playback,Label start and end dates,Unlabeled scrubbers,Context for the time window,low,synth,,,,",
                         "T-01,temporal")
        errs = validate_data.validate(d)
        self.assertTrue(errs)
        self.assertTrue(all("T-01" in e or "rules.csv" in e for e in errs))

    def test_bad_evidence(self):
        d = self.mutated("palettes.csv", ",synth,\nP-DIV", ",guess,\nP-DIV")
        self.one_error(d, "P-SEQ")

    def test_sourced_without_url(self):
        d = self.mutated("palettes.csv", ",sourced,https://example.org/src", ",sourced,")
        self.one_error(d, "P-DIV")

    def test_bad_hex(self):
        d = self.mutated("palettes.csv", "#6BAED6", "#12345G")
        self.one_error(d, "P-SEQ")

    def test_dangling_reference(self):
        d = self.mutated("problems.csv", "L-01;Y-01", "L-01;Y-99")
        self.one_error(d, "Y-99")
        d = self.mutated("problems.csv", ",LY-02,", ",LY-77,")
        self.one_error(d, "LY-77")
        d = self.mutated("problems.csv", ",P-DIV,", ",P-NOPE,")
        self.one_error(d, "P-NOPE")
        d = self.mutated("widgets.csv", ",T-01,", ",T-99,")
        self.one_error(d, "T-99")


if __name__ == "__main__":
    unittest.main()
