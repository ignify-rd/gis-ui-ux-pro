"""Validate the gis-ui-ux-pro CSV knowledge base. Exit 1 on any error."""
import argparse
import csv
import re
import sys
from pathlib import Path

from core import DATA_DIR, load_rows, split_list
from schema import COLUMNS, ENUMS, FILES, STACKS

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
                              ("layout", "rule_ids", "rule")]:
        for r in rows_by.get(kind, []):
            ref(kind, r, col, target)
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
