# Strings

* Strings is a basic but powerful data strucutre in Redis
* Strings are binary save, so we can story any data type
  * Strings can be used as generic data storage
  * If our data not fit in any of other Redis data type, we can store the data into string data type.
  * we can serialize any type of data into a string
  * Large amount of data cna be encoded into small spaces in strings
  * In Redis, a *string* is not a “text string” in the language sense. It can hold:
    * Text (`"hello"`)
    * Serialized objects
    * JSON
    * Numbers encoded as characters, e.g. `"123"`, `"-45"`
* String can behave as random access vector too
* Maximum size of the string is 512 MB

## Use cases

Here are the primary use cases for Redis Strings.

* Caching (HTML Fragments, API Responses)

  - **Concept:** Storing the result of expensive database queries or API calls to reduce latency and load on backend systems.
    - **Mechanism:**
      - Use `SET` to store the data (often serialized as JSON).
      - Use `SETEX` (or `SET ... EX`) to automatically expire the cache after a set time (TTL).

  - **Application:** Caching user profiles, product catalog details, or full HTML pages.
  
  - **Example:** Caching a user profile with 1-hour expiration
  
    ```
    redis> SET user:42 "{\"name\": \"John\", \"role\": \"admin\"}" EX 3600
    OK
    redis> GET user:42
    "{\"name\": \"John\", \"role\": \"admin\"}"
    ```

* Atomic Counters

  - **Concept:** tracking numeric values like page views, "likes," or video plays in real-time.

  - **Atomicity:** Redis operations like `INCR` and `DECR` are atomic, meaning multiple clients can update the same counter simultaneously without race conditions (no "lost updates").
    - **Mechanism:**
      - `INCR` increments a value by 1.
      - `INCRBY` increments by a specific amount.
      - `INCRBYFLOAT` handles floating-point numbers.


  - **Application:** Website hit counters, active connection counts, gaming leaderboards (simple).

  - **Example:** Incrementing page views

    ````
    redis> SET page:home:views 0
    OK
    redis> INCR page:home:views
    (integer) 1
    redis> INCRBY page:home:views 10
    (integer) 11
    ````


* Distributed Locks

  - **Concept:** Ensuring that only one process or server can perform a critical action at a time (e.g., generating a daily report, processing a payment).
    - **Mechanism:**
      - Use `SET` with the `NX` (Only set if Not Exists) option.
      - Include an expiration (`EX`) to prevent "deadlocks" if the process crashes before releasing the lock.


  - **Application:** Cron job coordination, preventing double-spending.

  - **Example**: Acquiring a lock

    ````
    redis> SET lock:report_job "server_1" NX EX 10
    OK
    redis> SET lock:report_job "server_2" NX EX 10
    (nil)
    ````


* Session Store

  - **Concept:** Storing user session state for web applications.

  - **Benefit:** Redis is faster than relational databases for this purpose and allows session data to be shared across a cluster of web servers (stateless architecture).

  - **Mechanism:** Keys are Session IDs (cookies); Values are serialized objects.

  - **Application:** Shopping carts, user login status, temporary workflows.

  - **Example**: Storing session data

    ````
    redis> SET session:xyz123 "uid=99;ip=192.168.1.1;cart_items=3"
    OK
    ````

* Rate Limiting

  - **Concept:** Limiting the number of requests a user or IP can make within a specific time window.
    - **Mechanism:**
      - Create a key specific to the user and the time window (e.g., `rate:ip:127.0.0.1:minute`).
      - Use `INCR` on every request.
      - If the result is `1`, set an expiration (`EXPIRE`).
      - If the result > Limit, reject the request.


  - **Application:** API quotas, preventing DDoS attacks, brute-force login protection.

  - **Example**: Simple rate limiter

    ```
    redis> INCR rate:10.0.0.1
    (integer) 1
    redis> EXPIRE rate:10.0.0.1 60
    (integer) 1
    redis> INCR rate:10.0.0.1
    (integer) 2
    ```


## Counting numbers using `INCR` and `DECR`

- `INCR` and `DECR` operate only on strings that represent valid integers
- If a key does not exist, Redis initializes it to `0` before applying the operation
- All increment and decrement operations are atomic
- The updated value is stored back as a string

```text
redis> INCR page:111:views
(integer) 1
redis> INCR page:111:views
(integer) 2
redis> DECR page:111:views
(integer) 1
```

- Values must fit within the signed 64-bit integer range
- Applying these commands to non-integer strings results in an error
- Use `INCR` / `DECR` instead of `GET` + `SET` to avoid race conditions

### `INCRBY` / `DECRBY`

- `INCRBY` increments an integer value by a specified amount
- `DECRBY` decrements an integer value by a specified amount
- The stored value must be a valid integer
- If the key does not exist, Redis initializes it to `0` before applying the operation
- Both operations are atomic

```
redis> INCRBY page:views 10
(integer) 11

redis> DECRBY page:views 3
(integer) 8
```

- Internally, `DECRBY key x` is equivalent to `INCRBY key -x`
- Values must remain within the signed 64-bit integer range
- Applying these commands to non-integer strings results in an error 03 Strings

### `INCRBYFLOAT`

- `INCRBYFLOAT` increments a numeric string by a floating-point value
- Floating-point values are stored and returned as strings
- The operation is atomic
- To decrease a floating-point value, pass a negative increment
  - Redis does not provide a separate `DECRBYFLOAT` command
  - Decrementing floating-point values is achieved by using `INCRBYFLOAT` with a negative number

```
redis> INCRBYFLOAT page:111:views 1.5
"12.5"

redis> INCRBYFLOAT page:111:views -0.75
"11.75"
```

- Applying this command to a non-numeric string results in an error

## Appending to strings using `APPEND`

The `APPEND` command appends the given value to the end of an existing string. The existing value is preserved and extended rather than replaced.

```
redis> SET greeting "Hello"
OK

redis> APPEND greeting ", Redis"
(integer) 12

redis> GET greeting
"Hello, Redis"

redis> APPEND greeting "!"
(integer) 13

redis> GET greeting
"Hello, Redis!"
```

No separator is added automatically; the appended content is concatenated exactly as provided.

### Using `APPEND` for logs or accumulative data

`APPEND` is well suited for cases where data grows over time and overwriting previous values is undesirable.

```
redis> SET website:stats:daily_visitors_log " 200"
OK

redis> APPEND website:stats:daily_visitors_log " 3000"
(integer) 10

redis> GET website:stats:daily_visitors_log
" 200 3000"
```

This pattern is commonly used for lightweight logs, sequential records, or append-only data where simplicity is preferred over structured access.

## Setting and getting multiple keys via `MSET`, `MGET`, `MSETNX`

Redis provides commands that allow working with multiple keys in a single operation. These commands help reduce network overhead and ensure consistent behavior when setting or retrieving related data.

### `MSET`

`MSET` sets multiple key–value pairs at once. The operation is atomic: either all keys are written or none of them are.

**Syntax:**

```
MSET key1 value1 key2 value2 ...
```

**Example:**

```
redis> MSET user:1:name "Alice" user:1:age "25" user:1:country "US"
OK
```

All keys are created or overwritten, regardless of whether they already exist.

### `MGET`

`MGET` retrieves the values of multiple keys in a single command. The returned values follow the same order as the requested keys.

**Syntax:**

```
MGET key1 key2 ...
```

**Example:**

```
redis> MGET user:1:name user:1:age user:1:country
1) "Alice"
2) "25"
3) "US"
```

If a key does not exist, Redis returns `nil` for that position.

### `MSETNX`

`MSETNX` (Multi Set if Not eXists) sets multiple keys **only if none of the specified keys already exist**. The command is atomic: if at least one key exists, no keys are set.

**Syntax:**

```
MSETNX key1 value1 key2 value2 ...
```

**Example:**

```
redis> MSETNX lock:job1 "running" lock:job2 "running"
(integer) 1
```

If any key already exists:

```
redis> MSETNX lock:job1 "running" lock:job2 "running"
(integer) 0
```

- `1` means all keys were successfully set
- `0` means no keys were set because at least one key already existed

`MSETNX` is useful for safe initialization of multiple keys and simple coordination or locking scenarios.

## Atomic read and update with `SET … GET`

### `SET` with `GET`

`SET` supports the `GET` option, which returns the previous value stored at the key while updating it in a single atomic operation.

**Syntax:**

```
SET key value GET
```

**Behavior:**

- Sets `key` to the new `value`
- Returns the old value
- Returns `nil` if the key did not previously exist
- Operation is atomic

**Example:**

```
redis> SET counter 10
OK

redis> SET counter 20 GET
"10"

redis> GET counter
"20"
```

> Starting with Redis 6.2.0, the recommended way to atomically set a new value and retrieve the old one is to use `SET` with the `GET` option. This approach replaces the older `GETSET` command and should be preferred when writing new code.

### Common use cases

#### Read-and-reset counters

```
redis> SET page:views 0 GET
"125"
```

This pattern is commonly used for:

- Periodic metrics
- Rolling counters
- Snapshot-and-reset workflows

#### State transitions

```
redis> SET job:status "processing" GET
"pending"
```

The atomic nature of the operation guarantees that no other client can modify the value between reading the old state and writing the new one.

## Reading substrings with `GETRANGE`

`GETRANGE` is a string command that allows reading a specific portion of a string value stored in Redis. It is useful when working with large strings and you only need a subset of the data.

### `GETRANGE`

**Syntax:**

```
GETRANGE key start end
```

**Behavior:**

- Returns the substring from index `start` to index `end` (both inclusive)
- Indexes are **zero-based**
- Negative indexes are supported and count from the end of the string
- If the key does not exist, Redis returns an empty string
- If the range is out of bounds, Redis safely trims it

**Example:**

```
redis> SET greeting "Hello, Redis!"
OK

redis> GETRANGE greeting 0 0
"H"

redis> GETRANGE greeting 0 4
"Hello"

redis> GETRANGE greeting 7 -2
"Redis"

redis> GETRANGE greeting -6 -2
"Redis"
```

### Working with large strings

`GETRANGE` is especially useful when storing large blobs of data (logs, serialized objects, files, or buffers) and retrieving only a small segment.

```
redis> GETRANGE logfile 0 99
```

This retrieves the first 100 bytes of the string without transferring the entire value over the network.

### Common use cases

- Partial reads of large strings
- Inspecting prefixes or suffixes
- Implementing simple pagination-like access over string data
- Reading headers or metadata from binary payloads

### Notes

- `GETRANGE` operates on **bytes**, not characters
- For UTF-8 or multi-byte encodings, ranges may cut through characters
- The maximum string size in Redis is 512 MB, and `GETRANGE` works safely within this limit

`GETRANGE` provides efficient, low-level access to string data without requiring full-value retrieval.

## Modifying substrings with `SETRANGE`

`SETRANGE` is a string command that overwrites part of an existing string starting at a specified offset. It allows in-place updates without replacing the entire value.

### `SETRANGE`

**Syntax:**

```
SETRANGE key offset value
```

**Behavior:**

- Overwrites the string stored at `key` starting at byte `offset`
- If the key does not exist, Redis treats it as an empty string
- If `offset` is greater than the current string length, Redis pads the gap with zero (`\x00`) bytes
- The command returns the **length of the resulting string**
- The operation is atomic

**Example:**

```
redis> SET greeting "Hello, Redis!"
OK

redis> SETRANGE greeting 7 "World"
(integer) 13

redis> GET greeting
"Hello, World!"
```

### Overwriting part of a string

`SETRANGE` replaces existing bytes starting at the given offset.

```
redis> SET key "abcdef"
OK

redis> SETRANGE key 2 "XYZ"
(integer) 6

redis> GET key
"abXYZf"
```

### Expanding strings with zero padding

If the offset exceeds the current string length, Redis fills the gap with zero bytes.

```
redis> SET key "abc"
OK

redis> SETRANGE key 5 "Z"
(integer) 6
```

Internally, the string becomes:

```
"a b c \x00 \x00 Z"
```

When retrieved with `GET`, zero bytes may not be visible but still count toward the string length.

### `SETRANGE` on a non-existent key

When `SETRANGE` is executed on a key that does not exist, Redis treats the key as an **empty string** and applies the operation as if the string had length `0`.

**Behavior:**

- Redis creates the key automatically
- The string is expanded up to the specified offset
- Any gap between the start of the string and the offset is filled with zero (`\x00`) bytes
- The provided value is written starting at the given offset
- The command returns the length of the resulting string

**Example:**

```
redis> EXISTS buffer
(integer) 0

redis> SETRANGE buffer 3 "A"
(integer) 4
```

The internal representation becomes:

```
"\x00\x00\x00A"
```

Retrieving the value:

```
redis> GET buffer
"\u0000\u0000\u0000A"
```

### Common use cases

- Updating fixed-position fields in binary data
- In-place edits of large strings
- Building buffers incrementally
- Emulating sparse arrays using strings

### Notes

- Offsets are **zero-based**
- Offsets must be non-negative (negative offsets are not allowed)
- `SETRANGE` operates on **bytes**, not characters
- Use carefully with text data, especially with UTF-8 strings

`SETRANGE` is a low-level but powerful command for partial, atomic string updates in Redis.

## String Encoding types

Redis decide the encoding automatically as per string values

- **`int`** — Stores numeric strings as a native 64-bit signed integer inside the object; most memory-efficient and fastest for arithmetic, but only applies to values that are valid integers and stops being used once the value becomes non-numeric.
- **`embstr`** — Optimized for small (≤ 44 bytes), read-mostly strings; object header and string data live in one allocation for better cache locality, but the string is immutable and any modification forces a conversion to `raw`.
- **`raw`** — General-purpose string encoding using a separate, mutable SDS allocation; slightly higher memory overhead, but supports efficient resizing and amortized growth, making it ideal for large or frequently modified strings.

`OBJECT ENCODING <key>` shows the internal representation Redis is using for that value *right now* (an implementation detail). Redis may change the encoding automatically as the value changes (size/content).

Below is a `redis-cli` style session showing each encoding and the common transitions.

* Small Immutable String (`embstr`) → Converted to `raw` After Modification

  ```
  redis> SET small "12345678901123456789011234567890112345678901"
  OK
  redis> OBJECT ENCODING small
  "embstr"
  redis> APPEND small "!"
  (integer) 45
  redis> OBJECT ENCODING small
  "raw"
  ```

* Large String Stored Directly as `raw`

  ```
  redis> SET big "123456789123456789123456789123456789123456789"
  OK
  redis> OBJECT ENCODING big
  "raw"
  ```

* Integer String (`int`) → Remains `int` for Numeric Ops → Converted to `raw` After Non-Numeric Change

  ```
  redis> SET counter 123
  OK
  redis> OBJECT ENCODING counter
  "int"
  redis> INCR counter
  (integer) 124
  redis> OBJECT ENCODING counter
  "int"
  redis> APPEND counter "x"
  (integer) 4
  redis> OBJECT ENCODING counter
  "raw"
  ```

