# Introduction

Express is a fast, unopnionated, minimalist web framework for Node.JS

* unopnionated means that it doesn't force anything into you, for example use a specific database.

## Basic Example

* `app.all()` matches *all* HTTP methods (GET, POST, PUT, DELETE, etc.) for the given path.
* `/{*splat}` — Catch-all route pattern in Express 5 that matches any path and captures it in `req.params.splat`.
  * The `*` means “match anything,” and `splat` is the name you choose for the parameter. You must give it a name inside the braces.
  * for Express 4, use `app.all("*", ...)`.

```javascript
const express = require('express')
const app = express()
const port = 3000

app.all('/{*splat}', (req, res) => {
  res.send('Hello World!')
})

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`)
})
```

## Basic Router

```javascript
const express = require('express')
const app = express()
const port = 3000
app.get('/', (req, res) => {
    res.send(`<h1>Welcome to the home GET page!</h1>`)
})

app.post('/', (req, res) => {
    res.send(`<h1>Welcome to the home POST page!</h1>`)
})

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`)
})
```

## Serving Static Files

* `app.use([path,] callback [, callback...])` Mounts the specified middleware function or functions at the specified path: the middleware function is executed when the base of the requested path matches path.

* `express.static(root, [options])`  This is a built-in middleware function in Express. It serves static files and is based on serve-static.

Giving:

* existing `public/node.png`

* `public/style.css`
  ```css
  body{
      text-align: center;
  }
  
  img{
      max-width: 200px;
  }
  ```
* `node.html`
  ```html  
  <!DOCTYPE html>
  <html>
  <head>
      <title></title>
      <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" />
      <link rel="stylesheet" href="./styles.css" />
  </head>
  <body>
      <div class="container">
          <h1>Node.js is a JavaScript runtime built on Chrome's V8 JavaScript engine.</h1>
          <img src="./node.png" />
      </div>
  </body>
  </html>
  ```
* `index.js`
  ```javascript
  const express = require('express')
  const path = require('path')
  const app = express()
  const port = 3000
  
  // 1️⃣ Static middleware: serve any file in the "public" folder
  // e.g. /style.css → ./public/style.css
  // This runs first, so static files have the highest priority.
  app.use(express.static("public"))
  
  // 2️⃣ Route for GET "/"
  // When the user goes to the home page ("/"), serve "node.html" from the project root
  app.get("/", (req, res) => {
      res.sendFile(path.join(__dirname, "/node.html"))
  })
  
  // 3️⃣ Catch-all route for anything else
  // This matches any method and any path not handled above
  // Returns a 404 Not Found response
  app.all('/{*splat}', (req, res) => {
    res.status(404).send('Not Found');
  })
  
  // Start the server on port 3000
  app.listen(port, () => {
    console.log(`Example app listening on port ${port}`)
  })
  ```
