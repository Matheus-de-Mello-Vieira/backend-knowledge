# Redis Connections

A Redis client keeps connection state across commands and replies. Reusing a connection avoids repeating acceptance and setup for each request; [pipelining](Mass%20Insertion%20of%20Data%20-%20Piping.md) additionally lets a client send several requests without waiting a round trip for each reply. Neither changes Redis's predominantly main-thread execution of ordinary commands. Redis's [event-loop and I/O-thread implementation](../05%20Architecture%20and%20Reliability/Internals.md#Main%20event%20loop) advances many such connections without dedicating a thread to each client.

## Transport and connection lifetime

Redis accepts connections through configured TCP, TLS, and Unix-domain listeners. A client on the same Unix-like host can use a [Unix-domain socket](../../../../Operating%20Systems/08%20Inter-Process%20Communication.md#Unix-Domain%20Sockets%20and%20Socket%20Pairs) instead of TCP when the server has a socket path configured and the client has permission to access it. Without a configured path, Redis does not create that listener. For example:

```conf
unixsocket /run/redis.sock
unixsocketperm 700
```

Connect the CLI to that path with `redis-cli -s /run/redis.sock`; an application client must also support Unix-domain sockets and use the configured path. Publishing a TCP port from a container does not share its Unix-domain socket: a client in another container needs the socket path shared into its filesystem.

The configured `maxclients` value limits admission, but the operating system's available file descriptors can lower the effective limit. When the client limit is reached, Redis rejects the connection; an error reply is best effort, and a TLS connection rejected before its handshake receives no such reply. [Admission](https://github.com/redis/redis/blob/498ecd0d6d007db11ddb3aea9428552598a78622/src/networking.c#L1666-L1738) · [Descriptor-limit adjustment](https://github.com/redis/redis/blob/498ecd0d6d007db11ddb3aea9428552598a78622/src/config.c#L2780-L2805)

## Application connections to distributed Redis

The deployment's routing model determines whether the application connects directly to data nodes or through a database endpoint:

- **Redis Open Source Cluster:** A cluster-aware client connects to a node's client/data port, not its inter-node cluster-bus port. It bootstraps a slot-to-node map with `CLUSTER SHARDS`, then routes commands to the node responsible for the key's hash slot. It must handle [`MOVED` and `ASK` redirects](../05%20Architecture%20and%20Reliability/Distributed%20Redis.md#Slot%20migration%20and%20client%20routing) when its map is stale or slots are migrating. The initial node is a discovery contact, not a proxy for all subsequent commands. [Redis Cluster specification](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/).
- **Redis Software:** In the default connection model, the application uses the database endpoint's fully qualified domain name (FQDN) and port. A [proxy routes operations to the responsible shards](../05%20Architecture%20and%20Reliability/Distributed%20Redis.md#Routing%20and%20availability), so the client does not maintain direct shard routing. If TLS is enabled for the database, the client must use the corresponding TLS configuration. [Database connections](https://redis.io/docs/latest/operate/rs/databases/connect/).
    - **Optional OSS Cluster API:** Enabling this mode changes the routing contract: clients must support the OSS Cluster API and use its topology and redirection information rather than treating the database as the default single-endpoint routing model. [OSS Cluster API](https://redis.io/docs/latest/operate/rs/databases/configure/oss-cluster-api/).

## Buffered replies and slow clients

Redis queues a command reply in client-managed output before the socket accepts it. If a peer reads slowly, unsent bytes remain in Redis's output buffers, separate from the kernel's send buffer, and a later writable event resumes transmission. Continued reply generation can grow that client-managed output; queuing or partially writing a reply does not establish that the peer received it. The [reply write path](../05%20Architecture%20and%20Reliability/Internals.md#Replies%20and%20slow%20clients) tracks partial progress across callbacks. [Socket write behavior](https://github.com/redis/redis/blob/498ecd0d6d007db11ddb3aea9428552598a78622/src/socket.c#L135-L163) · [Write progress](https://github.com/redis/redis/blob/498ecd0d6d007db11ddb3aea9428552598a78622/src/networking.c#L2847-L2999)

Redis 8.10.2 has two distinct controls for pending output:

- **Output-buffer limits:** Redis compares logical client output size with class-specific hard and soft thresholds. Normal clients (including MONITOR) default to `0 0 0`, replica clients to `256mb 64mb 60`, and Pub/Sub clients to `32mb 8mb 60`—hard bytes, soft bytes, then soft seconds. Both normal-client output thresholds are disabled by default; masters use the normal class for this check. A nonzero hard threshold closes the client when reached. A nonzero soft threshold closes it after output remains at or above that size for the configured duration; falling below resets the timer. Zero disables the corresponding byte threshold, but zero seconds alone does not disable a nonzero soft threshold. A configured replica hard threshold below `repl-backlog-size` is effectively raised to that size. Exceeding a limit schedules asynchronous closure when immediate freeing is unsafe, or closes the client directly from a safe context. Unauthenticated clients have a separate output restriction even when normal thresholds are disabled. [Configuration](https://github.com/redis/redis/blob/498ecd0d6d007db11ddb3aea9428552598a78622/redis.conf#L2439-L2476) · [Classification and checks](https://github.com/redis/redis/blob/498ecd0d6d007db11ddb3aea9428552598a78622/src/networking.c#L5375-L5465)
- **Write fairness:** Redis limits bytes sent per write invocation for ordinary clients so one writable connection does not monopolize an event loop. It bypasses that cap under its `maxmemory` condition; replica and monitor paths differ and try to drain more output. The cap protects other clients' progress, but does not bound accumulated output or guarantee bandwidth. [Write loop](https://github.com/redis/redis/blob/498ecd0d6d007db11ddb3aea9428552598a78622/src/networking.c#L2847-L2944)

## Input and aggregate client memory

- **Input-buffer limit:** Query-buffer limits disconnect clients that accumulate excessive input; unauthenticated clients have a tighter bound. [Query-buffer check](https://github.com/redis/redis/blob/498ecd0d6d007db11ddb3aea9428552598a78622/src/networking.c#L4029-L4045)
- **Client-memory limit:** `maxmemory-clients` is disabled by default. When configured, it triggers aggregate client-memory eviction among eligible normal and Pub/Sub clients rather than imposing a per-client output threshold on every class. Accounting includes pending replies, input buffers, and other client state. [Accounting](https://github.com/redis/redis/blob/498ecd0d6d007db11ddb3aea9428552598a78622/src/networking.c#L5289-L5317) · [Eviction](https://github.com/redis/redis/blob/498ecd0d6d007db11ddb3aea9428552598a78622/src/networking.c#L5713-L5788) · [Default](https://github.com/redis/redis/blob/498ecd0d6d007db11ddb3aea9428552598a78622/redis.conf#L2489-L2506)

## Disconnection

`timeout` governs ordinary idle-client disconnection when set; its default of zero disables that idle timeout. Replication has separate timeout handling, and output from a master connection is not counted as an interaction for its timeout tracking. Peer closure, fatal I/O errors, resource-limit enforcement, timeout, and an explicit close-after-reply state also lead to client cleanup. The [deferred reclamation path](../05%20Architecture%20and%20Reliability/Internals.md#Disconnection%20and%20deferred%20reclamation) coordinates that cleanup with I/O-worker callbacks. [Timeout configuration](https://github.com/redis/redis/blob/498ecd0d6d007db11ddb3aea9428552598a78622/src/config.c#L3520-L3556) · [Interaction update](https://github.com/redis/redis/blob/498ecd0d6d007db11ddb3aea9428552598a78622/src/networking.c#L2904-L2910)
