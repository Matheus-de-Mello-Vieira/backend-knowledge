# Publish/Subscribe

Redis Pub/Sub uses Redis as a lightweight message broker between publishers and subscribers. Publishers send messages to named channels, and Redis pushes each message to clients subscribed to the channel. Neither side needs to know the other clients.

- **Channels:** Named topics that route messages. Publishing or subscribing requires no prior channel declaration.
- **Publishers:** Clients use `PUBLISH` to send a payload to a channel.
- **Subscribers:** Clients use `SUBSCRIBE` to receive messages pushed to them while their subscription remains active.

## Delivery model

Pub/Sub is *fire and forget*: Redis delivers to current subscribers rather than storing messages for later consumption. This makes delivery depend on an active subscription at publication time.

- **Persistence:** Published messages are not retained as message history.
- **Offline delivery:** Messages are not queued for disconnected clients. Reconnecting does not recover missed messages.
- **Acknowledgements:** Pub/Sub has no consumer acknowledgement mechanism. Applications needing history or acknowledged consumption need a different mechanism, such as Redis Streams or an appropriately configured RabbitMQ queue.

Typical uses include:

- Real-time notifications, such as chat messages or sports scores.
- Inter-service communication.
- Live configuration updates.

These uses fit Pub/Sub only when missed messages are acceptable or the application has another way to recover the required state.

## Subscription state and replies

A subscription registers interest on a connection; Redis then pushes matching messages asynchronously to that connection. Subscription changes also produce replies, so clients distinguish subscription confirmations from message deliveries by the reply's first element.

- **Direct subscription:** Matches a specific channel name and produces a three-element delivery: `"message"`, channel, payload.
- **Pattern subscription:** Matches channel names with a glob-style pattern and produces a four-element delivery: `"pmessage"`, pattern, channel, payload.

Subscription confirmations and removals contain three elements: the operation name, the channel or pattern, and the remaining subscription count. That count is the client's **total active channel and pattern subscriptions**, not a separate count for each kind. Unsubscribing from channels alone does not end subscriber mode if patterns remain. [Redis subscription counts](https://redis.io/docs/latest/develop/pubsub/#the-meaning-of-the-subscription-count-with-pattern-matching)

> [!important] Subscriber mode depends on the protocol
> With RESP2, the Redis Serialization Protocol's version 2, a subscribed connection accepts only a restricted command set, including `SUBSCRIBE`, `UNSUBSCRIBE`, `PSUBSCRIBE`, `PUNSUBSCRIBE`, `PING`, and `QUIT`. After all channel and pattern subscriptions are removed, it returns to standard command mode. RESP3 permits any command while subscribed. [Redis Pub/Sub protocol behavior](https://redis.io/docs/latest/develop/pubsub/)

## Publishing and subscribing

> [!note] Command transcripts
> The examples below show Redis commands and replies, not shell scripts. Separate blocks represent independent connections unless stated otherwise. In interactive `redis-cli` subscriber mode, the CLI does not accept further commands; the unsubscribe transcripts describe protocol exchanges issued by a client that supports sending commands while subscribed. [Redis CLI subscriber behavior](https://redis.io/docs/latest/develop/pubsub/)

### `PUBLISH`

`PUBLISH` sends a message to a channel for immediate delivery to its connected subscribers. If no client is subscribed, the message is discarded; publishing does not require the channel to exist beforehand.

- **Cost:** O(N + M), where N is the number of direct subscribers to the channel and M is the total number of subscribed patterns across clients, not just matching patterns. [PUBLISH complexity](https://redis.io/docs/latest/commands/publish/)
- **Reply:** An integer reporting the number of clients the message was sent to, not an acknowledgement of receipt or processing.

```text
redis> PUBLISH internal_logs "backup_started"
(integer) 0

redis> PUBLISH notifications "new_user_signup"
(integer) 1

redis> PUBLISH chat_room_general "hello everyone"
(integer) 42
```

### `SUBSCRIBE`

`SUBSCRIBE channel [channel ...]` registers the connection for one or more specific channels. Each channel produces a confirmation; later publications arrive as separate message replies.

- **Cost:** O(N), where N is the number of channels being subscribed to.
- **Confirmation:** `"subscribe"`, channel, total active subscription count.
- **Message:** `"message"`, channel, payload.

On a connection with no existing subscriptions, subscribing to `system_alerts` produces a count of `1`. A later publication to that channel arrives asynchronously:

```text
redis> SUBSCRIBE system_alerts
1) "subscribe"
2) "system_alerts"
3) (integer) 1
1) "message"
2) "system_alerts"
3) "disk_space_low"
```

On that same connection, adding `news` and `sports` produces a confirmation for each channel and raises the count to `3`:

```text
redis> SUBSCRIBE news sports
1) "subscribe"
2) "news"
3) (integer) 2
1) "subscribe"
2) "sports"
3) (integer) 3
```

### `UNSUBSCRIBE`

`UNSUBSCRIBE [channel ...]` removes the named channel subscriptions. With no arguments, it removes all channel subscriptions but leaves pattern subscriptions intact.

- **Cost:** O(N), where N is the number of channels being unsubscribed from.
- **Reply:** `"unsubscribe"`, channel, remaining total subscription count.

On a fresh connection, subscribe to three channels:

```text
redis> SUBSCRIBE news sports weather
1) "subscribe"
2) "news"
3) (integer) 1
1) "subscribe"
2) "sports"
3) (integer) 2
1) "subscribe"
2) "weather"
3) (integer) 3
```

Removing `sports` leaves two subscriptions. Calling `UNSUBSCRIBE` without arguments then removes the other channels. Because this connection has no pattern subscriptions, its count reaches zero and it leaves subscriber mode:

```text
redis> UNSUBSCRIBE sports
1) "unsubscribe"
2) "sports"
3) (integer) 2

redis> UNSUBSCRIBE
1) "unsubscribe"
2) "news"
3) (integer) 1
1) "unsubscribe"
2) "weather"
3) (integer) 0
```

## Pattern subscriptions

### `PSUBSCRIBE`

`PSUBSCRIBE pattern [pattern ...]` registers glob-style patterns rather than individual channel names. A subscription receives messages from every channel whose name matches its pattern.

- **`*`:** Matches any character sequence.
- **`?`:** Matches one character.
- **`[abc]`:** Matches one character from the bracketed set.

Pattern deliveries include the matching pattern as well as the channel and payload, so the client knows which subscription matched.

- **Cost:** O(N), where N is the number of patterns being subscribed to.
- **Confirmation:** `"psubscribe"`, pattern, total active subscription count.
- **Message:** `"pmessage"`, matching pattern, channel, payload.

On a connection with no existing subscriptions, `news.*` matches `news.tech`:

```text
redis> PSUBSCRIBE news.*
1) "psubscribe"
2) "news.*"
3) (integer) 1
1) "pmessage"
2) "news.*"
3) "news.tech"
4) "redis_version_7_released"
```

Adding `logs.[ew]*` on the same connection matches names beginning with `logs.e` or `logs.w`, including `logs.error`:

```text
redis> PSUBSCRIBE logs.[ew]*
1) "psubscribe"
2) "logs.[ew]*"
3) (integer) 2
1) "pmessage"
2) "logs.[ew]*"
3) "logs.error"
4) "connection_timeout"
```

### `PUNSUBSCRIBE`

`PUNSUBSCRIBE [pattern ...]` removes the named pattern subscriptions. With no arguments, it removes all pattern subscriptions but leaves direct channel subscriptions intact. The client leaves subscriber mode only after both kinds are gone.

- **Cost:** O(N), where N is the number of patterns being unsubscribed from. [PUNSUBSCRIBE complexity](https://redis.io/docs/latest/commands/punsubscribe/)
- **Reply:** `"punsubscribe"`, pattern, remaining total subscription count.

On a fresh connection, register two patterns:

```text
redis> PSUBSCRIBE news.* logs.?
1) "psubscribe"
2) "news.*"
3) (integer) 1
1) "psubscribe"
2) "logs.?"
3) (integer) 2
```

Removing `news.*` leaves `logs.?` active, so the connection remains subscribed:

```text
redis> PUNSUBSCRIBE news.*
1) "punsubscribe"
2) "news.*"
3) (integer) 1
```

## Inspecting Pub/Sub state

### `PUBSUB CHANNELS`

`PUBSUB CHANNELS [pattern]` lists active channel names, optionally filtered by a glob-style pattern such as `sys.*`. A channel is active when it has at least one direct subscriber; pattern subscriptions alone do not make a channel appear in this list. [Active channel semantics](https://redis.io/docs/latest/commands/pubsub-channels/)

- **Cost:** O(N), where N is the number of active channels, assuming constant-time pattern matching for relatively short channel names and patterns.
- **Reply:** An array of active channel names.

```text
redis> PUBSUB CHANNELS
1) "notifications"
2) "events:login"

redis> PUBSUB CHANNELS events:*
1) "events:login"
```

### `PUBSUB NUMSUB`

`PUBSUB NUMSUB [channel ...]` reports direct subscriber counts for the requested channels. Pattern subscriptions are excluded, so a channel with no direct subscribers has a count of `0` even if a pattern matches it. Calling the command without channel names returns an empty list. [NUMSUB arguments and counts](https://redis.io/docs/latest/commands/pubsub-numsub/)

- **Cost:** O(N), where N is the number of requested channels.
- **Reply:** Alternating channel names and subscriber counts.

```text
redis> PUBSUB NUMSUB notifications nonexistent_channel
1) "notifications"
2) (integer) 5
3) "nonexistent_channel"
4) (integer) 0
```

### `PUBSUB NUMPAT`

`PUBSUB NUMPAT` reports the number of unique active subscribed patterns without listing their names. It counts distinct patterns, not clients subscribed to patterns.

- **Cost:** O(1).
- **Reply:** An integer pattern-subscription count.

```text
redis> PUBSUB NUMPAT
(integer) 2
```

> [!note] Cluster inspection
> In Redis Cluster, these `PUBSUB` inspection commands report the queried node's Pub/Sub state, not cluster-wide totals. [PUBSUB inspection scope](https://redis.io/docs/latest/commands/pubsub-numsub/)

## Publisher and subscriber interaction

A publisher and subscriber use separate connections. The subscriber must register before publication to receive the messages.

### 1. Subscribe

Client 1 registers for `events`.

```text
redis[1]> SUBSCRIBE events
1) "subscribe"
2) "events"
3) (integer) 1
```

### 2. Publish

Client 2 sends two messages. Assuming client 1 is the only subscriber, each integer reply reports one recipient.

```text
redis[2]> PUBLISH events "system_start"
(integer) 1

redis[2]> PUBLISH events "user_login"
(integer) 1
```

### 3. Receive

Client 1 receives two messages asynchronously on its subscribed connection. Each message is a three-element reply: the type (`"message"`), the channel (`"events"`), and the payload. The numbers identify fields within each reply, not separate messages; numbering restarts at `1)` for the second message.

```text
1) "message"
2) "events"
3) "system_start"
1) "message"
2) "events"
3) "user_login"
```
