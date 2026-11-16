import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import core  # noqa: E402

CASES = json.loads((HERE / "fixtures" / "relevance.json").read_text(encoding="utf-8"))


class TestRelevance(unittest.TestCase):
    def test_expected_id_in_top3(self):
        for c in CASES:
            with self.subTest(query=c["query"]):
                res = core.search(c["query"], domain=c["domain"], n=3,
                                  data_dir=core.DATA_DIR, stack=c.get("stack"))
                ids = [h["id"] for h in res["hits"]]
                self.assertIn(c["expected_id"], ids, f"{c['query']!r} -> {ids}")


if __name__ == "__main__":
    unittest.main()
