# gRPC

* Built above HTTP/v2

## Why gRPC was invented?

* The problem with Client Libraries

  * Any communication protocol needs client library for the language of choice
    * SOAP library
    * HTTP Client Library

  * Hard to maintain and patch client libraries
    * HTTP/1.1, HTTP/2, new features, security etc.

* gPRC have one library for popular languages

* Message Format :Protocol buffers as format

## gRPC modes

* Unary RPC: request-response
* Server streaming RPC: 
  * example:
    * download large file
    * logging
* Client streaming RPC
  * example
    * upload large file
* Bidirectional streaming RCP

# Demos

## Unary RPC

**todo.proto**

```protobuf
syntax = "proto3";

package pack.todo;

service Todo {
  rpc CreateTodo(TodoItem) returns (TodoItem);
  rpc ReadTodos(NoParams) returns (TodoItems);
}

message NoParams {}

message TodoItem {
  int32 id = 1;
  string text = 2;
}

message TodoItems {
  repeated TodoItem items = 1;
}
```



**server.js**

```javascript
const grpc = require("grpc");
const protoLoader = require("@grpc/proto-loader")
const packageDef = protoLoader.loadSync("todo.proto", {})

const grpcObject = grpc.loadPackageDefinition(packageDef)
const todoPackage = grpcObject.pack.todo;

const server = new grpc.Server()
server.bind("0.0.0.0:40000", grpc.ServerCredentials.createInsecure()) // HTTP2 is secure by default, the grpcs allows you bypass it
server.addService(todoPackage.Todo.service, {
    "CreateTodo": createTodo,
    "ReadTodos": readTodo
})

server.start()

const todos = []
function createTodo(call, callback) {
    const todoItem = {
        "id": todos.length + 1,
        "text": call.request.text
    }
    todos.push(todoItem)

    // the null is the size, when null it is calculated
    callback(null, todoItem)
}

function readTodo(call, callback) {
    callback(null, {"items": todos})
}
```

**client.js**

```javascript
const grpc = require("grpc");
const protoLoader = require("@grpc/proto-loader")
const packageDef = protoLoader.loadSync("todo.proto", {})

const grpcObject = grpc.loadPackageDefinition(packageDef)
const todoPackage = grpcObject.pack.todo;


const client = new todoPackage.Todo("localhost:40000", grpc.credentials.createInsecure())

input = process.argv[2]

client.createTodo({
    "id": -1,
    "text": input
}, (err, response) => {
    console.log("Received from server" + JSON.stringify(response))
})


client.readTodos({}, (err, response) => {
    if (response.items)
        response.items.map(item => console.log(`${item.id}: ${item.text}`));
})
```

So we can run the server and:

```bash
=> node client.js "Make the beds"
Received from server{"id":1,"text":"Make the beds"}

=> node client.js "Do the dishes"
1: Make the beds
Received from server{"id":2,"text":"Do the dishes"}

=> node client.js "Wipe kitchen counters and table"
1: Make the beds
2: Do the dishes
Received from server{"id":3,"text":"Wipe kitchen counters and table"}

=> node client.js "Take out the trash"
1: Make the beds
2: Do the dishes
3: Wipe kitchen counters and table
Received from server{"id":4,"text":"Take out the trash"}
```



But it is a bad idea: we a taking the whole array and shove down the client throat.

## Server streaming RPC

on `todo.proto`

```protobuf
service Todo {
  rpc CreateTodo(TodoItem) returns (TodoItem);
  rpc ReadTodos(NoParams) returns (TodoItems);
  rpc ReadTodosStream(NoParams) returns (stream TodoItem);
}
```

on `server.js`

```javascript
server.addService(todoPackage.Todo.service, {
    "CreateTodo": createTodo,
    "ReadTodos": readTodo,
    "ReadTodosStream": readTodosStream
})

...

function readTodosStream(call, callback) {
    todos.forEach(t => call.write(t))
    call.end()
}
```

on `client.js`

```javascript
const call = client.readTodosStream();
call.on("data", item => console.log(`${item.id}: ${item.text}`))
call.on("end", e => console.log("server done!"))
```

## Pros and Cons

* Pros
  * Fast and Compact
    * it is a binary protocol on top of HTTP/v2
  * One client library
    * as it have many possibilities (unary or stream), it can replace any protocol.
  * Progress Feedback (upload)
  * Cancel Request (h2)
  * H2/Protobuf 
* Cons
  * Schema
  * Thick Client
  * Proxies
  * Error handling
  * No native browser support
    * you can create a reverse proxy to convert browner-compatible protocols to RPC
  * Timeouts (pub/sub)
    * as it is H2, and it multiplex multiple streams - that can be many types - together, it's like put all eggs on the same basket.