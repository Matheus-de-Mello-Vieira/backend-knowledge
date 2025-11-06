# Push

## Request/response isn't always ideal

Client wants real time notification from backend

* Imagine implementing:
  * Youtube's notification system using request-response: billions of clients polling at the same time for new notifications. This traffic demand verge the unmanageable.
  * Chat system using request-response

## What is Push

* Client connects to a server
* Server sends data to the client
* Client doesn't have to request anything
* Protocol must be bidirectional
  * You can argue that the push can be unidirectional, but in practice we use TCP that is bidirectional

The RabbitMQ uses the push model: The client starts a connection with RabbitMQ, which will push the messages to the client. The Kafka used this same approach too, until they changed to the long polling model due to risk of overrunning the client.

## Pros and Cos

* Pros
  * Real Time: The server doesn't wait for the client to act because the server pushes the data to the client right away.
* Cons
  * Clients must be online
  * Clients might not be able to handle
    * the client can be overran with pushed messages and crash. So, polling is preferred for light clients 
  *  Requires a bidirectional protocol

## Demo

Server:

```javascript
const http = require("http");
const WebSocketServer = require("websocket").server;
let connections = [];

const httpServer = http.createServer();

const websocket = new WebSocketServer({ "httpServer": httpServer });

httpServer.listen(8080, () => console.log("My server is listening on port 8080"));

websocket.on("request", request => {
    const connection = request.accept(null, request.origin);
    connection.on("message", message => {
        connections.forEach(c => c.send(`User${connection.socket.remotePort} says: ${message.utf8Data}`));
    });
    connections.push(connection);
    
    connections.forEach(c => c.send(`User${connection.socket.remotePort} just connected.`));
});
```