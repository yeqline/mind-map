# Mind‑Map

> **What this is:** A practical, plain‑Markdown convention so your notes are readable today and parsable later into an infinite‑canvas mind map (nodes + links). This guide explains *why* each rule exists, shows examples, and gives you copy‑paste templates.

---

## 1) The mental model (why these rules?)

When you look at a complex topic, you want to *see* structure:
- **Concepts** become **boxes** (nodes) on the canvas.
- **Relationships** become **arrows** (edges) between boxes.
- **Details** (text, code, lists) stay inside the box, not as separate nodes—unless you want them to be.

Plain Markdown on its own doesn’t have formal “nodes” and “edges,” so we add a **tiny bit of structure** that:
- keeps files 100% readable in any Markdown app, and
- is easy to parse later.

You’ll do this by:
1) giving each concept a **stable ID**,
2) adding a simple **Meta** block with light metadata, and
3) declaring relationships in a short **edges** code fence (plus normal inline links for convenience).

---

## 2) Nodes = Headings (with stable IDs)

**Rule:** Every concept you want as a box on the canvas is a Markdown heading with a stable ID.

- Use `##` for primary concepts in a file (H2). Use `###` (H3) for sub‑concepts *if you also want them as nodes*.
- Give each concept a **stable ID** using the `{#id}` anchor syntax.
- IDs should be **kebab‑case** and start with `c-` so they’re easy to recognize and won’t collide (e.g., `{#c-sql-joins}`).

**Why:**
- Headings are natural visual separators in MD.
- The `{#id}` gives you a permanent handle to link to, even if you rename the heading later.

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
> aliases: Relational Joins, SQL Join Types
> tags: sql, databases, querying
> type: concept        # concept | category | example | exercise | cheat-sheet
> difficulty: 2        # 1 (intro) .. 5 (expert)
> parents: [[c-sql-basics]]
> prereqs: [[c-relational-model]]
> sources: [Mode SQL Tutorial](https://mode.com/sql-tutorial/), [PostgreSQL Docs](https://www.postgresql.org/docs/)
```

**What the fields mean (and why they’re useful on a canvas):**
- **aliases**: alternative names for search and nicer hover cards.
- **tags**: colors, filters, or groups on the canvas (`sql`, `databases`).
- **type**: lets you style different node types (e.g., `category` as big hubs, `example` as small rounded notes).
- **difficulty**: quick visual hint; you can also filter by difficulty when reviewing.
- **parents**: who is above this in the hierarchy (up‑arrow on the canvas).
- **prereqs**: what you should already know (directed arrows for learning order).
- **sources**: links that show up on hover or in a side panel.

> **Keep it light.** Only include fields you’ll actually use. Empty fields are fine to omit.

---

## 4) The `edges` fence (explicit relationships)

Below the Meta, add a tiny code fence named `edges`. This is unintrusive in MD and easy to parse later.

```edges
children: c-sql-inner-join, c-sql-outer-join, c-sql-cross-join
related: c-query-optimization, c-data-modeling
contrasts: c-nosql-joins
```

**Edge types you’ll likely need:**
- **parents / children** → hierarchy.
- **prereqs** → learning dependency (directed).
- **related** → lateral association (undirected).
- **contrasts** → opposing/alternative ideas.

**Why both Meta and `edges`?**
- Use **Meta** for upstream relations (`parents`, `prereqs`) close to the node.
- Use **`edges`** for any set of links you want to keep together (especially `children`, `related`, `contrasts`).
- It’s okay to repeat; your parser can dedupe. If there’s a conflict, you can treat the explicit `edges` fence as the source of truth.

---

## 5) Inline links = implicit relationships (the easy, daily habit)

While writing, you’ll naturally reference other concepts. Use wiki‑style links:

```markdown
See also [[c-sql-basics]] and [[databases#Normalization]].
```

- `[[c-id]]` links by ID (most stable).
- `[[file-name#Heading Title]]` links by location (handy while drafting).
- `[[c-target|Display Text]]` for nicer prose while keeping a clean target.

**Parsing rule later:** Treat inline links as **implicit** `related` edges unless a typed edge already connects the nodes.

> **Why this matters:** You get edges “for free” while writing naturally. The `edges` fence is only for clarity or when you need a specific relation type.

---

## 6) Content inside a node (clear, readable Markdown)

Everything below the Meta/edges belongs to the node’s content: paragraphs, lists, images, code.

**Example structure:**
```markdown
## SQL Inner Join {#c-sql-inner-join}

> [!meta]
> tags: sql, joins
> type: concept
> prereqs: [[c-sql-basics]]

```edges
contrasts: c-sql-outer-join
```

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

See also [[c-sql-outer-join]].
```

> **Note:** Sub‑sections (`###`) can also be nodes if you add `{#id}`. If you don’t add an ID, they’re just formatting—no separate box will be created.

---

## 7) Your “four sub‑headers” hub pattern (boxed example)

Here’s your exact scenario: one main box connected to four child boxes, with descriptions and code in some children, and cross‑links inside descriptions.

```markdown
# Learning Demo

## Header Example {#c-header-example}

> [!meta]
> aliases: Sample Hub
> tags: learning, demo
> type: category
> parents: [[c-learning-systems]]

```edges
children: c-sub-a, c-sub-b, c-sub-c, c-sub-d
related: c-linked-notes
```

**Overview:** This is the central box. It connects to four sub‑boxes. I’ll also reference [[c-linked-notes]] in text (that creates another edge automatically).

### Sub A (has code) {#c-sub-a}
A quick snippet:

```js
function spacedRepetition(item, days){
  return Date.now() + days*24*60*60*1000;
}
```

### Sub B (has description) {#c-sub-b}
This is a description. The term **backlinks** connects to [[c-linked-notes]].

### Sub C (points elsewhere) {#c-sub-c}
See also [[c-sub-d]] and [[learning-foundations#Active Recall]].

### Sub D (mini note) {#c-sub-d}
One‑liner with a nod back to [[c-learning-systems]].
```

In a different file:

```markdown
## Linked Notes {#c-linked-notes}

> [!meta]
> tags: zettelkasten
> type: concept
> related: c-header-example

Short description of linked notes / backlinks.
```

On the canvas, you’ll see:
- One big **Header Example** box with arrows to **Sub A**–**D** (children).
- Lateral edges between **Header Example** and **Linked Notes** (both from `edges` and inline mentions).

---

## 8) Cross‑file links and stability

You have two practical ways to link across files:

1) **By ID (preferred)**: `[[c-big-o]]` → never breaks if you move/rename files or headings.
2) **By location**: `[[algorithms#Big O Notation]]` → convenient while drafting; fragile if you rename the heading.

**Best practice:** Assign IDs (`{#c-...}`) to any heading you’ll likely link to, and favor `[[c-id]]` in your prose. Your future parser can resolve both, but IDs save headaches.

---

## 9) File‑level YAML (optional, for styling or grouping)

If you want global metadata (e.g., per‑file color or icon), put a YAML front‑matter at the top. It’s optional and harmless in viewers that ignore it.

```yaml
---
title: Calculus Foundations
tags: [math, foundations]
color: "#5B8FF9"   # could tint all nodes from this file
icon: "🧠"
---
```

Your app can use this to give nodes from the same file a shared color or default tag.

---

## 10) Types, tags, and difficulty (how they help visually)

- **type** → Different shapes or sizes: `category` (large hub), `concept` (standard), `example` (small rounded), `exercise` (diamond), `cheat-sheet` (note badge).
- **tags** → Colors or clusters on the canvas (`sql` in blue, `math` in green, etc.).
- **difficulty** → Filter while revising (start with `1` and `2`; work up to `4` and `5`).

Keep values simple and consistent. You can always restyle later.

---

## 11) Minimal conventions to remember

- **IDs**: unique, stable, `c-kebab-case` (e.g., `c-linear-algebra`).
- **One concept = one heading** (H2 for primaries; H3+ for sub‑concepts you care about).
- **Meta**: only the fields you need; keep it short.
- **`edges` fence**: list IDs only (avoid titles here). Comma‑separate or one per line—be consistent.
- **Inline links**: use `[[c-id]]` in prose whenever possible.

---

## 12) A full, realistic example (copy‑paste template)

```markdown
---
title: Databases 101
tags: [databases]
---

# Databases 101

## Relational Model {#c-relational-model}

> [!meta]
> tags: databases
> type: concept
> children: [[c-normalization]]

```edges
related: c-sql-basics
```

**What it is:** A way of organizing data into tables (relations), rows (tuples), and columns (attributes).

**Why it matters:** It’s the foundation of most production data systems.

### Keys and Constraints {#c-keys-constraints}
Primary keys uniquely identify rows; foreign keys link tables.

## SQL Basics {#c-sql-basics}

> [!meta]
> tags: sql
> type: category
> prereqs: [[c-relational-model]]

```edges
children: c-sql-select, c-sql-joins, c-sql-aggregation
```

### SELECT {#c-sql-select}
```sql
SELECT id, name FROM users WHERE active = TRUE;
```

### Joins Overview {#c-sql-joins}

> [!meta]
> tags: sql, joins
> type: concept
> prereqs: [[c-sql-select]]

```edges
children: c-sql-inner-join, c-sql-outer-join
related: c-query-optimization
contrasts: c-nosql-joins
```

Inner joins combine rows with matching keys; outer joins keep non‑matches from one side.

See also [[c-relational-model]].
```

---

## 13) Folder structure that scales

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
```

- Keep files focused by domain.
- It’s fine to have multiple nodes per file.
- Use a “MOC” (Map of Content) file per domain to list the top entry points you want on the canvas.

---

## 14) MOCs (Maps of Content) for overviews

A MOC is just a curated index you’ll pin or spotlight in the canvas.

```markdown
# Databases MOC {#c-databases-moc}

> [!meta]
> type: category
> tags: databases

- [[c-relational-model]]
- [[c-sql-basics]]
- [[c-normalization]]
- [[c-query-optimization]]
```

On the canvas, this becomes a hub node pointing to your chosen anchors.

---

## 15) Renaming, moving files, and not breaking links

- Prefer **ID links** (`[[c-id]]`) for stability.
- If you must link by location (`[[file#Heading]]`), be ready to refresh edges after renames (your parser can detect missing anchors and propose fixes).
- If you change a heading’s text, **do not change its `{#id}`** unless there’s a real reason. That’s your stable handle.

---

## 16) A tiny “linter” checklist for yourself

When you finish a note, quickly check:
- Does each important heading have a `{#c-...}` ID?
- Is the Meta block present (at least `type` and `tags` when useful)?
- Did I add an `edges` fence for any structured relations?
- Are inline links using `[[c-id]]` where it matters?
- Did I avoid duplicating the same edge in conflicting ways?

---

## 17) FAQ (practical gotchas)

**Q: Do sub‑headers *have* to be nodes?**  
A: No. Only add `{#id}` when you want a separate box. Otherwise, it’s just sectioning inside the parent node.

**Q: Can I write normal Markdown without Meta/edges?**  
A: Yes. It stays readable. You just won’t get structured edges for the canvas until you add them.

**Q: What if I mention something in text but forget to add it to `edges`?**  
A: Inline `[[...]]` links still become edges (as generic `related`). You can always promote them later to typed edges by editing the `edges` fence.

**Q: Commas vs new lines in `edges`?**  
A: Pick one and be consistent. Both are easy to parse. Example with new lines:

```edges
children:
  - c-a
  - c-b
related:
  - c-x
  - c-y
```

**Q: Do I need YAML front‑matter?**  
A: Optional. Use it if you want file‑level styling or grouping. Ignore it otherwise.

---

## 18) Quick starting template (copy this into new files)

```markdown
---
title: <File Title>
tags: [<domain>]
---

# <File Title>

## <Concept Title> {#c-<kebab-id>}

> [!meta]
> aliases:
> tags:
> type: concept
> parents:
> prereqs:
> sources:

```edges
children:
related:
contrasts:
```

**What it is:**

**Why it matters:**

### Notes {#c-<kebab-id>-notes}

### Example
```<lang>
// code here
```

See also [[c-...]].
```

---

## 19) How you’ll parse this later (so you can trust the format now)

- **Nodes**: every heading with an `{#c-...}` anchor becomes a node. The visible title is the node label; the `{#id}` is the node key.
- **Edges**: collected from `edges` fences (typed) and inline `[[...]]` links (implicit). Dedupe by `(sourceID, targetID, type)`.
- **Metadata**: read from the Meta block (simple `key: value` lines). Unknown keys can be ignored or stored as generic attributes.
- **Styling**: use `type`, `tags`, and optional file‑level YAML.

This keeps your Markdown pleasant to read while giving your future app a clean, deterministic structure.

---

### Final thought
Don’t aim for perfection on day one. Start with IDs and inline links. Add Meta and `edges` where they help structure. Over time, your notes naturally grow a map you can walk on.

