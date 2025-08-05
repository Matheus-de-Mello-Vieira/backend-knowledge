## Basic Authentication

```
npm install passport passport-http --save
```

In your `app.js` file, set up Passport as follows:

```javascript
passport.use(new BasicStrategy(
  function(userid, password, done) { // check credentials
    User.findOne({ username: userid }, function (err, user) {
      if (err) { return done(err); }
      if (!user) { return done(null, false); }
      if (!user.verifyPassword(password)) { return done(null, false); }
      return done(null, user);
    });
  }
));
```

So on your private routes:

```javascript
app.get('/private', 
  passport.authenticate('basic', { session: false }),
  function(req, res) {
    res.json(req.user);
  });
```

* As it is basic authentication,  the `session` option can be set to `false`, because the client will send the credentials on each request.
