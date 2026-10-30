# Redis Persistence

Redis serves data from memory; **persistence** supplies a local representation from which that data can be reconstructed after restart. Receiving a successful write reply is not, by itself, proof that the write crossed a [durability](../../Databases/Fundamentals/00%20Overview.md#Durability%20and%20Crash%20Recovery) boundary. The persistence mode and synchronization policy determine which acknowledged changes survive a failure.

Redis Open Source supports **RDB snapshots**, **append-only files (AOF)**, both together, or neither. Without either persistence mechanism, Redis has no local persistence source for restoring its in-memory writes. The multipart AOF layout described below applies to Redis 7.0 and later. [Redis persistence documentation](https://github.com/redis/docs/blob/main/content/operate/oss_and_stack/management/persistence.md).

## RDB Snapshots

An **RDB snapshot** serializes the dataset at a point in time into a compact binary file. Recovery loads that saved state rather than replaying every historical write.

### Save-Point Configuration

A **save point** is a configured trigger for automatic RDB snapshotting: a minimum elapsed interval and a minimum number of dataset changes. Both thresholds must be met within one save point; if several save points are configured, satisfying any one of them triggers a snapshot attempt.

Configure a save point in `redis.conf` with the `save` directive:

```conf
save 60 1000
```

This rule requests a snapshot after at least 60 seconds and 1,000 changes. It schedules an attempt, not a completed snapshot or a durability guarantee. [Redis persistence documentation](https://github.com/redis/docs/blob/main/content/operate/oss_and_stack/management/persistence.md).

For a running server, `CONFIG SET save "60 1000"` changes the active setting. Runtime changes do not update `redis.conf`; edit that file or use `CONFIG REWRITE` to retain them after restart. [Redis configuration documentation](https://github.com/redis/docs/blob/main/content/operate/oss_and_stack/management/config.md).

### Snapshot Creation

Background snapshotting uses `BGSAVE`, either requested explicitly or triggered by configured save points:

1. Redis forks a child process with a view of the dataset at the fork point.
2. The child serializes that view into a temporary RDB file while the parent continues serving clients.
3. After the new snapshot is complete, it atomically replaces the previous snapshot file.

The parent and child initially share physical pages through [copy-on-write](../../Operating%20Systems/03%20Memory%20Management.md#Controlled%20Sharing%20%26%20Concurrency). Writes to shared pages create private copies, preserving the child's earlier view without copying the entire dataset at fork time.

The child handles snapshot I/O, but background saving is not completely non-blocking:

- **Fork latency:** Redis pauses client processing while it creates the child and copies process metadata, including page tables. The pause depends on dataset size and the operating environment. [Redis fork latency](https://github.com/redis/docs/blob/main/content/operate/oss_and_stack/management/optimization/latency.md).
- **Memory pressure:** Pages modified while the child is active require additional memory. A write-heavy workload during a long snapshot increases copy-on-write pressure.
- **Storage load:** Snapshot creation writes the dataset while the parent serves traffic, creating competing I/O demand.

`SAVE`, unlike `BGSAVE`, performs a synchronous save that blocks Redis from serving every client, not just the caller, until it finishes. [Redis `SAVE` documentation](https://github.com/redis/docs/blob/main/content/commands/save.md).

Shutdown uses that same synchronous RDB save when at least one save point is configured. `SHUTDOWN SAVE` forces an RDB snapshot even without configured save points, while `SHUTDOWN NOSAVE` suppresses it. If AOF is enabled, Redis also flushes the AOF during shutdown; the `SAVE` modifier is not merely an AOF synchronization request. [Redis `SHUTDOWN` documentation](https://github.com/redis/docs/blob/main/content/commands/shutdown.md).

### Snapshot Recovery Point

With RDB alone, recovery restores the last successfully completed snapshot. Changes after that snapshot's captured state are absent, including writes acknowledged while the snapshot was being produced.

Scheduling snapshots does not make each intervening write durable. Failed or delayed saves leave an older recovery point. RDB provides a compact artifact for backup and transfer, but reducing potential write loss requires more frequent successful snapshots or an additional persistence mechanism.

## Append-Only Persistence

With `appendonly yes`, Redis records operations that change the dataset in an **append-only file (AOF)**. Recovery reconstructs state from that persisted representation and its subsequent operations rather than relying only on periodic standalone snapshots.

Appending to a file and making its contents durable are different events. A buffered AOF append modifies OS page-cache pages and marks them dirty; a successful file write does not establish that those bytes reached persistent storage. Kernel writeback persists dirty pages later, while explicit synchronization establishes a requested durability boundary. Redis uses an `appendfsync` policy to control [storage synchronization](../../Operating%20Systems/06%20Storage%20Management.md#Write%20Durability%20and%20Synchronization):

| Policy     | Synchronization boundary                                                         | Durability and cost                                                                                                                              |
| ---------- | -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| `always`   | Synchronizes each appended batch before sending its replies.                     | Puts synchronization latency on the reply path; several commands can share a batch and synchronization.                                          |
| `everysec` | Requests synchronization about once per second in a background thread.           | Avoids waiting for each batch to become durable, but permits loss of recent acknowledged writes. This is the default AOF synchronization policy. |
| `no`       | Redis does not explicitly synchronize the AOF; writeback is delegated to the OS. | Provides no Redis-controlled synchronization interval; failure exposure depends on OS writeback and the storage stack.                           |

The policy's intended synchronization interval is subject to these limits:

- **I/O delays:** The documented loss window for `everysec` is approximately one second under normal operation, not a hard real-time guarantee under delayed or failing I/O.
- **Rewrite configuration:** Suppressing synchronization during background persistence, such as with `no-appendfsync-on-rewrite yes`, further weakens that boundary.
- **Storage guarantees:** For every policy, persistence depends on the filesystem and device honoring synchronization requests.

> [!example] Acknowledgment before synchronization
> With `everysec`, a client receives success for a write before the next background synchronization finishes. A power failure in that interval can erase the acknowledged write. Replaying the surviving AOF cannot reconstruct operations that never became durable.
<!-- Separate callouts. -->
> [!note] AOF and write-ahead logging
> Redis's incremental AOF is a **logical redo log**, sharing the recovery-by-replay model of [Write-Ahead Logging (WAL)](../../Databases/Fundamentals/00%20Overview.md#Write-Ahead%20Logging%20(WAL)). The comparison has two dimensions:
>
> - **Acknowledgment boundary:** With `appendfsync always`, AOF follows the durable-commit principle of making the recovery log durable before acknowledging success, subject to the synchronization limits above.
> - **Persistence ordering:** Page-oriented WAL additionally requires durable log records before dependent data-page writes; Redis has no separate persistent data pages requiring that ordering. Redis updates its in-memory dataset before appending commands to AOF, but changing memory first does not itself conflict with WAL's write-ahead rule.

## AOF Rewriting and Multipart Files

An append-only history grows even when the live dataset does not. Repeatedly replacing one key creates history that is unnecessary for reconstructing its final value. **AOF rewriting** produces a new representation of the current dataset rather than retaining every past operation.

Since Redis 7.0, AOF persistence consists of:

- **Base file:** At most one file representing the dataset at the rewrite point, in RDB or AOF format.
- **Incremental files:** Record changes after the base state; there can be multiple incremental files.
- **Manifest:** Identifies the files constituting the active AOF and their loading order.

`BGREWRITEAOF`, or an automatic rewrite trigger, rebuilds that representation without discarding concurrent writes:

1. Redis forks a child to generate a new base while the parent records new changes in a new incremental file.
2. The child finishes the base. The parent prepares and persists a temporary manifest identifying the new base and the required incremental file.
3. Redis atomically replaces the active manifest, then removes obsolete files.

If rewriting fails before the switch, the previous base and incremental files, together with the new incremental file, still represent the dataset's recorded history. Rewriting reduces redundant history; it does not strengthen `appendfsync` or make unsynchronized writes durable. Like background snapshotting, it incurs fork, copy-on-write, and storage costs.

## Restart Recovery and Combined Persistence

The enabled persistence modes determine which representation Redis uses at restart:

- **RDB only:** Load the last completed standalone snapshot. Writes after its captured state are not recovered.
- **AOF only:** Load the base identified by the manifest, if present, then replay its incremental files in order. An RDB-format base is part of this AOF recovery chain, not a separate standalone snapshot selected independently.
- **RDB and AOF:** Redis chooses AOF for restart recovery because it is intended to contain the more complete write history. It does not merge an arbitrary standalone RDB snapshot with an unrelated AOF tail.

RDB's compact saved image is useful for backups and avoids replaying a long command history. AOF provides finer-grained persistence with additional append, synchronization, and rewrite work. Combining them retains snapshot artifacts alongside AOF recovery, but also consumes resources for both mechanisms.

> [!warning] Interrupted writes and storage loss
> With `aof-load-truncated` enabled, Redis accepts an AOF with an incomplete final command by discarding that incomplete tail. This is not a general repair guarantee for corruption elsewhere in the file. Neither local RDB nor local AOF protects against destruction of the storage holding it; separate backups remain necessary.
