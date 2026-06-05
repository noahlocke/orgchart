# Plan: Edit Mode (drag-to-reparent) + Tagging

Status: proposed. Target file for code: `src/template.html` (+ small `build.py` change).
Keep the hard constraint: **single self-contained HTML, no dependencies, no network.**

## 1. Goals

1. **Edit mode** toggle. When on, the user can **drag a node (and its whole
   subtree) onto another node to reparent it**. Releasing without a valid target
   reverts to the original position.
2. While dragging over a valid target, that target's **trunk lights up** to show
   it is safe to drop.
3. **Save** the edited structure as a **new CSV** (re-buildable via `build.py`),
   with a user-supplied file name.
4. **Tagging**: apply up to **2 tags per node** from an editable palette; tag
   names are editable and persisted to a new CSV column.

## 2. Decisions (confirmed)

- Save output: **new CSV** in the existing `Name,Class,Manager,Job Title` format
  plus a new `Tags` column. (No HTML snapshot.)
- Drag scope: **node + entire subtree** moves together.
- Tags: **max 2 per node**, chosen from a palette of tag *types*; type names are
  **editable** and saved to CSV.

## 3. Data model changes

### CSV (`build.py`)
- Add `tags` to `ALIASES` (`tags`, `labels`).
- Parse the `Tags` cell as a `|`-separated list (avoid clashing with the commas
  already used inside quoted Job Titles), e.g. `Review|Reassign`. Cap at 2 on read.
- Include `tags` in each RAW record only when the column exists:
  `{"name","cls","mgr","title","tags":[...]}`.
- On a normal build, this round-trips: a CSV saved from edit mode rebuilds 1:1.

### Template (`RAW` -> node objects)
- `byName.set(... {name, cls, mgr, title, tags: r.tags || [], children:[]})`.

### Tag palette (the two-or-more editable types)
- Keep a `TAGS` array in JS: `[{id, name, color}, ...]` (start with a few presets
  like Review / Reassign / Promote / Watch; colors from a fixed cycle).
- A node stores applied tag **ids** (max 2). On save, write the tag **names**
  (so the CSV is human-readable and rebuildable).
- Renaming a type updates its `name`; because nodes reference ids, renames are
  cheap and consistent. On load, map incoming names -> ids (create a type if a
  name is new). **Tradeoff:** palette colors are assigned deterministically by
  load order, not stored in the CSV (CSV has no global-config slot). Document this.

## 4. Edit mode toggle (UX)

- New **"Edit mode"** button in `#ui`. Toggling sets a global `EDIT=true/false`
  and an `body.editing` class for styling (e.g., accent border around the canvas,
  show the edit-only toolbar: tag palette + "Save as…").
- On entering edit mode: **clear re-root override and set filter to Both**
  (`applyRoot(''); FILTER='all'`) so drags operate on the true, full tree rather
  than a filtered/re-rooted view. Re-enable after exit if desired.
- Roots (blank-manager nodes / synthetic roots) are **not draggable**.

## 5. Drag-to-reparent

### Gesture
- Reuse the existing pointer threshold pattern (pan starts only after >3px move).
  In edit mode, a `pointerdown` on a *card* + move >4px **lifts** that node;
  a click without movement still toggles expand (navigation preserved).
- On lift: snapshot `{node, oldMgr, oldIndex}`; mark `g.dragging` (raise z-order,
  ~0.85 opacity, pointer-events:none so hit-testing sees what's underneath);
  the node follows the cursor. Its subtree can stay in place dimmed (cheaper) or
  travel with it (nicer). **Plan: keep subtree in place, dim it**; only the lifted
  card follows the cursor as a "handle".

### Hit-testing the drop target
- On `pointermove`, `document.elementFromPoint(x,y)` -> `closest('.card')` ->
  resolve to its node via a `card -> name` lookup (already have `elMap`).
- **Valid target** = a node that is not the dragged node and **not inside the
  dragged node's subtree** (cycle prevention; precompute the subtree name set on
  lift). Otherwise no highlight / not droppable.

### "Trunk lights up"
- Add `.drop-target` to the hovered target card (glow/brighter border) **and**
  draw a temporary highlighted **trunk**: the vertical connector segment from the
  target down to where the new child would attach. Implement by rendering an extra
  `<path class="trunk-hl">` for just that target's connector(s) during drag
  (separate from the single combined `#edges` path). Remove on dragleave.

### Drop / revert
- **Valid drop**: `reparent(node, target)` — remove from `oldMgr.children`, set
  `node.mgr = target.name`, push into `target.children`, re-run `sortKids` on the
  target (keeps ICs-above-managers ordering), `render()`, then `fitBox` the target
  subtree. Push an entry onto an **undo stack**.
- **Invalid / released on empty canvas**: revert using the snapshot, `render()`.
- Provide **Undo** (Cmd/Ctrl+Z) popping the stack — cheap insurance for fat-finger
  drops. (Nice-to-have but recommended.)

### Helper changes
- New `reparent()`, `subtreeNames(node)`, `cardToNode(el)`.
- `onNodeClick` stays for expand; drag logic lives in the svg pointer handlers,
  gated by `EDIT` and "started on a card".

## 6. Tagging

- **Apply**: in edit mode, each card shows a small **tag affordance** (e.g. a
  dot/▾ in the corner) that opens a **popover** listing the palette; clicking a
  type toggles it on the node, enforcing the **max-2** rule (third selection is
  blocked with a brief shake/tooltip).
- **Display**: render applied tags as small colored chips/ribbons on the card
  (top-right), visible in both view and edit modes so marks persist visually.
- **Edit palette**: a small panel (gear on the edit toolbar) lists the tag types
  with editable **name inputs** and color swatches; add/remove types.
- **Persistence**: applied tag names are written to the `Tags` CSV column on save.

## 7. Save flow

- **"Save as…"** button (edit toolbar) -> modal with a filename input
  (default `orgchart-edited`).
- Generate CSV from the current forest: walk **all** nodes (every root's subtree),
  emit `Name,Class,Manager,Job Title,Tags`, with `Manager` = current parent name
  (blank for roots), `Tags` = `name1|name2`. Quote fields containing commas/quotes.
- Trigger a client-side download via a `Blob` + temporary `<a download>`:
  `name.csv`. (Static page can't write disk directly; it downloads to the user's
  Downloads folder.)
- Tell the user: move the file to `data/` and run `./build.sh data/<file>.csv <name>`
  to regenerate — or just keep the CSV. (Round-trips through `build.py`.)

## 8. Files touched

- `src/template.html` — most work: edit toggle, drag/drop, trunk highlight,
  tag UI + chips, CSV export, undo. New CSS vars for tag colors + drop glow.
- `build.py` — `tags` alias + `|`-split parsing; include `tags` in RAW.
- `README.md` / `CLAUDE.md` — document edit mode, tags, the `Tags` column, and
  the save→rebuild loop. Add `reparent`/drag/export to the code map.
- `examples/sample-org.csv` — optionally add a couple of `Tags` values to demo.

## 9. Edge cases & risks

- **Cycles**: never allow dropping a node onto itself or a descendant. (Hard rule.)
- **Filter/re-root during edit**: avoided by forcing Both + no override in edit mode.
- **Click vs drag ambiguity**: solved by the move threshold; click = expand.
- **Hit-testing through the ghost**: set `pointer-events:none` on the lifted card.
- **Tag color/name persistence**: names persist via CSV; colors are
  deterministic, not stored (documented limitation).
- **Manager renames**: out of scope (names are the keys); reparenting only changes
  the `Manager` field, never `Name`.
- **Browser support**: Pointer Events + `elementFromPoint` are universal in modern
  browsers; no polyfills.

## 10. Build & verify

- After each change: `./build.sh --sample` then `node --check` the inlined script.
- **Round-trip test** (the key correctness check): in edit mode, reparent a node,
  Save CSV, run `build.py` on it, and diff the resulting forest structure against
  the in-browser state (same parent/child edges, same tags).
- Re-run the **no-overlap** layout check after reparenting (layout is unchanged,
  but the new tree shapes should still pass).
- Manual UX pass: lift, hover valid/invalid targets (trunk glow only on valid),
  drop, revert-on-miss, undo, max-2 tag enforcement.

## 11. Suggested sequencing

1. `build.py` + template: add `tags` plumbing (no UI yet); verify round-trip.
2. Edit-mode toggle + state, force Both/no-override, edit toolbar shell.
3. Drag lift + cursor-follow + revert-on-miss (no reparent yet).
4. Hit-testing + cycle guard + trunk highlight.
5. Commit reparent + re-sort + undo.
6. Tag palette + apply (max 2) + chips on cards.
7. Editable tag names + colors.
8. CSV export + filename modal + download.
9. Docs (README/CLAUDE.md) + sample tags + verification pass.

Steps 1–5 deliver the core drag feature; 6–9 complete tagging, saving, and docs.
