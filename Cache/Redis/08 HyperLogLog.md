# HyperLogLog


*   **Definition:** HyperLogLog is a **probabilistic data structure** used to estimate the **cardinality** of a set (the number of unique elements).
*   **Purpose:** It is designed to count unique things (e.g., "How many unique IPs visited the site today?") where storage space is a constraint and absolute precision is not strictly required.
*   **Storage:** Internally, a HyperLogLog is encoded and stored as a standard **Redis String**.
*   **Memory Efficiency:** This is its primary advantage. While a standard Set requires memory proportional to the number of elements (potentially hundreds of megabytes for millions of items), a HyperLogLog uses a fixed amount of memory: **at most 12 KB**.
*   **Capacity:** A single HLL of 12 KB can approximate the count of practically unlimited items (up to $2^{64}$ elements).
*   **The Trade-off:** HLLs exchange perfect accuracy for memory efficiency. They are not 100% precise; the standard error is approximately **0.81%**.
*   **Behavior:** Conceptually, it behaves like a Set for counting purposes (you "add" items to it), but it **does not store the actual elements**. You cannot retrieve members from an HLL, only the estimated count.

## Use cases

Here are the primary use cases for Redis HyperLogLog.

- Massive Scale Web Analytics (Unique Visitors)
  - **Concept:** Counting distinct users (UVs) or IP addresses visiting a high-traffic website.
  - **The Problem:** On a site with millions of daily visitors, storing every IP address in a standard Redis **Set** would consume gigabytes of RAM.
  - **The HLL Solution:** A HyperLogLog keeps the memory usage at a fixed 12KB, whether you have 100 visitors or 100 million.
  - **Acceptable Error:** For analytics dashboards, knowing you had roughly 10,050,000 visitors (vs. exactly 10,042,112) is usually acceptable.

  - **Example:** Counting Daily IPs
    ```
    redis> PFADD visits:2023-10-27 "192.168.0.1" "10.0.0.5" "172.16.0.1"
    (integer) 1
    redis> PFCOUNT visits:2023-10-27
    (integer) 3
    ```

- Digital Advertising (Ad Reach)
  - **Concept:** Tracking how many **unique** people saw a specific advertisement ("Reach") versus how many times it was shown total ("Impressions").
  - **Mechanism:**
    - Every time an ad is served, send the User ID or Device ID to the HLL.
    - HLL automatically deduplicates multiple views by the same user.
  - **Benefit:** Enables real-time reporting on campaign reach without heavy database queries.

- Search Query Analysis
  - **Concept:** Counting the diversity of search terms entered into a search engine.
  - **Scenario:** You want to know how many *unique* keywords were searched today to understand the breadth of user interest.
  - **Data Volume:** Search terms are strings of varying lengths. Storing millions of long strings in a Set is expensive. HLL hashes them and stores only probabilistic register data, saving massive space.

- Aggregating Time-Based Metrics (Merging)
  - **Concept:** Combining metrics from smaller time windows into larger ones (e.g., Daily $\rightarrow$ Weekly $\rightarrow$ Monthly).
  - **Feature:** The `PFMERGE` command allows you to combine multiple HLLs into one without losing the uniqueness properties.
  - **Mechanism:**
    1. Create an HLL for each day (`stats:day1`, `stats:day2`...).
    2. At the end of the week, merge them into `stats:week`.
    3. This correctly calculates unique users across the whole week (if User A visited on Monday and Tuesday, they are counted only once in the Weekly total).

  - **Example:** Calculating Weekly Uniques
    ```
    redis> PFADD day:1 "user_a" "user_b"
    (integer) 1
    redis> PFADD day:2 "user_b" "user_c"
    (integer) 1
    redis> PFMERGE week:1 day:1 day:2
    OK
    redis> PFCOUNT week:1
    (integer) 3
    ```

		*(Note: "user_b" was present in both days but is only counted once in the weekly total).*

## Adding Elements with `PFADD`

- **Function:** Adds one or more elements to the HyperLogLog stored at the key.
- **Creation:** If the key does not exist, a new HyperLogLog structure is created.
- **Storage:** The command hashes the element and updates the internal registers. It **does not** store the actual data of the element.
- **Origin:** The prefix `PF` stands for *Philippe Flajolet*, the mathematician who invented the HyperLogLog algorithm.
- **Return Value:**
  - `1`: If the internal probabilistic estimate was updated (implies the element is likely new).
  - `0`: If the internal state did not change (implies the element has likely already been processed).

**Example: Adding new items**

```
redis> PFADD total_users "alice" "bob"
(integer) 1
```

**Example: Adding a duplicate (No change)**

```
redis> PFADD total_users "alice"
(integer) 0
```

## Estimating Cardinality with `PFCOUNT`

- **Function:** Returns the approximated cardinality (count of unique elements) of the HyperLogLog stored at the key.
- **Precision:** The result is an approximation with a standard error of roughly **0.81%**.
- **Multi-Key:** You can pass multiple keys to this command (e.g., `PFCOUNT hll1 hll2`).
  - Redis will calculate the cardinality of the **union** of the passed HLLs on the fly.
  - This is useful for ad-hoc queries like "Total unique users from Server A and Server B combined" without permanently merging them.
- **Performance Cache:** For a single key, the count is cached within the HLL structure, making retrieval extremely fast until new elements are added.

**Example: Counting single key**

```
redis> PFCOUNT total_users
(integer) 2
```

**Example: Counting union of multiple keys**

```
redis> PFADD group_a "u1" "u2"
(integer) 1
redis> PFADD group_b "u2" "u3"
(integer) 1
redis> PFCOUNT group_a group_b
(integer) 3
```

*(Explanation: u1, u2, u3 are the 3 unique items combined).*

## Merging Structures with `PFMERGE`

- **Function:** Merges multiple source HyperLogLogs into a single destination HyperLogLog.
- **Logic:** The destination HLL will represent the **Union** of all source HLLs. The resulting cardinality is the count of unique elements across all merged structures.
- **Behavior:**
  - If the `destination` key does not exist, a new one is created.
  - If the `destination` key already exists, the source HLLs are merged *into* it (combining with whatever data was already there).
- **Use Case:** Critical for rolling up analytics, such as combining 24 hourly metrics into 1 daily metric, or 7 daily metrics into 1 weekly metric.

**Example: Creating a monthly report from daily data**

```
redis> PFADD daily:01 "userA" "userB"
(integer) 1
redis> PFADD daily:02 "userB" "userC"
(integer) 1
redis> PFMERGE monthly:jan daily:01 daily:02
OK
redis> PFCOUNT monthly:jan
(integer) 3
```
