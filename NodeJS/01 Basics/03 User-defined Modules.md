# Modules

A module is an encapsulated and reusable chunk of code that has its own context
* In Node.js, each file is treated as a separate module
* There is three types of Modules:
    1. Local modules - Modules that we create in our application
    2. Built-in modules - Modules that Node.js ships with out of the box
    3. Third party modules - Modules written by other developers that we can use in our application

## Local Modules

Modules that we create in our application

### CommonJS

CommonJS is a standard that states how a module should be structured and shared.
* Node.js adopted CommonJS when it started out, and it's what you will see in codebases.

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

* `add.js`
    ```javascript
    const add = (a, b) => {
        return a + b;
    }
    
    module.exports = add;
    ```
* `index.js`
    ```javascript
	const add = require("./math")
	console.log(add(2,3))
    ```


##### Second pattern

* `add.js`
    ```javascript
    module.exports = (a, b) => {
        return a + b;
    }
    ```
* `index.js`
    ```javascript
    const add = require("./math")
    console.log(add(2,3))
    ```

##### Third Pattern
* `add.js`
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

* `index.js`

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

* `add.js`
    ```javascript
     module.exports.add = (a, b) => {
        return a + b;
    };
    
    module.exports.subtract = (a, b) => {
        return a - b;
    };
    ```
* `index.js`

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


* `add.js`
    
    ```javascript
    exports.add = (a, b) => {
        return a + b;
    };
    
    exports.subtract = (a, b) => {
        return a - b;
    };
    ```
* `index.js`

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