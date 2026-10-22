# Transactions

A **database transaction** groups database operations into one logical unit of work. Its boundaries identify which reads and changes belong to the same operation, rather than treating each query as an independently completed task.

## Transaction Lifecycle

Executing the queries and completing the transaction are different stages. A successful update inside an unfinished transaction is not yet a committed result.

1. **Begin:** Establish the transaction boundary (`BEGIN`).
2. **Execute:** Perform reads and, for a read-write transaction, changes while the transaction is active.
3. **Complete:** End the unit of work with one of two outcomes:
    - **Commit:** Accept the transaction's work as a completed result. `COMMIT` requests this outcome; successful commit completes it.
    - **Abort:** End without accepting the transaction's changes. `ROLLBACK` explicitly requests that those changes be discarded.

## Atomicity

**Atomicity** gives a transaction an all-or-nothing outcome: successful commit accepts its changes together; abort discards all of its changes. An earlier successful statement is not independently completed work that survives the transaction's abort. This lets several database changes represent one operation without accepting only part of it.

> [!warning] Statement failure and transaction abort
> A statement error does not universally trigger automatic rollback of the entire transaction: the response depends on the database system and error. Once a transaction aborts, however, all of that transaction's changes are discarded, including changes from earlier successful statements.

The same guarantee applies when a database crashes before commit. [Crash recovery](00%20Overview.md#Write-Ahead%20Logging%20%28WAL%29) accounts for incomplete transactions after restart so their changes do not leave a partial committed transaction. This does not require the application to issue a literal `ROLLBACK` during the crash.

> [!example] Account transfer
> Transferring $100 from an account holding $1,000 to one holding $500 requires reading the source balance, debiting the source, and crediting the destination. The application requires the transfer to preserve the combined balance of $1,500, so the debit and credit belong to one transaction.
>
> If the database crashes after the debit but before the credit, accepting balances of $900 and $500 after restart would lose $100 from that total. Recovery must discard the incomplete transaction's changes, leaving $1,000 and $500. Successful commit instead accepts $900 and $600 together.

## Consistency and Application Invariants

An **invariant** is a rule that defines a valid database state and must remain true across completed transactions. **ACID consistency** means that correctly designed transactions take valid data to valid data, preserving the declared validity rules. Transactions do not automatically make incorrect application logic valid.

Validity rules differ in how they are enforced:

- **Database-enforced constraints:** The database rejects changes that violate declared constraints, such as duplicate primary keys or invalid foreign-key references.
- **Application-maintained rules:** Transaction logic must preserve rules that are not enforced by database constraints, such as agreement between a stored total and the detail records it summarizes.

For pictures and their likes, keys express identity and valid references:

- **Primary key:** A column or set of columns that uniquely identifies each row; primary-key values are not null. A picture's `id` identifies that picture.
- **Composite primary key:** A primary key made of multiple columns whose combined values are unique. In the likes records, `(user, picture_id)` identifies a unique like, allowing at most one like from a given user for a given picture.
- **Foreign key:** A constraint requiring a reference to match an existing referenced key. A like's `picture_id` references the picture's `id`, so the referenced picture must exist. This relationship enforces **referential integrity**.

If the application requires a picture's stored likes count to equal the number of its like records, that agreement is another invariant. A foreign key checks whether a referenced picture exists, not whether its stored count matches those records.

> [!example] Two different integrity failures
> A picture-sharing application stores pictures in `Pictures`, with an `id` and a stored likes count. A separate `Picture_Likes` table records each like as `(user, picture_id)`. Each like must reference an existing picture, and the application requires each picture's count to equal the number of its like records.
>
> Suppose only pictures 1 and 2 exist, but the stored data contains two errors:
>
> - **Count mismatch:** Picture 1 reports five likes, but its detail records contain only `(Jon, 1)` and `(Edmond, 1)`: the stored count and detail records disagree.
> - **Dangling reference:** A further like, `(Edmond, 4)`, references nonexistent picture 4 and violates referential integrity.
>
> An enforced foreign key rejects the reference to picture 4, but it does not enforce agreement between picture 1's count and its two like records. The count rule needs its own enforcement, such as application logic that updates the count and detail records together.

Preserving an invariant requires both correct transaction logic and guarantees that support that logic:

- **Atomicity:** Updating a like record and its stored count in one transaction prevents accepting only one of those related changes. Accepting both changes still produces invalid data if the logic computes the wrong count.
- **Isolation:** Concurrent transactions must execute under isolation guarantees appropriate to the invariant. Merely wrapping each operation in a transaction is insufficient when concurrent decisions interfere; [write skew](02%20Transaction%20Isolation.md#Write%20Skew) illustrates how an invariant fails despite each transaction's logic being valid in isolation.

ACID consistency concerns validity rules, not [read freshness](03%20Read%20Consistency.md): preserving invariants does not by itself guarantee that a read sees the latest committed data.

## Read-Only and Read-Write Transactions

A transaction's scope is not defined by whether it changes data:

- **Read-write transaction:** Reads and modifies database data as one unit of work, such as an account transfer.
- **Read-only transaction:** Reads without modifying database data, such as the queries used to generate a report.

A report assembled from several queries needs a coherent view if its detail rows and totals must describe the same database state. Concurrent commits between those queries would otherwise let them describe different moments.

Being read-only, or merely wrapping queries in a transaction, does **not** guarantee a transaction-wide stable snapshot. That guarantee depends on the database's isolation behavior. Under [snapshot isolation](02%20Transaction%20Isolation.md#Snapshot%20Isolation), reads use a consistent snapshot rather than incorporating other transactions' later commits into that view.
