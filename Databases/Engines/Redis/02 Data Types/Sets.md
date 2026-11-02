# Sets

A Redis set is an unordered collection of unique strings. It does not preserve insertion order like a list, and its members have no associated fields or values like a hash. Adding a member already present leaves the set unchanged.

```sh
redis> SADD colors "red" "green" "blue" "yellow"
(integer) 4
redis> SMEMBERS colors
1) "yellow"
2) "blue"
3) "red"
4) "green"
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

The set abstraction supports server-side membership checks and set algebra:

- **Membership:** `SISMEMBER` checks whether a member exists in $O(1)$ time, regardless of set size.
- **Intersection:** Members common to sets, such as users who liked both Post A and Post B.
- **Union:** Members in any set, such as users who liked Post A or Post B.
- **Difference:** Members in one set but not another, such as users who liked Post A but not Post B.

A set holds up to $2^{32} - 1$ members—more than four billion.

## Use cases

**Social graphs.** Unique members prevent duplicate follow relationships. Store each user's friends in a separate set, such as `user:1:friends`, then use `SINTER` to find mutual friends or shared interests. The same pattern supports friends-in-common, people-you-may-know, and mutual-follower features.

```sh
redis> SADD alice:friends "bob" "charlie" "dave"
(integer) 3
redis> SADD eve:friends "bob" "dave" "frank"
(integer) 3
redis> SINTER alice:friends eve:friends
1) "dave"
2) "bob"
```

**Unique analytics.** For unique daily visitors or IP addresses, `SADD` adds an ID to a set for the time window, such as `visitors:2023-10-27`. If the same visitor arrives 100 times, the next 99 adds have no effect. `SCARD` returns the distinct-member count, so insertion does not require a database lookup to check whether the visitor was already seen.

```sh
redis> SADD visits:today "192.168.1.1"
(integer) 1
redis> SADD visits:today "192.168.1.2"
(integer) 1
redis> SADD visits:today "192.168.1.1"
(integer) 0
redis> SCARD visits:today
(integer) 2
```

**Access control.** A whitelist or blacklist stores tokens, IP addresses, or usernames and checks each candidate with `SISMEMBER`. The $O(1)$ membership operation applies to both small and very large sets. Applications include revoked JWT tokens, banned IPs, and beta-tester allowlists.

```sh
redis> SADD banned_ips "10.0.0.5" "10.0.0.9"
(integer) 2
redis> SISMEMBER banned_ips "10.0.0.5"
(integer) 1
redis> SISMEMBER banned_ips "192.168.0.1"
(integer) 0
```

**Tagging and categorization.** A set assigns non-repeating labels to an object. Reversing the relationship forms an inverted index: create a set per tag (`tag:news`, `tag:tech`) and add matching article IDs. `SUNION` retrieves articles tagged news *or* tech; `SINTER` retrieves those tagged news *and* tech.

```sh
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

`SADD` adds one or more members, creating the set if its key is absent. Existing members are ignored, and the return value counts only newly added members.

Only new members increase the `SADD` result:

```sh
redis> SADD emails "john@example.com" "jane@example.com"
(integer) 2
redis> SADD emails "john@example.com"
(integer) 0
redis> SMEMBERS emails
1) "john@example.com"
2) "jane@example.com"
```

## Removing Members with `SREM`

`SREM` removes specified members and returns the number actually removed. It ignores absent members and deletes the key when the last member is removed.

Only `db` exists, so one member is removed:

```sh
redis> SADD tags "redis" "db" "nosql"
(integer) 3
redis> SREM tags "db" "unknown_tag"
(integer) 1
redis> SMEMBERS tags
1) "redis"
2) "nosql"
```

## Popping Random Members with `SPOP`

`SPOP` removes and returns random members, fitting lotteries, raffles, or random task selection. Since Redis 3.2, an optional `count` removes and returns an array of distinct members. If the count exceeds the set size, the command returns the whole set and removes its key. A missing key returns `(nil)`.

A single pop removes one randomly selected winner:

```sh
redis> SADD lottery "User A" "User B" "User C"
(integer) 3
redis> SPOP lottery
"User B"
redis> SCARD lottery
(integer) 2
```

A count of two pops two distinct members:

```sh
redis> SADD deck "Ace" "King" "Queen" "Jack"
(integer) 4
redis> SPOP deck 2
1) "Queen"
2) "Ace"
```

## Counting Members with `SCARD`

`SCARD` returns the set's cardinality (member count) in $O(1)$ time because Redis tracks the count in metadata rather than iterating over members. A missing key counts as an empty set and returns `0`.

The populated set contains three members:

```sh
redis> SADD users "alice" "bob" "charlie"
(integer) 3
redis> SCARD users
(integer) 3
```

After the key is deleted, its cardinality is `0`:

```sh
redis> DEL unknown_set
(integer) 1
redis> SCARD unknown_set
(integer) 0
```

## Verifying Membership with `SISMEMBER`

`SISMEMBER` checks one member in $O(1)$ time. It returns the integer `1` for a member and `0` for a nonmember or a missing key.

The check distinguishes a member from a nonmember:

```sh
redis> SADD admins "alice" "bob"
(integer) 2
redis> SISMEMBER admins "alice"
(integer) 1
redis> SISMEMBER admins "charlie"
(integer) 0
```

## Batch Verification with `SMISMEMBER`

`SMISMEMBER`, available since Redis 6.2.0, checks several members in one request instead of making several `SISMEMBER` round trips. It returns `0` or `1` for each requested member in argument order.

The result has one status for each candidate in request order:

```sh
redis> SADD vip_list "john" "jane"
(integer) 2
redis> SMISMEMBER vip_list "john" "mike" "jane"
1) (integer) 1
2) (integer) 0
3) (integer) 1
```

## Listing All Members with `SMEMBERS`

`SMEMBERS` returns every member without a specified order. Its $O(N)$ work, where $N$ is the member count, can block the server on sets with millions of members. For large sets, use `SSCAN` to iterate instead.

All members are returned without a promised order:

```sh
redis> SADD fruits "apple" "banana" "orange"
(integer) 3
redis> SMEMBERS fruits
1) "orange"
2) "banana"
3) "apple"
```

## Iterating Sets with `SSCAN`

`SSCAN` returns small batches from a set instead of returning every member at once like `SMEMBERS`, avoiding one large blocking response. A full cursor iteration proceeds in order:

1. Pass the set `key` and cursor `0`.
2. Use the returned cursor in the next call.
3. Stop when Redis returns cursor `0` again.

The iteration may return duplicates, which the application must handle; a full iteration returns every member present throughout it. Optional `MATCH pattern` filters members with a glob-style pattern such as `user:*`. Optional `COUNT count` hints at the batch size; its default is usually 10.

The first response gives a new cursor and a batch of members:

```sh
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

The first output entry, `"3"`, is the next cursor, so the next call uses `SSCAN user_ids 3`.

A pattern restricts the returned members:

```sh
redis> SADD configs "sys:a" "sys:b" "app:c" "app:d"
(integer) 4
redis> SSCAN configs 0 MATCH "sys:*"
1) "0"
2) 1) "sys:a"
   2) "sys:b"
```

## Sampling Members with `SRANDMEMBER`

Unlike `SPOP`, `SRANDMEMBER` returns random string members without changing the set. A missing key returns `(nil)`. The optional count changes sampling behavior:

- **Positive count:** Returns distinct members, or the entire set if the count exceeds its size.
- **Negative count:** Allows duplicates (sampling with replacement), for example when one person could win multiple draws.

The selected member remains in the set:

```sh
redis> SADD gallery "img1.jpg" "img2.jpg" "img3.jpg"
(integer) 3
redis> SRANDMEMBER gallery
"img2.jpg"
redis> SCARD gallery
(integer) 3
```

A positive count samples without repeats:

```sh
redis> SRANDMEMBER gallery 2
1) "img1.jpg"
2) "img3.jpg"
```

A negative count permits repeats:

```sh
redis> SRANDMEMBER gallery -3
1) "img1.jpg"
2) "img1.jpg"
3) "img2.jpg"
```

## Moving Members with `SMOVE`

`SMOVE` atomically removes a member from `source` and adds it to `destination`; other clients cannot observe an intermediate state. Its result depends on the member's initial state:

- **Present in source:** Remove it from the source and add it to the destination, returning `1`. If it was already in the destination, only the source changes; this is not an error.
- **Absent from source:** Leave both sets unchanged and return `0`.

The move removes `user1` from `candidates` and adds it to `hired`:

```sh
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

An absent source member returns `0`:

```sh
redis> SMOVE candidates hired "unknown_user"
(integer) 0
```

An existing destination member does not prevent removal from the source:

```sh
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

Redis performs set algebra on the server, so clients can filter, combine, and analyze unique-member collections without transferring the input sets. In the expressions below, $A$, $B$, and $C$ denote input sets.

### Combining Sets with `SUNION`

`SUNION` returns a list of members present in at least one input set: $A \cup B \cup C \dots$. Each member appears only once even if several sources contain it. A missing key acts as an empty set.

The union contains each interest once:

```sh
redis> SADD interests:music "jazz" "rock"
(integer) 2
redis> SADD interests:dance "jazz" "ballet"
(integer) 2
redis> SUNION interests:music interests:dance
1) "rock"
2) "ballet"
3) "jazz"
```

An absent input key contributes no members:

```sh
redis> SADD set_a "1" "2"
(integer) 2
redis> SUNION set_a non_existent_set
1) "1"
2) "2"
```

#### Storing Unions with `SUNIONSTORE`

`SUNIONSTORE` stores the union at `destination` instead of returning it to the client, overwriting an existing destination. The command returns the stored set's member count. Keeping a complex union in Redis avoids transferring a large result over the network and supports later reuse.

The stored union collects both product categories:

```sh
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

`SINTER` returns a list of members present in every input set: $A \cap B \cap C \dots$. If any key is missing, its set is empty and so is the intersection.

The intersection contains only followers shared by both sets:

```sh
redis> SADD user:1:follows "user:2" "user:3" "user:4"
(integer) 3
redis> SADD user:5:follows "user:1" "user:3" "user:4"
(integer) 3
redis> SINTER user:1:follows user:5:follows
1) "user:3"
2) "user:4"
```

#### Storing Intersections with `SINTERSTORE`

`SINTERSTORE` stores the intersection at `destination`, overwriting an existing destination, and returns the resulting member count.

The stored intersection keeps only developers who are also gamers:

```sh
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

`SDIFF` returns a list of members in the first input set but not in any subsequent set: $A - B - C \dots$. Unlike union and intersection, key order matters: `SDIFF key1 key2` can differ from `SDIFF key2 key1`. Missing keys act as empty sets.

Subtracting Bob’s skills leaves Alice’s unique skills:

```sh
redis> SADD skills:alice "coding" "design" "marketing"
(integer) 3
redis> SADD skills:bob "coding" "sales"
(integer) 2
redis> SDIFF skills:alice skills:bob
1) "design"
2) "marketing"
```

Reversing the input order leaves Bob’s unique skills:

```sh
redis> SDIFF skills:bob skills:alice
1) "sales"
```

#### Storing Differences with `SDIFFSTORE`

`SDIFFSTORE` stores the difference at `destination`, overwriting an existing destination, and returns the resulting member count. It supports filtering a population, such as users who registered but have not paid.

Subtracting paid users stores the remaining unpaid IDs:

```sh
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
