# Redis

* Redis is an open source in-memory data structure store
* It is open source
* Used as a database, cache and message broker
* Redis holds its entire database in memory
* Disk is used for persistent data store
* It is a NoSQL Database and follow a key-value store concepts.
* It supports robust data structures like strings, hashes, lists, sets, sorted sets, bitmap, hyperloglogs.
* Redis can be connected with various clients.
* Redis can be used with various modules, as `RediSearch`, `neural-redis`, `RedisGraph`, `rediSQL`, `RedisJSON`, etc.
* It can be scaled out.

## Basic commands

I will run a server using docker compose:

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

So you can run:

```bash
$ redis-cli
```

It will open the redis cli

* you can test the connection with:

  ```
  127.0.0.1:6379> ping
  PONG
  ```

* you can turn the server off with:

  ```
  127.0.0.1:6379> shutdown
  ```

  * On the server:

    ```
    * User requested shutdown...
    * Calling fsync() on the AOF file.
    * Saving the final RDB snapshot before exiting.
    * DB saved on disk
    # Redis is now ready to exit, bye bye...
    ```

* you can get the info of the server with:

  ```
  127.0.0.1:6379> info
  ```

  * It is print a lot of information. You can print only a section with:

    * ```
      info server
      ```
    * ```
      info memory
      ```
    * ```
      info cpu
      ```
    * ```
      info clients
      ```
    * ```
      info stats
      ```
    * ```
      info replication
      ```
    * ```
      info cluster
      ```