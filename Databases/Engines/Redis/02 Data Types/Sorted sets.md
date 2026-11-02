# Sorted Sets

A Redis sorted set contains unique string **members**, each associated with a floating-point **score**. It combines set-like uniqueness with a member-to-score mapping. Members appear in ascending score order; equal scores are ordered lexicographically by member string. Thus, changing a score also changes the member's position.

Redis uses a hash table for $O(1)$ lookup of a member's score and a skip list to maintain ordering, supporting range and rank operations. Adding, removing, or updating a member is generally $O(\log N)$, where $N$ is the number of members; this remains efficient for sets with millions of members.

## Use cases

Each use chooses members and scores to exploit score ordering or its lexicographic tie-breaker:

- **Leaderboards:** Store a user ID or username as the member and points as the score. `ZADD` updates a score in $O(\log N)$; `ZRANGE` with `REV` retrieves the top 10, and `ZRANK` gives a player's position. Unlike a SQL `ORDER BY` query over a growing table, the sorted set maintains ranking for efficient real-time reads.
- **Priority queues:** Store a job ID or task as the member and priority as the score (for example, 1 for critical and 10 for low priority). `ZADD` inserts tasks; `ZPOPMIN` removes and returns the lowest-score, highest-priority task. This supports background jobs and bandwidth allocation based on urgency rather than arrival time.
- **Sliding-window rate limiting:** Store a unique request ID (UUID) as the member and its Unix timestamp in milliseconds as the score. This retains each request's time rather than only a counter, giving a more precise moving window—for example, at most five requests per minute.
- **Autocomplete:** Store a word or phrase as the member with every score set to `0`. Equal scores expose lexicographic order; `ZRANGE ... BYLEX` scans prefixes such as `app` for `apple` and `application`.

For a sliding window, the operations have a meaningful order:

1. Add the current request with `ZADD`.
2. Remove requests outside the window with `ZREMRANGEBYSCORE`.
3. Count the remaining requests with `ZCARD`.

For a game leaderboard:

```sh
redis> ZADD leaderboard 500 "Alice" 1200 "Bob" 800 "Charlie"
(integer) 3
redis> ZINCRBY leaderboard 100 "Alice"
"600"
redis> ZRANGE leaderboard 0 1 REV WITHSCORES
1) "Bob"
2) "1200"
3) "Charlie"
4) "800"
```

For a priority queue:

```sh
redis> ZADD queue 1 "fix_critical_bug" 5 "send_email" 10 "cleanup_logs"
(integer) 3
redis> ZPOPMIN queue
1) "fix_critical_bug"
2) "1"
```

For a timestamped request:

```sh
redis> ZADD requests:ip:10.0.0.1 1698300005 "req_id_101"
(integer) 1
```

For alphabetical storage:

```sh
redis> ZADD dictionary 0 "apple" 0 "application" 0 "appetite" 0 "banana" 0 "apricot"
(integer) 5
redis> ZRANGE dictionary "[app" "(apq" BYLEX
1) "appetite"
2) "apple"
3) "application"
```

## Adding Members with `ZADD`

`ZADD` adds the specified member-score pairs. It creates the sorted set if the key does not exist. For an existing member, it updates the score and repositions the member to preserve ordering. Its return value is the number of **new** members added, not the number updated.

The options constrain which members are changed:

- **`NX`:** Add new members without updating existing ones.
- **`XX`:** Update existing members without adding new ones.
- **`GT`:** Update an existing member only if the new score is greater than its current score.
- **`LT`:** Update an existing member only if the new score is less than its current score.

To add two members:

```sh
redis> ZADD leaderboard 100 "Alice" 200 "Bob"
(integer) 2
```

To update only an existing score with `XX`:

```sh
redis> ZADD leaderboard XX 250 "Bob"
(integer) 0
redis> ZSCORE leaderboard "Bob"
"250"
```

## Retrieving Ranges with `ZRANGE`

`ZRANGE` returns members in a selected range. By default, it uses ascending score order and zero-based rank indices: `0` selects the first member, while `-1` selects the last. The result is a list of the selected members.

- **`WITHSCORES`:** Include each member's score in the result.
- **`REV` (Redis 6.2+):** Reverse the order to high-to-low.
- **`BYSCORE` (Redis 6.2+):** Interpret the range arguments as scores rather than rank indices.
- **`BYLEX` (Redis 6.2+):** Interpret the range arguments as lexicographic bounds.

To retrieve the three lowest scores:

```sh
redis> ZADD racers 10 "p1" 20 "p2" 30 "p3"
(integer) 3
redis> ZRANGE racers 0 2
1) "p1"
2) "p2"
3) "p3"
```

To retrieve all members with their scores:

```sh
redis> ZRANGE racers 0 -1 WITHSCORES
1) "p1"
2) "10"
3) "p2"
4) "20"
5) "p3"
6) "30"
```

To retrieve members with scores from 10 to 25:

```sh
redis> ZRANGE racers 10 25 BYSCORE
1) "p1"
2) "p2"
```

To retrieve members lexicographically between `a` and `c`:

```sh
redis> ZADD dictionary 0 "apple" 0 "banana" 0 "cherry" 0 "date"
(integer) 4
redis> ZRANGE dictionary "[a" "[c" BYLEX
1) "apple"
2) "banana"
```

For lexicographic bounds, `[` is inclusive and `(` is exclusive.

> [!note] Earlier lexicographic range command
> `ZRANGEBYLEX` performs this lexicographic range query in older Redis versions. Since Redis 6.2.0, `ZRANGE ... BYLEX` provides the same range mode.

## Incrementing Scores with `ZINCRBY`

`ZINCRBY` changes a member's score by an integer or double-precision floating-point increment. A negative increment decreases it. If the member is absent, its prior score is treated as zero; if the key is absent, Redis creates a sorted set containing that member. The command returns the new score as a string.

To add points to a player:

```sh
redis> ZADD points 100 "User1"
(integer) 1
redis> ZINCRBY points 50 "User1"
"150"
```

To decrease a score with a negative increment:

```sh
redis> ZINCRBY points -20 "User1"
"130"
```

## Finding Position with `ZRANK`

`ZRANK` returns a member's zero-based position in ascending score order: the lowest-scoring member has rank `0`. It returns an integer when the member exists and `(nil)` when the member or key does not exist. For high-to-low rankings, use `ZREVRANK`.

To find a player's position:

```sh
redis> ZADD race 10 "turtle" 50 "human" 80 "cheetah"
(integer) 3
redis> ZRANK race "turtle"
(integer) 0
redis> ZRANK race "cheetah"
(integer) 2
```

For a missing member:

```sh
redis> ZRANK race "snail"
(nil)
```

## Finding Reverse Position with `ZREVRANK`

`ZREVRANK` reverses the ranking: the highest-scoring member has rank `0`. This fits leaderboards where more points mean a better position. It returns an integer for an existing member and `(nil)` if the member or key does not exist.

To find the highest-scoring player's rank:

```sh
redis> ZADD leaderboard 1000 "Alice" 800 "Bob" 500 "Charlie"
(integer) 3
redis> ZREVRANK leaderboard "Alice"
(integer) 0
redis> ZREVRANK leaderboard "Charlie"
(integer) 2
```

## Removing Lowest Scores with `ZPOPMIN`

`ZPOPMIN` atomically removes and returns the `count` lowest-scoring members and their scores. If `count` is omitted, it removes one member. The operation takes members from the low-score end of the ordering.

To process the lowest-scoring job:

```sh
redis> ZADD queue 1 "job_A" 2 "job_B" 3 "job_C"
(integer) 3
redis> ZPOPMIN queue 1
1) "job_A"
2) "1"
redis> ZRANGE queue 0 -1
1) "job_B"
2) "job_C"
```

## Removing Specific Members with `ZREM`

`ZREM` removes the specified members and ignores those that are absent. It returns the number actually removed. If no members remain, Redis deletes the sorted-set key.

To remove a leaderboard member while ignoring a missing member:

```sh
redis> ZADD ranking 100 "user1" 200 "user2" 300 "user3"
(integer) 3
redis> ZREM ranking "user2" "user4"
(integer) 1
redis> ZRANGE ranking 0 -1
1) "user1"
2) "user3"
```

## Deleting Ranges by Lexicography with `ZREMRANGEBYLEX`

`ZREMRANGEBYLEX` removes members within the lexicographic bounds `min` and `max`, returning the number removed. This operation requires all members to have the same score for well-defined lexicographic range behavior; when scores differ, its behavior is unspecified.

- `[` marks an inclusive bound, while `(` marks an exclusive bound.
- `+` and `-` represent positive and negative infinity.

To remove an alphabetical range:

```sh
redis> ZADD contacts 0 "Aaron" 0 "Alex" 0 "Bob" 0 "Charlie" 0 "Dave"
(integer) 5
redis> ZREMRANGEBYLEX contacts "[A" "(C"
(integer) 3
redis> ZRANGE contacts 0 -1
1) "Charlie"
2) "Dave"
```

The exclusive upper bound `(C` removes Aaron, Alex, and Bob while retaining Charlie and Dave.

## Deleting Ranges by Rank with `ZREMRANGEBYRANK`

`ZREMRANGEBYRANK` removes all members from rank `start` through `stop` and returns the number removed. Ranks are zero-based in ascending score order, so rank `0` is the lowest-scoring member; negative ranks count back from the highest, with `-1` at the end. Removing low ranks trims a leaderboard to its top $N$ members, such as the top 10.

To retain the top three members:

In a five-person leaderboard, ranks 0 and 1 are the two lowest scores; ranks 2 through 4 are the top three.

```sh
redis> ZADD ranking 10 "A" 20 "B" 30 "C" 40 "D" 50 "E"
(integer) 5
redis> ZREMRANGEBYRANK ranking 0 -4
(integer) 2
redis> ZRANGE ranking 0 -1
1) "C"
2) "D"
3) "E"
```

With five members, `-4` resolves to rank 1. The inclusive range `0` through `-4` therefore deletes A and B.

## Lexicographical Ordering (Tie-Breaking)

Scores determine the primary order, but equal-score members follow a deterministic lexicographic tie-breaker. For UTF-8-encoded members, Redis compares their byte sequences byte-for-byte: `A` precedes `B`, `apple` precedes `application`, and a shorter prefix such as `be` precedes `bee`. Setting every score to `0` therefore turns the sorted set into an alphabetical index.

With equal scores, members appear in alphabetical order regardless of insertion order:

```sh
redis> ZADD names 0 "David" 0 "Alice" 0 "Bob" 0 "Carol"
(integer) 4
redis> ZRANGE names 0 -1
1) "Alice"
2) "Bob"
3) "Carol"
4) "David"
```

The result is A–Z even though insertion order differed.
