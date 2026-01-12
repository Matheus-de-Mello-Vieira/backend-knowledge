# Sets

- **Definition:** A Redis Set is an **unordered collection** of unique strings. Unlike a List, it does not maintain insertion order, and unlike a Hash, it has no keys or values—just distinct members.

  ```
  redis> SADD colors "red" "green" "blue" "yellow"
  (integer) 4
  redis> SMEMBERS colors
  1) "yellow"
  2) "blue"
  3) "red"
  4) "green"
  ```

- **Uniqueness:** Sets automatically enforce uniqueness. Adding the same element multiple times has no effect (duplicates are ignored).

  ```
  redis> SADD tags "news" "tech"
  (integer) 2
  redis> SADD tags "tech"
  (integer) 0
  redis> SADD tags "news" "sports"
  (integer) 1
  redis> SMEMBERS tags
  1) "news"
  2) "sports"
  3) "tech"
  ```

- **Set Algebra:** Redis Sets support server-side mathematical set operations, making them incredibly powerful for analytics:

  - **Intersection:** Find common members between sets (e.g., "users who liked Post A AND Post B").
  - **Union:** Combine members from multiple sets (e.g., "all users who liked Post A OR Post B").
  - **Difference:** Find members in one set but not another (e.g., "users who liked Post A BUT NOT Post B").

- **Membership Checks:** Testing if a specific element exists in a Set (`SISMEMBER`) is extremely fast (**O(1)**), regardless of the set's size.

- **Capacity:** A single Set can hold more than **4 billion members** ($2^{32} - 1$).

## Use cases

* Social Graph (Common Friends/Followers)

  - **Concept:** managing relationships between users where uniqueness is required (you can't follow the same person twice).

  - **Power Feature:** The **Intersection** (`SINTER`) operation allows you to instantly calculate "mutual friends" or "shared interests" between two users.
    - **Mechanism:**
      - Store each user's friends in a separate Set (`user:1:friends`).
      - Use `SINTER` to find the overlap.

  - **Application:** "Friends in common," "People you may know," mutual followers.

  * **Example:** Finding mutual friends
    ```
    redis> SADD alice:friends "bob" "charlie" "dave"
    (integer) 3
    redis> SADD eve:friends "bob" "dave" "frank"
    (integer) 3
    redis> SINTER alice:friends eve:friends
    1) "dave"
    2) "bob"
    ```

* Unique Analytics (Real-time Visitors)

  - **Concept:** Tracking metrics where duplicates must be ignored, such as "Unique Daily Visitors" or "Unique IPs."
      - **Mechanism:**
        - Simply `SADD` the User ID or IP address to a key representing the time window (e.g., `visitors:2023-10-27`).
        - If the user visits 100 times, `SADD` ignores the subsequent 99 adds.
        - Use `SCARD` (Set Cardinality) to get the total count.


  - **Benefit:** No need to query the database to check "has this user visited today?" before inserting.

  - **Example:** Tracking unique IPs
    
      ```
      redis> SADD visits:today "192.168.1.1"
      (integer) 1
      redis> SADD visits:today "192.168.1.2"
      (integer) 1
      redis> SADD visits:today "192.168.1.1"
      (integer) 0
      redis> SCARD visits:today
      (integer) 2
      ```


* Access Control (Blacklists/Whitelists)

  - **Concept:** High-speed security checks to determine if a token, IP, or username is allowed or banned.

  - **Performance:** `SISMEMBER` is **O(1)**. Checking a set with 10 million banned IPs takes the same amount of time as checking a set with 10.

  - **Application:** Revoked JWT tokens, banned IP addresses, beta-tester whitelists.

  - **Example:**Checking a blacklist
      ```
      redis> SADD banned_ips "10.0.0.5" "10.0.0.9"
      (integer) 2
      redis> SISMEMBER banned_ips "10.0.0.5"
      (integer) 1
      redis> SISMEMBER banned_ips "192.168.0.1"
      (integer) 0
      ```


* Tagging and Categorization

  - **Concept:** assigning multiple non-repeating labels to an object.

  - **Inverted Index:** You can reverse the relationship to find "All objects with Tag X."
      - **Mechanism:**
        - Create a Set for every tag (e.g., `tag:news`, `tag:tech`).
        - Add article IDs to these sets.
        - Use `SUNION` to find articles that are in "News" OR "Tech".
        - Use `SINTER` to find articles that are in "News" AND "Tech".

  - **Example:** Filtering by tags
    
      ```
      redis> SADD tag:action "movie:1" "movie:2"
      (integer) 2
      redis> SADD tag:comedy "movie:2" "movie:3"
      (integer) 2
      redis> SINTER tag:action tag:comedy
      1) "movie:2"
      redis> SUNION tag:action tag:comedy
      1) "movie:1"
      2) "movie:2"
      3) "movie:3"
      ```

## Adding Members with `SADD`

- **Function:** Adds the specified member(s) to the set stored at the key.
- **Creation:** If the key does not exist, a new set is created.
- **Uniqueness:** If a specified member is already a member of the set, it is ignored.
- **Return Value:** Returns the number of elements that were added to the set (excluding members that were already present).

**Example: Adding new and existing members**

```
redis> SADD emails "john@example.com" "jane@example.com"
(integer) 2
redis> SADD emails "john@example.com"
(integer) 0
redis> SMEMBERS emails
1) "john@example.com"
2) "jane@example.com"
```

## Removing Members with `SREM`

- **Function:** Removes the specified members from the set stored at the key.
- **Validation:** If a specified member is not a member of the set, it is ignored.
- **Cleanup:** If the set becomes empty after the removal, the key is deleted.
- **Return Value:** Returns the number of members that were actually removed from the set.

**Example: removing specific items**

```
redis> SADD tags "redis" "db" "nosql"
(integer) 3
redis> SREM tags "db" "unknown_tag"
(integer) 1
redis> SMEMBERS tags
1) "redis"
2) "nosql"
```

## Popping Random Members with `SPOP`

- **Function:** Removes and returns one or more **random** members from the set.
- **Use Case:** Ideal for implementing lotteries, raffles, or picking a random task from a pool.
- **Count Argument:** (Redis 3.2+) You can specify an optional `count` argument.
  - If `count` is provided, it removes and returns an array of distinct elements.
  - If `count` exceeds the set size, it returns the entire set and empties the key.
- **Return Value:** The removed member(s), or `(nil)` if the key does not exist.

**Example: Picking a winner (Single Pop)**

```
redis> SADD lottery "User A" "User B" "User C"
(integer) 3
redis> SPOP lottery
"User B"
redis> SCARD lottery
(integer) 2
```

**Example: Picking a group (Multi Pop)**

```
redis> SADD deck "Ace" "King" "Queen" "Jack"
(integer) 4
redis> SPOP deck 2
1) "Queen"
2) "Ace"
```

## Counting Members with `SCARD`

- **Function:** Returns the set cardinality (number of elements) of the set stored at the key.
- **Performance:** This is an **O(1)** operation. Redis tracks the count in the set's metadata, so it does not need to iterate through the members.
- **Missing Keys:** If the key does not exist, it is interpreted as an empty set and returns `0`.

**Example: getting the size of a populated set**

```
redis> SADD users "alice" "bob" "charlie"
(integer) 3
redis> SCARD users
(integer) 3
```

**Example: checking a non-existent key**

```
redis> DEL unknown_set
(integer) 1
redis> SCARD unknown_set
(integer) 0
```

## Verifying Membership with `SISMEMBER`

- **Function:** Checks if a specific `member` exists within the set stored at the key.
- **Performance:** extremely fast **O(1)** check.
- **Return Value:** Returns a boolean integer:
  - `1` if the element is a member of the set.
  - `0` if the element is not a member, or if the key does not exist.

**Example: checking single status**

```
redis> SADD admins "alice" "bob"
(integer) 2
redis> SISMEMBER admins "alice"
(integer) 1
redis> SISMEMBER admins "charlie"
(integer) 0
```

## Batch Verification with `SMISMEMBER`

- **Function:** Checks for the existence of multiple members in the set at once.
- **Availability:** Available since Redis 6.2.0.
- **Efficiency:** More efficient than running multiple `SISMEMBER` commands because it reduces network round-trips.
- **Return Value:** Returns a list of integers (0 or 1) corresponding to the membership status of each requested element, in the same order as the arguments.

**Example: checking multiple candidates**

```
redis> SADD vip_list "john" "jane"
(integer) 2
redis> SMISMEMBER vip_list "john" "mike" "jane"
1) (integer) 1
2) (integer) 0
3) (integer) 1
```

## Listing All Members with `SMEMBERS`

- **Function:** Returns all the members of the set value stored at the key.
- **Performance Warning:** This is an **O(N)** command. Running this on sets with millions of members can block the server. For large sets, use `SSCAN` instead.
- **Order:** The members are returned in no specific order.

**Example: retrieving the full collection**

```
redis> SADD fruits "apple" "banana" "orange"
(integer) 3
redis> SMEMBERS fruits
1) "orange"
2) "banana"
3) "apple"
```

## Iterating Sets with `SSCAN`

- **Function:** Incrementally iterates through the members of a Set.
- **Purpose:** A non-blocking alternative to `SMEMBERS`. While `SMEMBERS` returns all elements at once (which can freeze the server if the set is huge), `SSCAN` returns a small batch of elements at a time.
- **Cursor:** It uses a cursor-based approach. You start with cursor `0`, and Redis returns a new cursor to use in the next call. The iteration is complete when the returned cursor is `0` again.
- **Guarantees:**
  - It may return duplicate elements (application logic must handle this).
  - It guarantees to return all elements present in the collection from the start to the end of a full iteration.
- **Arguments:**
  - `key`: The set to scan.
  - `cursor`: The integer cursor (start with 0).
  - `MATCH pattern` (optional): Filter elements using a glob-style pattern (e.g., `user:*`).
  - `COUNT count` (optional): A hint for how many elements to return per batch (default is usually 10).

**Example: Scanning a set in batches**

```
redis> SADD user_ids 1 2 3 4 5 6 7 8 9 10 11 12
(integer) 12
redis> SSCAN user_ids 0 COUNT 5
1) "3"
2) 1) "1"
   2) "2"
   3) "5"
   4) "9"
   5) "12"
   6) "6"
```

*(Note: The first line of the output `"3"` is the next cursor. You would use `SSCAN user_ids 3` next.)*

**Example: Scanning with a pattern match**

```
redis> SADD configs "sys:a" "sys:b" "app:c" "app:d"
(integer) 4
redis> SSCAN configs 0 MATCH "sys:*"
1) "0"
2) 1) "sys:a"
   2) "sys:b"
```

## Sampling Members with `SRANDMEMBER`

- **Function:** Returns one or more random members from the set *without* removing them.
- **Comparison:** Unlike `SPOP`, the set remains unchanged.
- **Count Argument:**
  - **Positive Count (`> 0`):** Returns an array of `count` **distinct** elements. If `count` is larger than the set size, it returns the entire set.
  - **Negative Count (`< 0`):** Returns an array of `count` elements, allowing **duplicates** (sampling with replacement). This is useful if you need to pick a random winner multiple times where the same person *could* win twice.
- **Return Value:** The randomly selected string(s), or `(nil)` if the key does not exist.

**Example: getting a single random preview**

```
redis> SADD gallery "img1.jpg" "img2.jpg" "img3.jpg"
(integer) 3
redis> SRANDMEMBER gallery
"img2.jpg"
redis> SCARD gallery
(integer) 3
```

**Example: getting distinct samples (no repeats)**

```
redis> SRANDMEMBER gallery 2
1) "img1.jpg"
2) "img3.jpg"
```

**Example: getting samples with replacement (repeats allowed)**

```
redis> SRANDMEMBER gallery -3
1) "img1.jpg"
2) "img1.jpg"
3) "img2.jpg"
```

## Moving Members with `SMOVE`

- **Function:** Atomically moves a member from a `source` set to a `destination` set.
- **Atomicity:** The operation is atomic. If the member is removed from the source, it is guaranteed to be added to the destination; no intermediate state is visible to other clients.
- **Conditions:**
  - If the element exists in `source`, it is removed and added to `destination`.
  - If the element does *not* exist in `source`, no operation is performed, and `0` is returned.
  - If the element already exists in `destination`, it is just removed from `source` (no error).
- **Return Value:**
  - `1` if the element was moved.
  - `0` if the element was not found in the source set.

**Example: Promoting a user**

```
redis> SADD candidates "user1" "user2"
(integer) 2
redis> SADD hired "user3"
(integer) 1
redis> SMOVE candidates hired "user1"
(integer) 1
redis> SMEMBERS candidates
1) "user2"
redis> SMEMBERS hired
1) "user3"
2) "user1"
```

**Example: Moving a non-existent member**

```
redis> SMOVE candidates hired "unknown_user"
(integer) 0
```

**Example: Moving to a set where the member already exists**

```
redis> SADD candidates "alice" "bob"
(integer) 2
redis> SADD hired "alice" "charlie"
(integer) 2
redis> SMOVE candidates hired "alice"
(integer) 1
redis> SMEMBERS candidates
1) "bob"
redis> SMEMBERS hired
1) "alice"
2) "charlie"
```

## Mathematical Set Operations

Redis Sets natively implement fundamental set algebra, enabling high-performance server-side logic to filter, combine, and analyze relationships between different collections of unique data without transferring the datasets to the client.

### Combining Sets with `SUNION`

- **Function:** Returns the members of the set resulting from the **union** of all the given sets.
- **Math Logic:** Effectively performs $A \cup B \cup C \dots$ (elements present in at least one of the sets).
- **Duplicates:** Since sets enforce uniqueness, the resulting list will contain each distinct member exactly once, even if it appeared in multiple source sets.
- **Missing Keys:** Non-existent keys are treated as empty sets.
- **Return Value:** A list of all unique members from the combined sets.

**Example: Merging user interests**

```
redis> SADD interests:music "jazz" "rock"
(integer) 2
redis> SADD interests:dance "jazz" "ballet"
(integer) 2
redis> SUNION interests:music interests:dance
1) "rock"
2) "ballet"
3) "jazz"
```

**Example: Union with an empty set**

```
redis> SADD set_a "1" "2"
(integer) 2
redis> SUNION set_a non_existent_set
1) "1"
2) "2"
```

#### Storing Unions with `SUNIONSTORE`

- **Function:** Computes the union of the given sets (like `SUNION`) but **stores** the result in a `destination` key instead of returning it to the client.
- **Overwrite:** If the `destination` key already exists, it is overwritten.
- **Performance:** ideal for caching complex calculations. Instead of transferring a large result set over the network, you save it directly in Redis for later use.
- **Return Value:** The number of elements in the newly stored set.

**Example: Creating a 'master' category**

```
redis> SADD products:electronics "laptop" "phone"
(integer) 2
redis> SADD products:books "novel" "biography"
(integer) 2
redis> SUNIONSTORE products:all products:electronics products:books
(integer) 4
redis> SMEMBERS products:all
1) "laptop"
2) "phone"
3) "novel"
4) "biography"
```

### Finding Commonality with `SINTER`

- **Function:** Returns the members of the set resulting from the **intersection** of all the given sets.
- **Math Logic:** Effectively performs $A \cap B \cap C \dots$ (elements present in **all** specified sets).
- **Missing Keys:** If any of the keys do not exist (empty set), the result is an empty set (since the intersection with an empty set is empty).
- **Return Value:** A list of members common to all sets.

**Example: Finding mutual followers**

```
redis> SADD user:1:follows "user:2" "user:3" "user:4"
(integer) 3
redis> SADD user:5:follows "user:1" "user:3" "user:4"
(integer) 3
redis> SINTER user:1:follows user:5:follows
1) "user:3"
2) "user:4"
```

#### Storing Intersections with `SINTERSTORE`

- **Function:** Computes the intersection (like `SINTER`) but **stores** the result in a `destination` key.
- **Overwrite:** Overwrites the destination key if it exists.
- **Return Value:** The number of elements in the resulting set.

**Example: Saving the target audience**

```
redis> SADD group:gamers "alice" "bob" "dave"
(integer) 3
redis> SADD group:developers "bob" "dave" "frank"
(integer) 3
redis> SINTERSTORE target:dev_gamers group:gamers group:developers
(integer) 2
redis> SMEMBERS target:dev_gamers
1) "bob"
2) "dave"
```

### Finding Differences with `SDIFF`

- **Function:** Returns the members of the set resulting from the **difference** between the first set and all successive sets.
- **Math Logic:** Effectively performs $A - B - C \dots$ (elements present in the **first** set but **not** in any of the others).
- **Order Matters:** Unlike Union and Intersection, the order of keys is critical. `SDIFF key1 key2` produces a different result than `SDIFF key2 key1`.
- **Missing Keys:** Non-existent keys are treated as empty sets.
- **Return Value:** A list of members remaining after the subtraction.

**Example: Finding unique skills (Alice minus Bob)**

```
redis> SADD skills:alice "coding" "design" "marketing"
(integer) 3
redis> SADD skills:bob "coding" "sales"
(integer) 2
redis> SDIFF skills:alice skills:bob
1) "design"
2) "marketing"
```

**Example: Reversing the order (Bob minus Alice)**

```
redis> SDIFF skills:bob skills:alice
1) "sales"
```

#### Storing Differences with `SDIFFSTORE`

- **Function:** Computes the difference (like `SDIFF`) but **stores** the result in a `destination` key.
- **Overwrite:** If the `destination` key already exists, it is overwritten.
- **Use Case:** Ideal for filtering lists, such as finding "Users who have registered but not yet paid."
- **Return Value:** The number of elements in the resulting set.

**Example: Filtering unpaid users**

```
redis> SADD all_users "u1" "u2" "u3" "u4"
(integer) 4
redis> SADD paid_users "u1" "u3"
(integer) 2
redis> SDIFFSTORE unpaid_users all_users paid_users
(integer) 2
redis> SMEMBERS unpaid_users
1) "u2"
2) "u4"
```
