# Redis

Redis is an open-source, in-memory NoSQL data-structure store organized around keys and values. It holds its database in memory and uses disk for [persistence](13%20Persistence.md). Applications use it as a database, cache, or message broker.

Redis supports strings, hashes, lists, sets, sorted sets, bitmaps, and HyperLogLogs. Clients connect to the server through a range of client libraries; modules such as RediSearch, neural-redis, RedisGraph, rediSQL, and RedisJSON extend its capabilities. Redis also supports scaling out.

## Server and CLI

This Docker Compose configuration starts a Redis server, publishes port `6379`, mounts a data volume, and enables the append-only file:

```yaml
version: '3.9'

services:
  redis:
    image: redis:latest
    container_name: redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: ["redis-server", "--appendonly", "yes"]

volumes:
  redis_data:
```

For a client running on the same Unix-like host, Redis can also accept connections through a [Unix-domain socket](../../Operating%20Systems/08%20Inter-Process%20Communication.md#Unix-Domain%20Sockets%20and%20Socket%20Pairs) instead of TCP. Configure a socket path in `redis.conf`; Redis does not create a Unix-domain listener when no path is specified. The client needs permission to access the socket:

```conf
unixsocket /run/redis.sock
unixsocketperm 700
```

Connect the CLI to that path with `redis-cli -s /run/redis.sock`. An application client must likewise support Unix-domain sockets and use the configured path. The Docker Compose example above publishes a TCP port; a client in another container would need the socket path shared into its filesystem to use a Unix-domain connection instead.

Run `redis-cli` to open the Redis command-line client. The following commands inspect or control the connected server:

- **`PING`:** Tests the connection; the server replies `PONG`.
- **`INFO`:** Reports server information. `INFO server`, `INFO memory`, `INFO cpu`, `INFO clients`, `INFO stats`, `INFO replication`, and `INFO cluster` restrict the output to a section.
- **`SHUTDOWN`:** Stops the server. Depending on its persistence configuration, shutdown output can include AOF synchronization and a final RDB save.

```sh
redis> PING
PONG
redis> INFO
redis> INFO memory
redis> SHUTDOWN
```

> [!example] Shutdown output
> With AOF and an RDB save configured, the server can report:
>
> ```sh
> * User requested shutdown...
> * Calling fsync() on the AOF file.
> * Saving the final RDB snapshot before exiting.
> * DB saved on disk
> # Redis is now ready to exit, bye bye...
> ```
