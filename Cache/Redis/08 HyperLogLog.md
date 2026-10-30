# HyperLogLog

HyperLogLog (HLL) is a probabilistic data structure that estimates **cardinality**—the number of distinct elements. It suits counts such as daily unique visitors when storing every value is too expensive and an exact result is unnecessary. Redis encodes an HLL as a String: elements update probabilistic registers rather than being retained as retrievable members. You can obtain an estimated count, not list the inputs.

The trade-off is memory versus precision. A Set's memory grows with its members and may reach hundreds of megabytes for millions of values; an HLL uses at most **12 KB** to estimate up to $2^{64}$ distinct elements, with approximately **0.81% standard error**.

## Use cases

- **Unique-visitor analytics:** Count distinct users or IP addresses on a high-traffic site. Storing millions of addresses in a Set can consume gigabytes of RAM, while HLL memory stays within 12 KB for either 100 or 100 million visitors. An analytics dashboard may accept a count such as approximately 10,050,000 instead of an exact 10,042,112.
- **Ad reach:** Add a user or device ID each time an ad is served. The estimate counts unique viewers (reach), unlike the total number of showings (impressions); repeated views by one user do not add distinct users. This supports real-time campaign reporting without heavy database queries.
- **Search-query diversity:** Add search terms to estimate how many distinct keywords were entered in a day. Hashes and probabilistic registers avoid retaining millions of strings of varying lengths in a Set.
- **Time-window rollups:** Use `PFMERGE` to combine daily HLLs into a weekly HLL and then into larger windows such as a month. A user present on multiple days contributes once to the estimated weekly cardinality.

The rollup proceeds in sequence:

1. Create an HLL for each day, such as `stats:day1` and `stats:day2`.
2. Merge the daily structures into `stats:week` at the end of the week.
3. Count the resulting weekly union; a user present on Monday and Tuesday is represented once.

To estimate daily unique IP addresses:

```sh
redis> PFADD visits:2023-10-27 "192.168.0.1" "10.0.0.5" "172.16.0.1"
(integer) 1
redis> PFCOUNT visits:2023-10-27
(integer) 3
```

To merge daily counts into a weekly estimate:

```sh
redis> PFADD day:1 "user_a" "user_b"
(integer) 1
redis> PFADD day:2 "user_b" "user_c"
(integer) 1
redis> PFMERGE week:1 day:1 day:2
OK
redis> PFCOUNT week:1
(integer) 3
```

`user_b` appears on both days but is counted once in the weekly union.

## Adding Elements with `PFADD`

`PFADD` hashes one or more elements and updates the HLL's registers without storing the elements themselves. If the key does not exist, it creates a new HLL. The `PF` prefix refers to Philippe Flajolet, who invented the HyperLogLog algorithm.

- **`1`:** The internal state changed, suggesting at least one element was new.
- **`0`:** The internal state did not change, suggesting the element was already processed.

To add new users:

```sh
redis> PFADD total_users "alice" "bob"
(integer) 1
```

Adding `alice` again leaves the internal state unchanged in this example:

```sh
redis> PFADD total_users "alice"
(integer) 0
```

## Estimating Cardinality with `PFCOUNT`

`PFCOUNT` returns an approximate distinct-element count, with roughly **0.81% standard error**. With multiple keys, such as `PFCOUNT hll1 hll2`, it estimates the union's cardinality without permanently merging the HLLs. This supports ad-hoc counts across sources such as Server A and Server B. For a single key, Redis caches the count in the HLL until new elements are added, making repeated retrieval fast.

To count one HLL:

```sh
redis> PFCOUNT total_users
(integer) 2
```

To count the union of multiple HLLs:

```sh
redis> PFADD group_a "u1" "u2"
(integer) 1
redis> PFADD group_b "u2" "u3"
(integer) 1
redis> PFCOUNT group_a group_b
(integer) 3
```

The union contains three distinct inputs: `u1`, `u2`, and `u3`.

## Merging Structures with `PFMERGE`

`PFMERGE` merges source HLLs into a destination representing their union. It creates the destination if absent; if the destination already exists, its existing data is combined with the sources. The resulting cardinality estimates distinct elements across those structures. Rollups can combine 24 hourly metrics into a daily one or seven daily metrics into a weekly one.

To create a monthly estimate from daily HLLs:

```sh
redis> PFADD daily:01 "userA" "userB"
(integer) 1
redis> PFADD daily:02 "userB" "userC"
(integer) 1
redis> PFMERGE monthly:jan daily:01 daily:02
OK
redis> PFCOUNT monthly:jan
(integer) 3
```
