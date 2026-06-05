# CLAUDE.md

Context for working on this repo with Claude Code.

## What this is

A generator for a **single-file, dependency-free interactive org chart**.
`build.py` reads a CSV and injects it into an HTML template, producing a
self-contained `.html` (inline CSS + SVG + vanilla JS, no external libraries,
no network). Open the output directly in a browser.

## Architecture

There are only two pieces of real code:

1. **`build.py`** — a tiny, stdlib-only generator.
   - Reads the CSV, normalizes headers (case-insensitive + aliases, see `ALIASES`).
   - Emits a JSON array of `{name, cls, mgr, title}` and substitutes it for the
     literal token `__DATA__` in `src/template.html`.
   - CLI: `build.py SOURCE NAME` -> `dist/NAME.html`; `build.py --sample` ->
     `examples/sample-org.html`. Output dir is created if missing.

2. **`src/template.html`** — the entire chart (CSS + markup + JS in one file).
   The data line is `const RAW = __DATA__;` — build.py replaces `__DATA__`.
   **Edit the chart here, never edit generated files in `dist/`.**

### Data flow
`CSV -> build.py (JSON) -> __DATA__ in template -> RAW -> byName/forest -> layout -> render (SVG) -> camera`

### Code map for `src/template.html`
(approximate line numbers; the JS is in one `<script>` near the bottom)

- **Forest build** (`byName`, `realRoots`, `ensureSynthRoot`): turns the flat
  rows into a tree. A row whose `mgr` exists becomes a child; a named-but-absent
  manager becomes a *synthetic* root; a blank `mgr` makes that row a real root.
  `PRIMARY` = largest tree, sorted first (data-driven, nothing hardcoded).
- **Re-root** (`rootOverride`, `nodeByName`, `activeRoots`, `allManagers`):
  the Root dropdown sets `rootOverride`; `activeRoots()` returns `[thatNode]` or
  all `realRoots`. Everything downstream iterates `activeRoots()`, not `realRoots`.
- **Filter** (`FILTER`, `KEEP`, `passes`, `computeKeep`, `kids`, `hasKids`):
  the FTE/Contractor/Both toggle. `computeKeep()` marks which nodes survive the
  filter; `kids(n)` returns filter-surviving children; `hasKids` = "expandable
  under current filter". Run `computeKeep()` before layout each render.
- **Layout** (constants `CW,CH,VGAP,HGAP,DROP,ROOTGAP`; `layout`, `shift`,
  `runLayout`): pure, deterministic, fixed card size. Per manager, **IC children
  stack vertically above manager children**; manager children lay out as
  horizontal tidy subtrees. Each node gets card pos `x,y` and subtree box
  `bx,by,bw,bh`. `runLayout()` lays out the active roots and sets `WORLD`.
- **Visible set** (`visible`): walks `activeRoots()` + `kids()` honoring
  `isOpen`. Returns nodes to draw.
- **Render** (`metaHTML`, `classCounts`, `render`): keyed by name into `elMap`
  so cards persist across renders and CSS-transition between positions
  (smooth expand/collapse). `metaHTML` builds per-class count chips (respecting
  `FILTER`) + caret. `render` toggles `.has-kids`, `.is-mgr` (brighter manager
  cards), `.open`.
- **Camera** (`cam`, `apply`, `fitBox`, `animateTo`, wheel/drag handlers):
  single SVG `transform` (`translate scale`). `fitBox(box)` computes zoom-to-fit
  and tweens via `animateTo`. Wheel = zoom at pointer; drag (>3px) = pan.
- **Interactions**: `onNodeClick` toggles expand then fits the clicked subtree;
  `fitAll`/`expandAll`/`collapseAll` buttons; `applyRoot` (dropdown + `×`).

## Build & verify

```bash
./build.sh --sample                    # rebuild the committed demo
./build.sh data/orgchart.csv company   # build private data -> dist/company.html
```

Quick sanity check of the generated JS (the inlined `<script>` must parse):

```bash
python3 - <<'PY'
import re; s=open('examples/sample-org.html').read()
open('/tmp/v.js','w').write(re.search(r'<script>(.*)</script>', s, re.S).group(1))
PY
node --check /tmp/v.js && echo OK
```

The layout is pure and fixed-size, so it can be re-implemented standalone in
Node to assert "no two visible cards overlap" across expand states — that is the
main correctness check when touching the layout engine.

## Conventions / gotchas

- **Single self-contained file** is a hard requirement: no CDN, no external CSS/JS,
  inline everything. Keep it that way.
- After editing `src/template.html`, always rebuild before viewing; browsers cache
  aggressively, so hard-refresh (Cmd/Ctrl+Shift+R).
- `data/` and `dist/` are **gitignored** (private data + artifacts). The only
  tracked generated file is `examples/sample-org.html`. Don't commit real data.
- Names are assumed unique (used as map keys and DOM keys).
- Use `activeRoots()` (not `realRoots`) anywhere that walks the tree, or re-root
  will break.
- Run `computeKeep()` before `runLayout()`/`visible()` in any new render path.

## Repo layout
```
build.py  build.sh  README.md  CLAUDE.md  LICENSE  .gitignore
src/template.html           # the chart (edit here)
examples/sample-org.csv     # fake data (tracked)
examples/sample-org.html    # prebuilt demo (tracked)
data/   (gitignored)        # real CSV in data/orgchart.csv
dist/   (gitignored)        # generated charts
```
