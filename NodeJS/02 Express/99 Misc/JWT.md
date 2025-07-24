# JWT

## Problem

Create an Express app that uses middleware to check for an existing req.body.jwtToken on every route.

## Solution

I installed https://www.npmjs.com/package/jsonwebtoken



```javascript
var jwt = require('jsonwebtoken');

app.use(async (req, res, next) => {
    const token = req.body?.jwtToken;

    if (!token) {
        res.status(400).send("Error, jwtToken doesn't exist");
        return;
    }

    try {
        var decoded = jwt.verify(req.body.jwtToken, 'secret');
    } catch(err) {
       res.status(400).send("Error, jwtToken is invalid");
       return
    }

    req.user = decoded;
    next()
})
```

