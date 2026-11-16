import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import core  # noqa: E402

FIX = Path(__file__).parent / "fixtures" / "data"


class TestCore(unittest.TestCase):
    def test_normalize_folds_accents_and_case(self):
        self.assertEqual(core.normalize("Ground Déformation"), ["ground", "deformation"])

    def test_normalize_drops_stopwords(self):
        self.assertEqual(core.normalize("the of and"), [])

    def test_load_rows_handles_bom_and_multiline(self):
        rows = core.load_rows("rule", FIX)
        self.assertEqual(next(iter(rows[0])), "id")
        y = next(r for r in rows if r["id"] == "Y-01")
        self.assertEqual(y["do"], "Show legend,\nkeep it visible while panning")

    def test_bm25_ranks_matching_doc_first(self):
        bm = core.BM25([["map", "layer"], ["time", "slider"], ["legend", "key", "zebra"]])
        s = bm.scores(["zebra"])
        self.assertEqual(s.index(max(s)), 2)
        self.assertEqual(bm.scores(["unknown"]), [0.0, 0.0, 0.0])

    def test_search_returns_expected_fixture_id(self):
        r = core.search("zebrafish", "rule", data_dir=FIX)
        self.assertEqual(r["hits"][0]["id"], "Y-01")
        self.assertIn("_score", r["hits"][0])

    def test_search_empty_query_returns_no_hits_with_suggestions(self):
        r = core.search("", "rule", data_dir=FIX)
        self.assertEqual(r["hits"], [])
        self.assertTrue(r["suggestions"])

    def test_detect_domain_palette_and_problem(self):
        self.assertEqual(core.detect_domain("color ramp for ndvi")[0], "palette")
        self.assertEqual(core.detect_domain("dashboard for flood mapping")[0], "problem")
        self.assertEqual(core.detect_domain("xyzzy"), ("rule", None))

    def test_direction_hints_narrow(self):
        self.assertEqual(core.detect_domain("signature look and feel")[0], "direction")
        self.assertEqual(core.detect_domain("dark basemap colors")[0], "palette")
        self.assertNotEqual(core.detect_domain("theme")[0], "direction")

    def test_detect_domain_normalizes_plurals(self):
        self.assertEqual(core.detect_domain("layer panel colors"),
                         core.detect_domain("layer panel color"))

    def test_search_stack(self):
        r = core.search("attribution", stack="mapbox-maplibre", data_dir=FIX)
        self.assertEqual(r["domain"], "stack")
        self.assertEqual(r["hits"][0]["id"], "MB-01")

    def test_get_by_id(self):
        self.assertEqual(core.get_by_id("rule", "A-01", FIX)["severity"], "critical")
        self.assertIsNone(core.get_by_id("rule", "nope", FIX))


if __name__ == "__main__":
    unittest.main()
