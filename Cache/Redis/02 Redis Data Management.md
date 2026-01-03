# Redis Data Management

## Keys and Values - `GET` and `SET`

- Redis is a Key based data structure
- Redis is in the family of database called "Key-Value stores"
- Important: the data can only be retrieved if we know the exact 'key' used to store it

- To define a value:

  ```
  redis> SET key value
  ```

- To get the value:

  ```
  redis> GET keys
  ```

### Example

```
redis> SET name "Matheus"
OK
redis> GET name
"Matheus"
```

You you try to get a key that doesn't exists, you will receive a `nil`

```
redis> GET no-existent
(nil)
```

### Setting a Value Only If the Key Does Not Exist (`NX`)

Sometimes you want to store a value **only if the key is not already present**. Redis supports this directly using the `NX` option with the `SET` command.

```
redis> SET key value NX
```

- `NX` means *“set if not exists”*
- If the key **does not exist**, Redis stores the value and returns `OK`
- If the key **already exists**, Redis does nothing and returns `nil`

#### Example

```
redis> SET name "Matheus" NX
(nil)
```

The command returns `nil` because the key `name` already exists.

```
redis> SET age 23 NX
OK
redis> GET age
"25"
```

This is commonly used for:

- Preventing overwrites
- Ensuring idempotent operations
- Implementing simple locks (often combined with expiration)

> Note: Redis also has an older command `SETNX`, but `SET ... NX` is preferred because it supports additional options like expiration in a single atomic operation.

### Setting an expiration time when storing a value (`EX`)

Redis allows you to define an expiration time **at the same moment you set a value**, using options on the `SET` command. This is the preferred approach because it is **atomic**: the value and its expiration are applied in a single operation.

> **Note:** Redis also provides the older command `SETEX`, which sets a value and an expiration time in seconds. While still supported, `SET EX` is generally preferred because it is more flexible and expressive, allowing additional options such as `NX`, `XX`, `PX`, and `GET` to be combined in a single atomic operation.

#### Using `EX` (seconds)

```
redis> SET session:user:1 "active" EX 60
```

- The key is stored immediately
- It will expire automatically after **60 seconds**

#### Using `PX` (milliseconds)

```
redis> SET session:user:1 "active" PX 60000
```

- Same behavior as `EX`, but with millisecond precision

## Deleting Keys - `DEL`

- To delete a key:

  ```
  redis> DEL key
  ```

  - You can deleted many keys at once:

    ```
    redis> DEL key1 key2 key3
    ```

  - You will receive the number of deleted entitiies.

### Example

To delete:

```
redis> DEL name
(integer) 1
```

If you try to delete a a key that doesn't exists, you will receive a `0`:

```
redis> DEL name
(integer) 1
```

## Deleting Keys Asynchronously - `UNLINK`

- Removes the specified keys (similar to `DEL`)
  - Keys that do not exist are ignored
- Non-blocking behavior
  - Actual memory reclamation is handled in a separate thread
  - The command returns immediately
- Keyspace handling
  - Keys are unlinked from the keyspace right away
  - Data is physically removed later, asynchronously
- Command naming
  - The name reflects that keys are unlinked first, not immediately deleted

```
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

### `UNLINK` vs `DEL`

Both commands remove keys from Redis, but they differ in *how* the memory is reclaimed.

- **`UNLINK`**
  - Non-blocking
  - Immediately removes keys from the keyspace
  - Frees memory asynchronously in a background thread
  - Preferred for large keys and latency-sensitive production systems
  - May delay actual memory reclamation briefly
    - Peak memory usage may remain slightly higher for a short time.
- **`DEL`**
  - Blocking
  - Removes keys and frees memory synchronously
  - Suitable for small keys
  - Useful when immediate memory release is required
  - Can cause latency spikes when deleting large values



## Check if exists - `EXISTS`

To check if a key exists:

```
redis> EXISTS name
```

- You will receive `1` if it exists, `0` otherwise.

- You can test multiples keys

  ```
  redis> EXISTS key1 key2
  ```

  - You will receive the number of found entitiies.

### Example
If you check the key:

```
redis> EXISTS name
(integer) 1
```

## Expirations - `TTL`

A key can be:

- **volatile**: a key with an expire set
- **persistent**: a key that will never expire as no timeout is associated.

To define a key with 120 seconds of TTL:

```
redis> SET name "Matheus" ex 120
```

You can check the remaning time with:

```
redis> TTL name
```

- If the key is persistent (no timeout associated), you will receive a `-1`.
- If the key is already expired, you will receive a `-2`.

You can overide the expiration time with:

```
redis> EXPIRE name 10
```

- This means that the key `name` will be set to expire 10 seconds from the moment the `EXPIRE` command is executed.

You can remove the expiration form a key

```
redis> PERSIST name
```

- It will return `1` if the key had it's timeout removed, and `0` if it is already persistent or it don't exists.

You can also do it using millisecond:

```
SET name "Matheus" px 120000
```

To check the ttl in milliseconds:

```
redis> PTTL name
```

You can overide the expiration time in milliseconds:

```
redis> PEXPIRE name 10000
```

### How Redis handle keys expirations

Two ways

- **passive way**: A key is passively expired simply when some client tries to access it, and the key is found to be timed out.
- **active way** Test 20 random keys from the set of volatile keys, and delete all the keys found expired. If more than 25% of keys are expired, start again from step 1.
  - Redis does it 10 times per second by default, but it is configurable.

## Key Spaces - `SELECT`, `KEYS` and `FLUSHDB`

Key Spaces in Redis is similar to database namespaces schemas.

- this allow you to have same key name in multiple key spaces

- you can manage keys per each key spaces

- The first and default key space is `0`.

- You can change the key space with

  ```
  redis> SELECT 1
  ```


- You can see all keys set on the current space using

  ```
  redis> KEYS *
  ```

- You can delete all keys in the space using

  ```
  redis> FLUSHDB
  ```

- You cannot link keys with one key spcae to another key spaces.

Example

```
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

## Key naming conventions

- Keep it simpel but robuts
- Very short keys are often not a good idea - there are not very informative.
- Try best schema based on your database design
  - `object:<id>`
- The max allowed key size is 512 MB
- Redis keys are binary safe - you can use any binary sequence as a key
- Empty string is also a valid key

For example, given the entity `User` with attributes `id`, `name`, `group`, `friends`.

- You can use:

  - `user:100`

  - `user:100:group`

  - `user:100:friends`

- It is not recommended:

  - `userJohn`
    - using names is dangerous
      - it can happen to be written in non-English letters like "陽翔" or "عالي".
        - The redis will be OK with is on the technical perspective, but it will jeopardize the readability.
      - if you have multiple users named “John,” you immediately get collisions
    - Redis key namespaces (using `:`) are a common convention
      - This lets you easily group and filter keys by prefix — e.g. `SCAN user:*` finds all user-related data.
        - You can use `SCAN user*`, which internally makes no difference, but it produces less predictable results because it can match things like `userSettings` or `userProfileBackup`.

## Key patterns matching

You can search for the keys that match a pattern with `KEYS <pattern>`

- `h?llo` matches `hello`, `hallo` and `hxllo`
- `h*llo` matches `hllo` and `heeeelo`.
- `h[ae]llo` matches `hello`and `hallo`, but not `hillo` nor `haello`
  - `h[ee]llo` will match `hello`, but not `heelo`

- `h[^e]llo` matches `hallo`, `hbllo`..., but not `hello`
  - matches the same thing of `h*llo`, except `hello`

- `h[a-c]llo` matches `hallo`, `hbllo` and `hcllo`.
  - it is a range.


### Caveats:

- Redis running on an entry level laptop can scan a 1 million key database in 40 miliseconds.
- Consider `KEYS` as a command that should only be used in production environments with extreme care. It may ruin performance when it is executed against large databases.
  - Consider use `SCAN`.

### In pratice

You can:

- look all users with:

  ```
  redis> KEYS user:*
  1) "user:101"
  2) "user:100"
  3) "user:100:group"
  4) "user:101:group"
  ```

- look the group of all users

  ```
  redis> KEYS user:*:group
  1) "user:100:group"
  2) "user:101:group"
  ```


## Saving keys information on server - `SHUTDOWN`

To turn the redis off saving the info:

```
SHUTDOWN save
```

## Rename a key - `RENAME`

- RENAMES key to newkey

  ```
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

  - Returns an error if key does not exist

    ```
    redis> EXISTS missingkey
    (integer) 0
    redis> RENAME missingkey newkey
    (error) ERR no such key
    redis> EXISTS newkey
    (integer) 0
    redis> KEYS *
    (empty array)
    ```

  - If newkey already exists:

    - It is overwritten

      ```
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

    - An implicit DEL operation is executed

      - If the deleted key contains a very large value, this may cause high latency
        - This can happen even though RENAME is usually a constant-time operation

### `RENAMENX`

Renames `key` to `newkey` if `newkey` does not yet exist. It returns an error when `key` does not exist.

```
redis> SET mykey "Hello"
"OK"
redis> SET myotherkey "World"
"OK"
redis> RENAMENX mykey myotherkey
(integer) 0
redis> GET myotherkey
"World"
```

## Finding data type - `TYPE`

Returns the string representation of the type of the value stored at `key`. The different types that can be returned are: `string`, `list`, `set`, `zset`, `hash`, `stream`, and `vectorset`.

```
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

