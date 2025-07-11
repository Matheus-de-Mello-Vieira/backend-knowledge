

# Modules

A module is an encapsulated and reusable chunk of code that has its own context
* In Node.js, each file is treated as a separate module
* There is three types of Modules:
    1. Local modules - Modules that we create in our application
    2. Built-in modules - Modules that Node.js ships with out of the box
    3. Third party modules - Modules written by other developers that we can use in our application

## Local Modules

Modules that we create in our application

There is two module system: CommonJS and ES Modules.

### CommonJS

CommonJS is a standard that states how a module should be structured and shared.

* Node.js adopted CommonJS when it started out, and it's what you will see in codebases.
* Each file is treated as a module
* Variable, functions, classes, etc. are not accessible to other files by default
* Explicity tell the module system which parts of you code should be exported via `module.exports` or `export`
* To import code into a file, use the `require()` function

Examples:

* on `./index.js`
    ```javascript
    require("./add.js")
    
    console.log("Hello from index.js")
    ```
* on `./add.js`
    ```javascript
    const add = (a, b) => {
        return a + b
    }
    
    const sum = add(1, 2)
    console.log(sum)
    ```

on terminal:
```bash
.$ node index.js
3
Hello from index.js
```

#### Exports

* on `./index.js`
    ```javascript
    add = require("./add.js")
    
    const sum = add(1, 2)
    console.log(sum)
    ```
* on `./add.js`
    ```javascript
    const add = (a, b) => {
        return a + b
    }
    
    module.exports = add;
    ```

on terminal:
```bash
.$ node index.js
3
```

#### Module Scope

Each loaded module in Node.js is wrapped with an IIFE that provides private scoping of code.
* IFFE stands for Immediately Invoked Function Expression
* IIFE allows you to repeat variable or function names without any conflits
* 
Wrap you module with an IIFE means do it:
```javascript
(function() {
	// Module code actually lives in here
})
```

Given:

* `./index.js`:

    ```javascript
    batman = require("./batman.js")
    batman = require("./superman.js")
    ```
* `./batman.js`:
    ```javascript
    const superHero = "Batman"
    console.log(superHero)
    ```
* `./superman.js`:
    ```javascript
    const superHero = "Superman"
    console.log(superHero)
    ```

On terminal:

```bash
.$ node index.js
Batman
Superman
```

The IIFE that wraps every module contains 5 parameters which are pretty important for the functioning of a module. 
* `exports`: An object for exporting values from the module. Anything assigned to `exports` can be imported by other modules.
* `require`: A function to import other modules. It takes a module identifier (path or package name) and returns its exports.
* `module`: An object representing the current module. It contains metadata like `module.exports`, which is the actual exported value.
* `__filename`: The absolute path to the current module file. Useful for resolving paths relative to the file itself.
* `__dirname`: The absolute path to the directory containing the current module file. Useful for constructing paths to other files in the same folder.


You can access them from the module, as you already did with `require`.

#### Module Caching

When you run `require`, the result is cached. If you call it again with the same parameter, it will return the same object.

Given:

* `./superhero.js`

  ```javascript
  class SuperHero {
      constructor(name) {
          this.name = name;
      }
  
      getName() {
          return this.name;
      }
  
      setName(name) {
          this.name = name;
      }
  }
  
  module.exports = new SuperHero("Batman");
  ```

* `./index.js`

  ```javascript
  const superHero = require("./superhero")
  console.log(superHero.getName())
  superHero.setName("Superman")
  console.log(superHero.getName())
  
  const newSuperHero = require("./superhero")
  console.log(newSuperHero.getName())
  ```

On terminal:

```bash
.$ node index.js
Batman
Superman
Superman
```

#### Import Export Patterns

##### First pattern

* `./add.js`
    ```javascript
    const add = (a, b) => {
        return a + b;
    }
    
    module.exports = add;
    ```
* `./index.js`
    ```javascript
	const add = require("./math")
	console.log(add(2,3))
    ```


##### Second pattern

* `./add.js`
    ```javascript
    module.exports = (a, b) => {
        return a + b;
    }
    ```
* `./index.js`
    ```javascript
    const add = require("./math")
    console.log(add(2,3))
    ```

##### Third Pattern
* `./add.js`
    ```javascript
    const add = (a, b) => {
        return a + b;
    };
    
    const subtract = (a, b) => {
        return a - b;
    };
    
    module.exports = {
        add, subtract
    };
    ```
    
    * The last part is same of:
        ```javascript
        module.exports = {
            add: add,
            subtract: subtract
        };
        ```

* `./index.js`

    ```javascript
    const math = require("./math")
    console.log(math.add(2,3))
    console.log(math.subtract(2,3))
    ```
    
    * The same of:
    
      ```javascript
      const { add, subtract } = require("./math")
      console.log(add(2,3))
      console.log(subtract(2,3))
      ```

##### Fourth pattern

* `./add.js`
  
    ```javascript
     module.exports.add = (a, b) => {
        return a + b;
    };
    
    module.exports.subtract = (a, b) => {
        return a - b;
    };
    ```
* `./index.js`

    ```javascript
    const math = require("./math")
    console.log(math.add(2,3))
    console.log(math.subtract(2,3))
    ```
    
    * The same of:
    
      ```javascript
      const { add, subtract } = require("./math")
      console.log(add(2,3))
      console.log(subtract(2,3))
      ```

##### Fifth pattern

It is the most recommended.

* You can't reassign `exports` directly (for example, using `exports = {}`); you can only add properties to it. This approach is safer than using the fully assignable `module.exports`. Initially, `module.exports` and `exports` refer to the same object, but if you assign a new value to `module.exports`, it breaks that link and `module.exports` will point to something else.

Example


* `./add.js`
  
    ```javascript
    exports.add = (a, b) => {
        return a + b;
    };
    
    exports.subtract = (a, b) => {
        return a - b;
    };
    ```
* `./index.js`

    ```javascript
    const math = require("./math")
    console.log(math.add(2,3))
    console.log(math.subtract(2,3))
    ```
    
    * The same of:
    
      ```javascript
      const { add, subtract } = require("./math")
      console.log(add(2,3))
      console.log(subtract(2,3))
      ```

### ES Modules

* Reason of existence:
  * At the time Node.Js was created, there was no built-in module system in JavaScript
  * Node.Js defaulted to CommonJS as its module system.
  * As of ES2015, JavaScript does have a standardized module system as part of the language itself.
  * That module system is called EcmaScript Modules or ES Modules or ESM for short.
* Node.Js 14 and above support ES Modules.
* Instead of `module.exports`, we use the `export` keyword
* The `export` can be default of named
* We import the exported variables or functions using the `import` keyword.
  * If it is default export, we can assign any name while importing: `import math from "./math-esm.mjs"`
  * If it is named export, the import name must be the same: `import { add, subtract } from  "./math-esm.mjs"`


#### First pattern

* `./math-esm.mjs`

  ```javascript
  const add = (a, b) => {
      return a + b;
  }
  
  export default add;
  ```

* `./index.mjs`

  ```javascript
  import add from "./math-esm.mjs"
  
  console.log(add(5, 3))
  ```

#### Second pattern
* `./math-esm.mjs`
  ```javascript
  export default (a, b) => {
      return a + b;
  }
  ```

* `./index.mjs`
  
  ```javascript
  import add from "./math-esm.mjs"
  
  console.log(add(5, 3))
  ```
  
#### Third Pattern
* `./math-esm.mjs`
    ```javascript
    const add = (a, b) => {
        return a + b;
    };
    
    const subtract = (a, b) => {
        return a - b;
    };
    
    export default {
        add, subtract
    };
    ```
    
    * The last part is same of:
        ```javascript
        export default {
            add: add,
            subtract: subtract
        };
        ```

* `./index.js`

    ```javascript
    import math from "./math-esm.mjs"
    console.log(math.add(2,3))
    console.log(math.subtract(2,3))
    ```
#### Forth Pattern
* `./math-esm.mjs`
    ```javascript
    export const add = (a, b) => {
        return a + b;
    };
    
    export const subtract = (a, b) => {
        return a - b;
    };
    ```
* `./index.js`

    ```javascript
    import * as math from "./math-esm.mjs"
    console.log(math.add(2,3))
    console.log(math.subtract(2,3))
    ```
    * The same of:
    
      ```javascript
      import { add, subtract } from  "./math-esm.mjs"
      console.log(add(2,3))
      console.log(subtract(2,3))
      ```

### Importing JSON

* JSON stands for JavaScript Object Notation
* A data interchange format commonly used with web severs.

Example:

* `./data.json`

  ```json
  {
      "name": "Bruce Wayne",
      "address": {
          "street": "Wayne Manor",
          "city": "Gotham"
      }
  }
  ```

* `./index.js`

  ```javascript
  const data = require("./data.json")
  
  console.log(data)
  console.log(data.name)
  ```

  * you can also use `const data = require("./data")`,  but JavaScript will first look for `data.js`, and if that’s not found, it will then look for `data.json`.

### Watch mode

It allows the node restart automatically when a file in changed, to do it, `node --watch index.js`.

## Built-in Modules

* Modules that Node.Js ships with
* Also referred to be core modules
* Import the module before you can use it
  * example: `require("node:path")`
    * the `node` is optional, but it brings advantages:
      * makes it perfectly clear that the import is a Node.Js built-in module.
      * makes the import identifier a valid absolute URL.
      * Avoid conflicts for future Node.JS built-in modules.

### Path Module

The Path module provides utilities for working with file and directory paths

* `path.basename(filepath: string)` will get the last part of directory

  * Given `./src/index.js`
      ```javascript
      const path = require("node:path")
  	
      console.log(path.basename(__filename))
      console.log(path.basename(__dirname))
      ```
  	it will print:
  	
  	```
  	index.js
  	src
  	```

* `path.extname(filepath: string)` get the extension of the file
* `path.parse(filepath: string)` will return a object with:
  * root
  * dir
  * base
  * ext
  * name 
* `path.format(file: object)` do the inverse of `path.parse`
  * path.format(path.parse(obj)) == 
* `path.isAbsolute(filepath: string)`
* `path.join(folderName1: string, folderName2: string, ..., folderNameN: string)` concat strings, with the system's directory separator between the parts.
  * it also normalizes the parts, so:
    * if some part have a separator, even of different OS, prepended or appended, it will won't influence that result.
      * `path.join("/folder1", "//folder2", "index.html")` results in `/folder1/folder2/index.html`
        * as you could noticed, it doesn't applies to the prepended separator of the first part
    * you can use relative search, for example:
      * `path.join("folder1", "folder2", "../index.html")` will result in `folder1/index.hml`
* `path.resolve(folderName1: string, folderName2: string, ..., folderNameN: string)` gets the absolute path of `path.join(folderName1, folderName2, ..., folderNameN)`
  * if you prepended the first part with `/`, the `path.resolve` and `path.join` does the same thing.

### Events Module

The events module allows us to work with events in Node.Js

* An event is an action or an occurrence that has happened in our application that we can respond to.
* Using the events module, we can dispatch our own custom events and respond to those custom events in a non-blocking manner.

Given `./index.js`

```javascript
const EventEmitter = require("node:events")

const emitter = new EventEmitter()

emitter.on("order-pizza", (size, topping) => {
    console.log(`Order received! Baking ${size} a pizza with ${topping}`)
})

emitter.on("order-pizza", (size) => {
    if (size === "large") {
        console.log("Serving complimentary drink")
    }
})

emitter.emit("order-pizza", "large", "mushroom")
```

Then, on the terminal:

```bash
.$ node index.js
Order received! Baking large a pizza with mushroom
Serving complimentary drink
```

#### Extending Events Module

Most of asynchronous built-in modules, like `fs`, `streams` and `http` extends event module.

* doing it you can reduce the coupling between your classes.

Example:

* `pizza-shop.js`

  ```javascript
  const EventEmitter = require("node:events")
  
  class PizzaShop extends EventEmitter{
      constructor () {
          super();
          this.orderNumber = 0;
      }
  
      order (size, topping) {
          this.orderNumber++;
          this.emit("order", size, topping)
      }
  
      displayOrderNumber() {
          console.log(`Current order number: ${this.orderNumber}`)
      }
  }
  
  module.exports = PizzaShop

* `drink-machine.js`
    ```javascript
    class DrinkMachine {
        serveDrink(size) {
            if(size == "large") {
                console.log("Serviing complimentary drink")
            }
        }
    }
    
    module.exports = DrinkMachine;
    ```

* `index.js`

  ```javascript
  const PizzaShop = require("./pizza-shop")
  const DrinkMachine = require("./drink-machine")
  
  const pizzaShop = new PizzaShop();
  const drinkMachine = new DrinkMachine();
  
  pizzaShop.on("order", (size, topping) => {
      console.log(`Order received! Baking ${size} a pizza with ${topping}`)
      drinkMachine.serveDrink(size)
  })
  
  pizzaShop.order("large", "mushrooms")
  pizzaShop.displayOrderNumber()
  ```

### fs Module

The file system (fs) module allows you to work with the file system on your computer

* read:

  * thread-blocking

    * `./file.txt`
      ```javascript
      Hello World
      ```

    * `index.js`

      ```javascript
      const fs = require("node:fs")
      
      const fileContents = fs.readFileSync("./file.txt", "utf-8")
      
      console.log(fileContents)
      ```
    
  * non-thread-blocking
  
    * `index.js`
  
      ```javascript
      const fs = require("node:fs")
      
      fs.readFile("./file.txt", "utf-8", (error, data) => {
          if (error) {
              console.log(error)
          } else {
              console.log(data)
          }
      })
      ```

* write
  * thread-blocking
    * `index.js`

      ```javascript
      const fs = require("node:fs")
      
      fs.writeFileSync("./greet.txt", "Hello world!")
      ```
  
  * non-thread-blocking
  
    * `index.js`
  
      ```javascript
      const fs = require("node:fs")
      
      fs.writeFile("./greet.txt", "Hello world!", (error) => {
          if (error) {
              console.log(error)
          }
      })
      ```
  

#### Streams

You can work with data in chunks instead of waiting for the entire data to be available.

```javascript
const fs = require("node:fs")

const readableStream = fs.createReadStream("./source.txt", { encoding: "utf-8" })
const writeableStream = fs.createWriteStream("./destination.txt")

readableStream.on("data", (chunk) => { 
    console.log(chunk)
    writeableStream.write(chunk)
})
```

* or, alternatively

  ```javascript
  readableStream.pipe(writeableStream)
  ```

It allows having multiple steps of streams, for example compression:

```javascript
const fs = require("node:fs")
const zlib = require("node:zlib")

const gzip = zlib.createGzip()

const readableStream = fs.createReadStream("./source.txt", { encoding: "utf-8" })
const writeableStream = fs.createWriteStream("./destination.txt.gz")

readableStream.pipe(gzip).pipe(writeableStream)
```



### Promise

A better way to handle asynchronous codes

* it slower that callback, but it is a lot more legible. 

Example:

* `.then`/`.catch`
  
    ```javascript
    const fs = require("node:fs/promises")
    
    fs.readFile("file.txt", "utf-8")
        .then(data => console.log(data))
        .catch((error) => console.log(error))
    ```
    
* `async` / `await`
    ```javascript
    const fs = require("node:fs/promises")
    
    async function readFile() {
        try {
            const data = await fs.readFile("file.txt", "utf-8")
            console.log(data)
        } catch (err) {
            console.log(err)
        }
    }
    
    readFile()
    ```

### HTTP

Basic example

* on `index.js`:
    ```javascript
    const http = require("node:http")
    
    const server = http.createServer((req, res) => {
        res.writeHead(200, {"Content-Type": "text/plain"})
        res.end("Hello World\n")
    })
    
    server.listen(3000, () => {
        console.log("Server running on port 3000")
    })
    ```

* on terminal:
    ```bash
    $ node index.js
    Server running on port 3000
    ```

* on another terminal
    ```bash
    $ curl http://localhost:3000
    Hello World
    ```

Beyond plain text, you can send:

* JSON

  * `index.html`
    
      ```javascript
      const server = http.createServer((req, res) => {
          const superHero = {
              firstName: "Bruce",
              lastName: "Wayne"
          }
          res.writeHead(200, {"Content-Type": "application/json"})
          res.end(JSON.stringify(superHero))
      })
      ```
  
* HTML
    * 1 Harded coded 
    
        * `index.js`
            ```javascript
            const server = http.createServer((req, res) => {
            	res.writeHead(200, {"Content-Type": "application/json"})
            r	es.end("<h1>Hello World</h1>")
            })
            ```
        
    * 2 From File
      
        * `index.html`
          
            ```html
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Node.JS Tutorial</title>
            </head>
            <body>
                <h1>From index.html</h1>
            </body>
            </html>
            ```
            
        * `index.js`
          
            ```javascript
            const server = http.createServer((req, res) => {
                res.writeHead(200, {"Content-Type": "text/html"})
                const html = fs.readFileSync("./index.html", "utf-8")
                res.end(html)
            })
            ```
            
            * Or, even better:
            
              ```javascript
              const server = http.createServer((req, res) => {
                  res.writeHead(200, {"Content-Type": "text/html"})
                  fs.createReadStream("./index.html", { encoding: "utf-8" }).pipe(res)
              })
              ```
    
    * 3 From Template
    
      * `index.html`
    
        ```html
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Node.JS Tutorial</title>
        </head>
        <body>
            <h1>From {{name}}, welcome to Node.JS</h1>
        </body>
        </html>
        ```
    
      * `index.js`
    
        ```javascript
        const server = http.createServer((req, res) => {
            res.writeHead(200, {"Content-Type": "text/html"})
            
            const name = "Matheus"
            let html = fs.readFileSync("./index.html", "utf-8")
            html = html.replace("{{name}}", name)
            res.end(html)
        })
        ```

#### Routing

Do it by:

* `req.url`: like `/api`
* `req.method`: like `GET`, `POST`, `PUT`, `DELETE`, etc

```javascript
const server = http.createServer((req, res) => {
    if (req.url == "/") {
        res.writeHead(200, { "Content-Type": "text/plain" })
        res.end("Home page")
    } else if (req.url === "/about") {
        res.writeHead(200, { "Content-Type": "text/plain" })
        res.end("About page")
    } else if (req.url === "/api") {
        res.writeHead(200, { "Content-Type": "application/json" })
        res.end(JSON.stringify({
            firstName: "Bruce",
            lastName: "Wayne"
        }))
    } else {
        res.writeHead(404)
        res.end("Page not found")
    }
})
```

