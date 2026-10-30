# Strings

Redis strings are binary-safe byte sequences, not just text in a programming-language sense. They hold text, serialized objects, JSON, or numeric text such as `"123"` and `"-45"`. This makes a string a general-purpose value when another Redis data type does not fit; serialization can also pack application data into a compact string. Byte offsets provide random-access vector-like operations. A string value has a maximum size of 512 MB.

## Use cases

Strings support several application patterns through different commands:

**Caching.** Store an expensive query result, API response, HTML fragment, user profile, or product detail with `SET`, often after serialization. `SET ... EX` gives the cached value a time to live (TTL), reducing repeated backend work.

```sh
redis> SET user:42 "{\"name\": \"John\", \"role\": \"admin\"}" EX 3600
OK
redis> GET user:42
"{\"name\": \"John\", \"role\": \"admin\"}"
```

> [!note] Earlier expiration command
> `SETEX` also sets a value and timeout in seconds. `SET ... EX` supports other write options in the same operation.

**Atomic counters.** `INCR`, `DECR`, `INCRBY`, and `INCRBYFLOAT` update numeric values without a separate read-modify-write race. Examples include page views, likes, video plays, active connections, and simple gaming leaderboards.

```sh
redis> SET page:home:views 0
OK
redis> INCR page:home:views
(integer) 1
redis> INCRBY page:home:views 10
(integer) 11
```

**Distributed locks.** `SET ... NX EX` admits one holder while the key is absent and gives the lock an expiration if the holder crashes before release. The pattern supports coordination of jobs such as report generation or payment processing; lock-based prevention of double-spending requires more than acquisition alone.

```sh
redis> SET lock:report_job "server_1" NX EX 10
OK
redis> SET lock:report_job "server_2" NX EX 10
(nil)
```

**Session storage.** A session ID used in a cookie identifies a key whose value holds serialized session state. This shares login status, shopping-cart data, or temporary workflow state across web servers rather than binding it to one server's process. Redis can be faster than a relational database for this access pattern.

```sh
redis> SET session:xyz123 "uid=99;ip=192.168.1.1;cart_items=3"
OK
```

**Rate limiting.** A key for each user or IP and time window, such as `rate:ip:127.0.0.1:minute`, counts requests. Increment on each request, set `EXPIRE` when the count first becomes `1`, and reject counts above the limit. Applications include API quotas and defenses against abusive traffic or brute-force login attempts.

```sh
redis> INCR rate:10.0.0.1
(integer) 1
redis> EXPIRE rate:10.0.0.1 60
(integer) 1
redis> INCR rate:10.0.0.1
(integer) 2
```

## Counting numbers using `INCR` and `DECR`

`INCR` and `DECR` atomically change a string that represents an integer. For a missing key, Redis starts from `0`; the updated value is stored as a string. Unlike `GET` followed by `SET`, these commands do not lose concurrent updates.

```sh
redis> INCR page:111:views
(integer) 1
redis> INCR page:111:views
(integer) 2
redis> DECR page:111:views
(integer) 1
```

Values must fit within the signed 64-bit integer range. A non-integer string causes an error.

### `INCRBY` / `DECRBY`

`INCRBY` and `DECRBY` atomically change an integer string by a specified amount. As with `INCR`, the key must hold a valid integer or be missing, in which case Redis starts from `0`.

```sh
redis> SET page:views 1
OK
redis> INCRBY page:views 10
(integer) 11

redis> DECRBY page:views 3
(integer) 8
```

`DECRBY key x` is equivalent to `INCRBY key -x`. The result must remain within the signed 64-bit integer range; a non-integer string causes an error.

### `INCRBYFLOAT`

`INCRBYFLOAT` atomically changes a numeric string by a floating-point amount. Redis stores and returns the result as a string. A negative increment decreases the value; there is no separate `DECRBYFLOAT` command.

```sh
redis> SET page:111:views 11
OK
redis> INCRBYFLOAT page:111:views 1.5
"12.5"

redis> INCRBYFLOAT page:111:views -0.75
"11.75"
```

A non-numeric string causes an error.

## Appending to strings using `APPEND`

`APPEND` extends the existing string with the supplied bytes rather than replacing it. Redis adds no separator; the caller must supply one if needed.

```sh
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

### Using `APPEND` for logs or accumulative data

`APPEND` suits lightweight logs, sequential records, and other accumulating data when overwriting previous values is undesirable and structured access is unnecessary.

```sh
redis> SET website:stats:daily_visitors_log " 200"
OK

redis> APPEND website:stats:daily_visitors_log " 3000"
(integer) 9

redis> GET website:stats:daily_visitors_log
" 200 3000"
```

## Working with multiple keys

Multi-key commands reduce network round trips when related values are written or retrieved together. `MSET` writes unconditionally, `MGET` reads, and `MSETNX` writes only when every specified key is absent.

### `MSET`

`MSET key1 value1 key2 value2 ...` atomically creates or overwrites multiple key–value pairs: either all pairs are written or none are.

```sh
redis> MSET user:1:name "Alice" user:1:age "25" user:1:country "US"
OK
```

### `MGET`

`MGET key1 key2 ...` retrieves values in the same order as the requested keys. A missing key produces `nil` at its position.

```sh
redis> MGET user:1:name user:1:age user:1:country
1) "Alice"
2) "25"
3) "US"
```

### `MSETNX`

`MSETNX key1 value1 key2 value2 ...` (Multi Set if Not eXists) atomically sets all pairs only if none of their keys exist. If any key exists, it writes none. This supports safe multi-key initialization and simple coordination or locking scenarios.

```sh
redis> MSETNX lock:job1 "running" lock:job2 "running"
(integer) 1
```

If any key already exists:

```sh
redis> MSETNX lock:job1 "running" lock:job2 "running"
(integer) 0
```

The return value is `1` when all keys were set and `0` when an existing key prevented every write.

## Atomic read and update with `SET … GET`

`SET key value GET` atomically replaces a value and returns its previous value, or `nil` if the key did not exist. No other client can change the value between this read and write.

```sh
redis> SET counter 10
OK

redis> SET counter 20 GET
"10"

redis> GET counter
"20"
```

> [!NOTE]
> Redis 6.2.0 introduced `SET ... GET` as the preferred replacement for the older `GETSET` command in new code.

### Read-and-reset counters

```sh
redis> SET page:views 0 GET
"125"
```

This read-and-reset pattern supports periodic metrics, rolling counters, and snapshot-and-reset workflows.

### State transitions

```sh
redis> SET job:status "processing" GET
"pending"
```

The returned status identifies the previous state while the key becomes `"processing"`.

## Reading substrings with `GETRANGE`

`GETRANGE key start end` reads a byte range without transferring the entire string. It uses zero-based, inclusive `start` and `end` indexes; negative indexes count backward from the end.

Redis trims out-of-bounds ranges and returns an empty string for a missing key.

```sh
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

### Partial reads

For a large blob such as a log, serialized object, file, or buffer, a range read transfers only the requested segment:

```sh
redis> GETRANGE logfile 0 99
```

This retrieves the first 100 bytes. Other uses include inspecting prefixes or suffixes, pagination-like access over string data, and reading headers or metadata from binary payloads. Ranges operate on **bytes**, not characters, so a UTF-8 range may cut through a multibyte character. `GETRANGE` works within the 512 MB string limit.

## Modifying substrings with `SETRANGE`

`SETRANGE key offset value` overwrites bytes from a specified zero-based offset without replacing the entire value. The operation is atomic and returns the length of the resulting string. The offset must be non-negative.

If the key is missing, Redis starts with an empty string and creates it. If the offset exceeds the current length, Redis pads the gap with zero (`\x00`) bytes before writing the supplied value.

```sh
redis> SET greeting "Hello, Redis!"
OK

redis> SETRANGE greeting 7 "World"
(integer) 13

redis> GET greeting
"Hello, World!"
```

### Overwriting part of a string

The existing bytes at and after the offset are replaced:

```sh
redis> SET key "abcdef"
OK

redis> SETRANGE key 2 "XYZ"
(integer) 6

redis> GET key
"abXYZf"
```

### Expanding strings with zero padding

An offset beyond the end expands the string with zero padding:

```sh
redis> SET key "abc"
OK

redis> SETRANGE key 5 "Z"
(integer) 6
```

Internally, the string becomes:

```text
"a b c \x00 \x00 Z"
```

Zero bytes may not be visible in `GET` output but count toward the string length.

### `SETRANGE` on a non-existent key

On a missing key, the same padding rule applies from an initial length of `0`:

```sh
redis> EXISTS buffer
(integer) 0

redis> SETRANGE buffer 3 "A"
(integer) 4
```

The internal representation becomes:

```text
"\x00\x00\x00A"
```

Retrieving the value:

```sh
redis> GET buffer
"\u0000\u0000\u0000A"
```

Uses include fixed-position binary fields, partial edits of large strings, incremental buffer construction, and sparse-array-like layouts. Since offsets address **bytes**, not characters, partial updates to UTF-8 text can split a character.

## String encodings

Redis chooses an internal encoding according to the value and may change it as the value changes. These encodings are implementation details, not different Redis data types:

- **`int`:** Stores a valid integer string as a native signed 64-bit integer inside the object. It is memory-efficient and fast for arithmetic, but a non-numeric modification changes the encoding.
- **`embstr`:** Packs an object header and a small string (up to 44 bytes in the implementation described here) into one allocation for locality. The encoded value is immutable, so modification converts it to `raw`.
- **`raw`:** Uses a separate, mutable SDS allocation. Its greater memory overhead supports resizing and amortized growth for large or frequently modified strings.

`OBJECT ENCODING <key>` shows the representation in use at inspection time. The following `redis-cli` sessions show encodings and transitions:

**Small `embstr` value converted to `raw` by modification.**

```sh
redis> SET small "12345678901123456789011234567890112345678901"
OK
redis> OBJECT ENCODING small
"embstr"
redis> APPEND small "!"
(integer) 45
redis> OBJECT ENCODING small
"raw"
```

**Large string stored as `raw`.**

```sh
redis> SET big "123456789123456789123456789123456789123456789"
OK
redis> OBJECT ENCODING big
"raw"
```

**Integer stays `int` through arithmetic, then becomes `raw` after a non-numeric change.**

```sh
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
