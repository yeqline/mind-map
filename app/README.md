# Mind-Map Generator — User Guide

Convert markdown files into visual mind maps using Excalidraw.

## Quick Start

### 1. Install Dependencies

```bash
cd app
uv sync
```

### 2. Create Your Project

```bash
mkdir -p atlas/sql
cd atlas/sql
```

### 3. Write Your Markdown

Create `sql.md` following the [manifest.md](../../manifest.md) convention:

````markdown
## SQL Basics {#c-sql-basics}

> [!meta]
> tags: sql, databases
> type: concept

Introduction to SQL...

### SELECT Queries {#c-sql-select}

> [!meta]
> type: code

```edges
prereqs: c-sql-basics
```
````

The SELECT statement retrieves data from tables.

````

### 4. Create Config (Optional)

Create `config.yaml` in the same folder to define project-specific tags:

```yaml
tags:
  sql:
    color: "#2196f3"
  databases:
    color: "#1565c0"
````

**Note:** Config is optional! If not provided, the app uses defaults.

### 5. Generate the Mind Map

```bash
cd ../../app
python run.py generate ../atlas/sql/sql.md
```

**What happens automatically:**

- ✓ Creates `atlas/sql/sql.excalidraw` (same folder)
- ✓ Uses `atlas/sql/config.yaml` if it exists
- ✓ Validates the markdown (fails on errors)
- ✓ Applies layout to all nodes
- ✓ Saves positions for future edits

### 6. Edit in Excalidraw

1. Open `atlas/sql/sql.excalidraw` at [excalidraw.com](https://excalidraw.com)
2. Rearrange nodes as you like
3. Save the file (Ctrl+S)
4. Run `generate` again → positions are preserved!

```bash
python run.py generate ../atlas/sql/sql.md
# Automatically syncs your layout changes
```

---

## Commands

### `generate` — Create Excalidraw File

```bash
python run.py generate <markdown_file>
```

**Convention-based with zero configuration:**

- Output file: `<markdown_file>.excalidraw` (same folder)
- Config: `config.yaml` in same folder (or uses app defaults)
- Positions: Automatically synced from excalidraw if you've edited it
- Layout: Applied only to new nodes (existing positions preserved)
- Linting: Runs automatically, fails if validation errors

**Example:**

```bash
cd app
python run.py generate ../atlas/sql/sql.md

# Creates: ../atlas/sql/sql.excalidraw
# Uses: ../atlas/sql/config.yaml (if exists)
# Preserves: Any positions you've manually set in Excalidraw
```

### `lint` — Validate Markdown (Optional)

Linting happens automatically during `generate`. Use this for standalone validation:

```bash
python run.py lint <markdown_file>
```

**Example:**

```bash
python run.py lint ../atlas/sql/sql.md
```

Checks for:

- Valid node IDs (globally unique, `c-kebab-case`)
- Valid types (`concept`, `example`, `code`, `table`)
- Defined tags (from `config.yaml`)
- Valid edge references

---

## Markdown Syntax

### Nodes

Create nodes with headings and IDs:

```markdown
## My Concept {#c-my-concept}
```

- Use `##` (H2) for top-level nodes
- Use `###` (H3) for child nodes
- IDs must be globally unique across all files
- IDs must start with `c-` and use kebab-case

### Meta Block

Add metadata right after the heading:

```markdown
> [!meta]
> tags: tag1, tag2
> type: concept
```

**Fields:**

- `tags` — Comma-separated list (must be defined in config.yaml)
- `type` — One of: `concept`, `example`, `code`, `table`

If omitted, defaults to `type: concept` with no tags.

### Edges

Define relationships in an edges block:

````markdown
```edges
prereqs: c-other-concept
related: c-related-one, c-related-two
contrasts: c-alternative
```
````

````

**Edge Types:**
| Type | Visual | Description |
|------|--------|-------------|
| `prereqs` | Arrow | Learning dependencies |
| `related` | Line | Related concepts |
| `contrasts` | Dashed line | Opposing ideas |

**Parent-child edges** are created automatically from heading hierarchy.

### Inline Links

Reference other concepts in your content:

```markdown
See also [[c-other-concept]] for more details.
````

Inline links create `related` edges automatically.

### Content

Everything below the meta/edges blocks is node content:

````markdown
## My Concept {#c-my-concept}

> [!meta]
> type: concept

**What it is:** A brief explanation.

**Why it matters:** The importance of this concept.

- Bullet point 1
- Bullet point 2

```python
# Code example
print("Hello")
```
````

```

---

## Project Structure

### Atlas Folder

Organize your knowledge base in the `atlas/` folder with each project in its own subfolder:

```

mind-map/
├── app/ # Application code
│ └── default_config.yaml # Base config for all projects
├── atlas/ # Your knowledge base
│ ├── sql/
│ │ ├── sql.md
│ │ ├── sql_media/ # Media for sql.md
│ │ ├── config.yaml # Project-specific config (optional)
│ │ ├── sql.excalidraw
│ │ └── sql.positions.json
│ ├── python/
│ │ ├── python.md
│ │ ├── config.yaml
│ │ └── ...
│ └── algorithms/
│ └── ...
└── manifest.md

````

### Config Hierarchy

The app uses a **merge-based configuration system**:

1. **Default Config** (`app/default_config.yaml`): Base styles for all projects
2. **Project Config** (`atlas/<project>/config.yaml`): Optional, overrides defaults
3. **Explicit Config** (`-c` flag): Manually specify any config file

**How it works:**

```bash
# Uses default_config.yaml only
python -m app generate atlas/project/notes.md

# Auto-detects atlas/project/config.yaml if it exists
python -m app generate atlas/project/notes.md

# Explicitly use a specific config
python -m app generate notes.md -c path/to/custom.yaml
````

**What you can override:**

- **Tags**: Define project-specific tags
- **Node styles**: Customize colors, fonts, borders
- **Edge styles**: Adjust colors, line styles, arrows
- **Layout settings**: Change spacing, algorithm

**Granular property-level merging:**

The config system merges at the **property level**, not object level. This means:

```yaml
# app/default_config.yaml (loaded first)
node_types:
  concept:
    fill: "#e3f2fd"
    stroke: "#1976d2"
    stroke_width: 2
    font_family: 1
    font_size: 20
    border_radius: 8
    padding: 16

# atlas/sql/config.yaml (overrides only fill)
node_types:
  concept:
    fill: "yellow"

# Result: concept nodes have:
# - fill: "yellow" (from project config)
# - stroke: "#1976d2" (from default config)
# - stroke_width: 2 (from default config)
# - font_family: 1 (from default config)
# ... all other properties from default
```

**Example project config:**

```yaml
# atlas/sql/config.yaml
# Only override what's needed - rest comes from defaults

tags:
  sql:
    color: "#2196f3"
  databases:
    color: "#1565c0"

node_types:
  code:
    fill: "#263238" # Dark background for SQL code
    stroke: "#00bcd4"
    # stroke_width, font_size, etc. come from default_config.yaml
```

---

## Configuration

### Node Types

Define visual styles for each node type:

```yaml
node_types:
  concept:
    fill: "#e3f2fd" # Background color
    stroke: "#1976d2" # Border color
    stroke_width: 2
    font_family: 1 # 1=Virgil, 2=Helvetica, 3=Cascadia
    font_size: 20
    border_radius: 8
    padding: 16
```

### Edge Types

Define styles for each edge type:

```yaml
edge_types:
  parent_child:
    stroke: "#666666"
    stroke_width: 2
    stroke_style: solid # solid | dashed | dotted
    start_arrowhead: null
    end_arrowhead: arrow

  prereqs:
    stroke: "#d32f2f"
    stroke_width: 1
    stroke_style: solid
    end_arrowhead: arrow

  related:
    stroke: "#9e9e9e"
    stroke_style: dotted
    end_arrowhead: null # No arrow (line)

  contrasts:
    stroke: "#ff5722"
    stroke_style: dashed
    end_arrowhead: null
```

### Tags

Define your project's tags:

```yaml
tags:
  sql:
    color: "#2196f3"
  python:
    color: "#4caf50"
  math:
    color: "#ff9800"
```

Nodes with tags inherit the color of their first tag.

### Layout

Configure auto-layout behavior:

```yaml
layout:
  node_width: 250
  node_min_height: 80
  horizontal_gap: 120
  vertical_gap: 100
  auto_layout: tree # tree | force | none
```

---

## Workflow

### Initial Creation

1. Write your markdown file in `atlas/<project>/` following the manifest
2. Optionally create `config.yaml` in the same folder with project-specific tags
3. Run `generate` to create the Excalidraw file
4. Open in Excalidraw to view

### Editing Layout in Excalidraw

1. Open the `.excalidraw` file at excalidraw.com or in the Excalidraw app
2. Rearrange nodes as desired
3. Save the file (Ctrl+S or File → Save)
4. Run `generate` again — **positions are automatically synced!**
5. The generator detects the modified excalidraw file and updates positions

**No manual sync needed!** The app automatically detects when your excalidraw file is newer than the positions file and syncs them.

### Updating Content

1. Edit your markdown file (add nodes, change relationships, etc.)
2. Run `python run.py generate <file.md>` again
3. New nodes get auto-positioned
4. Existing nodes keep their saved positions (from your last Excalidraw edit)
5. The layout algorithm only affects new nodes

---

## Generated Files

For a file `atlas/sql/sql.md`, the generator creates:

```
atlas/sql/
├── sql.md              # Your source markdown
├── config.yaml         # Project config (optional)
├── sql.excalidraw      # Generated Excalidraw file
├── sql.positions.json  # Saved node positions
└── sql_media/          # Media folder (images, videos, etc.)
```

All generated files are co-located with your markdown file for easy project management.

---

## Troubleshooting

### "Unknown type 'xxx'"

The type must be one of: `concept`, `example`, `code`, `table`.

### "Undefined tag 'xxx'"

Add the tag to your `config.yaml` file.

### "Duplicate node ID"

Each `{#c-...}` ID must be unique across all files.

### "Edge target not found"

The referenced node ID doesn't exist. Check spelling.

### Positions not saving

Positions are automatically synced when you run `generate` if the excalidraw file is newer than the positions file. Just save your excalidraw file and run `generate` again.

---

## Examples

### Simple Hierarchy

````markdown
## Programming Basics {#c-programming-basics}

> [!meta]
> tags: programming
> type: concept

The foundations of programming.

### Variables {#c-variables}

> [!meta]
> type: concept

Variables store data values.

### Functions {#c-functions}

> [!meta]
> type: concept

```edges
prereqs: c-variables
```
````

Functions are reusable blocks of code.

````

### With Code Examples

```markdown
## Python Lists {#c-python-lists}

> [!meta]
> tags: python
> type: code

```edges
related: c-python-tuples
````

Lists are mutable sequences:

```python
my_list = [1, 2, 3]
my_list.append(4)
```

````

### Cross-File Linking

In `databases.md`:
```markdown
## SQL Joins {#c-sql-joins}

```edges
prereqs: c-sql-basics
related: c-python-pandas
````

See also [[c-python-pandas]] for Python integration.

```

The link to `c-python-pandas` works even if it's defined in a different file.

```
