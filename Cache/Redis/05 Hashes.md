# Hashes

A Redis hash stores field-value pairs under one key: `username` → `"jdoe"`, `age` → `"30"`, and `status` → `"active"` are three fields of one hash. It is a map or dictionary, not an ordered list. Like a flat JSON object, Python dictionary, or Java `HashMap`, it represents an entity through named attributes; both fields and values are strings. Hashes have no predefined schema, so adding a field to one hash does not change other hashes.

- A hash holds up to $2^{32} - 1$ field-value pairs—more than four billion.
- Grouping an object's attributes under one hash key reduces repeated key names and per-key overhead compared with separate string keys, such as `user:1000:name` and `user:1000:age`; the overall memory and performance trade-offs depend on object size and access patterns.

## Hashes, Redis JSON, one JSON string, or separate string keys

The same entity has four possible representations:

- **Hash:** `user:1000` contains fields such as `name` and `age`.
- **Redis JSON:** `user:1000` contains a JSON document whose nested values Redis can access by path.
- **One JSON string:** `user:1000` contains a serialized document such as `{"name":"Alice","age":30}`.
- **Separate strings:** `user:1000:name` and `user:1000:age` hold individual attributes.

Redis JSON is a [document data type](16%20JSON.md); one JSON string is a plain Redis string containing JSON text, which Redis treats as bytes without document-path operations. Choose according to access patterns and lifecycle rather than key count alone.

| Dimension | Hash | Redis JSON | One JSON string | Separate string keys |
| --- | --- | --- | --- | --- |
| Structure | Named string-valued fields; nested objects require application encoding. | Native JSON values, including nested objects, arrays, and typed scalars. | Application serialization preserves nested objects, arrays, and JSON value types. | Each attribute is an independent string value. |
| Access and updates | `HGET`/`HMGET` select fields; `HSET`/`HINCRBY` update them without transferring the entire entity. | `JSON.GET` reads selected paths; `JSON.SET` changes a path and `JSON.NUMINCRBY` updates a number without transferring the entire document. | `GET` retrieves the document; `SET` replaces it. A property change normally requires application-side deserialization and serialization. | `GET`/`SET` operate on individual attributes; [`MGET`/`MSET`](03%20Strings.md#Working%20with%20multiple%20keys) batch them. |
| [Memory](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/memory-optimization/) | One key plus field metadata; small hashes use compact encoding within configured field-count and value-size limits. Crossing those limits changes the encoding. | One key plus an in-memory parsed document structure; size depends on the document and is not necessarily smaller than serialized JSON. | One key plus serialized field names, values, and JSON syntax. | Repeated key prefixes and per-key metadata for every attribute. |
| Expiration | `EXPIRE` sets a whole-entity timeout; [field timeouts](https://redis.io/docs/latest/commands/hexpire/) are also supported from Redis 7.4 through `HEXPIRE`, so distinct field lifetimes do not inherently rule out a hash. | [Key expiration](02%20Data%20Management.md#Key%20Expiration) removes the entire document; JSON paths have no independent timeout. | Key timeout removes the entire document. | Each attribute has its own key timeout. |
| [Eviction](https://redis.io/docs/latest/develop/reference/eviction/) | Evicting the key removes all fields together. | Evicting the key removes the whole document. | Evicting the key removes the whole document. | Attributes are independently eligible for key eviction. |
| Atomic updates | One multi-field `HSET` is atomic; a sequence of hash commands is not automatically atomic. | One path update or numeric increment is atomic; a sequence of JSON commands is not automatically atomic. | One `SET` replaces the document atomically; a preceding read and edit are not part of that atomic operation. | Individual writes are atomic; coordinated changes need an atomic multi-key command or explicit transaction/script coordination. |
| [Cluster distribution](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/) | The key's fields stay on one shard. | The document's paths stay on one shard. | The document stays on one shard. | Attributes are separate placement units, but different keys do not guarantee different shards; native multi-key operations require the same hash slot. |

For a property update in one JSON string, the normal sequence is `GET` → deserialize → edit → serialize → `SET`. Concurrent clients that read the same version can overwrite each other's changes: atomic `SET` does not make the whole read–modify–write sequence atomic. Redis JSON avoids that client-side cycle for path updates. A condition checked by one command and acted on by another still needs explicit coordination, whether the data is Redis JSON, a hash, or separate strings.

No representation is universally smallest or fastest; compare representative data and operations.

Cluster distributes keys, not hash fields or JSON paths. One key per entity still distributes entities, but adding shards does not split one large or hot key.

Choose the representation according to the operations and lifecycle of the attributes:

- **Hash:** Flat, field-oriented entities.
- **Redis JSON:** Typed or nested documents that need path-level operations.
- **One JSON string:** Whole-document reads and replacements.
- **Separate strings:** Independently managed attributes.

## Use cases

**Structured objects.** A hash groups attributes of a user profile, product, or vehicle under one key, much like a relational row or flat JSON object. For example, `user:1` replaces separate keys such as `user:1:name` and `user:1:email`. Unlike a serialized JSON string, it exposes attributes directly for field-level operations.

```sh
redis> HSET product:5001 type "Laptop" price "1200" stock "50"
(integer) 3
redis> HGET product:5001 price
"1200"
redis> HGETALL product:5001
1) "type"
2) "Laptop"
3) "price"
4) "1200"
5) "stock"
6) "50"
```

**Partial object updates.** A serialized JSON string requires `GET` → deserialize → update → serialize → `SET` to change one attribute. A hash changes just that field with `HSET` or `HINCRBY`, reducing network bandwidth and processing. This fits last-seen timestamps, online status, and inventory counts.

```sh
redis> HSET product:5001 price "1100"
(integer) 0
redis> HINCRBY product:5001 stock -1
(integer) 49
```

**Shopping carts.** A transient cart uses the user or session ID as its key, item IDs as fields, and quantities as values. `HEXISTS` checks for an item, `HINCRBY` increases its quantity, `HDEL` removes it, and `HGETALL` retrieves the cart.

```sh
redis> HSET cart:user:99 item:A 1
(integer) 1
redis> HINCRBY cart:user:99 item:A 2
(integer) 3
redis> HSET cart:user:99 item:B 1
(integer) 1
redis> HDEL cart:user:99 item:A
(integer) 1
redis> HGETALL cart:user:99
1) "item:B"
2) "1"
```

**Grouped counters and metrics.** Related counters share one key instead of occupying separate keys in the global namespace. `HINCRBY` atomically increments individual fields. Examples include player statistics (kills, deaths, gold), post analytics (likes, shares, views), and server metrics (`cpu_load`, `mem_usage`).

```sh
redis> HINCRBY post:123:stats views 1
(integer) 1
redis> HINCRBY post:123:stats likes 1
(integer) 1
redis> HGETALL post:123:stats
1) "views"
2) "1"
3) "likes"
4) "1"
```

## Setting Fields with `HSET`

`HSET` sets one or more field-value pairs under a key, creating a hash when the key is absent and overwriting any existing fields. Its return value counts only newly added fields, not overwritten ones.

One call adds three new fields:

```sh
redis> HSET user:1001 name "John Doe" email "john@example.com" year "1990"
(integer) 3
```

Overwriting `year` changes its value but adds no field, so the result is `0`:

```sh
redis> HSET user:1001 year "1991"
(integer) 0
```

> [!note] Earlier multi-field hash command
> `HMSET` writes multiple fields but has been deprecated since Redis 4.0.0. Use `HSET` with multiple field-value pairs for new code.

## Retrieving Values with `HGET`

`HGET` retrieves one field value as a string in $O(1)$ time. A missing field or missing hash key returns `(nil)`.

An existing field returns its string value:

```sh
redis> HGET user:1001 name
"John Doe"
```

A missing field returns `(nil)`:

```sh
redis> HGET user:1001 phone_number
(nil)
```

## Fetching Everything with `HGETALL`

`HGETALL` returns every field and value as one array of interleaved entries: `field1`, `value1`, `field2`, `value2`, and so on. This loads an entire object at once, but its $O(N)$ work, where $N$ is the hash's field count, can block the server for a hash with millions of fields.

The array interleaves field names and values:

```sh
redis> HGETALL user:1001
1) "name"
2) "John Doe"
3) "email"
4) "john@example.com"
5) "year"
6) "1991"
```

## Fetching Multiple Values with `HMGET`

`HMGET` retrieves a list of values for selected fields in one round trip, reducing network latency compared with sequential `HGET` calls. The results follow the requested field order; each missing field has `(nil)` in its position rather than causing the command to fail.

The result follows the requested `brand`, `model` order:

```sh
redis> HSET laptop id "99" model "X1" brand "ThinkPad" price "1500"
(integer) 4
redis> HMGET laptop brand model
1) "ThinkPad"
2) "X1"
```

A missing `stock` field occupies its own `(nil)` position:

```sh
redis> HMGET laptop id stock price
1) "99"
2) (nil)
3) "1500"
```

## Counting Fields with `HLEN`

`HLEN` returns a hash's field count in $O(1)$ time because Redis tracks the size in metadata rather than traversing the fields. A missing key counts as an empty hash and returns `0`. The count also indicates whether a dynamic collection, such as a shopping cart, is empty or growing.

The populated hash contains three fields:

```sh
redis> HSET article:10 title "Redis Guide" author "Antirez" year "2024"
(integer) 3
redis> HLEN article:10
(integer) 3
```

A missing hash has field count `0`:

```sh
redis> HLEN missing_key
(integer) 0
```

## Removing Fields with `HDEL`

`HDEL` removes one or more fields and returns the number actually removed; missing fields are ignored. Removing the last field also deletes the hash key.

Deleting `preference` leaves `status` intact:

```sh
redis> HSET user:50 preference "dark_mode" status "active"
(integer) 2
redis> HDEL user:50 preference
(integer) 1
redis> HGETALL user:50
1) "status"
2) "active"
```

The absent `unknown_field` does not increase the removal count:

```sh
redis> HSET config timeout "30" retries "3"
(integer) 2
redis> HDEL config timeout unknown_field
(integer) 1
```

## Checking Existence with `HEXISTS`

`HEXISTS` checks whether a field has been set without retrieving its value, for example when checking a user setting. It returns `1` when the hash contains the field and `0` when either the field or the hash key is absent.

Present and absent fields return `1` and `0`, respectively:

```sh
redis> HSET car model "Tesla" year "2023"
(integer) 2
redis> HEXISTS car model
(integer) 1
redis> HEXISTS car color
(integer) 0
```

An absent hash key also returns `0`:

```sh
redis> HEXISTS imaginary_car model
(integer) 0
```

## Listing Fields with `HKEYS`

`HKEYS` returns a list of all field names as strings, without their values. The field order is not guaranteed and may vary, although it is usually consistent with `HVALS`. Like `HGETALL`, its $O(N)$ work can block the server on a very large hash; use `HSCAN` for large production datasets.

The result contains field names without their values:

```sh
redis> HSET profile name "Alice" age "30" country "Wonderland"
(integer) 3
redis> HKEYS profile
1) "name"
2) "age"
3) "country"
```

A missing hash returns an empty array:

```sh
redis> HKEYS ghost_profile
(empty array)
```

## Listing Values with `HVALS`

`HVALS` returns a list of all values as strings, without their field names. Their order usually corresponds to the field order returned by `HKEYS`. Like `HKEYS` and `HGETALL`, its $O(N)$ work warrants caution on large hashes.

The result contains values without their field names:

```sh
redis> HSET inventory apple "50" banana "120" cherry "15"
(integer) 3
redis> HVALS inventory
1) "50"
2) "120"
3) "15"
```

A missing hash returns an empty array:

```sh
redis> HVALS missing_inventory
(empty array)
```

## Incrementing Integers with `HINCRBY`

`HINCRBY` atomically adds an integer increment to a hash field, making it suitable for concurrent counters such as real-time likes. A missing field starts at `0`; a negative increment decrements it. The stored string must represent an integer—decimals or nonnumeric content cause an error—and the operation supports signed 64-bit integers.

Positive and negative increments change the same counter:

```sh
redis> HSET game:1 score "100"
(integer) 1
redis> HINCRBY game:1 score 50
(integer) 150
redis> HINCRBY game:1 score -10
(integer) 140
```

A missing field starts at `0` before the increment:

```sh
redis> HINCRBY game:1 bonus_points 5
(integer) 5
```

## Incrementing Floats with `HINCRBYFLOAT`

`HINCRBYFLOAT` adds a floating-point increment to a field containing either an integer or floating-point value and returns the new value as a string. It uses double-precision floating point for decimal-valued data such as scientific measurements, temperature readings, or currency calculations.

Floating-point increments adjust the stored reading:

```sh
redis> HSET sensor:temperature cpu "45.5"
(integer) 1
redis> HINCRBYFLOAT sensor:temperature cpu 1.2
"46.7"
redis> HINCRBYFLOAT sensor:temperature cpu -0.5
"46.2"
```

The increment also accepts exponential notation:

```sh
redis> HSET physics mass "100"
(integer) 1
redis> HINCRBYFLOAT physics mass 2.5e2
"350"
```

## Random Sampling with `HRANDFIELD`

`HRANDFIELD`, available since Redis 6.2.0, samples fields from the hash at `key`. Without `count`, it returns one random field. With `count`, the sign determines whether repeated fields are allowed:

- **Positive count:** Returns an array of distinct fields.
- **Negative count:** Returns an array that permits duplicates (sampling with replacement).

`WITHVALUES` includes each sampled field's value in an interleaved result. The command is generally $O(N)$ for requested count $N$, so small samples are efficient.

Without `count`, the result is one field:

```sh
redis> HSET coin head "tails" tail "heads" edge "standing"
(integer) 3
redis> HRANDFIELD coin
"head"
```

A positive count samples distinct fields:

```sh
redis> HRANDFIELD coin 2
1) "tail"
2) "edge"
```

A negative count permits duplicates, while `WITHVALUES` returns their values:

```sh
redis> HRANDFIELD coin -3 WITHVALUES
1) "head"
2) "tails"
3) "head"
4) "tails"
5) "edge"
6) "standing"
```
