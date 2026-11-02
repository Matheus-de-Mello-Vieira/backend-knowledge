# Bitmaps

Redis bitmaps represent Boolean flags as individual bits in [strings](Strings.md), not as a separate Redis value type. An application assigns each entity a stable integer offset; a bit value of `1` records that the entity satisfies a condition, while `0` records that it does not.

- **Addressing:** Offsets are zero-based. Within each byte, offset `0` selects the most significant bit, offset `7` the least significant bit, and offset `8` starts the next byte.
- **Capacity:** Bit offsets must be nonnegative and smaller than $2^{32}$, giving a maximum bitmap size of 512 MiB.
- **Storage:** Memory follows the highest allocated offset, not the number of bits set to `1`. Dense integer identifiers fit this representation better than sparse, very large identifiers.

## Use cases

- **Daily activity:** Store one bitmap per day and use a user identifier as the offset. Repeated activity sets the same bit rather than counting the user again.
- **Cohort comparisons:** Combine daily bitmaps to identify users active on every selected day or on at least one selected day.
- **Boolean status:** Track bounded populations of enabled features, completed tasks, or available resources with one flag per offset.

Exact membership requires a collision-free mapping from entities to offsets. Hashing arbitrary identifiers into a bounded bitmap introduces collisions; a [Bloom filter](Bloom%20filter.md) uses probabilistic membership semantics rather than preserving exact identity.

## Setting and reading bits with `SETBIT` and `GETBIT`

`SETBIT key offset value` writes `0` or `1` and returns the **previous bit**, not the new value. If necessary, Redis creates or extends the string and initializes the added bits to zero. `GETBIT key offset` returns the current bit; a missing key or an offset beyond the string length reads as `0` without allocating storage.

The examples use initially absent keys. User offsets `2` and `5` become active in the first day's bitmap:

```sh
redis> SETBIT activity:day1 2 1
(integer) 0
redis> SETBIT activity:day1 5 1
(integer) 0
redis> GETBIT activity:day1 2
(integer) 1
redis> GETBIT activity:day1 100
(integer) 0
```

Setting an already-set bit returns `1`. Clearing it also returns `1`, because both replies describe the value before the write:

```sh
redis> SETBIT activity:day1 2 1
(integer) 1
redis> SETBIT activity:day1 2 0
(integer) 1
redis> GETBIT activity:day1 2
(integer) 0
```

> [!warning] High offsets allocate intervening storage
> Writing a distant offset grows the string through that position, even when writing `0`. Initial allocation and zero-filling can block the server while the string grows. Clearing a bit does not shrink the string. Although individual bit access is documented as $O(1)$, allocation cost matters when extending a bitmap.

## Counting set bits with `BITCOUNT`

`BITCOUNT key` counts bits equal to `1`, not allocated bits or bytes. It returns `0` for a missing key. Counting scans the selected data and is $O(N)$, where $N$ is the amount of string data examined.

Restoring user `2` leaves two active users, even after repeated activity from user `5`:

```sh
redis> SETBIT activity:day1 2 1
(integer) 0
redis> SETBIT activity:day1 5 1
(integer) 1
redis> BITCOUNT activity:day1
(integer) 2
```

`BITCOUNT key start end [BYTE | BIT]` restricts the count to an inclusive range. Without a unit, the indexes address **bytes**, not bits. Negative indexes count backward from the end. The explicit `BYTE` and `BIT` options require Redis 7.0 or later.

The first byte contains both active bits, but bit offsets `0` through `3` contain only user `2`:

```sh
redis> BITCOUNT activity:day1 0 0
(integer) 2
redis> BITCOUNT activity:day1 0 3 BIT
(integer) 1
```

## Combining bitmaps with `BITOP`

`BITOP operation destination source [source ...]` applies a bitwise operation and stores the result in the destination, replacing its previous value. It returns the result's length in **bytes**, not its number of set bits. All source bitmaps must use the same entity-to-offset mapping for the result to represent meaningful membership.

- **`AND`:** A result bit is `1` only when every source has that bit set.
- **`OR`:** A result bit is `1` when at least one source has that bit set.
- **`XOR`:** A result bit is `1` when an odd number of sources have that bit set. With two sources, this selects bits that differ.
- **`NOT`:** Inverts every stored bit in one source; this operation accepts exactly one source.

For `AND`, `OR`, and `XOR`, the result has the length of the longest source. Shorter sources are zero-padded, and missing sources are treated as empty strings. `NOT` preserves the source length: it inverts padding bits too, so its result is not automatically the complement of a logical population smaller than the allocated bit range.

The second day contains users `5` and `7`. Each day's bitmap occupies one byte:

```sh
redis> SETBIT activity:day2 5 1
(integer) 0
redis> SETBIT activity:day2 7 1
(integer) 0
```

Intersection retains user `5`, who was active on both days. `BITCOUNT` measures membership separately from `BITOP`'s byte-length reply:

```sh
redis> BITOP AND activity:both activity:day1 activity:day2
(integer) 1
redis> BITCOUNT activity:both
(integer) 1
redis> GETBIT activity:both 5
(integer) 1
```

Union retains users `2`, `5`, and `7`, who were active on either day:

```sh
redis> BITOP OR activity:either activity:day1 activity:day2
(integer) 1
redis> BITCOUNT activity:either
(integer) 3
```

`BITOP` scans bitmap data, so large strings make combinations more expensive than individual bit reads or writes. Materializing a result also consumes destination storage. In Redis Cluster, source and destination keys for a multi-key operation must share a hash slot; the example key names assume a non-clustered server.

## Finding a bit with `BITPOS`

`BITPOS key bit [start [end [BYTE | BIT]]]` finds the first `0` or `1` and returns its absolute bit offset, even when searching a range. Range endpoints are inclusive and address bytes by default; `BIT` selects bit indexes instead. The explicit `BYTE` and `BIT` options require Redis 7.0 or later. Negative indexes count backward from the end. Searching scans data and is $O(N)$ in the amount examined.

The first day's bitmap still contains users `2` and `5`. Restricting the search to bit offsets `3` through `7` skips user `2` but returns user `5`'s absolute offset:

```sh
redis> BITPOS activity:day1 1
(integer) 2
redis> BITPOS activity:day1 1 3 7 BIT
(integer) 5
redis> BITPOS activity:day1 1 6 7 BIT
(integer) -1
```

Searching for zero has an important boundary distinction:

- **Without an explicit end:** Redis treats the string's right side as zero-padded. If every stored bit is `1`, the first zero is just beyond the stored string; the search does not allocate that bit.
- **With both start and end:** The search stays within the specified range and returns `-1` when that range contains no zero.
- **Missing key without a range:** Searching for `0` returns `0`; searching for `1` returns `-1`.

Starting with an absent `flags:full` key, writing `0` at offset `7` creates one zero byte. Inverting that byte sets all eight bits. An unbounded zero search reaches offset `8`, but a search bounded to the first byte finds no zero:

```sh
redis> SETBIT flags:full 7 0
(integer) 0
redis> BITOP NOT flags:full flags:full
(integer) 1
redis> BITPOS flags:full 0
(integer) 8
redis> BITPOS flags:full 0 0 0
(integer) -1
```

A zero search therefore needs an explicit end when only a bounded population of offsets represents valid entities.
