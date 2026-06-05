#!/usr/bin/env python3
"""
Build the interactive org chart from a CSV.

Repository layout:
  src/template.html        chart template + code   (tracked)
  data/orgchart.csv        your private data        (gitignored)  -- default input
  dist/orgchart.html       generated chart          (gitignored)  -- default output
  examples/sample-org.csv  fake sample data         (tracked)
  examples/sample-org.html sample demo build        (tracked)

Usage:
  python3 build.py SOURCE NAME    # build SOURCE (csv) -> dist/NAME.html
  python3 build.py --sample       # build the bundled sample demo

Generate as many charts as you like by giving each a unique NAME, e.g.:
  python3 build.py data/orgchart.csv  company      ->  dist/company.html
  python3 build.py data/sales.csv     sales-team   ->  dist/sales-team.html

CSV columns (header row required; matched case-insensitively, common aliases ok):
  Name       (required)   employee name
  Class      (required)   FTE / Contractor / Org  (drives color + filter)
  Manager    (required)   this person's manager's Name  (blank = top-level root)
  Job Title  (optional)   shown under the name on each card
"""
import csv, json, os, sys

HERE       = os.path.dirname(os.path.abspath(__file__))
TEMPLATE   = os.path.join(HERE, "src", "template.html")
DEFAULT_IN = os.path.join(HERE, "data", "orgchart.csv")
DIST       = os.path.join(HERE, "dist")
SAMPLE_IN  = os.path.join(HERE, "examples", "sample-org.csv")
SAMPLE_OUT = os.path.join(HERE, "examples", "sample-org.html")

ALIASES = {
    "name":  ["name", "employee", "employee name", "full name"],
    "cls":   ["class", "type", "employee class", "worker type"],
    "mgr":   ["manager", "reports to", "manager name", "supervisor"],
    "title": ["job title", "title", "role", "position", "job"],
}

def norm(s):
    return " ".join((s or "").split()).lower()

def pick_columns(header):
    lookup = {norm(h): i for i, h in enumerate(header)}
    cols = {}
    for field, names in ALIASES.items():
        for nm in names:
            if nm in lookup:
                cols[field] = lookup[nm]
                break
    missing = [f for f in ("name", "cls", "mgr") if f not in cols]
    if missing:
        raise SystemExit("ERROR: CSV missing required column(s): "
                         + ", ".join(missing) + f"\nFound headers: {header}")
    return cols

def load_rows(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    if not rows:
        raise SystemExit("ERROR: CSV is empty.")
    cols = pick_columns(rows[0])
    out = []
    for r in rows[1:]:
        if not r:
            continue
        def get(field):
            i = cols.get(field)
            return r[i].strip() if (i is not None and i < len(r)) else ""
        name = get("name")
        if not name:
            continue
        rec = {"name": name, "cls": get("cls"), "mgr": get("mgr")}
        if "title" in cols:
            rec["title"] = get("title")
        out.append(rec)
    return out, ("title" in cols)

def build(src, out):
    if not os.path.exists(TEMPLATE):
        raise SystemExit(f"ERROR: template not found: {TEMPLATE}")
    if not os.path.exists(src):
        raise SystemExit(f"ERROR: input CSV not found: {src}")
    data, has_title = load_rows(src)
    template = open(TEMPLATE, encoding="utf-8").read()
    html = template.replace("__DATA__", json.dumps(data, ensure_ascii=False))
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    open(out, "w", encoding="utf-8").write(html)

    names   = {d["name"] for d in data}
    roots   = sorted({d["mgr"] for d in data if d["mgr"] and d["mgr"] not in names})
    classes = {}
    for d in data:
        classes[d["cls"]] = classes.get(d["cls"], 0) + 1
    titled = sum(1 for d in data if d.get("title"))

    rel = lambda p: os.path.relpath(p, HERE)
    print(f"Built {rel(out)} from {rel(src)}")
    print(f"  people:  {len(data)}")
    print(f"  classes: {classes}")
    print(f"  roots:   {roots or ['(blank manager -> single root)']}")
    print(f"  job titles: {titled}/{len(data)}" if has_title
          else "  job titles: no column found (cards show name + class only)")
    if len(roots) > 1:
        print("  NOTE: multiple roots detected -- each renders as its own top-level tree.")

USAGE = (
    "Usage:\n"
    "  python3 build.py SOURCE NAME    # SOURCE csv -> dist/NAME.html\n"
    "  python3 build.py --sample       # build the bundled sample demo\n"
)

def main():
    argv = sys.argv[1:]
    if "--sample" in argv:
        build(SAMPLE_IN, SAMPLE_OUT)
        return
    if len(argv) != 2:
        raise SystemExit(USAGE)
    src, name = argv
    # NAME is just a label; force the output into dist/ as <name>.html so
    # multiple charts never collide.
    stem = os.path.splitext(os.path.basename(name))[0]
    if not stem:
        raise SystemExit("ERROR: NAME must be a non-empty file name (e.g. 'company').")
    out = os.path.join(DIST, stem + ".html")
    build(src, out)

if __name__ == "__main__":
    main()
