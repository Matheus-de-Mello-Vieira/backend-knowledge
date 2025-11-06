

# Middleware

Middleware function is any function that has access to the `req`, `res` and `next`

* A middleware needs to call `next` to go to the next middleware, otherwise it is the end of the request.
* The route handler is just the last middleware
* `res.locals` is a shared variable available throughout the middlewares. 

Example:

1) Request come in
2) We need to validate the user, sometimes
3) We need to store some things in the DB
4) If there is data form the user we need to parse it and store it

```javascript
// This is a middleware function named validateUser.
// Middleware in Express is any function with (req, res, next) signature.
// It can modify the request or response objects, or run code before passing control to the next middleware/route.
function validateUser(req, res, next) {
  res.locals.validated = true   // Store a flag in res.locals (available to later handlers)
  console.log("Validated Ran!") // Log that this middleware ran

  next()  // Call next() to pass control to the next middleware or route handler
}

// Register the middleware globally with app.use.
// This means validateUser will run on *every* incoming request, for *every* route.
app.use(validateUser)

app.get("/", (req, res, next) => {
  res.send("<h1>Main Page</h1>")
  console.log(res.locals.validated)  // Access the value set by the validateUser middleware
})
```

Or, alternatively, if you want to use the middleware only on `GET /`:

```javascript
app.get("/", validateUser)

app.get("/", (req, res, next) => {
  res.send("<h1>Main Page</h1>")
  console.log(res.locals.validated)
})
```

We can specify which routes use the middleware:

```javascript
app.use("/admin", validateUser)

app.get("/", (req, res, next) => {
  res.send("<h1>Main Page</h1>")
  console.log(res.locals.validated) // undefined
})

app.get("/admin", (req, res, next) => {
  res.send("<h1>Admin Page</h1>")
  console.log(res.locals.validated) // true
})
```

## Built-in Middlewares

* `express.json` it parses incoming requests with JSON payloads

  * you can set the attribute `type` with a string, array of string or function, that by default is `application/json`

    * You can configure your Express server to accept JSON payloads even when clients send them with the `Content-Type` header set to `text/plain`—a common scenario with certain services like AWS SNS.
        ```javascript
        app.use('/json', express.json({ type: ['application/json', 'text/plain'] }));
        
        app.post('/json', (req, res) => {
          const contentType = req.get('Content-Type');
          console.log('---- New Request ----');
          console.log('Content-Type:', contentType);
          console.log('Parsed Body:', req.body);
        
          res.json({message: 'JSON received successfully!'});
        });
        ```

* `express.static` It serves static files and is based on serve-static.

  * Check out [Serving Static Files](../01 Introduction/01 Introduction.md#serving-static-files) for details on serving static content in Express.

* `express.urlencoded` It parses incoming request with `urlencoded` payloads

  * you can set the attribute `type` with a string, array of string or function, that by default is  `application/x-www-form-urlencoded`
  
  * it will parse the body that comes as "Form Data"
  
  * Example
  
    * In `./index.html`
  
      ```html
      <!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <title>POST Form Example</title>
      </head>
      <body>
        <h1>Submit Form Data</h1>
        <form action="/results" method="POST">
          <label for="name">Name:</label>
          <input type="text" id="name" name="name" required><br><br>
      
          <label for="age">Age:</label>
          <input type="number" id="age" name="age" required><br><br>
      
          <label for="city">City:</label>
          <input type="text" id="city" name="city" required><br><br>
      
          <button type="submit">Submit</button>
        </form>
      </body>
      </html>
      ```
  
    * In `./index.js`
  
      ```javascript
      const express = require('express')
      const path = require('path')
      const app = express()
      const port = 3000
      
      app.use(express.urlencoded({ extended: false }))
      
      app.get("/", (req, res) => {
        console.log(path.join(__dirname, "/index.html"))
        res.sendFile(path.join(__dirname, "/index.html"))
      })
      
      app.post('/results', (req, res) => {
        console.log(req.body);
        res.send("Test")
      });
      
      app.listen(port, () => {
        console.log(`Example app listening on port ${port}`)
      })
      ```



## Third-parties Middlewares

### Helmet

* [Helmet](https://helmetjs.github.io/) can help protect your app from some well-known web vulnerabilities by setting HTTP headers appropriately.
* It is recommended officially by Express https://expressjs.com/en/advanced/best-practice-security.html#use-helmet
* on their [README.md](https://github.com/helmetjs/helmet): It's not a silver bullet, but it can help
* it brings a lot of advantages with no disadvantage, so there is no reason to don't use helmet.

To use their full protection:

```bash
npm install helmet --save
```

So:

```javascript
const helmet = require("helmet")

...

app.use(helmet())
```

