# NGINX Internals

NGINX combines a [multi-process execution model](../../Backend%20Engineering/Concurrency/02%20Application%20Server%20Concurrency.md#Multi-Process) with [event-driven connection handling](../../Backend%20Engineering/Concurrency/02%20Application%20Server%20Concurrency.md#Event-Driven%20Connection%20Handling). Worker processes provide CPU parallelism across cores, while each worker's event loop coordinates many network connections without creating one thread per connection.

This architecture separates two paths. Client and upstream traffic flows through listening and connected sockets owned by workers. Process-control messages flow between the master and its children so the master can change the process topology without carrying request data itself.

## The Worker Process Model

An NGINX instance normally consists of one master process and one or more worker processes. Some features also create helper processes, such as cache manager and cache loader processes.

- **Master process:** Reads configuration, prepares a configuration cycle, creates child processes, and coordinates their lifecycle. It does not process client traffic.
- **Worker processes:** Accept connections and advance client, upstream, timer, and protocol state through event handlers. A worker is primarily single-threaded and event-driven.
- **Helper processes:** Perform feature-specific background work that does not belong in the request-processing path.
- **Thread pools:** Offload selected operations that would otherwise block a worker. They supplement the event loop rather than replace the process model.

The configured worker count determines how much worker-level CPU parallelism is available. The default is one worker process; when `worker_processes auto` is configured, NGINX attempts to detect the number of available processors. Matching workers to available processors is a starting point rather than an invariant because the appropriate count also depends on the workload and surrounding resources.

## Startup and Worker Creation

Startup establishes the resources and relationships that the workers later use to process traffic:

1. The master reads the configuration and builds a configuration cycle containing module configuration, listening definitions, paths, and other runtime state.
2. It prepares shared resources such as log files and the listening sockets required by the configured listener architecture.
3. On Unix, before [`fork()`](../../Operating%20Systems/05%20Process%20Management.md#POSIX%20Process-Control%20Interface) creates a non-detached child, NGINX creates a [`socketpair(AF_UNIX, SOCK_STREAM, ...)`](../../Operating%20Systems/08%20Inter-Process%20Communication.md#Unix-Domain%20Sockets%20and%20Socket%20Pairs). The parent and child retain opposite endpoints as an internal control channel.
4. The child inherits the descriptors and state made available through process creation, then initializes the event-processing environment for its process type.
5. Worker processes enter their event loops and begin handling events for the listening sockets and connections assigned to them.

Because the master creates each child and its socket pair, the control endpoints require no pathname, listener, or later connection handshake.

## Connection Acceptance and Socket Management

The kernel maintains the [queues associated with each listening socket](../../Operating%20Systems/07%20Socket%20Management.md#Pending%20and%20Established%20Connection%20Queues). When a connection becomes available, a worker accepts it and receives a new connected socket. That worker then owns the client-side transport I/O until the connection is closed, although it may also coordinate separate upstream connections while processing the client's request.

NGINX supports two listener-ownership models. They differ in how the kernel and workers select the worker that will accept a new connection.

### Shared Listening Socket

Several workers can inherit references to one [shared listening socket](../../Operating%20Systems/07%20Socket%20Management.md#Shared%20Listening%20Socket) and call `accept()` themselves. Only one worker receives a given connected socket, but several workers may observe activity on the shared listener.

NGINX and the operating system can coordinate this accept path in different ways. An enabled `accept_mutex` serializes acceptance among workers. On supported systems, wake-up behavior such as `EPOLLEXCLUSIVE` reduces unnecessary competition without that mutex. The available behavior therefore depends on the event method, platform, version, and configuration rather than solely on the fact that the listener is shared.

### Per-Worker Listeners with `reuseport`

When a `listen` directive enables [`reuseport`](../../Operating%20Systems/07%20Socket%20Management.md#Multiple%20Listeners%20with%20SO_REUSEPORT) on a supported platform, NGINX creates an independent listening socket for each worker while binding those sockets to the same local address and port. The kernel assigns incoming traffic among the sockets, so workers do not coordinate access to one shared accept path.

Separate listeners reduce accept-path contention, but kernel distribution operates on transport traffic rather than the amount of application work that each connection will produce. Connections can therefore be distributed evenly while CPU, memory, or request-processing work remains uneven.

| Dimension | Shared listener | Per-worker `reuseport` listeners |
| --- | --- | --- |
| Listener ownership | Several workers reference one socket | Each worker owns an independent socket |
| Accept queue | Shared by the workers | Separate queue for each listener |
| Initial distribution | Workers coordinate acceptance | Kernel selects a listener |
| Main limitation | Contention or unnecessary wake-ups can occur | Transport distribution may not balance application work |

> [!note] Version boundary
> The `reuseport` parameter became available in NGINX 1.9.1. It introduced an optional listener architecture rather than replacing the shared-listener model for every later deployment.

## Worker Event Loop and Connection Lifecycle

A worker uses an operating-system event method such as `epoll` or `kqueue` to observe many resources through [readiness-based I/O](../../Operating%20Systems/07%20Socket%20Management.md#Readiness-Based%20I%2FO). Readiness means that an operation may make progress; the corresponding handler still performs the `accept()`, `read()`, or `write()` operation and updates the resource's state.

Each event-loop iteration follows an ordered cycle:

1. Find the timer nearest to expiration and use it to bound the next wait.
2. Ask the configured event module to wait for I/O events.
3. Dispatch handlers for resources reported as ready.
4. Expire elapsed timers and invoke their handlers.
5. Process events that handlers deferred to the posted-events queue.

The handlers advance connections incrementally rather than completing one connection before considering another:

1. A readiness event on a listener causes the worker to accept a client connection and allocate connection state for the resulting socket.
2. The selected protocol handler initializes the connection, including any required proxy-protocol parsing or TLS handshake.
3. Later read and write events advance request parsing, response transmission, or bidirectional stream forwarding.
4. Reverse proxying adds an upstream connection whose connect, read, write, and timeout events are coordinated by the same worker event loop.
5. After processing finishes, NGINX either waits for another request on a reusable connection or closes the connection and releases its state.

When one connection is waiting for network readiness, the worker continues dispatching ready events for other connections. This is the mechanism that produces high I/O concurrency within a single worker; the multiple worker processes separately provide CPU parallelism.

## Blocking Work and Thread-Pool Offload

Nonblocking network waits do not suspend the worker on behalf of one connection. The event loop records the required state, stops advancing that connection, and handles other ready work. If no events are ready, the worker sleeps inside the operating system's event-wait operation until I/O or the next timer wakes it.

A blocking system call or long CPU-bound handler has a different effect: it occupies the worker's event-loop thread, so the worker cannot advance its other connections until that operation returns. NGINX modules must therefore avoid blocking work in event handlers or arrange an appropriate offload mechanism.

NGINX thread pools provide bounded offload for selected operations, including supported file I/O. A worker submits a task, continues processing events, and later handles the task's completion. This interface is not a general-purpose threaded request model: most NGINX functions are not thread-safe, so an offloaded task must restrict itself to supported system calls or thread-safe library work.

## Master Process and Worker Control

The master uses the Unix-domain socket pairs it creates for child processes to send compact process-control messages rather than client request data. Commands include graceful quit, immediate termination, log reopening, and opening or closing process channels.

NGINX maintains process-channel information in every process as its topology changes. The master creates a child's socket pair before `fork()`, so the new child inherits descriptors that already exist, including channels for earlier children. If the master later creates a socket pair for another child, that new child inherits the older channels, but an earlier worker cannot retroactively inherit the newly created channel.

To distribute that later channel, the master sends an `NGX_CMD_OPEN_CHANNEL` (`OPEN_CHANNEL`) message to already-running children. The message passes the new process's [channel descriptor](../../Operating%20Systems/08%20Inter-Process%20Communication.md#Explicit%20Descriptor%20Passing) with `SCM_RIGHTS`; it does not create the underlying socket pair. Each receiver gets its own process-local descriptor referring to the same channel endpoint and updates its local process/channel bookkeeping. When a child exits, the master sends `CLOSE_CHANNEL` so the remaining processes release the stale descriptor.

These bidirectional socket pairs are IPC primitives, but NGINX's process-control protocol primarily uses them from the master toward its children. They remain separate from the [listening and connected sockets](../../Operating%20Systems/07%20Socket%20Management.md#Listening%20Socket%20vs.%20Connected%20Socket) that carry client and upstream traffic.

### Configuration Reload

A reload replaces one worker generation without abruptly terminating connections owned by the previous generation:

1. The master receives a reload signal and validates the new configuration.
2. It attempts to prepare new resources, including log files and listening sockets required by that configuration.
3. If preparation fails, the master keeps the previous configuration and existing workers running.
4. If preparation succeeds, the master starts a new worker generation with the new configuration.
5. It asks the old workers to shut down gracefully. Those workers close their listening sockets, stop accepting new connections, and continue serving existing clients.
6. Each old worker exits after its remaining connections finish.

The same control boundary supports other lifecycle actions:

- **Graceful shutdown:** Workers stop accepting new connections and drain existing work before exiting.
- **Fast shutdown:** Workers terminate without waiting for active connections to complete.
- **Log reopening:** Processes reopen log files after external rotation.
- **Executable upgrade:** The master coordinates starting a new executable while preserving the resources required for a controlled transition.
