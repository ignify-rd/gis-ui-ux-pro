import json
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import blueprint  # noqa: E402

FIX = HERE / "fixtures" / "data"
SEARCH = str(HERE.parent / "search.py")


def bp():
    return blueprint.build_blueprint("flood river gauge", FIX)


class TestScreenSpec(unittest.TestCase):
    def test_slots_parsed_with_position_and_size(self):
        slots = {s["slot"]: s for s in bp()["screen"]["slots"]}
        self.assertEqual(list(slots), ["panel", "map"])
        self.assertEqual(slots["panel"]["position"], "left")
        self.assertEqual(slots["panel"]["size"], "320px")
        self.assertEqual(slots["map"]["position"], "fill")

    def test_widget_goes_to_first_available_slot(self):
        slots = {s["slot"]: s for s in bp()["screen"]["slots"]}
        # W-01 prefers "timeline", which LY-01 lacks, so it falls to "panel"
        self.assertEqual(slots["panel"]["widgets"], ["Time slider"])

    def test_map_corner_slots_exist_when_layout_has_map(self):
        screen = blueprint.build_screen(
            {"slots": "map: fill", "mobile_slots": ""},
            [{"item": "x", "widget": {"name": "Legend panel", "slot": "map-bottom-left;panel"}}])
        self.assertEqual(screen["slots"][-1]["slot"], "map-bottom-left")
        self.assertEqual(screen["slots"][-1]["widgets"], ["Legend panel"])

    def test_unplaced_widget_reported(self):
        screen = blueprint.build_screen(
            {"slots": "map: fill", "mobile_slots": ""},
            [{"item": "x", "widget": {"name": "Odd", "slot": "kpi-strip"}}])
        self.assertEqual(screen["unplaced"], ["Odd"])

    def test_fallback_region_when_no_preferred_slot(self):
        screen = blueprint.build_screen(
            {"slots": "panel: left, 300px; map: fill", "mobile_slots": ""},
            [{"item": "x", "widget": {"name": "Odd", "slot": "kpi-strip"}}])
        self.assertEqual(screen["slots"][0]["widgets"], ["Odd (fallback)"])
        self.assertEqual(screen["unplaced"], [])

    def test_mobile_moves_panels_into_sheet(self):
        mob = {s["slot"]: s for s in bp()["screen"]["mobile"]}
        self.assertEqual(mob["sheet"]["widgets"], ["Time slider"])
        self.assertEqual(mob["map"]["size"], "70vh")

    def test_states_and_controls_present(self):
        screen = bp()["screen"]
        self.assertEqual([s["state"] for s in screen["states"]],
                         [s["state"] for s in blueprint.SCREEN_STATES])
        self.assertTrue(any("C04" in c for c in screen["map_controls"]))

    def test_no_layout_gives_none(self):
        self.assertIsNone(blueprint.build_screen(None, []))

    def test_markdown_section_after_widgets(self):
        md = blueprint.render_markdown(bp())
        self.assertLess(md.index("## Widgets"), md.index("## Screen spec"))
        self.assertLess(md.index("## Screen spec"), md.index("## Temporal"))
        self.assertIn("| panel | left | 320px | Time slider |", md)

    def test_widget_item_that_is_an_id_resolves_exactly(self):
        self.assertEqual(bp()["widgets"][0]["widget"]["id"], "W-01")

    def test_phone_catchall_when_mobile_lacks_region(self):
        screen = blueprint.build_screen(
            {"slots": "drawer: right, 360px; map: fill", "mobile_slots": "map: fill; sheet: bottom, 30vh"},
            [{"item": "x", "widget": {"id": "a", "name": "Chart", "slot": "header"}}])
        self.assertEqual(screen["slots"][0]["widgets"], ["Chart (fallback)"])
        mob = {s["slot"]: s for s in screen["mobile"]}
        self.assertEqual(mob["sheet"]["widgets"], ["Chart (fallback)"])

    def test_phone_unplaced_reported(self):
        screen = blueprint.build_screen(
            {"slots": "drawer: right, 360px; map: fill", "mobile_slots": "map: fill; header: top, 48px"},
            [{"item": "x", "widget": {"id": "a", "name": "Chart", "slot": "drawer"}}])
        self.assertEqual(screen["phone_unplaced"], ["Chart"])
        self.assertTrue(any("No phone region for: Chart" in line
                            for line in blueprint._render_screen(screen)))

    def test_duplicates_deduped_by_id_not_name(self):
        same = {"id": "a", "name": "Chart", "slot": "panel"}
        other = {"id": "b", "name": "Chart", "slot": "panel"}
        screen = blueprint.build_screen(
            {"slots": "panel: left, 300px", "mobile_slots": ""},
            [{"item": "1", "widget": same}, {"item": "2", "widget": same}, {"item": "3", "widget": other}])
        self.assertEqual(screen["slots"][0]["widgets"], ["Chart", "Chart"])

    def test_no_map_no_corners(self):
        screen = blueprint.build_screen({"slots": "panel: left, 300px", "mobile_slots": ""}, [])
        self.assertEqual([s["slot"] for s in screen["slots"]], ["panel"])

    def test_cited_rule_ids_exist(self):
        import re
        import core
        ids = {r["id"] for r in core.load_rows("rule")}
        text = " ".join(blueprint.MAP_CONTROLS + [s["shows"] for s in blueprint.SCREEN_STATES])
        cited = set(re.findall(r"\b[A-Z]\d{2}\b", text))
        self.assertTrue(cited)
        self.assertEqual(cited - ids, set())

    def test_every_real_playbook_places_all_widgets(self):
        import core
        for p in core.load_rows("problem"):
            with self.subTest(problem=p["id"]):
                s = blueprint.build_blueprint(p["name"])["screen"]
                self.assertEqual(s["unplaced"], [])
                self.assertEqual(s["phone_unplaced"], [])

    def test_json_has_screen(self):
        r = subprocess.run([sys.executable, SEARCH, "flood river gauge", "--blueprint", "-f", "json",
                            "--data-dir", str(FIX)], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("slots", json.loads(r.stdout)["screen"])


if __name__ == "__main__":
    unittest.main()
