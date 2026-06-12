# Backend Execution Patterns

Previously we talked about how backend communicates with clients. Here the focus is on how a backend works internally.

## Process vs Thread

### Process

* From the CPU perspective, a process is a set of instructions.
* A process has isolated memory.
  * It owns a reserved memory space that other processes cannot normally read.
  * In some cases you can explicitly share memory between processes.
* Every process has a PID.
* Processes are scheduled on the CPU.
  * CPU time is scarce, so processes compete for it.
  * When a process performs blocking work, such as disk I/O, the kernel can deschedule it immediately.

### Thread

* Also called a lightweight process.
* A thread is also a set of instructions.
* Threads share memory with the parent process.
* Each thread has its own ID.
* Threads are also scheduled on the CPU.

### Single-threaded process

* One process with a single thread.
* Simpler execution model.
* Example: Node.js.

### Multi-process

* An application runs multiple processes.
* Each process has its own memory.
* Examples: NGINX and Postgres.
* Takes advantage of multiple CPU cores.
* Uses more memory, but gives stronger isolation.
* Redis backup routines are a useful example.
  * Redis needs to persist in-memory data without stopping normal traffic.
  * Copy-on-write helps here.
  * When the backup process is reading memory and a page is about to change, the OS copies that page so the backup sees a consistent snapshot.

### Multi-threaded

* One process with multiple threads.
* Threads share memory, so they compete for shared state.
* Takes advantage of multiple CPU cores.
* Uses less memory than multi-process designs.
* Introduces race conditions if shared state is not synchronized properly.
* Locks and latches can make a multi-threaded program slower if contention is high.
* Examples: Apache and Envoy.

### How many is too many?

* CPU context switching is costly.
* More processes or threads usually means more scheduling overhead.
* A common rule of thumb is to start around `number of cores = number of workers`, then adjust based on workload.


## Architecture

Backends can [establish connections](../Networking/03%20Connections/01%20How%20Connections%20are%20Established.md) and [read and send data](../Networking/03%20Connections/02%20Reading%20and%20Sending%20Data.md) in several ways, depending on how they distribute three core roles:

- **`listener`:** The thread or process that binds to an address/port, calls `listen()`, and manages the listening socket.
- **`acceptor`:** The thread or process that calls `accept()` on the listening socket, turning pending network connections into dedicated file descriptors (connected sockets).
- **`worker`:** The code responsible for reading the request, executing the business logic, and writing the response.

A single thread can do all three jobs simultaneously, or the backend can split them strategically to scale.

### 1. Single Listener, Single Worker Thread

- **Example:** Node.js, Redis.
- **How it works:** One single main thread acts as the listener, acceptor, and worker, relying heavily on non-blocking I/O and an Event Loop to juggle connections.
- **Pros:** Extremely simple to reason about; no data locking or thread synchronization issues.
- **Cons:** If there is a massive spike in active connections (or if the business logic requires heavy CPU computation), that single thread becomes a bottleneck.
- **Scaling:** You scale horizontally by running multiple isolated processes (e.g., using Node's `cluster` module) rather than spawning threads.

### 2. Single Listener, Multiple Worker Threads

- **Example:** Memcached.
- **How it works:** A single main process/thread owns the listening and accepting phases. Once it accepts a connection, it hands off the file descriptor to a pool of worker threads.
- **Pros:** The main thread effectively acts as an internal load balancer, distributing connections across the workers.
- **Cons:** Load balancing connections can be tricky because connection lifespan and CPU cost vary wildly.
- **Variation (RAMCloud):** The main process listens, accepts, _and_ reads the raw network data, only offloading the actual request processing to the worker threads. However, the central accepting process can still become a bottleneck under heavy connection loads.

### 3. Multiple Threads, Single Shared Socket

- **Example:** NGINX (older configurations) or standard Apache worker models.
- **How it works:** The OS maintains one listening socket, but multiple worker threads/processes all share it and actively compete to call `accept()` on it.
- **Pros:** Once a worker successfully accepts a connection, it fully owns the file descriptor and handles all the work.
- **Cons:** Requires strict locking and coordination. If a new connection arrives and wakes up _all_ sleeping workers to accept it, but only one succeeds, it causes a massive spike in wasted CPU cycles (a classic issue known as the **Thundering Herd** problem).

### 4. Multiple Listeners (Same Port and Address)

- **Example:** NGINX (modern configurations), HAProxy.
- **How it works:** Uses the `SO_REUSEPORT` socket option. The OS allows multiple independent worker processes to bind to the exact same port. The OS kernel creates separate accept queues for each listener and distributes incoming connections between them.
- **Pros:**
    - Completely eliminates the "Thundering Herd" problem because workers no longer step on each other competing for a single socket.
    - Removes the need for locking mechanisms around a shared acceptor.
- **Cons:**
    - **Unfair Balancing:** The OS-level load balancer uses a simple hash algorithm; it does not understand the actual CPU cost of requests, so some workers might get overloaded while others sit idle.
    - **UDP/QUIC Issues:** With connectionless protocols, datagrams belonging to the same application-level session can sometimes be routed to different workers awkwardly.
    - **Security Risk:** Port hijacking is a risk if unrelated, malicious processes are allowed to bind to the same active port.

## Idempotency

* An idempotent request can be repeated without changing the final backend state after the first successful application.
* This matters when the server may have processed a request, but the client never received the response.
* In that case, the client or an intermediary may retry.

### In HTTP

* `GET` is idempotent.
  * Browsers and proxies assume that.
  * So `GET` should not perform writes beyond incidental effects such as logs.
* `POST` is not idempotent by default, but you can design it to be.

### Common ways to make writes idempotent

* Use a `requestID` or idempotency key.
  * If the key was already processed, return the stored result or avoid repeating the side effect.
  * This requires persistent lookup and bookkeeping.
* Use an upsert-style write.
  * Instead of blindly inserting, create the record or update it if it already exists.

This is especially important in payment flows, retries through proxies, and any system where duplicate execution is expensive.

## When do you use threads?

Threads add complexity, shared-state management, and locking concerns, so they should be used when they solve a real execution problem.

You should consider threads when one or more of these apply:

### IO blocking

* Disk I/O may block the executing thread depending on the kernel interface and API used.
* Offloading that work to a different thread keeps the main execution path responsive.
* Logging is a common example.
* If you can perform the work asynchronously, such as with `io_uring`, extra threads may be less necessary.
* Socket I/O is usually handled asynchronously with mechanisms such as `epoll` or `select`.

### Heavy CPU-bound work

* Some work consumes enough CPU time that it starves the rest of the process.
* Offloading it to another thread lets the main execution path continue on its core while the heavy task runs elsewhere.

### Large volumes of small tasks

* A single execution path may not provide enough throughput for very high rates of small tasks.
* Accepting large numbers of incoming connections is a good example.
* In these cases, multiple threads can increase throughput, especially when combined with designs such as `SO_REUSEPORT`.

Threads are not automatically better. They become worth the coordination cost only when the workload justifies them.
