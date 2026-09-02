# PostgreSQL

PostgreSQL is a general-purpose relational database management system designed to run as a **database server**. Applications connect to that server, send SQL queries, and receive results; they do not open PostgreSQL's data files directly.

## Main Point

PostgreSQL is useful when many independent clients need to share structured data while the database centrally enforces transactions, constraints, concurrency control, query planning, and durability. The server owns the persistent state and coordinates access on behalf of all connected applications.

This makes PostgreSQL fundamentally different from an embedded database such as [SQLite](SQLite.md#Main%20Point). With PostgreSQL, an application normally talks to another process, potentially on another machine. With SQLite, the database engine itself is part of the application process.

## Process Architecture

A PostgreSQL instance uses a process-oriented architecture. A main server process accepts incoming connections and each client connection is normally handled by its own backend process. PostgreSQL also runs background processes for responsibilities such as writing dirty buffers, checkpointing, autovacuum, and WAL-related work.

The backend processes have separate virtual address spaces, but they still need to cooperate over common database state. PostgreSQL therefore uses [shared memory](../Operating%20Systems/03%20Memory%20Management.md#Controlled%20Sharing%20%26%20Concurrency) for structures that must be visible across the instance.

This process model has an important operational consequence: opening thousands of database connections means creating thousands of backend processes and associated per-connection state. Application-side connection pools are therefore commonly used to limit the number of active PostgreSQL sessions.

## Shared Buffers

Database tables and indexes ultimately live in persistent files, but executing queries directly against storage for every access would be far too slow. PostgreSQL maintains a shared cache called **shared buffers**, accessible by its backend processes.

When a backend needs a database page, PostgreSQL checks whether that page is already present in shared buffers. If it is, the backend can work with the in-memory copy. Otherwise PostgreSQL reads the page from the underlying file into a shared buffer. Modified pages become **dirty** and are eventually written back to persistent storage.

Shared buffers are therefore part of PostgreSQL's own buffer-management layer. The operating system may additionally cache the same underlying files in its filesystem page cache, so PostgreSQL intentionally has both database-managed caching and OS-managed caching in the I/O path.

## Transactions and Concurrency

PostgreSQL is designed for many clients to read and modify the same logical data concurrently. It uses **Multi-Version Concurrency Control (MVCC)** so readers can often observe a consistent snapshot without blocking writers that are creating newer row versions.

Transactions still require coordination. Locks protect operations and structures where concurrent access cannot safely proceed independently, while transaction isolation determines which changes a transaction is allowed to observe. MVCC reduces contention; it does not eliminate synchronization.

Because old row versions can remain after updates and deletes, PostgreSQL also needs **VACUUM** to eventually reclaim versions that are no longer visible to any transaction. This makes storage cleanup part of the normal lifecycle of an MVCC database rather than a simple consequence of deleting a row.

## Durability and WAL

PostgreSQL uses [Write-Ahead Logging (WAL)](00%20Overview.md#Write-Ahead%20Logging%20(WAL)) for durability. Before a change to a database page is considered safely committed, the information required to reproduce that change is written to the WAL and persisted according to the configured durability guarantees.

This avoids having to synchronously flush every modified table or index page at commit time. Dirty data pages can be written later because, after a crash, PostgreSQL can replay WAL records to reconstruct changes that had been committed but had not yet reached their final data files.

### WAL Synchronization Method

PostgreSQL still needs an operating-system mechanism for forcing WAL records from volatile caches to durable storage. The `wal_sync_method` setting chooses which synchronization primitive PostgreSQL uses for that operation; it changes the mechanism used to establish the durability boundary, not the underlying WAL algorithm.

Possible methods include:

- **`open_datasync`:** opens WAL files with [`O_DSYNC`](../Operating%20Systems/06%20Storage%20Management.md#Synchronous%20Writes:%20`O_SYNC`%20and%20`O_DSYNC`), so writes complete with data-synchronization semantics.
- **`fdatasync`:** performs ordinary writes and calls `fdatasync()` when WAL must be forced durable.
- **`fsync`:** performs ordinary writes and calls [`fsync()`](../Operating%20Systems/06%20Storage%20Management.md#Writes,%20Writeback,%20and%20Durability) when WAL must be forced durable.
- **`fsync_writethrough`:** uses a platform-specific `fsync()` variant that additionally requests write-through of a device write cache when the platform provides such a mechanism.
- **`open_sync`:** opens WAL files with [`O_SYNC`](../Operating%20Systems/06%20Storage%20Management.md#Synchronous%20Writes:%20`O_SYNC`%20and%20`O_DSYNC`), making each WAL write use synchronized file-I/O semantics.

Not every method is available on every operating system. If PostgreSQL's `fsync` configuration is disabled, `wal_sync_method` is irrelevant because PostgreSQL is no longer requiring WAL updates to be forced to durable storage through these mechanisms.

The synchronization primitive is also separate from **how often** PostgreSQL needs to establish a durability boundary. Multiple transactions that commit close together can participate in **group commit**, allowing one WAL flush to make several transactions durable. This preserves the WAL ordering guarantee while reducing the cost that would result from performing an independent storage synchronization for every transaction.
