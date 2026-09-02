# SQLite

SQLite is a relational SQL database engine designed to run **inside the application process** rather than as a separate database server. The application links the SQLite library, calls its API directly, and usually stores the entire database in one ordinary file.

## Main Point

SQLite is useful when an application needs structured, transactional local persistence but does not need a separately operated database server. It provides tables, indexes, SQL queries, constraints, and ACID transactions while remaining essentially a library plus a database file.

This makes SQLite well suited to mobile applications, desktop software, local caches, device software, command-line tools, and application-specific file formats. Instead of inventing a binary or JSON file format and writing custom indexing and transaction logic, an application can use SQLite as its persistent storage layer.

Unlike [PostgreSQL](PostgreSQL.md#Main%20Point), there is no dedicated database server process accepting requests from many remote clients. SQLite executes in the same address space and usually the same thread that called it, so database operations are ordinary library calls rather than network or IPC requests.

## Execution Model

SQLite treats SQL almost like a small programming language. It parses and compiles an SQL statement into SQLite bytecode, then executes that bytecode using its internal virtual machine. The engine itself performs query planning, index selection, transaction handling, and file access inside the caller's process.

This execution model removes a large amount of operational machinery: there is no database daemon to deploy, no server port, and no connection pool between the application and the engine. The trade-off is that SQLite is primarily designed for local access rather than acting as a centralized database service for many independent machines.

## Storage Model

A normal SQLite database is stored in a single portable database file containing tables, indexes, schema information, and other persistent structures. Internally, the file is divided into fixed-size **pages**, which are the units SQLite reads, caches, modifies, and writes.

Tables and indexes are organized using B-trees. A query therefore does not generally scan arbitrary bytes in the file; the database engine navigates these tree structures to find the pages containing the requested rows or index entries.

SQLite also maintains an internal **page cache**. Pages read from the database file can remain in memory so repeated accesses do not require another storage read. This is an application-level cache managed by SQLite, distinct from the operating system's filesystem cache.

## Transactions and Concurrency

SQLite provides ACID transactions even though the database is an ordinary file. Depending on its journaling mode, it protects atomicity using mechanisms such as a rollback journal or a **Write-Ahead Log (WAL)**.

Concurrency reflects SQLite's embedded, single-file design. Multiple readers can operate concurrently, but writes ultimately need serialization because they modify the same database file. WAL mode improves reader/writer concurrency by allowing readers to continue using the stable database while a writer appends new changes to the WAL, but SQLite still has a single-writer model.

This is an important distinction from a server database such as PostgreSQL. SQLite is optimized for avoiding the cost and complexity of a separate server, not for scaling large numbers of independent writers across a network.
