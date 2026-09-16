# NGINX Internals

NGINX combines a multi-process execution model with [event-driven connection handling](../../Backend%20Engineering/Concurrency/02%20Application%20Server%20Concurrency.md#Event-Driven%20Connection%20Handling). [Application-server concurrency models](../../Backend%20Engineering/Concurrency/02%20Application%20Server%20Concurrency.md#Application%20Execution%20Models) provide the broader context for these two architectural decisions.

## The Worker Process Model

An NGINX instance normally consists of one master process and multiple worker processes; helper processes may also exist for features such as cache management. The master owns process lifecycle and control, while workers handle client traffic. A worker is primarily event-driven and single-threaded; optional thread pools can offload selected blocking work without turning the whole NGINX instance into a single process.

- **Multi-Process Architecture:** NGINX relies on multiple worker processes rather than spawning a new thread per connection.
- **Hardware Thread Mapping:** By default (when set to auto-mode), NGINX spins up exactly one worker process per available hardware thread (CPU core).
- **High Concurrency:** Because of its non-blocking, event-driven nature, a single NGINX worker process can simultaneously handle thousands of active client connections.
- **CPU Efficiency:** Workers are designed to stay active on the CPU for the maximum time possible to process requests efficiently.
- **Context Switching:** A worker only exits the CPU (yields) when it is forced to wait on a blocking I/O operation, such as reading content from a physical disk or waiting for a response from an upstream backend server.

## Master Process and Worker Control

The master process creates worker and helper processes and coordinates their lifecycle. On Unix, before [`fork()`](../../Operating%20Systems/05%20Process%20Management.md#POSIX%20Process-Control%20Interface) creates a non-detached child, NGINX creates a [`socketpair(AF_UNIX, SOCK_STREAM, ...)`](../../Operating%20Systems/08%20Inter-Process%20Communication.md#Unix-Domain%20Sockets%20and%20Socket%20Pairs); the parent and child retain opposite endpoints as an internal control channel. Because the master creates the child itself, the endpoints can be distributed through that process-creation relationship without a pathname, listener, or later connection handshake.

NGINX sends compact process-control messages through these channels rather than client request data. The channel protocol includes commands for graceful quit, immediate termination, reopening logs, and opening or closing process channels. When a new worker or helper starts, the master can send an `OPEN_CHANNEL` message containing that process's channel descriptor to already-running children; when a child exits, it sends `CLOSE_CHANNEL` so the remaining processes can release the stale descriptor. The socket pair is bidirectional as an IPC primitive, although NGINX currently uses these process-control messages from the master toward its children.

These control channels are separate from the [listening and connected sockets](../../Operating%20Systems/07%20Socket%20Management.md#Listening%20Socket%20vs.%20Connected%20Socket) that carry client traffic. A worker's event loop handles network connections, while the master-to-child socket pairs coordinate the process topology that surrounds those workers.

## Connection Acceptance and Socket Management

- **Kernel Handoff:** The operating system kernel sits directly behind the worker processes, maintaining the [queues for incoming network traffic](../../Operating%20Systems/07%20Socket%20Management.md#Pending%20and%20Established%20Connection%20Queues).
- **Rapid Acceptance:** NGINX aims to accept incoming connections as quickly as possible. Once a connection is accepted, a specific worker becomes the dedicated reader for that connection's lifecycle.
- **Pre-1.9.1 (Single Shared Socket / Multiple Acceptors):** In older versions, NGINX used a shared socket approach where multiple worker processes actively competed to call `accept()` on a single listening socket. This required strict locking and often caused the "[Thundering Herd](../../Operating%20Systems/07%20Socket%20Management.md#Shared%20Listening%20Socket)" problem, wasting CPU cycles.
- **Post-1.9.1 (Socket Sharding / Multiple Listeners):** Modern NGINX uses socket sharding by leveraging the [`SO_REUSEPORT`](../../Operating%20Systems/07%20Socket%20Management.md#Multiple%20Listeners%20with%20SO_REUSEPORT) kernel feature. Multiple independent worker processes bind to the exact same port.
- **Kernel Load Balancing:** With socket sharding enabled, the OS kernel creates separate accept queues for each worker process and handles the distribution of incoming connections, completely eliminating the Thundering Herd problem and the need for internal locking.
