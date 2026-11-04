# Tables, Pages, and Indexes

## Relational terminology

In the relational model, a **relation** is a set of **tuples** described by a **relation schema**. The schema defines the attributes; each tuple assigns a value to every attribute.

- **Attribute:** A named component of the schema, corresponds to a table column. Its **domain** specifies the values it can take.
- **Tuple:** One combination of attribute values in the relation, corresponds to a table row.
- **Relation value:** The set of tuples that belong to the relation at a particular time. As a set, it has no duplicate tuples or inherent row order.

## Relation and table

A **table** is the SQL database object that organizes data into columns and rows. It resembles a relation, but the terms are not interchangeable: a relation is a mathematical set of tuples, whereas a SQL table permits duplicate rows unless constraints prevent them. SQL also supports `NULL` in nullable columns, while a tuple in the classical relational model assigns a value from each attribute's domain. Neither a relation nor a SQL table guarantees an order for its tuples or rows; a query needs `ORDER BY` to specify result order.

## Logical keys and internal row identifiers

A **primary key** identifies a logical row through values defined in the table schema. An internal row identifier is maintained by the database to locate stored rows or row versions; its form and relationship to the primary key depend on the storage implementation.

- **InnoDB:** A hidden, system-generated row ID is used only when no suitable declared key is available for its clustered index; it is not the same as a declared primary key.
- **PostgreSQL:** The system column `ctid` contains a tuple identifier (`tid`) that locates a particular row version within its table. It changes when the row is updated or moved, so it is not a stable substitute for a primary key.

## Pages

A **page** is a fixed-size unit of database storage and buffer management. In a row store, a data page holds row records; a column store groups values by column, so its pages need not contain complete rows.

Page size depends on the engine and its configuration. PostgreSQL commonly uses 8 KiB pages, while InnoDB defaults to 16 KiB pages.

> [!example]
> If each page held exactly three rows, 1,001 rows would require at least $\lceil 1001 / 3 \rceil = 334$ pages. Actual capacity also depends on row sizes and page overhead.

## Heap-organized tables

A **heap-organized table** stores rows in available space across its data pages rather than maintaining them in an index's key order. Inserts use available locations; updates and deletes can make locations reusable, subject to the engine's cleanup rules. Rows with nearby key values can therefore occupy different pages. Because indexes are separate structures that locate rows in those pages, following nearby index entries can require scattered heap-page reads rather than sequential reads.

This database-storage meaning of *heap* is distinct from a process's [memory heap](../../Operating%20Systems/02%20The%20Anatomy%20of%20a%20Process.md#The%20Heap), which serves dynamic allocations. It also does not mean a heap priority-queue data structure.

## Indexes

An **index** organizes selected values from one or more table columns into a search structure. On a heap-organized table, a row-locating index is separate from the heap: its entries associate indexed values with locators for matching rows. Those locators narrow the heap pages to inspect instead of requiring a scan of every page. Other index types summarize page ranges rather than locating individual rows.

An index lookup reads index pages to find matching entries, then fetches table data when the index does not contain everything the query needs. Some queries can be answered from the index without a table-data fetch. Index pages can themselves require I/O when absent from memory; a smaller index is more likely to fit in cache and avoid those reads. B-tree-family structures are a common way to organize index entries.

### Clustered and secondary indexes

A **clustered index** stores the table rows in its leaf pages according to the index key, instead of keeping the table in a separate heap. Some systems call a table stored this way an **index-organized table**. A **secondary index** is separate from the table data and uses a locator to reach a matching row. A primary key defines logical identity; whether its index is clustered depends on the database engine.

- **InnoDB:** Every table has a clustered index. It uses a declared primary key when one exists, otherwise the first suitable `UNIQUE` index with only `NOT NULL` columns, and otherwise a hidden generated row ID. Each secondary-index entry carries the clustered key value—normally the primary-key value—which InnoDB uses to find the row in the clustered index.
- **PostgreSQL:** Table rows reside in a heap, and all indexes are secondary, including the primary-key index. Row-locating indexes use tuple identifiers (`tid`) to identify heap locations; the system column `ctid` exposes the location of a row version. Not every index stores a locator for each row: a BRIN index, for example, summarizes ranges of heap pages.

## Page reads and I/O

For page-oriented row storage, fetching a row not already in memory requires its containing page rather than an isolated row. Other rows on that page arrive with the same read, and a request may span multiple pages. The number of rows returned therefore does not directly determine the number of page reads.

A request for a database page is not necessarily a physical storage read: the page may already be in a database buffer pool, or a file read may be satisfied by the operating system's [page cache](../../Operating%20Systems/06%20Storage%20Management.md#Caching). Avoiding physical reads depends on cache hits as well as on how many pages the query needs.
