# Convert callbacks into promises

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

## Example

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

    