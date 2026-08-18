# Concurrency Fundamentals

**Concurrency** describes a system in which multiple tasks can make progress during overlapping periods of time. **Parallelism** is the narrower case in which multiple tasks are actually executing at the same instant using separate hardware execution resources.

A program can therefore be concurrent without being parallel. On a single CPU core, the operating-system scheduler can interleave runnable threads, giving several tasks opportunities to make progress even though only one executes at a particular instant. On a multi-core CPU, different runnable threads may execute simultaneously and provide true parallelism.

The operating system fundamentally schedules [threads](../../Operating%20Systems/05%20Process%20Management.md#Processes%20vs.%20Threads), while processes primarily provide resource and isolation boundaries such as virtual address spaces and file descriptor tables. Threads within the same process naturally share memory, while different processes normally require explicitly shared memory or another communication mechanism to operate on the same state.

Concurrency becomes difficult when independently executing tasks interact through **shared mutable state**.

## Race Conditions

A **race condition** occurs when the correctness of an operation depends on the relative timing or interleaving of concurrent execution.

Suppose two threads share an integer:

```c
int a = 0;
```

and both execute:

```c
a++;
```

Although `a++` appears to be one operation in source code, it is conceptually a **read-modify-write** sequence:

1. Read the current value of `a`.
2. Compute `a + 1`.
3. Store the new value.

The exact machine instructions depend on the compiler and CPU, but unless the operation is implemented using an appropriate atomic instruction or protected by synchronization, another thread may execute between these steps.

One possible interleaving is:

| Time | Thread A | Thread B | Shared `a` |
| --- | --- | --- | ---: |
| `t0` | Reads `a = 0` | — | `0` |
| `t1` | Computes `0 + 1 = 1` | — | `0` |
| `t2` | — | Reads `a = 0` | `0` |
| `t3` | — | Computes `0 + 1 = 1` | `0` |
| `t4` | Writes `1` | — | `1` |
| `t5` | — | Writes `1` | `1` |

Both threads completed an increment, so the expected final value was `2`. Instead, both calculations were based on the same old value and both wrote `1`.

This is a **lost update**: two concurrent operations observed the same old state and one write overwrote the effect of the other.

Lost updates are not specific to threads or memory. The same fundamental problem can occur at higher abstraction levels, such as two database transactions reading the same record and independently writing changes based on that stale value. The mechanisms used to prevent or detect those conflicts are covered separately as concurrency control.

### Critical Sections

A **critical section** is a region of code that accesses shared state in a way that cannot safely overlap with conflicting execution.

For the previous example, the complete read-modify-write sequence is the critical operation. Protecting only the final write would not be sufficient because the correctness of the result also depends on the value that was originally read.

Synchronization mechanisms provide different ways to make such operations safe.

## Synchronization Mechanisms

Synchronization mechanisms coordinate concurrent execution. Some prevent multiple execution contexts from entering a critical section simultaneously, some provide signaling between execution contexts, and some make individual state transitions atomic.

### Mutexes

A **mutex** provides mutual exclusion: only one thread at a time may own the mutex and execute the critical section it protects.

Suppose both threads want to increment the same shared variable:

```c
lock(mutex);
a++;
unlock(mutex);
```

Initially, `a = 0` and the mutex is unlocked.

| Time | Thread A             | Thread B                       | Mutex      | Shared `a` |
| ---- | -------------------- | ------------------------------ | ---------- | ---------: |
| `t0` | Acquires mutex       | —                              | Owned by A |        `0` |
| `t1` | Reads `a = 0`        | —                              | Owned by A |        `0` |
| `t2` | Computes `0 + 1 = 1` | Tries to acquire mutex → waits | Owned by A |        `0` |
| `t3` | Writes `1`           | Waiting                        | Owned by A |        `1` |
| `t4` | Releases mutex       | Waiting                        | Unlocked   |        `1` |
| `t5` | —                    | Acquires mutex                 | Owned by B |        `1` |
| `t6` | —                    | Reads `a = 1`                  | Owned by B |        `1` |
| `t7` | —                    | Computes `1 + 1 = 2`           | Owned by B |        `1` |
| `t8` | —                    | Writes `2`                     | Owned by B |        `2` |
| `t9` | —                    | Releases mutex                 | Unlocked   |        `2` |

Unlike the race-condition example, Thread B cannot enter the protected read-modify-write sequence while Thread A owns the mutex. The two increments are therefore serialized and the final value is correctly `2`.

If the mutex is implemented as a blocking lock, Thread B normally stops being runnable while waiting rather than continuously consuming CPU.

### Spinlocks

A **spinlock** also provides mutual exclusion, but it handles waiting differently.

Instead of blocking when the lock is unavailable, the waiting thread remains runnable and repeatedly checks whether the lock has become available:

```c
while (locked) {
    // spin
}
```

Spinning consumes CPU cycles, but blocking and later waking a thread introduces scheduler and [context-switching overhead](../../Operating%20Systems/05%20Process%20Management.md#Context%20Switching%20Overhead). A spinlock can therefore be efficient when the critical section is extremely short and the lock holder is expected to release it before putting the waiting thread to sleep and waking it again would be worthwhile.

The trade-off depends primarily on **expected waiting time**. As that time grows, spinning wastes increasingly more CPU.

Spinlocks are particularly problematic if the lock holder cannot run. A waiting thread may consume an entire CPU core repeatedly checking a lock whose owner is currently descheduled. On a single-core system this is especially undesirable because the spinning thread itself may prevent the lock holder from receiving CPU time.

> [!example] PostgreSQL, Spinlocks, and Kernel Preemption
> In 2026, an Amazon/AWS engineer found that PostgreSQL throughput on a development version of Linux 7.0 had fallen to roughly half of previous kernel versions under a highly concurrent `pgbench` workload. Profiling showed that a large fraction of CPU time was now being consumed inside PostgreSQL's userspace spinlocks. The regression was traced to a Linux change that altered the kernel's available preemption behavior.
>
> PostgreSQL uses multiple backend processes that coordinate through shared memory. For extremely short critical sections, it sometimes uses **spinlocks**: if one backend owns the lock, another backend does not immediately sleep. It remains runnable and repeatedly checks the lock, based on the assumption that the owner will release it very quickly.
>
> The problematic interaction appeared when a backend acquired a spinlock and then triggered a [page fault](../../Operating%20Systems/03%20Memory%20Management.md#Limitations%20of%20Virtual%20Memory). Although execution had entered the kernel to service the fault, the PostgreSQL backend still logically owned the userspace spinlock. With the changed preemption behavior, that backend could be preempted before the fault handling completed and before it returned to PostgreSQL to release the lock.
>
> This is where a **spinlock is substantially worse than a blocking mutex**. Other PostgreSQL backends waiting for the same spinlock remain runnable. The scheduler can therefore spend CPU time running processes whose only useful action is repeatedly checking a lock that cannot possibly become available until the preempted lock owner runs again.
>
> In the pathological case, scheduling can therefore work against progress: the lock holder is delayed, while CPU time is given to one or more waiters spinning on **the exact lock that only the delayed process can release**. Those waiters consume CPU without advancing the critical section and can increase the scheduling pressure competing with the process they depend on.
>
> With a blocking mutex, waiters would normally become non-runnable after failing to acquire the lock. They would still suffer the lock holder's latency, but they would not continuously consume CPU while waiting. The PostgreSQL regression was therefore not merely an example of the general rule that “a delayed lock holder delays its waiters”; it exposed the specific danger of a spinlock when the assumption that **the owner will continue running and release the lock almost immediately** stops being true.
>
> PostgreSQL's process-heavy architecture and memory behavior further amplified the workload, with the investigation pointing to page faults and TLB-related effects as important contributors.
>
> The key lesson is that a spinlock is efficient only when waiting is expected to be extremely short **and the lock holder is expected to keep executing**. If the operating system can suspend the owner while leaving the waiters runnable, spinning can turn scheduler time into wasted CPU cycles instead of helping the protected operation finish.
>
### Semaphores

A **semaphore** maintains a number of available permits. Unlike a mutex or spinlock, it can allow more than one actor to proceed concurrently.

Suppose a semaphore starts with `2` permits, meaning at most two workers may use a resource simultaneously.

Initially, `permits = 2`.

| Time | Worker A        | Worker B        | Worker C                 | Available permits |
| ---- | --------------- | --------------- | ------------------------ | ----------------: |
| `t0` | Acquires permit | —               | —                        |               `1` |
| `t1` | Using resource  | Acquires permit | —                        |               `0` |
| `t2` | Using resource  | Using resource  | Tries to acquire → waits |               `0` |
| `t3` | Releases permit | Using resource  | Waiting                  |               `1` |
| `t4` | —               | Using resource  | Acquires permit          |               `0` |
| `t5` | —               | Releases permit | Using resource           |               `1` |
| `t6` | —               | —               | Releases permit          |               `2` |

The semaphore does not require Worker B to wait for Worker A because there were initially two permits. Worker C waits only after all available permits have been consumed.

This is the main distinction from mutexes and spinlocks:

* A **mutex/spinlock** usually represents exclusive access: one owner at a time.
* A **counting semaphore** represents capacity: up to `N` concurrent acquisitions.

A semaphore can also be used for signaling. If initialized to `0`, a consumer that calls `wait` immediately blocks until another actor calls `signal`, making a permit available.
Yes. Your process-management note gives a stronger foundation because it already establishes that the scheduler operates on **threads**, and that a thread waiting for an event can become **blocked/non-runnable**, allowing another runnable thread to use the CPU.

### Condition Variables

A **condition variable** allows a thread to stop executing until some condition over shared state may have become true. It is normally paired with a mutex because the condition itself depends on shared state that must be inspected and modified safely.

Consider a bounded queue shared by producers and consumers. A mutex can prevent concurrent modifications from corrupting the queue, but mutual exclusion alone does not solve what happens when a consumer acquires the mutex and discovers that the queue is empty.

The consumer cannot simply keep checking:

```c
lock(mutex);

while (queue_is_empty()) {
    // keep checking
}

item = dequeue();

unlock(mutex);
```

If it keeps the mutex while waiting, a producer cannot acquire that mutex to insert the item the consumer is waiting for. If it repeatedly releases and reacquires the mutex, it effectively performs a form of polling and wastes CPU or introduces arbitrary delays.

A condition variable solves this by connecting **synchronization state** with the thread's [scheduling state](../../Operating%20Systems/05%20Process%20Management.md#Processes%20vs.%20Threads).

Conceptually:

```text
wait(condition, mutex)
```

performs two closely coupled operations:

1. releases the mutex;
2. suspends the calling thread on the condition variable.

The release and transition into waiting must behave atomically with respect to the condition-variable protocol. Otherwise another thread could change the state and signal between those operations, causing the waiter to miss the notification.

Once waiting, the thread is no longer a runnable execution context competing for CPU time. The operating system can schedule another runnable thread instead, just as with other forms of blocking described in [Process Management](../../Operating%20Systems/05%20Process%20Management.md).

Suppose the queue is initially empty and the mutex is unlocked:

|Time|Consumer|Producer|Consumer state|Mutex|Queue|
|---|---|---|---|---|---|
|`t0`|Acquires mutex|—|Running|Consumer|Empty|
|`t1`|Checks queue → empty|—|Running|Consumer|Empty|
|`t2`|`wait(not_empty)` releases mutex and waits|—|**Blocked**|Unlocked|Empty|
|`t3`|—|Acquires mutex|Blocked|Producer|Empty|
|`t4`|—|Enqueues item|Blocked|Producer|1 item|
|`t5`|—|Signals `not_empty`|**Runnable**|Producer|1 item|
|`t6`|—|Releases mutex|Runnable|Unlocked|1 item|
|`t7`|Reacquires mutex|—|Running|Consumer|1 item|
|`t8`|Dequeues item|—|Running|Consumer|Empty|
|`t9`|Releases mutex|—|Running|Unlocked|Empty|

The scheduling transition is important. When the producer signals `not_empty`, the consumer does **not necessarily begin executing immediately**. The signal makes the waiting thread eligible to continue, but the operating-system scheduler still decides when it receives CPU time.

This connects directly to [context switching](../../Operating%20Systems/05%20Process%20Management.md#Context%20Switching). At `t2`, the consumer can no longer make progress and gives up the CPU. After it is awakened, the scheduler eventually dispatches it again and restores its execution context.

There is one more synchronization step before `wait` can return: the consumer must **reacquire the mutex**. If another thread owns the mutex when the consumer is scheduled, it may have to wait again until the mutex becomes available.

The normal usage is therefore:

```c
lock(mutex);

while (queue_is_empty()) {
    wait(not_empty, mutex);
}

item = dequeue();

unlock(mutex);
```

The condition is checked with `while`, not `if`, because being awakened does not guarantee that the predicate is still true when the thread eventually executes.

For example, another consumer may acquire the mutex first and remove the newly inserted item:

|Time|Consumer A|Consumer B|Queue|
|---|---|---|---|
|`t0`|Waiting on `not_empty`|Waiting on `not_empty`|Empty|
|`t1`|Becomes runnable|Becomes runnable|1 item|
|`t2`|—|Acquires mutex and removes item|Empty|
|`t3`|Acquires mutex later|—|Empty|
|`t4`|Checks condition again → false|—|Empty|
|`t5`|Waits again|—|Empty|

Condition-variable implementations may also permit **spurious wakeups**, making the same rule necessary even when no competing consumer consumed the state.

Therefore, a signal should be interpreted as:

> **Something changed that may make your condition true; reacquire the lock and check again.**

The mutex and condition variable have different responsibilities:

* the **mutex** protects the shared state while it is inspected or modified;
* the **condition variable** allows a thread that cannot currently make progress to become non-runnable until another actor changes relevant state.

This makes condition variables fundamentally different from spinlocks. A thread waiting on a spinlock remains runnable and consumes CPU while checking the lock; a thread waiting on a condition variable gives up the CPU until it has a reason to try again.

> [!example] The Classic Bounded Producer/Consumer Problem  
> The **bounded producer/consumer problem** is a classic synchronization problem involving a shared queue with finite capacity.
>
> Producers add items to the queue, while consumers remove them. Because both operate on the same shared state, access to the queue must be synchronized. The bounded capacity introduces two additional conditions:
>
> * a producer cannot insert when the queue is full;
>
> * a consumer cannot remove when the queue is empty.
>
>
> A typical solution therefore combines **mutual exclusion** with two condition variables:
>
> ```text
> not_empty
> not_full
> ```
>
> Producers wait on `not_full` when the queue has reached its capacity, while consumers wait on `not_empty` when there is nothing to consume.
>
> The problem is useful because it demonstrates that mutual exclusion alone is insufficient. A mutex can prevent concurrent corruption of the queue, but condition variables are needed to suspend threads whose operation is currently invalid and wake them when the shared state changes.
>
### Monitors

A **monitor** is a higher-level synchronization abstraction that combines:

* shared mutable state;
* operations that manipulate that state;
* mutual exclusion around those operations;
* condition variables for operations that cannot currently make progress.

A monitor therefore packages mechanisms already introduced separately into one synchronization boundary.

Without a monitor, callers might manipulate shared state manually:

```c
lock(mutex);

while (queue_is_empty()) {
    wait(not_empty, mutex);
}

item = dequeue();

unlock(mutex);
```

A monitor instead encapsulates the state and synchronization together:

```text
monitor BoundedQueue:
    mutex
    queue

    condition not_empty
    condition not_full

    put(item):
        lock(mutex)

        while queue is full:
            wait(not_full, mutex)

        enqueue(item)
        signal(not_empty)

        unlock(mutex)

    take():
        lock(mutex)

        while queue is empty:
            wait(not_empty, mutex)

        item = dequeue()
        signal(not_full)

        unlock(mutex)

        return item
```

Entering a monitor operation conceptually acquires exclusive access to the monitor's protected state. If another thread is already executing a protected operation, the entering thread must wait.

This provides **mutual exclusion**, but a monitor also needs conditional waiting because exclusive access does not imply that an operation can make progress.

Suppose a consumer enters `take()` while the queue is empty:

|Time|Consumer|Producer|Consumer state|Monitor|Queue|
|---|---|---|---|---|---|
|`t0`|Enters `take()`|—|Running|Consumer|Empty|
|`t1`|Finds queue empty|—|Running|Consumer|Empty|
|`t2`|Waits on `not_empty` and gives up monitor|—|**Blocked**|Free|Empty|
|`t3`|—|Enters `put()`|Blocked|Producer|Empty|
|`t4`|—|Enqueues item|Blocked|Producer|1 item|
|`t5`|—|Signals `not_empty`|**Runnable**|Producer|1 item|
|`t6`|—|Leaves `put()`|Runnable|Free|1 item|
|`t7`|Re-enters monitor|—|Running|Consumer|1 item|
|`t8`|Dequeues item|—|Running|Consumer|Empty|
|`t9`|Leaves `take()`|—|Running|Free|Empty|

The important step is `t2`. The consumer cannot remain the monitor's exclusive owner while waiting, because the state it needs can only become true if another thread is allowed to enter the monitor and modify that state.

`wait(not_empty)` therefore performs the same scheduling transition described for condition variables: the consumer gives up exclusive access and becomes blocked. The [scheduler](../../Operating%20Systems/05%20Process%20Management.md#Processes%20vs.%20Threads) can then execute some other runnable thread, such as the producer.

When the producer signals `not_empty`, the consumer becomes eligible to execute again. The signal does not transfer the CPU directly to the consumer, nor does it generally mean that the consumer immediately owns the monitor. The scheduler must eventually run it, and the consumer must regain exclusive access before continuing.

A monitor therefore coordinates **two different kinds of waiting**:

* **Waiting to enter the monitor** occurs when another thread currently owns the monitor. The thread has not entered the protected region yet and waits for the monitor's mutual-exclusion lock to become available.
* **Waiting on a condition variable** occurs after a thread has entered the monitor and inspected the protected state, but discovers that its operation cannot currently proceed. It calls `wait()` on a particular condition variable, such as `not_empty` or `not_full`, which releases the monitor and blocks the thread until relevant state changes.

That distinction is important. A mutex answers:

> **May I access this state now?**

A condition variable answers:

> **Is the state currently suitable for the operation I want to perform?**

A monitor combines both questions into the abstraction that owns the state.

Conceptually:

```text
Monitor
    = protected shared state
    + mutual exclusion
    + condition-based waiting
    + operations that enforce those rules
```

The main advantage is **encapsulation of synchronization policy**. Callers do not need to know which mutex protects the object or which condition variables must be signaled after a state transition. They call operations such as `put()` and `take()`, while the monitor itself maintains the synchronization invariants.

From the operating system's perspective, however, there is nothing special about the monitor abstraction. The kernel still schedules [threads](../../Operating%20Systems/05%20Process%20Management.md#Processes%20vs.%20Threads). Threads that can execute are runnable; threads waiting on synchronization may become blocked; waking them makes them runnable again; and actual execution occurs only when the scheduler dispatches them onto a CPU core.

So monitors are best understood as a **programming-level structure built on top of the thread scheduling and synchronization mechanisms described in Process Management**, rather than as a new kind of scheduler primitive.

### Atomic Operations

An **atomic operation** is performed as one indivisible state transition with respect to other execution contexts observing the same atomic state. Another thread cannot observe the atomic operation halfway through.

CPUs provide instructions that can implement operations such as atomic increment, exchange, and **compare-and-swap (CAS)**. Languages and runtimes expose these capabilities through atomic types and synchronization libraries.

For the previous counter example, an atomic increment can perform the complete read-modify-write operation atomically:

```c
atomic_fetch_add(&a, 1);
```

This prevents the lost update without placing the operation inside a mutex-protected critical section.

Another important primitive is compare-and-swap. Conceptually, CAS performs:

```text
if current_value == expected_value:
    current_value = new_value
    succeed
else:
    fail
```

The comparison and replacement occur atomically. This allows software to detect whether another execution context changed the state between observing it and attempting to modify it.

Atomicity applies only to the operation being made atomic. Several individually atomic operations do not automatically make a larger multi-step algorithm safe. If multiple values or invariants must change together, a higher-level synchronization mechanism may still be required.

CAS also establishes an important connection to optimistic concurrency control: instead of preventing another actor from modifying the state, the operation detects whether the state changed before accepting the update.

## Concurrency Hazards

Synchronization prevents many race conditions, but coordination between execution contexts introduces additional failure modes.

### Deadlock

A **deadlock** occurs when a set of execution contexts wait indefinitely for resources held by one another.

For example:

1. Thread A acquires Lock 1.
2. Thread B acquires Lock 2.
3. Thread A waits for Lock 2.
4. Thread B waits for Lock 1.

Neither thread can continue because each waits for the other to release a resource.

A common prevention technique is **consistent lock ordering**. If every execution context must acquire Lock 1 before Lock 2, the circular dependency cannot arise through those two locks.

Deadlocks are not specific to threads. The same dependency pattern can occur between processes, database transactions, distributed services, or any system in which actors hold resources while waiting for others.

### Starvation

**Starvation** occurs when an execution context is capable of making progress in principle but repeatedly fails to obtain the CPU time or synchronization resource it needs.

Common causes include:

* unfair lock acquisition;
* a continuous stream of other actors acquiring the resource first;
* scheduling policies that repeatedly favor other runnable threads.

Unlike a deadlock, the system as a whole may continue making progress while one particular participant waits indefinitely.

### Priority Inversion

**Priority inversion** occurs when a high-priority thread is indirectly prevented from running by a lower-priority thread.

Consider three threads:

1. A low-priority thread acquires a mutex.
2. A high-priority thread attempts to acquire the same mutex and blocks.
3. Medium-priority threads remain runnable and repeatedly preempt the low-priority thread.

The high-priority thread now depends on the low-priority thread, but the low-priority thread cannot receive enough CPU time to finish its critical section and release the mutex.

A common mitigation is **priority inheritance**. If a high-priority thread becomes blocked waiting for a mutex held by a low-priority thread, the low-priority thread temporarily inherits the higher priority. This allows the lock holder to run ahead of unrelated medium-priority threads, finish its critical section, and release the mutex sooner. After releasing it, the thread returns to its original priority and the high-priority thread can continue.

## Correctness vs. Performance

A concurrent program can be completely correct and still scale poorly.

Synchronization and parallel execution interact with the scheduler and CPU memory hierarchy, so preventing race conditions is only one part of designing concurrent software.

Common performance costs include:

* **Lock contention:** As more threads compete for the same lock, an increasing fraction of execution time is spent waiting instead of performing useful work.
* **Blocking and wakeups:** Moving threads between runnable and blocked states introduces scheduler and [context-switching overhead](../../Operating%20Systems/05%20Process%20Management.md#Context%20Switching%20Overhead).
* **Cache locality:** Moving execution between CPU cores can reduce reuse of data already present in a particular core's [cache hierarchy](../../Operating%20Systems/04%20Inside%20The%20CPU.md#The%20Cache%20Hierarchy).
* **Cache-line bouncing:** When multiple cores repeatedly modify shared cache lines, the [cache-coherence protocol](../../Operating%20Systems/04%20Inside%20The%20CPU.md#Cache%20coherency) must repeatedly transfer ownership of those lines between cores.
* **False sharing:** Independent variables modified by different threads can accidentally occupy the same cache line, causing unnecessary coherence traffic even though the threads do not logically share the variables. This is covered in [False Sharing](../../Operating%20Systems/04%20Inside%20The%20CPU.md#The%20Developer%20Trap:%20False%20Sharing).

Adding concurrency therefore introduces a trade-off. More execution contexts can expose additional parallelism or allow useful work to proceed while other operations wait, but they can also increase synchronization, scheduling, memory, and cache-coherence costs.

The objective is not to maximize the number of concurrent execution contexts. It is to introduce enough concurrency to improve useful progress without allowing coordination overhead to dominate the work itself.

## Concurrency Control Strategies

When multiple actors can access the same mutable state concurrently, the system needs a strategy for preventing or detecting conflicting operations. At a high level, concurrency control usually follows one of two approaches: **pessimistic control**, which prevents conflicting actors from proceeding at the same time, and **optimistic control**, which allows concurrent work but validates that the underlying state did not change before accepting the result.

These strategies are general. A mutex protecting memory is a pessimistic mechanism, while compare-and-swap is an optimistic one. The same ideas also appear at higher abstraction levels such as database rows and distributed application state.

> [!example]- Version Control: Pessimistic vs. Optimistic Concurrency  
> Version-control systems provide a useful analogy for the difference between pessimistic and optimistic concurrency control.
>
> Some early systems, such as **RCS and SCCS**, commonly used **reserved checkouts**. Before modifying a file, a developer acquired a lock that prevented other developers from modifying the same file concurrently. This is pessimistic concurrency control: prevent the conflict before it can occur.
>
> Later systems increasingly adopted an **unreserved checkout** or **copy-modify-merge** model. Multiple developers can independently modify their own copies of the same file. When their changes are combined, the version-control system attempts to merge them and reports a conflict when the changes cannot be reconciled automatically.
>
> This is analogous to optimistic concurrency control: allow independent work to proceed without holding a long-lived lock, then detect and resolve conflicting changes when the results are combined.
>
> Git extended the idea into a distributed model where every developer has a complete local repository and can create branches and commits independently before eventually integrating divergent histories.
>
> The trade-off is the same as in other concurrency-control systems: pessimistic locking reduces conflicting work but can leave others waiting on the lock holder, while optimistic coordination maximizes independent progress but may require conflict resolution later.
>
### Pessimistic Concurrency Control

**Pessimistic concurrency control** assumes that conflicting access is sufficiently likely, or sufficiently expensive, that it should be prevented before the operation proceeds.

An actor first acquires exclusive or restricted access to the state it needs, performs the operation while that access is held, and releases it afterward:

```text
acquire access
read state
compute change
write state
release access
```

While the protected state is locked, conflicting actors must wait rather than proceed concurrently. The system therefore avoids stale writes by preventing incompatible operations from overlapping in the first place.

This works well when conflicts are common, retries would be expensive, or correctness depends on keeping some state stable for the duration of an operation.

The trade-off is reduced concurrency. Once an actor acquires a lock, the progress of other conflicting actors depends on the **lock holder being able to continue executing and eventually release it**.

If the lock holder is delayed by scheduling, slow I/O, a page fault, another lock, or any other blocking operation, every dependent actor remains waiting even if those actors are otherwise ready to run. With blocking locks, those waiters normally sleep instead of consuming CPU, but their latency still inherits the lock holder's delay.

This makes **lock duration** particularly important. A lock should normally cover only the state and time interval required to preserve the invariant. Holding it while performing unrelated work unnecessarily extends contention.

> [!example]- Mutex  
> A [mutex](#Mutexes) is a low-level example of pessimistic concurrency control.
>
> Suppose several threads modify the same shared value:
>
> ```c
> lock(mutex);
> 
> a++;
> 
> unlock(mutex);
> ```
>
> The thread acquires exclusive access before performing the read-modify-write operation. Another thread attempting to acquire the same mutex must wait until the current owner releases it.
>
> The conflict is therefore prevented before it occurs rather than detected afterward.
>
> If the lock holder is descheduled, blocked on I/O, handling a page fault, or otherwise delayed, the waiting threads remain blocked as well. This is related to the dependency described for [spinlocks](#Spinlocks), although a blocking mutex normally puts waiters to sleep instead of making them consume CPU while they wait.
> [!example]- Database Row Lock  
> Databases can apply the same strategy by locking data before performing a read-modify-write operation.
>
> Suppose a transaction wants to inspect an account before changing its balance:
>
> ```sql
> BEGIN;
> 
> SELECT balance
> FROM accounts
> WHERE id = 123
> FOR UPDATE;
> ```
>
> The transaction acquires a lock on the row before using its value to make a decision. A conflicting transaction that also needs an incompatible lock on that row must wait.
>
> The first transaction can then safely apply the change:
>
> ```sql
> UPDATE accounts
> SET balance = 70
> WHERE id = 123;
> 
> COMMIT;
> ```
>
> The important property is that the lock is held across the read and subsequent write, preventing another conflicting transaction from changing the protected state in between.
>
> The cost is that a slow transaction delays every transaction waiting for the same lock. Holding database locks while performing network calls, slow computation, or unrelated work can therefore create substantial contention.
>
#### Lock Granularity

Pessimistic control must also decide **how much state a lock protects**.

A coarse-grained lock protects a large amount of state. This simplifies synchronization but reduces concurrency because operations that do not logically conflict may still block one another.

For example, a global lock protecting every customer record would prevent two threads from updating completely different customers at the same time.

A finer-grained design might use one lock per customer. Operations on Customer A and Customer B can then proceed concurrently because they protect independent state.

Fine-grained locking increases potential concurrency, but it also creates more locks to manage. Operations that need several resources may need to acquire several locks, increasing the risk of [deadlocks](#Deadlock) and making consistent lock ordering more important.

The correct lock granularity should therefore follow the **invariant boundary**. The lock must cover all state that needs to remain consistent together, but ideally no unrelated state.

#### Cost of Contention

As more actors compete for the same lock, the protected resource effectively becomes serialized.

If one critical section takes `5 ms` and only one actor can execute it at a time, adding more concurrent callers does not increase the throughput of that critical section. Instead, the additional callers accumulate in a queue.

This can turn a small protected region into a system-wide bottleneck when:

* the critical section takes too long;
* the lock protects too much state;
* many operations need the same resource;
* the lock holder is frequently delayed;
* several locks create dependency chains between actors.

Pessimistic concurrency control therefore trades **conflict prevention** for **waiting and reduced concurrency**. It works best when avoiding wasted or conflicting work is more valuable than allowing every actor to proceed independently.

### Optimistic Concurrency Control

**Optimistic concurrency control** assumes conflicts are sufficiently uncommon that preventing concurrent work would cost more than occasionally detecting and retrying a conflict.

Instead of reserving the state before performing work, an actor:

1. Reads the current state.
2. Computes a result based on that state.
3. Checks whether the state changed in the meantime.
4. Accepts the update only if the original assumptions are still valid.

The critical requirement is that **the validation (3) and the write (4) must happen atomically**. The initial read and computation deliberately remain outside that atomic boundary: other actors are allowed to modify the state while the operation is being prepared. This is one of the defining differences from pessimistic concurrency control, which attempts to prevent conflicting modifications during the protected read-modify-write operation. Optimistic concurrency control instead detects at the end whether such a modification occurred and rejects the result if its assumptions became stale.

> [!example]- Compare-and-Swap
> **Compare-and-swap (CAS)** is a low-level example of optimistic concurrency control.
>
> Suppose a thread reads a shared value of `100`, computes a new value of `70`, and then attempts:
>
> ```text
> CAS(value, expected=100, new=70)
> ```
>
> The update succeeds only if `value` is still `100`. If another thread changed it before the CAS executes, the comparison fails and the write to `70` is rejected.
>
> The thread can then reread the current value, recompute its operation, and try again.
>
> CAS therefore does not prevent another actor from modifying the state. It allows concurrent work but makes the final write conditional on the assumption used to compute it still being true.
>
> [!example]- Conditional Database Update
> Databases can implement optimistic concurrency control through an **atomic conditional write**: the expected current state is included directly in the update predicate, and the database evaluates that predicate and performs the modification as one indivisible operation.
>
> Suppose several workers can claim the same job:
>
> ```javascript
> {
>     _id: 123,
>     busy: false
> }
> ```
>
> A worker can attempt to claim it with:
>
> ```javascript
> db.jobs.updateOne(
>     { _id: 123, busy: false },
>     { $set: { busy: true } }
> )
> ```
>
> The important property is not merely that the worker checks `busy == false`. The database guarantees that **checking the predicate and changing `busy` to `true` belong to the same atomic write**. MongoDB explicitly guarantees this at the single-document level.
>
> If Worker A succeeds first, the document becomes:
>
> ```javascript
> {
>     _id: 123,
>     busy: true
> }
> ```
>
> When Worker B's update is evaluated, `{ busy: false }` no longer matches, so Worker B modifies no document. There is no point between checking `busy` and changing it where Worker B can slip in and independently claim the same job.
>
> This is fundamentally different from:
>
> ```javascript
> const job = db.jobs.findOne({ _id: 123 })
>
> if (job.busy === false) {
>     db.jobs.updateOne(
>         { _id: 123 },
>         { $set: { busy: true } }
>     )
> }
> ```
>
> Here the read and write are two separate operations. Another worker can modify the document after `findOne()` but before `updateOne()`, so the application has recreated a race condition.
>
> The same conditional-write pattern exists in relational databases:
>
> ```sql
> UPDATE jobs
> SET busy = TRUE
> WHERE id = 123
>   AND busy = FALSE;
> ```
>
> If another transaction changed the state first, the predicate no longer matches and the update affects zero rows.
>
> **Distribution does not remove the atomicity requirement.** In a distributed database, the database system is responsible for coordinating whatever replicas, partitions, or transaction participants are necessary to preserve the atomicity guarantee exposed by the operation. The application still submits one logical conditional mutation rather than implementing the check and write as separate network requests. Systems such as Spanner and CockroachDB, for example, provide atomic distributed transactions even though the underlying data is distributed across machines.
>
> The exact **atomicity boundary depends on the database**. In MongoDB, a single-document update is atomic; if correctness depends on several documents or shards changing together, an explicit distributed transaction may be required.
>
> The general optimistic-concurrency pattern is therefore:
>
> ```text
> application:
>     read state
>     compute change
>
> database, atomically:
>     verify expected state
>     if it still matches:
>         apply change
>     else:
>         reject the change
> ```
>
> The application may perform the expensive computation optimistically, but **the final validation and state transition must share one atomic concurrency-control boundary**.
>
> [!example]- HTTP Conditional Requests
> HTTP can expose the same optimistic-concurrency pattern across a network boundary using entity tags and conditional request headers.
>
> Suppose a client reads:
>
> ```http
> ETag: "v7"
> ```
>
> It later attempts to modify the resource:
>
> ```http
> PUT /documents/123
> If-Match: "v7"
> ```
>
> `If-Match` means that the server should perform the modification only if the current representation still matches `"v7"`.
>
> Conceptually, the server must enforce:
>
> ```text
> atomic:
>     if current_etag == "v7":
>         apply modification
>     else:
>         reject modification
> ```
>
> The precondition check and the state change must belong to the same concurrency-control boundary. If the server checks the ETag and then performs an unrelated, unprotected write afterward, another request could modify the resource between those operations.
>
> `If-None-Match` expresses the opposite precondition. For example:
>
> ```http
> PUT /documents/123
> If-None-Match: *
> ```
>
> requests that the modification succeed only if a current representation does not already exist. This is useful for create-if-absent operations where two clients might otherwise race to create the same resource.
>
> If the precondition no longer holds, the server rejects the state-changing request instead of blindly applying a stale operation.
