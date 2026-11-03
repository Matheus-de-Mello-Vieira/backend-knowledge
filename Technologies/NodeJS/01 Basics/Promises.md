# Promises

A Promise represents an eventual completion value or failure reason. It separates the result of an operation from the code that consumes it; creating a Promise does not make synchronous work non-blocking.

## Lifecycle and resolution

A Promise has one of three states:

- **Pending:** No fulfillment value or rejection reason is available yet.
- **Fulfilled:** The operation has a fulfillment value.
- **Rejected:** The operation has a rejection reason.

**Settled** means fulfilled or rejected. Settlement is permanent: a settled Promise does not return to pending or change its outcome.

`new Promise((resolve, reject) => { ... })` runs its **executor** synchronously. The executor connects the operation to its result: call `resolve(value)` for success or `reject(reason)` for failure. A synchronous exception escaping the executor rejects the Promise; an exception thrown later in an asynchronous callback must be handled in that callback.

**Resolution is not the same as fulfillment.** Resolving with another Promise adopts its eventual outcome, so a resolved Promise can still be pending. Resolution also assimilates **thenables**: objects with a callable `then` method. Once the first resolving call commits the outcome, later `resolve` or `reject` calls do not replace it, even while an adopted Promise remains pending.

- **`Promise.resolve(value)`:** Produces a Promise adopting a value, Promise, or thenable; an ordinary value produces fulfillment.
- **`Promise.reject(reason)`:** Produces a rejected Promise with that reason, without adopting it.

### Executor and handler timing

Construction runs the executor immediately, but fulfillment and rejection handlers run asynchronously, after the current synchronous execution finishes. Promise reactions use [microtask queues](../01%20Basics/04%20Internals.md#Microtask%20Queues), not synchronous calls from `resolve()`.

```javascript
const promise = new Promise((resolve) => {
  console.log('Executor');
  resolve(42);
});

promise.then((value) => console.log(value));
console.log('Synchronous');
```

The output is:

```text
Executor
Synchronous
42
```

The executor has already fulfilled the Promise before `then()` registers its handler. Registration still schedules the handler asynchronously; it does not invoke it inline.

## Chaining and error propagation

`then()`, `catch()`, and `finally()` each return a new Promise. The original Promise's outcome selects a handler; the handler's behavior determines the next Promise's outcome. Returning the chain lets a caller await its completion and handle its failure.

### `then()` and `catch()`

`promise.then(onFulfilled, onRejected)` registers handlers for the original Promise's fulfillment value or rejection reason. A missing or non-callable handler passes the corresponding outcome through unchanged.

For the selected handler:

- **Return an ordinary value:** Fulfill the next Promise with that value. Returning nothing fulfills it with `undefined`.
- **Return a Promise or thenable:** Resolve the next Promise to that result, waiting for its eventual outcome.
- **Throw:** Reject the next Promise with the thrown error.

```javascript
Promise.resolve(10)
  .then((value) => value * 2)
  .then((value) => console.log(value)); // 20
```

`catch(onRejected)` is shorthand for `then(undefined, onRejected)`. A rejection handler that returns a value recovers the chain into fulfillment; throwing or returning a rejected Promise keeps it rejected.

The second argument to `then()` handles rejection of the Promise on which it is registered, not exceptions thrown by its sibling fulfillment handler. Those exceptions reject the newly returned Promise and require a downstream handler:

```javascript
Promise.resolve('start')
  .then(
    (result) => {
      console.log('First then:', result);
      throw new Error('Boom inside onFulfilled');
    },
    (error) => {
      console.error('Caught in onRejected:', error.message); // Not called
    }
  )
  .catch((error) => {
    console.error('Caught in catch:', error.message);
  });
```

```text
First then: start
Caught in catch: Boom inside onFulfilled
```

Return asynchronous work from a handler when it belongs to the chain. Starting an operation without returning its Promise disconnects its completion and rejection from downstream handlers.

### `finally()`

`finally(onFinally)` runs cleanup after fulfillment or rejection without receiving the value or reason. Unlike `then(fn, fn)`, it normally preserves the original outcome.

- **Normal return:** Preserve the original value or rejection reason; an ordinary return value is ignored.
- **Returned Promise or thenable:** Wait for cleanup. Fulfilled cleanup preserves the original outcome.
- **Thrown error or rejected cleanup:** Reject the next Promise with the cleanup failure, replacing the original outcome.

```javascript
const preserved = Promise.resolve(10).finally(() => 99); // Fulfills with 10
const replaced = Promise.resolve(10).then(() => 99, () => 99); // Fulfills with 99
```

For a Promise-returning application function `checkMail()`, logging and cleanup form one chain:

```javascript
checkMail()
  .then((mail) => {
    console.log(mail);
  })
  .catch((error) => {
    console.error(error);
  })
  .finally(() => {
    console.log('Experiment completed');
  });
```

Here, `catch()` consumes the mail failure if logging returns normally. `finally()` then runs for either path; its own failure would still reject the returned chain.

## Async/await

An `async` function returns a Promise. Calling it executes its body synchronously until an `await` suspends it or the function completes. Returning a value fulfills its Promise, returning a Promise adopts its outcome, and an uncaught exception rejects it.

`await` resumes with the fulfillment value or throws the rejection reason at the await expression. Resumption is asynchronous even for an already-fulfilled Promise or an ordinary value. Use `try/catch` around awaited work to handle its rejection.

The mail flow can also be written as an async function:

```javascript
async function inspectMail() {
  try {
    const mail = await checkMail();
    console.log(mail);
  } catch (error) {
    console.error(error);
  } finally {
    console.log('Experiment completed');
  }
}
```

The caller must still await, return, or handle `inspectMail()`'s Promise. `async` syntax does not remove failure ownership.

### Sequential and concurrent starts

Await sequentially when later work depends on an earlier result. For independent operations, start both before waiting so their waiting time overlaps. Assuming `fetchData()` starts work when called:

```javascript
async function sequential() {
  const first = await fetchData(1);
  const second = await fetchData(2); // Starts after the first completes
  return [first, second];
}

async function concurrent() {
  const first = fetchData(1);
  const second = fetchData(2); // Starts without waiting for the first
  return await Promise.all([first, second]);
}
```

Concurrency comes from starting the operations, not from `Promise.all()` itself. This does not make CPU-bound JavaScript execute in parallel.

> [!warning] Async callbacks in `forEach()`
> `forEach()` ignores callback return values, so even awaiting `forEach()` does not wait for the async work. Assuming `processItem(item)` returns a Promise:
>
> **Wrong — the callbacks' Promises are discarded:**
>
> ```javascript
> await items.forEach(async (item) => {
>   await processItem(item);
> });
> ```
>
> **Sequential — wait for each item before starting the next:**
>
> ```javascript
> for (const item of items) {
>   await processItem(item);
> }
> ```
>
> **Concurrent — observe all completions and failures:**
>
> ```javascript
> await Promise.all(items.map((item) => processItem(item)));
> ```

## Concurrent Promise composition

The four combinators accept an iterable containing Promises, thenables, or ordinary values and return a new Promise. Ordinary values participate as fulfilled inputs.

| Method                 | Fulfillment                                                        | Rejection                                                                |
| ---------------------- | ------------------------------------------------------------------ | ------------------------------------------------------------------------ |
| `Promise.all()`        | Array of values after every input fulfills, in input order         | First observed input rejection                                           |
| `Promise.allSettled()` | Array of outcome records after every input settles, in input order | Input rejection is recorded rather than rejecting the aggregate          |
| `Promise.any()`        | First observed fulfillment value                                   | `AggregateError` if every input rejects; its `errors` follow input order |
| `Promise.race()`       | Value if the first observed settlement is fulfillment              | Reason if the first observed settlement is rejection                     |

`allSettled()` records are `{ status: 'fulfilled', value }` or `{ status: 'rejected', reason }`. Result order for `all()` and `allSettled()` is unrelated to completion order.

For an empty iterable, `all()` and `allSettled()` fulfill with `[]`, `any()` rejects with an `AggregateError`, and `race()` remains pending.

None of these methods cancels underlying operations. An early rejection from `all()` or a winner from `race()` leaves the remaining work running. Passing thousands of already-started operations also imposes no concurrency limit or backpressure.

## Cancellation and timeouts

Promises have no universal cancellation method. Cancellation belongs to the underlying operation: APIs that accept an `AbortSignal` observe its abort request according to their own contract. `AbortController.abort()` requests abortion explicitly; `AbortSignal.timeout()` creates a signal that aborts after a delay.

In Node.js versions supporting `AbortSignal.timeout()` and the signal option of `node:fs/promises.readFile()`, a file read can receive a timeout signal. In an ES module:

```javascript
import { readFile } from 'node:fs/promises';

try {
  const data = await readFile('file.txt', {
    encoding: 'utf8',
    signal: AbortSignal.timeout(5000),
  });
  console.log(data);
} catch (error) {
  console.error('Read failed or was aborted:', error);
}
```

The signal requests abortion of the read rather than merely rejecting a separate timer Promise. For this API, abortion stops internal buffering, not individual operating-system requests already in progress. A `Promise.race()` against a timeout alone would stop waiting for the result without requesting that cleanup.

## Converting callback-based APIs

Prefer native Promise APIs when available, such as `node:fs/promises`. Wrap callbacks only when adapting an API that does not already return a Promise. The snippets below use ES-module imports; their top-level `await` requires an ES-module context.

### Error-first callbacks

A conventional Node.js callback receives `(error, result)`. It reports completion through the callback rather than the function's return value:

```javascript
import { readFile } from 'node:fs';

readFile('file.txt', 'utf8', (error, data) => {
  if (error) {
    console.error(error);
    return;
  }
  console.log(data);
});
```

### Manual wrapping

Forward the callback's error to `reject()` and its result to `resolve()`. Returning after rejection prevents the success path from running:

```javascript
function readFileAsync(path, encoding) {
  return new Promise((resolve, reject) => {
    readFile(path, encoding, (error, data) => {
      if (error) {
        reject(error);
        return;
      }
      resolve(data);
    });
  });
}

const data = await readFileAsync('file.txt', 'utf8');
```

### `util.promisify()`

For a function whose final argument is a standard error-first callback, `promisify()` returns a Promise-returning function. Invoke that new function with the operation's arguments; awaiting the function object does not run the operation.

```javascript
import { promisify } from 'node:util';

const readFilePromise = promisify(readFile);
const data = await readFilePromise('file.txt', 'utf8');
```

Methods that depend on `this` need their receiver preserved, for example through binding. Nonstandard callback signatures require an explicit adapter or custom promisification rather than assuming the error-first contract.

## Fire-and-forget and unhandled rejections

Fire-and-forget starts an operation without awaiting its completion in the current flow. It does not remove responsibility for failure handling.

The `void` operator evaluates an expression and returns `undefined`, discarding its value:

```javascript
void 123; // undefined
void doSomethingAsync(); // Starts the call and discards its returned Promise
```

`void` does not attach a rejection handler, cancel work, or guarantee completion. Promise-aware lint rules may accept it as an intentional discard depending on configuration; JavaScript and TypeScript do not make the operation safe merely because it uses `void`.

Attach a handler that owns background failure:

```javascript
void doSomethingAsync().catch((error) => {
  console.error('Background operation failed:', error);
});
```

The final handler must itself complete without throwing or returning a rejected Promise; otherwise the Promise returned by `catch()` becomes an unobserved rejection.

Node.js reports rejections without timely handlers. Process behavior depends on the Node.js version, `--unhandled-rejections` mode, and installed process-level handlers. Under the documented default `throw` mode, an unhandled rejection is raised as an uncaught exception if no `unhandledRejection` hook is installed; absent exception handling, that terminates the process. Process-level hooks are not a substitute for handling failures where the operation is owned.

## References

- [ECMAScript Promise semantics](https://tc39.es/ecma262/#sec-promise-objects)
- [Node.js Promise-based file reads](https://nodejs.org/api/fs.html#fspromisesreadfilepath-options)
- [Node.js AbortSignal](https://nodejs.org/api/globals.html#class-abortsignal)
- [Node.js util.promisify](https://nodejs.org/api/util.html#utilpromisifyoriginal)
- [Node.js unhandled rejection modes](https://nodejs.org/api/cli.html#--unhandled-rejectionsmode)
