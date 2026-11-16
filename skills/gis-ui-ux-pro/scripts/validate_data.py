"""Validate the gis-ui-ux-pro CSV knowledge base. Exit 1 on any error."""
import argparse
import csv
import re
import sys
from pathlib import Path

from core import DATA_DIR, load_rows, split_list
from schema import COLUMNS, ENUMS, FILES, INTENSITY_ORDER, STACKS

HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")


def _check_enum(errs, fname, rid, col, row, enum):
    if row.get(col) not in ENUMS[enum]:
        errs.append(f"{fname} [{rid}] {col}: {row.get(col)!r} not in {sorted(ENUMS[enum])}")


def validate(data_dir=DATA_DIR):
    data_dir = Path(data_dir)
    errs, ids, nrows, nfiles = [], {}, 0, 0
    tables = [(d, FILES[d], d, None) for d in FILES]
    tables += [("stack", f"stacks/{s}.csv", "stack", s) for s in STACKS
               if (data_dir / "stacks" / f"{s}.csv").exists()]
    rows_by = {}
    for domain, fname, kind, stack in tables:
        try:
            with open(data_dir / fname, encoding="utf-8-sig", newline="") as f:
                header = csv.DictReader(f).fieldnames or []
            # ragged rows give None cells (or a None key for extras); normalize
            rows = [{k: v or "" for k, v in r.items() if k is not None}
                    for r in load_rows(domain, data_dir, stack)]
        except FileNotFoundError:
            errs.append(f"{fname}: file missing")
            continue
        nfiles += 1
        nrows += len(rows)
        missing = [c for c in COLUMNS[kind] if c not in header]
        if missing:
            errs.append(f"{fname}: missing column(s) {', '.join(missing)}")
            if kind != "stack" and "id" in header:  # keep refs resolvable
                ids[kind] = {r["id"].strip() for r in rows}
            continue
        seen = set()
        for r in rows:
            rid = r["id"].strip()
            if not rid:
                errs.append(f"{fname} [?] id: empty")
                continue
            if rid in seen:
                errs.append(f"{fname} [{rid}] id: duplicate")
            seen.add(rid)
            if "severity" in COLUMNS[kind]:
                _check_enum(errs, fname, rid, "severity", r, "severity")
            if kind == "rule":
                _check_enum(errs, fname, rid, "category", r, "category")
            if "evidence" in COLUMNS[kind]:
                _check_enum(errs, fname, rid, "evidence", r, "evidence")
                if r["evidence"] == "sourced" and not r["source_url"].strip():
                    errs.append(f"{fname} [{rid}] source_url: required when evidence=sourced")
            if "intensity_default" in COLUMNS[kind]:
                _check_enum(errs, fname, rid, "intensity_default", r, "intensity")
            if kind == "direction":
                rng = split_list(r["intensity_range"])
                for x in rng:
                    if x not in ENUMS["intensity"]:
                        errs.append(f"{fname} [{rid}] intensity_range: {x!r} not in "
                                    f"{sorted(ENUMS['intensity'])}")
                pos = sorted(INTENSITY_ORDER.index(x) for x in rng if x in INTENSITY_ORDER)
                if pos and pos != list(range(pos[0], pos[-1] + 1)):
                    errs.append(f"{fname} [{rid}] intensity_range: {r['intensity_range']!r} "
                                f"has a gap in {INTENSITY_ORDER}")
                if r["intensity_default"] in ENUMS["intensity"] and r["intensity_default"] not in rng:
                    errs.append(f"{fname} [{rid}] intensity_range: must include "
                                f"intensity_default {r['intensity_default']!r}")
            if kind == "palette":
                _check_enum(errs, fname, rid, "type", r, "palette_type")
                for col in ("stops_hex", "dark_basemap_stops_hex"):
                    for h in split_list(r[col]):
                        if not HEX.match(h):
                            errs.append(f"{fname} [{rid}] {col}: bad hex {h!r}")
        if kind != "stack":
            ids[kind] = seen
            rows_by[kind] = rows

    def ref(kind, row, col, target):
        for x in split_list(row[col]):
            if x not in ids.get(target, ()):
                errs.append(f"{FILES[kind]} [{row['id']}] {col}: unknown {target} id {x!r}")

    for kind, col, target in [("problem", "rule_ids", "rule"), ("problem", "palette_ids", "palette"),
                              ("problem", "layout_id", "layout"), ("widget", "rule_ids", "rule"),
                              ("layout", "rule_ids", "rule"),
                              ("problem", "direction_ids", "direction"),
                              ("direction", "fits_problems", "problem")]:
        for r in rows_by.get(kind, []):
            ref(kind, r, col, target)
    dirs = {d["id"]: d for d in rows_by.get("direction", [])}
    linked = set()
    for pr in rows_by.get("problem", []):
        pid, dids = pr["id"], split_list(pr["direction_ids"])
        if not dids:
            errs.append(f"problems.csv [{pid}] direction_ids: empty")
            continue
        known = [d for d in dids if d in dirs]
        linked.update((pid, d) for d in known)
        want = pr["intensity_default"]
        supported = any(want in split_list(dirs[d]["intensity_range"]) for d in known)
        if known and want in ENUMS["intensity"] and not supported:
            errs.append(f"problems.csv [{pid}] intensity_default: {pr['intensity_default']!r} "
                        f"not in intensity_range of any linked direction")
    fits = {(p, d["id"]) for d in dirs.values() for p in split_list(d["fits_problems"])
            if p in ids.get("problem", ())}
    for pid, did in sorted(linked - fits):
        errs.append(f"directions.csv [{did}] fits_problems: missing {pid!r} (linked by problem direction_ids)")
    for pid, did in sorted(fits - linked):
        errs.append(f"directions.csv [{did}] fits_problems: {pid!r} does not link {did!r} in direction_ids")
    return errs


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data-dir", default=str(DATA_DIR))
    args = ap.parse_args(argv)
    errs = validate(Path(args.data_dir))
    if errs:
        print("\n".join(errs))
        return 1
    n = sum(len(load_rows(d, args.data_dir)) for d in FILES)
    m = len(FILES)
    for s in STACKS:
        if (Path(args.data_dir) / "stacks" / f"{s}.csv").exists():
            n += len(load_rows("stack", args.data_dir, s))
            m += 1
    print(f"OK: {n} rows in {m} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
