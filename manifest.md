# Mind‑Map

> **What this is:** A deterministic, plain‑Markdown convention so your notes are readable today and parsable into an infinite‑canvas mind map (nodes + links). This specification is 100% deterministic—no ambiguity in parsing.

---

## 1) The mental model (why these rules?)

When you look at a complex topic, you want to _see_ structure:

- **Concepts** become **boxes** (nodes) on the canvas.
- **Relationships** become **arrows** (edges) between boxes.
- **Details** (text, code, lists) stay inside the box, not as separate nodes—unless you want them to be.

Plain Markdown on its own doesn’t have formal “nodes” and “edges,” so we add a **tiny bit of structure** that:

- keeps files 100% readable in any Markdown app, and
- is easy to parse later.

You’ll do this by:

1. giving each concept a **stable ID**,
2. adding a simple **Meta** block with light metadata, and
3. declaring relationships in a short **edges** code fence (plus normal inline links for convenience).

---

## 2) Nodes = Headings (with stable IDs)

**Rule:** Every concept you want as a box on the canvas is a Markdown heading with a stable ID.

- Use `##` for primary concepts in a file (H2). Use `###` (H3) for sub‑concepts _if you also want them as nodes_.
- Give each concept a **stable ID** using the `{#id}` anchor syntax.
- IDs should be **globally unique** across your entire app, **kebab‑case**, and start with `c-` for concept IDs (e.g., `{#c-sql-joins}`).

**Why:**

- Headings are natural visual separators in MD.
- The `{#id}` gives you a permanent handle to link to, even if you rename the heading later.
- The `c-` prefix provides **namespace isolation** - it prevents conflicts with other ID systems and makes concept IDs instantly recognizable in your text and code.

**Example:**

```markdown
## SQL Joins {#c-sql-joins}
```

Now `c-sql-joins` is the canonical node ID.

> **Tip:** If you later rename the title to “Relational Joins in SQL,” the ID stays the same. All your links keep working.

---

## 3) The Meta block (lightweight, readable, and parseable)

Right under the heading, add a short callout that holds structured fields. We’ll use a normal blockquote so it looks decent in any viewer.

```markdown
> [!meta]
> tags: sql, databases, querying
> type: concept # concept | example | code | table
```

**What the fields mean (and why they're useful on a canvas):**

- **tags**: must be from the predefined list in your project's `config.yaml`. Used for colors/filters on the canvas.
- **type**: must be one of: `concept` | `example` | `code` | `table`. Each type has distinct visual styling.

**Rules:**

- Omit empty fields entirely.
- If no `[!meta]` block is present, defaults are applied: `type: concept`, no tags.

---

## 4) The `edges` fence (explicit relationships)

Below the Meta, add a tiny code fence named `edges`. This is unintrusive in MD and easy to parse later.

```edges
prereqs: c-sql-basics
related: c-query-optimization, c-data-modeling
contrasts: c-nosql-joins
```

**Edge types (exhaustive list):**

| Type        | Visual                | Description                                       |
| ----------- | --------------------- | ------------------------------------------------- |
| `prereqs`   | Arrow (narrow stroke) | Learning dependencies. Directed: source → target. |
| `related`   | Line (no arrow)       | Lateral associations. Undirected.                 |
| `contrasts` | Line (no arrow)       | Opposing/alternative ideas. Undirected.           |

**Parent-child edges:** Automatically inferred from heading hierarchy (H2 → H3 → H4). Never declared explicitly in `edges`.

**Rules:**

- If no `edges` fence is present, only inline links and heading hierarchy create edges.
- The `edges` fence is optional.
- Use comma-separated IDs on one line, or one ID per line—be consistent within a file.

---

## 5) Inline links = implicit relationships (the easy, daily habit)

While writing, you'll naturally reference other concepts. Use standard markdown links with anchors:

```markdown
See also [SQL Basics](#c-sql-basics) and [Database Normalization](#c-database-normalization).
```

- `[Display Text](#c-id)` links to the heading with that anchor ID.
- These links are **clickable** in VS Code, Cursor, and most markdown editors.
- The parser extracts these as `related` edges for the mind map.

**Parsing rule:** Treat inline links to `#c-` anchors as **implicit** `related` edges unless a typed edge already connects the nodes.

> **Why this matters:** You get edges "for free" while writing naturally, and the links are immediately clickable for navigation. The `edges` fence is only for clarity or when you need a specific relation type.

---

## 6) Media (images, video, URLs)

Node content can include media using standard Markdown syntax.

**Folder structure:** For `notes.md`, media files go in `notes_media/` alongside the markdown file.

```
notes.md
notes_media/
  diagram.png
  demo.mp4
```

**Embedding:**

```markdown
![Diagram](./notes_media/diagram.png)
![Demo video](./notes_media/demo.mp4)
[External resource](https://example.com/docs)
```

**Rendering:**

- Images: displayed inline in the node.
- Videos: displayed as thumbnail (if supported) or clickable link.
- URLs: displayed as clickable text that opens in browser.

---

## 7) Content inside a node (clear, readable Markdown)

Everything below the Meta/edges belongs to the node's content: paragraphs, lists, images, code, media.

**Example structure:**

````markdown
## SQL Inner Join {#c-sql-inner-join}

> [!meta]
> tags: sql, joins
> type: concept

```edges
prereqs: c-sql-basics
contrasts: c-sql-outer-join
```
````

**What it is:** The inner join returns rows where keys match in both tables.

**Why it matters:** It’s the most common join for combining normalized tables.

### Syntax {#c-sql-inner-join-syntax}

```sql
SELECT *
FROM orders o
JOIN customers c ON o.customer_id = c.id;
```

### Pitfalls {#c-sql-inner-join-pitfalls}

- Missing JOIN conditions → accidental cross joins.
- Duplicate keys → unintended row multipliers.

See also [SQL Outer Join](#c-sql-outer-join).

````

> **Note:** Sub‑sections (`###`) can also be nodes if you add `{#id}`. If you don’t add an ID, they’re just formatting—no separate box will be created.

---

## 8) Your "four sub‑headers" hub pattern (boxed example)

Here’s your exact scenario: one main box connected to four child boxes, with descriptions and code in some children, and cross‑links inside descriptions.

```markdown
# Learning Demo

## Header Example {#c-header-example}

> [!meta]
> tags: learning, demo
> type: concept

```edges
prereqs: c-learning-systems
related: c-linked-notes
````

**Overview:** This is the central box. The four `###` sub-headers below automatically become children (inferred from heading hierarchy). I'll also reference [Linked Notes](#c-linked-notes) in text (that creates another edge automatically).

### Sub A (has code) {#c-sub-a}

A quick snippet:

```js
function spacedRepetition(item, days) {
  return Date.now() + days * 24 * 60 * 60 * 1000;
}
```

### Sub B (has description) {#c-sub-b}

This is a description. The term **backlinks** connects to [Linked Notes](#c-linked-notes).

### Sub C (points elsewhere) {#c-sub-c}

See also [Sub D](#c-sub-d) and [Active Recall](#c-active-recall).

### Sub D (mini note) {#c-sub-d}

One‑liner with a nod back to [Learning Systems](#c-learning-systems).

````

In a different file:

```markdown
## Linked Notes {#c-linked-notes}

> [!meta]
> tags: zettelkasten
> type: concept
> related: c-header-example

Short description of linked notes / backlinks.
````

On the canvas, you'll see:

- **Header Example** box with arrows to **Sub A**–**D** (children, inferred from heading hierarchy) and to **Learning Systems** (prereqs).
- Lines (no arrows) between **Header Example** and **Linked Notes** (related edges from `edges` fence and inline mentions).

---

## 9) Cross‑file links and stability

Link across files using globally unique IDs:

`[Big O](#c-big-o)` → never breaks if you move/rename files or headings since IDs are stable across your entire app.

**Best practice:** Always use `[Display Text](#c-id)` links. IDs are globally unique, so they provide reliable cross-file linking without any fragility. Plus, these links are clickable in your editor.

---

## 10) File‑level YAML (optional, for styling or grouping)

If you want global metadata (e.g., per‑file color or icon), put a YAML front‑matter at the top. It’s optional and harmless in viewers that ignore it.

```yaml
---
title: Calculus Foundations
tags: [math, foundations]
color: "#5B8FF9" # could tint all nodes from this file
icon: "🧠"
---
```

Your app can use this to give nodes from the same file a shared color or default tag.

---

## 11) Types and tags

**Types (predefined, exhaustive):**

| Type      | Use case                                    |
| --------- | ------------------------------------------- |
| `concept` | Default. Standard explanatory nodes.        |
| `example` | Worked examples, demonstrations.            |
| `code`    | Code snippets, implementations.             |
| `table`   | Data tables, comparisons, reference charts. |

**Tags:** Defined per project in `config.yaml`. Each tag maps to a color. Nodes inherit the color of their first tag.

**Validation:** Parser rejects unknown types. Parser warns on undefined tags.

---

## 12) Minimal conventions to remember

- **IDs**: globally unique across your entire app, stable, `c-kebab-case` (e.g., `c-linear-algebra`).
- **One concept = one heading** (H2 for primaries; H3+ for sub‑concepts you care about).
- **Meta**: only the fields you need; keep it short.
- **`edges` fence**: list IDs only (avoid titles here). Comma‑separate or one per line—be consistent.
- **Inline links**: use `[Display Text](#c-id)` in prose whenever possible—they're clickable!

---

## 13) A full, realistic example (copy‑paste template)

````markdown
---
title: Databases 101
tags: [databases]
---

# Databases 101

## Relational Model {#c-relational-model}

> [!meta]
> tags: databases
> type: concept

```edges
related: c-sql-basics
```
````

**What it is:** A way of organizing data into tables (relations), rows (tuples), and columns (attributes).

**Why it matters:** It’s the foundation of most production data systems.

### Keys and Constraints {#c-keys-constraints}

Primary keys uniquely identify rows; foreign keys link tables.

## SQL Basics {#c-sql-basics}

> [!meta]
> tags: sql
> type: concept

```edges
prereqs: c-relational-model
```

### SELECT {#c-sql-select}

```sql
SELECT id, name FROM users WHERE active = TRUE;
```

### Joins Overview {#c-sql-joins}

> [!meta]
> tags: sql, joins
> type: concept

```edges
prereqs: c-sql-select
related: c-query-optimization
contrasts: c-nosql-joins
```

Inner joins combine rows with matching keys; outer joins keep non‑matches from one side.

See also [Relational Model](#c-relational-model).

```

---

## 14) Folder structure that scales

```

/notes
/learning
learning-foundations.md
spaced-repetition.md
/databases
databases-101.md
sql-joins.md
/programming
python-basics.md
algorithms.md

````

- Keep files focused by domain.
- It’s fine to have multiple nodes per file.
- Use a “MOC” (Map of Content) file per domain to list the top entry points you want on the canvas.

---

## 15) MOCs (Maps of Content) for overviews

A MOC is just a curated index you’ll pin or spotlight in the canvas.

```markdown
# Databases MOC {#c-databases-moc}

> [!meta]
> type: concept
> tags: databases

- [Relational Model](#c-relational-model)
- [SQL Basics](#c-sql-basics)
- [Normalization](#c-normalization)
- [Query Optimization](#c-query-optimization)
````

On the canvas, this becomes a hub node pointing to your chosen anchors.

---

## 16) Renaming, moving files, and not breaking links

- **ID links** (`[text](#c-id)`) are your only linking method - they provide complete stability and are clickable.
- If you change a heading’s text, **do not change its `{#id}`** unless there’s a real reason. That’s your stable handle for cross-file linking.

---

## 17) A tiny "linter" checklist for yourself

When you finish a note, quickly check:

- Does each important heading have a **globally unique** `{#c-...}` ID?
- Is the Meta block present (at least `type` and `tags` when useful)?
- Did I add an `edges` fence for any structured relations?
- Are inline links using `[text](#c-id)` where it matters?
- Did I avoid duplicating the same edge in conflicting ways?

---

## 18) FAQ (practical gotchas)

**Q: Do sub‑headers _have_ to be nodes?**  
A: No. Only add `{#id}` when you want a separate box. Otherwise, it’s just sectioning inside the parent node.

**Q: Can I write normal Markdown without Meta/edges?**  
A: Yes. It stays readable. You just won’t get structured edges for the canvas until you add them.

**Q: What if I mention something in text but forget to add it to `edges`?**  
A: Inline `[text](#c-id)` links still become edges (as generic `related`). You can always promote them later to typed edges by editing the `edges` fence.

**Q: Commas vs new lines in `edges`?**  
A: Pick one and be consistent. Both are easy to parse. Example with new lines:

```edges
prereqs:
  - c-a
  - c-b
related:
  - c-x
  - c-y
```

**Q: Why do IDs start with `c-`?**  
A: The `c-` prefix stands for "concept" and provides namespace isolation. It prevents conflicts with other ID systems in your app and makes concept IDs instantly recognizable in text, links, and code.

**Q: Do I need YAML front‑matter?**  
A: Optional. Use it if you want file‑level styling or grouping. Ignore it otherwise.

---

## 19) Quick starting template (copy this into new files)

````markdown
---
title: <File Title>
tags: [<domain>]
---

# <File Title>

## <Concept Title> {#c-<kebab-id>}

> [!meta]
> tags: <from config.yaml>
> type: concept

```edges
prereqs: <c-ids>
related: <c-ids>
contrasts: <c-ids>
```
````

**What it is:**

**Why it matters:**

### Notes {#c-<kebab-id>-notes}

### Example

```<lang>
// code here
```

See also [Topic Name](#c-topic-id).

```

---

## 20) How you'll parse this later (so you can trust the format now)

**Nodes:**
- Every heading with `{#c-...}` anchor becomes a node.
- Title = node label; `{#id}` = node key.
- **Enforce global uniqueness** of IDs. Reject duplicates.
- If no `[!meta]` block: apply defaults (`type: concept`, no tags).
- Reject unknown `type` values. Warn on undefined `tags`.

**Edges:**
- **Parent-child:** Inferred from heading hierarchy (H2 → H3 → H4). Visual: arrow.
- **`prereqs`:** From `edges` fence. Visual: arrow (narrow stroke).
- **`related`:** From `edges` fence or inline `[text](#c-id)` links. Visual: line (no arrow).
- **`contrasts`:** From `edges` fence. Visual: line (no arrow).
- Dedupe by `(sourceID, targetID, type)`.
- Warn and skip edges referencing non-existent nodes.

**Media:**
- Images/videos: `![alt](./filename_media/file.ext)` → embed in node.
- URLs: `[text](url)` → clickable link.

**Validation:**
- Tags must exist in `config.yaml`.
- Types must be: `concept` | `example` | `code` | `table`.

---

## 21) Project structure (atlas folder)

**Rule:** Organize your knowledge base in the `atlas/` folder, with each project as a subfolder.

```

atlas/
├── sql/
│ ├── sql.md
│ ├── sql_media/
│ ├── config.yaml # Optional: project-specific config
│ ├── sql.excalidraw
│ └── sql.positions.json
├── python/
│ ├── python.md
│ ├── config.yaml
│ └── ...
└── ...

````

**Config hierarchy:**

1. **Default config:** `app/default_config.yaml` — defines base styles for all node types, edge types, and layout settings.
2. **Project config:** `atlas/<project>/config.yaml` — optional, overrides defaults for project-specific tags and style preferences.

**How it works:**

- If a project-specific `config.yaml` exists in the same directory as your markdown file, it will be loaded and merged with the default config.
- Project config values override defaults. For example:
  - Define project-specific tags (e.g., `sql`, `databases`)
  - Customize node/edge colors for this project
  - Change layout settings
- If no project config exists, the app uses `default_config.yaml`.
- You can also specify a config explicitly with `-c path/to/config.yaml`.

**Example project config:**

```yaml
# atlas/sql/config.yaml
tags:
  sql:
    color: "#2196f3"
  databases:
    color: "#1565c0"
  querying:
    color: "#0d47a1"

# Override node style for code blocks
node_types:
  code:
    fill: "#263238"
    stroke: "#00bcd4"
    font_size: 16
````

**Why this structure?**

- **Separation:** Each project/topic has its own folder with all related files.
- **Portability:** You can share or backup individual projects easily.
- **Flexibility:** Define tags and styles per project while maintaining consistent defaults.
- **Media organization:** Each MD file gets its own `<filename>_media/` folder for images/videos.

---

### Final thought

Don’t aim for perfection on day one. Start with IDs and inline links. Add Meta for node properties and `edges` for relationships. Parent-child relationships are automatically inferred from your heading hierarchy, so focus on the relationships that matter most. Over time, your notes naturally grow a map you can walk on.

```

```
