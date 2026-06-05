#!/usr/bin/env python3
"""
Rebuild the interactive org chart from a CSV.

Usage:
    python3 build.py                      # reads ./orgchart.csv  -> writes ./orgchart.html
    python3 build.py path/to/data.csv     # custom input
    python3 build.py data.csv out.html    # custom input + output

The CSV must have a header row. Columns are matched case-insensitively and
flexibly, so any of these headers work:
    Name        (required)            -> employee name
    Class       (required)            -> FTE / Contractor / Org (drives color + filter)
    Manager     (required)            -> the name of this person's manager
    Job Title   (optional)            -> shown under the name on each card
                also accepts: Title, Role, Position

Anyone whose Manager is not found in the Name column becomes a top-level root.
"""

import csv, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "orgchart.template.html")

# header aliases -> canonical field
ALIASES = {
    "name":    ["name", "employee", "employee name", "full name"],
    "cls":     ["class", "type", "employee class", "worker type"],
    "mgr":     ["manager", "reports to", "manager name", "supervisor"],
    "title":   ["job title", "title", "role", "position", "job"],
}

def norm(s):
    return re.sub(r"\s+", " ", (s or "").strip()).lower()

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
        raise SystemExit(
            "ERROR: CSV is missing required column(s): "
            + ", ".join(missing)
            + f"\nFound headers: {header}"
        )
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

def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "orgchart.csv")
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "orgchart.html")

    if not os.path.exists(src):
        raise SystemExit(f"ERROR: input CSV not found: {src}")
    if not os.path.exists(TEMPLATE):
        raise SystemExit(f"ERROR: template not found: {TEMPLATE}")

    data, has_title = load_rows(src)
    template = open(TEMPLATE, encoding="utf-8").read()
    html = template.replace("__DATA__", json.dumps(data, ensure_ascii=False))
    open(out, "w", encoding="utf-8").write(html)

    names = {d["name"] for d in data}
    roots = sorted({d["mgr"] for d in data if d["mgr"] and d["mgr"] not in names})
    classes = {}
    for d in data:
        classes[d["cls"]] = classes.get(d["cls"], 0) + 1
    titled = sum(1 for d in data if d.get("title"))

    print(f"Built {os.path.basename(out)} from {os.path.basename(src)}")
    print(f"  people:  {len(data)}")
    print(f"  classes: {classes}")
    print(f"  roots:   {roots or ['(none)']}")
    if has_title:
        print(f"  job titles present: {titled}/{len(data)}")
    else:
        print("  job titles: no 'Job Title' column found (cards show name + class only)")
    if len(roots) > 1:
        print("  NOTE: multiple roots detected — each renders as its own top-level tree.")

if __name__ == "__main__":
    main()
