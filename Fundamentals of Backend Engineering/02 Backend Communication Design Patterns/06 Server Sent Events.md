# Server Sent Events

One Request, a very very long response

* A response has start and end
* Client sends a request
* Servers sends logical events as part of response
* Server never writes the end of the response
* It is still a request but an unending response
* Client parses the streams data looking for this events
* Works with request/response (HTTP)

## Pros and Cons

* Pros
  * real time: because we have a open channel with client
  * compatible with request/response
* Cons 
  * client might no be able to handle (very similar to cos of the push model)
    * clients must be on-line
    * polling is preferred for light clients
  * HTTP/1.1 allows the client to send data to the server, opening a connection with it, over which only the server can send data to the client—never the other way around. In addition, web browsers normally limit the number of simultaneous open connections to 6. Bottom line, clients are capped to 6 streams of server data.

## Demo

server

```javascript
const app = require("express")();

app.get("/", (req, res) => res.send("hello!"));

app.get("/stream", (req, res) => {
    res.setHeader("Content-Type", "text/event-stream");
    send(res)
});

const port = process.env.PORT || 8888;

let i = 0;
function send(res) {
    // Each message to the client must start with "data: " and end with "\n\n" — this defines a complete SSE (Server-Sent Event) message.
    res.write("data: " + `hello from server ---- [${i++}]` + "\n\n");
    
    setTimeout(() => send(res), 1000);
}

app.listen(port)
console.log(`Listening on ${port}`)
```

client code

```javascript
let sse = new EventSource("http://localhost:8888/stream");
sse.onmessage = console.log
```

Most web browsers have natively `EventSource`.