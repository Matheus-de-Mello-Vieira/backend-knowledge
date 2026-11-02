# Redis Transactions

A Redis transaction groups commands for sequential execution without requests from other clients interleaving between them. `MULTI` starts queueing commands on a connection; `EXEC` submits that queue for execution. This isolation does **not** imply rollback: a command that fails during execution does not undo successful commands in the group. [Redis transaction semantics](https://redis.io/docs/latest/develop/using-commands/transactions/).

## Queueing and execution

The transaction lifecycle belongs to one connection:

1. **Enter with `MULTI`:** Redis replies `OK` and enters transaction mode.
2. **Queue commands:** Accepted commands reply `QUEUED`, not their eventual results. They have not changed the dataset yet. Other clients continue operating while this connection builds its queue.
3. **Execute with `EXEC`:** Unless an error or a failed `WATCH` check prevents execution, Redis runs the queued commands in order without serving another client's request between them. It returns an array containing one reply per command, in queue order, and leaves transaction mode.

`DISCARD` instead clears the unexecuted queue and exits transaction mode. It is cancellation before execution, not rollback afterward. If the connection closes before `EXEC` is sent, the queued commands are never executed. [Transaction lifecycle](https://github.com/redis/docs/blob/main/content/develop/using-commands/transactions.md).

For example, assume `visits` does not exist. On one connection, start the transaction and queue an increment followed by a read:

```text
> MULTI
OK
> INCR visits
QUEUED
> GET visits
QUEUED
```

Neither command has run yet. `EXEC` performs the increment first, then reads its result with no other client's command between those operations:

```text
> EXEC
1) (integer) 1
2) "1"
```

These exact results assume no other client changes `visits` before `EXEC`. Queueing itself does not reserve or lock the key. A read queued after `MULTI` also cannot supply a value for a client-side decision while building that same queue: its result arrives only with `EXEC`.

## Errors and the absence of rollback

The stage at which an error occurs determines its effect:

- **Queue-time errors:** An unknown command or an incorrect argument count prevents a command from being queued. In Redis 2.6.5 and later, such an error marks the transaction for rejection: `EXEC` returns an error and executes none of the queued commands.
- **Execution-time errors:** A syntactically valid command can fail against the dataset, such as a list operation on a string key. Its error appears in the `EXEC` reply array; the other queued commands still execute. Redis does not reverse earlier changes or skip later commands because of that failure.

For example, `LPUSH` is valid when queued, but fails after the preceding `SET` makes `item` a string. The later `SET` still runs:

```text
> MULTI
OK
> SET item "text"
QUEUED
> LPUSH item "x"
QUEUED
> SET marker "done"
QUEUED
> EXEC
1) OK
2) (error) WRONGTYPE Operation against a key holding the wrong kind of value
3) OK
```

The first write remains in place, and `marker` becomes `"done"`; the error neither rolls back the first command nor stops the third.

An `EXEC` reply array therefore needs per-command inspection; receiving it is not proof that every command succeeded. Validate application assumptions rather than treating Redis transactions as an all-or-nothing rollback mechanism. [Redis transaction error handling](https://github.com/redis/docs/blob/main/content/develop/using-commands/transactions.md#errors-inside-a-transaction).

## Optimistic updates with `WATCH`

`MULTI` alone does not protect a value read before queueing begins. Another client could change it before `EXEC`, making a client-computed update stale. `WATCH` provides **optimistic check-and-set**: monitor the keys used for a decision, then execute the queued update only if none was modified in the meantime. It detects conflicts rather than blocking other writers. [Redis optimistic locking](https://github.com/redis/docs/blob/main/content/develop/using-commands/transactions.md#optimistic-locking-using-check-and-set).

Use the same connection throughout this sequence:

1. Issue `WATCH` for every key whose state the decision depends on, **before reading** those keys.
2. Read their current values and compute or validate the proposed update in the client.
3. Issue `MULTI` and queue the update commands.
4. Issue `EXEC`. If a watched key changed, Redis returns a null reply and executes none of the queue; otherwise it executes the queue normally.
5. On a watch conflict, start again with `WATCH`, reread the values, and recompute the decision. Reusing the old computed update defeats the check.

Assume `counter` initially holds `10`. Client A plans to write `11`, but client B changes the watched key before A executes its queue (shown with RESP2-style replies):

```text
Client A> WATCH counter
OK
Client A> GET counter
"10"
Client B> INCR counter
(integer) 11
Client A> MULTI
OK
Client A> SET counter 11
QUEUED
Client A> EXEC
(nil)
```

A's `SET` does not run. To retry the increment, A must watch and read `counter` again, then compute `12` from its current value of `11`; replaying the stale write would leave the counter at `11` instead of applying A's increment.

The conflict check concerns changes, not just equality of the final value. The client must distinguish a null conflict result from an executed transaction containing an individual command error.

- **Watch cleanup:** `EXEC` clears watched keys whether it executes or aborts. `DISCARD` also clears them; `UNWATCH` explicitly clears watches when abandoning a decision before `MULTI`. Closing the connection clears its watches.
- **Retry responsibility:** Redis does not retry the application decision. The client controls retries and their limits; concurrent updates can cause repeated conflicts.

These connection-scoped states require keeping a pooled connection assigned to the operation until transaction and watch state have been cleared. [Redis watch lifecycle](https://github.com/redis/docs/blob/main/content/develop/using-commands/transactions.md#watch-explained).

## Transactions versus pipelining

[Pipelining](Mass%20Insertion%20of%20Data%20-%20Piping.md) sends commands without waiting for each preceding reply, reducing round-trip overhead. A plain pipeline does not establish the no-interleaving execution boundary supplied by `MULTI` and `EXEC`.

The mechanisms are complementary: a client can pipeline transaction commands to reduce transport waits, but the transaction semantics come from the Redis commands, not from batching bytes. Client libraries differ in whether their pipeline abstraction also wraps commands in a transaction; inspect the selected client's behavior rather than inferring atomic execution from the word “pipeline.” [Redis pipelining](https://redis.io/docs/latest/develop/using-commands/pipelining/).

## Persistence and deployment constraints

- **Durability:** A successful `EXEC` is not an unconditional guarantee that the changes survive a crash. The configured [persistence mode and synchronization policy](../05%20Architecture%20and%20Reliability/Persistence.md) determine local crash recovery; transaction isolation does not replace those durability mechanisms.
- **Redis Open Source Cluster:** Keys involved in a transaction, including watched keys, must share a [hash slot](../05%20Architecture%20and%20Reliability/Distributed%20Redis.md#Partitioning%20and%20key%20locality). `MULTI`/`EXEC` does not provide a cross-shard transaction. Related hash tags support this locality requirement, at the cost of concentrating those keys on one partition. [Redis multi-key constraints](https://redis.io/docs/latest/develop/using-commands/multi-key-operations/).
