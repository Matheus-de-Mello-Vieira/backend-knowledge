# POSIX Synchronization

POSIX separates synchronization of memory from locking of file regions. The `pthread_*` interfaces coordinate access to shared memory, while `fcntl()` record locks coordinate byte ranges of a file. Neither family is a generic `lock()` system call.

## In-Memory Synchronization Objects

The POSIX Threads API maps the [synchronization mechanisms](../Backend%20Engineering/Concurrency/01%20Concurrency%20Fundamentals.md#Synchronization%20Mechanisms) used in abstract algorithms to concrete objects and operations.

| Concept | POSIX interface |
| --- | --- |
| Mutex | `pthread_mutex_lock()` / `pthread_mutex_unlock()` |
| Nonblocking mutex attempt | `pthread_mutex_trylock()` |
| Read lock | `pthread_rwlock_rdlock()` |
| Write lock | `pthread_rwlock_wrlock()` |
| Read-write unlock | `pthread_rwlock_unlock()` |
| Spinlock | `pthread_spin_lock()` / `pthread_spin_unlock()` |
| Condition wait | `pthread_cond_wait()` |
| Condition notification | `pthread_cond_signal()` / `pthread_cond_broadcast()` |

A mutex follows the familiar critical-section pattern:

```c
pthread_mutex_lock(&mutex);

a++;

pthread_mutex_unlock(&mutex);
```

`pthread_mutex_lock()` waits when another thread owns the mutex; `pthread_mutex_unlock()` releases it. A condition wait atomically releases its associated mutex while blocking, then reacquires that mutex before returning. The caller therefore tests the protected predicate in a loop rather than treating the notification itself as proof that the condition holds.

Read-write locks grant shared ownership to readers and exclusive ownership to writers. Mutex acquisition also has nonblocking, timed, and clock-based variants in addition to the ordinary blocking operation.

### Mutex Lifecycle and Implementation Boundary

A mutex can be initialized statically or initialized and destroyed explicitly:

```c
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
```

```c
pthread_mutex_t mutex;

pthread_mutex_init(&mutex, NULL);

/* use mutex */

pthread_mutex_destroy(&mutex);
```

Explicit initialization permits attributes such as recursive or robust mutex behavior, priority protocols, and process-shared synchronization.

POSIX specifies the interface and synchronization semantics, not that every operation must cross into the kernel. An implementation can acquire an uncontended mutex with user-space atomic operations. When contention requires a thread to sleep, the implementation can obtain kernel assistance; Linux implementations commonly use futexes for that waiting path.

### Spinlocks and Privilege Mode

A spinlock describes a waiting strategy, not a privilege mode. A `pthread_spin_lock()` implementation typically loops in user mode, repeatedly attempting an atomic acquisition. A kernel spinlock is instead used by kernel code and spins while the CPU executes in kernel mode.

A blocking mutex normally avoids that repeated user-space work after contention by waiting until the holder releases it. Spinning is therefore suitable only when the holder is expected to release the lock very quickly; a descheduled holder leaves user-space spinlock waiters runnable and consuming CPU.

## Locks and Descriptor-Based Readiness

A `pthread_mutex_t`, `pthread_rwlock_t`, or `pthread_spinlock_t` is memory-resident synchronization state. It is neither a [file descriptor](02%20The%20Anatomy%20of%20a%20Process.md#File%20Descriptors%20%28FDs%29) nor an open file description, so `select()`, `poll()`, and `epoll` cannot monitor it directly. Kernel-assisted blocking does not change that boundary.

File or record locking is a separate model. A process uses a descriptor to request a lock on a file range with `fcntl()`:

```c
fcntl(fd, F_SETLK, &lock);  /* attempt without waiting */
fcntl(fd, F_SETLKW, &lock); /* wait to acquire */
```

The descriptor identifies the file, but lock availability is not a readiness condition of that descriptor: a readable file does not imply that a record lock is available, and there is no general `EPOLL_LOCK_AVAILABLE` event. Linux open-file-description locks such as `F_OFD_SETLK` associate lock ownership with an open file description, but they still do not create an event source for ordinary readiness interfaces.

### Bridging Memory Synchronization to an Event Loop

An event loop does not wait for a mutex to unlock. When a worker modifies a mutex-protected queue and the loop must react, the worker signals a separate descriptor-backed object after releasing the mutex:

1. The worker locks the queue, modifies it, and unlocks it.
2. The worker writes a notification to the descriptor-backed object.
3. The event loop wakes when that object becomes readable, then acquires the mutex as needed to inspect the shared state.

A pipe provides a portable notification channel. On Linux, `eventfd` provides a dedicated event-counter descriptor that can be monitored by `epoll`. The descriptor carries the wakeup; the mutex still protects the queue's invariants.

## Interprocess Synchronization

Processes share ordinary data through a [shared-memory mapping](08%20Inter-Process%20Communication.md#Shared-Memory%20IPC). To share a POSIX mutex, the mutex itself must be stored in that mapping and configured as `PTHREAD_PROCESS_SHARED`. The default, `PTHREAD_PROCESS_PRIVATE`, is valid only for threads in the same process. The processes use one synchronization object, not separate mutexes that communicate with each other; their virtual addresses for the mapping need not match.

```c
struct SharedState {
    pthread_mutex_t mutex;
    int counter;
};

pthread_mutexattr_t attr;

pthread_mutexattr_init(&attr);
pthread_mutexattr_setpshared(&attr, PTHREAD_PROCESS_SHARED);
pthread_mutex_init(&shared->mutex, &attr);
```

An ordinary heap mutex remains private after `fork()` because ordinary process memory is copy-on-write. A `MAP_SHARED` mapping created before `fork()` instead remains a mapping of the same backing in parent and child. Independently started processes need another way to acquire compatible mappings of the same shared backing.

### Semaphore Placement and Failure Handling

POSIX supports two corresponding semaphore models:

- **Unnamed semaphore:** Place a `sem_t` in shared memory and initialize it with a nonzero `pshared` argument, as in `sem_init(&shared->semaphore, 1, 1)`.
- **Named semaphore:** Independently started processes call `sem_open()` with the same name to connect to one named semaphore object; they do not need to arrange a mapping containing the `sem_t`.

The same distinction applies broadly: shared memory makes an object visible to participants, while a named kernel-managed object lets them rendezvous through its name. Neither model turns a process-shared mutex into a file descriptor.

Process-shared read-write locks and condition variables also place their state in shared memory. File locks and System V semaphores instead belong to the kernel-managed-object model.

If a process dies while holding an ordinary process-shared mutex, another participant can remain blocked indefinitely. Robust mutexes let a later acquirer detect that the previous owner died and recover the protected shared state according to the application's failure protocol.
