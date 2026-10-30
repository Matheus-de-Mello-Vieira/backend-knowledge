# Transaction Isolation

A database transaction groups several operations into one logical unit, but **atomicity alone does not make concurrent transactions safe**. Two transactions can each execute correctly in isolation and still interfere with one another when their reads and writes overlap.

**Transaction isolation** defines how much of one transaction's intermediate or concurrent activity can become visible to another transaction. Stronger isolation makes concurrent execution behave more like transactions were executed one at a time, while weaker isolation allows more overlap in exchange for potentially exposing concurrency anomalies.

The underlying problem is the same one described in [Concurrency Fundamentals](../../Backend%20Engineering/Concurrency/01%20Concurrency%20Fundamentals.md): multiple actors may observe and modify shared state concurrently. The difference is the abstraction level. Here, the actors are **transactions**, and the database's concurrency-control mechanisms determine which states those transactions are allowed to observe.

## Serial Execution and Serializability

**Serial execution** runs transactions one at a time, without overlap. Each transaction starts from the database state left by preceding transactions, so no other transaction changes that state while it executes:

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

This prevents interference and makes execution easy to reason about, but removes transaction-level concurrency. Allowing transactions to overlap avoids that restriction; the correctness question is whether their combined behavior still matches a serial execution.

A **history** is the sequence of operations performed by transactions. A concurrent history is **serializable** when its observable results and final database state are equivalent to those of some valid serial ordering of the same transactions. Operations may interleave, but they must not produce an outcome that no serial order could produce.

The distinction is between an execution strategy and a correctness guarantee:

- **Serial execution:** Transactions actually execute one after another.
- **Serializable isolation:** Transactions are allowed to overlap, but their combined behavior must remain equivalent to a serial execution.

Serializable isolation does not prescribe a concurrency-control mechanism. A database may enforce it through locking, versioning with conflict detection, or a combination of mechanisms.

## Transaction Anomalies

Weaker isolation allows some concurrent interactions that would not appear during serial execution. These behaviors are described as **transaction anomalies**.

Each timeline uses one column per concurrent transaction, rather than per physical thread: isolation governs transactions regardless of how threads execute them. Each transaction remains open until it commits or rolls back.

> [!note] Reading the timelines
> Time advances downward through logical steps, not measured durations. To keep the tables compact, a row may contain operations from both transactions. Read those operations **left to right within the row**, then continue to the next row; sharing a row does not imply simultaneous execution. This ordering describes the illustrated history, not an ordering guaranteed by the database. A dash means no operation is shown for that transaction at that step.

The tables show histories allowed when the relevant anomaly is not prevented. Stronger isolation or explicit concurrency control changes which operations proceed, wait, or abort.

### Dirty Read

A **dirty read** occurs when one transaction reads data written by another transaction that has not committed yet.

Initially, `balance = 100`.

| Time | Transaction A | Transaction B |
| --- | --- | --- |
| t1 | Begin transaction. | Begin transaction. |
| t2 | Write `balance = 0`; not committed. | Read `balance` → `0` (A's uncommitted value). |
| t3 | Roll back; discard the write. | Commit. |

Transaction B observed `0`, but A's rollback means that value never became part of the committed database state. B's observation therefore relied on a change that was later discarded.

Dirty reads are prevented when transactions only observe committed data.

### Non-Repeatable Read

A **non-repeatable read** occurs when a transaction reads the same row twice and receives different committed values because another transaction modified the row between those reads.

Initially, `balance = 100`.

| Time | Transaction A | Transaction B |
| --- | --- | --- |
| t1 | Begin transaction. | Begin transaction. |
| t2 | Read `balance` → `100`. | Write `balance = 50`. |
| t3 | — | Commit. |
| t4 | Read the same row's `balance` → `50`. | — |
| t5 | Commit. | — |

Both values were committed and individually valid, but A did not observe a stable view of the row during its own lifetime. Unlike a dirty read, the second value was committed before A observed it.

### Phantom Read

A **phantom read** occurs when a transaction repeats a query over a set of rows and the set's membership changes because another transaction inserted, deleted, or modified rows affecting the query predicate.

Initially, 10 orders satisfy `status = 'pending'`.

| Time | Transaction A | Transaction B |
| --- | --- | --- |
| t1 | Begin transaction. | Begin transaction. |
| t2 | `SELECT * FROM orders WHERE status = 'pending';` → 10 rows. | Insert an order with `status = 'pending'`. |
| t3 | — | Commit. |
| t4 | Repeat the same query → 11 rows. | — |
| t5 | Commit. | — |

The newly returned row is a **phantom**. A non-repeatable read concerns a previously selected row changing value; a phantom read concerns the **membership of a result set** changing.

### Lost Update

A **lost update** occurs when two transactions read the same old state, independently compute updates, and one write overwrites the effect of the other.

Initially, `balance = 100`. A intends to subtract `30`; B intends to subtract `50`.

| Time | Transaction A | Transaction B |
| --- | --- | --- |
| t1 | Begin transaction. | Begin transaction. |
| t2 | Read `balance` → `100`. | Read `balance` → `100`. |
| t3 | Compute `100 - 30 = 70` locally. | Compute `100 - 50 = 50` locally. |
| t4 | Write `balance = 70`. | — |
| t5 | Commit. | Write `balance = 50` using the earlier computation. |
| t6 | — | Commit. |

The final value is `50`: A's successful update has disappeared. B overwrote it using a calculation based on the old balance, rather than applying its subtraction to A's committed result.

This is the same fundamental [lost-update race](../../Backend%20Engineering/Concurrency/01%20Concurrency%20Fundamentals.md#Race%20Conditions) that occurs in shared memory, now occurring through database transactions.

A transaction system can prevent lost updates pessimistically by locking the relevant state, or optimistically by making the final write conditional on the state or version originally observed, as described in [Concurrency Control Strategies](../../Backend%20Engineering/Concurrency/01%20Concurrency%20Fundamentals.md#Concurrency%20Control%20Strategies).

### Read Skew / Inconsistent Read

**Read skew**, or an **inconsistent read**, occurs when a transaction reads related values at different moments and observes a combination that never existed together in a committed state.

Initially, Account A and Account B each contain `500`, for a total of `1000`. Transaction B transfers `100` from Account A to Account B in one transaction.

| Time | Transaction A (reader) | Transaction B (transfer) |
| --- | --- | --- |
| t1 | Begin transaction. | Begin transaction. |
| t2 | Read Account A → `500`. | Write Account A = `400`. |
| t3 | — | Write Account B = `600`. |
| t4 | — | Commit both changes. |
| t5 | Read Account B → `600`. | — |
| t6 | Compute observed total: `500 + 600 = 1100`. | — |
| t7 | Commit. | — |

Every individual value was valid at some point, but the reader combined Account A's pre-transfer balance with Account B's post-transfer balance. The total remained `1000` in both committed states; the observed `1100` never represented the two accounts together.

When several values represent one logical invariant, reading committed values individually is not enough to ensure a consistent combined observation.

### Write Skew

A **write skew** occurs when two transactions read overlapping state, make individually valid decisions based on that state, and then write different records in a way that jointly violates an invariant.

A hospital requires **at least one doctor to remain on call**. Initially, both `Alice.on_call = true` and `Bob.on_call = true`.

| Time | Transaction A (Alice leaves)                         | Transaction B (Bob leaves)                           |
| ---- | ---------------------------------------------------- | ---------------------------------------------------- |
| t1   | Begin transaction.                                   | Begin transaction.                                   |
| t2   | Read `Bob.on_call` → `true`; decide Alice can leave. | Read `Alice.on_call` → `true`; decide Bob can leave. |
| t3   | Write `Alice.on_call = false`.                       | Write `Bob.on_call = false`.                         |
| t4   | Commit.                                              | Commit.                                              |

Both doctors are now off call. Each decision was valid against the state read, but their combined effect violated the invariant.

The transactions updated different rows, so checking only for concurrent writes to the same row detects no direct conflict. Neither transaction overwrote the other's write.

Preventing dirty reads or lost updates is therefore not enough to guarantee serializable behavior. Correctness also depends on **relationships between multiple records**, not just conflicts over one row.

## Isolation Levels

An **isolation level** defines which kinds of concurrent observations a transaction is allowed to make. The four traditional SQL levels provide progressively stronger guarantees, with potential costs in blocking, conflict detection, retries, or bookkeeping.

| Isolation level | Core guarantee | Anomalies still possible | Important caveats |
| --- | --- | --- | --- |
| **Read Uncommitted** | Very little isolation; reads of another transaction's uncommitted changes are permitted. | Dirty reads and other concurrency anomalies are not ruled out. | Gives concurrent execution the most freedom, but observations may disappear after rollback, making application reasoning difficult. Many modern engines omit true Read Uncommitted or provide stronger semantics under this name. |
| **Read Committed** | Reads only committed data, preventing dirty reads. Each statement may observe a different committed point in time. | Non-repeatable reads, phantom reads, and some lost-update patterns. | A common default that prevents uncommitted-data visibility while retaining substantial concurrency. Lost-update protection requires appropriate locking or conditional updates when the engine does not provide it automatically. |
| **Repeatable Read** | Previously read data remains stable within the transaction, preventing non-repeatable reads. | Phantom reads and write-related anomalies depend on the engine's guarantees. | A concurrent commit must not make a repeated read suddenly expose a new value in violation of the repeatable-read guarantee. |
| **Serializable** | Observable results and committed effects are equivalent to some serial ordering of the transactions: the strongest conventional isolation guarantee. | No anomalies requiring a history impossible under serial execution, including write skew. | Concurrent execution is still permitted; transactions may fail with serialization conflicts and require retries. |

- **Implementation differences:** These are conceptual guarantees; a database's documentation determines its exact semantics. Repeatable Read differs particularly in phantom protection and write-conflict handling: some engines use snapshot-based semantics, while others combine locks and range protection. The name `REPEATABLE READ` alone does not establish identical behavior across engines.
- **Serializable execution:** Serializability does not require locking every transaction from beginning to end or executing transactions one at a time. An optimistic implementation allows overlap and aborts a transaction when conflict detection determines that the history cannot be serialized safely. Applications must be prepared to **retry transactions that fail because of serialization conflicts**.

## Snapshot Isolation

**Snapshot isolation** gives a transaction a consistent view of committed data from a particular logical point in time. Commits by other transactions do not refresh that view. It is a widely used isolation model, distinct from the four traditional SQL isolation levels.

The snapshot separates what a transaction reads from changes committed concurrently:

- **Stable read view:** Reads use the same committed snapshot throughout the transaction, preventing dirty reads and keeping observations stable despite other transactions' commits.
- **Reader–writer concurrency:** Preserving that read view does not itself require blocking another transaction from updating and committing the data.

> [!example] A stable snapshot during a concurrent update
> 1. Transaction A establishes snapshot `S1`.
> 2. Transaction B updates a row and commits.
> 3. Transaction A reads the row from `S1`, without observing B's newly committed version.

Stable reads do not, by themselves, make the combined effects of concurrent transactions serializable. Write-conflict checks and cross-record dependencies address different problems:

- **Direct write conflicts:** Snapshot-isolation implementations commonly detect incompatible concurrent writes to the same record, preventing both transactions from independently committing those writes.
- **Write skew:** Transactions that read the same snapshot and update different records have no direct write–write conflict. Both can commit even when their combined changes violate an invariant, as in the on-call-doctor example.

Snapshot isolation is therefore **not a guarantee of serializability**. Serializable systems built on snapshot techniques require additional conflict detection beyond ordinary snapshot isolation to reject combinations of transactions that cannot correspond to a serial execution.

## How Isolation Is Implemented

Isolation levels specify **guarantees**; concurrency-control mechanisms determine how the database enforces them. Locking restricts conflicting operations, versioning controls which data readers observe, and serializable conflict detection rejects incompatible transaction histories. A database can combine these mechanisms rather than choosing only one.

### Locking

**Pessimistic locking** coordinates access before conflicting operations proceed. When an operation requests a lock incompatible with one already held, it waits until the conflicting lock is released.

The protected scope determines which operations interfere with one another:

- **Row locks:** Protect individual rows.
- **Page locks:** Protect database pages.
- **Table locks:** Protect whole tables.
- **Key-range or index-range locks:** Protect ranges of keys rather than only individual existing rows.

Locks prevent anomalies by restricting conflicting access, but introduce contention and the possibility of [deadlocks](../../Backend%20Engineering/Concurrency/01%20Concurrency%20Fundamentals.md#Deadlock). Broader lock granularity blocks more unrelated work along with the operations that genuinely conflict.

Preventing phantom reads through locking requires protecting query membership, not just the rows already returned. Locking existing rows alone does not protect against insertion of another matching row; range or predicate protection addresses that gap.

### Multi-Version Concurrency Control

**Multi-Version Concurrency Control (MVCC)** retains multiple logical versions of data, separating **read visibility** from the latest physical version. An update creates a newer row version while older versions remain available for snapshots that still need them. A reader therefore does not have to block a writer merely to preserve its snapshot.

**MVCC is a mechanism, not an isolation level.** A snapshot uses visibility rules to select which retained versions a reader observes. [Snapshot isolation](#Snapshot%20Isolation) keeps the same committed snapshot throughout a transaction and adds rules for write conflicts. Using MVCC alone does not establish those guarantees: snapshot lifetime and conflict rules determine the isolation provided.

Version management has three responsibilities:

- **Visibility:** The database tracks metadata that determines which versions each transaction observes.
- **Retention:** Versions required by active snapshots remain available, allowing a reader to observe a stable snapshot while another transaction updates the same logical row.
- **Reclamation:** Once no active transaction can require an obsolete version, the database eventually reclaims its storage rather than retaining old versions indefinitely.

> [!example] Different versions of the same row
> An older transaction's snapshot exposes row version `V1`. After an update creates `V2`, a newer transaction whose snapshot includes that update observes `V2`, while the older snapshot continues to expose `V1`.

MVCC improves concurrency, but does not by itself guarantee serializability. The database still needs rules for write conflicts and, where serializable guarantees require it, additional dependency detection.

### Serializable Conflict Detection

**Optimistic serializable conflict detection** allows concurrent work, then rejects combinations of transactions whose dependencies cannot form a valid serial history:

1. Transactions execute concurrently while the database tracks dependencies between their reads and writes.
2. If allowing all of them to commit would produce a history incompatible with every serial ordering, the database aborts a transaction.
3. The application retries the aborted transaction against newer state.

This is [optimistic concurrency control](../../Backend%20Engineering/Concurrency/01%20Concurrency%20Fundamentals.md#Concurrency%20Control%20Strategies): concurrent work proceeds, but validation rejects a result when its assumptions cannot safely coexist with other committed work.

