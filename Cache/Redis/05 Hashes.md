# Hashes

- **Definition:** A Hash is a collection of **field-value pairs** stored under a single Redis key. It is not a "list" (which implies order), but rather a "map" or "dictionary."
- **Structure:** It maps specific fields to values:
  - `username` → `"jdoe"`
  - `age` → `"30"`
  - `status` → `"active"`
- **Analogy:** Conceptually similar to a **JSON object** (flat, non-nested), a Python Dictionary, or a Java HashMap. They are the perfect data type for representing objects (like Users, Products, or Vehicles).
- **Data Types:** Both the *field* and the *value* are strictly **Strings**.
- **Schemaless:** Hashes are flexible. You can add new fields to a specific hash at any time without affecting other hashes. There is no predefined blueprint.
- **Capacity:** A single Hash can store more than **4 billion field-value pairs** ($2^{32} - 1$).
- **Optimization:** Storing an object as a single Hash is often more memory-efficient and faster than storing every attribute as a separate String key (e.g., `user:1000:name`, `user:1000:age`).

## Use Cases

Here are the primary use cases for Redis Hashes.

* Storing Structured Objects (User Profiles, Products)

  - **Concept:** Hashes are the primary data structure for representing "objects" or entities. They map directly to a row in a relational database or a flat JSON object.

  - **Efficiency:** Instead of creating separate keys for every attribute (e.g., `user:1:name`, `user:1:email`), you group them under a single key (`user:1`).

  - **Memory:** Storing an object as a Hash is significantly more memory-efficient than storing it as a generic serialized JSON string or as multiple separate keys.

  - **Application:** User profiles, product catalog details, vehicle configurations.

  * **Example:** Storing a product profile
    
    ```
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

* Partial Object Updates

  - **Concept:** Modifying a specific attribute of an object without reading and rewriting the entire object.

  - **Comparison:** If you store a user as a serialized JSON string in a standard Redis **String**, updating their "last login" requires: `GET` (fetch full JSON) → Deserialize → Update → Serialize → `SET` (write full JSON).

  - **Advantage:** With Hashes, you simply update the specific field using `HSET` or `HINCRBY`. This reduces network bandwidth and processing overhead.

  - **Application:** Updating last seen timestamps, changing online status, updating inventory counts.

  - **Example:** Updating just the stock and price
    
      ```
      redis> HSET product:5001 price "1100"
      (integer) 0
      redis> HINCRBY product:5001 stock -1
      (integer) 49
      ```


* Shopping Carts

  - **Concept:** Storing a transient collection of items associated with a user session.

  - **Structure:** The Key is the User/Session ID; the Field is the Item ID; the Value is the Quantity.

  - **Features:**
    - Easily check if an item is already in the cart (`HEXISTS`).
      - Increment quantity if they add it again (`HINCRBY`).
      - Remove an item (`HDEL`).
      - Get the full cart list (`HGETALL`).
  - **Example:** Managing a shopping cart
    ```
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

* Grouped Counters / Metrics

  - **Concept:** Maintaining multiple related counters for a single entity without polluting the global key namespace.

  - **Atomicity:** `HINCRBY` allows you to atomically increment specific fields within the hash.

  - **Application:** Player statistics (kills, deaths, gold), post analytics (likes, shares, views), server metrics (cpu_load, mem_usage).
  
  
    - **Example:** Tracking blog post metrics
  
      ```
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

- **Function:** Sets the value of one or more fields in the hash stored at the key.
- **Creation:** If the key does not exist, a new key holding a hash is created.
- **Updates:** If a field already exists in the hash, its value is overwritten.
- **Variadic:** You can set multiple field-value pairs in a single command.
- **Return Value:** Returns the number of fields that were *newly* added (fields that already existed and were updated are not counted).

**Example: Setting multiple fields at once**

```
redis> HSET user:1001 name "John Doe" email "john@example.com" year "1990"
(integer) 3
```

**Example: Updating an existing field (Returns 0)**

```
redis> HSET user:1001 year "1991"
(integer) 0
```

## Retrieving Values with `HGET`

- **Function:** Returns the value associated with a specific `field` in the hash.
- **Type:** Always returns a String.
- **Missing Data:**
  - Returns `(nil)` if the field is not present in the hash.
  - Returns `(nil)` if the key itself does not exist.
- **Performance:** Extremely fast **O(1)** operation.

**Example: Retrieving a specific value**

```
redis> HGET user:1001 name
"John Doe"
```

**Example: Accessing a non-existent field**

```
redis> HGET user:1001 phone_number
(nil)
```

## Fetching Everything with `HGETALL`

- **Function:** Returns **all** fields and values of the hash stored at the key.
- **Output Format:** Returns a single list (array) where field names and values are interleaved.
  - Format: `field1`, `value1`, `field2`, `value2`...
- **Use Case:** Ideal for loading an entire object into memory at once.
- **Performance Warning:** Since this command is **O(N)** (where N is the size of the hash), running this on a hash with millions of fields can block the server.

**Example: Retrieving the entire object**

```
redis> HGETALL user:1001
1) "name"
2) "John Doe"
3) "email"
4) "john@example.com"
5) "year"
6) "1991"
```

## Fetching Multiple Values with `HMGET`

- **Function:** Returns the values associated with the specified fields in the hash stored at the key.
- **Order:** The values in the returned list correspond exactly to the order of the fields requested in the arguments.
- **Missing Fields:** If a requested field does not exist in the hash, a `(nil)` value is returned in that specific position; the command does not fail.
- **Efficiency:** Much faster than executing multiple `HGET` commands sequentially because it reduces network latency by retrieving all required data in a single round trip.
- **Return Value:** A list of values.

**Example: retrieving specific fields (subset of an object)**

```
redis> HSET laptop id "99" model "X1" brand "ThinkPad" price "1500"
(integer) 4
redis> HMGET laptop brand model
1) "ThinkPad"
2) "X1"
```

**Example: handling missing fields**

```
redis> HMGET laptop id stock price
1) "99"
2) (nil)
3) "1500"
```

## Counting Fields with `HLEN`

- **Function:** Returns the number of fields contained in the hash stored at the key.
- **Performance:** This is an **O(1)** operation. Redis tracks the size of the hash in metadata, so it does not need to traverse the fields to count them.
- **Missing Keys:** If the key does not exist, it is treated as an empty hash, and the command returns `0`.
- **Use Case:** Useful for checking if a hash is empty or monitoring the size of a dynamic collection (like a shopping cart).

**Example: getting the size of a populated hash**

```
redis> HSET article:10 title "Redis Guide" author "Antirez" year "2024"
(integer) 3
redis> HLEN article:10
(integer) 3
```

**Example: checking a non-existent key**

```
redis> HLEN missing_key
(integer) 0
```

## Removing Fields with `HDEL`

- **Function:** Removes the specified fields from the hash stored at the key.
- **Variadic:** Can accept one or multiple fields to delete in a single command.
- **Non-existent Fields:** If a specified field does not exist in the hash, it is simply ignored.
- **Return Value:** Returns the number of fields that were actually removed (excluding fields that were not found).
- **Cleanup:** If the last field of a hash is deleted, the hash itself (the key) is automatically deleted from Redis.

**Example: deleting a single field**

```
redis> HSET user:50 preference "dark_mode" status "active"
(integer) 2
redis> HDEL user:50 preference
(integer) 1
redis> HGETALL user:50
1) "status"
2) "active"
```

**Example: deleting multiple fields (including missing ones)**

```
redis> HSET config timeout "30" retries "3"
(integer) 2
redis> HDEL config timeout unknown_field
(integer) 1
```

## Checking Existence with `HEXISTS`

- **Function:** Determines if a specific field exists within the hash stored at the key.
- **Result:** Returns a boolean integer:
  - `1` if the hash contains the field.
  - `0` if the hash does not contain the field, or if the key itself does not exist.
- **Use Case:** Useful for verifying if an attribute has been set without needing to retrieve its value (e.g., checking if a user has a specific setting enabled).

**Example: checking for present and missing fields**

```
redis> HSET car model "Tesla" year "2023"
(integer) 2
redis> HEXISTS car model
(integer) 1
redis> HEXISTS car color
(integer) 0
```

**Example: checking on a missing key**

```
redis> HEXISTS imaginary_car model
(integer) 0
```

## Listing Fields with `HKEYS`

- **Function:** Returns all field names (keys) contained in the hash stored at the key.
- **Content:** Only the field names are returned; the associated values are omitted.
- **Order:** The order of fields returned is not guaranteed and may vary, although it is usually consistent with `HVALS`.
- **Performance:** Like `HGETALL`, this is an **O(N)** operation. On very large hashes, this can block the server, so use `HSCAN` for large datasets in production.
- **Return Value:** A list of strings representing the field names.

**Example: retrieving field names**

```
redis> HSET profile name "Alice" age "30" country "Wonderland"
(integer) 3
redis> HKEYS profile
1) "name"
2) "age"
3) "country"
```

**Example: listing fields of a missing key**

```
redis> HKEYS ghost_profile
(empty array)
```

## Listing Values with `HVALS`

- **Function:** Returns all values contained in the hash stored at the key.
- **Content:** Only the values are returned; the associated field names are omitted.
- **Order:** The order usually corresponds to the order of fields returned by `HKEYS`.
- **Performance:** This is an **O(N)** operation. Like `HKEYS` and `HGETALL`, running this on large hashes should be done with caution.
- **Return Value:** A list of strings representing the values.

**Example: retrieving values only**

```
redis> HSET inventory apple "50" banana "120" cherry "15"
(integer) 3
redis> HVALS inventory
1) "50"
2) "120"
3) "15"
```

**Example: values from a missing key**

```
redis> HVALS missing_inventory
(empty array)
```

## Incrementing Integers with `HINCRBY`

- **Function:** Increments the integer value of a hash field by the specified `increment`.
- **Initialization:** If the field does not exist, it is set to `0` before performing the operation.
- **Atomicity:** The operation is atomic; safe to use in concurrent environments (e.g., counting likes in real-time).
- **Subtraction:** You can decrement values by providing a **negative** increment.
- **Constraints:** The value stored at the field must be a string representing an integer. If the value contains decimals or non-numeric characters, an error is returned.
- **Range:** Supports signed 64-bit integers.

**Example: Basic counting**

```
redis> HSET game:1 score "100"
(integer) 1
redis> HINCRBY game:1 score 50
(integer) 150
redis> HINCRBY game:1 score -10
(integer) 140
```

**Example: Incrementing a non-existent field**

```
redis> HINCRBY game:1 bonus_points 5
(integer) 5
```

## Incrementing Floats with `HINCRBYFLOAT`

- **Function:** Increments the floating-point value of a hash field by the specified `increment`.
- **Precision:** Uses double precision floating-point numbers.
- **Flexibility:** Can interact with both integer and float values stored in the hash.
- **Return Value:** Returns the new value as a string.
- **Use Case:** Essential for scientific data, temperature readings, or currency calculations that require decimals.

**Example: Adjusting precise values**

```
redis> HSET sensor:temperature cpu "45.5"
(integer) 1
redis> HINCRBYFLOAT sensor:temperature cpu 1.2
"46.7"
redis> HINCRBYFLOAT sensor:temperature cpu -0.5
"46.2"
```

**Example: Exponential notation support**

```
redis> HSET physics mass "100"
(integer) 1
redis> HINCRBYFLOAT physics mass 2.5e2
"350"
```

## Random Sampling with `HRANDFIELD`

- **Function:** Returns a random field from the hash value stored at the key.
- **Availability:** Available since Redis 6.2.0.
- **Arguments:**
  - **key:** The hash to sample from.
  - **count (optional):**
    - If `count` is positive (`> 0`), returns an array of `count` **distinct** fields.
    - If `count` is negative (`< 0`), returns an array of `count` fields, but allows **duplicates** (sampling with replacement).
  - **WITHVALUES (optional):** If this modifier is used, the command returns both the fields and their values (interleaved).
- **Performance:** Generally **O(N)** where N is the requested count, but very efficient for small counts.

**Example: Picking a single random field**

```
redis> HMSET coin head "tails" tail "heads" edge "standing"
OK
redis> HRANDFIELD coin
"head"
```

**Example: Picking multiple distinct fields**

```
redis> HRANDFIELD coin 2
1) "tail"
2) "edge"
```

**Example: Picking random fields with values (With Replacement)**

```
redis> HRANDFIELD coin -3 WITHVALUES
1) "head"
2) "tails"
3) "head"
4) "tails"
5) "edge"
6) "standing"
```
