# Databases

A database is software that gives applications a structured way to persist, retrieve, and update data while handling concerns such as indexing, transactions, concurrency, and recovery. Different database engines solve different deployment and access problems, so their internal architecture often follows from the role they are designed to play.

## Database Models in These Notes

| Database | Main role | Execution model | Data model | Architectural emphasis |
| --- | --- | --- | --- | --- |
| [PostgreSQL](PostgreSQL.md#Main%20Point) | General-purpose transactional database server | Separate client/server processes | Relational / SQL | Rich queries, many concurrent clients, transactions, durability |
| [SQLite](SQLite.md#Main%20Point) | Structured persistent storage embedded inside an application | Library in the application's process | Relational / SQL | Zero administration, single-file storage, local application data |
| [LMDB](LMDB.md#Main%20Point) | Very small embedded persistent ordered map | Library in the application's process | Ordered key-value | Extremely cheap reads, memory-mapped storage, simple concurrency model |

The most important distinction is not SQL versus key-value by itself. PostgreSQL is a **database server** that owns the database on behalf of many clients, while SQLite and LMDB are **embedded databases** whose engine executes inside the application process. SQLite then provides a full relational SQL interface, whereas LMDB deliberately exposes a much smaller ordered key-value abstraction.

These differences affect almost every internal design choice: whether communication requires [IPC](../Operating%20Systems/08%20Inter-Process%20Communication.md) or networking, where caches live, how concurrency is coordinated, how files are accessed, and how much responsibility is delegated to the operating system.

## Buffer Pools and Storage Caching

Database engines commonly organize persistent data into fixed-size **database pages**. Rather than reading a page from storage every time a query needs it, an engine can keep useful pages in an in-memory **buffer pool** or page cache that it manages itself.

A database-managed cache can use information that the operating system does not have. The engine knows which pages belong to indexes or tables, which pages are frequently reused, which pages are dirty, and which access patterns are likely to follow from query execution. It can therefore make cache-retention, eviction, prefetching, and writeback decisions according to database semantics rather than only generic file-access behavior.

The operating system may still cache the same underlying files in its filesystem [page cache](../Operating%20Systems/06%20Storage%20Management.md#Caching). With normal buffered I/O, the path can therefore contain two caching layers: `Storage → OS Page Cache → Database Buffer Pool`.

This is sometimes called **double caching**. It can be useful when the two layers complement each other, but it can also consume RAM twice for the same underlying data and give the kernel and database independent replacement policies.

Database engines therefore make different choices about who should own caching. Some deliberately cooperate with the operating system's page cache. Others use [Direct I/O (`O_DIRECT`)](../Operating%20Systems/06%20Storage%20Management.md#Direct%20I/O%20(`O_DIRECT`)) so database-file data normally bypasses that cache, allowing the engine's own buffer pool to be the primary long-lived cache. Memory-mapped designs can take another approach by mapping file-backed pages directly into the process address space and relying heavily on the operating system's virtual-memory machinery.

There is no universally best choice. The appropriate design depends on the engine's workload, its own cache-management sophistication, the operating system, and the desired balance between application control and kernel-managed caching.

### Storage Access Strategies

The databases in these notes provide useful examples of different ways software can divide storage responsibilities between the application and operating system.

- **[SQLite](SQLite.md#Storage%20Model)**: Uses ordinary filesystem files and maintains its own database page cache while still operating through the OS file and page-cache infrastructure.
- **[PostgreSQL](PostgreSQL.md#Shared%20Buffers)**: Maintains its own shared buffer pool while also using the operating system's page cache for ordinary data-file I/O. Its [WAL](#Write-Ahead%20Logging%20(WAL)) path uses explicit storage synchronization to establish transaction durability boundaries.
- **[LMDB](LMDB.md#File%20Access%20Through%20%60mmap%60)**: Memory-maps its database and relies much more directly on the operating system's virtual-memory and file-cache machinery to manage the resident working set.
- **Design Choice**: These approaches demonstrate that there is no universal rule that a database should either “use the OS cache” or “bypass the OS cache.” Cache ownership, file access, and durability mechanisms are architectural choices made according to the engine's workload and design.

## Durability and Crash Recovery

Database durability is not only about issuing writes. A database must remain internally consistent when a process crashes, the operating system fails, or power is lost at an inconvenient point during an update.

Storage writes can become durable at different times. A modified database page may first exist only in the database's memory, then in the operating system's dirty page cache, then in a volatile device write cache, and finally in non-volatile media. Database engines therefore need explicit durability boundaries and recovery protocols rather than assuming that an ordinary completed write means all related state is safely persistent.

### Torn Pages

A database page can be larger than the storage system's guaranteed crash-atomic write unit. Suppose an engine uses an 8 KiB database page while the underlying storage can guarantee atomic persistence only for smaller units. Persisting the database page may then require multiple lower-level writes.

If power is lost after some of those writes reach persistent storage but before the rest do, the page can contain a mixture of the old and new versions. This is called a **torn page** or **torn write**.

The problem is not created specifically by the operating system's page cache. Bypassing that cache with Direct I/O does not inherently make a larger database-page update atomic either. The fundamental issue is that the database's logical update can span several storage operations whose crash-atomicity boundary is smaller than the database structure being changed.

Database engines therefore combine logging and engine-specific recovery mechanisms so that interrupted page writes can be detected, reconstructed, or replaced. The exact strategy differs between engines; examples include logging complete page images at selected times, checksums, copy-on-write structures, and maintaining a separate safe copy before overwriting a page.

## Write-Ahead Logging (WAL)

**Write-Ahead Logging (WAL)** separates the durability of a logical database change from the later writeback of the full data pages affected by that change.

Before a modified database page is allowed to reach persistent storage in a state that depends on a change, the engine first records enough information about that change in an append-oriented log. The essential ordering rule is that the relevant log record must become durable **before** the corresponding data-page update can require it for recovery.

This changes the write path. A transaction does not normally need to synchronously persist every modified table or index page at commit time. Instead, the database can make the required WAL records durable and allow dirty data pages to be written later in larger or more convenient batches.

After a crash, the engine examines the durable log and replays whatever committed changes are necessary to reconstruct data pages that had not yet reached their final persistent form. Depending on the database design, the recovery process may also need to ignore, roll back, or otherwise account for changes belonging to transactions that did not commit.

WAL therefore serves two related purposes: it provides a compact durability path for transactions and gives the database a history from which it can recover after interrupted writeback. It does not by itself imply one particular file-I/O strategy; a database can combine WAL with buffered I/O, Direct I/O, memory mapping, or other storage techniques according to its architecture.

### WAL and Filesystem Journaling

Database WAL and [filesystem journaling](06%20Storage%20Management.md#Journaling%20and%20Crash%20Consistency) use a similar idea—persist recovery information before allowing dependent state to become unrecoverable—but they protect consistency at different abstraction layers.

A filesystem journal protects **filesystem invariants**. It understands structures such as inodes, directory entries, allocation metadata, and filesystem blocks. Its goal is to ensure that a crash does not leave the filesystem itself structurally inconsistent. Depending on the filesystem and journaling mode, ordinary file contents may not be included in the journal at all.

A database WAL protects **database invariants**. The database understands transactions, database pages, tables, indexes, and relationships between changes that the filesystem sees only as writes to ordinary files. For example, if one database transaction modifies several pages, the filesystem cannot know that those page changes belong to one atomic database operation.

Filesystem journaling therefore cannot replace WAL. It may guarantee that all database files remain valid filesystem objects after a crash while their contents still represent only part of a database transaction. The database needs its own recovery information to determine which changes were committed and reconstruct a consistent database state.

WAL cannot generally replace filesystem journaling either. The database relies on the filesystem to maintain its own metadata and storage mappings correctly. Database recovery records cannot repair arbitrary corruption of filesystem structures such as allocation metadata or directory entries.

Using both can cause some **write amplification**, particularly when the filesystem also journals file data, but the two logs are not logically redundant. They establish crash consistency for different layers of the storage stack.