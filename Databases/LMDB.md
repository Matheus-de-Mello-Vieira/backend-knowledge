# LMDB

LMDB (Lightning Memory-Mapped Database) is a small **embedded ordered key-value database**. Applications link it directly into their process and store opaque byte keys and values without running a separate database server or using SQL.

## Main Point

LMDB is useful when an application needs very fast local key-value reads, transactional persistence, and a small operational footprint. Its interface is intentionally narrow: instead of tables, joins, or a query planner, the database behaves primarily like a persistent ordered map from `key` to `value`.

This makes LMDB substantially different from [SQLite](SQLite.md#Main%20Point). Both are embedded databases, but SQLite provides a complete relational SQL engine while LMDB provides a much smaller ordered key-value abstraction. LMDB was originally developed for OpenLDAP, where a database backend needs extremely frequent indexed lookups and predictable local access without operating another database service.

## Storage Model

Keys and values are byte sequences. Looking up a key returns its corresponding value, while the ordering of keys also makes range scans and ordered iteration efficient.

Internally, LMDB stores these entries in a **B+ tree**. Branch pages guide searches toward the appropriate part of the key space, while leaf pages contain the stored entries. A lookup therefore follows a small path through the tree rather than scanning the complete database.

LMDB's storage engine is built around memory-mapping its database file into the process's [virtual address space](../Operating%20Systems/03%20Memory%20Management.md#Virtual%20Memory). Once the required file-backed pages are resident in physical memory, reads can operate directly on the tree pages without maintaining a separate database buffer pool. The operating system therefore participates directly in managing which database pages form the resident working set.

### File Access Through `mmap`

LMDB provides a concrete example of a database architecture built around the operating system's [`mmap`](../Operating%20Systems/02%20The%20Anatomy%20of%20a%20Process.md#The%20%60mmap%60%20System%20Call%20(Memory%20Mapping)) mechanism.

A simplified read path is:

1. LMDB opens the database file.
2. The file is mapped into the process's virtual address space.
3. A key lookup follows pointers through B+ tree pages.
4. If a required mapped page is already resident in RAM, the CPU can access it through the mapping.
5. If the page is not resident, accessing it can trigger a [page fault](../Operating%20Systems/03%20Memory%20Management.md#Limitations%20of%20Virtual%20Memory).
6. The operating system brings the required file-backed page into physical memory.
7. LMDB continues traversing the database structure.

- **No Separate Read Buffer Pool**: LMDB does not need to copy every database page into a separate application-managed read cache.
- **OS Residency Management**: The operating system's virtual-memory and file-caching mechanisms determine which mapped database pages remain physically resident.
- **Cross-Layer Example**: LMDB therefore connects filesystem storage, process virtual-address mappings, page faults, and database access in one architecture.

The configured database mapping can be much larger than physical RAM because reserving virtual address space does not make every mapped page resident immediately. Hot pages tend to remain in memory while colder clean pages can be reclaimed and loaded again from the database file when needed.

The deliberately small abstraction is important to LMDB's design. Features such as relational joins, SQL parsing, and sophisticated query planning are outside its scope; the application is responsible for building any higher-level data model it needs on top of the key-value interface.

## Transactions and Concurrency

LMDB provides ACID transactions and uses **Multi-Version Concurrency Control (MVCC)** so readers can operate on stable snapshots while updates create newer versions of modified pages.

Read transactions are intentionally cheap and do not require a global read lock. Many readers can execute concurrently without blocking the writer, and the writer does not invalidate the pages currently being observed by existing readers.

Writes are more constrained: LMDB allows only **one write transaction at a time**. This serialized-writer design removes a large amount of locking complexity and is a good fit for workloads dominated by reads, but it makes LMDB a poor choice when an application requires high concurrent write throughput from many independent writers.

## Copy-on-Write Updates

LMDB does not normally overwrite database pages that are still part of a reader's current snapshot. When a write transaction modifies data, it creates replacement pages and updates the B+ tree to refer to the new versions. Existing readers can continue traversing the old pages until their transactions finish.

This copy-on-write behavior works naturally with its file-backed storage model. Most unchanged pages remain clean and recoverable from the database file, while LMDB maintains free-page information so pages made obsolete by completed transactions can eventually be reused.
