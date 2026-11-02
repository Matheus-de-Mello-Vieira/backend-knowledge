# Data Management

## Keys and Values

Redis is a key-value store: a value is retrieved by its exact key. `SET` stores a string value under a key, and `GET` retrieves it. A missing key yields `(nil)`.

```sh
redis> SET name "Matheus"
OK
redis> GET name
"Matheus"
redis> GET no-existent
(nil)
```

### Conditional and Expiring Writes

`SET key value NX` uses the `NX` (not exists) condition to store the value only when the key does not already exist. It returns `OK` when it writes the value and `(nil)` when it leaves an existing value unchanged.

```sh
redis> SET name "Matheus" NX
(nil)
redis> SET age 23 NX
OK
redis> GET age
"23"
```

This condition prevents overwrites and supports idempotent operations and simple locks, often combined with expiration.

> [!note] Earlier conditional command
> `SETNX` provides the existence condition. `SET ... NX` also accepts options such as expiration in one atomic operation.

`SET` also accepts an expiration in the same atomic operation as the write:

- **`EX`:** Specifies seconds; `SET session:user:1 "active" EX 60` stores the key immediately with a 60-second lifetime.
- **`PX`:** Specifies milliseconds; `SET session:user:1 "active" PX 60000` expresses the same lifetime at millisecond precision.

> [!note] Earlier expiration command
> `SETEX` also sets a value and a timeout in seconds. `SET` with `EX` is more flexible because it can combine expiration with options such as `NX`, `XX`, `PX`, and `GET` in one atomic operation.

## Removing Keys

`DEL key` removes a key and synchronously reclaims its memory. It accepts multiple keys and returns the number actually removed; nonexistent keys do not contribute to the count.

```sh
redis> DEL name
(integer) 1
redis> DEL name
(integer) 0
redis> DEL key1 key2 key3
```

`UNLINK` removes keys from the keyspace immediately but reclaims their memory asynchronously in a separate thread. Its name reflects the first step: keys are unlinked before their data is freed. It also accepts multiple keys, ignores missing keys, and returns the number removed from the keyspace.

```sh
redis> SET key1 "hello"
redis> SET key2 "world"
redis> SET key3 "!"
redis> KEYS key*
1) "key1"
2) "key2"
3) "key3"
redis> UNLINK key1 key2 missing_key
(integer) 2
redis> KEYS key*
1) "key3"
redis> DEL key3
(integer) 1
```

The difference matters when values are large:

- **`UNLINK`:** Avoids synchronous memory-reclamation work on the command path, making it preferable for large keys or latency-sensitive workloads. Memory can remain allocated briefly after the keys disappear, temporarily increasing peak usage.
- **`DEL`:** Releases memory synchronously, which suits small keys or cases requiring immediate reclamation but can cause latency spikes for large values.

## Checking Key Existence

`EXISTS key` returns `1` when a key exists and `0` otherwise. With multiple keys, it returns the number found.

```sh
redis> EXISTS name
(integer) 1
redis> EXISTS key1 key2
```

## Key Expiration

A **volatile key** has an expiration, while a **persistent key** has no timeout and therefore does not expire through the expiration mechanism. `SET ... EX` or `SET ... PX` establishes the timeout with the value. `EXPIRE` and `PEXPIRE` set or replace a timeout on an existing key, measured from the command's execution.

```sh
redis> SET name "Matheus" EX 120
redis> TTL name
redis> EXPIRE name 10
redis> PERSIST name
redis> SET name "Matheus" PX 120000
redis> PTTL name
redis> PEXPIRE name 10000
```

- **`TTL`:** Reports remaining lifetime in seconds; it returns `-1` for a persistent key and `-2` for a missing or expired key.
- **`PTTL`:** Reports remaining lifetime in milliseconds.
- **`PERSIST`:** Removes an existing timeout. It returns `1` when it removes a timeout and `0` when the key is already persistent or does not exist.

Redis removes expired keys through two complementary mechanisms:

- **Passive expiration:** Access to a timed-out key discovers that it has expired and removes it.
- **Active expiration:** Redis samples volatile keys and deletes expired ones independently of client access. The described sampling cycle tests 20 random keys and repeats when more than 25% have expired; its default frequency is ten times per second and is configurable.

## Logical Keyspaces

Redis logical keyspaces act like separate namespaces: the same key name can hold different values in different keyspaces, and key operations apply to the currently selected one. Keyspace `0` is the default. Keys in different keyspaces cannot be linked to one another.

- **`SELECT 1`:** Switches the connection to keyspace `1`.
- **`KEYS *`:** Lists keys in the selected keyspace.
- **`FLUSHDB`:** Removes all keys from the selected keyspace.

```sh
redis> SET key1 value1
OK
redis> GET key1
"value1"
redis> SELECT 1
OK
redis> SET key1 value2
OK
redis> GET key1
"value2"
redis> SET key2 value2
OK
redis> KEYS *
1) "key1"
2) "key2"
redis> SELECT 0
OK
redis> GET key1
"value1"
redis> KEYS *
1) "key1"
redis> FLUSHDB
OK
redis> KEYS *
(empty array)
```

## Key Iteration with `SCAN`

`SCAN` iterates over keys in the current keyspace without the single blocking traversal of `KEYS`, making it the preferred alternative for large datasets and production workloads. It returns keys, not their values; it does not inspect string encodings.

An iteration starts with cursor `0`. Each reply contains a next cursor and a batch of keys. Pass the returned cursor to the next call until Redis returns `0`.

```sh
redis> SCAN 0
1) "14"
2) 1) "user:1"
   2) "user:2"
   3) "session:9"
redis> SCAN 14
```

- **`MATCH`:** Filters by key-name pattern, as in `SCAN 0 MATCH user:*`.
- **`TYPE`:** Filters by logical value type, as in `SCAN 0 TYPE string`.
- **`COUNT`:** Hints at the amount of work per call, as in `SCAN 0 COUNT 100`. Its default is `10`, but the requested count does not guarantee a batch size.

These options can be combined in one `SCAN` call.

## Key Naming

Redis keys are binary-safe: any binary sequence, including an empty string, is a valid key. The stated maximum key size is 512 MB. Within those limits, choose a simple, informative naming scheme that reflects the data model; very short keys often obscure their meaning. A common convention is `object:<id>`.

For a `User` with `id`, `name`, `group`, and `friends`, keys such as `user:100`, `user:100:group`, and `user:100:friends` group related data under a stable identifier. A name-based key such as `userJohn` is less reliable:

- Two users named John collide under the same key.
- Names can contain non-English characters such as `陽翔` or `عالي`. Redis accepts them, but they can make keys harder to read.
- Colon-separated prefixes make grouping and filtering more predictable. `user:*` targets that namespace, whereas `user*` also matches names such as `userSettings` and `userProfileBackup`.

## Key-Name Patterns

`KEYS <pattern>` matches keys by name. The same pattern syntax is useful with `SCAN MATCH` when a cursor-based traversal is preferable.

- **`?`:** Matches one character; `h?llo` matches `hello`, `hallo`, and `hxllo`.
- **`*`:** Matches any sequence, including an empty one; `h*llo` matches `hllo` and `heeeelo`.
- **Character set:** `h[ae]llo` matches `hello` and `hallo`, but not `hillo` or `haello`. Repeating a character in the set, as in `h[ee]llo`, still matches one `e`, not `ee`.
- **Negated set:** `h[^e]llo` matches a single character other than `e`, such as `hallo` or `hbllo`, but not `hello`.
- **Range:** `h[a-c]llo` matches `hallo`, `hbllo`, and `hcllo`.

`KEYS` performs a database-wide lookup and requires extreme care in production: a large keyspace can make it harm latency. Use `SCAN` for incremental traversal. One example measurement of 40 milliseconds for one million keys on an entry-level laptop is workload- and environment-specific, not a performance guarantee.

```sh
redis> KEYS user:*
1) "user:101"
2) "user:100"
3) "user:100:group"
4) "user:101:group"
redis> KEYS user:*:group
1) "user:100:group"
2) "user:101:group"
```

The second pattern selects the `group` keys within the `user:` prefix.

## Saving the Dataset

`SAVE` and `BGSAVE` create [RDB snapshots](../05%20Architecture%20and%20Reliability/Persistence.md#RDB%20Snapshots). The distinction is where snapshot work occurs:

- **`SAVE`:** Writes the snapshot synchronously and stops processing commands from all clients until it finishes.
- **`BGSAVE`:** Forks a child to write the snapshot while the parent serves clients. Client processing still pauses while the child is created; the snapshot writing itself runs in the background.

```sh
redis> SAVE
redis> BGSAVE
```

When AOF is enabled, Redis flushes it during shutdown. The `SHUTDOWN` save option separately controls an RDB snapshot:

- **`SHUTDOWN`:** Saves an RDB synchronously when at least one [save point](../05%20Architecture%20and%20Reliability/Persistence.md#Save-Point%20Configuration) is configured; otherwise, it creates no RDB snapshot.
- **`SHUTDOWN SAVE`:** Forces a synchronous RDB snapshot even without save points.
- **`SHUTDOWN NOSAVE`:** Skips the RDB snapshot even with save points.

## Renaming Keys

`RENAME key newkey` moves the value to the new name. The old name then disappears. If the source key does not exist, Redis returns an error. The following transcripts illustrate independent starting states.

```sh
redis> SET mykey hello
OK
redis> GET mykey
"hello"
redis> RENAME mykey newkey
OK
redis> GET mykey
(nil)
redis> GET newkey
"hello"
redis> KEYS *
1) "newkey"
```

```sh
redis> EXISTS missingkey
(integer) 0
redis> RENAME missingkey newkey
(error) ERR no such key
redis> EXISTS newkey
(integer) 0
redis> KEYS *
(empty array)
```

When the destination already exists, `RENAME` overwrites it through an implicit deletion of its old value. Deleting a very large destination value can cause high latency even though renaming is ordinarily constant-time.

```sh
redis> SET mykey value1
OK
redis> SET newkey value2
OK
redis> GET mykey
"value1"
redis> GET newkey
"value2"
redis> RENAME mykey newkey
OK
redis> GET mykey
(nil)
redis> GET newkey
"value1"
redis> KEYS *
1) "newkey"
```

`RENAMENX key newkey` performs the rename only when the destination does not exist. It returns an error when the source does not exist; the following existing destination remains unchanged.

```sh
redis> SET mykey "Hello"
"OK"
redis> SET myotherkey "World"
"OK"
redis> RENAMENX mykey myotherkey
(integer) 0
redis> GET myotherkey
"World"
```

## Inspecting Value Type

`TYPE key` returns the logical type of the stored value: `string`, `list`, `set`, `zset`, `hash`, `stream`, or `vectorset`. A missing key returns `none`.

```sh
redis> SET key1 "hello"
OK
redis> LPUSH key2 "a" "b" "c"
(integer) 3
redis> TYPE key1
string
redis> TYPE key2
list
redis> TYPE missing_key
none
```
