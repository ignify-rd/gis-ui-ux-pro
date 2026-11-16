import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import blueprint  # noqa: E402

FIX = HERE / "fixtures" / "data"
SEARCH = str(HERE.parent / "search.py")

SECTIONS = ["# Dashboard Blueprint: ", "## Matched problem", "## Key user questions",
            "## Layout", "## Layers", "## Palettes", "## Widgets", "## Temporal",
            "## Interactions", "## Alerts & severity", "## Pitfalls", "## Rules to apply",
            "## Signature", "## Pre-delivery checklist"]


def cli(*args):
    return subprocess.run([sys.executable, SEARCH, *args, "--data-dir", str(FIX)],
                          capture_output=True, text=True, encoding="utf-8")


class TestBlueprint(unittest.TestCase):
    def test_blueprint_matches_fixture_problem(self):
        bp = blueprint.build_blueprint("flood river gauge", FIX)
        self.assertEqual(bp["problem"]["id"], "flood-monitoring")
        self.assertIsNotNone(bp["layout"])
        self.assertEqual(bp["widgets"][0]["item"], "W-01")

    def test_blueprint_includes_checklist_with_critical_rules(self):
        bp = blueprint.build_blueprint("flood river gauge", FIX)
        self.assertNotIn("A-01", bp["problem"]["rule_ids"].split(";"))
        self.assertIn("A-01", [c["rule_id"] for c in bp["checklist"]])
        self.assertEqual([r["id"] for r in bp["rules"]], ["L-01"])

    def test_render_has_all_sections(self):
        md = blueprint.render_markdown(blueprint.build_blueprint("flood river gauge", FIX))
        pos = [md.index(s) for s in SECTIONS]
        self.assertEqual(pos, sorted(pos))
        self.assertIn("[side|map]", md)
        self.assertIn("- [ ] Is every color-coded status", md)

    def test_no_match_returns_none(self):
        self.assertIsNone(blueprint.build_blueprint("zzzz", FIX))
        r = cli("zzzz", "--blueprint")
        self.assertEqual(r.returncode, 1)
        self.assertIn("Available:", r.stdout)
        self.assertEqual(r.stderr, "")

    def test_persist_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as t:
            blueprint.persist("a", Path(t), "P")
            with self.assertRaises(FileExistsError):
                blueprint.persist("b", Path(t), "P")
            p = blueprint.persist("c", Path(t), "P", force=True)
            self.assertEqual(p.read_text(encoding="utf-8"), "c")

    def test_persist_dir_with_spaces(self):
        with tempfile.TemporaryDirectory() as t:
            p = blueprint.persist("x", Path(t) / "my project", "Vessel Watch")
            self.assertTrue(p.exists())
            self.assertEqual(p.parts[-3:], ("gis-design", "vessel-watch", "BLUEPRINT.md"))

    def test_cli_blueprint_json(self):
        r = cli("flood river gauge", "--blueprint", "-f", "json")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("problem", json.loads(r.stdout))

    def test_cli_persist_twice(self):
        with tempfile.TemporaryDirectory() as t:
            a = ["flood river gauge", "--blueprint", "--persist", "-o", t, "-p", "My Proj"]
            self.assertEqual(cli(*a).returncode, 0)
            r = cli(*a)
            self.assertEqual(r.returncode, 1)
            self.assertIn("use --force", r.stderr)
            self.assertEqual(cli(*a, "--force").returncode, 0)

    def test_persist_json_stdout_is_pure_json(self):
        with tempfile.TemporaryDirectory() as t:
            r = cli("flood river gauge", "--blueprint", "--persist", "-o", t, "-f", "json")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("problem", json.loads(r.stdout))
            self.assertIn("Saved", r.stderr)

    def test_slug_folds_accents_and_falls_back(self):
        self.assertEqual(blueprint.slug("B\u1ea3n \u0111\u1ed3 l\u0169 Hu\u1ebf"), "ban-do-lu-hue")
        with tempfile.TemporaryDirectory() as t:
            p = blueprint.persist("x", Path(t), "!!!", fallback="flood")
            self.assertEqual(p.parts[-3:], ("gis-design", "flood", "BLUEPRINT.md"))

    def test_render_shows_scores(self):
        bp = blueprint.build_blueprint("flood river gauge", FIX)
        self.assertIn(f"(score {bp['score']})", blueprint.render_markdown(bp))

    def test_json_flag_with_blueprint(self):
        r = cli("flood river gauge", "--blueprint", "--json")
        self.assertIn("problem", json.loads(r.stdout))

    def _sig(self, **kw):
        return blueprint.build_blueprint("flood river gauge", FIX, **kw)["signature"]

    def _ids(self, sig):
        return [d["id"] for d in sig["directions"]]

    def test_signature_default_intensity(self):
        sig = self._sig()
        self.assertEqual(sig["intensity"], "balanced")
        self.assertEqual(sig["intensity_source"], "problem")
        self.assertEqual(self._ids(sig), ["night-ops", "story-bold"])
        self.assertIsNone(sig["fallback_note"])
        self.assertEqual(sig["baseline"]["id"], "civic-paper")

    def test_signature_override_subtle_falls_back(self):
        sig = self._sig(intensity="subtle")
        self.assertEqual(self._ids(sig), ["night-ops", "story-bold"])
        self.assertIn("at balanced", sig["fallback_note"])
        self.assertNotEqual(sig["baseline"]["id"], sig["directions"][0]["id"])

    def test_signature_override_bold(self):
        sig = self._sig(intensity="bold")
        self.assertEqual(self._ids(sig), ["story-bold", "night-ops"])
        self.assertIsNotNone(sig["fallback_note"])

    def test_signature_forced_direction_first(self):
        self.assertEqual(self._ids(self._sig(direction_id="story-bold"))[0], "story-bold")

    def test_signature_unknown_direction_raises(self):
        with self.assertRaises(blueprint.UnknownDirection):
            self._sig(direction_id="nope")

    def test_cli_unknown_direction_exits_2(self):
        r = cli("zzz", "--blueprint", "--direction", "nope")
        self.assertEqual(r.returncode, 2)
        self.assertIn("Unknown direction 'nope'. Available:", r.stderr)

    def test_intensity_reason(self):
        sig = self._sig()
        self.assertEqual(sig["intensity_reason"], "default for flood-monitoring: ops and analyst tools")
        md = blueprint.render_markdown(blueprint.build_blueprint("flood river gauge", FIX))
        self.assertIn("- Intensity: **balanced** (default for flood-monitoring: ops and analyst tools)", md)
        sig = self._sig(intensity="bold")
        self.assertEqual(sig["intensity_reason"], "override via --intensity")
        md = blueprint.render_markdown(blueprint.build_blueprint("flood river gauge", FIX, intensity="bold"))
        self.assertIn("- Intensity: **bold** (override via --intensity)", md)

    def test_direction_keeps_separate_from_locked(self):
        sig = self._sig()
        self.assertEqual(sig["locked"], blueprint.LOCKED_BASE)
        self.assertEqual(sig["direction_keeps"], ["no blur"])
        md = blueprint.render_markdown(blueprint.build_blueprint("flood river gauge", FIX))
        self.assertLess(md.index("### Locked conventions"), md.index("### Direction must-keeps"))
        self.assertIn("### Direction must-keeps\n- no blur", md)

    def test_forced_direction_is_primary_even_out_of_range(self):
        sig = self._sig(direction_id="civic-paper", intensity="bold")
        self.assertEqual(self._ids(sig)[0], "civic-paper")
        self.assertIn("civic-paper", sig["fallback_note"])

    def test_baseline_stripped_when_no_alternative(self):
        sig = self._sig(direction_id="civic-paper", intensity="subtle")
        self.assertEqual(sig["baseline"]["id"], "civic-paper")
        self.assertTrue(sig["baseline"]["stripped"])
        md = blueprint.render_markdown(blueprint.build_blueprint(
            "flood river gauge", FIX, direction_id="civic-paper", intensity="subtle"))
        self.assertIn(f"- Safe baseline: {sig['baseline']['name']} with signature removed "
                      "(locked conventions, default markers, no hero)", md)

    def test_baseline_differs_from_chosen_by_default(self):
        sig = self._sig()
        self.assertNotIn(sig["baseline"]["id"], self._ids(sig))
        self.assertFalse(sig["baseline"]["stripped"])

    def test_baseline_skips_chosen_subtle_link(self):
        sig = blueprint.build_signature(
            {"direction_ids": "civic-paper;night-ops", "intensity_default": "subtle"}, FIX)
        self.assertEqual(self._ids(sig), ["civic-paper", "night-ops"])
        self.assertTrue(sig["baseline"]["stripped"])
        self.assertEqual(sig["baseline"]["id"], "civic-paper")

    def test_baseline_stripped_without_fallback_row(self):
        old = blueprint.BASELINE_FALLBACK
        blueprint.BASELINE_FALLBACK = "missing-direction"
        try:
            sig = self._sig()
        finally:
            blueprint.BASELINE_FALLBACK = old
        self.assertEqual(sig["baseline"]["id"], "night-ops")
        self.assertTrue(sig["baseline"]["stripped"])

    def test_duplicate_direction_ids_deduped(self):
        sig = blueprint.build_signature({"direction_ids": "night-ops;night-ops;story-bold"}, FIX)
        self.assertEqual(self._ids(sig), ["night-ops", "story-bold"])

    def test_signature_no_directions(self):
        self.assertIsNone(blueprint.build_signature({"direction_ids": ""}, FIX))
        self.assertIsNone(blueprint.build_signature({}, FIX))
        bp = blueprint.build_blueprint("flood river gauge", FIX)
        bp["signature"] = None
        self.assertIn("(no directions linked)", blueprint.render_markdown(bp))

    def test_parse_kv(self):
        self.assertEqual(blueprint.parse_kv("tone: light; labels: sparse; odd"),
                         [("tone", "light"), ("labels", "sparse"), ("", "odd")])

    def test_json_has_signature(self):
        r = cli("flood river gauge", "--blueprint", "-f", "json")
        self.assertEqual(json.loads(r.stdout)["signature"]["intensity"], "balanced")


if __name__ == "__main__":
    unittest.main()
