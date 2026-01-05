# Architecture Documentation

This document explains the internal architecture of the mind-map generator for developers who want to understand, maintain, or extend the codebase.

## Overview

The mind-map generator converts markdown files (following the `manifest.md` convention) into Excalidraw JSON files. The system is designed with clear separation of concerns across multiple modules.

```
                           ┌─────────────────────────────────────┐
                           │              CLI Layer              │
                           │            (cli.py)                 │
                           └─────────────────┬───────────────────┘
                                             │
         ┌───────────────────────────────────┼───────────────────────────────────┐
         │                                   │                                   │
         ▼                                   ▼                                   ▼
┌─────────────────┐                 ┌─────────────────┐                 ┌─────────────────┐
│     Parser      │                 │     Layout      │                 │   Excalidraw    │
│   (parser.py)   │                 │   (layout.py)   │                 │ (excalidraw.py) │
└────────┬────────┘                 └────────┬────────┘                 └────────┬────────┘
         │                                   │                                   │
         │                                   │                                   │
         ▼                                   ▼                                   ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    Graph Model                                          │
│                                    (graph.py)                                           │
│                                                                                         │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐                                            │
│   │  Node   │    │  Edge   │    │  Graph  │                                            │
│   └─────────┘    └─────────┘    └─────────┘                                            │
└─────────────────────────────────────────────────────────────────────────────────────────┘
         ▲                                   ▲
         │                                   │
┌─────────────────┐                 ┌─────────────────┐
│     Config      │                 │    Positions    │
│   (config.py)   │                 │ (positions.py)  │
└─────────────────┘                 └─────────────────┘
```

## Module Descriptions

### 1. `graph.py` — Core Data Structures

The foundation of the system. Defines three main classes:

#### `Node`

Represents a concept/heading in the markdown:

```python
@dataclass
class Node:
    id: str           # Globally unique, e.g., "c-sql-joins"
    title: str        # Display title from heading
    level: int        # Heading level (2 for ##, 3 for ###)
    node_type: NodeType  # concept | example | code | table
    tags: list[str]   # From config.yaml
    content: str      # Markdown content below heading
    parent_id: Optional[str]  # Inferred from heading hierarchy
    x, y: float       # Position on canvas
    width, height: float  # Dimensions
```

#### `Edge`

Represents a relationship between nodes:

```python
@dataclass
class Edge:
    source_id: str    # Source node ID
    target_id: str    # Target node ID
    edge_type: EdgeType  # parent_child | prereqs | related | contrasts
```

#### `Graph`

Container for all nodes and edges:

- `add_node()` — Adds node, raises on duplicate ID
- `add_edge()` — Adds edge, deduplicates
- `get_children()` — Get child nodes
- `validate()` — Check for broken references

#### Enums

- `NodeType`: CONCEPT, EXAMPLE, CODE, TABLE
- `EdgeType`: PARENT_CHILD, PREREQS, RELATED, CONTRASTS

---

### 2. `config.py` — Configuration Management

Loads and validates `config.yaml` files with a **merge-based override system**.

#### Config Hierarchy

1. **Default Config**: `app/default_config.yaml` is loaded first
2. **Project Config**: If provided (or auto-detected), it merges at property level
3. **Result**: Merged configuration with project values overriding only specific properties

**Granular Merging Example:**

```python
# Default config defines: concept.fill="#e3f2fd", concept.stroke="#1976d2"
# Project config defines: concept.fill="yellow"
# Result: concept.fill="yellow", concept.stroke="#1976d2" (from default)
```

This allows project configs to be minimal, overriding only what's needed.

#### Key Classes

- `NodeStyle` — Visual properties for node types (fill, stroke, font, etc.)
- `EdgeStyle` — Visual properties for edge types (stroke, arrows, etc.)
- `TagStyle` — Color for tags
- `LayoutConfig` — Layout algorithm settings
- `Config` — Complete configuration container

#### Key Functions

- `load_config(path)` — Load config with merge from defaults
  - Always loads `default_config.yaml` first
  - If `path` provided, loads and merges it over defaults
  - Project-specific values override defaults
- `_apply_config_data(config, data)` — Merges YAML data into Config object
- Config validation happens automatically during parsing

#### Auto-Detection

The CLI automatically detects project-specific configs:

- Looks for `config.yaml` in the same directory as the markdown file
- If found, uses it to override defaults
- If not found, uses only `default_config.yaml`
- Can be overridden with `-c` flag

---

### 3. `parser.py` — Markdown Parsing

Parses markdown files into Graph structures.

#### Parsing Rules (from manifest.md)

1. **Nodes**: Headings with `{#c-...}` anchors

   ```markdown
   ## SQL Joins {#c-sql-joins}
   ```

2. **Meta blocks**: `[!meta]` blockquotes

   ```markdown
   > [!meta]
   > tags: sql, databases
   > type: concept
   ```

3. **Edges fence**: Triple-backtick edges blocks

   ````markdown
   ```edges
   prereqs: c-sql-basics
   related: c-query-optimization
   ```
   ````

   ```

   ```

4. **Inline links**: `[[c-...]]` become related edges

5. **Parent-child**: Inferred from heading hierarchy (## → ### → ####)

#### Key Classes

- `Parser` — Main parsing class
- `ParseError` — Fatal parsing error
- `ParseWarning` — Non-fatal issue

#### Parsing Flow

1. Read file line by line
2. Detect headings with IDs → create nodes
3. Parse meta blocks → apply to current node
4. Parse edges blocks → create edges
5. Extract inline links → create related edges
6. Track heading hierarchy → create parent-child edges
7. Validate graph → return with warnings

---

### 4. `layout.py` — Auto-Layout Algorithms

Positions nodes automatically when no saved positions exist.

#### Algorithms

**Tree Layout** (default)

- Arranges nodes hierarchically based on parent-child relationships
- Calculates subtree widths for proper spacing
- Parents are centered above their children

**Force-Directed Layout**

- Simulates physical forces:
  - Repulsion between all nodes
  - Attraction along edges
- Iteratively converges to stable positions

#### Key Function

```python
apply_layout(graph: Graph, config: Config) -> None
```

---

### 5. `positions.py` — Position Persistence

Saves and loads node positions to preserve manual adjustments.

#### File Format

For `notes.md`, creates `notes.positions.json`:

```json
{
  "c-sql-joins": { "x": 150, "y": 300, "width": 250, "height": 80 }
}
```

#### Key Functions

- `load_positions(md_path)` — Load saved positions
- `save_positions(md_path, graph)` — Save current positions
- `apply_saved_positions(graph, positions)` — Apply to graph
- `sync_positions_from_excalidraw(exc_path, md_path)` — Extract from edited file

#### Workflow

1. User generates Excalidraw file
2. User edits positions in Excalidraw
3. User runs `sync-positions` command
4. Positions extracted and saved to `.positions.json`
5. Next generation preserves those positions

---

### 6. `excalidraw.py` — Excalidraw JSON Generation

Generates Excalidraw-compatible JSON files.

#### Excalidraw Element Types Generated

**Rectangle** (for nodes)

```json
{
  "id": "c-sql-joins",
  "type": "rectangle",
  "x": 100,
  "y": 200,
  "width": 250,
  "height": 80,
  "strokeColor": "#1976d2",
  "backgroundColor": "#e3f2fd",
  "roundness": { "type": 3, "value": 8 }
}
```

**Text** (for node content)

```json
{
  "id": "c-sql-joins-text",
  "type": "text",
  "containerId": "c-sql-joins",
  "text": "**SQL Joins**\n\nContent here..."
}
```

**Arrow** (for directed edges: parent_child, prereqs)

```json
{
  "id": "edge-...",
  "type": "arrow",
  "startBinding": { "elementId": "c-source" },
  "endBinding": { "elementId": "c-target" },
  "endArrowhead": "arrow"
}
```

**Line** (for undirected edges: related, contrasts)

- Same as arrow but with `endArrowhead: null`

#### Key Functions

- `generate_excalidraw(graph, config)` — Returns dict
- `save_excalidraw(graph, config, path)` — Saves to file

---

### 7. `cli.py` — Command-Line Interface

Uses Click library for CLI commands. **Convention-based with minimal options.**

#### Commands

**generate** (main command)

```bash
python -m app generate atlas/sql/sql.md
```

Convention-based flow:
1. Auto-detect config (`config.yaml` in same folder)
2. Auto-sync positions (if excalidraw file is newer)
3. Lint markdown (fails on errors)
4. Parse markdown into graph
5. Load saved positions
6. Apply layout (only to new nodes)
7. Save positions
8. Generate excalidraw file (same folder, same name)

**Zero options needed:**
- Output: Always `<markdown>.excalidraw`
- Config: Always `config.yaml` in same folder (or defaults)
- Positions: Always synced automatically
- Linting: Always runs
- Layout: Always applied to new nodes

**lint** (optional standalone validation)

```bash
python -m app lint atlas/sql/sql.md
```

1. Auto-detect config
2. Parse markdown
3. Validate IDs, types, tags, edges
4. Report errors/warnings

Note: Linting happens automatically during `generate`.

---

## Data Flow

### Generation Flow (Automatic Position Sync)

```
                    ┌──────────────────────────────────────────┐
                    │ Check if excalidraw is newer than        │
                    │ positions file → auto-sync if needed     │
                    └──────────────┬───────────────────────────┘
                                   ▼
notes.md ──► Lint ──► Parser ──► Graph ──► Layout ──► Excalidraw Generator
               │         │          │          │              │
               │         ▼          ▼          │              │
               │     Config    Positions ◄─────┘              │
               │                   ▲                          │
               │                   └──────────────────────────┘
               ▼
          Fail if errors
```

**Key Points:**
- Position sync happens automatically at the start of generation
- Linting is integrated into the generation flow
- Config is auto-detected from the project folder
- Output is always same name/folder as input

---

## Extending the System

### Adding a New Node Type

1. Add to `NodeType` enum in `graph.py`
2. Add style in `default_config.yaml`
3. Update validation in `config.py`

### Adding a New Edge Type

1. Add to `EdgeType` enum in `graph.py`
2. Add style in `default_config.yaml`
3. Update parsing in `parser.py`
4. Update validation in `config.py`

### Adding a New Layout Algorithm

1. Create function `_apply_XXX_layout(graph, config)` in `layout.py`
2. Add case to `apply_layout()` function
3. Document in config options

### Adding Media Support

1. Extend `parser.py` to extract image/video/URL patterns
2. Store media references in `Node.content` or new field
3. Create Excalidraw image elements in `excalidraw.py`
4. Handle media file paths relative to markdown file

---

## File Structure

```
mind-map/
├── app/
│   ├── __init__.py         # Package metadata
│   ├── __main__.py         # Entry point for python -m app
│   ├── cli.py              # CLI commands (with config auto-detection)
│   ├── config.py           # Configuration loading (merge-based)
│   ├── default_config.yaml # Default styles (base layer)
│   ├── excalidraw.py       # Excalidraw JSON generation
│   ├── graph.py            # Core data structures
│   ├── layout.py           # Auto-layout algorithms
│   ├── parser.py           # Markdown parsing
│   ├── positions.py        # Position persistence
│   ├── pyproject.toml      # Project config (uv)
│   ├── ARCHITECTURE.md     # This file
│   └── README.md           # User guide
├── atlas/
│   ├── sql/                # Project folder
│   │   ├── sql.md
│   │   ├── sql_media/
│   │   ├── config.yaml     # Project-specific config (overrides defaults)
│   │   ├── sql.excalidraw
│   │   └── sql.positions.json
│   ├── python/
│   │   ├── python.md
│   │   ├── config.yaml
│   │   └── ...
│   └── ...
└── manifest.md
```

### Config File Locations

- **`app/default_config.yaml`**: Base configuration for all projects
- **`atlas/<project>/config.yaml`**: Optional project-specific overrides
- The app automatically detects and merges project configs

---

## Testing Strategy

### Setup with uv

```bash
cd app
uv sync  # Installs dev dependencies including pytest
```

### Running Tests

```bash
uv run pytest
```

### Unit Tests

- `test_graph.py` — Node/Edge/Graph creation and validation
- `test_parser.py` — Markdown parsing with various inputs
- `test_config.py` — Config loading and validation
- `test_layout.py` — Layout algorithm correctness
- `test_excalidraw.py` — JSON structure validation

### Integration Tests

- End-to-end: markdown → excalidraw file
- Position persistence round-trip
- Config customization

### Test Files

Create sample markdown files in `tests/fixtures/`:

- `simple.md` — Single node
- `hierarchy.md` — Parent-child relationships
- `edges.md` — All edge types
- `complex.md` — Real-world example
