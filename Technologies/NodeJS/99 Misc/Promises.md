# Promises

The Promise object represents the eventual completion (or failure) of an asynchronous operation and its resulting value.

## Promise concurrency

The Promise class offers four static methods to facilitate async task concurrency

* `Promise.all()` Fulfills when **all** of the promises fulfill; rejects when **any** of the promises rejects.
* `Promise.allSettled()` Fulfills when all promises settle, regardless of whether they were **fulfilled** or **rejected**.
* `Promise.any()` Fulfills when **any** of the promises fulfills; rejects when **all** of the promises reject.
* `Promise.race()` Settles when **any** of the promises settles. In other words, fulfills when any of the promises fulfills; rejects when any of the promises rejects.

All these methods take an iterable of promises (thenables, to be exact) and return a new promise.

## Instance methods

The `Promise` have three instance methods, every one returns another promise, so you can chain them.

* `then()`: takes up to two arguments: callback functions for the fulfilled (`onFulfilled`) and rejected cases (`onRejected`) of the Promise. It stores the callbacks within the promise it is called on

  * `somePromise.then(onFulfilled, onRejected)` is equivalent of

    ```javascript
    (async () => {
        try {
            await somePromise;
        } catch (err) {
            onRejected(err);
            return; // very important
        }
    
        onFulfilled();
    })();
    ```

    

  * The second argument is optional

  * The second argument won't cover errors inside the `then`

    * given

      ```javascript
      Promise.resolve("start")
        .then(
          (result) => {
            console.log("First then:", result);
            throw new Error("Boom inside onFulfilled");
          },
          (err) => {
            console.error("Caught in onRejected:", err.message); // This won't run
          }
        )
        .catch((error) => {
          console.error("Caught in catch:", error.message);
        });
      ```

    * the expected result is

      ```txt
      First then: start
      Caught in catch: Boom inside onFulfilled
      ```

      

* `catch()`: schedules a function to be called when the promise is rejected. 

  * it is a shortcut for `.then(undefined, onRejected)`

* `finally()`: schedules a function to be called when the promise is settled (either fulfilled or rejected).

  * This lets you avoid duplicating code in both the promise's `then()` and `catch()` handlers.
  * it is a shortcut for `.then()` when you pass the same value to `onFulfilled` and `onRejected`

```javascript
checkMail()
  .then((mail) => {
    console.log(mail);
  })
  .catch((err) => {
    console.error(err);
  })
  .finally(() => {
    console.log("Experiment completed");
  });
```

* it is equivalent to:

  ```javascript
  (async () => {
      try {
          const mail = await checkMail();
          console.log(mail);
      } catch (err) {
          console.error(err);
      } finally {
          console.log("Experiment completed");
      }
  })();
  ```

## Convert callbacks into promises

Many Node.js APIs (especially older ones) follow the Node.js-style callback pattern:

```javascript
callbackBasedFunction(arg1, arg2, (err, result) => {
  if (err) return console.error(err)
  console.log(result)
})
```

But this isn't compatible with async/await, which expects functions that return Promises. To bridge that gap, we can wrap callback-based functions in a Promise manually:

```javascript
const result = await new Promise((resolve, reject) => {
  callbackBasedFunction(args, (err, data) => {
    if (err) return reject(err)
    resolve(data)
  })
})
```

If the function uses the standard Node-style callback `(err, result) => {}`, you can use Node’s built-in `util.promisify()` to convert it into a Promise-returning function.

```javascript
const { promisify } = require('util')

const result = await promisify(callbackBasedFunction)
```

### Example

* `fs.readFile`

  * Before (callback-style):

    ```javascript
    const fs = require('fs')
    
    fs.readFile('file.txt', 'utf8', (err, data) => {
      if (err) throw err
      console.log(data)
    })
    ```

  * After (manual promise-wrapping)

    ```javascript
    const fs = require('fs')
    
    async function readFileAsync(path, encoding) {
      return await new Promise((resolve, reject) => {
        fs.readFile(path, encoding, (err, data) => {
          if (err) return reject(err)
          resolve(data)
        })
      })
    }
    
    const data = await readFileAsync('file.txt', 'utf8')
    console.log(data)
    ```

  * After (Using `util.promisify`)

    ``` javascript
    const fs = require('fs')
    const { promisify } = require('util')
    
    const readFile = promisify(fs.readFile)
    const data = await readFile('file.txt', 'utf8')
    ```

  * **Note:** In modern Node.js (v10+), many core modules like the file system have built-in Promise-based APIs. For example, instead of manually converting `fs.readFile`, you can simply use

    ```javascript
    const fs = require('fs/promises')
    const data = await fs.readFile('file.txt', 'utf8')
    ```


## `fire-and-forgot` a promise

### the `void` operator

In JavaScript, the `void` operator evaluates an expression and **returns `undefined`**, regardless of what the expression’s actual value is.

For example:

```javascript
void 123; // => undefined
void (function() { return 42 })(); // => undefined
```

So the core idea is:

> "`void x` means: run `x`, ignore its result, and yield `undefined`."

### Using `void` to “fire-and-forget” a Promise

When dealing with asynchronous code, sometimes you want to start a Promise but not await it — i.e., fire and forget.

However, many linters (like ESLint) and TypeScript will warn you if you write code like:

```javascript
doSomethingAsync(); // Warning: 'Promise' returned by async function is not handled
```

That’s where `void` comes in handy.

You can write:

```javascript
void doSomethingAsync();
```

- Executes `doSomethingAsync()` (which returns a Promise)
- Explicitly discards the Promise result
- Suppresses linter warnings about unhandled Promises
- Makes it clear to readers: *“Yes, this async call is intentionally not awaited.”*
