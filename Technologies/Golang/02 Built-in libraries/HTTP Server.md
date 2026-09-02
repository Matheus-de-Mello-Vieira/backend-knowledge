# HTTP Server

## Creating the router

Inside your `main()` function, you start by creating a **router**, called a *ServeMux* in Go:

```go
mux := http.NewServeMux()
```

This router decides which function should handle which URL path.

## Defining a simple route

A **route** is a URL path paired with a function that runs when a request hits it.

Example:

```go
mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "text/plain; charset=utf-8")
    w.WriteHeader(http.StatusOK)
    w.Write([]byte("hello from net/http"))
})
```

- `HandleFunc` connects the path `/` to the given handler function.
- Every handler function receives:
  - `w` — used to **write the response** back to the client.
  - `r` — the **incoming request**, containing details like headers and URL.
- The handler sets the response header (to say it’s plain text), sends a 200 OK status, and writes `"hello from net/http"` as the response body.

## Returning JSON data

You can send JSON responses by using Go’s built-in JSON encoder:

```go
mux.HandleFunc("/api/hello", func(w http.ResponseWriter, r *http.Request) {
    type resp struct {
        Message string    `json:"message"`
        When    time.Time `json:"when"`
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(resp{
        Message: "hi 👋",
        When:    time.Now(),
    })
})
```

This creates a struct (a small data object), fills it, and converts it to JSON automatically before sending it to the client.

Example output:

```json
{
  "message": "hi 👋",
  "when": "2025-10-24T16:10:45Z"
}
```

## Handling POST Requests (Receiving Data)

In Go, you handle POST requests almost the same way as GET — the difference is that POST usually **carries data from the client**, either as form data or JSON.
 Here’s how to handle both.

### Basic POST route

You define a route just like before, but check the request method:

```go
mux.HandleFunc("/api/submit", func(w http.ResponseWriter, r *http.Request) {
    if r.Method != http.MethodPost {
        http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
        return
    }

    // Handle the data...
})
```

This ensures only POST requests are processed.

### Handling JSON POST bodies

If the client sends JSON, you can decode it directly into a Go struct using `json.Decoder`.

Example:

```go
mux.HandleFunc("/api/submit", func(w http.ResponseWriter, r *http.Request) {
    if r.Method != http.MethodPost {
        http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
        return
    }

    // Define the expected input shape
    type Input struct {
        Name  string `json:"name"`
        Email string `json:"email"`
    }

    var data Input
    err := json.NewDecoder(r.Body).Decode(&data)
    if err != nil {
        http.Error(w, "invalid JSON", http.StatusBadRequest)
        return
    }

    // Respond back with confirmation
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(map[string]string{
        "message": "data received",
        "name":    data.Name,
    })
})
```

#### How it works:

- The `r.Body` stream contains the JSON sent by the client.
- `json.NewDecoder(r.Body).Decode(&data)` reads and parses it into a Go struct.
- Always check for errors to handle invalid JSON safely.
- You can then use `data.Name`, `data.Email`, etc., inside your handler.

Example request (using `curl`):

```bash
curl -X POST http://localhost:8080/api/submit \
     -H "Content-Type: application/json" \
     -d '{"name":"Alice","email":"alice@example.com"}'
```

Example response:

```json
{
  "message": "data received",
  "name": "Alice"
}
```

### Handling HTML form data

If you’re dealing with an HTML form instead of JSON, you can use `r.ParseForm()` and read fields like this:

```go
mux.HandleFunc("/contact", func(w http.ResponseWriter, r *http.Request) {
    if r.Method != http.MethodPost {
        http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
        return
    }

    err := r.ParseForm()
    if err != nil {
        http.Error(w, "invalid form data", http.StatusBadRequest)
        return
    }

    name := r.FormValue("name")
    email := r.FormValue("email")

    w.Write([]byte("Thanks, " + name + "! We'll contact you at " + email))
})
```

This works automatically for form submissions like:

```html
<form method="POST" action="/contact">
  <input name="name">
  <input name="email">
  <button type="submit">Send</button>
</form>
```

## Using Headers in Go’s `net/http`

### Reading headers from a request

You can access incoming headers through the `http.Request` object.
 The header map is available as `r.Header`, and you can fetch a value using `r.Header.Get()`:

```go
mux.HandleFunc("/inspect", func(w http.ResponseWriter, r *http.Request) {
    userAgent := r.Header.Get("User-Agent")
    token := r.Header.Get("Authorization")

    w.Write([]byte("User-Agent: " + userAgent + "\n"))
    w.Write([]byte("Authorization: " + token + "\n"))
})
```

`r.Header` is a `map[string][]string`, but `.Get()` is the easiest way to retrieve a single header’s first value.

### Writing headers in a response

Response headers are set on the `http.ResponseWriter` before sending data.
 For example:

```go
mux.HandleFunc("/api/info", func(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    w.Header().Add("X-App-Version", "1.0")
    w.WriteHeader(http.StatusOK)
    w.Write([]byte(`{"status":"ok"}`))
})
```

- Use `Set` to assign or replace a header.
- Use `Add` if the header supports multiple values (for example, `Set-Cookie`).
- Always set headers before calling `Write()` or `WriteHeader()`, because once the body starts sending, headers are finalized.

#### Custom headers

You can freely define your own headers for internal metadata or debugging:

```go
w.Header().Set("X-Trace-ID", "abc123")
```

Clients or middleware can use these custom headers for logging, tracing, or versioning.

### Example: selecting a response format based on `Accept`

Checking request headers lets your server adapt its response:

```go
mux.HandleFunc("/data", func(w http.ResponseWriter, r *http.Request) {
    switch r.Header.Get("Accept") {
    case "application/json":
        w.Header().Set("Content-Type", "application/json")
        w.Write([]byte(`{"msg":"JSON response"}`))
    default:
        w.Header().Set("Content-Type", "text/plain; charset=utf-8")
        w.Write([]byte("plain text response"))
    }
})
```

This pattern is common in APIs that support both JSON and text or HTML output.

## Serving static files

You can let the server deliver static files (like images or CSS) from a folder on disk:

```go
fileServer := http.FileServer(http.Dir("./public"))
mux.Handle("/static/", http.StripPrefix("/static/", fileServer))
```

This means:

- Any URL starting with `/static/` will serve files from a local folder called `public`.
- For example, visiting `/static/logo.png` serves the file `./public/logo.png`.

## Adding middleware (like logging)

A **middleware** is a wrapper that runs before and after your handler.
 A simple logging middleware looks like this:

```go
func logging(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        next.ServeHTTP(w, r)
        log.Printf("%s %s (%s)", r.Method, r.URL.Path, time.Since(start))
    })
}
```

You would then apply it by wrapping your router:

```go
handler := logging(mux)
```

This makes the server log every request’s method, path, and duration.

## Using Structs as Handlers with `ServeHTTP`

In Go, any type that implements the method

```go
ServeHTTP(w http.ResponseWriter, r *http.Request)
```

satisfies the `http.Handler` interface.
 This means you can turn a struct into a reusable, stateful handler — one that can hold configuration, dependencies, or internal data.

### Example: a struct-based handler

```go
type GreetHandler struct {
    Greeting string
}
```

To make this struct a handler, define the `ServeHTTP` method:

```go
func (h *GreetHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "text/plain; charset=utf-8")
    w.Write([]byte(h.Greeting + ", world!"))
}
```

Now you can use an instance of the struct wherever a handler is expected:

```go
func main() {
    mux := http.NewServeMux()

    mux.Handle("/hello", &GreetHandler{Greeting: "Hello"})
    mux.Handle("/hi", &GreetHandler{Greeting: "Hi"})
    mux.Handle("/hey", &GreetHandler{Greeting: "Hey"})

    http.ListenAndServe(":8080", mux)
}
```

Each route uses the same handler type but with different data inside the struct.

### Why use a struct instead of `HandleFunc`?

Using a struct handler is useful when:

- You need to **store configuration or dependencies** (like a database connection, logger, or templates).
- You want a **cleaner structure** for complex logic that involves multiple methods.
- You’re following a more **object-oriented style** of organizing handlers.

For example:

```go
type UserHandler struct {
    DB *sql.DB
}

func (h *UserHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    users, err := h.fetchUsers()
    if err != nil {
        http.Error(w, "could not fetch users", http.StatusInternalServerError)
        return
    }
    json.NewEncoder(w).Encode(users)
}
```

Here, the `UserHandler` can access the database connection (`h.DB`) for every request — something that wouldn’t be as clean with anonymous functions.

### Combining struct handlers with middleware

Since a struct handler satisfies `http.Handler`, it integrates naturally with middleware:

```go
logged := logging(&GreetHandler{Greeting: "Hello"})
mux.Handle("/hello", logged)
```

The middleware doesn’t care whether the handler is a function or a struct — it just needs the `ServeHTTP` method.

## Context on handlers

In Go’s **`net/http`** package, every incoming HTTP request (`*http.Request`) carries a **context** object — accessible via the method `r.Context()`.

This context is extremely useful for:

- Detecting when a client cancels a request (for example, if they close the browser tab or lose connection).
- Handling timeouts and deadlines.
- Passing request-scoped values down to other functions.

The context helps you **write responsive and resource-efficient servers** — since you can stop processing work as soon as the client disconnects.

When a request is created, Go automatically associates it with a context.
 You can get it by calling:

```go
ctx := r.Context()
```

Then, you can:

- Listen for cancellation: `<-ctx.Done()`

  - The client disconnects.

  - The server times out the request.

  - The context is explicitly canceled.

    ```go
    ctx, cancel := context.WithCancel(r.Context())
    defer cancel()
    ```

- Check for errors: `ctx.Err()`

- Derive new contexts with timeout or values.

### Example

```go
func handler(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	log.Println("Request started")
	defer log.Println("Request finished")

	select {
	case <-time.After(5 * time.Second):
		// Simulate a long-running operation
		log.Println("Request processed successfully")
		fmt.Fprintln(w, "Request processed successfully")

	case <-ctx.Done():
		// The client canceled the request
		log.Println("Request canceled by the client:", ctx.Err())
		http.Error(w, "Request canceled by the client", http.StatusRequestTimeout)
	}
}
```
## Starting the web server

Once you’ve defined your routes and middleware, you can create an `http.Server`:

```go
srv := &http.Server{
    Addr:         ":8080",
    Handler:      handler,
    ReadTimeout:  10 * time.Second,
    WriteTimeout: 15 * time.Second,
    IdleTimeout:  60 * time.Second,
}
```

- `Addr` — the port to listen on (here it’s `8080`).
- `Handler` — what handles incoming requests.
- The timeouts protect against very slow or stuck clients.

To actually start the server:

```go
go func() {
    log.Printf("listening on http://localhost%v", srv.Addr)
    if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
        log.Fatalf("listen: %v", err)
    }
}()
```

This starts the server in a **background goroutine**, allowing the main program to keep running (so we can later shut it down cleanly).

## Graceful shutdown

When the user stops the server (for example, pressing `Ctrl+C`), it’s good practice to let existing requests finish before exiting.

That’s what this code does:

```go
stop := make(chan os.Signal, 1)
signal.Notify(stop, os.Interrupt)
<-stop
```

It waits until a stop signal (SIGINT) is received, then:

```go
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()
log.Println("shutting down...")
if err := srv.Shutdown(ctx); err != nil {
    log.Fatalf("server shutdown: %v", err)
}
log.Println("bye")
```

- The shutdown is given 5 seconds to finish any active requests.
- After that, the program exits cleanly.

## Running the server

1. Open a terminal in your project folder.

2. Initialize a Go module:

   ```bash
   go mod init example.com/myserver
   ```

3. Run the program:

   ```bash
   go run .
   ```

4. Visit:

   - [http://localhost:8080](http://localhost:8080/) → plain text
   - http://localhost:8080/api/hello → JSON response
   - http://localhost:8080/static/ → static files