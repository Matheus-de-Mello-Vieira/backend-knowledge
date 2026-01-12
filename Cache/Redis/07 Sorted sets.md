# Sorted Sets

- **Definition:** A Sorted Set is a collection of unique strings (members), where every member is associated with a floating-point number called a **Score**.
- **Hybrid Structure:** Conceptually, it acts as a mix between a **Set** (unique members) and a **Hash** (mapping a member to a score).
- **Ordering Rules:**
  1. Members are ordered low-to-high based on their **Score**.
  2. If two members have the same score, they are ordered **lexicographically** (alphabetically by the member string).
- **Internal Implementation:** They are implemented using a dual data structure:
  - A **Hash Table** allows for $O(1)$ access to the score of any member.
  - A **Skip List** maintains the order of elements, allowing for extremely fast range queries and rank operations.
- **Performance:** Adding, removing, or updating elements is generally **$O(\log N)$**, making it efficient even for millions of items.

## Use cases

* Real-time Leaderboards (Gaming)

  - **Concept:** The most classic use case. Managing high scores where users are ranked by their points.
    - **Mechanism:**
      - **Member:** User ID / Username.
      - **Score:** The points achieved.
      - **Operations:**
        - `ZADD` updates a player's score (O(log N)).
        - `ZRANGE` with `REV` retrieves the "Top 10" instantly.
        - `ZRANK` gets a specific player's exact position.

  - **Benefit:** Unlike SQL `ORDER BY`, which gets slower as data grows, Redis calculates ranks in real-time efficiently.

  - **Example:** Managing a game high score
      
      ```
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

* Priority Queues

  - **Concept:** A queue where items are processed based on urgency (weight) rather than arrival time.
      - **Mechanism:**
        - **Member:** The Job ID or Task.
        - **Score:** Priority level (e.g., 1 = Critical, 10 = Low).
        - **Operations:**
          - `ZADD` inserts tasks with specific priorities.
          - `ZPOPMIN` removes and returns the item with the lowest score (highest priority).


    - **Application:** Background job processing, bandwidth allocation.



    - **Example:** Processing tasks by urgency
      
        ```
        redis> ZADD queue 1 "fix_critical_bug" 5 "send_email" 10 "cleanup_logs"
        (integer) 3
        redis> ZPOPMIN queue
        1) "fix_critical_bug"
        2) "1"
        ```

* Sliding Window Rate Limiting

  - **Concept:** Limiting the number of actions a user can perform in a moving time window (e.g., "Max 5 requests per minute").
      - **Mechanism:**
        - **Member:** A unique Request ID (UUID).
        - **Score:** The Unix Timestamp (in milliseconds) of the request.
        - **Logic:**
          1. Add current request with `ZADD`.
          2. Remove old requests (outside the window) with `ZREMRANGEBYSCORE`.
          3. Count remaining items with `ZCARD`.


    - **Precision:** More accurate than simple counter-based rate limiting because it tracks the exact time of every request.



    - **Example:** Adding a request timestamp
        
        ```
        redis> ZADD requests:ip:10.0.0.1 1698300005 "req_id_101"
        (integer) 1
        ```


* Autocomplete / Typeahead

  - **Concept:** Searching for words that start with a specific prefix (e.g., typing "app" suggests "apple", "application").
      
      - **Mechanism:**
        - **Member:** The word/phrase.
        - **Score:** Set all scores to `0`.
        - **Ordering:** When scores are tied, Redis sorts elements lexicographically (alphabetically).
        - **Operations:** Use `ZRANGE` with the `BYLEX` argument (or `ZRANGEBYLEX` in older versions) to scan ranges of strings.
      
  - **Example:** Alphabetical storage
      
      ```
      redis> ZADD dictionary 0 "apple" 0 "application" 0 "appetite" 0 "banana" 0 "apricot"
      (integer) 5
      redis> ZRANGE dictionary "[app" "(apq" BYLEX
      1) "appetite"
      2) "apple"
      3) "application"
      ```

## Adding Members with `ZADD`

- **Function:** Adds all the specified members with the specified `score` to the sorted set stored at the key.
- **Update:** If a specified member is already a member of the sorted set, the score is updated and the element reinserted at the right position to ensure the correct ordering.
- **Creation:** If the key does not exist, a new sorted set with the specified members as sole members is created.
- **Arguments:**
  - `NX`: Don't update already existing elements. Always add new elements.
  - `XX`: Only update elements that already exist. Never add new elements.
  - `GT`: Only update existing elements if the new score is **greater than** the current score.
  - `LT`: Only update existing elements if the new score is **less than** the current score.
- **Return Value:** The number of new elements added.

**Example: Basic adding**

```
redis> ZADD leaderboard 100 "Alice" 200 "Bob"
(integer) 2
```

**Example: Updating a score (XX)**

```
redis> ZADD leaderboard XX 250 "Bob"
(integer) 0
redis> ZSCORE leaderboard "Bob"
"250"
```

## Retrieving Ranges with `ZRANGE`

- **Function:** Returns the specified range of elements in the sorted set stored at the key.
- **Order:** The elements are considered to be ordered from the lowest to the highest score (Ascending).
- **Indexing:** Zero-based indices (`0` is the first element, `1` is the next). Negative indices indicate offsets starting at the end of the sorted set (`-1` is the last element).
- **Arguments:**
  - `WITHSCORES`: Includes the score of the element in the returned list.
  - `REV`: (Redis 6.2+) Returns the range in reverse order (high to low).
  - `BYSCORE`: (Redis 6.2+) Treats the range arguments as scores instead of indices.
  - `BYLEX`: (Redis 6.2+) Treats the range arguments as lexicographical strings.
- **Return Value:** List of elements in the specified range.

**Example: Getting the bottom 3 (Lowest scores)**

```
redis> ZADD racers 10 "p1" 20 "p2" 30 "p3"
(integer) 3
redis> ZRANGE racers 0 2
1) "p1"
2) "p2"
3) "p3"
```

**Example: Getting the full list with scores**

```
redis> ZRANGE racers 0 -1 WITHSCORES
1) "p1"
2) "10"
3) "p2"
4) "20"
5) "p3"
6) "30"
```

**Example: Range by Score (Get items with score 10 to 25)**

```
redis> ZRANGE racers 10 25 BYSCORE
1) "p1"
2) "p2"
```

**Example: Range by Lexicographical order (Get items between "a" and "c")**

```
redis> ZADD dictionary 0 "apple" 0 "banana" 0 "cherry" 0 "date"
(integer) 4
redis> ZRANGE dictionary "[a" "[c" BYLEX
1) "apple"
2) "banana"
```

*(Note: `[` indicates inclusive, `(` indicates exclusive).*

## Incrementing Scores with `ZINCRBY`

- **Function:** Increments the score of `member` in the sorted set stored at `key` by `increment`.
- **Initialization:** If `member` does not exist in the sorted set, it is added with `increment` as its score (effectively assuming the previous score was 0).
- **Updates:** If `key` does not exist, a new sorted set with the specified member as its sole member is created.
- **Values:** The `increment` value can be an integer or a double precision floating-point number.
- **Return Value:** The new score of `member` (as a string).

**Example: Adding points to a player**

```
redis> ZADD points 100 "User1"
(integer) 1
redis> ZINCRBY points 50 "User1"
"150"
```

**Example: Decrementing a score (using negative value)**

```
redis> ZINCRBY points -20 "User1"
"130"
```

## Finding Position with `ZRANK`

- **Function:** Returns the **rank** (index) of `member` in the sorted set, with the scores ordered from low to high.
- **Indexing:** The rank (or index) is 0-based, which means that the member with the lowest score has rank `0`.
- **Result:**
  - Returns the integer rank if the member exists.
  - Returns `(nil)` if the member or key does not exist.
- **Inverse:** To get the rank ordered from high to low (e.g., "Who is #1 on the leaderboard?"), use `ZREVRANK`.

**Example: Finding a player's standing**

```
redis> ZADD race 10 "turtle" 50 "human" 80 "cheetah"
(integer) 3
redis> ZRANK race "turtle"
(integer) 0
redis> ZRANK race "cheetah"
(integer) 2
```

**Example: Checking a missing member**

```
redis> ZRANK race "snail"
(nil)
```

## Finding Reverse Position with `ZREVRANK`

- **Function:** Returns the **rank** of `member` in the sorted set, with the scores ordered from **high to low**.
- **Indexing:** The rank is 0-based. The member with the **highest** score has rank `0`.
- **Use Case:** Ideal for leaderboards where "more points" means "better rank" (e.g., getting the Top 1 player).
- **Result:**
  - Returns the integer rank if the member exists.
  - Returns `(nil)` if the member or key does not exist.

**Example: Who is the winner?**

```
redis> ZADD leaderboard 1000 "Alice" 800 "Bob" 500 "Charlie"
(integer) 3
redis> ZREVRANK leaderboard "Alice"
(integer) 0
redis> ZREVRANK leaderboard "Charlie"
(integer) 2
```

## Removing Lowest Scores with `ZPOPMIN`

- **Function:** Removes and returns the `count` members with the **lowest** scores in the sorted set.
- **Default:** If `count` is not specified, it defaults to 1.
- **Behavior:** It atomically pops elements from the "bottom" (left side) of the sorted set.
- **Return Value:** A list containing the removed members and their scores.

**Example: Processing the lowest priority items**

```
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

- **Function:** Removes the specified members from the sorted set stored at `key`.
- **Validation:** Non-existing members are ignored.
- **Result:** Returns the number of members explicitly removed (not counting ignored ones).
- **Cleanup:** If the sorted set becomes empty, the key is automatically deleted.

**Example: Removing users from a leaderboard**

```
redis> ZADD ranking 100 "user1" 200 "user2" 300 "user3"
(integer) 3
redis> ZREM ranking "user2" "user4"
(integer) 1
redis> ZRANGE ranking 0 -1
1) "user1"
2) "user3"
```

## Deleting Ranges by Lexicography with `ZREMRANGEBYLEX`

- **Function:** Removes all members in the sorted set stored at `key` strictly between the lexicographical range specified by `min` and `max`.
- **Condition:** This command only works correctly when **all members in the sorted set have the same score**. If scores vary, the behavior is unspecified (likely incorrect deletion based on score ordering).
- **Syntax:**
  - Starts with `[` for inclusive.
  - Starts with `(` for exclusive.
  - Use `+` and `-` for positive/negative infinity.
- **Return Value:** The number of elements removed.

**Example: Removing alphabetical ranges**

```
redis> ZADD contacts 0 "Aaron" 0 "Alex" 0 "Bob" 0 "Charlie" 0 "Dave"
(integer) 5
redis> ZREMRANGEBYLEX contacts "[A" "(C"
(integer) 3
redis> ZRANGE contacts 0 -1
1) "Charlie"
2) "Dave"
```

*(Removed Aaron, Alex, and Bob; kept Charlie and Dave).*

## Deleting Ranges by Rank with `ZREMRANGEBYRANK`

- **Function:** Removes all members in the sorted set stored at `key` with a **rank** between `start` and `stop`.
- **Indexing:** Zero-based indices with `0` being the element with the lowest score. Negative indices are supported (`-1` is the highest score).
- **Use Case:** Trimming a leaderboard to keep only the top N players (e.g., delete everyone *except* the top 10).
- **Return Value:** The number of elements removed.

**Example: Keeping only the Top 3 (Removing everyone else)**

*Assume a leaderboard of 5 people. Ranks 0, 1 are low scores. Ranks 2, 3, 4 are high scores.*

```
redis> ZADD ranking 10 "A" 20 "B" 30 "C" 40 "D" 50 "E"
(integer) 5
redis> ZREMRANGEBYRANK ranking 0 -4
(integer) 2
redis> ZRANGE ranking 0 -1
1) "C"
2) "D"
3) "E"
```

*(Explanation: Indices 0 to -4 means "From the first element up to the 4th-to-last element". In a 5-item list, -4 is index 1. So it deletes index 0 and 1 ("A" and "B").)*

## Lexicographical Ordering (Tie-Breaking)

In a Redis Sorted Set, the Score is the primary sorting key. However, when multiple members share the **exact same score**, Redis does not leave their order undefined. Instead, it applies a deterministic tie-breaking rule:

- **Mechanism:** Members with identical scores are sorted **lexicographically** (effectively alphabetically) based on their UTF-8 byte sequence.
- **Significance:** This allows Sorted Sets to be used as purely alphabetical indexes by setting all scores to `0`.
- **Sorting Rule:**
  - Comparison is byte-for-byte.
  - "A" comes before "B".
  - "apple" comes before "application".
  - Shorter strings come before longer strings if one is a prefix of the other (e.g., "be" comes before "bee").

**Example: Automatic alphabetical sorting**

```
redis> ZADD names 0 "David" 0 "Alice" 0 "Bob" 0 "Carol"
(integer) 4
redis> ZRANGE names 0 -1
1) "Alice"
2) "Bob"
3) "Carol"
4) "David"
```

*(Notice how the order is A-Z automatically, even though the order of insertion was random.)*