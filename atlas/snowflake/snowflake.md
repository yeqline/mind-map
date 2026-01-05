# Snowflake (High‑Level Mind Map)

## Snowflake MOC {#c-snowflake-moc}

> [!meta]
> type: concept

```edges
related: c-snowflake-overview, c-snowflake-architecture, c-snowflake-data-organization, c-snowflake-ingestion, c-snowflake-query-compute, c-snowflake-security-governance, c-snowflake-sharing-collaboration, c-snowflake-data-engineering, c-snowflake-programmability, c-snowflake-cost-management, c-snowflake-ops-observability
```

- [Snowflake Overview](#c-snowflake-overview)
- [Core Architecture](#c-snowflake-architecture)
- [Data Organization](#c-snowflake-data-organization)
- [Ingestion & Loading](#c-snowflake-ingestion)
- [Query & Compute](#c-snowflake-query-compute)
- [Security & Governance](#c-snowflake-security-governance)
- [Data Sharing & Collaboration](#c-snowflake-sharing-collaboration)
- [Data Engineering](#c-snowflake-data-engineering)
- [Programmability](#c-snowflake-programmability)
- [Cost Management](#c-snowflake-cost-management)
- [Operations & Observability](#c-snowflake-ops-observability)

## Snowflake Overview {#c-snowflake-overview}

> [!meta]
> type: concept

```edges
related: c-snowflake-architecture, c-snowflake-query-compute, c-snowflake-data-organization
```

**What it is:** A cloud-native data platform centered on SQL analytics, elastic compute, and managed storage.

**Core ideas:** Separation of storage and compute, scale-out virtual warehouses, and built-in security/governance for shared data use.

See also [Core Architecture](#c-snowflake-architecture) and [Cost Management](#c-snowflake-cost-management).

## Core Architecture {#c-snowflake-architecture}

> [!meta]
> type: concept

```edges
related: c-snowflake-query-compute, c-snowflake-data-organization, c-snowflake-ops-observability
```

Snowflake is commonly described as three logical layers: **cloud services**, **compute**, and **storage**. Most day-to-day design choices come down to how you size/scale compute and how you model data for storage efficiency.

### Storage / Compute Separation {#c-snowflake-storage-compute-separation}

Independent scaling of compute (warehouses) without moving data; multiple workloads can access the same storage.

### Cloud Services Layer {#c-snowflake-cloud-services-layer}

Handles metadata, authentication, transaction management, query optimization, and coordination of execution.

### Virtual Warehouses {#c-snowflake-virtual-warehouses}

Isolated compute clusters that execute queries and DML. Warehouses are where most cost and concurrency decisions live.

See also [Multi-Cluster Warehouses](#c-snowflake-multi-cluster-warehouses) and [Auto-suspend / Auto-resume](#c-snowflake-auto-suspend-resume).

### Multi-Cluster Warehouses {#c-snowflake-multi-cluster-warehouses}

Automatic scale-out for concurrency (multiple clusters) while keeping a consistent warehouse interface for users.

### Caching (Result + Data) {#c-snowflake-caching}

Multiple caching layers can reduce repeated work. It affects performance, reproducibility, and benchmarking.

## Data Organization {#c-snowflake-data-organization}

> [!meta]
> type: concept

```edges
related: c-snowflake-micro-partitions, c-snowflake-stages-file-formats, c-snowflake-time-travel-zero-copy
```

Focus on **clear boundaries** (account/database/schema) and **query-friendly physical layout** (micro-partitions, clustering, pruning).

### Account / Organization Model {#c-snowflake-account-organization}

Security and usage are scoped to accounts; cross-account collaboration uses sharing/replication patterns (see [Data Sharing & Collaboration](#c-snowflake-sharing-collaboration)).

### Database / Schema / Table {#c-snowflake-db-schema-table}

Core logical containers. Keep schemas purposeful (domain boundaries) and tables modeled for analytical access patterns.

### Views and Materialized Views {#c-snowflake-views-materialized-views}

Encapsulation for logic; materialized views trade storage/maintenance for speed on repeatable patterns.

### Micro-partitions {#c-snowflake-micro-partitions}

Automatic, immutable columnar storage segments with metadata used for pruning; the basis for many performance behaviors.

See also [Clustering Keys](#c-snowflake-clustering-keys) and [Search Optimization](#c-snowflake-search-optimization).

### Stages & File Formats {#c-snowflake-stages-file-formats}

Staging locations (internal/external) and file format definitions used for loading and external data access.

## Ingestion & Loading {#c-snowflake-ingestion}

> [!meta]
> type: concept

```edges
related: c-snowflake-stages-file-formats, c-snowflake-copy-into, c-snowflake-snowpipe
```

Loading patterns range from batch (SQL-driven) to near-real-time (event-driven). Pick based on latency needs, operational complexity, and cost.

### COPY INTO {#c-snowflake-copy-into}

Batch loading from a stage into tables; good for scheduled loads and predictable batches.

### Snowpipe {#c-snowflake-snowpipe}

Managed continuous ingestion that reacts to new files; useful for streaming-ish file arrival patterns.

### External Tables {#c-snowflake-external-tables}

Query data in external storage with metadata definitions; often a bridge for lake-house style access.

## Query & Compute {#c-snowflake-query-compute}

> [!meta]
> type: concept

```edges
related: c-snowflake-virtual-warehouses, c-snowflake-caching, c-snowflake-performance-optimization
```

Most performance work is **warehouse sizing**, **concurrency control**, and **data pruning** (see [Micro-partitions](#c-snowflake-micro-partitions)).

### Warehouse Sizing & Concurrency {#c-snowflake-warehouse-sizing-concurrency}

Choose sizes for latency/throughput and split workloads into separate warehouses to reduce contention.

### Query Profiling {#c-snowflake-query-profiling}

Use execution details to identify bottlenecks (scan volume, skew, joins, spilling), then adjust warehouse/data layout.

### Semi-structured Data (VARIANT) {#c-snowflake-variant-semi-structured}

Store JSON/Avro/Parquet-like structures and query with SQL; design needs attention to projection, pruning, and schema drift.

## Performance & Optimization {#c-snowflake-performance-optimization}

> [!meta]
> type: concept

```edges
prereqs: c-snowflake-query-compute, c-snowflake-micro-partitions
related: c-snowflake-clustering-keys, c-snowflake-search-optimization
```

Performance work is typically about **reducing scanned data**, **avoiding wasted compute**, and **improving concurrency**.

### Clustering Keys {#c-snowflake-clustering-keys}

Optional tuning to improve pruning on large tables with common filter patterns; comes with maintenance trade-offs.

### Search Optimization {#c-snowflake-search-optimization}

Optional feature to accelerate selective lookups; use for targeted access patterns where pruning alone isn’t enough.

### Caching Strategy {#c-snowflake-caching-strategy}

Understand when caches help vs mislead (e.g., benchmarks). Pair with warehouse isolation for repeatable testing.

See also [Caching](#c-snowflake-caching).

## Security & Governance {#c-snowflake-security-governance}

> [!meta]
> type: concept

```edges
related: c-snowflake-rbac, c-snowflake-masking-row-access, c-snowflake-auditing
```

Treat Snowflake as a governed platform: least-privilege access, policy-based protection for sensitive data, and auditable usage.

### RBAC (Roles & Grants) {#c-snowflake-rbac}

Role-based permissions for objects and actions; typically modeled as a hierarchy aligned to teams and environments.

### Data Masking & Row Access Policies {#c-snowflake-masking-row-access}

Enforce column masking and row-level filtering centrally, reducing app-side logic and risk of leakage.

### Network Controls (Policies / Private Connectivity) {#c-snowflake-network-controls}

Restrict access by IP/network and prefer private connectivity options for sensitive environments.

### Auditing & Usage Tracking {#c-snowflake-auditing}

Use account usage and access history for governance, incident response, and cost attribution.

## Data Sharing & Collaboration {#c-snowflake-sharing-collaboration}

> [!meta]
> type: concept

```edges
related: c-snowflake-secure-data-sharing, c-snowflake-marketplace, c-snowflake-replication-failover
```

Snowflake enables data collaboration without copying data in the traditional sense; design sharing with governance and lifecycle in mind.

### Secure Data Sharing {#c-snowflake-secure-data-sharing}

Share database objects with other accounts while keeping governance controls; avoids “export + re-import” workflows.

### Marketplace Patterns {#c-snowflake-marketplace}

Operational and product considerations for publishing/consuming shared datasets (entitlements, versions, SLAs).

### Replication & Failover {#c-snowflake-replication-failover}

Replicate data/objects across regions/accounts for resilience and DR; coordinate with security and cost strategies.

## Data Engineering (Change + Automation) {#c-snowflake-data-engineering}

> [!meta]
> type: concept

```edges
related: c-snowflake-streams, c-snowflake-tasks, c-snowflake-time-travel-zero-copy
```

Use built-in primitives for incremental processing and automation; keep pipelines observable and idempotent.

### Streams (Change Tracking) {#c-snowflake-streams}

Capture table changes for incremental downstream processing; often paired with tasks.

### Tasks (Scheduling) {#c-snowflake-tasks}

Run SQL on schedules or dependency chains; align task graphs with data freshness requirements.

### Time Travel & Zero-Copy Cloning {#c-snowflake-time-travel-zero-copy}

Recover/inspect prior data states and clone objects quickly for dev/test and safe experimentation.

## Programmability {#c-snowflake-programmability}

> [!meta]
> type: concept

```edges
related: c-snowflake-snowpark, c-snowflake-udf-procedures, c-snowflake-native-apps
```

Choose between SQL-first patterns and embedded compute depending on complexity, governance, and team skills.

### Snowpark {#c-snowflake-snowpark}

APIs for data transformations in languages (in addition to SQL) while staying close to the platform’s governance model.

### UDFs / Stored Procedures {#c-snowflake-udf-procedures}

Encapsulate reusable logic; balance power with operational complexity and security constraints.

### Native Apps {#c-snowflake-native-apps}

Package and distribute applications within the platform; consider isolation, permissions, and upgrade strategies.

## Cost Management {#c-snowflake-cost-management}

> [!meta]
> type: concept

```edges
related: c-snowflake-auto-suspend-resume, c-snowflake-resource-monitors, c-snowflake-warehouse-sizing-concurrency
```

Cost is primarily driven by **warehouse runtime** and **storage footprint**. Start with guardrails and attribution, then optimize.

### Auto-suspend / Auto-resume {#c-snowflake-auto-suspend-resume}

Turn warehouses off when idle to control spend; tune timeouts to avoid thrash.

### Resource Monitors {#c-snowflake-resource-monitors}

Budgets, alerts, and enforcement to prevent runaway spend; align monitors to teams/projects.

### Workload Isolation {#c-snowflake-workload-isolation}

Separate warehouses by workload type (ELT, BI, ad hoc) to reduce contention and make cost attribution clearer.

## Operations & Observability {#c-snowflake-ops-observability}

> [!meta]
> type: concept

```edges
related: c-snowflake-auditing, c-snowflake-query-profiling, c-snowflake-resource-monitors
```

Operational excellence comes from visibility: query behavior, user activity, failures, and spend—then closing the loop with guardrails.

### Account Usage Views {#c-snowflake-account-usage-views}

Historical views for usage, performance, security events, and cost analysis; foundational for dashboards and alerts.

### Alerting & Incident Response {#c-snowflake-alerting-incident-response}

Define what “bad” looks like (latency, failures, spend spikes, access anomalies) and automate notifications and runbooks.
