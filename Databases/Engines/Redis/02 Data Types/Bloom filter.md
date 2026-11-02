# Bloom Filters

A **Bloom filter** is a probabilistic set-membership structure: it answers whether an element has been seen before without storing the elements themselves. Like HyperLogLog, it trades exactness for space efficiency, but it answers a different question—membership rather than cardinality. A small, fixed-size bit array can represent millions of items regardless of each item's size, enabling fast checks with little memory.

Its answers are asymmetric:

- **Negative:** The element is definitely not in the filter; standard Bloom filters have no false negatives.
- **Positive:** The element is likely in the filter, but the result has a small chance of being a false positive.

Adding elements sets bits that other elements may share. Standard Bloom filters therefore support insertion and membership checks but generally do not support deletion: clearing an element's bits could also affect other elements. In Redis, Bloom filters are typically provided by the **RedisBloom** module through `BF.` commands; they can also be implemented manually with Bitmaps.

## Use cases

- **Cache penetration:** Requests for nonexistent IDs miss both the cache and database. Large numbers of random IDs can overload the database. If a filter contains all valid IDs, a negative check lets the application return 404 without querying the database; a positive check proceeds to the cache or database because it may be a false positive.
- **Username availability:** A filter containing registered usernames can avoid a database query for every keystroke during registration. A negative check means the username is absent from the filter; a positive check requires a final database check before treating it as taken.
- **Ad frequency capping:** Add `User_ID:Ad_ID` pairs for ads already shown. Check the pair before serving the same ad to that user again.

## RedisBloom commands

`BF.ADD` inserts an item into a filter. It returns `1` when the item's bits changed, suggesting it was not already present, and `0` when those bits were already set, suggesting it was already present:

```sh
redis> BF.ADD processed_users "user_123"
(integer) 1
```

`BF.EXISTS` checks membership. It returns `1` for a possible member (including false positives) and `0` for a definite nonmember:

```sh
redis> BF.ADD crawled_urls "https://google.com"
(integer) 1
redis> BF.EXISTS crawled_urls "https://google.com"
(integer) 1
redis> BF.EXISTS crawled_urls "https://unknown.com"
(integer) 0
```

`BF.RESERVE` creates a filter with a chosen error rate and capacity. If the default error rate of approximately 1% is too high, specify a lower rate when creating the filter; this requires more memory. This example reserves capacity for 100,000 items with a 0.1% false-positive rate:

```sh
redis> BF.RESERVE specific_filter 0.001 100000
OK
```
