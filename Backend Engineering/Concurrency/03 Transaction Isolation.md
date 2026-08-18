# Transaction Isolation

A database transaction groups several operations into one logical unit, but **atomicity alone does not make concurrent transactions safe**. Two transactions can each execute correctly in isolation and still interfere with one another when their reads and writes overlap.

**Transaction isolation** defines how much of one transaction's intermediate or concurrent activity can become visible to another transaction. Stronger isolation makes concurrent execution behave more like transactions were executed one at a time, while weaker isolation allows more overlap in exchange for potentially exposing concurrency anomalies.

The underlying problem is the same one described in [Concurrency Fundamentals](01%20Concurrency%20Fundamentals.md): multiple actors may observe and modify shared state concurrently. The difference is the abstraction level. Here, the actors are **transactions**, and the database's concurrency-control mechanisms determine which states those transactions are allowed to observe.

## Serial Execution and Serializability

The simplest way to avoid transaction interference would be to execute transactions one at a time:

```text
Transaction A
    read
    write
    commit

Transaction B
    read
    write
    commit
```

This is **serial execution**. Because transactions never overlap, each transaction observes a stable database state produced by all transactions that completed before it.

Serial execution is easy to reason about but severely limits concurrency. Databases therefore allow transactions to overlap while trying to preserve some or all of the guarantees of serial execution.

A concurrent history is **serializable** when its final effect is equivalent to some valid serial ordering of the same transactions.

The transactions do not need to literally execute one after another. Their operations may overlap internally, as long as the database prevents the resulting history from producing an outcome that could not have occurred under any serial order.

Serializable isolation is therefore primarily a **correctness guarantee**, not an implementation strategy. A database may implement it using locking, versioning, conflict detection, or a combination of mechanisms.

## Transaction Anomalies

Weaker isolation allows some concurrent interactions that would not appear during serial execution. These behaviors are usually described as **transaction anomalies**.

### Dirty Read

A **dirty read** occurs when one transaction reads data written by another transaction that has not committed yet.

Suppose an account begins with:

```text
balance = 100
```

Transaction A changes it:

```text
Transaction A:
    UPDATE balance = 0
    // not committed
```

Before A commits, Transaction B reads:

```text
Transaction B:
    SELECT balance
    → 0
```

If Transaction A later rolls back, the value `0` was never part of the committed database state:

```text
Transaction A:
    ROLLBACK
```

Transaction B has therefore made an observation based on state that effectively never existed.

Dirty reads are prevented when transactions can only observe committed data.

### Non-Repeatable Read

A **non-repeatable read** occurs when a transaction reads the same row twice and receives different committed values because another transaction modified the row between those reads.

For example:

```text
Transaction A:
    SELECT balance
    → 100
```

Then another transaction modifies and commits the row:

```text
Transaction B:
    UPDATE balance = 50
    COMMIT
```

Transaction A reads the row again:

```text
Transaction A:
    SELECT balance
    → 50
```

Both values were committed and individually valid. The anomaly is that Transaction A does not observe a stable view of the row during its own lifetime.

This differs from a dirty read because the second value was committed before A observed it.

### Phantom Read

A **phantom read** occurs when a transaction repeats a query over a set of rows and the set itself changes because another transaction inserted, deleted, or modified rows that now satisfy the query predicate.

Suppose Transaction A executes:

```sql
SELECT *
FROM orders
WHERE status = 'pending';
```

and receives 10 rows.

Transaction B then inserts another pending order and commits:

```sql
INSERT INTO orders (...)
VALUES (..., 'pending');

COMMIT;
```

If Transaction A repeats the original query and now receives 11 rows, the new row is a **phantom**.

A non-repeatable read concerns a row that was already selected but changed value. A phantom read concerns the **membership of a result set** changing.

### Lost Update

A **lost update** occurs when two transactions read the same old state, independently compute updates, and one write overwrites the effect of the other.

Suppose:

```text
balance = 100
```

Both transactions read the same value:

```text
Transaction A reads 100
Transaction B reads 100
```

They independently compute:

```text
Transaction A: 100 - 30 = 70
Transaction B: 100 - 50 = 50
```

and then write:

```text
Transaction A writes 70
Transaction B writes 50
```

The final value is `50`. Transaction A's successful update has disappeared.

This is the same fundamental [lost-update race](01%20Concurrency%20Fundamentals.md#Race%20Conditions) that can happen in shared memory, now occurring through database transactions.

A transaction system can prevent lost updates pessimistically by locking the relevant state, or optimistically by making the final write conditional on the state or version that was originally observed, as described in [Concurrency Control Strategies](01%20Concurrency%20Fundamentals.md#Concurrency%20Control%20Strategies).

### Read Skew / Inconsistent Read

A transaction may need several values to represent one logical invariant. If those values are read at different moments while another transaction modifies them, the reader can observe a combination of values that never existed together.

Suppose two accounts contain:

```text
Account A = 500
Account B = 500
Total     = 1000
```

Transaction B transfers `100` from A to B:

```text
A = 400
B = 600
```

If Transaction A reads Account A before the transfer and Account B after the transfer, it may observe:

```text
A = 500
B = 600
Total = 1100
```

Every individual value was valid at some point, but the combination was never a valid committed state of the two accounts together.

This is commonly called **read skew** or an inconsistent read.

### Write Skew

A **write skew** occurs when two transactions read overlapping state, make decisions that are individually valid based on that state, and then write different records in a way that jointly violates an invariant.

Suppose a hospital requires at least one doctor to remain on call:

```text
Alice on_call = true
Bob   on_call = true
```

Transaction A checks that Bob is on call and decides Alice can leave:

```text
read Bob.on_call = true
write Alice.on_call = false
```

At the same time, Transaction B checks that Alice is on call and decides Bob can leave:

```text
read Alice.on_call = true
write Bob.on_call = false
```

The transactions update different rows, so a simple check for concurrent writes to the same row may detect no direct conflict.

Both commit:

```text
Alice on_call = false
Bob   on_call = false
```

The invariant has been violated even though neither transaction overwrote the other's write.

Write skew is particularly important because preventing dirty reads or lost updates is not enough to guarantee serializable behavior. Correctness may depend on **relationships between multiple records**, not just conflicts over one row.

## Isolation Levels

An **isolation level** defines which kinds of concurrent observations a transaction is allowed to make.

The traditional SQL levels are:

1. Read Uncommitted
2. Read Committed
3. Repeatable Read
4. Serializable

Higher levels generally provide stronger guarantees but may require more blocking, conflict detection, retries, or bookkeeping.

The exact behavior of a named isolation level can differ between database engines. The descriptions below are therefore conceptual; a database's documentation is the source of truth for its exact semantics.

### Read Uncommitted

**Read Uncommitted** provides very little isolation between transactions.

A transaction may be allowed to observe changes made by another transaction before those changes commit, which makes **dirty reads** possible.

This level maximizes freedom for concurrent execution but makes application reasoning difficult because observed state may later disappear through rollback.

Many modern database engines either do not expose true Read Uncommitted behavior or internally provide stronger semantics even when this level is requested.

### Read Committed

**Read Committed** ensures that a transaction only reads committed data.

This prevents dirty reads:

```text
Transaction B cannot observe Transaction A's uncommitted write.
```

However, each statement may observe the database at a different committed point in time. If another transaction commits between two reads, the second read may return different data.

Read Committed can therefore still allow:

- non-repeatable reads;
- phantom reads;
- some lost-update patterns unless writes use appropriate locking or conditional updates.

It is a common default because it prevents the most obvious visibility problem while still allowing substantial concurrency.

### Repeatable Read

**Repeatable Read** strengthens the guarantee so that data already observed by a transaction remains stable for that transaction.

Conceptually, if a transaction reads:

```text
balance = 100
```

another transaction may commit a change to that row, but repeating the read inside the first transaction should continue to produce a view consistent with the isolation guarantee rather than suddenly exposing the new value.

This prevents non-repeatable reads.

The treatment of phantom rows and write conflicts varies significantly between implementations. Some databases use snapshot-based semantics, while others combine locks and range protection. The name `REPEATABLE READ` should therefore not be assumed to imply identical behavior across database engines.

### Serializable

**Serializable** provides the strongest conventional transaction-isolation guarantee.

Concurrent transactions are allowed to overlap, but the database ensures that their committed effects are equivalent to some serial execution order.

This prevents anomalies that require a history impossible under serial execution, including write skew.

Providing this guarantee does not necessarily mean every transaction is locked from beginning to end. A database may instead allow optimistic concurrency and abort a transaction when it detects that the concurrent history cannot be serialized safely.

Applications using serializable isolation must therefore generally be prepared to **retry transactions that fail because of serialization conflicts**.

## Snapshot Isolation

**Snapshot Isolation** is a widely used model that is not identical to the four traditional SQL isolation levels.

Under snapshot isolation, a transaction reads from a consistent snapshot representing the database at a particular logical point in time. Other transactions may continue committing changes, but those changes do not suddenly appear inside the existing transaction's snapshot.

This naturally prevents dirty reads and provides stable reads across the transaction.

For example:

```text
Transaction A starts with snapshot S1
Transaction B updates a row and commits
Transaction A continues reading snapshot S1
```

Transaction A does not need to block Transaction B merely to preserve its own consistent read view.

Snapshot isolation often detects direct write-write conflicts, preventing two transactions from independently committing incompatible writes to the same record.

However, snapshot isolation is **not necessarily serializable**.

The write-skew example demonstrates why. Two transactions can read the same consistent snapshot, update different records, and both commit without a direct write-write conflict even though their combined result violates an invariant.

Serializable systems built on snapshot techniques therefore require additional conflict detection beyond ordinary snapshot isolation.

## How Isolation Is Implemented

Isolation levels describe **guarantees**. Databases still need concrete concurrency-control mechanisms to provide them.

### Locking

A database can use pessimistic locking to prevent conflicting operations from overlapping.

Common lock scopes include:

- rows;
- pages;
- tables;
- key ranges or index ranges.

A transaction that holds an incompatible lock can force another transaction to wait until the lock is released.

Locks can directly prevent many anomalies, but they introduce contention and can produce [deadlocks](01%20Concurrency%20Fundamentals.md#Deadlock). Lock granularity determines how much unrelated work is unnecessarily blocked.

Range or predicate protection is especially relevant to phantom reads. Locking only rows that currently exist may not prevent another transaction from inserting a new row that satisfies the same predicate.

### Multi-Version Concurrency Control

**Multi-Version Concurrency Control (MVCC)** keeps multiple logical versions of data so readers do not always need to block writers.

Instead of overwriting the only copy of a row immediately, an update creates a newer version while older versions may remain temporarily available to transactions whose snapshots still need them.

Conceptually:

```text
Row version V1 → visible to older transaction
Row version V2 → visible to newer transaction
```

The database tracks metadata that determines which versions are visible to each transaction.

This allows a reader to continue observing a stable snapshot while another transaction updates the same logical row.

MVCC therefore improves concurrency by separating **read visibility** from the latest physical version of the data. It does not, by itself, guarantee serializability. The database still needs rules for write conflicts and potentially additional dependency detection.

Old versions also cannot remain forever. Once no active transaction can require them, the database eventually reclaims the obsolete storage.

### Serializable Conflict Detection

A database can also provide serializable behavior optimistically.

Transactions are allowed to execute concurrently, but the database tracks dependencies between their reads and writes. If committing all of them would create a history that cannot correspond to any serial ordering, one transaction is aborted.

The application then retries the aborted transaction against newer state.

This follows the same general optimistic-concurrency principle described in [Concurrency Control Strategies](01%20Concurrency%20Fundamentals.md#Concurrency%20Control%20Strategies): allow concurrent work, but reject a result when the final validation proves that its assumptions cannot safely coexist with other committed work.

## Isolation Is About Invariants

Choosing an isolation level is ultimately a question about **which application invariants must remain true under concurrent execution**.

For a simple independent update, Read Committed plus an atomic conditional write may be sufficient.

For an operation whose correctness depends on several rows remaining mutually consistent, a stronger transactional boundary may be necessary.

The database cannot infer every business invariant from individual SQL statements. If correctness depends on a rule such as:

```text
at least one doctor must remain on call
```

the transaction design and isolation guarantee must protect that rule as a whole.

The important question is therefore not simply:

> Which isolation level is fastest?

but:

> Which concurrent histories can the application safely allow?

A weaker level is appropriate only when the anomalies it permits cannot violate the invariants of the operation being implemented.
