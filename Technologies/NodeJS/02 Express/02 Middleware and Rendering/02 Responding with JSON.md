# Respoding with JSON

You need to do something like

```javascript
app.get("/", (req, res) => {
  content = {
    "name": "Matheus"
  }

  res.writeHead(200, { "Content-Type": "application/json" })
  res.end(JSON.stringify(content))
})
```

or, alternatively 

```javascript
app.get("/", (req, res) => {
  content = {
    "name": "Matheus"
  }

  res.set('Content-Type', "application/json")
  res.send(JSON.stringify(content))
})
```

* `send` and `end` works pretty the same, but only the last one allow close the connection without send anything.

or, alternatively 

```javascript
app.get("/", (req, res) => {
  content = {
    "name": "Matheus"
  }

  res.json(content)
})
```

