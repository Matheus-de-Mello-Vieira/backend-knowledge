# Distributed Concurrency

A local database transaction can provide one atomic and isolated boundary around several reads and writes. Distributed workflows become harder when one logical business operation spans **multiple services, databases, queues, or external systems** because there is no longer one concurrency-control boundary covering the whole operation.

Consider an order workflow that must:

1. create the order;
2. reserve inventory;
3. charge the customer;
4. arrange delivery.

Each step may be individually transactional inside its own service, but the complete workflow cannot usually be protected by one local [transaction isolation](../../Databases/02%20Transaction%20Isolation.md) boundary. Between those local commits, other actors can observe and modify the same business state.

Distributed concurrency is therefore concerned with preserving **business invariants across independently executing and independently failing components**.

The problem combines two sources of uncertainty:

- **Concurrency:** another workflow may change relevant state while this workflow is still in progress.
- **Partial failure:** one step may succeed while another fails, times out, or becomes unreachable.

A distributed design must therefore decide how intermediate state becomes visible, how conflicting workflows coordinate, how partially completed work is compensated, and how repeated messages or requests are prevented from repeating side effects.

## Local Transactions Do Not Create a Distributed Transaction

Suppose an order service and an inventory service use separate databases.

Initially:

```text
Order 42     = pending
Product X    = 1 unit available
```

Two order workflows try to reserve the last unit.

| Time | Workflow A | Workflow B | Inventory state |
| --- | --- | --- | --- |
| `t0` | Reads product as available | — | `1 available` |
| `t1` | — | Reads product as available | `1 available` |
| `t2` | Requests reservation | — | `1 available` |
| `t3` | — | Requests reservation | `1 available` |
| `t4` | Inventory commits reservation for A | — | `0 available` |
| `t5` | — | Inventory rejects B | `0 available` |

The inventory service can protect its own invariant atomically, for example through [pessimistic or optimistic concurrency control](01%20Concurrency%20Fundamentals.md#Concurrency%20Control%20Strategies). The order service does not need direct access to the inventory database to obtain that protection.

However, that local atomicity does not make the entire order workflow atomic. Workflow A may successfully reserve inventory and then fail before payment succeeds. The system now contains an intentionally intermediate state that must eventually be completed or reversed.

This is the central distinction:

> **Local transaction isolation protects one transactional resource. Distributed coordination protects a business operation that crosses several transactional resources.**

## Sagas

A **Saga** represents a long-running business operation as a sequence of independently committed local transactions.

Instead of attempting one atomic transaction across every participant, each step commits its own state. If a later step fails, the Saga executes **compensating actions** for earlier steps where compensation is possible.

For an order:

```text
create order
reserve inventory
charge payment
arrange delivery
```

the compensating actions might be:

```text
cancel order
release inventory
refund payment
cancel delivery
```

A compensation is not a database rollback. The original transaction already committed and may already have been observed by other actors. Compensation is a **new business operation** that attempts to counteract the earlier effect.

### Intermediate State Is Real State

Because Saga steps commit independently, intermediate states are visible.

Suppose inventory is reserved before payment completes.

| Time | Order Saga | Another customer | Inventory state |
| --- | --- | --- | --- |
| `t0` | Reserves last unit | — | `reserved` |
| `t1` | Begins payment | Tries to buy same product | `reserved` |
| `t2` | Payment fails | Cannot reserve product | `reserved` |
| `t3` | Releases inventory as compensation | — | `available` |

The other customer was affected by a state belonging to a Saga that ultimately failed.

This is not necessarily incorrect. The reservation may be exactly the intended concurrency-control mechanism. What matters is that the intermediate state has explicit business semantics rather than being treated as though the whole Saga were isolated.

A Saga therefore requires the application to decide **which intermediate states may be externally visible and what they mean**.

## Compensation Is Not Rollback

A local transaction can usually roll back because its uncommitted changes were never made part of the committed database state.

A distributed compensation happens after an earlier step has already committed.

For example:

```text
charge customer → committed
shipping fails
refund customer → new operation
```

The refund does not erase the original charge from history. Both operations happened. They may appear separately in financial records, audit logs, notifications, and external systems.

Compensation can also fail and may itself need retries.

Some effects may not be perfectly reversible at all. An email cannot be "unsent", a package may already have left a warehouse, and a market order may have changed the external world before compensation begins.

For that reason, Saga design should distinguish:

- **reversible operations**, where a meaningful compensating action exists;
- **retriable operations**, where failure can be resolved by trying again;
- **irreversible operations**, which should often be delayed until the workflow has reached a point where executing them is acceptable.

## Concurrent Sagas

Sagas solve partial completion, but multiple Sagas can still interfere with one another.

Suppose two workflows both read an entity before either modifies it.

Initially:

```text
booking.status = available
```

| Time | Saga A | Saga B | Booking state |
| --- | --- | --- | --- |
| `t0` | Reads `available` | — | `available` |
| `t1` | — | Reads `available` | `available` |
| `t2` | Attempts reservation | — | `available` |
| `t3` | — | Attempts reservation | `available` |

If reservation is implemented as a blind write, both workflows may believe they succeeded.

The same [optimistic concurrency](01%20Concurrency%20Fundamentals.md#Optimistic%20Concurrency%20Control) rule still applies: the final validation and state transition must share one atomic boundary.

For example, the owning service can perform an atomic conditional write:

```sql
UPDATE bookings
SET status = 'reserved'
WHERE id = 123
  AND status = 'available';
```

Only one workflow can change the expected state from `available` to `reserved`. The other observes that zero rows were modified and must react to the conflict.

Distributed architecture therefore does not remove local concurrency control. Instead, **each service protects the invariants it owns locally, while the workflow coordinates the consequences across services**.

## Semantic Locks

Sometimes an intermediate business state can act as a **semantic lock**.

A database mutex says that another transaction cannot access some protected state. A semantic lock expresses the restriction through domain state that other workflows understand.

For example:

```text
order.status = PAYMENT_PENDING
```

may mean that another workflow is not allowed to cancel or fulfill the order until payment reaches a terminal state.

The state is visible rather than hidden behind a long-lived database lock. Other services can inspect it and decide which operations are currently valid.

Semantic locks are useful for workflows that may take seconds, minutes, or longer because holding a database lock across network calls would create tight coupling and potentially severe contention.

However, semantic locks must have explicit recovery rules. If the workflow crashes while an entity remains `PAYMENT_PENDING`, the system needs a timeout, reconciliation process, or other recovery mechanism that can determine what should happen next.

## Failure Ambiguity

Distributed calls have a fundamental ambiguity: **a missing response does not reveal whether the remote operation happened**.

Suppose a client sends a payment request.

| Time | Client | Payment service |
| --- | --- | --- |
| `t0` | Sends `charge $100` | — |
| `t1` | — | Receives request |
| `t2` | — | Charges `$100` successfully |
| `t3` | Waiting for response | Sends success response |
| `t4` | Connection fails before response arrives | — |

From the client's perspective, the result is unknown.

The request may have:

- never reached the service;
- reached the service but failed before executing;
- succeeded while the response was lost;
- still be executing.

A timeout can therefore tell the caller **that it stopped waiting**, but not whether the remote side effect occurred.

This is why retries and idempotency are tightly connected.

## Idempotency

An operation is **idempotent** when repeating the same intended operation does not produce additional business effects after the first successful application.

For example:

```text
increase(1)
```

is not naturally idempotent:

| Attempt | Value before | Value after |
| --- | ---: | ---: |
| first | `10` | `11` |
| retry | `11` | `12` |

Every execution adds another effect.

By contrast:

```text
set(5)
```

is naturally idempotent:

| Attempt | Value before | Value after |
| --- | ---: | ---: |
| first | `10` | `5` |
| retry | `5` | `5` |

Repeating the operation does not compound the state change.

Idempotency is particularly important in distributed systems because retries are often necessary precisely when the result of the previous attempt is unknown. An idempotent interface lets a caller retry without first proving whether the previous attempt completed.

### Idempotency Is About the Logical Operation

Idempotency does not mean that literally nothing changes when an operation is repeated.

A repeated request may still:

- create access logs;
- update metrics;
- perform authentication;
- consume CPU and network resources;
- refresh bookkeeping timestamps.

The important property is that the **intended business effect is not applied again**.

Likewise, two requests with identical payloads are not necessarily retries of the same logical operation. A customer may intentionally buy the same product twice. The system therefore often needs an explicit identity for the operation rather than deduplicating requests merely because their contents look similar.

## Idempotency Keys

A naturally non-idempotent operation can be made idempotent by assigning a stable identifier to the **logical operation**.

For an HTTP API, the client may send:

```http
POST /payments
Idempotency-Key: 8df7c8a4-...
```

The first request executes normally. The server records that the key represents this payment operation and stores enough information to recognize future retries.

A repeated request using the same key is then treated as another delivery of the **same operation**, not as a new payment.

Conceptually:

| Time | Client                              | Server                                          |
| ---- | ----------------------------------- | ----------------------------------------------- |
| `t0` | Sends operation with key `K`        | —                                               |
| `t1` | —                                   | Atomically claims `K`                           |
| `t2` | —                                   | Performs business operation                     |
| `t3` | Response is lost                    | Records result for `K`                          |
| `t4` | Retries with key `K`                | —                                               |
| `t5` | —                                   | Finds existing `K`; does not repeat side effect |
| `t6` | Receives original/equivalent result | —                                               |
|      |                                     |                                                 |

The key must remain stable across retries. Generating a new key for every network attempt defeats the mechanism because the server can no longer distinguish a retry from a genuinely new operation.

### The Idempotency Record Must Be Atomic

The deduplication mechanism introduces its own concurrency problem.

This is unsafe:

```text
if key does not exist:
    // another request with the same key can arrive here
    execute operation
    store key
```

Two concurrent deliveries can both observe that the key is absent and both execute the side effect.

The server therefore needs an atomic boundary that ensures only one actor can successfully claim a key.

For example, a database table can enforce a unique constraint:

```sql
INSERT INTO idempotency_keys (key, status)
VALUES ('K', 'processing');
```

If `key` is unique, only one concurrent request can create the record. Other requests receive a uniqueness conflict and can inspect the existing operation instead of executing a duplicate.

The same principle can be implemented using an atomic conditional write in another database.

This follows the same rule described in [Optimistic Concurrency Control](01%20Concurrency%20Fundamentals.md#Optimistic%20Concurrency%20Control): **validation and state transition must happen atomically**.

### Idempotency Key Scope

An idempotency key needs a well-defined scope.

The system must know what uniqueness means, for example:

```text
(customer, idempotency_key)
```

or:

```text
(API operation, idempotency_key)
```

A globally unique key may also be used.

The important property is that two unrelated operations must not accidentally collide while retries of the same operation resolve to the same identity.

The server should also associate the key with the original operation's relevant parameters. If the same key is later reused with a materially different request, silently returning the old result can hide a client bug. A common policy is to reject reuse of the key with different parameters.

### Storing the Result

Deduplication is stronger when the server stores the outcome associated with the key, not merely that the key was seen.

For example:

```text
K → succeeded → payment_id=456
```

A retry can then return the original result instead of merely saying that the duplicate was ignored.

The record may need to represent several states:

```text
processing
succeeded
failed
```

A concurrent retry that sees `processing` should not start the operation again. It may wait, return a retryable response, or query the operation later depending on the API design.

An API may also explicitly indicate that a response came from a previous execution, for example with an implementation-specific header such as:

```http
Idempotency-Replayed: true
```

This is not required for idempotency itself; it is only a diagnostic or API-level signal that the server recognized the request as a retry.

### Naturally Idempotent Write Patterns

Not every idempotent write requires a separate idempotency-key table.

An **upsert-style write** can be naturally idempotent when it deterministically converges on the same state. For example:

```sql
INSERT INTO user_preferences (user_id, theme)
VALUES (123, 'dark')
ON CONFLICT (user_id)
DO UPDATE SET theme = 'dark';
```

Repeating the same logical operation does not create additional preference records or compound the effect; the state converges on `theme = 'dark'`.

The same idea applies to set-like operations such as:

```text
set status = CLOSED
ensure membership exists
replace configuration with version V
```

Whether such an operation is truly idempotent depends on its **business semantics**, not merely on the database syntax. An upsert that increments a counter or appends another child record on every conflict would still be non-idempotent.

### Idempotency Retention

Idempotency records cannot necessarily be stored forever.

Systems often retain keys for a bounded period. After expiration, the same key may be treated as new.

That retention period becomes part of the API's semantics: a retry is protected only while the server still remembers the logical operation.

The appropriate duration depends on how long delayed or repeated deliveries may realistically occur and how expensive duplicate execution would be.

## HTTP Method Idempotency

HTTP defines idempotency as a property of the **intended effect of repeating a request method**.

Methods such as `GET`, `PUT`, and `DELETE` are defined to have idempotent semantics. `POST` is not idempotent by default.

For example, repeating:

```http
PUT /users/123/preferences
```

with the same complete representation can naturally converge on the same intended state.

Repeating:

```http
POST /payments
```

may create a second payment unless the application adds an idempotency mechanism.

HTTP method semantics help clients and intermediaries reason about retries, but they do not automatically make the underlying application correct. A handler for an idempotent method must still implement idempotent business semantics, and naturally non-idempotent operations may need an application-level idempotency key.

## `If-Match`, `If-None-Match`, and Idempotency

Conditional HTTP requests solve a related but different concurrency problem.

An `Idempotency-Key` answers:

> **Have I already executed this logical operation?**

`If-Match` answers:

> **Is the resource still in the version I previously observed?**

For example:

```http
PUT /documents/123
If-Match: "v7"
```

prevents a stale client from blindly overwriting version `"v8"`.

`If-None-Match: *` can express create-if-absent semantics:

```http
PUT /documents/123
If-None-Match: *
```

which succeeds only when a current representation does not already exist.

These mechanisms are forms of optimistic concurrency control, while idempotency handles duplicate execution. They are complementary: a request can need both a version precondition and an idempotency key.

## Message Delivery and Duplicate Processing

Asynchronous systems have the same [failure ambiguity](#Failure%20Ambiguity) as request-response communication, but it can appear on **both sides of the broker**.

On the producer side, the application needs confirmation that responsibility for a message successfully moved to the broker. If the broker accepts a message but its confirmation is lost, the producer cannot distinguish that case from one in which the message never reached the broker.

| Time | Producer | Broker |
| --- | --- | --- |
| `t0` | Sends `M1` | — |
| `t1` | — | Accepts `M1` |
| `t2` | Waits for confirmation | Sends confirmation |
| `t3` | Connection fails before receiving it | Already accepted `M1` |
| `t4` | Retries `M1` | Receives the publication again |

The retry happens because the result is **ambiguous**, not because the producer knows that the original publication failed.

Some brokers can recognize particular producer retransmissions and avoid storing another copy. This is another form of idempotency, but its identity belongs to the messaging protocol rather than to the business operation. It does not determine whether two independent publications represent the same logical purchase, payment, or order.

On the consumer side, the broker must determine whether a delivered message was successfully processed. If processing cannot be confirmed, reliable messaging systems commonly make the work available again rather than risk losing it. This deliberately introduces the possibility of duplicate processing.

### Queue-Based Redelivery

In queue-oriented messaging, delivering a message usually gives a consumer temporary responsibility for processing it. The broker keeps enough state to determine that processing has not yet been confirmed.

If completion is not confirmed, the message can become eligible for delivery again. Different brokers determine this point differently.

> [!example] SQS and RabbitMQ
> **Amazon SQS** temporarily hides a received message from other consumers. If the consumer does not complete processing and remove the message before this visibility period expires, the message becomes visible and can be delivered again.
>
> **RabbitMQ** instead tracks whether a delivery has been acknowledged. If a consumer disappears while a message remains unacknowledged, or explicitly asks for it to be requeued, the message can be delivered again.
>
> Both mechanisms solve the same problem: the broker cannot assume that delivering a message means its business effect completed successfully.

Suppose a consumer processes `M1` and commits its business effect, but fails before confirming completion to the broker.

| Time | Consumer | Broker |
| --- | --- | --- |
| `t0` | Receives `M1` | Considers `M1` in progress |
| `t1` | Commits business effect | Waits for completion |
| `t2` | Crashes before confirming completion | Still considers delivery incomplete |
| `t3` | — | Makes `M1` eligible for delivery again |
| `t4` | Receives `M1` again | — |

The broker faces a fundamental trade-off. If it assumes success, it can lose work that actually failed. If it retries, it can repeat work that actually succeeded. **At-least-once delivery chooses the second trade-off:** preserve the work even if duplicate processing must be tolerated.

Without deduplication, the business effect can therefore occur twice. The consumer can instead treat the message ID as an [idempotency key](#Idempotency%20Keys) and atomically record that the logical message has already been applied.

### Log-Based Replay

Log-oriented messaging uses a different model. Consuming a message does not necessarily remove it from the broker. Messages remain in an ordered log, while consumers separately record how far through that log they have successfully processed.

If a consumer applies a business effect but fails before recording its new progress, a later consumer can resume from the older position and process the same message again.

| Time | Consumer | Business state | Recorded progress |
| --- | --- | --- | --- |
| `t0` | Reads `M1` | Unchanged | Before `M1` |
| `t1` | Applies business effect | Changed | Before `M1` |
| `t2` | Crashes | Changed | Before `M1` |
| `t3` | Restarts | Changed | Before `M1` |
| `t4` | Reads `M1` again | Effect may repeat | Before `M1` |

Kafka is a common example of this model. It records consumer progress using **offsets**. The message itself does not need to be requeued: it remained in the log, and the consumer simply resumes from a position from which that message is still visible.

> [!example] Kafka Producer Idempotency
> Kafka can distinguish a producer retry from a new publication by associating publications with a producer identity and sequence information. If the producer retransmits the same publication because its acknowledgement was lost, Kafka can recognize the retransmission instead of appending another copy.
>
> This is different from an application-level [idempotency key](#Idempotency%20Keys). Two explicit publications from the application are still two messages, even if their payloads are identical. Kafka cannot infer whether they mean “retry purchase A” or “the customer bought the same product again.” That distinction requires a business identity such as an order or payment ID.

Queue redelivery and log replay therefore reach the same application-level consequence through different transport mechanisms: **the same logical operation may be processed more than once**. This is why at-least-once messaging requires idempotent processing or equivalent deduplication whenever duplicate effects are unsafe.

## Atomic Business Update and Deduplication

A subtle failure remains if the consumer stores the deduplication record separately from the business effect.

This sequence is unsafe:

```text
write business state
crash
write processed-message record
```

A crash between the two writes leaves the business effect committed without the deduplication marker. Redelivery repeats the effect.

Reversing the order is also unsafe:

```text
write processed-message record
crash
write business state
```

Now redelivery sees the marker and skips a business effect that never happened.

When both records live in the same transactional database, the strongest design is to commit them in **one local transaction**:

```text
transaction:
    verify/claim message ID
    modify business state
    record message as processed
commit
```

This creates one atomic boundary between deduplication and the side effect.

When the business effect belongs to an external system that cannot participate in the same local transaction, the problem becomes a distributed workflow again and requires protocol-level coordination, reconciliation, or an idempotency guarantee from that external system.

## Transactional Outbox

A common distributed failure occurs when one local transaction must both modify database state and publish a message.

This is unsafe:

```text
commit database
publish event
```

because the process may crash after the database commit but before publishing.

This is also unsafe:

```text
publish event
commit database
```

because the database transaction may later fail after the event has already escaped.

The **Transactional Outbox** pattern stores the business change and an outgoing message record in the same local database transaction:

```text
transaction:
    modify business state
    insert outbox record
commit
```

A separate publisher reads committed outbox records and sends them to the broker.

The publisher may send an outbox message more than once if it crashes around acknowledgment, so downstream consumers must still tolerate duplicate delivery.

The outbox does not create exactly-once execution across the whole distributed system. It transforms a difficult cross-system atomicity problem into:

1. one local atomic database transaction;
2. reliable eventual publication;
3. idempotent or deduplicated consumption.

## Inbox / Processed-Message Pattern

The receiving side can apply the symmetric **Inbox** or **Processed Message** pattern.

The consumer records a unique message identifier in the same transaction as the business update:

```text
transaction:
    insert message ID if absent
    apply business change
commit
```

If the broker later redelivers the same message, insertion of the duplicate message ID fails or the existing record is found, and the business update is not repeated.

This is application-level exactly-once **effect** for the protected local state even when the transport itself delivers at least once.

The guarantee is only as broad as the atomic boundary. If one consumer action also calls an external service, that external side effect still needs its own idempotency or coordination mechanism.

## Exactly-Once Delivery vs. Exactly-Once Effect

The phrase **exactly once** is easy to misinterpret.

A network cannot generally prevent every duplicate transmission while also recovering transparently from all ambiguous failures. Messages and requests may be retried because neither side can always know what the other side observed before a failure.

What applications usually need is not "the bytes were delivered exactly once", but:

> **the logical business effect is applied exactly once despite possible duplicate delivery.**

Idempotency keys, unique constraints, transactional inboxes, conditional writes, and deduplication records are mechanisms for achieving that property within a defined state boundary.

The distinction is important because a transport can redeliver a message while the application still produces only one durable effect.

## Retries

Retries are a resilience mechanism: a transient failure may disappear on the next attempt.

But a retry is also a **new concurrent attempt against a system whose previous state may be unknown**.

Before automatically retrying a state-changing operation, the caller should know how duplicate execution is controlled.

A retry is straightforward when:

- the operation is naturally idempotent;
- the request carries an idempotency key;
- the write is conditional on an expected state;
- the downstream system exposes another explicit deduplication guarantee.

Without one of those mechanisms, retrying after an ambiguous failure can trade an availability problem for a correctness problem.

Retries also increase load. During an outage, many callers retrying aggressively can amplify pressure on an already degraded dependency. Backoff, jitter, retry limits, and circuit breaking therefore remain resilience concerns even when the underlying operation is idempotent.

Idempotency makes a retry **safe from duplicate business effects**; it does not make unlimited retries operationally safe.

## Reconciliation

Distributed workflows should assume that unusual combinations of partial failure will eventually occur.

A **reconciliation process** compares actual state against expected business invariants and repairs or escalates discrepancies.

For example, it may find:

```text
order = PAID
inventory = RESERVED
shipment = missing
```

and determine that shipment creation should be retried.

Reconciliation is different from synchronous compensation. Compensation is part of the normal workflow for a known failed step; reconciliation detects state that remained inconsistent because the normal workflow itself failed to finish correctly.

Durable workflow state, operation identifiers, timestamps, and audit records make reconciliation possible because they provide enough evidence to determine which actions already occurred.

## Distributed Concurrency Is About Business Invariants

A distributed system cannot rely on one global lock or one local ACID transaction to make every business operation appear instantaneous.

Instead, correctness is usually composed from several smaller guarantees:

- each service protects the state and invariants it owns;
- concurrent updates use pessimistic or optimistic concurrency control where appropriate;
- long-running workflows expose explicit intermediate states;
- failures trigger retries or compensating actions;
- duplicate deliveries are made harmless through idempotency or deduplication;
- local database changes and message publication are connected through patterns such as the outbox;
- reconciliation repairs states that escape the normal workflow.

The central design question is therefore:

> **Which business invariants must hold immediately, which may be temporarily violated, and what mechanism eventually restores or confirms them?**

Local [transaction isolation](../../Databases/02%20Transaction%20Isolation.md) remains essential inside each transactional boundary, but distributed correctness comes from deliberately coordinating the boundaries rather than pretending they form one transaction.
