# Redis Streams

A **Redis Stream** is an ordered sequence of retained entries. Each entry has an ID and field–value pairs. Producers append entries; readers use IDs to resume from a position, and consumer groups coordinate work across consumers. Unlike [Pub/Sub](PublishSubscribe%20Model.md#Delivery%20model), which pushes messages only to current subscribers, a stream keeps entries until they are deleted or trimmed. Retention makes later reads possible, but does not itself guarantee durability or indefinite availability. [Redis Streams](https://redis.io/docs/latest/develop/data-types/streams/)

The command transcripts below use Redis CLI's RESP2-style replies. The main sequence follows one fresh `events` key with explicit IDs so each returned ID is predictable; the auto-ID and live-read illustrations use separate keys. They illustrate command behavior rather than a recorded server session.

## Appending entries with `XADD`

`XADD` appends field–value pairs and returns the new entry's ID. Explicit IDs must increase within the stream. Here, `1000-0` and `1000-1` are illustrative IDs chosen for a fresh key, not timestamps measured from a running server:

```sh
redis> XADD events 1000-0 type order.created order_id 42
"1000-0"
redis> XADD events 1000-1 type order.created order_id 43
"1000-1"
```

The first command adds **one entry** to `events` with stream ID `1000-0`. The arguments after that ID alternate field and value: `type` is `"order.created"`, and `order_id` is the string `"42"`. The application field `order_id` is distinct from the stream entry ID. The second command adds a separate entry with ID `1000-1` and `order_id` value `"43"`.

In ordinary use, `*` asks Redis to generate an ID with a millisecond-time component and a sequence component. For example, a separate fresh stream might return the following ID; its exact value depends on server state and time:

```sh
redis> XADD live_events * type order.created order_id 44
"1700000000000-0"
```

IDs establish order **within one stream**. They do not establish global event time or the order in which consumers finish processing. [XADD](https://redis.io/docs/latest/commands/xadd/)

## Reading entries with `XRANGE` and `XREAD`

### `XRANGE`

`XRANGE` selects retained entries by **inclusive stream-ID boundaries** and returns them in ascending ID order:

```text
XRANGE key start-ID end-ID [COUNT count]
```

- **`start-ID`:** The minimum entry ID to include (inclusive). `-` means no lower bound, starting with the oldest retained entry.
- **`end-ID`:** The maximum entry ID to include (inclusive). `+` means no upper bound, extending through the newest retained entry.

The symbols specify ID bounds, not a direction of travel. Thus `XRANGE events - + COUNT 10` reads from oldest to newest and returns at most the first ten retained entries; `COUNT` only caps the number returned:

```sh
redis> XRANGE events - + COUNT 10
1) 1) "1000-0"
   2) 1) "type"
      2) "order.created"
      3) "order_id"
      4) "42"
2) 1) "1000-1"
   2) 1) "type"
      2) "order.created"
      3) "order_id"
      4) "43"
```

Explicit bounds from `1000-0` through `1000-1` would also include both entries because the endpoints are inclusive.

### `XREAD`

`XREAD` instead asks for IDs **greater than** a supplied cursor. A reader starting at `0-0` gets the first entry, then supplies the actual returned ID to resume without repeating it:

```sh
redis> XREAD COUNT 1 STREAMS events 0-0
1) 1) "events"
   2) 1) 1) "1000-0"
         2) 1) "type"
            2) "order.created"
            3) "order_id"
            4) "42"

redis> XREAD COUNT 1 STREAMS events 1000-0
1) 1) "events"
   2) 1) 1) "1000-1"
         2) 1) "type"
            2) "order.created"
            3) "order_id"
            4) "43"
```

Redis does not store this independent reader's cursor: the application retains it. Other `XREAD` clients keep their own cursors and can read the same entries; a read does not delete an entry. When matching entries already exist, `XREAD` returns them immediately even if `BLOCK` is specified. Otherwise, its waiting behavior depends on `BLOCK`:

- **No `BLOCK`:** Return immediately, with `(nil)` if there is no newer entry.
- **`BLOCK 0`:** Wait indefinitely for a matching entry.
- **Positive `BLOCK` value:** Wait up to the specified number of milliseconds for an entry, then return `(nil)` on timeout. The timeout is approximate, not a hard scheduling deadline.

After the reader has received `1000-1`, a finite wait returns no entry if nothing newer arrives during the roughly five-second interval:

```sh
redis> XREAD BLOCK 5000 STREAMS events 1000-1
(nil)
```

To skip existing entries and wait for newly appended ones, use `$` on the **first** `XREAD`. Redis resolves it to the stream's current last ID when that call begins; it does not remember a cursor for the reader. In this separate example, `live_demo` starts with `1000-1`. The reader blocks, then a producer appends `1000-2`, which wakes the reader:

```sh
redis> XADD live_demo 1000-1 type order.created
"1000-1"
# Reader (blocks):
redis> XREAD BLOCK 0 STREAMS live_demo $
# Producer (another client):
redis> XADD live_demo 1000-2 type order.created
"1000-2"
# Reader (unblocks):
1) 1) "live_demo"
   2) 1) 1) "1000-2"
         2) 1) "type"
            2) "order.created"
```

If `1000-3` arrives before the next read, the reader supplies **`1000-2`**, the last ID it received. `XREAD` then returns the newer entry. Supplying `$` again would resolve to the new tail, `1000-3`, and skip that entry instead:

```sh
redis> XADD live_demo 1000-3 type order.paid
"1000-3"
redis> XREAD STREAMS live_demo 1000-2
1) 1) "live_demo"
   2) 1) 1) "1000-3"
         2) 1) "type"
            2) "order.paid"
```

[XRANGE](https://redis.io/docs/latest/commands/xrange/) · [XREAD](https://redis.io/docs/latest/commands/xread/)

## Creating and consuming a group with `XGROUP` and `XREADGROUP`

A **consumer group** shares new deliveries among named consumers. Redis tracks the group's last-delivered position and a **pending entries list (PEL)** for delivered but unacknowledged entries. A different group has its own position and PEL, independent of this group and independent `XREAD` readers. Delivery records responsibility; it does not mean processing succeeded. [Redis Streams consumer groups](https://redis.io/docs/latest/develop/data-types/streams/#consumer-groups)

`XGROUP CREATE` at `0` includes the existing `events` history in ordinary group delivery. `MKSTREAM` creates the stream if absent. Starting at `$` instead skips existing entries and begins after the current tail:

```sh
redis> XGROUP CREATE events workers 0 MKSTREAM
OK
```

`>` requests entries never delivered to this group. The first call assigns `1000-0` to `worker-a` and adds it to the PEL. `BLOCK 1000` would wait up to 1,000 milliseconds if no new group entry were ready; here the entry already exists:

```sh
redis> XREADGROUP GROUP workers worker-a COUNT 1 BLOCK 1000 STREAMS events >
1) 1) "events"
   2) 1) 1) "1000-0"
         2) 1) "type"
            2) "order.created"
            3) "order_id"
            4) "42"
```

After the application finishes the effect for order `42`, `XACK` removes `1000-0` from this group's PEL. Its reply counts acknowledged entries, not deleted stream entries:

```sh
redis> XACK events workers 1000-0
(integer) 1
```

The same consumer then receives `1000-1`, but fails before acknowledging it:

```sh
redis> XREADGROUP GROUP workers worker-a COUNT 1 STREAMS events >
1) 1) "events"
   2) 1) 1) "1000-1"
         2) 1) "type"
            2) "order.created"
            3) "order_id"
            4) "43"
```

Another consumer's `>` reads do not automatically retry `1000-1`. An explicit ID such as `0` with `XREADGROUP` re-reads only **that consumer's own pending entries**, not every pending entry in the group. Multiple consumers divide new deliveries, but processing and acknowledgements need not finish in stream-ID order. Acknowledge only after the effect succeeds. [XGROUP CREATE](https://redis.io/docs/latest/commands/xgroup-create/) · [XREADGROUP](https://redis.io/docs/latest/commands/xreadgroup/) · [XACK](https://redis.io/docs/latest/commands/xack/)

## Recovering pending entries with `XPENDING` and `XAUTOCLAIM`

`XPENDING` summarizes group work that has been delivered but not acknowledged. After the failure above, one entry remains assigned to `worker-a`; the last nested pair gives that consumer's pending count:

```sh
redis> XPENDING events workers
1) (integer) 1
2) "1000-1"
3) "1000-1"
4) 1) 1) "worker-a"
      2) "1"
```

A detailed `XPENDING` range also reports individual entries, owners, idle times, and delivery counts. Recovery must decide when a pending entry has been idle long enough to transfer. `XAUTOCLAIM` scans and reassigns entries meeting a minimum idle time. This illustration uses `0` milliseconds solely to make the transfer eligible without assuming elapsed time; a real recovery threshold must reflect the workload and can race an active slow worker:

```sh
redis> XAUTOCLAIM events workers worker-b 0 0-0 COUNT 10
1) "0-0"
2) 1) 1) "1000-1"
      2) 1) "type"
         2) "order.created"
         3) "order_id"
         4) "43"
3) (empty array)
```

The reply contains the next scan cursor, the claimed entries, and—in Redis 7.0 and later—IDs of deleted entries removed from the PEL during scanning. The `0-0` cursor here ends this scan; a recovery loop continues from any nonzero returned cursor until it reaches `0-0`. After successfully processing order `43`, `worker-b` acknowledges its ID:

```sh
redis> XACK events workers 1000-1
(integer) 1
```

A process can complete an external effect and crash before `XACK`, causing recovery to repeat the effect. Use idempotent effects or application-level deduplication where duplicates matter. Consumer groups track delivery, not exactly-once effects or a transaction spanning Redis and the external system. At-least-once processing depends on an active retry path, entries remaining available, and appropriate Redis durability; it is not an unconditional guarantee of the group. [XPENDING](https://redis.io/docs/latest/commands/xpending/) · [XAUTOCLAIM](https://redis.io/docs/latest/commands/xautoclaim/)

> [!example] Thumbnail generation as a worker job
> Suppose original images are stored durably and each upload needs an independently generated thumbnail. The application enqueues an image ID and object key, **not the image bytes**. A Redis Streams consumer group fits this worker queue under these conditions:
>
> - **Independent jobs:** Each thumbnail is a separate job; the group delivers its entry to a worker and keeps it pending until acknowledged or claimed after failure.
> - **Regenerable outputs:** A missing thumbnail can be rebuilt from its durable original.
> - **Bounded history:** The application needs only a short, bounded job history.
> - **Existing Redis operation:** The application already has a reliably operated Redis deployment.
>
> Run the following commands in **one shell session** against a Redis instance where `thumbnail_jobs_demo` does not yet exist. The shell variable `job_id` keeps the ID returned by `XADD`; the consumer names represent workers, not separate CLI sessions. Create the group at `0` so it includes the job appended next:
>
> ```sh
> redis-cli XGROUP CREATE thumbnail_jobs_demo thumbnail_workers 0 MKSTREAM
> job_id=$(redis-cli --raw XADD thumbnail_jobs_demo '*' image_id img-42 object_key originals/img-42.jpg)
> ```
>
> `worker-a` receives the job and becomes its pending owner. The application would read the original object and write a thumbnail; this command demonstrates only the Redis delivery:
>
> ```sh
> redis-cli XREADGROUP GROUP thumbnail_workers worker-a COUNT 1 BLOCK 1000 STREAMS thumbnail_jobs_demo '>'
> ```
>
> Treat `worker-a` as having stopped immediately after the read: **do not acknowledge** the job. `XPENDING` shows the group's pending summary and then the entry's owner, idle time, and delivery count:
>
> ```sh
> redis-cli XPENDING thumbnail_jobs_demo thumbnail_workers
> redis-cli XPENDING thumbnail_jobs_demo thumbnail_workers - + 10
> ```
>
> Only after the failed worker has stopped, `worker-b` claims the entry. The `0`-millisecond minimum idle time is **for this controlled demonstration only**; a production threshold must allow for legitimate processing time, and an active slow worker could otherwise be raced. `XAUTOCLAIM` returns a next-scan cursor as well as claimed entries. A recovery loop must continue from a nonzero returned cursor until it reaches `0-0`, rather than treating one scan as exhaustive:
>
> ```sh
> redis-cli XAUTOCLAIM thumbnail_jobs_demo thumbnail_workers worker-b 0 0-0 COUNT 10
> ```
>
> After `worker-b` successfully generates the thumbnail, it acknowledges the captured entry ID. If the application uses a deterministic output identity derived from `image_id`, a retry can replace or upsert the same thumbnail instead of creating a second logical result. This matters if a worker writes the thumbnail and crashes before `XACK`: recovery repeats the job, not an exactly-once transaction across Redis and object storage.
>
> ```sh
> redis-cli XACK thumbnail_jobs_demo thumbnail_workers "$job_id"
> ```
>
> The application still needs a retry loop that inspects and claims stale pending work. Redis persistence and failover settings determine which recent writes survive failures; avoid eviction of unprocessed jobs, size capacity and retention for the recovery window, and reconcile missing thumbnails against the durable originals. `XACK` does not delete the payload, and trimming does not protect pending payloads, so retain entries until recovery no longer needs them.

## Trimming retained entries with `XTRIM`

`XTRIM MAXLEN` limits the stream by **entry count**. With both entries now acknowledged, an exact limit of one removes the oldest entry and returns the number removed; it does not undo acknowledgements or change the surviving entry's ID:

```sh
redis> XTRIM events MAXLEN 1
(integer) 1
redis> XRANGE events - +
1) 1) "1000-1"
   2) 1) "type"
      2) "order.created"
      3) "order_id"
      4) "43"
```

`XADD` can trim while appending, and `MAXLEN ~` requests approximate trimming with less frequent eviction work. Neither form is a time-to-live policy. `XACK` removes a PEL reference, not the stream payload, so acknowledgement and retention require separate decisions. [XTRIM](https://redis.io/docs/latest/commands/xtrim/)

Trimming before a slow reader catches up removes data it has not read. By default, trimming can also remove the payload of a **pending** entry while leaving its PEL reference; pending status does not protect the payload. Size retention to the required replay and recovery window, including stalled groups and independent readers.

> [!warning] Retention is not crash durability
> Stream entries and group state follow Redis [persistence](../05%20Architecture%20and%20Reliability/Persistence.md) settings. A successful append or acknowledgement is not automatically durable across a crash. During failover, [asynchronous replication](../05%20Architecture%20and%20Reliability/Distributed%20Redis.md#Replication%2C%20failover%2C%20and%20write%20loss) can also lose writes not yet received by the promoted replica. Retention, persistence, and replication solve different parts of the delivery problem.
