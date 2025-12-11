# Builder

> Separate the construction of a complex object from its representation so that the same construction process can create different representations.

## Motivation

A service responsible for establishing outbound connections requires a configuration object with many optional and evolving parameters: timeouts, TLS settings, retry policies, limits, and host/port details. Early iterations rely on a single struct literal or a constructor with numerous arguments. This creates several issues:

- Callers must understand default values and invariants.
- Long parameter lists make misuse easy and readability poor.
- Many configuration fields are optional but still must be specified.
- Cross-field validation is scattered across the codebase.

The Builder pattern enables incremental and explicit configuration of a complex object while centralizing defaults and validation in one place.

## Sample Code

### Product

```go
type ClientConfig struct {
    Host           string
    Port           int
    EnableTLS      bool
    CertFile       string
    KeyFile        string
    TimeoutSeconds int
    RetryCount     int
}
```

### Builder

```go
type ClientConfigBuilder struct {
    cfg ClientConfig
}

func NewClientConfigBuilder(host string, port int) *ClientConfigBuilder {
    return &ClientConfigBuilder{
        cfg: ClientConfig{
            Host:           host,
            Port:           port,
            TimeoutSeconds: 5,
            RetryCount:     3,
        },
    }
}

func (b *ClientConfigBuilder) EnableTLS(certFile, keyFile string) *ClientConfigBuilder {
    b.cfg.EnableTLS = true
    b.cfg.CertFile = certFile
    b.cfg.KeyFile = keyFile
    return b
}

func (b *ClientConfigBuilder) Timeout(seconds int) *ClientConfigBuilder {
    b.cfg.TimeoutSeconds = seconds
    return b
}

func (b *ClientConfigBuilder) Retries(n int) *ClientConfigBuilder {
    b.cfg.RetryCount = n
    return b
}

func (b *ClientConfigBuilder) Build() (ClientConfig, error) {
    if b.cfg.EnableTLS && (b.cfg.CertFile == "" || b.cfg.KeyFile == "") {
        return ClientConfig{}, fmt.Errorf("TLS enabled but missing certificate/key")
    }
    return b.cfg, nil
}
```

### Client

```go
cfg, err := NewClientConfigBuilder("api.example.com", 443).
    EnableTLS("/etc/cert.pem", "/etc/key.pem").
    Timeout(15).
    Retries(5).
    Build()
```

## Consequences

- **Centralized construction logic**: Defaults, invariants, and relationships are handled in one place.
- **Readable configuration**: Each builder method clearly expresses the configuration being applied.
- **Single validation point**: `Build` can enforce dependencies between fields.
- **Separation of phases**: Partial configuration stays inside the builder; clients receive only complete, validated objects.
- **Extensible design**: New fields require adding one builder method without affecting callers.
- **Added complexity**: Introduces an additional type and may violate strict command/query separation due to mutation + chaining.

## Implementation

### Builder Mutation Models

* **Pointer-receiver builders**: Methods mutate shared state and return the same builder, combining mutation and value-returning behavior. This is ergonomic but couples configuration steps tightly to a single mutable instance.
  ```go
  func (b *CfgBuilder) Timeout(s int) *CfgBuilder {
      b.cfg.TimeoutSeconds = s // shared mutation
      return b                 // chaining
  }
  ```

* **Value-receiver builders**: Each method works on a copy and returns the updated copy. This limits side effects and avoids leaking state across chains, while still allowing fluent usage.
  ```go
  func (b CfgBuilder) Timeout(s int) CfgBuilder {
      b.cfg.TimeoutSeconds = s // mutation of the copy
      return b                 // new builder value
  }
  ```

* **Strict separation variant**: Setter methods mutate but return nothing; only `Build` returns the final product. This removes fluent chaining but cleanly isolates configuration from querying.
  
  ```go
  func (b *CfgBuilder) SetTimeout(s int) { b.cfg.TimeoutSeconds = s }
  func (b *CfgBuilder) Build() Config    { return b.cfg }
  ```

### Faceted Builders

To illustrate faceted builders, consider a `Person` type whose fields naturally group into distinct domains:

```go
type Person struct {
    // address
    StreetAddress, Postcode, City string
  
    // job
    CompanyName, Position         string
    AnnualIncome                  int
}
```

- **Multiple focused builders**: A faceted builder splits configuration into distinct sub-builders, each responsible for a specific domain.

  - Address facet (`PersonAddressBuilder`): configures `StreetAddress`, `City`, and `Postcode`.
  - Job facet (`PersonJobBuilder`): configures `CompanyName`, `Position`, and `AnnualIncome`.
     This separation prevents a single builder type from accumulating many unrelated setters.

  ```go
  type PersonAddressBuilder struct{ PersonBuilder }
  type PersonJobBuilder     struct{ PersonBuilder }
  ```

- **Shared underlying object**: Each facet embeds the root `PersonBuilder`, which holds a pointer to the same underlying `Person` instance.

  - All facets mutate the same product under construction.
  - No additional coordination is required across facets because all mutations converge on the same state.

  ```go
  type PersonBuilder struct{ person *Person }
  ```

- **Chaining across facets**: Because each facet embeds the root builder, callers can move fluidly from one facet to another in a single expression.
   The example below mirrors the original code and shows how the pattern produces a clean domain-oriented DSL:

  ```go
  pb := NewPersonBuilder()
  pb.
    Lives().
      At("123 London Road").
      In("London").
      WithPostcode("SW12BC").
    Works().
      At("Fabrikam").
      AsA("Programmer").
      Earning(123000)
  
  person := pb.Build()
  ```

- **Things to be aware of**:

  - **CQS considerations**: Facet methods mutate shared builder state and return the facet for chaining, combining command and query behaviors in each call.
  - **Shared state reuse**: Reusing a single builder for multiple independent builds can leak state unexpectedly.
  - **Concurrency**: All facets mutate the same pointer; the pattern is unsafe for concurrent use.
  - **Testing considerations**: Partial intermediate states depend on hidden shared mutation, which may complicate isolation in tests.
  - **Idiomaticity**: This fluent, OOP-styled pattern is uncommon in Go; struct literals or functional options usually provide a simpler and more conventional API.

### Hiding the Underlying Struct

Hiding the underlying struct is appropriate when the type cannot be safely or meaningfully constructed outside the builder’s control. Some objects require defaults, validation rules, or a specific sequence of configuration steps to reach a valid state. If callers can bypass the builder and instantiate the struct directly, they can create inconsistent or partially initialized objects that violate those rules. Hiding the struct ensures that every instance goes through the same construction path, reinforcing invariants, preventing misuse, and keeping the type’s correctness guarantees intact. It also stabilizes the API surface by allowing internal representation and validation logic to evolve without exposing those details to external code.

**Encapsulated product type**: The builder can be the exclusive way to construct a type by making the underlying struct unexported. This forces callers to use the builder and guarantees that all instances pass through controlled construction logic.

```go
// unexported
type email struct {
    from, to, subject, body string
}

type EmailBuilder struct {
    email email
}
func (it *EmailBuilder) From(addr string) *EmailBuilder {
    if !strings.Contains(addr, "@") {
        panic("email should contain @!")
    }
    it.email.from = addr
    return it
}

func SendEmail(action func(*EmailBuilder)) {
    builder := EmailBuilder{}
    action(&builder)
    sendMailImpl(&builder.email) // all construction flows through here
}

// usage
func main() {
    SendEmail(func(b *EmailBuilder) {
        b.
            From("sender@example.com").
            To("receiver@example.com").
            Subject("Hello").
            Body("This is a test email.")
    })
}
```

* **Why use encapsulation here**:

  - **Ensures validation is always applied**: Callers must use `From`, so the `"@"` validation cannot be bypassed. If `email` were exported, nothing would stop callers from writing `email{from: "bad"}` and passing it directly to the mail-sending logic.

  - **Prevents partially initialized emails**: The builder ensures all required fields can be set before sending. Direct struct literals would allow missing `to`, `subject`, or `body` fields, producing invalid runtime behavior.

  - **Centralizes finalization**: All emails are funneled through `SendEmail`, which captures the complete builder state and calls `sendMailImpl` in a controlled way. If `email` were public, callers might call `sendMailImpl` directly with unsafe or incomplete data.

  - **Keeps internal representation flexible**: Because callers never instantiate `email` directly, you are free to change its fields, rename them, or introduce derived fields without breaking external code.

  - **Eliminates misuse-by-construction**: The builder API exposes only valid operations (e.g., setting `From`), so it's impossible for users to construct logically invalid permutations of the email structure.

### Functional Builder Variant

- **Action accumulation**: Instead of mutating the product directly, each builder method records a function that knows how to modify the final object. The builder stores these functions in order, preserving construction sequencing without requiring shared mutable state.

  ```go
  type personMod func(*Person)
  
  type PersonBuilder struct {
      actions []personMod
  }
  
  func (b *PersonBuilder) Called(name string) *PersonBuilder {
      b.actions = append(b.actions, func(p *Person) { p.name = name })
      return b
  }
  ```

- **Single-point materialization**: `Build` creates a fresh product instance and applies all recorded actions to it. This pattern cleanly separates configuration from execution and keeps intermediate states immutable.

  ```go
  func (b *PersonBuilder) WorksAsA(job string) *PersonBuilder {
      b.actions = append(b.actions, func(p *Person) { p.position = job })
      return b
  }
  
  func (b *PersonBuilder) Build() *Person {
      p := &Person{}
      for _, a := range b.actions {
          a(p)
      }
      return p
  }
  ```

- **CQS alignment**: Builder methods return the builder for chaining but do not mutate the product. All mutations occur inside `Build`, improving reasoning about side effects and avoiding the shared-state concerns of pointer-based builders.

- **Extensibility**: New configuration steps require only appending another modifier function. This keeps the builder small and incremental, without adding multiple facet types or embedding layers.

- **Trade-offs**:

  - **Debugging and validation**: Because the actual mutations are deferred into closures, validation must be centralized in `Build` or placed inside each modifier. Tracking incorrect configuration can be less direct than in a declarative or struct-literal approach.
  - **Runtime overhead**: Each builder method allocates a closure. Typically negligible, but relevant for high-performance or allocation-sensitive paths.
  - **Not strictly idiomatic**: Go codebases more commonly use declarative config structs or functional options. Functional builders are appropriate when fluent chaining is valuable and deferred execution clarifies the model.

### Validation

- **Validation in `Build`**: Centralizes correctness checks.
- **Validation per setter**: Returns errors earlier but increases method complexity.

### Reuse

- Builders are typically **single-use**.
- If reuse is required, provide a `Reset` method or prefer value builders.

### Error Handling

- `Build` should return `(ClientConfig, error)` for invalid combinations.
- Use panics only for invariant violations that indicate a programming error.

## Go-Idiomatic Alternatives

### Functional Options

A common Go-native approach is to represent configuration steps as functions:

```go
type ClientOption func(*ClientConfig)
```

Examples:

```go
func WithTLS(cert, key string) ClientOption {
    return func(cfg *ClientConfig) {
        cfg.EnableTLS = true
        cfg.CertFile = cert
        cfg.KeyFile = key
    }
}

func WithTimeout(s int) ClientOption {
    return func(cfg *ClientConfig) {
        cfg.TimeoutSeconds = s
    }
}
```

Constructor:

```go
func NewClientConfig(host string, port int, opts ...ClientOption) (ClientConfig, error) {
    cfg := ClientConfig{
        Host:           host,
        Port:           port,
        TimeoutSeconds: 5,
        RetryCount:     3,
    }

    for _, opt := range opts {
        opt(&cfg)
    }

    if cfg.EnableTLS && (cfg.CertFile == "" || cfg.KeyFile == "") {
        return ClientConfig{}, fmt.Errorf("TLS enabled but missing certificate/key")
    }

    return cfg, nil
}
```

Usage:

```go
cfg, err := NewClientConfig(
    "api.example.com",
    443,
    WithTLS("/etc/client.crt", "/etc/client.key"), // optional feature
    WithTimeout(15),                               // override default timeout
    WithRetries(5),                                // override default retry policy
)
```

Characteristics:

- **Constructor-centric**: No builder object required.
- **Extensible**: New options are added without touching existing code.
- **Compact call sites**: Callers select desired options explicitly.
- **Common in Go**: Matches language idioms and standard library patterns.

Functional options are preferred when:

- The object is created in a single step.
- Configuration is mostly optional.
- The builder type would add unnecessary complexity.

### Declarative Configuration

- **Struct-as-configuration**: Callers provide a complete configuration struct, often nested, that describes the desired final object.
- **Single-shot construction**: A constructor or `Build` function interprets the struct, applies defaults, validates fields, and returns the runtime object.
- **No stepwise construction**: There is no intermediate mutable state or ordered build sequence; everything is specified up front.
- **Natural fit for Go**: Struct literals, JSON/YAML compatibility, and separation of configuration from behavior make this approach common in Go APIs.
- **Used by major ecosystems**: Kubernetes manifests, Terraform resource specs, Pulumi configurations, and many stdlib patterns (e.g., `tls.Config`, `http.Server`) rely on declarative configuration.
- **When to prefer it**: Use this model when the object can be fully described as data, ordering does not matter, and you want immutability, serialization friendliness, and easy composition.

## Known Uses

### `strings.Builder` (standard library)

A dedicated object accumulates text in steps and produces the final string via `String()`, matching the Builder idea of staged construction:

```go
var b strings.Builder
b.WriteString("Hello")
b.WriteByte(' ')
b.WriteString("World")
result := b.String() // final constructed product
```

### `bytes.Buffer` (standard library)

Similar to `strings.Builder`, but for constructing binary data incrementally:

```go
var buf bytes.Buffer
buf.Write([]byte{0x01, 0x02})
buf.WriteString(" payload")
data := buf.Bytes()   // final product
text := buf.String()  // alternative finalized representation
```

### `net/http.Request` construction

Although not exposed as a formal builder, the pattern emerges naturally: create a base object, then configure it in steps before use.

```go
req, err := http.NewRequest("GET", "https://example.com", nil)
if err != nil { /* handle */ }

req.Header.Set("User-Agent", "MyClient/1.0")
req.Header.Set("Accept", "application/json")
req = req.WithContext(ctx) // staged, incremental configuration

resp, err := http.DefaultClient.Do(req) // final usage
```

This mirrors the builder flow: construct → configure → finalize.

### `encoding/json.Encoder`

An `Encoder` allows staged configuration before producing output:

```go
buf := &bytes.Buffer{}
enc := json.NewEncoder(buf)

enc.SetIndent("", "  ")       // configuration step
enc.SetEscapeHTML(false)      // configuration step

_ = enc.Encode(map[string]any{
    "message": "hello",
})

final := buf.String() // final serialized document
```

The encoder maintains internal state until a finalizing action (`Encode`) produces the output.

### Terraform Plugin SDK (third-party)

Schema definitions and resource configurations frequently use *Declarative Configuration*.

```go
schema := &schema.Resource{
    Schema: map[string]*schema.Schema{
        "name": {
            Type:     schema.TypeString,
            Required: true,
        },
    },
}

resource := schema.Data(nil) // constructing a final resource from staged config
```
