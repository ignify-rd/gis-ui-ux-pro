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

    def test_json_has_screen(self):
        r = subprocess.run([sys.executable, SEARCH, "flood river gauge", "--blueprint", "-f", "json",
                            "--data-dir", str(FIX)], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("slots", json.loads(r.stdout)["screen"])


if __name__ == "__main__":
    unittest.main()
