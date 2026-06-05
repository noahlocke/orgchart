# Org Chart

An interactive, self-contained HTML org chart. No internet or dependencies needed to view — just open `orgchart.html` in any browser.

## Rebuilding after you edit the data

Keep these four files in the same folder:

- `orgchart.csv` — your data (edit this)
- `build.py` — the generator
- `build.sh` — convenience wrapper
- `orgchart.template.html` — the chart template (don't edit)

Then rebuild with either:

```bash
./build.sh
```

or

```bash
python3 build.py
```

This regenerates `orgchart.html`. Refresh your browser to see changes.

## CSV format

A header row plus one row per person. Required columns: **Name**, **Class**, **Manager**.
Optional column: **Job Title** (shown under each name). Header matching is
case-insensitive and accepts common variants (e.g. "Title"/"Role" for Job Title,
"Reports To" for Manager).

| Name        | Class      | Manager     | Job Title              |
|-------------|------------|-------------|------------------------|
| Noah Locke  | FTE        |             | Senior Director, PM    |
| Jane Doe    | FTE        | Noah Locke  | Product Manager        |
| Acme Corp   | Contractor | Jane Doe    | Contract Engineer      |

- **Class** drives card color and the FTE/Contractor filter (FTE, Contractor, Org).
- Anyone whose **Manager** isn't listed as a Name becomes a top-level root.

## Using a different file name

```bash
python3 build.py path/to/yourdata.csv            # custom input
python3 build.py path/to/yourdata.csv out.html   # custom input and output
```

## Tip: export from Excel

In Excel, File → Save As → CSV UTF-8, save it as `orgchart.csv` in this folder, then run the build.
