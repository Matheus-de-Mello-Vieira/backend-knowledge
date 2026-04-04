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

## Connections and Socket I/O

These topics were moved to Networking and are maintained there:

* [How Connections are Established](../../../Networking/03%20Connections/01%20How%20Connections%20are%20Established.md)
* [Reading and Sending Data](../../../Networking/03%20Connections/02%20Reading%20and%20Sending%20Data.md)
* [Nagle's Algorithm](../../../Networking/03%20Connections/03%20Nagle%27s%20algorithm.md)

From the backend perspective, these notes explain what the kernel is doing before your application logic even starts: creating connections, buffering reads and writes, acknowledging data, and sometimes delaying small writes for efficiency.

## Architecture

### Definitions

* `listener`: the thread or process that calls `listen` on an address and port and gets back a listening socket.
* `acceptor`: whatever has access to that socket and calls `accept` to turn pending connections into file descriptors.
* `worker`: the code responsible for reading, processing, and writing data.

A single thread can do all three jobs, or you can split them strategically.

### Single listener, single worker thread

* Node.js is a common example.
* One single thread is the listener, acceptor, and reader.
* You can still scale by running multiple Node processes.
* If there are many active connections, that single thread can become overloaded.

### Single listener, multiple worker threads

* Memcached is an example.
* A single process owns listening and accepting.
* Worker threads each handle a set of accepted connections.
* The main process effectively load-balances connections across threads.
* This can be tricky because connection cost and duration vary a lot.

RAMCloud uses a related idea with more explicit offloading:

* A process listens, accepts, and reads.
* It then offloads requests to worker threads.
* That central process can still become a bottleneck.

### Multiple threads, single socket

* NGINX can be configured this way.
* One listening socket is shared across workers.
* Multiple threads or workers compete to accept from the same socket.
* This requires coordination so two workers do not accept the same connection.
* Once a worker accepts a connection, it owns it.

### Multiple listeners on the same port and address

* The OS creates separate accept paths for each listener and distributes incoming work between them.
* This is common in proxies, including NGINX.
* `SO_REUSEPORT` is the key socket option for this design.
* Advantages:
  * Workers do not step on each other while accepting.
  * It removes some locking around a single shared acceptor.
* Problems:
  * OS-level balancing can be unfair because it does not understand actual request cost.
  * With UDP and QUIC, datagrams from the same application-level exchange can be distributed awkwardly.
  * Port hijacking is a risk if unrelated processes can bind the same port.

## Idempotency

* An idempotent request can be repeated without changing the final backend state after the first successful application.
* This matters when the server may have processed a request but the client never received the response.
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
