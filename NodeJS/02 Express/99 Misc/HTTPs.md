# HTTPs

## Problem

You cannot run your Express server behind a proxy, so it MUST be running on https. How do you accomplish this? Outline the steps.

## Solution

According with https://nodejs.org/api/https.html

Given 

```bash
openssl req -x509 -newkey rsa:2048 -nodes -sha256 -subj '/CN=localhost' \
  -keyout private-key.pem -out certificate.pem 
```

So

```javascript
const express = require("express");
const https = require("node:https");
const fs = require("node:fs");

const app = express();

const options = {
  key: fs.readFileSync("private-key.pem"),
  cert: fs.readFileSync("certificate.pem"),
};

const secureExpressServer = https.createServer(options, app);

app.get("/test", (req, res) => {
  res.send("test page");
});

secureExpressServer.listen(3000, () => {
  console.log("HTTPS server running on https://localhost:3000");
});

```

So

```bash
curl -k https://localhost:8000/
```

### Redirect HTTP to HTTPS

```javascript
http.createServer((req, res) => {
  const host = req.headers['host']?.replace(/:\d+$/, ":3000"); // preserve hostname, set correct HTTPS port
  res.writeHead(301, { Location: `https://${host}${req.url}` });
  res.end();
}).listen(80, () => {
  console.log("HTTP server redirecting all traffic to HTTPS");
});
```

