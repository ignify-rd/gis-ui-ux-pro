import json
import re
import shlex
import subprocess
import sys
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent.parent
REPO = SKILL_DIR.parent.parent
SKILL_MD = SKILL_DIR / "SKILL.md"


def skill_text():
    return SKILL_MD.read_text(encoding="utf-8")


def frontmatter():
    lines = skill_text().splitlines()
    assert lines[0] == "---", "frontmatter must start on line 1"
    end = lines.index("---", 1)
    fm = {}
    for line in lines[1:end]:
        key, _, value = line.partition(":")
        fm[key.strip()] = value.strip()
    return fm


class TestPackaging(unittest.TestCase):
    def test_rule_count_in_skill_md(self):
        sys.path.insert(0, str(SKILL_DIR / "scripts"))
        from core import load_rows
        m = re.search(r"(\d+) rules", skill_text())
        self.assertEqual(int(m.group(1)), len(load_rows("rule")))

    def test_frontmatter_valid(self):
        fm = frontmatter()
        self.assertEqual(set(fm), {"name", "description"})
        self.assertEqual(fm["name"], "gis-ui-ux-pro")
        self.assertEqual(fm["name"], SKILL_DIR.name)
        desc = fm["description"]
        self.assertLessEqual(len(desc), 1024)
        self.assertIn("Use when", desc)
        self.assertFalse(desc.startswith(("I ", "You ")), desc[:20])

    def test_skill_md_under_300_lines(self):
        self.assertLessEqual(len(skill_text().splitlines()), 300)

    def test_no_plugin_root_variable(self):
        self.assertNotIn("CLAUDE_PLUGIN_ROOT", skill_text())

    def test_referenced_files_exist(self):
        paths = set(re.findall(r"(?:references|scripts)/[\w./-]+\.\w+", skill_text()))
        self.assertTrue(paths)
        for p in paths:
            self.assertTrue((SKILL_DIR / p).is_file(), p)

    def test_manifests_parse_and_names_match(self):
        plugin = json.loads((REPO / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        market = json.loads((REPO / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(plugin["name"], "gis-ui-ux-pro")
        self.assertEqual(market["plugins"][0]["name"], plugin["name"])
        self.assertEqual(plugin["version"], "0.1.0")
        self.assertEqual(market["plugins"][0]["version"], "0.1.0")

    def test_all_example_commands_run(self):
        blocks = re.findall(r"```[a-z]*\n(.*?)```", skill_text(), re.S)
        cmds = [l.strip() for b in blocks for l in b.splitlines() if "search.py" in l]
        self.assertTrue(cmds)
        for cmd in cmds:
            argv = shlex.split(cmd.replace("${CLAUDE_SKILL_DIR}", SKILL_DIR.as_posix()))
            i = next(n for n, a in enumerate(argv) if a.endswith("search.py"))
            argv = [sys.executable, *argv[i:]]
            self.assertNotIn("--persist", argv, "examples must not write files")
            r = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(r.returncode, 0, f"{cmd}\n{r.stderr}")


if __name__ == "__main__":
    unittest.main()
