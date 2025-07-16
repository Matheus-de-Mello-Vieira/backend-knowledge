# Rendering

The frontend can be:

* client-side rendering: frontend be only static files
  * So the javascript code inside it can call the backend, who will response jsons.
* server-side rendering: backend generate the HTML, CSS and JS dynamically. 

Here we will see the options that Node.JS offers for the second.

The process it:

1) The creates the HTTP API, with all middlewares
2) We define a view engine
   * EJS
   * Mustache
   * HandleBars
   * Pug (formerly Jade)
3) We can `res.render` from the router handler
   * We pass two things:
     * the file we want to use
     * the data we want to send to that file
   * express uses the engine to compile that two things together into final HTML, CSS and JS.

## EJS

```bash
npm install ejs --save
```

Basic Example

* an `views/index.ejs`

  ```ejs
  <h1>Rendering</h1>
  ```

  * The folder `views` is the default, but you can set through `app.set("view", "absolut-path")` or `app.set("view", ["folder 1", "folder 2"])`

* an `index.js`

    ```javascript
    app.set("view engine", "ejs")
    
    app.get("/", (req, res, next) => {
      res.render("index")
    })
    ```

We learn at `https://ejs.co/`

Example:

* 
    ```ejs
    <ul>
        <% for(let i = 0; i < 10; i++){ %>
          <li>Test</li>
        <% } %>
    </ul>
    ```
    
    will generate
    ```html
    <ul>
        <li>Test</li>
        <li>Test</li>
        <li>Test</li>
        <li>Test</li>
        <li>Test</li>
        <li>Test</li>
        <li>Test</li>
        <li>Test</li>
        <li>Test</li>
        <li>Test</li>
    </ul>
    ```
    
* 
    ```ejs
    <ul>
      <% for(let i = 0; i < 10; i++){ %>
        <% if (i % 2 === 0){ txt = "even" } else { txt = "odd" } %>
        <li><%= i %> - <%= txt %></li>
      <% } %>
    </ul>
    ```
    
    will generate
    ```html
    <li>0 - even</li>
    <li>1 - odd</li>
    <li>2 - even</li>
    <li>3 - odd</li>
    <li>4 - even</li>
    <li>5 - odd</li>
    <li>6 - even</li>
    <li>7 - odd</li>
    <li>8 - even</li>
    <li>9 - odd</li>
    ```
    
* We can pass values to the ejs
  
  * in `index.js`
  
      ```java
      app.get("/", (req, res, next) => {
        res.render("index", {
          msg: "Success!"
        })
      })
      ```
  
      * It will append `msg` into `res.locals`
  
  * `views/index.ejs`
  
      ```ejs
      <h1><%= msg %></h1>
      ```
  
      * or, alternatively
  
          ```ejs
          <h1><%= locals.msg %></h1>
          ```
  
  * Will generate
  
      ```html
      <h1>Success!</h1>
      ```

* We can access `res.locals`
  * in `index.js`
  
      ```java
      function validateUser(req, res, next) {
        res.locals.validated = true;
        next()
      }
      
      app.use(validateUser)
      
      app.get("/", (req, res, next) => {
        res.render("index", {
          msg: "Success!"
        })
      })
      ```
  
      * It will append `msg` into `res.locals`
  
  * `views/index.ejs`
  
      ```ejs
      <h1><%= msg %></h1>
      <h2><%= validated %></h1>
      ```
  
      * or, alternatively
  
          ```ejs
          <h1><%= locals.msg %></h1>
          <h2><%= locals.validated %></h1>
          ```
  
  * Will generate
  
      ```html
      <h1>Success!</h1>
      <h2>true</h2>
      ```



We can include html code from variable using

```ejs
<%- variableWithHTML >
```

We can comment inside ejs using

```
<%# This is a comment %>
```

We can use multiple `.ejs` files to generate the html files

Example

* `views/head.ejs`

  ```ejs
  <!DOCTYPE html>
  <html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>My Website</title>
  
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" />
    <link rel="stylesheet" href="/styles.css" />
  </head>
  ```

* `views/navbar.ejs`

  ```ejs
  <nav class="navbar navbar-expand-lg navbar-light bg-light">
  <div class="container-fluid">
      <a class="navbar-brand" href="#">WebSiteName</a>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
      <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
      <ul class="navbar-nav">
          <li class="nav-item active">
          <a class="nav-link" href="#">Home</a>
          </li>
          <li class="nav-item">
          <a class="nav-link" href="#">Page 1</a>
          </li>
          <li class="nav-item">
          <a class="nav-link" href="#">Page 2</a>
          </li>
          <li class="nav-item">
          <a class="nav-link" href="#">Page 3</a>
          </li>
      </ul>
      </div>
  </div>
  </nav>
  ```

* `views/index.ejs`

  ```ejs
  <%- include('head') %>
  
  <body>
    <%- include('navbar') %>
    <h1>Home Page!</h1>
  </body>
  ```
* `views/about.ejs`

  ```ejs
  <%- include('head') %>
  
  <body>
    <%- include('navbar') %>
    <h1>About Page!</h1>
  </body>
  ```
  
* `views/index.js`

  ```javascript
  app.set("view engine", "ejs")
  
  app.get("/", (req, res, next) => {
    res.render("index")
  })
  
  app.get("/about", (req, res, next) => {
    res.render("index")
  })
  ```
