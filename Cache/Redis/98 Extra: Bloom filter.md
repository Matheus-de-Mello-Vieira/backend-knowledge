# Bloom Filters

- **Definition:** A Bloom Filter is a **probabilistic data structure** used to verify **membership** in a set (checking if an element is present).
- **Purpose:** It answers the question "Have I seen this item before?" extremely fast and with very little memory.
- **Efficiency:** Like HyperLogLog, it is space-efficient. It can represent a set of millions of items using a small, fixed-size bit array, regardless of the size of the elements themselves.
- **The Trade-off:**
  - **No False Negatives:** If the filter says "No", the element is **definitely not** in the set. (100% confidence).
  - **Possible False Positives:** If the filter says "Yes", the element is **likely** in the set, but there is a small probability it is not.
- **Implementation:** In Redis, this is typically available via the **RedisBloom** module (commands starting with `BF.`) or can be manually implemented using Bitmaps.
- **Behavior:** You can add elements and check for existence, but you generally **cannot delete** elements (in standard implementations) because removing one item might disturb the bits representing other items.

## Use Cases

* Preventing Cache Penetration
  - **Concept:** Preventing requests for non-existent keys from hitting your database.

  - **Problem:** Malicious users might query for millions of random IDs that don't exist. Your application checks the cache (miss) $\to$ checks the DB (miss). This crashes the DB.

  - **Solution:** Store all valid IDs in a Bloom Filter. When a request comes in, check the filter first.
    - If Filter says "No": Return 404 immediately. Don't touch the DB.
      - If Filter says "Yes": Check Cache/DB.
* Username Availability

  - **Concept:** Checking if a username is already taken during registration.

  - **Efficiency:** Instead of querying the `users` table for every keystroke, check a Bloom Filter containing all registered usernames.
    - "No" means the username is definitely available.
      - "Yes" means it's likely taken (do a final DB check to confirm).
* Ad Serving (Frequency Capping)
  - **Concept:** Avoiding showing the same ad to a user who has already seen it.
  - **Mechanism:** Store `User_ID:Ad_ID` pairs in a filter. Before serving an ad, check if it exists in the filter.

## Adding Elements with `BF.ADD`

- **Function:** Adds an item to the Bloom Filter.
- **Return:**
  - `1`: If the item was likely not present (bits were modified).
  - `0`: If the item was arguably already present (bits were already set).

**Example: Marking a user as "processed"**

```
redis> BF.ADD processed_users "user_123"
(integer) 1
```

## Checking Existence with `BF.EXISTS`

- **Function:** Checks if an item exists in the filter.
- **Return:**
  - `1`: **Likely** exists (False positive possible).
  - `0`: **Definitely** does not exist (100% certain).

**Example: Checking if a URL has been crawled**

```
redis> BF.ADD crawled_urls "https://google.com"
(integer) 1
redis> BF.EXISTS crawled_urls "https://google.com"
(integer) 1
redis> BF.EXISTS crawled_urls "https://unknown.com"
(integer) 0
```

## `BF.RESERVE` (Custom Configuration)

- **Function:** Creates a filter with a specific error rate and capacity.
- **Why use it?** The default error rate is usually 1% (0.01). If you need higher precision (e.g., 0.1%), you must reserve it upfront.
- **Trade-off:** Lower error rates require more memory.

**Example: Creating a high-precision filter**

```
redis> BF.RESERVE specific_filter 0.001 100000
OK
```

*(Creates a filter for 100k items with a 0.1% false positive rate).*