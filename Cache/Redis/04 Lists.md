# Lists

* **Definition:** A Redis List is an ordered sequence of strings.
* **Ordering:** The order of elements is determined by the **sequence of insertion**. Elements added first appear earlier (unless pushed to the front), allowing for both First-In-First-Out (FIFO) and Last-In-First-Out (LIFO) behavior.
* **Data Type:** While they can structurally represent numbers or serialized objects, every individual element inside a List is technically a **String**.
* **Capacity:** A single List can hold more than **4 billion elements** ($2^{32} - 1$).
* **Implementation:** Lists are implemented as **Linked Lists** (not arrays).
  - **Benefit:** Adding elements to the Head or Tail is extremely fast ($O(1)$), even if the list has millions of items.
  - **Trade-off:** Accessing an element by index in the middle of a very large list is slower ($O(N)$).
* **Memory Optimization:** Redis automatically uses memory-efficient encodings (like `listpack`) for small lists to minimize memory footprint without sacrificing performance.

## Use cases

* Job Queues (Message Brokering)

  - **Concept:** Lists act as a buffer between a "Producer" (creating tasks) and a "Consumer" (processing tasks). This decouples application components.
    - **Mechanism:**
      - **Producers** add jobs using `LPUSH`.
      - **Consumers** take jobs using `RPOP`.
      - **Blocking:** Consumers can use `BRPOP` to block the connection and wait until a new element arrives, avoiding polling loops.

  - **Application:** Background email sending, video encoding, resizing uploaded images.

* Recent Activity Feeds (Capped Lists)

  - **Concept:** Storing a fixed window of the most recent events (e.g., "Last 10 items viewed").
    - **Mechanism:**
      - Add a new event with `LPUSH`.
      - Immediately limit the size with `LTRIM 0 99` (to keep the latest 100).

  - **Benefit:** Extremely fast retrieval of recent history without querying a relational database.

  - **Application:** Social media timelines, "Who visited your profile", server logs.

* Reliable Queue Processing

  - **Concept:** preventing data loss if a consumer crashes while processing a message.
    - **Mechanism:**
      - Use `LMOVE` (or `RPOPLPUSH` in older versions).
      - The item is popped from the **Queue** list and simultaneously pushed into a **Processing** list.
      - If the worker fails, the job remains in the **Processing** list and can be re-queued or analyzed.

  - **Application:** Financial transactions, critical order processing.

* Circular Lists (Round Robin)

  - **Concept:** Cycling through a list of items repeatedly.
    - **Mechanism:**
      - Use `LMOVE source source LEFT RIGHT`.
      - This takes the head element, processes it, and places it back at the tail of the same list.

  - **Application:** Rotating through proxy servers, distributing requests among workers in a round-robin fashion, cycling through banner ads.

* Stacks (LIFO Navigation)

  - **Concept:** Last-In, First-Out data structure where the most recently added item is the first one retrieved.
    - **Mechanism:**
      - Use `LPUSH` to add items.
      - Use `LPOP` to remove them.

  - **Application:** Implementing "Undo/Redo" functionality, browser "Back" button history.

## Creating a list using `LPUSH` and `RPUSH`

### LPUSH (Left Push)

- **Function:** Inserts one or specified values at the head (left side) of the list stored at the key.
- **Creation:** If the key does not exist, it is created as an empty list before performing the push operations.
- **Multi-value behavior:** If multiple values are specified, they are inserted one after the other. The last value specified appears first in the list (Stack behavior).
- **Return value:** The length of the list after the push operations.

**Example: Basic LPUSH usage**

```
redis> LPUSH mylist "world"
(integer) 1
redis> LPUSH mylist "hello"
(integer) 2
redis> LRANGE mylist 0 -1
1) "hello"
2) "world"
```

**Example: Pushing multiple values (Stack order)**

```
redis> LPUSH languages "python" "java" "ruby"
(integer) 3
redis> LRANGE languages 0 -1
1) "ruby"
2) "java"
3) "python"
```

### RPUSH (Right Push)

- **Function:** Inserts one or specified values at the tail (right side) of the list stored at the key.
- **Creation:** Like LPUSH, if the key does not exist, it is created as an empty list.
- **Multi-value behavior:** Values are appended to the end of the list in the exact order they are specified (Queue behavior).
- **Return value:** The length of the list after the push operations.

**Example: Basic RPUSH usage**

```
redis> RPUSH user_log "login"
(integer) 1
redis> RPUSH user_log "view_page"
(integer) 2
redis> LRANGE user_log 0 -1
1) "login"
2) "view_page"
```

**Example: Pushing multiple values (Sequential order)**

```
redis> RPUSH queue "job1" "job2" "job3"
(integer) 3
redis> LRANGE queue 0 -1
1) "job1"
2) "job2"
3) "job3"
```

## Slicing Lists with `LRANGE`

- **Function:** Returns a specified range of elements from the list stored at the key.
- **Indices:** The command uses zero-based indexing (`0` is the first element, `1` is the second).
- **Negative Indices:** Supports negative integers to reference the end of the list (`-1` is the last element, `-2` is the penultimate).
- **Consistency:** Always retrieves elements from Left (Head) to Right (Tail).
- **Out of Range:** If the range is larger than the list, it returns all available elements. If `start` is larger than the end of the list, it returns an empty list.

**Example: Setup and retrieving ranges**

```
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

- **Function:** Returns the element at the specified `index` within the list stored at the key.
- **Indexing:** Uses zero-based indexing (`0` is the first element, `1` is the second).
- **Negative Indices:** Can be used to designate elements starting at the tail of the list (`-1` is the last element, `-2` is the penultimate).
- **Out of Range:** If the index is out of range (larger than the list size), the command returns `(nil)`.
- **Non-Destructive:** Unlike `LPOP` or `RPOP`, this command does not remove the element from the list.

**Example: Retrieving head and tail elements**

```
redis> RPUSH playlist "Song A" "Song B" "Song C"
(integer) 3
redis> LINDEX playlist 0
"Song A"
redis> LINDEX playlist -1
"Song C"
```

**Example: Accessing an arbitrary index**

```
redis> LPUSH games "Chess" "Checkers" "Go"
(integer) 3
redis> LINDEX games 1
"Checkers"
redis> LINDEX games 99
(nil)
```

## Injecting Elements with `LINSERT`

- **Function:** Inserts a new value into the list positioned either `BEFORE` or `AFTER` a specific reference value (the pivot).
- **Traversal:** The list is searched from the Head (Left) to the Tail. The operation is performed only on the **first** occurrence of the pivot value found.
- **Requirement:** Unlike `PUSH` commands, the key must already exist. If the key does not exist, no operation is performed.
- **Return Values:**
  - Returns the new length of the list upon success.
  - Returns `-1` if the `pivot` value was not found.
  - Returns `0` if the key does not exist.

**Example: Inserting before and after a value**

```
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

**Example: Handling missing pivots**

```
redis> LINSERT todo_list BEFORE "gym" "run"
(integer) -1
```

Here is an overview of `LPOP` and `RPOP` for removing elements.

## Remove elements via `LPOP` and `RPOP`

### LPOP (Left Pop)

- **Function:** Removes and returns the **first** element (the Head) of the list stored at the key.
- **Empty Lists:** If the list is empty or the key does not exist, it returns `(nil)`.
- **Count Argument:** (Redis 6.2+) You can specify an optional `count` argument to remove and return multiple elements from the left side at once.
- **Return Value:** The value of the removed element, or a list of values if `count` was specified.

**Example: Basic LPOP usage**

```
redis> RPUSH queue "customer1" "customer2" "customer3"
(integer) 3
redis> LPOP queue
"customer1"
redis> LRANGE queue 0 -1
1) "customer2"
2) "customer3"
```

**Example: LPOP with count (Removing multiple items)**

```
redis> RPUSH letters "A" "B" "C" "D"
(integer) 4
redis> LPOP letters 2
1) "A"
2) "B"
redis> LRANGE letters 0 -1
1) "C"
2) "D"
```

### RPOP (Right Pop)

- **Function:** Removes and returns the **last** element (the Tail) of the list stored at the key.
- **Empty Lists:** Returns `(nil)` if the list is empty or the key does not exist.
- **Count Argument:** (Redis 6.2+) Can accept a `count` argument to remove and return multiple elements from the right side.
- **Return Value:** The value of the removed element, or a list of values if `count` was specified.

**Example: Basic RPOP usage**

```
redis> RPUSH stack "plate1" "plate2" "plate3"
(integer) 3
redis> RPOP stack
"plate3"
redis> LRANGE stack 0 -1
1) "plate1"
2) "plate2"
```

**Example: Pop from empty list**

```
redis> DEL empty_list
(integer) 1
redis> RPOP empty_list
(nil)
```

## Trimming Lists with `LTRIM`

- **Function:** Trims an existing list so that it will contain *only* the specified range of elements.
- **Destructive:** Unlike `LRANGE`, which just reads data, `LTRIM` permanently **removes** all elements outside the specified `start` and `stop` indices.
- **Indexing:** Supports zero-based indexing (`0` is the head) and negative indexing (`-1` is the tail).
- **Use Case:** ideal for maintaining fixed-length lists (e.g., "Keep only the latest 100 log entries") by pushing new elements and immediately trimming the old ones.
- **Out of Range:**
  - If `start` is larger than the end of the list, the list is emptied (left with 0 elements).
  - If `stop` is larger than the actual end of the list, Redis treats it as the last element of the list.

**Example: Keeping the first 3 elements**

```
redis> RPUSH numbers 1 2 3 4 5
(integer) 5
redis> LTRIM numbers 0 2
OK
redis> LRANGE numbers 0 -1
1) "1"
2) "2"
3) "3"
```

**Example: Keeping the last 2 elements (Rolling window)**

```
redis> RPUSH recent_views "home" "about" "contact" "products"
(integer) 4
redis> LTRIM recent_views -2 -1
OK
redis> LRANGE recent_views 0 -1
1) "contact"
2) "products"
```

**Example: Emptying a list (Start index > Stop index)**

```
redis> RPUSH data "A" "B" "C"
(integer) 3
redis> LTRIM data 1 0
OK
redis> LLEN data
(integer) 0
```

## Updating Elements with `LSET`

- **Function:** Sets the list element at the specified `index` to a new value.
- **Replacement:** This operation overwrites the existing value at that index; it does not add a new element or shift others.
- **Requirements:** The key must already exist and hold a list. Unlike `LPUSH`/`RPUSH`, `LSET` cannot create a list.
- **Indexing:** Supports zero-based indexing (`0` is the head) and negative indexing (`-1` is the tail).
- **Errors:** Returns an error if the index is out of range (i.e., greater than the list length) or if the key does not exist.

**Example: Overwriting specific indices**

```
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

**Example: Handling out of range errors**

```
redis> RPUSH small_list "A" "B"
(integer) 2
redis> LSET small_list 5 "C"
(error) ERR index out of range
```

## Counting Elements with `LLEN`

- **Function:** Returns the length (number of elements) of the list stored at the specified key.
- **Performance:** This is an **O(1)** operation. Redis stores the current length in the list's metadata, so it does not need to traverse the list to count elements.
- **Missing Keys:** If the key does not exist, it is interpreted as an empty list, and the command returns `0`.
- **Wrong Type:** If the value stored at the key is not a list (e.g., a String or Set), an error is returned.

**Example: Getting the size of a populated list**

```
redis> RPUSH messages "Hello" "World" "Again"
(integer) 3
redis> LLEN messages
(integer) 3
```

**Example: Checking a non-existent key**

```
redis> DEL unknown_key
(integer) 1
redis> LLEN unknown_key
(integer) 0
```

## Searching Indices with `LPOS`

- **Function:** Returns the index of matching elements within a list.
- **Availability:** Available since Redis 6.0.6.
- **Direction:** By default, scans the list from Head (Left) to Tail.
- **Options:**
  - `RANK`: Specifies which occurrence to return. Positive ranks scan left-to-right (`1` is the first match). Negative ranks scan right-to-left (`-1` is the last match).
  - `COUNT`: Returns an array of indices for the first *N* matches found. If set to `0`, it returns *all* matches.
  - `MAXLEN`: Limits the number of list elements to compare, useful for performance on very large lists.
- **Return Value:** Returns the integer index (or array of indices) if found, or `(nil)` if the element is not in the list.

**Example: Finding the first occurrence**

```
redis> RPUSH playlist "songA" "songB" "songC" "songB"
(integer) 4
redis> LPOS playlist "songB"
(integer) 1
```

**Example: Finding the last occurrence (Reverse scan)**

```
redis> LPOS playlist "songB" RANK -1
(integer) 3
```

**Example: Finding multiple matches**

```
redis> RPUSH nums 1 2 1 2 1 2
(integer) 6
redis> LPOS nums 1 COUNT 2
1) (integer) 0
2) (integer) 2
```

## Removing Specific Values with `LREM`

- **Function:** Removes the first `count` occurrences of elements equal to `value` from the list stored at the key.
- **The `count` Argument:** The sign and magnitude of the `count` parameter determine how the removal is performed:
  - **count > 0:** Removes elements moving from **Head to Tail** (Left to Right).
  - **count < 0:** Removes elements moving from **Tail to Head** (Right to Left).
  - **count = 0:** Removes **all** elements equal to `value`.
- **Return Value:** Returns the number of elements that were actually removed.
- **Non-existent Elements:** If the value is not found in the list, it returns `0`.

**Example: Removing the first N occurrences (Head to Tail)**

```
redis> RPUSH meeting "bob" "alice" "bob" "dave" "bob"
(integer) 5
redis> LREM meeting 2 "bob"
(integer) 2
redis> LRANGE meeting 0 -1
1) "alice"
2) "dave"
3) "bob"
```

**Example: Removing the last N occurrences (Tail to Head)**

```
redis> RPUSH logs "error" "info" "error" "warning"
(integer) 4
redis> LREM logs -1 "error"
(integer) 1
redis> LRANGE logs 0 -1
1) "error"
2) "info"
3) "warning"
```

**Example: Removing all occurrences**

```
redis> RPUSH nums 1 2 1 3 1
(integer) 5
redis> LREM nums 0 1
(integer) 3
redis> LRANGE nums 0 -1
1) "2"
2) "3"
```

## Moving Elements with `LMOVE`

- **Function:** Atomically removes an element from one list (source) and pushes it into another (destination).
- **Atomicity:** The operation is atomic; no other client can see the state between the pop and the push.
- **Self-reference:** The `source` and `destination` keys can be the same, effectively rotating the list.
- **Arguments:**
  - `source` key
  - `destination` key
  - `LEFT` or `RIGHT` (where to pop from source)
  - `LEFT` or `RIGHT` (where to push to destination)
- **Availability:** Available since Redis 6.2.0 (replaces the older `RPOPLPUSH`).
- **Return Value:** The element that was moved.

**Example: Moving from Tail of one list to Head of another**

```
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

**Example: Rotating a list (Circular Buffer)**

```
redis> RPUSH carousel "A" "B" "C"
(integer) 3
redis> LMOVE carousel carousel RIGHT LEFT
"C"
redis> LRANGE carousel 0 -1
1) "C"
2) "A"
3) "B"
```
