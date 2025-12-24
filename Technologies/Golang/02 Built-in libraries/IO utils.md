# IO Utils

## io.NopCloser

io.NopCloser is a small but important utility in Go’s standard library. It exists to solve a very specific interface-mismatch problem cleanly and idiomatically.

`io.NopCloser` is a function in the `io` package:

```go
func NopCloser(r io.Reader) io.ReadCloser
```

It takes an `io.Reader` and returns an `io.ReadCloser` whose `Close` method does nothing.

Internally, it wraps the reader and adds a no-op `Close()` method.

### Why it exists

Many APIs in Go require an `io.ReadCloser`, not just an `io.Reader`. A common example is `http.Request.Body`, which is defined as:

```go
Body io.ReadCloser
```

But in many situations, you only have a reader (for example, `*bytes.Reader`, `*strings.Reader`, or `*bytes.Buffer`), which does **not** implement `Close()`.

`io.NopCloser` bridges that gap.

### Typical use case

#### HTTP requests

```go
body := strings.NewReader(`{"name":"alice"}`)
req, err := http.NewRequest("POST", url, io.NopCloser(body))
```

Here:

- `strings.NewReader` returns an `io.Reader`
- `http.NewRequest` wants an `io.Reader`, but later the request stores it as an `io.ReadCloser`
- `io.NopCloser` ensures the request can safely call `Close()` without special handling