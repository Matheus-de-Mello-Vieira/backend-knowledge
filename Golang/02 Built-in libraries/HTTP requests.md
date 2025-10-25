# HTTP requests

```go
package main

import (
    "fmt"
    "io"
    "net/http"
)

func main() {
    resp, err := http.Get("https://www.google.com")
    if err != nil {
        panic(err)
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        fmt.Printf("Request failed with status: %s\n", resp.Status)
        return
    }

    body, err := io.ReadAll(resp.Body)
    if err != nil {
        panic(err)
    }

    fmt.Println(string(body))
}
```

## Receve a JSON

See [json](./JSON.md)

## `http.NewRequest`

In Go, `http.NewRequest` is the function used to **create an HTTP request object** (`*http.Request`) before sending it with an HTTP client (like `http.Client`).

```go
req, err := http.NewRequest(method, url, body)
```

### Signature

```go
func NewRequest(method, url string, body io.Reader) (*http.Request, error)
```

### Parameters

- **`method`**: HTTP method like `"GET"`, `"POST"`, `"PUT"`, `"DELETE"`, etc.
- **`url`**: The target URL as a string (e.g., `"https://example.com/api"`).
- **`body`**: The request body (use `nil` for methods without a body like GET).
   The body must implement `io.Reader` — e.g. `strings.NewReader`, `bytes.NewBuffer`, or a file.

### Returns

- `*http.Request`: the request object you can modify before sending.
- `error`: non-nil if there’s a problem creating the request (e.g., invalid URL).

### Execution

````go
resp, err := http.DefaultClient.Do(req)
````

Or, with a client object:

```go
client := &http.Client{}
resp, err := client.Do(req)
if err != nil {
    panic(err)
}
defer resp.Body.Close()
```

### How to Customize the Request

#### Set Headers

Use the `Header` map to set or add headers:

```go
req.Header.Set("Content-Type", "application/json")
req.Header.Set("Authorization", "Bearer your-token")
req.Header.Add("X-Custom", "custom-value")
```

#### Add Query Parameters

You can manipulate the request URL directly:

```go
q := req.URL.Query()
q.Add("page", "1")
q.Add("limit", "20")
req.URL.RawQuery = q.Encode()
```

This modifies the URL to something like:

```
https://example.com/api/users?page=1&limit=20
```

#### Set Cookies

Cookies can be attached manually:

```go
req.AddCookie(&http.Cookie{
    Name:  "session_id",
    Value: "xyz123",
})
```

### Custom Body (Streams, Files, etc.)

You can use any `io.Reader` as a body — for example, to upload a file:

```go
file, _ := os.Open("photo.jpg")
defer file.Close()

req, _ := http.NewRequest("PUT", "https://example.com/upload", file)
req.Header.Set("Content-Type", "image/jpeg")
```

* Note: When using a stream as body, the request cannot be retried automatically because the body can’t be re-read.

### Set a Custom Host Header

You can override the host header (useful for testing reverse proxies):

```go
req.Host = "custom.example.com"
```

## Timeout

In Go, you can set a timeout on an HTTP request in **three main ways**, depending on what level of control you want — globally (via the client), per request, or through a context.

### Set Timeout on the `http.Client`

This is the simplest and most common way — it sets a timeout for the entire request (including connection, redirects, and reading the body).

```go
package main

import (
    "fmt"
    "net/http"
    "time"
)

func main() {
    client := &http.Client{
        Timeout: 5 * time.Second, // total timeout for the request
    }

    resp, err := client.Get("https://example.com")
    if err != nil {
        fmt.Println("Error:", err)
        return
    }
    defer resp.Body.Close()

    fmt.Println("Status:", resp.Status)
}
```

* The timeout covers **the entire lifecycle** of the request — from dialing to reading the response body.

###  Use `context.WithTimeout` for per-request timeout

This lets you control timeout on a per-request basis — useful if you don’t want a global timeout.

```go
package main

import (
    "context"
    "fmt"
    "net/http"
    "time"
)

func main() {
    ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
    defer cancel()

    req, err := http.NewRequestWithContext(ctx, "GET", "https://example.com", nil)
    if err != nil {
        fmt.Println("Error creating request:", err)
        return
    }

    resp, err := http.DefaultClient.Do(req)
    if err != nil {
        fmt.Println("Error:", err)
        return
    }
    defer resp.Body.Close()

    fmt.Println("Status:", resp.Status)
}
```

* This timeout only affects this specific request.
* You can also cancel manually via `cancel()` if needed.

### Set timeouts on the Transport (fine-grained control)

If you need separate control over **connection**, **TLS handshake**, or **response read** timeouts, configure `http.Transport`:

```go
package main

import (
    "fmt"
    "net"
    "net/http"
    "time"
)

func main() {
    transport := &http.Transport{
        DialContext: (&net.Dialer{
            Timeout:   2 * time.Second, // connection timeout
            KeepAlive: 30 * time.Second,
        }).DialContext,
        TLSHandshakeTimeout:   2 * time.Second,
        ResponseHeaderTimeout: 3 * time.Second, // wait for server headers
        ExpectContinueTimeout: 1 * time.Second,
    }

    client := &http.Client{
        Transport: transport,
    }

    resp, err := client.Get("https://example.com")
    if err != nil {
        fmt.Println("Error:", err)
        return
    }
    defer resp.Body.Close()

    fmt.Println("Status:", resp.Status)
}
```

* Where `DialContext` is a function that opens a network (TCP) connection using a `context.Context`.
* This gives **fine-grained** control and can be combined with `Client.Timeout` or a `context`.
