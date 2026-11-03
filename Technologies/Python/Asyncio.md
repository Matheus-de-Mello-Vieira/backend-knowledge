# Asyncio

`asyncio` coordinates concurrent work through coroutines, Tasks, and an event loop. It is useful when operations spend time waiting through asynchronous APIs: while one Task waits, the loop runs other ready work. It does not make ordinary Python code nonblocking or automatically run CPU work in parallel.

## Coroutines, Tasks, and Futures

The three awaitable types have different roles:

- **Coroutine:** Calling an `async def` coroutine function creates an object describing suspended execution. The function body has not started. Await it or schedule it; merely calling it does not run the operation.
- **Task:** A scheduled coroutine with a result, exception, and cancellation state. `asyncio.create_task(coro)` gives a coroutine an independently scheduled lifetime on the running loop.
- **Future:** A completion object holding a pending result, eventual value, exception, or cancellation. Low-level adapters use Futures to connect callbacks to `await`; application code normally consumes them through higher-level APIs rather than constructing them.

`await operation` retrieves its result or raises its exception. Directly awaiting a coroutine drives it within the current Task; it does not create another Task. A coroutine object cannot be awaited again after completion, whereas multiple awaiters can observe the same Task's outcome.

[Coroutine suspension](Python%20Internals.md#Coroutines%20and%20asyncio%20scheduling) happens only when the awaited work actually yields control. An already-completed awaitable can return immediately. Consequently, `await` is not a guaranteed scheduling handoff; `await asyncio.sleep(0)` deliberately yields to other work.

> [!note] Task start timing
> With the default deferred scheduling behavior, creating a Task schedules its execution rather than running its body inline. Eager task factories or eager-start configuration change this: the coroutine starts during Task construction and runs until it blocks or completes. Do not depend on deferred start when configuring eager execution.

## Starting and awaiting work

### The application entry point

`asyncio.run(main())` creates and manages an event loop, runs the entry coroutine, returns its result, and performs shutdown, including asynchronous-generator and default-executor cleanup. Use it at the synchronous application boundary, not inside another coroutine.

This complete program creates `main`'s coroutine first; `run` then drives it. The awaited sleep suspends the Task without blocking the loop thread.

```python
import asyncio


async def main():
    await asyncio.sleep(0.01)
    return "finished"


if __name__ == "__main__":
    print(asyncio.run(main()))
```

- **Existing running loop:** `asyncio.run()` cannot run while another event loop is running in the same thread. In a framework or notebook that already drives a loop, use its async entry mechanism and await the coroutine instead.
- **Repeated top-level calls:** `asyncio.Runner` (Python 3.11+) provides a context manager for several top-level async calls using the same loop and execution context.
- **Resource lifetime:** Close application resources while async cleanup can still run. Runner shutdown is not a replacement for explicitly owning child work and resources.

### Sequential work and independent Tasks

Await sequentially when one operation depends on the previous result. Independent waits overlap only after the work has been scheduled independently.

The following fragments form one program. `fetch` represents an operation that waits through an async API:

```python
import asyncio


async def fetch(item):
    await asyncio.sleep(0.01)
    return item * 10
```

Two direct awaits execute one after the other. In the concurrent branch, both Tasks exist before either result is awaited; awaiting `first` does not prevent `second` from progressing.

```python
async def main():
    sequential = [await fetch(1), await fetch(2)]

    first = asyncio.create_task(fetch(1))
    second = asyncio.create_task(fetch(2))
    concurrent = [await first, await second]
    return sequential, concurrent


if __name__ == "__main__":
    print(asyncio.run(main()))
```

This demonstrates successful execution, not coordinated failure cleanup. If awaiting `first` raises, the next await is skipped; a Task group gives the pair a shared failure and cleanup scope.

## Coordinating concurrent operations

Choose a coordinator by its result and lifetime semantics, not simply by whether it accepts several operations. Each example below is an alternative `main` fragment using the `asyncio` import and `fetch` function above; run it with `asyncio.run(main())` at the synchronous entry point.

### Collecting results with `asyncio.gather`

`asyncio.gather(*aws)` schedules coroutine arguments as Tasks and returns results in input order, regardless of completion order. Await the aggregate when the caller needs the results together:

```python
async def main():
    results = await asyncio.gather(fetch(1), fetch(2))
    return results  # [10, 20], in input order
```

- **Failure propagation:** By default, the first raised exception propagates immediately, but other children are not automatically cancelled. After `gather` has propagated an exception and become done, cancelling it does not cancel surviving children.
- **Exception collection:** `return_exceptions=True` waits for all inputs and places exceptions alongside successful values in the result list. Callers must inspect these outcomes.
- **Cancellation:** Cancelling an unfinished `gather` cancels its unfinished children. A cancelled child does not itself cancel the aggregate; it is treated as raising `CancelledError`.

### Structured lifetime with `asyncio.TaskGroup`

`asyncio.TaskGroup` (Python 3.11+) owns related child Tasks within an `async with` block and waits for them before exiting. Independent operations that must finish together belong in one Task group. Results are available after normal context exit because all children have completed successfully:

```python
async def main():
    async with asyncio.TaskGroup() as group:
        first = group.create_task(fetch(1))
        second = group.create_task(fetch(2))

    return first.result(), second.result()
```

A child's non-cancellation failure cancels remaining children. Exit waits for sibling cancellation and cleanup rather than leaving a sibling running unnoticed; failures are then raised together in an `ExceptionGroup` or `BaseExceptionGroup`.

- **Failure triggers:** A child's cancellation alone is not a sibling-failure trigger. An exception in the block also participates in the group's failure handling.
- **Special exceptions:** `KeyboardInterrupt` and `SystemExit` are re-raised specially after the other children are cancelled and awaited.
- **Group handling:** Use `except* SomeError` when handling matching members of an exception group; ordinary `except SomeError` does not unpack the group.

### Inspecting completion with `asyncio.wait`

`asyncio.wait(tasks, ...)` returns `(done, pending)` sets without retrieving results. `return_when` selects all completion, first completion, or first exception. Pass Tasks or Futures, not bare coroutine objects; bare coroutines are rejected since Python 3.11.

Wait for the first completion, retrieve completed results explicitly, and then await the remaining work. The `finally` block retains responsibility for cancelling and awaiting unfinished Tasks if result retrieval fails or the caller is cancelled:

```python
async def main():
    tasks = {asyncio.create_task(fetch(item)) for item in (1, 2)}
    try:
        done, pending = await asyncio.wait(
            tasks, return_when=asyncio.FIRST_COMPLETED
        )
        for task in done:
            print(task.result())
        for task in pending:
            print(await task)
    finally:
        for task in tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
```

A timeout returns pending work without cancelling it; the caller still owns it. Inspect completed Tasks with `result()` or await them to observe errors.

### Processing completion order with `asyncio.as_completed`

`asyncio.as_completed(aws)` exposes outcomes in completion order. With plain iteration, each yielded item is a wrapper coroutine, not an original Task; await it to retrieve its result or exception.

Process each result as it becomes available. This fragment retains the Tasks so cleanup also awaits them if processing fails or the caller is cancelled:

```python
async def main():
    tasks = [asyncio.create_task(fetch(item)) for item in (1, 2)]
    try:
        for completed in asyncio.as_completed(tasks):
            print(await completed)
    finally:
        for task in tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
```

- **Completion and cleanup:** Normal exhaustion after awaiting every yielded wrapper means all original Tasks are complete. An exception from an `await`, cancellation, or an early `break`/`return` can leave Tasks unfinished; this fragment's `finally` cancels pending Tasks and awaits them, rather than guaranteeing successful completion.
- **Identity correlation:** Since Python 3.13, asynchronous iteration yields the originally supplied Tasks/Futures, allowing identity-based correlation; coroutine inputs receive implicit Tasks.
- **Timeout:** A timeout raises `TimeoutError`; it does not cancel remaining operations.

### Bounding active work and backlog

Scheduling concurrent operations does not impose a resource limit. Choose the control according to what must remain bounded:

- **Active operations:** A semaphore limits entry to a protected region, such as calls to `fetch`.
- **Pending backlog:** A bounded queue with fixed workers limits queued items as well as active consumers, without creating a Task per item.

#### Semaphore for a finite batch

For a finite batch that fits in memory, create one Task per item but acquire a semaphore before entering the resource-consuming operation. In this example, at most three Tasks execute `fetch` concurrently; the others await a permit. `async with` releases the permit when the protected operation exits, including through an exception or cancellation.

```python
async def main():
    semaphore = asyncio.Semaphore(3)

    async def limited_fetch(item):
        async with semaphore:
            return await fetch(item)

    async with asyncio.TaskGroup() as group:
        tasks = [
            group.create_task(limited_fetch(item))
            for item in range(10)
        ]

    return [task.result() for task in tasks]
```

The Task group owns failure and cleanup; the semaphore owns admission to `fetch`. Creating a Task for every item still allocates all those Tasks, including Tasks waiting for permits. This pattern does not bound Task count or the batch's retained inputs and results.

#### Bounded queue with fixed workers

For a larger stream, keep a fixed worker set and feed it through `asyncio.Queue(maxsize=...)`. With a positive capacity, `await queue.put(item)` waits while the queue is full: the producer stops advancing until a worker removes an item. This is producer backpressure. `maxsize=0`, the default, creates an unbounded queue.

The following fragments form one alternative `main`. The queue holds at most six waiting items, and three workers each process one item at a time. `stop` is a private sentinel that tells a worker to exit; `queue.get()` waits when no item is available.

```python
async def main():
    worker_count = 3
    queue = asyncio.Queue(maxsize=6)
    stop = object()

    async def worker():
        while True:
            item = await queue.get()
            if item is stop:
                return
            result = await fetch(item)
            print(result)
```

Start the workers before producing items, then enqueue one sentinel per worker after the input ends. Queue order places the sentinels behind the submitted items. Task-group exit waits for the workers, including any operations still in progress when another worker receives a sentinel.

```python
    async with asyncio.TaskGroup() as group:
        for _ in range(worker_count):
            group.create_task(worker())

        for item in range(100):
            await queue.put(item)

        for _ in range(worker_count):
            await queue.put(stop)
```

- **Failure ownership:** Production runs inside the same Task-group scope as the workers. A worker's non-cancellation failure cancels its siblings and interrupts the producer, including a producer waiting in `put`; group exit awaits cleanup and raises the failure rather than leaving the producer waiting on a full queue with no consumers.
- **Bounded state:** There are three worker Tasks, at most three items being processed, and at most six queued items. The producer also holds the current item while waiting to enqueue it. These are item-count bounds, not a total-memory bound: item sizes, source prefetching, and retained results require separate control. The example consumes results immediately instead of collecting them all.
- **Completion:** Sentinels terminate workers, and the Task group waits for their exit. This pattern does not use `queue.join()` or `task_done()`; `join()` tracks item accounting when paired with `task_done()`, not worker termination.

## Cancellation and cleanup

`task.cancel()` requests cancellation. At a cancellation opportunity, the Task receives `asyncio.CancelledError`; the request is not an immediate interrupt, rollback, or proof that an external operation stopped. A coroutine that never yields prevents other Tasks on that loop from running, including work that would request its cancellation.

Cancellation follows an observable sequence:

1. An owner requests cancellation, directly or through a timeout/group.
2. The coroutine receives `CancelledError` when execution permits delivery.
3. Cleanup executes in `finally` or context-manager exit methods.
4. Letting `CancelledError` escape makes the Task terminally cancelled; its awaiters observe cancellation.

`CancelledError` derives from `BaseException`, so `except Exception` does not catch it. If explicitly caught for cleanup, re-raise it. Swallowing cancellation interferes with timeout and Task-group protocols.

The following complete program starts a worker, allows it to reach a wait, then cancels and awaits it. The `finally` block runs before the owner finishes observing cancellation.

```python
import asyncio


async def worker():
    try:
        await asyncio.sleep(60)
    finally:
        print("worker cleanup")


async def main():
    task = asyncio.create_task(worker())
    await asyncio.sleep(0)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("worker cancelled")


if __name__ == "__main__":
    asyncio.run(main())
```

Awaiting a Task normally connects cancellation of the awaiter to the awaited Task. `asyncio.shield(task)` prevents cancellation through that await from cancelling the inner Task, but the caller still receives `CancelledError`. Retain the inner Task and arrange to observe its eventual outcome; shielding neither detaches ownership nor protects against direct cancellation of the inner Task.

### Timeouts

Timeouts are cancellation policies, not hard execution-time limits:

- **`asyncio.timeout(seconds)` (Python 3.11+):** An async context manager that cancels the current Task on expiry and translates the resulting cancellation into `TimeoutError` outside the context. It scopes several awaits under one deadline.
- **`asyncio.wait_for(aw, timeout)`:** Awaits one operation, scheduling a coroutine argument as a Task. On timeout it cancels that operation and waits for cancellation to finish, so total elapsed time can exceed the timeout. An exception raised during cancellation propagates.
- **`asyncio.wait(..., timeout=seconds)`:** Stops waiting and returns pending Tasks without cancelling them. Use it when the caller must decide separately what happens to unfinished work.

Catch the timeout outside its context so that translation has already occurred:

```python
async def fetch_with_timeout(item):
    try:
        async with asyncio.timeout(1):
            return await fetch(item)
    except TimeoutError:
        return None
```

The example uses `fetch` defined earlier. Side effects performed before timeout remain performed; cancellation does not undo a request already accepted by a remote service.

## Background work and failure ownership

`asyncio.create_task()` returns immediately with a Task handle; it does not establish who will retain, supervise, or shut down that work. The loop keeps only weak references to Tasks, so keep a strong application reference for background work whose lifetime matters.

An owner has three responsibilities:

- **Retention:** Keep Tasks in a field, collection, or Task group until their lifetime has been accounted for.
- **Observation:** Await completion or explicitly retrieve/log failures. An unobserved Task exception is reported by asyncio rather than raised in an unrelated caller.
- **Shutdown:** Stop accepting work, cancel remaining Tasks when appropriate, and await them so cleanup finishes. Loop teardown is not a durable job system.

A completion callback that removes a Task from a set handles retention cleanup only. It does not, by itself, retrieve the Task's exception. Prefer Task groups when child work fits a lexical scope; use an explicit supervisor for longer-lived work.

## Integrating synchronous code

An ordinary blocking call inside `async def` still runs on the loop thread. `time.sleep`, synchronous network clients, and expensive computations stall other Tasks until the call returns. Async syntax changes neither the function being called nor its execution location.

- **`asyncio.to_thread(func, *args, **kwargs)` (Python 3.9+):** Returns a coroutine that runs a synchronous callable in a worker thread when driven; it propagates the current `contextvars` context. Await it to retrieve the value or exception.
- **`loop.run_in_executor(executor, func, *args)`:** Submits immediately and returns an asyncio Future. Use `asyncio.get_running_loop()` inside async code; `None` selects the default executor, while an explicit executor provides a separate execution policy.
- **CPU-bound work:** In conventional GIL-enabled CPython, threads do not provide parallel execution of ordinary Python CPU work. Process-based execution is an alternative; native extensions that release the GIL and free-threaded builds have different constraints.

### File I/O through a worker thread

[Ordinary file operations](Python%20Internals.md#Files%2C%20native%20asynchronous%20I%2FO%2C%20and%20data%20transfer) are synchronous: calling `open`, `read`, or `write` inside a coroutine still blocks the loop thread. To keep the loop responsive, put the complete file operation in a synchronous helper and await that helper through `asyncio.to_thread`. This is thread-offloaded synchronous I/O, not kernel-native asynchronous file I/O.

> [!note] Async file libraries
> Standard `asyncio` has no built-in native asynchronous API for regular files; the pattern below uses thread offloading. Third-party libraries expose awaitable file operations with different backends:
>
> - **[aiofiles](https://github.com/tinche/aiofiles):** Delegates ordinary file operations to an executor's worker threads.
> - **[aiofile](https://github.com/mosquito/aiofile) / `caio`:** Uses `caio` for low-level `AIOFile` reads and writes, with Linux io_uring/libaio or thread backends. Other operations still use executor paths; an async method does not imply a native backend for every operation.
>
> Native-backend support depends on the platform, kernel, filesystem, file type, and requested operation.

The helper owns opening, reading, and closing the file; the coroutine receives the completed result rather than an open file handle. This complete program requires a UTF-8 `example.txt` in the working directory:

```python
import asyncio
from pathlib import Path


def read_text(path):
    return Path(path).read_text(encoding="utf-8")


async def main():
    text = await asyncio.to_thread(read_text, "example.txt")
    print(text)


if __name__ == "__main__":
    asyncio.run(main())
```

`Path.read_text` opens and closes the file inside the worker. Awaiting `to_thread` suspends the coroutine while the helper runs, leaving the loop available for other Tasks; normal completion returns the text, and a helper exception propagates through the await. Apply the same boundary to writes or multi-step file processing: keep all operations that share the open file inside one synchronous helper, rather than returning a file whose caller might close it while the worker is still using it.

Two lifetime constraints matter when using this pattern in a service:

- **Cancellation and shutdown:** Cancelling the await does not forcibly stop an already-running thread callable. Its file remains owned by the helper until the helper actually finishes and closes it. Design side effects, resource lifetime, and shutdown around that completion, not merely around the awaiting Task's cancellation.
- **Admission and backlog:** Bound submissions as well as worker counts; offloading an unlimited backlog only moves the queue. The bounded-queue and fixed-worker pattern above supplies producer backpressure. When adapting it to threads, preserve each occupied worker slot until its thread call actually completes, or otherwise track unfinished thread calls and count them against the admission limit. Cancelling an async worker does not stop its running thread operation; replacing that worker before completion can exceed the intended bound. Likewise, a semaphore released when an await is cancelled does not prove that the underlying file operation has finished, so it is not by itself a strict bound on still-running file operations.

## Synchronization and asynchronous protocols

Tasks share the loop thread but still interleave across suspension points. A read–await–write sequence is not atomic merely because it runs in one thread. Asyncio primitives coordinate Tasks; they are not thread-safe substitutes for thread synchronization.

- **`asyncio.Lock`:** Protects a shared invariant across awaits. `async with lock` acquires it and releases it on exit, including exceptional exit.
- **`asyncio.Semaphore`:** Limits how many Tasks enter a region simultaneously. Use `async with semaphore` around the operation consuming the limited resource.
- **`asyncio.Event`:** Broadcasts a flag. `wait()` blocks until the flag is set; `set()` wakes waiters and leaves the flag set until `clear()`. It does not count individual notifications.
- **`asyncio.Queue`:** Transfers items between producers and consumers. With positive `maxsize`, `await put()` waits when full; `await get()` waits when empty. Call `task_done()` once for each retrieved item when processing is accounted for; `join()` waits for that accounting, not for worker Tasks to exit.

The language's asynchronous protocols compose with these APIs:

- **`async with`:** Awaits asynchronous context entry and exit. The context manager implements `__aenter__` and `__aexit__`; the protocol permits async acquisition and cleanup but does not itself make the enclosed body concurrent.
- **`async for`:** Consumes an asynchronous iterator. `__aiter__` returns the iterator; awaiting `__anext__` produces an item or raises `StopAsyncIteration`. Iteration is sequential unless its body explicitly schedules independent work.

## Comparison with Node.js Promises

[JavaScript async execution](../NodeJS/01%20Basics/Promises.md#Async%2Fawait) and Python coroutines both support result-oriented `await` syntax, but their starting and scheduling rules differ.

| Dimension | Python asyncio | JavaScript Promises |
| --- | --- | --- |
| Calling an async function | Creates an unstarted coroutine | Starts the body synchronously, returning a Promise |
| Scheduling independent work | Create Tasks or use a coordinator that schedules coroutines | Operations commonly start when their producing functions are called |
| Awaiting an already-completed result | Can continue without yielding | Resumption is asynchronous |
| Completion object | Future records an outcome; Task additionally drives a coroutine | Promise represents eventual settlement, not a coroutine driver |
| Aggregate failure | `gather` propagates a failure without cancelling siblings; Task groups cancel and await siblings | `Promise.all` rejects without cancelling underlying operations |
| Cancellation | Task cancellation and timeout protocols deliver `CancelledError` cooperatively | Promise settlement itself has no cancellation operation; cancellation belongs to the underlying API |

`gather(return_exceptions=True)` resembles `Promise.allSettled` in waiting for all outcomes, but returns values/exceptions rather than status records. `wait(FIRST_COMPLETED)` is not a direct `Promise.race` replacement: it returns Task sets, leaves pending work owned by the caller, and does not itself retrieve the winning result.

## References

- [Python: Coroutines and Tasks](https://docs.python.org/3/library/asyncio-task.html)
- [Python: Runners](https://docs.python.org/3/library/asyncio-runner.html)
- [Python: Synchronization primitives](https://docs.python.org/3/library/asyncio-sync.html)
- [Python: Queues](https://docs.python.org/3/library/asyncio-queue.html)
- [Python: Asynchronous iterators and context managers](https://docs.python.org/3/reference/datamodel.html#asynchronous-iterators)
