# Internals

## libuv

* **what?**: `Libuv` is a cross platform open source library written in C language
* **why?**: handles asynchronous non-blocking operations in Node.JS
* **how?**: using, mainly, thread pool and event loop

In Node.JS, async methods are handled by libuv

They are handled in two different ways:

1) Native async mechanism (delegates to the OS kernel)
   * Network I/O (TCP, UDP, pipes, TTY)
   * File system change notifications
   * Timers
   * OS signals
   * Child process spawning
   * Cross-thread async notifications
2) Thread pool
   * Filesystem operations (reading, writing, metadata)
   * DNS resolution
   * CPU-bound tasks (e.g., crypto, compression, custom work)

### thread pool

#### Structure

```mermaid
flowchart LR
    MainThread(Main Thread)
    ThreadPool(Thread Pool)
     
    MainThread --> ThreadPool
    subgraph "libuv"
      ThreadPool
    end

```

#### How it works

For example, the code:

```javascript
const fs = require('fs');

// 1. Offload file read to libuv's thread pool via async API
fs.readFile('example.txt', 'utf8', (err, data) => {
  if (err) {
    console.error('Error reading file:', err);
    return;
  }
  console.log('Main thread: File contents received:', data);
});

// 2. Meanwhile, main thread keeps running other tasks
console.log('Main thread: Doing Task A...');
console.log('Main thread: Doing Task B...');;
```

It runs:

```mermaid
sequenceDiagram
    participant MainThread
    participant libuv
    participant ThreadPool

	MainThread->>libuv: Request to read file
    Note right of MainThread: Continues executing other tasks...

    libuv->>ThreadPool: Assign file read task
    ThreadPool-->>libuv: Task complete with file contents

    MainThread-->>MainThread: Do Task A
    MainThread-->>MainThread: Do Task B

    libuv-->>MainThread: Invoke callback with data

```

It increases the performance in doing multiple async tasks at same time, for example:

```javascript
const fs = require('fs');

// List of files to read
const files = ['file1.txt', 'file2.txt', 'file3.txt'];

files.forEach((filename) => {
  fs.readFile(filename, 'utf8', (err, data) => {
    if (err) {
      console.error(`Error reading ${filename}:`, err);
      return;
    }
    console.log(`File ${filename} contents:\n`, data);
  });
});

// Meanwhile, the main thread keeps doing other things
console.log('Main thread: Executing Task A...');
console.log('Main thread: Executing Task B...');
```

```mermaid
sequenceDiagram
    participant MainThread
    participant libuv
    participant ThreadPool

    MainThread->>libuv: Request read file1
    libuv->>ThreadPool: Assign file1 task
    MainThread->>libuv: Request read file2
    libuv->>ThreadPool: Assign file2 task
    MainThread->>libuv: Request read file3
    libuv->>ThreadPool: Assign file3 task

    Note right of MainThread: Executes Task A and B...

    ThreadPool-->>libuv: file1 read complete
    ThreadPool-->>libuv: file2 read complete
    ThreadPool-->>libuv: file3 read complete

    libuv-->>MainThread: Callback with file1 contents
    libuv-->>MainThread: Callback with file2 contents
    libuv-->>MainThread: Callback with file3 contents

```

By default, Libuv's thread pool have 4 threads.

* You can change it by:

  ```
  process.env.UV_THREADPOOL_SIZE = 5;
  ```

  * if you increase the thread-pool size beyond to number of CPU cores, the average time per CPU-bound task increase.
    * Given `n` cores and `UV_THREADPOOL_SIZE=n`, each task has its own CPU core. Then, `n` similar asynchronous CPU-bound tasks requested at the same time will run in parallel, with each taking roughly `t` time, so all tasks together will take about `t` time.
    * Conversely, given `UV_THREADPOOL_SIZE=2n`, each pair of tasks shares the same CPU core, so their pace is halved. Then, `2n` similar asynchronous CPU-bound tasks requested at the same time will run in parallel, with each taking roughly `2t` time, so all tasks together will take about `2t` time.
    * Although the thread pool preserves asynchronous with respect to Node’s main thread, it can still become a bottleneck if all threads are busy

network IO tasks don't use thread pool, instead Libuv delegates the work to the operation system kernel and whenever possible, it will poll the kernel and see if the request has completed.

### Event loop

* It is a C program and is part of libuv
* A design pattern that orchestrates or co-ordinates the execution of synchronous and asynchronous code in Node.js.
* It co-ordinates the execution of callbacks in six different queues:

  * 4 macro-tasks queue:
    1) **timer queue**: `setTimeout`/`setInterval` callbacks
    2) **I/O queue**: I/O callbacks
    3) **check queue**: `setImmediate` callbacks
    4) **close queue**: close handlers
  * 2 micro-tasks queue
    1) **nextTick queue**
    2) **promise queue**

#### Process

1) After the call stack is empty, the event loop takes control.
   * Synchronous JavaScript runs to completion before any async callbacks.
   * Async callbacks are enqueued synchronously.

2) The event loop processes its phases in order. In each phase, it executes *all* ready callbacks in that phase. For **each** callback:
   * Runs the callback.
   * Drains all microtasks:
     * `process.nextTick` queue first, then the Promise microtask queue.
     * After draining Promises, Node.js rechecks `nextTick` before continuing.
     * If microtasks keep being scheduled, this draining can repeat indefinitely before the next callback.

3) Phases are processed in order:
   1. Timers phase: executes timer callbacks one by one, draining microtasks after each.
   1. I/O phase: executes I/O callbacks one by one, draining microtasks after each.
   1. Check phase: executes check callbacks one by one, draining microtasks after each.
   1. Close phase: executes close callbacks one by one, draining microtasks after each.

4) When there are no more callbacks to process in any queue and no pending work, the event loop exits and the process ends.

So:

```mermaid
sequenceDiagram
  participant EventLoop
  participant NextTickQueue
  participant PromiseQueue

  Note over EventLoop: Start draining microtasks

  loop While microtasks queues are not empty
    Note over NextTickQueue: Drain nextTick queue completely
    loop While nextTickQueue is not empty
      EventLoop->>NextTickQueue: Get next nextTick callback
      NextTickQueue-->>EventLoop: Execute nextTick callback
    end
    Note over NextTickQueue: nextTick queue is empty

    Note over PromiseQueue: Drain Promise queue completely
    loop While Promise queue is not empty
      EventLoop->>PromiseQueue: Get next Promise callback
      PromiseQueue-->>EventLoop: Execute Promise callback
    end
    Note over PromiseQueue: Promise queue is empty
  end

  Note over EventLoop: Microtasks fully drained
```

```mermaid
sequenceDiagram
  participant MainThread
  participant EventLoop
  participant TimerQueue
  participant IOQueue
  participant CheckQueue
  participant CloseQueue

  MainThread->>EventLoop: Call stack empty
  Note over EventLoop: Event loop cycle starts

  loop While there are callbacks to process
    EventLoop->>EventLoop: Drain Microtasks Queue (see microtasks diagram)

    Note over EventLoop: Timers phase
    loop For each timer callback
      EventLoop->>TimerQueue: Get next timer callback
      TimerQueue-->>EventLoop: Timer callback
      EventLoop->>EventLoop: Drain Microtasks Queue (see microtasks diagram)
    end

    Note over EventLoop: Poll phase

  	loop While in Poll phase
    alt I/O callbacks ready
      EventLoop->>IOQueue: Get next I/O callback
      IOQueue-->>EventLoop: I/O callback
      EventLoop->>EventLoop: Drain Microtasks Queue (see microtasks diagram)
    else Can Node wait for I/O?
      alt setImmediate queue is empty AND no timers are ready
        Note over EventLoop: Node waits for I/O to complete
      else setImmediate queue is not empty OR timers are ready
        Note over EventLoop: Node skips waiting and exits Poll phase
      end
    end
    end

    Note over EventLoop: Poll phase ends

    Note over EventLoop: Check phase
    loop For each check callback
      EventLoop->>CheckQueue: Get next check callback
      CheckQueue-->>EventLoop: Check callback
      EventLoop->>EventLoop: Drain Microtasks Queue (see microtasks diagram)
    end

    Note over EventLoop: Close phase
    loop For each close callback
      EventLoop->>CloseQueue: Get next close callback
      CloseQueue-->>EventLoop: Close callback
      EventLoop->>EventLoop: Drain Microtasks Queue (see microtasks diagram)
    end
  end

  Note over EventLoop: No more callbacks to process, event loop exits
  EventLoop-->>MainThread: Exit process

```



#### Micro tasks queue

##### nextTick queue

```javascript
process.nextTick(() => {
    console.log("this is process.nextTick 1")
})
```

it will enqueue the callback to nextTick queue

##### promise queue

```javascript
Promise.resolve().then(() => {
    console.log("this is Promise.resolve 1")
})
```

##### Experiment

The, the code:

```javascript
process.nextTick(() => console.log("this is process.nextTick 1"));
process.nextTick(() => {
    console.log("this is process.nextTick 2");
    process.nextTick(() =>
        console.log("this is the inner next tick inside next tick")
    );
});
process.nextTick(() => console.log("this is process.nextTick 3"));

Promise.resolve().then(() => console.log("this is Promise.resolve 1"));
Promise.resolve().then(() => {
    console.log("this is Promise.resolve 2");
    process.nextTick(() =>
        console.log("this is the inner next tick inside Promise then block")
    );
    Promise.resolve().then(() => console.log("this is inner Promise"));
});
Promise.resolve().then(() => console.log("this is Promise.resolve 3"));

```

It would result:

```
this is process.nextTick 1
this is process.nextTick 2
this is process.nextTick 3
this is the inner next tick inside next tick
this is Promise.resolve 1
this is Promise.resolve 2
this is Promise.resolve 3
this is inner Promise
this is the inner next tick inside Promise then block
```

It is executed in this way:

```mermaid
sequenceDiagram
  participant Main
  participant nextTickQueue
  participant PromiseQueue

  Main->>nextTickQueue: schedule process.nextTick 1
  Main->>nextTickQueue: schedule process.nextTick 2
  Main->>nextTickQueue: schedule process.nextTick 3
  Main->>PromiseQueue: schedule Promise.resolve 1
  Main->>PromiseQueue: schedule Promise.resolve 2
  Main->>PromiseQueue: schedule Promise.resolve 3

  Note over nextTickQueue: Start draining nextTick queue

  nextTickQueue-->>Main: this is process.nextTick 1
  nextTickQueue-->>Main: this is process.nextTick 2
  nextTickQueue->>nextTickQueue: schedule inner next tick inside next tick

  Note over nextTickQueue: Note: nextTick 3 was already in the queue before<br>so it will be executed before the newly scheduled inner next tick

  nextTickQueue-->>Main: this is process.nextTick 3
  nextTickQueue-->>Main: this is the inner next tick inside next tick

  Note over nextTickQueue: nextTickQueue empty, moving to PromiseQueue

  Note over PromiseQueue: Start draining Promise queue

  PromiseQueue-->>Main: this is Promise.resolve 1
  PromiseQueue-->>Main: this is Promise.resolve 2
  PromiseQueue->>nextTickQueue: schedule inner next tick inside Promise then block
  PromiseQueue-->>PromiseQueue: schedule inner Promise
  PromiseQueue-->>Main: this is Promise.resolve 3
  PromiseQueue-->>Main: this is inner Promise

  Note over PromiseQueue: PromiseQueue empty, checking nextTickQueue again before next phase

  Note over nextTickQueue: Drain newly added nextTick

  nextTickQueue-->>Main: this is the inner next tick inside Promise then block
  Note over nextTickQueue: Both nextTickQueue and PromiseQueue are now empty, moving to the next event loop phase
```

#### Timer Queue

It is called "queue", but it is heap, because involves time

```javascript
setTimeout(() => console.log("this is setTimeout"), 0)
```

##### Experiment 1

```javascript
setTimeout(() => {
  console.log('timer 1');
  process.nextTick(() => console.log('microtask inside timer 1'))
});

setTimeout(() => {
  console.log('timer 2');
}, 0);
```

results in:

```
timer 1
microtask inside timer 1
timer 2
```

##### Experiment 2

```javascript
setTimeout(() =>  console.log('timer 1'), 1000);
setTimeout(() =>  console.log('timer 2'), 500);
setTimeout(() =>  console.log('timer 3'), 0);
```

results in:

```
timer 3
timer 2
timer 1
```

#### I/O Queue

Most of the async methods from the built-in modules queue the callback function in the I/O queue

```javascript
fs.readFile(__filename, () => {
    console.log("this is readFile 1")
})
```

##### Experiment 3

The code

```javascript
const fs = require("fs");

setTimeout(() => console.log("this is setTimeout1"), 0);
fs.readFile(__filename, () => console.log("this is readFile1"))
```

Will result in:

```bash

$ node index.js 
this is readFile1
this is setTimeout1
$ node index.js 
this is readFile1
this is setTimeout1
$ node index.js 
this is readFile1
this is setTimeout1
$ node index.js 
this is setTimeout1
this is readFile1
```

When running `setTimeout` with delay `0ms` and an I/O async method, the order of execution can never be guaranteed.

* It is because even when you use 0 milliseconds, the JavaScript puts a least 1 milliseconds delay. And whether the event pass pass through queue time before or after it is pure fluke

If we put a loop that does nothing, but ensures that the event loop pass through timer queue after 1 millisecond, the order can be guaranteed

```javascript
const fs = require("fs");

setTimeout(() => console.log("this is setTimeout1"), 0);
fs.readFile(__filename, () => console.log("this is readFile1"))

for(let i = 0; i < 2e6; i++) {}
```

```bash
$ node index.js 
this is setTimeout1
this is readFile1
$ node index.js 
this is setTimeout1
this is readFile1
$ node index.js 
this is setTimeout1
this is readFile1
```

#### Check Queue

```javascript
setImmediate(() => console.log("this is setImmediate 1"))
```

##### Experiment 4

```javascript
const fs = require("fs");

fs.readFile(__filename, () => console.log("this is readFile1"))
setImmediate(() => console.log("this is setImmediate 1"))

for(let i = 0; i < 2e6; i++) {}
```

will result in

```bash
$ node index.js 
this is setImmediate 1
this is readFile1
```

The `this is setImmediate 1` was printed before `this is readFile1` because when the Poll phase ran, the `fs.readFile` I/O had not completed yet, so there were no ready I/O callbacks. Since the `setImmediate` was already queued, Node skipped waiting in the Poll phase and moved immediately to the Check phase to run `setImmediate 1`. The `readFile1` callback only ran later, once the I/O actually finished and the event loop returned to the Poll phase in a subsequent iteration.

```mermaid
sequenceDiagram
  participant MainThread
  participant EventLoop
  participant Libuv
  participant CheckQueue
  participant Threadpool

  Note over MainThread: Synchronous script execution
  MainThread->>Threadpool: offload fs.readFile
  MainThread->>CheckQueue: schedule setImmediate 1

  Note over Threadpool: fs.readFile runs asynchronously
  Threadpool-->>Libuv: Marks fs.readFile completion as ready
  Note over Libuv: Completion is ready internally, even while MainThread is blocking

  Note over MainThread: Long blocking for-loop runs to completion

  Note over EventLoop: Event loop iteration 1 begins

  EventLoop->>EventLoop: Drain Microtasks (none here)

  Note over EventLoop: Poll phase
  EventLoop->>Libuv: Checks for ready I/O events
  alt setImmediate is queued
    Note over EventLoop: Poll phase skips waiting for I/O readiness
    Note over EventLoop: Even though fs.readFile is ready internally, it isn't delivered yet
    EventLoop->>EventLoop: Moves immediately to Check phase
  end

  Note over EventLoop: Check phase
  EventLoop->>CheckQueue: Get setImmediate 1
  CheckQueue-->>EventLoop: setImmediate 1 callback
  EventLoop->>MainThread: console.log("this is setImmediate 1")
  EventLoop->>EventLoop: Drain Microtasks (none)

  Note over EventLoop: Event loop iteration 2 begins

  EventLoop->>EventLoop: Drain Microtasks (none here)

  Note over EventLoop: Poll phase
  EventLoop->>Libuv: Checks for ready I/O events
  alt fs.readFile completion now delivered
    Libuv-->>EventLoop: Delivers fs.readFile callback
    EventLoop->>MainThread: console.log("this is readFile1")
    EventLoop->>EventLoop: Drain Microtasks (none)
  end

```

#### Close Queue

```javascript
const fs = require("fs");

const readableStream = fs.createReadStream(__filename);
readableStream.close();

readableStream.on("close", () => {
  console.log("this is from readableStream close event callback");
});
```

