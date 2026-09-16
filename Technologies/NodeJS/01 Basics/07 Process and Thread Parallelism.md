# Process and Thread Parallelism

A Node.js process executes JavaScript callbacks on one application thread. Non-blocking I/O lets that thread coordinate many connections, but a CPU-bound callback prevents it from running other JavaScript callbacks until it returns. Parallel CPU execution therefore requires additional processes or application threads.

- **Cluster workers:** Separate Node.js processes are useful when several server instances should accept work through one port.
- **Worker threads:** Threads inside one Node.js process are useful when CPU-intensive work should run in parallel without process isolation.

These mechanisms do not make one synchronous callback execute on several cores. The application must divide independent work between workers.

## Cluster Module

The `node:cluster` module starts several Node.js worker processes under a primary process. The workers can share a server port, allowing the operating system to schedule their application threads on different CPU cores. This is a process-based form of the [multi-process application-server model](../../../Backend%20Engineering/Concurrency/02%20Application%20Server%20Concurrency.md#Multi-Process).

### Primary and Worker Responsibilities

`cluster.fork()` uses the same Node child-process mechanism as [`child_process.fork()`](04%20Internals.md#Child%20Processes%20and%20IPC). Each worker has its own address space, V8 instance, and event loop; the primary communicates with it through the process IPC channel. Cluster adds server-handle coordination and connection distribution on top of that child-process relationship.

- **Primary process:** Starts workers, observes their lifecycle, and coordinates server handles. It should not retain application state that workers must access for every request.
- **Worker process:** Runs the application server and handles the connections assigned to it.
- **Process-local memory:** An object, cache, or session stored in one worker is not visible to another worker. State shared across workers belongs in an external service or another explicit coordination mechanism.
- **Worker count:** [`os.availableParallelism()`](https://nodejs.org/api/os.html#osavailableparallelism) provides the number of parallelism units available to the process. Use it as a starting point, then measure memory use, contention, and throughput for the actual workload.

### Cluster Connection Distribution

The primary starts a worker for each available parallelism unit. The following program creates the application server only in worker processes:

```javascript
const cluster = require('node:cluster');
const http = require('node:http');
const { availableParallelism } = require('node:os');

if (cluster.isPrimary) {
  for (let index = 0; index < availableParallelism(); index += 1) {
    cluster.fork();
  }

  cluster.on('exit', (worker, code, signal) => {
    console.error(
      `Worker ${worker.process.pid} exited with code ${code} and signal ${signal}`
    );
    // An application may decide whether and when to replace this worker.
  });
} else {
  http.createServer((request, response) => {
    response.end(`Handled by worker ${process.pid}\n`);
  }).listen(3000);
}
```

Every Cluster worker executes the same `server.listen(3000)` call, but that source-code location does not determine which process accepts connections. Cluster's scheduling policy determines whether the primary distributes accepted connections or workers accept them directly.

#### Primary-Distributed Connections

The default policy on platforms other than Windows follows the [single-acceptor, multiple-worker model](../../../Backend%20Engineering/Concurrency/02%20Application%20Server%20Concurrency.md#Single%20Acceptor,%20Multiple%20Workers):

1. A worker calls `listen(3000)`.
2. Cluster sends that request to the primary through its internal IPC channel.
3. The primary owns the listening socket and accepts new connections.
4. The primary selects a worker and passes the connected socket to it through IPC.
5. The selected worker handles the connection and its requests.

The worker's `listen()` call therefore requests access to a shared server; it does not independently bind port `3000`.

#### Direct Worker Acceptance

Cluster also supports the [multiple-workers, shared-listening-socket model](../../../Backend%20Engineering/Concurrency/02%20Application%20Server%20Concurrency.md#Multiple%20Workers,%20Single%20Shared%20Listening%20Socket). The primary creates the listening socket and makes it available to workers, which then accept connections directly. The operating-system scheduler can distribute connections unevenly, so neither mode guarantees that expensive requests are balanced across workers.

Set `cluster.schedulingPolicy` to `cluster.SCHED_NONE` in the primary before creating any workers or calling `cluster.setupPrimary()`:

```javascript
if (cluster.isPrimary) {
  cluster.schedulingPolicy = cluster.SCHED_NONE;

  for (let index = 0; index < availableParallelism(); index += 1) {
    cluster.fork();
  }
}
```

The policy is global and becomes fixed after the first worker is spawned or `cluster.setupPrimary()` runs. `NODE_CLUSTER_SCHED_POLICY=none` sets the same policy when Node starts.

## Worker Threads Module

The `node:worker_threads` module runs JavaScript in parallel threads inside one Node.js process. Unlike Cluster workers and child processes, worker threads can exchange data through message passing and can explicitly share memory with `SharedArrayBuffer`. Shared mutable memory requires synchronization.

Worker threads fit CPU-intensive tasks that can be separated from request handling, such as parsing or computation. They do not improve ordinary I/O-heavy work, because Node's asynchronous I/O already avoids blocking the application thread while I/O waits. For repeated tasks, reuse a pool of worker threads rather than creating a thread for every request.

```javascript
// worker-task.js
const { parentPort, workerData } = require('node:worker_threads');

let total = 0;
for (let index = 0; index < workerData.limit; index += 1) {
  total += index;
}

parentPort.postMessage(total);
```

```javascript
// main.js
const { Worker } = require('node:worker_threads');

function sumInWorker(limit) {
  return new Promise((resolve, reject) => {
    const worker = new Worker('./worker-task.js', {
      workerData: { limit },
    });

    worker.once('message', resolve);
    worker.once('error', reject);
    worker.once('exit', (code) => {
      if (code !== 0) {
        reject(new Error(`Worker stopped with exit code ${code}`));
      }
    });
  });
}
```

## Choosing a Concurrency Boundary

| Requirement | Appropriate mechanism | Main consequence |
| --- | --- | --- |
| Scale an HTTP server across process isolation boundaries | Cluster workers | Separate memory and event loops; coordinate shared state explicitly. |
| Run a bounded CPU-heavy task beside request handling | Worker threads | Shared process resources are available; shared mutable memory needs synchronization. |
| Start and communicate with a specific separate Node.js program | `child_process.fork()` | Separate process connected through IPC; no shared server-port behavior is added. |

Processes and threads are complementary rather than interchangeable. A service can use several processes to scale request handling and worker threads inside each process for CPU-heavy tasks, but each added execution unit also adds memory use, scheduling overhead, and coordination work.
