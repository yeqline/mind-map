# Excalidraw Mind-Map Generator — Plan

## Overview

Parse markdown files (per `manifest.md`) → generate `.excalidraw` JSON files viewable at excalidraw.com.

---

## 1. Config File (`config.yaml`)

Defines visual mappings for all manifest elements.

### 1.1 Node Type Styles (exhaustive list)

```yaml
node_types:
  concept:
    fill: "#e3f2fd"
    stroke: "#1976d2"
    stroke_width: 2
    font_family: 1 # 1=Virgil, 2=Helvetica, 3=Cascadia
    font_size: 20
    border_radius: 8
    padding: 16

  example:
    fill: "#f3e5f5"
    stroke: "#7b1fa2"
    font_size: 18

  code:
    fill: "#f5f5f5"
    stroke: "#424242"
    font_family: 3 # Cascadia (monospace)
    font_size: 14

  table:
    fill: "#e8f5e9"
    stroke: "#388e3c"
    font_size: 16
```

### 1.2 Edge Type Styles (exhaustive list)

```yaml
edge_types:
  # Inferred from heading hierarchy (H2 → H3 → H4)
  parent_child:
    stroke: "#666666"
    stroke_width: 2
    stroke_style: solid
    arrow_start: none
    arrow_end: arrow

  # From edges fence
  prereqs:
    stroke: "#d32f2f"
    stroke_width: 1 # narrow
    stroke_style: solid
    arrow_start: none
    arrow_end: arrow

  # From edges fence or inline [[...]] links
  related:
    stroke: "#9e9e9e"
    stroke_width: 1
    stroke_style: dotted
    arrow_start: none
    arrow_end: none # line, no arrow

  # From edges fence
  contrasts:
    stroke: "#ff5722"
    stroke_width: 1
    stroke_style: dashed
    arrow_start: none
    arrow_end: none # line, no arrow
```

### 1.3 Tags (project-specific, required)

Tags are defined per project. Parser rejects undefined tags.

```yaml
tags:
  sql:
    color: "#2196f3"
  databases:
    color: "#1565c0"
  math:
    color: "#4caf50"
  algorithms:
    color: "#7cb342"
  # add all valid tags for your project
```

**Rule:** Nodes inherit fill color from their first tag. If no tags, use type's default fill.

### 1.4 Layout Defaults

```yaml
layout:
  node_width: 200
  node_min_height: 60
  horizontal_gap: 100
  vertical_gap: 80
  auto_layout: tree # tree | force | none
```

---

## 2. Media Handling

**Folder structure:** For `notes.md` → media in `notes_media/`

```
notes.md
notes_media/
  diagram.png
  demo.mp4
```

**Excalidraw rendering:**

- **Images:** Embed as Excalidraw image elements inside the node.
- **Videos:** Embed as thumbnail image (if available) with play icon overlay, or as clickable link text.
- **URLs:** Render as clickable text element.

**Parser extracts:**

- `![alt](./notes_media/file.png)` → image path
- `![alt](./notes_media/file.mp4)` → video path
- `[text](https://...)` → external URL

---

## 3. Position Persistence

**Problem:** User repositions nodes in Excalidraw UI → next regeneration should preserve positions.

### Solution: Sidecar Position File

For each `notes.md` → store `notes.positions.json`:

```json
{
  "c-sql-joins": { "x": 150, "y": 300 },
  "c-sql-inner-join": { "x": 400, "y": 200 },
  "c-sql-outer-join": { "x": 400, "y": 400 }
}
```

**Workflow:**

1. Parse markdown → extract nodes/edges
2. Load `.positions.json` if exists
3. For nodes with saved positions → use them
4. For new nodes → auto-layout, then append to positions file
5. Generate `.excalidraw` file

**Position extraction from Excalidraw:**

- User edits in Excalidraw UI
- Export/save `.excalidraw` file
- Run `sync-positions` command → reads Excalidraw JSON, extracts node positions by matching element IDs, updates `.positions.json`

---

## 4. Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  notes.md   │────▶│    Parser    │────▶│  Graph Model    │
└─────────────┘     └──────────────┘     │  (nodes/edges)  │
                                         └────────┬────────┘
                                                  │
┌─────────────┐                                   ▼
│ config.yaml │──────────────────────▶   ┌───────────────────┐
└─────────────┘                          │  Excalidraw       │
                                         │  Generator        │
┌──────────────────┐                     └─────────┬─────────┘
│ notes.positions  │────────────────────▶          │
│ .json            │                               ▼
└──────────────────┘                     ┌───────────────────┐
                                         │ notes.excalidraw  │
                                         └───────────────────┘
```

### 3.1 Modules

| Module          | Responsibility                                                      |
| --------------- | ------------------------------------------------------------------- |
| `parser.py`     | Parse markdown → extract nodes (id, title, meta, content) and edges |
| `graph.py`      | Data structures for Node, Edge, Graph                               |
| `config.py`     | Load and validate `config.yaml`                                     |
| `layout.py`     | Auto-layout algorithms (tree, force-directed)                       |
| `positions.py`  | Read/write/sync `.positions.json` files                             |
| `excalidraw.py` | Generate Excalidraw JSON format                                     |
| `cli.py`        | Command-line interface                                              |

### 3.2 CLI Commands

```bash
# Generate excalidraw file from markdown
mindmap generate notes.md -o notes.excalidraw

# Sync positions back from edited excalidraw file
mindmap sync-positions notes.excalidraw

# Validate markdown against manifest rules
mindmap lint notes.md
```

---

## 5. Excalidraw JSON Structure

Based on official Excalidraw API documentation:
https://docs.excalidraw.com/docs/@excalidraw/excalidraw/api

Key elements we need to generate:

```json
{
  "type": "excalidraw",
  "version": 2,
  "elements": [
    {
      "id": "c-sql-joins",
      "type": "rectangle",
      "x": 100,
      "y": 200,
      "width": 200,
      "height": 80,
      "strokeColor": "#1976d2",
      "backgroundColor": "#e3f2fd",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "roundness": { "type": 3, "value": 8 }
    },
    {
      "id": "c-sql-joins-label",
      "type": "text",
      "x": 110,
      "y": 220,
      "text": "SQL Joins",
      "fontSize": 20,
      "fontFamily": 1,
      "containerId": "c-sql-joins"
    },
    {
      "id": "edge-c-sql-joins-c-sql-inner-join",
      "type": "arrow",
      "x": 300,
      "y": 240,
      "points": [
        [0, 0],
        [100, 50]
      ],
      "startBinding": { "elementId": "c-sql-joins" },
      "endBinding": { "elementId": "c-sql-inner-join" }
    }
  ]
}
```

---

## 6. Decisions (resolved)

| Decision            | Answer                                                         |
| ------------------- | -------------------------------------------------------------- |
| Multi-file support  | One `.excalidraw` per `.md` file                               |
| Content display     | Display all content in the canvas                              |
| Heading hierarchy   | Draw as edges (parent → child arrows)                          |
| Broken links        | Warn and skip edge                                             |
| Types               | `concept`, `example`, `code`, `table` (exhaustive)             |
| Tags                | Defined per project in `config.yaml`                           |
| Children edges      | Only inferred from heading hierarchy, never explicit           |
| Edge visuals        | Parent-child & prereqs = arrows; related & contrasts = lines   |
| Empty meta fields   | Omit entirely                                                  |
| Missing meta block  | Valid, defaults applied (`type: concept`)                      |
| Missing edges fence | Valid, only inline links + hierarchy create edges              |
| Media               | Standard markdown syntax, stored in `<filename>_media/` folder |

---

## 7. Implementation Order

1. **Phase 1:** Parser + Graph model + basic Excalidraw output (rectangles + lines/arrows)
2. **Phase 2:** Config file support (types, tags, edge styles)
3. **Phase 3:** Media handling (images, videos, URLs)
4. **Phase 4:** Position persistence (sidecar files + sync command)
5. **Phase 5:** Auto-layout algorithms
6. **Phase 6:** CLI polish + validation/linting

---

## Next Steps

- [x] Finalize decisions (Section 6)
- [x] Approve config schema (Section 1)
- [x] Confirm position persistence approach (Section 3)
- [x] Review and approve this plan
- [x] Phase 1: Parser + Graph model + basic Excalidraw output
- [x] Phase 2: Config file support (types, tags, edge styles)
- [ ] Phase 3: Media handling (images, videos, URLs)
- [x] Phase 4: Position persistence (sidecar files + sync command)
- [x] Phase 5: Auto-layout algorithms
- [x] Phase 6: CLI polish + validation/linting

**Implementation complete!** See `app/README.md` for usage and `app/ARCHITECTURE.md` for developer docs.
