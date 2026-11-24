# PostgreSQL

PostgreSQL is a general-purpose relational database management system designed to run as a **database server**. Applications connect to that server, send SQL queries, and receive results; they do not open PostgreSQL's data files directly.

The server owns the persistent state and coordinates access to shared structured data for independent clients, centrally managing transactions, constraints, concurrency control, query planning, and durability.

## Commands

### `VACUUM`

`VACUUM` removes row versions left by updates and deletes once no transaction needs them, making their space available for reuse. This cleanup is necessary because PostgreSQL's MVCC retains old versions while they may still be visible to active transactions. Standard `VACUUM` generally does not return that space to the operating system; autovacuum performs routine cleanup automatically when enabled. [PostgreSQL routine vacuuming](https://www.postgresql.org/docs/18/routine-vacuuming.html).

```text
postgres=# VACUUM grades;
postgres=# VACUUM (ANALYZE) grades;
```

The first command cleans `grades`; the second also updates planner statistics. `VACUUM FULL` rewrites a table to compact it and reclaim more disk space, but requires extra space during the rewrite and an `ACCESS EXCLUSIVE` lock that blocks concurrent use of that table. `VACUUM` cannot run inside a transaction block. [PostgreSQL `VACUUM` documentation](https://www.postgresql.org/docs/18/sql-vacuum.html).

### `EXPLAIN`

`EXPLAIN` shows the execution plan PostgreSQL chooses for a statement, including operations such as scans and joins, estimated costs, and estimated row counts. It plans the statement without executing it.

For example, a plan for an unfiltered query against a `grades` table shows a sequential scan:

```txt
postgres=# EXPLAIN SELECT * FROM grades;
                         QUERY PLAN
-------------------------------------------------------------
Seq Scan on grades  (cost=0.00..219935.18 rows=13141718 width=22)
(1 row)
```

- **`Seq Scan on grades`:** Read the `grades` table sequentially to produce the result.
- **`cost=0.00..219935.18`:** Estimated startup cost before producing rows, followed by the total cost to produce all rows. These are planner cost units, not elapsed time.
- **`rows=13141718`:** Estimated number of rows this plan node outputs, not a measured row count.
    - For this unfiltered query, use it as a cheap approximation of the table's row count when an exact value is unnecessary. The estimate depends on table statistics and may be stale; `SELECT count(*) FROM grades` must scan the table or an index to return an exact count. [PostgreSQL row estimation](https://www.postgresql.org/docs/current/row-estimation-examples.html) and [`count(*)` behavior](https://www.postgresql.org/docs/current/functions-aggregate.html).
- **`width=22`:** Estimated average size of each output row, in bytes.

The displayed `cost`, `rows`, and `width` values are planner estimates, not measurements. `QUERY PLAN` is the output column heading; `(1 row)` here and the row counts after later plan outputs count lines of plan output, not rows returned by the queries. [PostgreSQL `EXPLAIN` basics](https://www.postgresql.org/docs/current/using-explain.html).

`EXPLAIN ANALYZE` executes the statement and adds actual row counts and timing for each plan node, making it useful for comparing estimates with observed work. Because it executes the statement, data-changing commands have their normal effects. [PostgreSQL `EXPLAIN` documentation](https://www.postgresql.org/docs/current/sql-explain.html).

## Query Planning and Execution

PostgreSQL chooses among candidate plans using estimated costs, not a fixed row-count threshold. The chosen plan determines how rows are found, ordered, and, when applicable, processed in parallel. [PostgreSQL `EXPLAIN` scan examples](https://www.postgresql.org/docs/18/using-explain.html).

The examples use a `grades` table with a primary-key index on `id` and another index on `g`. This setup creates the table, populates it with generated values, and creates the index on `g`:

```text
postgres=# CREATE TABLE grades (
    id SERIAL PRIMARY KEY,
    g INT,
    name TEXT
);

postgres=# INSERT INTO grades (g, name)
SELECT
    random() * 100,
    substring(md5(random()::TEXT), 0, floor(random() * 31)::INT)
FROM generate_series(0, 1000000);

postgres=# CREATE INDEX grades_g ON grades(g);
```

The insert generates 1,000,001 rows because both endpoints of `generate_series` are included. The captured plans use different table statistics: their estimated row counts and costs will not match a fresh table populated by this insert alone. [PostgreSQL `generate_series`](https://www.postgresql.org/docs/current/functions-srf.html) and [`EXPLAIN` examples](https://www.postgresql.org/docs/current/sql-explain.html).

### Access Paths and Selectivity

For this equality condition on the primary key, PostgreSQL chose an index scan instead of reading the whole table:

```txt
postgres=# EXPLAIN SELECT * FROM grades WHERE id = 10;
                                QUERY PLAN
---------------------------------------------------------------------------
 Index Scan using grades_pkey on grades  (cost=0.43..8.45 rows=1 width=22)
   Index Cond: (id = 10)
(2 rows)
```

`grades_pkey` is the index created by `id SERIAL PRIMARY KEY`. `Index Cond: (id = 10)` shows that PostgreSQL uses the condition to find matching index entries, then fetches the corresponding table row. The primary key permits at most one match; `rows=1` is the planner's estimate, not confirmation that row `10` exists. [PostgreSQL primary keys](https://www.postgresql.org/docs/current/ddl-constraints.html#DDL-CONSTRAINTS-PRIMARY-KEYS) and [`EXPLAIN` basics](https://www.postgresql.org/docs/current/using-explain.html).

These scans differ in how they locate heap rows (the table's stored row versions) and in the cost of visiting their pages:

- **Table scan (`Seq Scan`):** Reads the table's heap pages sequentially and tests rows against any filter. It avoids index lookups and is attractive when a large share of the table must be read, even if an index exists.
- **Index scan (`Index Scan`):** Finds matching entries in an index and follows their row locations into the heap as it goes. This avoids scanning unrelated table pages when few rows match, but many matches scattered across heap pages make the repeated heap visits expensive. A suitable B-tree index scan can also deliver rows in index order.
- **Bitmap scan (`Bitmap Index Scan` + `Bitmap Heap Scan`):** Collects matching row locations from an index before visiting the relevant heap pages in physical order. Bitmap-building work trades off against fewer scattered heap-page visits when more rows match than a simple index scan handles cheaply; bitmap heap access loses index order, so an `ORDER BY` may still require a sort.

The following plans all project only `name` and show how estimated selectivity changes the access path. For `id < 100`, PostgreSQL estimates 98 matching rows and uses the primary-key index to find their heap rows:

```text
postgres=# EXPLAIN SELECT name FROM grades WHERE id < 100;
Index Scan using grades_pkey on grades  (cost=0.43..391.13 rows=98 width=4)
  Index Cond: (id < 100)
```

For `id > 100`, it estimates 5,000,248 output rows and chooses to scan the table, applying the condition as a `Filter` rather than visiting the index and then fetching many heap rows:

```text
postgres=# EXPLAIN SELECT name FROM grades WHERE id > 100;
Seq Scan on grades  (cost=0.00..134265.34 rows=5000248 width=4)
  Filter: (id > 100)
```

For `g > 95`, the plan instead uses the `g` index to build a bitmap of candidate heap locations, then fetches the rows through `Bitmap Heap Scan`:

```text
postgres=# EXPLAIN SELECT name FROM grades WHERE g > 95;
Bitmap Heap Scan on grades  (cost=3859.77..110758.53 rows=205850 width=4)
  Recheck Cond: (g > 95)
  ->  Bitmap Index Scan on g  (cost=0.00..3808.31 rows=205850 width=0)
        Index Cond: (g > 95)
```

The captured index is named `g`, whereas the setup above names it `grades_g`. These are plan estimates from the captured instance, not measured row counts or universal thresholds for choosing a scan.

#### Bitmap Scan Mechanics

`Bitmap Index Scan` is the index-reading child, not a separate kind of index or a complete table-row scan. Its parent `Bitmap Heap Scan` fetches the rows and checks visibility. [PostgreSQL index/heap access](https://www.postgresql.org/docs/18/indexes-index-only-scans.html).

The bitmap represents candidates on each heap page in one of two ways:

- **Exact entry:** Records candidate tuple locations within the page, so the heap scan examines those tuples rather than every row on the page.
- **Lossy entry:** Records that the page contains candidates but not their tuple locations. The heap scan examines tuples on that page and rechecks the condition to discard nonmatches.

One bitmap can contain both kinds of entry. When the bitmap grows beyond its memory allowance, which depends on `work_mem`, PostgreSQL can convert exact entries to lossy ones. This saves bitmap memory at the cost of examining and rechecking more heap tuples. An index access method can also mark candidate matches for rechecking even when their bitmap entries are exact. [PostgreSQL tuple-ID bitmap implementation](https://doxygen.postgresql.org/tidbitmap_8c_source.html) and [index access methods](https://www.postgresql.org/docs/current/index-functions.html).

The index phase gathers candidates before the heap phase reads pages. The diagram collapses exact tuple locations and lossy page entries into the same page-level mark: `1` means the page contains candidates, not that the bitmap stores only its page number. Here, index matches mark pages 0, 1, and 3; page 2 stays unmarked. The heap scan then visits the marked pages in physical order rather than following each index match immediately:

```mermaid
block-beta
  columns 5
  page["Heap page"] p0["0"] p1["1"] p2["2"] p3["3"]
  before["Before index scan"] b0["0"] b1["0"] b2["0"] b3["0"]
  after["After index scan"] a0["1"] a1["1"] a2["0"] a3["1"]
  style a0 fill:#c8e6c9,stroke:#388e3c
  style a1 fill:#c8e6c9,stroke:#388e3c
  style a3 fill:#c8e6c9,stroke:#388e3c
```

Separate indexes produce separate bitmaps that PostgreSQL combines before visiting the heap. For exact entries, `BitmapAnd` intersects candidate tuple locations and `BitmapOr` takes their union. The next diagram again shows only pages: index A marks pages 0 and 3, index B marks pages 0 and 1, and page 2 remains unmarked by either. Its `BitmapAnd` result assumes that both indexes identify at least one of the same rows on page 0; sharing a page alone is insufficient for an exact row match. With a lossy entry, a shared page can remain a candidate even without a matching row, so the heap scan must recheck its tuples:

```mermaid
block-beta
  columns 5
  page["Heap page"] p0["0"] p1["1"] p2["2"] p3["3"]
  indexA["Index A"] a0["1"] a1["0"] a2["0"] a3["1"]
  indexB["Index B"] b0["1"] b1["1"] b2["0"] b3["0"]
  both["BitmapAnd"] c0["1"] c1["0"] c2["0"] c3["0"]
  style a0 fill:#c8e6c9,stroke:#388e3c
  style a3 fill:#c8e6c9,stroke:#388e3c
  style b0 fill:#c8e6c9,stroke:#388e3c
  style b1 fill:#c8e6c9,stroke:#388e3c
  style c0 fill:#c8e6c9,stroke:#388e3c
```

`BitmapAnd` and `BitmapOr` combine candidate locations, not table rows. `Recheck Cond` names the condition available for testing fetched rows when a bitmap entry or index match is lossy; its presence in a plan does not establish that any recheck occurred. [PostgreSQL bitmap index combination](https://www.postgresql.org/docs/18/indexes-bitmap-scans.html) and [index scanning](https://www.postgresql.org/docs/18/index-scanning.html).

A captured plan for `g > 95 AND id < 10000` uses `BitmapAnd` to intersect candidate row locations from **two different indexes**: `grades_pkey` for `id < 10000` and `g` for `g > 95`. The parent `Bitmap Heap Scan` then fetches rows from the combined candidates:

```text
postgres=# EXPLAIN SELECT name FROM grades WHERE g > 95 AND id < 10000;
Bitmap Heap Scan on grades  (cost=3988.96..5479.62 rows=394 width=4)
  Recheck Cond: ((id < 10000) AND (g > 95))
  ->  BitmapAnd  (cost=3988.96..3988.96 rows=394 width=0)
        ->  Bitmap Index Scan on grades_pkey  (cost=0.00..180.21 rows=9570 width=0)
              Index Cond: (id < 10000)
        ->  Bitmap Index Scan on g  (cost=0.00..3808.31 rows=205850 width=0)
              Index Cond: (g > 95)
```

Plain `EXPLAIN` shows the planned combination, not whether execution uses exact or lossy bitmap entries.

### Ordering and Sorts

With an existing `grades_g` index on `grades(g)`, the plan for `ORDER BY g` uses that index:

```txt
postgres=# EXPLAIN SELECT * FROM grades ORDER BY g;

------------------------------------------------------------------------------------
 Index Scan using grades_g on grades  (cost=0.43..595687.21 rows=13141718 width=22)
(1 row)
```

`Index Scan using grades_g on grades` reads index entries in `g` order and fetches the corresponding table rows, so this plan needs no separate `Sort` node. Its `0.43` startup cost reflects estimated work to descend the B-tree before the first index entry is available; the sequential scan above has a modeled startup cost of `0.00`. [PostgreSQL B-tree cost estimator](https://doxygen.postgresql.org/selfuncs_8c.html).

For `ORDER BY name`, this plan uses a sequential scan followed by an explicit sort:

```txt
postgres=# EXPLAIN SELECT * FROM grades ORDER BY name;
                               QUERY PLAN
-------------------------------------------------------------------------
 Sort  (cost=2312809.95..2345664.25 rows=13141718 width=22)
   Sort Key: name
   ->  Seq Scan on grades  (cost=0.00..219935.18 rows=13141718 width=22)
(3 rows)
```

Read the plan from the child node upward: `Seq Scan on grades` reads the table rows, then `Sort` orders them by `name`, as shown by `Sort Key: name`. The index on `g` does not provide `name` order, so it cannot replace this sort. Both nodes estimate the same number of output rows because sorting changes their order, not their count. Unlike the index scan above, the sort must process its input before producing the first ordered row, which contributes to its higher startup cost. [PostgreSQL `EXPLAIN` basics](https://www.postgresql.org/docs/current/using-explain.html).

### Parallel Execution

The same query produced a parallel plan on another instance:

```txt
postgres=# EXPLAIN SELECT * FROM grades ORDER BY name;
                              QUERY PLAN
----------------------------------------------------------------------
 Gather Merge  (cost=1024586.74..2205065.16 rows=10117680 width=31)
   Workers Planned: 2
   ->  Sort  (cost=1023586.72..1036233.82 rows=5058840 width=31)
         Sort Key: name
         ->  Parallel Seq Scan on grades  (cost=0.00..218201.40 rows=5058840 width=31)
(5 rows)
```

Here, `Parallel Seq Scan` divides table blocks among cooperating processes, each `Sort` orders its portion by `name`, and `Gather Merge` combines the sorted streams without losing that order. The child nodes estimate rows for a partial output; the top node estimates the combined output. `Workers Planned: 2` is a plan to request two background workers, not proof that both ran: plain `EXPLAIN` does not execute the query. Differences in table statistics and parallel-query settings can lead PostgreSQL to choose this plan instead of the serial scan and sort above. [PostgreSQL parallel plans](https://www.postgresql.org/docs/current/parallel-plans.html) and [parallel-query execution](https://www.postgresql.org/docs/current/how-parallel-query-works.html).

## Process Architecture

A PostgreSQL instance uses a process-oriented architecture. A main server process accepts incoming connections and each client connection is normally handled by its own backend process. PostgreSQL also runs background processes for responsibilities such as writing dirty buffers, checkpointing, [autovacuum](#VACUUM), and WAL-related work.

The backend processes have separate virtual address spaces, but they still need to cooperate over common database state. PostgreSQL therefore uses [shared memory](../../Operating%20Systems/03%20Memory%20Management.md#Controlled%20Sharing%20%26%20Concurrency) for structures that must be visible across the instance.

```mermaid
flowchart TB
    C1[Client 1] <-->|Queries and results| B1
    C2[Client 2] <-->|Queries and results| B2

    subgraph PG[PostgreSQL instance]
        Main[Main server process]
        B1[Backend process 1]
        B2[Backend process 2]
        BG[Background processes]
        Shared[Shared memory]

        Main -.->|Starts for a connection| B1
        Main -.->|Starts for a connection| B2
        Main -.->|Starts| BG
        B1 <--> Shared
        B2 <--> Shared
        BG <--> Shared
    end
```

Each backend has its own private address space as well as access to shared memory. Dashed arrows show process creation; solid arrows show client communication or access to shared state, not queries passing through the main server process.

This process model has an important operational consequence: opening thousands of database connections means creating thousands of backend processes and associated per-connection state. Application-side connection pools are therefore commonly used to limit the number of active PostgreSQL sessions.

## Shared Buffers

Database tables and indexes ultimately live in persistent files, but executing queries directly against storage for every access would be far too slow. PostgreSQL maintains a shared cache called **shared buffers**, accessible by its backend processes.

When a backend needs a database page, PostgreSQL checks whether that page is already present in shared buffers. If it is, the backend can work with the in-memory copy. Otherwise PostgreSQL reads the page from the underlying file into a shared buffer. Modified pages become **dirty** and are eventually written back to persistent storage.

Shared buffers are therefore part of PostgreSQL's own buffer-management layer. The operating system may additionally cache the same underlying files in its filesystem page cache, so PostgreSQL intentionally has both database-managed caching and OS-managed caching in the I/O path.

> [!info] Shared memory versus memory-mapped data files
> PostgreSQL supports allocating shared buffers through anonymous `mmap`: this creates shared memory, not a direct mapping of table or index files.
>
> Directly modifying database files through a writable shared mapping would let the OS write dirty pages back independently. PostgreSQL instead controls when modified pages leave shared buffers so it can enforce **write-ahead ordering**: the corresponding WAL records must be durable before the data page reaches persistent storage. Simply replacing shared buffers with file mappings would lose that control and require additional coordination. This is a constraint on a direct replacement, not a claim that databases cannot use `mmap`.

## Asynchronous Data-File I/O

When PostgreSQL needs a page absent from shared buffers, it reads the relevant relation file. Before PostgreSQL 18, a backend could have to wait for one uncached read before initiating later reads. Kernel read-ahead mitigates sequential access, but it does not know the query plan or every page the database will need.

PostgreSQL 18 introduced an asynchronous I/O (AIO) subsystem that lets backends issue multiple eligible page reads before consuming their results. Sequential scans, bitmap heap scans, and [VACUUM](#VACUUM) can use knowledge of upcoming pages to keep reads in flight instead of serializing the latency of each read. A backend still waits when execution needs a page whose read has not completed; AIO enables overlap rather than eliminating storage waits.

### I/O Execution Methods

The `io_method` setting selects how PostgreSQL executes asynchronous-eligible operations:

- **`worker` (PostgreSQL 18 default):** The issuing backend places I/O requests in a shared queue. Dedicated PostgreSQL I/O worker processes perform ordinary blocking file operations and process their completion state. The backend can continue other work or wait for a requested result. `io_workers` controls the shared worker pool (three processes by default), so worker availability bounds how many delegated blocking operations can execute concurrently.
- **`io_uring`:** On supported Linux installations built with `liburing`, the backend submits operations through kernel submission/completion rings and later processes their results. PostgreSQL 18 uses an `io_uring` instance per backend rather than delegating each read to a PostgreSQL I/O worker. This avoids the extra PostgreSQL process handoff, although the kernel may use its own workers for operations that cannot proceed directly.
- **`sync`:** Asynchronous-eligible operations are executed synchronously instead. This provides a comparison and fallback path, but does not offer the same read overlap to the issuing backend.

Both `worker` and `io_uring` expose **completion-oriented behavior to the query backend**: it submits a particular read and later learns its result. With `worker`, another PostgreSQL process uses a blocking system call to carry out that read; with `io_uring`, the kernel-facing interface accepts the submitted operation directly. Asynchronous application behavior therefore does not require every underlying system call to be non-blocking.

The execution method determines how reads are carried out, while separate settings control how aggressively PostgreSQL initiates them:

- **`effective_io_concurrency` and `maintenance_io_concurrency`:** Influence the number of concurrent I/O requests initiated for query and maintenance workloads, respectively.
- **`io_max_concurrency`:** Limits the outstanding I/O operations allowed for an individual PostgreSQL process.
- **`io_workers`:** Sets the size of the shared PostgreSQL I/O worker pool; it has no effect with `io_uring`.
- **`io_method`:** Requires a server restart when changed.

Selecting `io_method` changes eligible data-file I/O execution, not client-socket handling, shared-buffer caching, or the WAL synchronization rules that establish transaction durability.

### Concurrency and Trade-offs

`io_uring` avoids the PostgreSQL worker handoff, but fewer handoffs do not guarantee a faster query. The methods also differ in where read-related CPU work happens and how many processes share that work.

- **CPU-work distribution:** With `worker`, I/O workers perform read-related work, including checksum verification, outside the issuing backend. With `io_uring`, the backend handles completion-side work itself. A small number of backends performing large scans can therefore benefit from workers when that CPU work limits throughput, even if `io_uring` is available.
- **Handoff overhead:** Workers require queue coordination, wakeups, and completion notifications between PostgreSQL processes. `io_uring` avoids that extra PostgreSQL process handoff, reducing scheduling and coordination overhead when those costs are significant, including workloads with many outstanding reads.
- **Shared capacity versus backend concurrency:** All issuing backends compete for the same PostgreSQL I/O worker pool. Too few workers create a bottleneck; increasing their number consumes additional process and CPU resources. With many active backends, `io_uring` already distributes completion-side CPU work across those backends without a shared PostgreSQL worker-pool limit. Storage and per-process concurrency limits still apply.

The benefit of either method depends on cache hits, storage latency, available device parallelism, worker capacity, and submission overhead. A completed file read does not imply physical disk access: the operating system's page cache may have satisfied it. Consequently, compare the methods under representative cache conditions and backend concurrency rather than treating `io_uring` availability as evidence of superior performance.

> [!example] Scan performance in PostgreSQL 18
> Tomas Vondra's benchmarks found `worker` faster than `io_uring` for sequential scans and, with enough workers, bitmap scans. He identifies distributing read-related CPU costs as a likely explanation, not a universal performance guarantee. [Benchmark and trade-off analysis](https://vondra.me/posts/tuning-aio-in-postgresql-18/)

## Storage Files and OS I/O

PostgreSQL ultimately stores relations and other persistent structures in ordinary filesystem files managed by the database server.

### Creating Relation Files

Creating a new database object can eventually require PostgreSQL to create a corresponding filesystem object. PostgreSQL must distinguish between successfully creating the intended new file and accidentally opening an unrelated file that already occupies the pathname. On POSIX-like systems, creation paths can therefore use the same [`O_CREAT | O_EXCL`](../../Operating%20Systems/06%20Storage%20Management.md#File%20Creation) pattern described by `open()`.

## Heap Page Layout and HOT Updates

PostgreSQL's heap table access method stores physical row versions (tuples) in pages with these regions:

- **Page header:** A 24-byte `PageHeaderData` structure holds page metadata, including free-space boundaries.
- **Line pointers:** Each 4-byte `ItemIdData` entry records a tuple's byte offset, length, and state bits.
- **Free space:** The gap between the line-pointer array and tuple data. New pointers grow into it from the front; tuple storage grows backward from the other end.
- **Tuple items:** The physical row versions, whose lengths vary with their contents.
- **Special space:** Access-method-specific data; empty on ordinary heap pages. Index methods use it differently—for example, B-tree pages store sibling links here. It is not restricted to B-tree leaf pages.

A [tuple identifier](../Internals/01%20Tables%2C%20Pages%2C%20and%20Indexes.md#Logical%20keys%20and%20internal%20row%20identifiers), or **CTID**, combines the page number with a line-pointer index, not a tuple byte offset. Compaction moves tuple bytes and adjusts their line pointers without changing those indexes. This stability lasts until the pointer is freed; it does not make CTID a permanent logical row identity. [PostgreSQL page layout](https://www.postgresql.org/docs/current/storage-page-layout.html).

An update creates another heap tuple version with a new tuple identifier. Ordinarily, PostgreSQL adds entries to the table's indexes that locate this new version—even where the indexed values did not change—because an index entry identifies a physical tuple version, not a logical row. Entries for old versions remain until those versions can be reclaimed. **Heap-only tuples (HOT)** avoid this index maintenance.

The optimization applies when both conditions hold:

- The new version fits on the old version's page.
- The update leaves columns referenced by non-summarizing indexes unchanged. Summarizing indexes, such as BRIN, are exempt, but their summaries may still require updates.

HOT links versions into a same-page chain while index entries retain the original version's line-pointer reference. It does **not** simply overwrite that pointer to address the new tuple at update time: older versions remain available to transactions that still need them.

During pruning, PostgreSQL removes versions no transaction needs. After removing the original tuple's data, its line pointer becomes a redirect to the oldest version that might still be visible. Obsolete intermediate versions and their pointers are reclaimed. This preserves index access while shortening the chain, without requiring a separate [VACUUM](#VACUUM) for every such cleanup. [PostgreSQL HOT documentation](https://www.postgresql.org/docs/current/storage-hot.html).

## Transactions and Concurrency

PostgreSQL is designed for many clients to read and modify the same logical data concurrently. It uses **[Multi-Version Concurrency Control (MVCC)](../Fundamentals/02%20Transaction%20Isolation.md#Multi-Version%20Concurrency%20Control)** so readers can often observe a consistent snapshot without blocking writers that are creating newer row versions.

Updates and deletes leave old row versions behind to preserve snapshot visibility; [VACUUM](#VACUUM) reclaims their storage once no transaction needs them.

Transactions still require coordination. Locks protect operations and structures where concurrent access cannot safely proceed independently, while [transaction isolation](../Fundamentals/02%20Transaction%20Isolation.md#Isolation%20Levels) determines which changes a transaction is allowed to observe. MVCC reduces contention; it does not eliminate synchronization.

### Snapshot Visibility Across Statements

For ordinary table reads, PostgreSQL 18 distinguishes these snapshot lifetimes:

- **Read Committed:** Each statement obtains a new snapshot. This is the default isolation level.
- **Repeatable Read:** The first query or data-modification statement establishes the transaction's snapshot; `BEGIN` alone does not establish it. Later reads retain that view of other transactions' changes.
- **Serializable:** Uses the same snapshot lifetime as Repeatable Read, with additional read/write dependency checks through **Serializable Snapshot Isolation (SSI)**.

All three levels expose the transaction's own earlier writes. PostgreSQL maps Read Uncommitted to Read Committed; its Repeatable Read also prevents phantom reads, but not all serialization anomalies. These are PostgreSQL-specific semantics, not guarantees inferred solely from isolation-level names. [PostgreSQL 18 isolation documentation](https://www.postgresql.org/docs/18/transaction-iso.html).

> [!example] Another transaction commits between two reads
> Use a disposable database and two independent connections, A and B, with no other writers. Run setup once outside an explicit transaction. Do not use a temporary table: both sessions need the same data.
>
> ```sql
> CREATE TABLE isolation_on_call (
>     doctor text PRIMARY KEY,
>     on_call boolean NOT NULL
> );
> INSERT INTO isolation_on_call VALUES ('Alice', true), ('Bob', true);
> ```
>
> Execute each numbered row in order; a dash means that session performs no operation. Leave A open while B updates and commits:
>
> | Step | Session A | Session B |
> | --- | --- | --- |
> | 1 | `BEGIN ISOLATION LEVEL READ COMMITTED;` | — |
> | 2 | `SELECT on_call FROM isolation_on_call WHERE doctor = 'Bob';` → `true` | — |
> | 3 | — | `BEGIN;` |
> | 4 | — | `UPDATE isolation_on_call SET on_call = false WHERE doctor = 'Bob';` |
> | 5 | — | `COMMIT;` |
> | 6 | Repeat A's `SELECT` → `false` | — |
> | 7 | `COMMIT;` | — |
>
> A's ordinary `SELECT` does not hold a row lock that blocks B's update. At Read Committed, A's second statement sees B's committed version. Reset both rows with `UPDATE isolation_on_call SET on_call = true;` after both transactions end, then repeat with A using `BEGIN ISOLATION LEVEL REPEATABLE READ;`: both reads return `true` because A retains its first snapshot.

### Write Skew and Serializable Retries

PostgreSQL Repeatable Read provides a stable snapshot but still permits [write skew](../Fundamentals/02%20Transaction%20Isolation.md#Write%20Skew); its direct write-conflict protection does not enforce every cross-row rule.

Serializable Snapshot Isolation (SSI) detects incompatible read/write dependencies and rejects a transaction rather than allowing a nonserializable outcome. [PostgreSQL Serializable isolation](https://www.postgresql.org/docs/18/transaction-iso.html#XACT-SERIALIZABLE).

- **Blocking behavior:** Dependency tracking does not itself block the other writer, although ordinary lock conflicts still cause waits.
- **Failure timing and victim:** A serialization failure can occur during a statement or at commit; applications must not depend on a particular victim or failure point.

A serialization failure invalidates the transaction's attempt, so recovery must repeat its decisions, not just its final write. On SQLSTATE `40001` (`serialization_failure`):

1. Roll back any still-open failed transaction.
2. Retry the **whole transaction**, including its reads and application decisions—not just the failed update or commit.

Repeatable Read also requires whole-transaction retries when concurrent updates cause serialization failures. A retry is not guaranteed to succeed under continued contention. [PostgreSQL serialization failure handling](https://www.postgresql.org/docs/18/mvcc-serialization-failure-handling.html).

> [!example] Concurrent departures violate the on-call rule
> Using the `isolation_on_call` table from the preceding example, reset both rows to `true` outside any explicit transaction. The intended rule is that **at least one doctor must remain on call**; each session allows its doctor to leave only if its on-call count exceeds one:
>
> | Step | Session A | Session B |
> | --- | --- | --- |
> | 1 | `BEGIN ISOLATION LEVEL REPEATABLE READ;` | — |
> | 2 | — | `BEGIN ISOLATION LEVEL REPEATABLE READ;` |
> | 3 | `SELECT count(*) FROM isolation_on_call WHERE on_call;` → `2` | — |
> | 4 | — | `SELECT count(*) FROM isolation_on_call WHERE on_call;` → `2` |
> | 5 | `UPDATE isolation_on_call SET on_call = false WHERE doctor = 'Alice';` | — |
> | 6 | — | `UPDATE isolation_on_call SET on_call = false WHERE doctor = 'Bob';` |
> | 7 | `COMMIT;` | — |
> | 8 | — | `COMMIT;` |
>
> Both counts return `2`, so the application issues both updates; the updates themselves do not enforce the rule. Repeatable Read allows both commits, leaving zero doctors on call. Read Committed also permits this schedule because both decisions occur before either commit.
>
> Reset again and repeat with **both** sessions using `BEGIN ISOLATION LEVEL SERIALIZABLE;`. SSI rejects a transaction instead of allowing both departures to commit. After the surviving transaction commits, a fresh count is `1`, so the retry must leave the remaining doctor on call.

## Durability and WAL

PostgreSQL uses [Write-Ahead Logging (WAL)](../Fundamentals/00%20Overview.md#Write-Ahead%20Logging%20%28WAL%29) for durability. Before a change to a database page is considered safely committed, the information required to reproduce that change is written to the WAL and persisted according to the configured durability guarantees.

This avoids having to synchronously flush every modified table or index page at commit time. Dirty data pages can be written later because, after a crash, PostgreSQL can replay WAL records to reconstruct changes that had been committed but had not yet reached their final data files.

### WAL Synchronization Method

PostgreSQL still needs an operating-system mechanism for forcing WAL records from volatile caches to durable storage. The `wal_sync_method` setting chooses which synchronization primitive PostgreSQL uses for that operation; it changes the mechanism used to establish the durability boundary, not the underlying WAL algorithm.

Possible methods include:

- **`open_datasync`:** opens WAL files with [`O_DSYNC`](../../Operating%20Systems/06%20Storage%20Management.md#Synchronous%20Completion), so writes complete with data-synchronization semantics.
- **`fdatasync`:** performs ordinary writes and calls [`fdatasync()`](../../Operating%20Systems/06%20Storage%20Management.md#Writes,%20Writeback,%20and%20Durability) when WAL must be forced durable.
- **`fsync`:** performs ordinary writes and calls [`fsync()`](../../Operating%20Systems/06%20Storage%20Management.md#Writes,%20Writeback,%20and%20Durability) when WAL must be forced durable.
- **`fsync_writethrough`:** uses a platform-specific `fsync()` variant that additionally requests write-through of a device write cache when the platform provides such a mechanism.
- **`open_sync`:** opens WAL files with [`O_SYNC`](../../Operating%20Systems/06%20Storage%20Management.md#Synchronous%20Completion), making each WAL write use synchronized file-I/O semantics.

Not every method is available on every operating system. If PostgreSQL's `fsync` configuration is disabled, `wal_sync_method` is irrelevant because PostgreSQL is no longer requiring WAL updates to be forced to durable storage through these mechanisms.

The synchronization primitive is also separate from **how often** PostgreSQL needs to establish a durability boundary. Multiple transactions that commit close together can participate in **group commit**, allowing one WAL flush to make several transactions durable. This preserves the WAL ordering guarantee while reducing the cost that would result from performing an independent storage synchronization for every transaction.
