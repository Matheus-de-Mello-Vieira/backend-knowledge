# Decorator

> Facilitates the addition of behaviors to individual objects through embedding.

## Motivation

- **Cross-cutting behavior on interfaces**: In Go, functionality like logging, metrics, retries, or authorization often needs to be layered on top of existing interface implementations without modifying their concrete types.
- **Avoiding type explosion**: Without decorators, combining behaviors leads to a growing number of wrapper structs or ad-hoc implementations (for example, `LoggingClient`, `RetryingClient`, `LoggingRetryingClient`), which scales poorly as concerns multiply.
- **Preserving interface contracts**: Embedding or wrapping an interface allows additional behavior while still satisfying the same interface, keeping call sites unaware of the added logic.
- **Minimizing invasive changes**: Retrofitting new behavior directly into existing implementations forces code changes across packages, increasing coupling and regression risk.
- **Runtime composition**: Go favors explicit construction over inheritance; decorators allow behavior to be composed at initialization time based on configuration or environment, without conditional logic spread through the codebase.

## Sample Code

**Stable contract**: Defines the behavior that both concrete components and decorators must satisfy.

```go
type Service interface {
	Do(req string) (string, error)
}
```

**Core behavior**: Implements the business logic without any cross-cutting concerns.

```go
type baseService struct{}

func (baseService) Do(req string) (string, error) {
	return "ok:" + req, nil
}
```

**Delegation point**: Holds a reference to another `Service` and forwards calls by default.

```go
type serviceDecorator struct {
	next Service
}

func (d serviceDecorator) Do(req string) (string, error) {
	return d.next.Do(req)
}
```

**Behavior extension**: Adds logging before or after delegating to the wrapped service.

```go
type loggingDecorator struct {
	serviceDecorator
}

func (d loggingDecorator) Do(req string) (string, error) {
	res, err := d.next.Do(req)
	println("req:", req, "err:", err)
	return res, err
}
```

**Independent concern**: Adds metrics without modifying either the base service or other decorators.

```go
type metricsDecorator struct {
	serviceDecorator
}

func (d metricsDecorator) Do(req string) (string, error) {
	res, err := d.next.Do(req)
	// record metrics here
	return res, err
}
```

**Runtime composition**: Builds a decorator chain explicitly, keeping concerns modular and order-controlled.

```go
func newService() Service {
	var svc Service = baseService{}
	svc = metricsDecorator{serviceDecorator{next: svc}}
	svc = loggingDecorator{serviceDecorator{next: svc}}
	return svc
}
```

## Implementation

### Interface-first boundary

Decorators are most effective when applied at an interface seam that already exists and is stable.

```go
type Client interface {
	Do(req string) error
}
```

This keeps decorators orthogonal to concrete implementations and prevents leakage of internal details.

### Struct wrapper vs function wrapper

Struct-based and function-based decorators are both idiomatic in Go, but they optimize for different constraints.

* **Struct wrapper**: Makes dependencies and configuration explicit, supports internal state, and scales naturally to multi-method interfaces at the cost of more boilerplate.

  ```go
  type loggingClient struct {
    next Client
  }

  func (l loggingClient) Do(req string) error {
    println("start:", req)
    return l.next.Do(req)
  }
  ```

* **Function wrapper**: For [Single-Method Interface Adapters via Function Types](../01%20Essentials/05%20Structs%20and%20Custom%20types.md#single-method-interface-adapters-via-function-types), function wrappers are concise and effective for single-method interfaces, but they become opaque once behavior grows, state is needed, or multiple methods must be forwarded.

  ```go
  func withLogging(next Client) Client {
    return clientFunc(func(req string) error {
      println("start:", req)
      return next.Do(req)
    })
  }
  ```

### Embedding a forwarding base

A shared forwarding struct reduces boilerplate but centralizes delegation.

```go
type decorator struct {
	next Client
}

func (d decorator) Do(req string) error {
	return d.next.Do(req)
}
```

Concrete decorators embed this type and override only the methods they extend.

### Multi-method interfaces

Large interfaces increase decorator surface area and maintenance cost.

```go
type Storage interface {
	Get(key string) (string, error)
	Put(key, value string) error
}
```

Decorating such interfaces often motivates splitting them into smaller, role-specific interfaces.

### Pointer vs value receivers

Receiver choice mainly affects whether the decorator can safely carry mutable state and how it behaves when copied.

* **Value receiver**: Works well for immutable decorators (configuration-only, observation-only), is easy to stack, and avoids shared mutable state, but copying the decorator value is part of the API contract.

  ```go
  type timingDecorator struct {
    next Client
  }
  
  func (d timingDecorator) Do(req string) error {
    // observe only; no internal mutation
    return d.next.Do(req)
  }
  ```

- **Pointer receiver**: Required when the decorator mutates internal state (counters, caches, token buckets), avoids accidental state loss from copies, but introduces shared state that needs synchronization if used concurrently.

  ```go
  type countingDecorator struct {
    next  Client
    count int
  }
  
  func (d *countingDecorator) Do(req string) error {
    d.count++
    return d.next.Do(req)
  }
  ```

### Error and context propagation

Decorators must be explicit about whether they observe or transform failures.

```go
func (d retryDecorator) Do(req string) error {
	err := d.next.Do(req)
	if err != nil {
		return fmt.Errorf("retry failed: %w", err)
	}
	return nil
}
```

Unintended error rewriting can break callers that rely on specific error semantics.

### Ordering is part of the behavior

Decorator composition order directly affects semantics.

```go
func newClient(base Client) Client {
	c := timeoutDecorator{next: base}
	c2 := retryDecorator{next: c}
	return c2
}
```

This ordering encodes policy and should be treated as part of the system design.

### Configuration surface area

Each decorator should own its configuration.

```go
type retryDecorator struct {
	next  Client
	limit int
}
```

Avoid passing shared configuration through the entire chain unless it is truly global.

### Testing strategy

Decorators are easiest to test against a controlled stub.

```go
type stubClient struct {
	called bool
}

func (s *stubClient) Do(req string) error {
	s.called = true
	return nil
}
```

This isolates the decorator’s behavior from the rest of the system.

### Performance overhead

Every decorator adds a call boundary.

```go
func (d noopDecorator) Do(req string) error {
	return d.next.Do(req)
}
```

In hot paths, keep decorators shallow and avoid per-call allocations.

### Interop with standard patterns

Prefer existing extension points when available.

```go
type RoundTripper interface {
	RoundTrip(*http.Request) (*http.Response, error)
}
```

Aligning with established interfaces makes decorators composable with the wider Go ecosystem.

### `Wrap` function for composition

A `Wrap` helper makes decorator assembly explicit and repeatable, especially when the same stack is built in multiple places.

```go
type Decorator func(Client) Client

func Wrap(base Client, decorators ...Decorator) Client {
	c := base
	for i := len(decorators) - 1; i >= 0; i-- {
		c = decorators[i](c)
	}
	return c
}
```

Usage example

```go
func withLogging(next Client) Client {
	return loggingClient{next: next}
}

func withMetrics(next Client) Client {
	return metricsDecorator{next: next}
}
client := Wrap(
	baseClient{},
	withMetrics,
	withLogging,
)
```

- **Explicit composition**: Call sites clearly show which behaviors are applied and in what order.
- **Reusable wiring**: The same decorators can be recombined without duplicating construction logic.
- **Order-sensitive semantics**: The slice order defines behavior, so changes must be reviewed carefully.
- **Abstraction trade-off**: Simplifies client code but can hide the concrete decorator chain if naming and structure are sloppy.

## Go-Idiomatic Alternatives

### Constructor configuration instead of wrapping

```go
type Client struct {
	log bool
}

func NewClient(log bool) *Client {
	return &Client{log: log}
}
```

- **Prefer when**: The behavior is a simple feature toggle or parameter that does not need independent composition or ordering.
- **Trade-off**: Couples optional behavior to the concrete type and does not scale well as concerns multiply.

### Explicit collaborators over implicit layering

```go
type Service struct {
	logger Logger
}

func (s Service) Do(req string) {
	s.logger.Log(req)
}
```

- **Prefer when**: The concern is fundamental to the operation and separating it into a wrapper would obscure control flow.
- **Trade-off**: Reduces flexibility at runtime and makes behavior harder to retrofit across many implementations.

### Pipeline-style APIs instead of object decoration

```go
type Handler func(req string)

func Logging(next Handler) Handler {
	return func(req string) {
		println("req:", req)
		next(req)
	}
}
```

- **Prefer when**: The domain naturally fits a linear request/response pipeline rather than an object with identity.
- **Trade-off**: Less suitable when state, multiple methods, or richer interfaces are involved.

### Package-level helpers instead of polymorphic extension

```go
func LogRequest(req string) {
	println("req:", req)
}
```

- **Prefer when**: The behavior is purely mechanical and does not need to vary per implementation.
- **Trade-off**: Loses substitutability and cannot be composed or reordered per use case.

### Accepting duplication for clarity

```go
func (s ServiceA) Do(req string) {
	println("req:", req)
	// logic A
}

func (s ServiceB) Do(req string) {
	println("req:", req)
	// logic B
}
```

- **Prefer when**: Only one or two call sites need the behavior and abstraction would add more complexity than value.
- **Trade-off**: Duplication becomes technical debt if the concern spreads.

## Known Uses

- **Go standard library `io.LimitReader` / `io.TeeReader`**: Return an `io.Reader` that wraps another reader to add limits or side-effects while preserving the same interface.
- **Go standard library `bufio.NewReader` / `bufio.NewWriter`**: Wrap `io.Reader`/`io.Writer` to add buffering behavior without changing call sites.
- **Go standard library `http.TimeoutHandler` / `http.StripPrefix`**: Return an `http.Handler` that wraps another handler to enforce timeouts or rewrite requests before delegation.
- **gRPC interceptors (`grpc.UnaryServerInterceptor`, `grpc.UnaryClientInterceptor`)**: Compose cross-cutting behavior (auth, logging, retries, metrics) around RPC handlers/clients via wrapper chains.
- **Prometheus `promhttp` instrumentation helpers**: Wrap `http.Handler`/`RoundTripper` to add metrics collection transparently at the boundary.
- **OpenTelemetry `otelhttp` handler/transport wrappers**: Wrap `http.Handler` and `http.RoundTripper` to inject tracing/context propagation without touching business logic.
- **`justinas/alice` middleware chaining**: Provides a small composition API for stacking `http.Handler` decorators cleanly and predictably.
