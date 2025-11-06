# Synchronous vs Asynchronous workloads

## Synchronous

In synchronous connections, the caller must keep the connection open until the receiver responds.

* Meanwhile, the receiver sits idle.

* In the ’90s, when even the web was fully synchronous, a running background loop could stop button animations from working.

### Example of an OS synchronous I/O

* Program asks OS to read form disk
* Program main thread is taken off of the CPU
  * the kernel will put other process on the meantime
* Read completes, program can resume execution
  * the kernel back the program to the CPU

## Asynchronous

* Caller sends a request
* Caller can work until it gets a response
* Caller either:
  * Checks if the response is ready (epool)
  * Receiver calls back whe it's done (io_uring)
  * Spins up a new thread that blocks
    * There is a trick that transforms a synchronous operation into an asynchronous one: instead of handling the blocking task directly, the main thread defers it to another thread.
* Caller and receiver are not necessary in sync

### Example of an OS asynchronous call (NodeJS)

* Programs spins up a secondary thread
* Secondary thread reads from disk, OS blocks it
* Main program still running and executing code
* Thread finish reading and calls back main thread

```javascript
// Program starts
// CPU begins executing synchronous tasks
doWork();

// Program initiates an asynchronous read from disk
// Specifies a callback (onReadFinished) to be invoked when done
readFile("largefile.dat", onReadFinished);

// The file read is likely still in progress
// Meanwhile, the program continues with other work
doWork2();

// Later, once the file read is complete...
// The event loop invokes the callback
----> onReadFinished(theFile)
```

## Synchronous vs Asynchronous is Request-Response

* Synchronicity is a client property: "can I continue to work while want?"
* most modern client libraries are asynchronous
* Eg. Clients send a HTTP request and do work
* Whether the processing is synchronous or asynchronous depends on the scope. For example, a client can make an asynchronous request to the backend for a long-running task, but then repeatedly polls to check the result. Thus, although each individual requests is asynchronous, the overall system behaves synchronously.

# Asynchronous workload is everywhere

* Asynchronous Programming (promises/futures)
  * when a task calls an async routine, instead running it within the same flow of execution, it defer to another flow of execution, so the caller remains unblocked. Instead of returning the results immediately, the async function returns a promise that can be used by the caller to get the results later.
* Asynchronous back-end processing
  * The most beautiful way to process something asynchronously is queuing: the client sends a request, the server immediately queues it and returns a job ID to the client, which the client uses to request the results.
* Asynchronous commits in PostgreSQL:
  * The database leans on two data structures to handle the transactions. The first one is 'the WAL' (Write-Ahead Log), which is stored in the durable memory and serves as a journal for an ongoing transaction's changes. The second one is 'the pages', which are partly in-memory (the buffer), and partly on the durable memory. In an ongoing transaction, all the changes are recorded in the WAL and at the in-memory pages.
  * A commit means to flush the changes that are in the WAL to the durable pages. The database can't simply flush the changes from the in-memory pages because it isn't crash safe, unlike the WAL. A synchronous commit keeps the connection with the client until the flushing finishes. An asynchronous commit will close that connection before it happens, creating a risk that the client may be unaware of a write failure.
* Asynchronous replication: given a stateful service, the client can synchronously write to the primary shard, which can asynchronously relay it to the replica shards.
* Asynchronous OS fsync (fs cache): when you invoke `write()` to write something to secondary memory, it doesn't actually go there immediately; instead, it stays in the file system cache for a while, then the os flushes it to secondary memory based on cache usage or time criteria, minimizing either the HDD fragmentation or SSD page rewrites. However, databases usually use `fsync()` to write data synchronously, since it ensures data durability, and typically they already have their own mechanisms to avoid excessive IO operations.

# Demo NodeJS

Given the `text.txt`

```
loren
```

## Sync

Given the `sync.js`

```javascript
const fs = require("fs");

console.log("1");
const res = fs.readFileSync("text.txt");
console.log("file: " + res)
console.log("2")
```

Then the output is;

```
> node sync.js
1
file: loren
2
```

The `fs.readFileSync` is blocking the system, this is the reason why the `1` was printed before and `2` after the file content.

## Async

Given the `async.js`

```javascript
const fs = require("fs");

console.log("1");
fs.readFile("text.txt", (err, data) => console.log("file: " + data.toString()));
console.log("2")
```

Then the output is;

```
> node async.js
1
2
file: loren
```

The `fs.readFile` method doesn't block the system, so `2` is printed immediately after the `fs.readFile` call, while the file is being read asynchronously in the background.
