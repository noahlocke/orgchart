# Interactive Org Chart

A lightweight, dependency-free org chart you can generate from a simple CSV.
The output is a single self-contained HTML file — open it in any browser, no
server or internet required.

![demo](examples/sample-org.html)
> Open `examples/sample-org.html` in a browser to see a live demo built from fake data.

## Features

- **Collapse / expand** any manager by clicking it; the chart re-fits to view.
- **Vertical expansion** with individual contributors stacked *above* sub-managers,
  so expanding a team never buries the ICs.
- **Automatic width reflow** when sibling subtrees grow into each other.
- **Zoom-to-fit** on every interaction, free scroll-zoom / drag-pan, and a
  "Fit entire chart" button.
- **Per-class report counts** on collapsed managers (e.g. ● 11 FTE  ● 9 Contractor),
  which respect the active filter.
- **Class filter** — show FTE only, Contractors only, or both.
- **Manager nodes are visually brighter** than individual contributors.
- Each card shows **name, job title, and class**.

## Repository layout

```
.
├── build.py                 # generator (CSV -> HTML)
├── build.sh                 # convenience wrapper
├── src/
│   └── template.html        # the chart template + code  (edit the chart here)
├── examples/
│   ├── sample-org.csv       # fake sample data
│   └── sample-org.html      # prebuilt demo (committed)
├── data/                    # YOUR private data  (gitignored)
│   └── orgchart.csv         # <- put your real CSV here
└── dist/                    # generated output   (gitignored)
    └── orgchart.html        # <- your built chart
```

Source code and the sample live in `src/` and `examples/` and are safe to share.
**`data/` and `dist/` are gitignored**, so your real org data and the chart
generated from it never get committed.

## Quick start

```bash
# 1. See the demo
open examples/sample-org.html                 # macOS (or just double-click it)

# 2. Build from your own data
cp your-people.csv data/orgchart.csv
./build.sh data/orgchart.csv company          # -> dist/company.html
open dist/company.html
```

Requires Python 3 (standard library only — no packages to install).

## CSV format

A header row plus one row per person. Column names are matched
case-insensitively and accept common aliases.

| Column      | Required | Aliases accepted                  | Purpose                                   |
|-------------|----------|-----------------------------------|-------------------------------------------|
| `Name`      | yes      | Employee, Full Name               | Person's name (must be unique)            |
| `Class`     | yes      | Type, Worker Type                 | FTE / Contractor / Org — color + filter   |
| `Manager`   | yes      | Reports To, Supervisor            | The manager's `Name` (blank = root)       |
| `Job Title` | no       | Title, Role, Position             | Shown under the name on each card         |

Anyone whose `Manager` is not found among the `Name`s becomes a top-level root;
multiple roots render side by side.

## Build commands

The build script takes two arguments — a **source** CSV and an output **name** —
so you can keep many charts side by side in `dist/` without overwriting each other:

```bash
./build.sh SOURCE NAME                 # SOURCE csv -> dist/NAME.html

./build.sh data/orgchart.csv company   # -> dist/company.html
./build.sh data/sales.csv   sales-team # -> dist/sales-team.html
./build.sh --sample                    # rebuild examples/sample-org.html
```

`NAME` is just a label; the output always lands in `dist/<NAME>.html`
(a `.html` you include is ignored, so `company` and `company.html` are equivalent).

## Customizing the chart

All styling and behavior live in `src/template.html` (colors, card size, layout
constants, interactions). After editing it, rerun `./build.sh` to regenerate.

## License

MIT — see [LICENSE](LICENSE).
