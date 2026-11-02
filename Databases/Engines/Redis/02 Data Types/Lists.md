# Lists

Redis lists are ordered sequences of string elements, including elements that represent numbers or serialized objects. `LPUSH` adds at the head and `RPUSH` at the tail, so insertion and removal at the chosen ends produce FIFO queues or LIFO stacks.

- **Capacity:** A list holds up to $2^{32}-1$ elements—more than four billion.
- **End operations:** Adding at the head or tail is $O(1)$, including for large lists.
- **Indexed access:** Finding an element in the middle requires traversal and is $O(N)$ in the list length.
- **Representation:** Redis uses a linked-node-oriented representation rather than an array and applies compact encodings such as `listpack` to reduce memory use. The exact encoding is an implementation detail.

## Use cases

- **Job queue:** A producer adds work with `LPUSH`, and a consumer takes it with `RPOP`. This buffers and decouples tasks such as sending email, encoding video, or resizing images. `BRPOP` waits for work on a blocked connection instead of polling.
- **Capped recent-activity feed:** Push a new event with `LPUSH`, then use `LTRIM key 0 99` to retain the latest 100. This gives fast recent-history reads for timelines, profile visits, or server logs without querying a relational database.
- **Processing queue:** `LMOVE` atomically transfers a job from the pending queue to a processing list. If a worker fails, the job remains in processing for analysis or re-queuing. This supports critical work such as orders or financial transactions.
- **Circular list:** `LMOVE source source LEFT RIGHT` rotates the head to the tail, supporting round-robin proxy selection, worker distribution, or banner rotation.
- **Stack:** `LPUSH` followed by `LPOP` retrieves the most recently pushed element first. Examples include undo/redo navigation and browser back history.

## Creating a list using `LPUSH` and `RPUSH`

### `LPUSH` (left push)

`LPUSH` adds values at the head, creating the list if the key is missing. With multiple arguments, it pushes them one after another, so the last argument appears first. It returns the resulting list length.

Pushing at the head places the newest element first:

```sh
redis> LPUSH mylist "world"
(integer) 1
redis> LPUSH mylist "hello"
(integer) 2
redis> LRANGE mylist 0 -1
1) "hello"
2) "world"
```

Multiple arguments appear in reverse argument order:

```sh
redis> LPUSH languages "python" "java" "ruby"
(integer) 3
redis> LRANGE languages 0 -1
1) "ruby"
2) "java"
3) "python"
```

### `RPUSH` (right push)

`RPUSH` adds values at the tail, creating the list if needed. Multiple values remain in argument order, and the command returns the resulting length.

Pushing at the tail preserves earlier elements first:

```sh
redis> RPUSH user_log "login"
(integer) 1
redis> RPUSH user_log "view_page"
(integer) 2
redis> LRANGE user_log 0 -1
1) "login"
2) "view_page"
```

Multiple arguments retain their argument order:

```sh
redis> RPUSH queue "job1" "job2" "job3"
(integer) 3
redis> LRANGE queue 0 -1
1) "job1"
2) "job2"
3) "job3"
```

## Slicing Lists with `LRANGE`

`LRANGE` reads elements from head to tail within a specified range. Indexes are zero-based (`0` is the head); negative indexes count from the tail (`-1` is the last element). A range extending past the tail returns the available elements, while a start beyond the tail returns an empty list.

The same list yields full, middle, and tail ranges:

```sh
redis> RPUSH frameworks "Flask" "Django" "FastAPI" "Rails"
(integer) 4
redis> LRANGE frameworks 0 -1
1) "Flask"
2) "Django"
3) "FastAPI"
4) "Rails"
redis> LRANGE frameworks 1 2
1) "Django"
2) "FastAPI"
redis> LRANGE frameworks -2 -1
1) "FastAPI"
2) "Rails"
```

## Accessing Elements with `LINDEX`

`LINDEX` reads one element without removing it. It uses zero-based indexes from the head and negative indexes from the tail (`-1` is the last element). An out-of-range index returns `(nil)`.

Indexes `0` and `-1` select the head and tail:

```sh
redis> RPUSH playlist "Song A" "Song B" "Song C"
(integer) 3
redis> LINDEX playlist 0
"Song A"
redis> LINDEX playlist -1
"Song C"
```

An out-of-range index returns `(nil)`:

```sh
redis> LPUSH games "Chess" "Checkers" "Go"
(integer) 3
redis> LINDEX games 1
"Checkers"
redis> LINDEX games 99
(nil)
```

## Injecting Elements with `LINSERT`

`LINSERT` inserts a value `BEFORE` or `AFTER` a pivot. Redis searches from head to tail and acts on the **first** matching pivot. Unlike a push, it does not create a missing list. It returns the new length on success, `-1` if the pivot is absent, or `0` if the key is absent.

A pivot positions each inserted value:

```sh
redis> RPUSH todo_list "clean" "sleep"
(integer) 2
redis> LINSERT todo_list BEFORE "sleep" "eat"
(integer) 3
redis> LINSERT todo_list AFTER "eat" "read"
(integer) 4
redis> LRANGE todo_list 0 -1
1) "clean"
2) "eat"
3) "read"
4) "sleep"
```

An absent pivot returns `-1`:

```sh
redis> LINSERT todo_list BEFORE "gym" "run"
(integer) -1
```

## Remove elements via `LPOP` and `RPOP`

`LPOP` removes and returns the head; `RPOP` does the same at the tail. A missing or empty list returns `(nil)`. Since Redis 6.2, either command accepts an optional `count` to remove and return multiple elements as a list instead of one value.

### `LPOP` (left pop)

Popping the head leaves the remaining elements in order:

```sh
redis> RPUSH queue "customer1" "customer2" "customer3"
(integer) 3
redis> LPOP queue
"customer1"
redis> LRANGE queue 0 -1
1) "customer2"
2) "customer3"
```

A count removes several head elements at once:

```sh
redis> RPUSH letters "A" "B" "C" "D"
(integer) 4
redis> LPOP letters 2
1) "A"
2) "B"
redis> LRANGE letters 0 -1
1) "C"
2) "D"
```

### `RPOP` (right pop)

Popping the tail removes the last element:

```sh
redis> RPUSH stack "plate1" "plate2" "plate3"
(integer) 3
redis> RPOP stack
"plate3"
redis> LRANGE stack 0 -1
1) "plate1"
2) "plate2"
```

After the list is deleted, a pop returns `(nil)`:

```sh
redis> DEL empty_list
(integer) 1
redis> RPOP empty_list
(nil)
```

## Trimming Lists with `LTRIM`

`LTRIM` keeps only an indexed range and **removes** everything else; unlike `LRANGE`, it changes the list. Indexes are zero-based from the head, with negative values counting from the tail. A start beyond the end empties the list, while a stop beyond the end acts like the last element. Pushing new entries and then trimming maintains a fixed-length recent-history window.

Trimming to indexes `0` through `2` retains the first three elements:

```sh
redis> RPUSH numbers 1 2 3 4 5
(integer) 5
redis> LTRIM numbers 0 2
OK
redis> LRANGE numbers 0 -1
1) "1"
2) "2"
3) "3"
```

Negative indexes retain the last two entries in a rolling window:

```sh
redis> RPUSH recent_views "home" "about" "contact" "products"
(integer) 4
redis> LTRIM recent_views -2 -1
OK
redis> LRANGE recent_views 0 -1
1) "contact"
2) "products"
```

A start index after the stop index empties the list:

```sh
redis> RPUSH data "A" "B" "C"
(integer) 3
redis> LTRIM data 1 0
OK
redis> LLEN data
(integer) 0
```

## Updating Elements with `LSET`

`LSET` replaces an element without inserting or shifting other elements. It requires an existing list and an in-range index; otherwise it returns an error. Indexes are zero-based from the head or negative from the tail.

The head and tail elements are replaced without changing list length:

```sh
redis> RPUSH status "pending" "loading" "complete"
(integer) 3
redis> LSET status 0 "starting"
OK
redis> LSET status -1 "done"
OK
redis> LRANGE status 0 -1
1) "starting"
2) "loading"
3) "done"
```

An out-of-range replacement returns an error:

```sh
redis> RPUSH small_list "A" "B"
(integer) 2
redis> LSET small_list 5 "C"
(error) ERR index out of range
```

## Counting Elements with `LLEN`

`LLEN` returns the number of elements in $O(1)$ time because Redis keeps the length in list metadata rather than traversing the list. A missing key returns `0`; a key holding another type, such as a string or set, produces an error.

The list length reflects its pushed elements:

```sh
redis> RPUSH messages "Hello" "World" "Again"
(integer) 3
redis> LLEN messages
(integer) 3
```

A missing key has length zero:

```sh
redis> DEL unknown_key
(integer) 1
redis> LLEN unknown_key
(integer) 0
```

## Searching Indices with `LPOS`

`LPOS` (available since Redis 6.0.6) searches for an element and returns its index, or `(nil)` if it is absent. By default it scans from head to tail. Its options change the search:

- **`RANK`:** Selects an occurrence; positive ranks scan from the head (`1` is the first match), while negative ranks scan from the tail (`-1` is the last).
- **`COUNT`:** Returns an array of indexes for the first *N* matches; `0` returns all matches.
- **`MAXLEN`:** Limits how many elements are compared, bounding work on a large list.

The default search returns the first matching index:

```sh
redis> RPUSH playlist "songA" "songB" "songC" "songB"
(integer) 4
redis> LPOS playlist "songB"
(integer) 1
```

Negative rank selects the last occurrence:

```sh
redis> LPOS playlist "songB" RANK -1
(integer) 3
```

`COUNT` returns multiple matching indexes:

```sh
redis> RPUSH nums 1 2 1 2 1 2
(integer) 6
redis> LPOS nums 1 COUNT 2
1) (integer) 0
2) (integer) 2
```

## Removing Specific Values with `LREM`

`LREM` removes occurrences equal to `value` and returns the number removed (`0` if none match). The sign and magnitude of `count` choose which matches:

- **Positive count:** Remove up to that many matches from head to tail.
- **Negative count:** Remove up to that many matches from tail to head.
- **Zero count:** Remove all matches.

A positive count removes matches from the head:

```sh
redis> RPUSH meeting "bob" "alice" "bob" "dave" "bob"
(integer) 5
redis> LREM meeting 2 "bob"
(integer) 2
redis> LRANGE meeting 0 -1
1) "alice"
2) "dave"
3) "bob"
```

A negative count removes matches from the tail:

```sh
redis> RPUSH logs "error" "info" "error" "warning"
(integer) 4
redis> LREM logs -1 "error"
(integer) 1
redis> LRANGE logs 0 -1
1) "error"
2) "info"
3) "warning"
```

A zero count removes every matching value:

```sh
redis> RPUSH nums 1 2 1 3 1
(integer) 5
redis> LREM nums 0 1
(integer) 3
redis> LRANGE nums 0 -1
1) "2"
2) "3"
```

## Moving Elements with `LMOVE`

`LMOVE source destination LEFT|RIGHT LEFT|RIGHT` atomically pops one end of the source and pushes it to the chosen end of the destination. No client sees an intermediate state. It returns the moved element, and the source and destination may be the same key to rotate a list.

> [!note] Earlier list transfer command
> Redis 6.2.0 introduced `LMOVE` as a replacement for `RPOPLPUSH`. Its right-to-left transfer corresponds to `LMOVE source destination RIGHT LEFT`.

The source tail moves to the destination head atomically:

```sh
redis> RPUSH processing "job1"
(integer) 1
redis> RPUSH pending "job2" "job3"
(integer) 2
redis> LMOVE pending processing RIGHT LEFT
"job3"
redis> LRANGE processing 0 -1
1) "job3"
2) "job1"
redis> LRANGE pending 0 -1
1) "job2"
```

Moving an element within the same list rotates it:

```sh
redis> RPUSH carousel "A" "B" "C"
(integer) 3
redis> LMOVE carousel carousel RIGHT LEFT
"C"
redis> LRANGE carousel 0 -1
1) "C"
2) "A"
3) "B"
```
