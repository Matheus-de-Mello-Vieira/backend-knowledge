# Res, Req and Router

## Query string parameter 

To get values embedded on the url as `fail` in `/login?msg=fail`

```javascript
res.locals.msg
```

## Params

To get values embedded on the url as `1` in `/story/1`, we need set a wildcard

* in a route, anything prefixed with `:` is a wildcard
* a willcard is a slot that have to be filled with values

```javascript
app.get("/story/:storyId", (req, res, next) => {
  res.send(`<h1>Story ${req.params.storyId}</h1>`)
})
```

You can use multiple on the same URL, as `2` and `linkURL` on `/story/2/linkURL`

```javascript
app.get("/story/:storyId/:link", (req, res, next) => {
  res.send(`<h1>Story ${req.params.storyId} - ${req.params.link}</h1>`)
})
```

### Param middleware

You can add a middleware based on the param value.

```javascript
app.param("id", (req, res, next, id) => {
  console.log("Params called:", id);
  next()
})

app.get("/story/:id", (req, res, next) => {
  res.send(`<h1>Story ${req.params.storyId} - ${req.params.link}</h1>`)
})
```

it will run the callback on `app.param` first, and then `app.get` one.

We can do interesting things with it, for example:

```javascript
 app.param('user_id', function(req, res, next, id){
   User.find(id, function(err, user){
     if (err) {
       next(err);
     } else if (user) {
       req.user = user;
       next();
     } else {
       next(new Error('failed to load user'));
     }
   });
 });
```

will make a *:user_id* parameter automatically load a user's information from the database without any additional code,

## Redirect

To Make the client browser to redirect the page 

```javascript
res.redirect("/welcome")
```

* it will set the response status code to 302, and set `location` response header to `/welcome`

## Send files

Use `res.sendFile` to make the client browser only show the file:

```javascript
res.sendFile(path.join(__dirname, "userStatements/BankStatementChequing.png"))
```

* The browser is likely to show the image because the response header `Content-Type=image/png` and no `Content-Disposition` header.

Use `res.download` to make the client browser download the file, the second parameter is the filename.

```javascript
res.download(
    path.join(__dirname, "userStatements/BankStatementChequing.png"),
    "Statement.png"
)
```

* The browser is likely to download the image because the response headers `Content-Type=image/png` and `Content-Disposition=attachment; filename="Statement.png"`.

* the `res.download` uses `res.sendFile` under the hood. So alternatively we could:

  * ``` javascript
    res.sendFile(path.join(__dirname, "userStatements/BankStatementChequing.png"))
    res.set("Content-Disposition", "attachment; filename=\"Statement.png\"")
    ```
  * ```javascript
    res.sendFile(path.join(__dirname, "userStatements/BankStatementChequing.png"))
    res.attachment("Statement.png") // Set Content-Disposition header to attachment with optional filename.
    ```


## Cookies

Info stored by the client, who send it to server on each request

To use cookies, we need use the package `cookie-parser`

```bash
npm install cookie-parser --save
```

Use their middleware

```javascript
const cookieParser = require("cookie-parser")
...
app.use(cookieParser())
```

On a middleware

* to set a cookie:

    ```javascript
    res.cookie("username", username)
    ```
* to get a cookie:

    ```javascript
    req.cookies.username
    ```
* to delete a cookie:

    ```javascript
    res.clearCookie('username')
    ```

## Router

Router creates a branch of the API, like a url path prefix being a independent express

* on `index.js`
  ```javascript
  const subRouter = require("./subRouter")
  
  app.use("/sub-router", subRouter)
  ```
* on `routerApp.js`
  ```javascript
  const express = require('express');
  let router = express.Router();
  
  router.get("/", (req, res, next) => {
      res.json({
          "msg": "Router works!"
      })
  })
  
  module.exports = router;
  ```

We also have `route.all`, `route.post`, `router.delete`, `router.use`, and go on.

