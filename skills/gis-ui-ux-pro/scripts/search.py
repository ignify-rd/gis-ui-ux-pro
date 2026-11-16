#!/usr/bin/env python3
"""CLI: BM25 search over the GIS UI/UX knowledge base."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core  # noqa: E402
from schema import STACKS  # noqa: E402

MAX_LEN = 300


def _fmt(v, full):
    return v if full or len(v) <= MAX_LEN else v[:MAX_LEN] + "…"


def render(res, query, full):
    d = res["domain"]
    if res["auto_detected"]:
        r = f", runner-up: {res['runner_up']}" if res["runner_up"] else ""
        dom = f"Domain: {d} (auto-detected{r})"
    else:
        dom = f"Domain: {d}"
    out = ["## GIS UI/UX Pro Search Results", "", dom, ""]
    if not res["hits"]:
        out.append(f'No matches for "{query}" in {d}.')
        out.append("Try: " + ", ".join(res["suggestions"][:8]))
        return "\n".join(out)
    for i, h in enumerate(res["hits"], 1):
        title = h.get("name") or h.get("guideline") or ""
        out += [f"### Result {i}: {title} [{h.get('id', '')}]"]
        out += [f"- **{k}:** {_fmt(v, full)}" for k, v in h.items()
                if k != "_score" and v]
        out.append("")
    return "\n".join(out)


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description="Search the GIS UI/UX knowledge base")
    p.add_argument("query")
    p.add_argument("-d", "--domain", choices=["rule", "problem", "palette", "widget", "layout", "direction"])
    p.add_argument("-s", "--stack", choices=STACKS)
    p.add_argument("-n", type=int, default=3, choices=range(1, 21), metavar="1..20")
    p.add_argument("--json", action="store_true")
    p.add_argument("--full", action="store_true")
    p.add_argument("--data-dir", default=str(core.DATA_DIR))
    p.add_argument("--blueprint", action="store_true")
    p.add_argument("--intensity", choices=["subtle", "balanced", "bold"])
    p.add_argument("--direction")
    p.add_argument("-f", "--format", choices=["markdown", "json"], default="markdown")
    p.add_argument("--persist", action="store_true")
    p.add_argument("-o", "--output-dir")
    p.add_argument("-p", "--project")
    p.add_argument("--force", action="store_true")
    args = p.parse_args(argv)

    if not Path(args.data_dir).is_dir():
        p.error(f"--data-dir not found: {args.data_dir}")
    if (args.intensity or args.direction) and not args.blueprint:
        p.error("--intensity/--direction require --blueprint")
    if args.blueprint:
        if args.json:
            args.format = "json"
        import blueprint  # lazy: created in Task 4
        return blueprint.main_blueprint(args)

    res = core.search(args.query, args.domain, args.n, args.data_dir, args.stack)
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(render(res, args.query, args.full))
    return 0


if __name__ == "__main__":
    sys.exit(main())
