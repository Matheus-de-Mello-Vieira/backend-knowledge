# Tables, Pages, and Indexes

A [SQL table](../Fundamentals/04%20Relational%20Model.md#Relations%20and%20SQL%20Tables) organizes logical data into columns and rows. Its storage layout determines how those values are arranged in pages and reached through indexes; the logical table does not prescribe that layout.

## Logical keys and internal row identifiers

A **primary key** identifies a logical row through values defined in the table schema. An internal row identifier is maintained by the database to locate stored rows or row versions; its form and relationship to the primary key depend on the storage implementation.

- **InnoDB:** A hidden, system-generated row ID is used only when no suitable declared key is available for its clustered index; it is not the same as a declared primary key.
- **PostgreSQL:** The system column `ctid` contains a tuple identifier (`tid`) that locates a particular row version within its table. It changes when the row is updated or moved, so it is not a stable substitute for a primary key.

## Pages

A **page** is a fixed-size unit of storage and buffer management in a page-oriented database engine. Row-store data pages hold row records; index pages hold index entries. The page is an engine-level unit, not the same thing as a storage device's logical block, and one page request does not necessarily correspond to one physical I/O.

Not every database format uses pages as its universal read unit. Column-oriented formats group values by column in pages, compressed blocks, or larger segments, depending on the implementation. Even when a format defines pages, a scan may read several together. The amount transferred depends on the format and access path rather than on the word *page* alone.

Page size depends on the engine and its configuration. PostgreSQL commonly uses 8 KiB pages, while InnoDB defaults to 16 KiB pages.

> [!example]
> In a page-oriented row store, if each data page held exactly three rows, 1,001 rows would require at least $\lceil 1001 / 3 \rceil = 334$ data pages. Actual capacity also depends on row sizes and page overhead.

### Page-size trade-offs

Page size determines how much data travels and occupies cache space together. Its benefit depends on how much of that data the workload uses:

- **Smaller pages:** Bring fewer unrelated bytes into memory for scattered, small accesses, but repeat fixed per-page metadata across more pages for the same amount of data.
- **Larger pages:** Amortize fixed page-header overhead across more data and bring more nearby records together. When those records are not needed, the extra bytes consume transfer bandwidth and cache capacity without helping the request.

Neither size is universally faster: access locality, cache contents, storage behavior, and the engine's supported page sizes constrain the trade-off. Larger pages offer more capacity, but do not prevent index-page splits; whether an insertion fits still depends on entry sizes and the space remaining in its target page.

### Page addresses within files

One storage model lays out fixed-size pages consecutively from the start of a file. In that model, the byte offset of a page is $p \times S$, where $p$ is its zero-based page index within that file and $S$ is the page size in bytes. Reading one page requests $S$ bytes at that offset.

> [!example]
> With $S = 8192$ bytes, page $p = 2$ starts at byte offset $2 \times 8192 = 16384$. Pages 2 through 9 span eight pages, or $8 \times 8192 = 65536$ bytes.

The page index alone does not identify the containing file or segment. The engine must resolve that identity before applying the file-local offset; a table need not correspond to one file. A file-relative address is also distinct from the physical storage location: consecutive byte offsets do not guarantee adjacent physical disk blocks. Other storage layouts require their own mapping rather than this simple multiplication.

## Heap-organized tables

A **heap-organized table** stores rows in available space across its data pages rather than maintaining them in an index's key order. Inserts use available locations; updates and deletes can make locations reusable, subject to the engine's cleanup rules. Rows with nearby key values can therefore occupy different pages. Because indexes are separate structures that locate rows in those pages, following nearby index entries can require scattered heap-page reads rather than sequential reads.

This database-storage meaning of *heap* is distinct from a process's [memory heap](../../Operating%20Systems/02%20The%20Anatomy%20of%20a%20Process.md#The%20Heap), which serves dynamic allocations. It also does not mean a heap priority-queue data structure.

## Indexes

An **index** organizes selected values from one or more table columns into a search structure. On a heap-organized table, a row-locating index is separate from the heap: its entries associate indexed values with locators for matching rows. Those locators narrow the heap pages to inspect instead of requiring a scan of every page. Other index types summarize page ranges rather than locating individual rows.

An index lookup reads index pages to find matching entries, then fetches table data when the index does not contain everything the query needs. Some queries can be answered from the index without a table-data fetch. Index pages can themselves require I/O when absent from memory; a smaller index is more likely to fit in cache and avoid those reads. B-tree-family structures are a common way to organize index entries.

### Index search keys and primary keys

An **index search key** is the column or combination of columns used to search an index. A **secondary index key** provides a search path by values other than the primary key. It need not be unique; a unique secondary index enforces uniqueness separately. Here, *secondary key* describes an index's search values, not a second primary-key constraint.

These key roles do not determine storage layout. A primary-key index is not necessarily clustered, and a clustered index does not necessarily use the declared primary key. The physical distinction is whether the index's leaf pages contain the table rows or entries that locate rows stored elsewhere.

### Clustered and secondary indexes

A **clustered index** stores table rows in its leaf pages in index-key order instead of keeping them in a separate heap. Some systems call a table stored this way an **index-organized table**. A **secondary index** is separate from the table data: its entries pair search-key values with a way to locate matching rows. The same table therefore has only one clustered row order but can have indexes on other search keys.

For a B-tree-based clustered index, keeping rows in key order does not require every page to be full. When a row is inserted, the engine finds the leaf page for its key and places the row among that page's entries if space remains. If it does not fit, the engine splits or otherwise reorganizes pages and updates the index structure so the key ranges remain ordered.

Free space arises in different ways:

- **Page splits:** A split can leave the resulting pages partly filled.
- **Reserved space:** Some engines leave room in pages in advance to accommodate later inserts.

Neither means that pages are always half-empty. Free space reduces some immediate splits but uses more pages for the same rows, increasing storage and potentially the pages a range scan must read. Key order describes the index's traversal order, not a guarantee that neighboring leaf pages occupy adjacent physical disk blocks.

- **InnoDB:** Every table has a clustered index. It uses a declared primary key when one exists, otherwise the first suitable `UNIQUE` index with only `NOT NULL` columns, and otherwise a hidden generated row ID. Each secondary-index entry carries the clustered key value—normally the primary-key value—which InnoDB uses to find the row in the clustered index.
- **PostgreSQL:** Table rows reside in a heap, and all indexes are secondary, including the primary-key index. Row-locating indexes use tuple identifiers (`tid`) to identify heap locations; the system column `ctid` exposes the location of a row version. Not every index stores a locator for each row: a BRIN index, for example, summarizes ranges of heap pages.

## Page reads and I/O

For page-oriented row storage, fetching a row not already in memory requires its containing page rather than an isolated row. Other rows on that page arrive with the same read, and a request may span multiple pages. The number of rows returned therefore does not directly determine the number of page reads.

A request for a database page is not necessarily a physical storage read: the page may already be in a database buffer pool, or a file read may be satisfied by the operating system's [page cache](../../Operating%20Systems/06%20Storage%20Management.md#Caching). Avoiding physical reads depends on cache hits as well as on how many pages the query needs.

## Row-based vs column based databases

**Row-oriented** and **column-oriented** storage group the same logical table values differently. A row layout groups a record's attributes; a column layout groups one attribute's values across rows. This determines which values a read brings together and which values must be gathered separately.

### Physical layout and row reconstruction

- **Row-oriented storage:** A [data page](#Pages) holds records from multiple rows. Reading it brings those records' stored attributes together, including attributes the query does not use. Large values may be stored separately, depending on the engine.
- **Column-oriented storage:** A page or compressed block holds values of one column across many rows. Accessing another column means accessing its own storage rather than finding it beside the first value.

Column storage preserves the association between a row's separated values through corresponding positions or identifiers. Gathering the requested values for a row is **row reconstruction**.

### Query shape and the layout trade-off

A **projection** is the set of columns a query returns. Filters, joins, and aggregates can require additional columns that do not appear in that result.

- **Few columns across many rows:** Column storage reads the relevant columns without carrying unrelated attributes through the scan. A row-store table scan reads pages containing those attributes too, though it need not interpret or return them. This makes column layout favorable for narrow scans because more relevant values fit in each page or block and fewer bytes need to be read under comparable storage and cache conditions.
- **Many columns from a few rows:** Once a row is located, row storage has its stored attributes together. Column storage accesses the requested values across multiple column structures and reconstructs the row. The amount of work varies with the requested columns and rows, physical organization, and caching.

### Scans and search access paths

Layout controls grouping; an **access path** controls how matching values are found. Without a usable index, ordering, or pruning mechanism, either layout scans candidate data to evaluate a predicate.

- **Row-store scan:** Examines row-storage pages. Each matching record already carries its stored attributes, while the pages also bring along attributes the query does not need.
- **Column-store scan:** Examines predicate columns to identify matching row positions or identifiers, then accesses other requested columns for those matches. It avoids unrelated columns even when it must scan the predicate column.

Indexes and pruning structures reduce the data examined in either layout. A row-store query satisfied entirely from an index avoids table-record reads; a column store may likewise use a search or pruning structure instead of scanning all column data. The chosen access path, storage organization, and cache contents determine actual reads.

### Compression

Values grouped by column share a type and may repeat or resemble one another, giving column-specific encodings useful input. Compression reduces stored and transferred bytes but adds encoding or decoding work; supported operations in some column engines run on encoded values. Its benefit depends on the values, their order, and the encoding. Row storage also supports compression, but grouping by column creates different encoding opportunities.

### Inserts, updates, and deletes

A logical row change must remain consistent across its stored values. Row layout groups those values in a record; column layout represents them across the affected column structures. The engine's versioning, compression, and write path determine when physical maintenance occurs.

- **Inserts:** Row storage adds a record. Column storage represents the new values in the affected columns. Batching spreads that work across rows, and a write-optimized area can defer integration into compressed column structures.
- **Updates:** Maintenance depends on the changed attributes and their storage representation. Compressed or sorted column data may need additional work; an engine can instead manage versions or defer reorganization. Row storage does not require updating the old record in place either.
- **Deletes:** The row's values become invisible together. A column store can mark a row deleted and reclaim its column values during later cleanup, separating immediate delete work from reclamation work.

### Workload tendencies

The grouping trade-off explains common workload fits:

- **Online transaction processing (OLTP):** Short transactions that locate a few rows and read or change several attributes benefit from row layout.
- **Online analytical processing (OLAP):** Scans, filters, and aggregations over many rows but a subset of columns benefit from selective column access and compression.

These are workload tendencies, not restrictions: row stores execute analytics, and column stores support transactions. Access paths, columns touched, selectivity, and change patterns matter alongside layout.

> [!example] Query shape and storage layout
> For `SELECT first_name FROM emp WHERE ssn = 666`, a row-store table scan reads row pages. A column-store scan reads `ssn` and gathers `first_name` for matching row positions, leaving unrelated columns aside.
>
> `SELECT * FROM emp WHERE id = 1` requires both layouts to find a match. The row store then has its stored attributes together; the column store gathers them from separate representations.
>
> `SELECT SUM(salary) FROM emp` processes the applicable salary values. Column storage reads the salary representation alone, while a row-store table scan reads pages containing other attributes as well.
>
> A suitable index changes the access path, including by supplying required values without fetching table records when an index-only plan is available.

### Mixed row and column storage

Storage layout is a physical choice, not a property that every table in a database must share. Mixed workloads motivate several designs. If an engine supports choosing a layout per table, the same database can contain row-oriented and column-oriented tables. Other mixed designs combine layouts without making that per-table choice:

- **Different layouts for different tables:** Each table has one primary layout, chosen for the queries and changes expected on that table.
- **Multiple representations of the same data:** A system maintains row- and column-oriented representations so different queries can use different read paths. Keeping them synchronized adds storage and write-maintenance work; the visibility of recent changes depends on the engine's design.
- **Hybrid storage within a table:** An engine combines layouts or separates write-optimized storage from read-optimized column storage. Its write path determines when and how data moves between representations.

These designs preserve the logical meaning of a row but change how the engine retrieves and maintains its values. Their consequences differ:

- **Per-table access costs:** A query may scan a narrow column representation in one table and fetch complete records from a row representation in another. Filters, indexes, pruning, and cache state still determine the work performed.
- **Cross-table operations:** Where the engine supports joins across differently stored tables, their cost depends on the chosen plan and on how each input is read. The presence of both layouts alone does not make a mixed query fast.
- **Write and consistency costs:** Updating a table stored once follows that table's write path. Maintaining two representations of the same data adds coordination; transaction and freshness guarantees depend on the engine rather than following from the layouts alone.
