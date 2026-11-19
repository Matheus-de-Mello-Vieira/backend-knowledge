# Distributed Transaction Isolation

**Distributed transaction isolation** constrains concurrent transactions whose reads and writes span database partitions. A partition is a subset of the data managed separately; replication creates copies of that data. Cross-partition isolation requires a coherent transaction history, not merely correct concurrency control within each partition.

- **Atomic commit:** All participants agree whether a transaction commits or aborts. [Distributed atomic commit](06%20Distributed%20Transactions.md) prevents a transaction from committing on only some participants.
- **Isolation:** Reads and conflicts across those participants obey the promised [isolation level](02%20Transaction%20Isolation.md). An all-or-nothing outcome does not by itself prevent incompatible concurrent decisions.
- **Real-time ordering:** [Strict serializability](03%20Read%20Consistency.md#Validity%2C%20Isolation%2C%20and%20Freshness) additionally requires the serial transaction order to respect non-overlapping transactions in real time. Serializability alone does not impose this freshness condition.

Two transactions might each have an atomic outcome yet jointly violate an invariant because both acted on outdated reads. Conversely, assigning both transactions an ordered timestamp does not establish that every participant durably accepted their outcomes.

## Coherent Cross-Partition Snapshots

A transaction reading several partitions needs a view permitted by its isolation contract. Independently reading each partition's latest available value does not establish a transaction-wide snapshot: another transaction might commit between the reads, or one replica might lag behind another.

With [MVCC](02%20Transaction%20Isolation.md#Multi-Version%20Concurrency%20Control), partitions retain multiple versions. A distributed snapshot uses a common visibility boundary, such as a read timestamp, to select compatible committed versions across partitions. The timestamp identifies the intended view; the read protocol must establish that the selected data is safe to return.

- **Committed visibility:** A reader must resolve or wait for relevant provisional writes rather than treating every stored version as committed.
- **Snapshot completeness:** A partition must establish that no still-unresolved transaction will subsequently commit a version belonging in the requested snapshot. A replica also needs the necessary updates applied locally.
- **Version retention:** Serving a historical snapshot requires retaining its versions; an older timestamp is not sufficient after the required history has been discarded.

These conditions distinguish choosing a snapshot from making that snapshot available. A partition that is behind the chosen boundary must wait, obtain the necessary state, or reject the read according to the database's protocol.

### Read-Only and Read-Write Transactions

- **Read-only transaction:** Has no writes to atomically commit across participants, but its reads still require a coherent view. A safe MVCC snapshot permits reads without locking against newer writes. Whether a read waits depends on snapshot availability and the requested freshness, not simply on being read-only. Spanner's timestamped read-only transactions illustrate this distinction. [Spanner paper](https://www.usenix.org/system/files/conference/osdi12/osdi12-final-16.pdf)
- **Read-write transaction:** Also needs its decisions to remain valid relative to concurrent transactions. Under distributed [snapshot isolation](02%20Transaction%20Isolation.md#Snapshot%20Isolation), a coherent snapshot and write-conflict detection still permit **write skew**: transactions read overlapping facts but update different items, even when those items reside on different partitions. Serializable isolation must prevent incompatible dependency cycles rather than only simultaneous writes to the same key. [Berenson et al.](https://15721.courses.cs.cmu.edu/spring2019/papers/02-transactions/p1-berenson.pdf)

## Concurrency Control Across Partitions

Local concurrency control must compose into one valid global history. For example, allowing transaction A to precede B on one partition while B precedes A on another can create a cycle that no serial order satisfies. A shared transaction identity, compatible ordering rules, and cross-participant conflict handling are therefore part of the distributed protocol.

### Distributed Locks and Two-Phase Locking

A **distributed lock** provides exclusion over a resource across nodes. **Two-phase locking (2PL)** is a rule governing a transaction's complete lock lifecycle:

1. During the growing phase, acquire locks without releasing any.
2. During the shrinking phase, release locks without acquiring new ones.

For transactions spanning partitions, the rule applies across all their locks, not independently to an arbitrary subset of operations on each partition. Serializable locking also requires protecting the relevant read predicates or key ranges, not only existing rows. Strict variants retain write locks until commit or abort, preventing other transactions from observing uncommitted writes.

- **Conflict waiting:** An incompatible request waits or causes a transaction to abort, according to the conflict policy.
- **Distributed deadlocks:** Transactions holding locks on different partitions can wait cyclically. Prevention, detection, or timeout policies must break the cycle.
- **Commit coupling:** A prepared participant that still holds locks continues blocking conflicts while the outcome is unresolved. Network delay therefore extends lock holding beyond local execution time.

> [!warning] Two different “two-phase” protocols
> 2PL governs conflicting access; [two-phase commit](06%20Distributed%20Transactions.md) governs agreement on commit or abort. Acquiring a distributed lock is not automatically 2PL, and completing 2PC is not automatically serializable isolation.

### MVCC and Optimistic Validation

MVCC supplies versions; it does not by itself specify which concurrent histories are allowed. **Optimistic concurrency control (OCC)** executes work before deciding whether conflicts permit commitment, trading less conflict waiting for discarded work when validation fails. The classical structure is read/compute, validate, then publish writes. [Kung and Robinson](https://www.eecs.harvard.edu/~htk/publication/1981-tods-kung-robinson.pdf)

A distributed implementation must coordinate validation with concurrent publication. Checking each participant at unrelated moments is insufficient if a conflicting transaction can invalidate a previously accepted check before commitment.

- **Read validation:** Establish whether the values and predicates used to make decisions remain compatible with the proposed serialization order.
- **Write validation:** Resolve incompatible writers and ensure provisional writes belong to the transaction's agreed outcome.
- **Timestamp advancement:** If the protocol moves a transaction to a later timestamp, earlier reads require validation at the new boundary; merely relabeling them does not make their results current.

If validation fails, the system aborts or restarts the transaction according to its protocol. Retrying recomputes decisions from a new valid view; resending only the final write preserves the invalid earlier decision. Under heavy contention, repeated validation failures waste work and increase latency.

## Timestamps and Distributed Clocks

A **timestamp** is an ordering or visibility label, not necessarily a measurement of wall-clock time. A database must specify how labels are assigned, compared, propagated, and enforced. Even globally unique, monotonically ordered timestamps do not detect every read/write dependency or decide a transaction's atomic outcome.

### Physical Time and Uncertainty

Physical clocks approximate real time but differ because of synchronization error and oscillator drift. A larger local clock reading on one machine does not alone prove that its event occurred later than an event on another machine.

An explicit uncertainty interval represents the range in which the actual time is believed to lie under the clock system's assumptions. Overlapping intervals do not establish a physical order. A protocol relying on bounded error must preserve that bound or stop making guarantees that require it; synchronizing clocks without a trustworthy error model is not equivalent to proving real-time ordering. [Logical Physical Clocks](https://cse.buffalo.edu/tech-reports/2014-04.pdf)

### Lamport Clocks

**Happened-before** captures causal order through local event order, message send-before-receive, and transitivity. Events are concurrent in this relation when neither precedes the other; this does not require simultaneous wall-clock execution.

A **Lamport clock** maintains a scalar counter. A process advances it for local events and sends it with messages; on receiving a message, it advances beyond both its own counter and the received counter.

- **Causal implication:** If event A happened before B, A receives a smaller clock value.
- **Missing converse:** A smaller value does not prove causality; unrelated events also receive comparable values.
- **Total-order extension:** A deterministic process-identity tie-breaker orders equal counters, producing a total order compatible with causality. That chosen order is not a measurement of elapsed time or proof of real-time precedence.

Logical order helps assign compatible labels, but a database still needs concurrency control to enforce a valid transaction history. [Lamport](https://research.cs.wisc.edu/areas/os/Qual/papers/lamport-clocks.pdf)

### Vector Clocks

A **vector clock** records logical progress for each tracked participant. A process increments its own component and merges received vectors component by component using the maximum.

- **Causality:** In the standard vector-clock model, one event causally precedes another exactly when its vector is componentwise no greater and strictly smaller in at least one component.
- **Concurrency:** Incomparable vectors identify events with neither causal ordering.
- **Metadata cost:** A full vector grows with the tracked participant set, unlike a scalar clock.

Vectors expose causal relationships rather than wall-clock time. Concurrent vectors do not choose which conflicting transaction should win; the transaction protocol must decide whether to order, wait, or abort. [Vector-time properties](https://www.cs.uic.edu/~ajayk/ext/IPL92.pdf)

### Hybrid Logical Clocks

A **hybrid logical clock (HLC)** combines a physical-time-derived component with a logical counter. Local events and received timestamps advance the pair without losing happened-before ordering when physical readings coincide or move backward. [HLC research](https://cse.buffalo.edu/tech-reports/2014-04.pdf)

- **Compact ordering:** HLC preserves the one-way causal implication of Lamport clocks without a vector per participant.
- **Physical association:** Its physical component stays near the underlying physical clock under the algorithm's assumptions; its logical component distinguishes events when that component does not advance.
- **Guarantee boundary:** HLC alone neither reconstructs full causality nor supplies a trustworthy bound on actual real time. External consistency requires additional protocol rules and assumptions.

> [!example] HLC timestamps do not replace validation
> CockroachDB uses hybrid logical clock timestamps for versions and transaction ordering. Its timestamp cache can push a writer forward; under serializable isolation, read refreshing checks whether earlier reads remain valid, and a failed refresh requires a retry. The timestamps, conflict machinery, and validation cooperate rather than independently establishing serializability. [Transaction layer](https://www.cockroachlabs.com/docs/stable/architecture/transaction-layer)

## TrueTime, Commit Wait, and External Consistency

**TrueTime** exposes uncertainty instead of presenting a physical timestamp as exact. Its `TT.now()` result contains `earliest` and `latest` bounds enclosing actual time, provided the implementation's error bounds hold. The Spanner design uses GPS and atomic-clock references to maintain these bounds; ordinary clients do not each require their own atomic clock. [Spanner paper](https://www.usenix.org/system/files/conference/osdi12/osdi12-final-16.pdf)

Serializable concurrency control establishes a valid serial order; **strict serializability** additionally constrains that order by real time. Spanner combines these requirements when assigning commit timestamps:

1. Select a commit timestamp no earlier than the relevant `TT.now().latest`, also respecting participant and transaction-order constraints.
2. Perform **commit wait** until `TT.now().earliest` is greater than the commit timestamp, before reporting successful completion.
3. A subsequent externally consistent read-write transaction selects a later commit timestamp because the earlier timestamp is now definitely in the past.

The uncertainty wait connects timestamp order to observed real-time order. Larger uncertainty increases the required waiting. With serializable concurrency control, this supports **external consistency**: the serial order respects externally observed transaction completion. This is a transaction-level guarantee, not merely synchronized clocks or independent fresh reads. [TrueTime and external consistency](https://docs.cloud.google.com/spanner/docs/true-time-external-consistency)

Strong reads begun after that completion observe the committed transaction. Stale reads deliberately select an older snapshot and do not promise this freshness, even though their snapshot remains coherent. [Timestamp bounds](https://docs.cloud.google.com/spanner/docs/timestamp-bounds)

Commit wait does not discover conflicts, replicate a decision, or force every participant to commit. Spanner combines clock-based ordering with locking, versioned reads, and an atomic commit protocol. Accurate clocks reduce ambiguity about time; they do not remove agreement about outcomes or enforcement of isolation.
