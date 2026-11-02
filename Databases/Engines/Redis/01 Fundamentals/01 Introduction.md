# Redis

Redis (`/ˈrɛdɪs/`) is an open-source, in-memory NoSQL data-structure store organized around keys and values. It holds its database in memory and uses disk for [persistence](../05%20Architecture%20and%20Reliability/Persistence.md). Applications use it as a database, cache, or message broker.

Redis supports [strings](../02%20Data%20Types/Strings.md), [hashes](../02%20Data%20Types/Hashes.md), [lists](../02%20Data%20Types/Lists.md), [sets](../02%20Data%20Types/Sets.md), [sorted sets](../02%20Data%20Types/Sorted%20sets.md), bitmaps, and [HyperLogLogs](../02%20Data%20Types/HyperLogLog.md). For messaging, it provides [Pub/Sub](../03%20Messaging/PublishSubscribe%20Model.md) and [Streams](../03%20Messaging/Streams.md). Clients connect to the server through a range of client libraries; modules such as neural-redis, RedisGraph, rediSQL, [RedisBloom](../02%20Data%20Types/Bloom%20filter.md), and [RedisJSON](../02%20Data%20Types/JSON.md) extend its capabilities. Redis also supports [scaling out](../05%20Architecture%20and%20Reliability/Distributed%20Redis.md).

[Redis Search](03%20Redis%20Search.md), formerly called RediSearch, adds secondary indexing and queries over Redis data. It was previously distributed as a separate module; starting with Redis 8, Redis Open Source includes it.

## Use cases

Redis combines data structures and messaging mechanisms for different application needs:

- **Caching:** Store frequently requested results as [strings](../02%20Data%20Types/Strings.md#Use%20cases) to avoid repeating work in a slower backend; expiration bounds how long a cached result remains.
- **Shared sessions:** Store session attributes in [hashes](../02%20Data%20Types/Hashes.md) so multiple application servers can read and update the same session state.
- **Task queues:** Use [lists](../02%20Data%20Types/Lists.md#Use%20cases) to buffer work between producers and workers instead of making a request wait for background processing.
- **Recommendations:** Group items by tag in [sets](../02%20Data%20Types/Sets.md#Use%20cases), then intersect tags to find items that match multiple interests.
- **Leaderboards:** Keep members ordered by score in [sorted sets](../02%20Data%20Types/Sorted%20sets.md#Use%20cases) to retrieve rankings as scores change.
- **Live notifications:** Use [Pub/Sub](../03%20Messaging/PublishSubscribe%20Model.md#Delivery%20model) to broadcast to current subscribers when missed messages are acceptable.
- **Event processing:** Use [Streams](../03%20Messaging/Streams.md) to retain ordered messages for later reading or coordinated consumption; retention alone does not guarantee durability.
