# Redis

Redis is an open-source, in-memory NoSQL data-structure store organized around keys and values. It holds its database in memory and uses disk for [persistence](13%20Persistence.md). Applications use it as a database, cache, or message broker.

Redis supports strings, hashes, lists, sets, sorted sets, bitmaps, and HyperLogLogs. Clients connect to the server through a range of client libraries; modules such as RediSearch, neural-redis, RedisGraph, rediSQL, and RedisJSON extend its capabilities. Redis also supports scaling out.

## Use cases

Redis combines data structures and messaging mechanisms for different application needs:

- **Caching:** Store frequently requested results as [strings](03%20Strings.md#Use%20cases) to avoid repeating work in a slower backend; expiration bounds how long a cached result remains.
- **Shared sessions:** Store session attributes in [hashes](05%20Hashes.md) so multiple application servers can read and update the same session state.
- **Task queues:** Use [lists](04%20Lists.md#Use%20cases) to buffer work between producers and workers instead of making a request wait for background processing.
- **Recommendations:** Group items by tag in [sets](06%20Sets.md#Use%20cases), then intersect tags to find items that match multiple interests.
- **Leaderboards:** Keep members ordered by score in [sorted sets](07%20Sorted%20sets.md#Use%20cases) to retrieve rankings as scores change.
- **Live notifications:** Use [Pub/Sub](09%20PublishSubscribe%20Model.md#Delivery%20model) to broadcast to current subscribers when missed messages are acceptable.
- **Event processing:** Use [Streams](15%20Streams.md) to retain ordered messages for later reading or coordinated consumption; retention alone does not guarantee durability.
