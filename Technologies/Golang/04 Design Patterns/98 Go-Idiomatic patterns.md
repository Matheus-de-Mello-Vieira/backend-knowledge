# Go-Idiomatic Patterns

This note collects alternatives to classical [GoF-style builders](02%20Builder.md) that align better with Go norms.

## Functional Options

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

## Declarative Configuration

- **Struct-as-configuration**: Callers provide a complete configuration struct, often nested, that describes the desired final object.
- **Single-shot construction**: A constructor or `Build` function interprets the struct, applies defaults, validates fields, and returns the runtime object.
- **No stepwise construction**: There is no intermediate mutable state or ordered build sequence; everything is specified up front.
- **Natural fit for Go**: Struct literals, JSON/YAML compatibility, and separation of configuration from behavior make this approach common in Go APIs.
- **Used by major ecosystems**: Kubernetes manifests, Terraform resource specs, Pulumi configurations, and many stdlib patterns (e.g., `tls.Config`, `http.Server`) rely on declarative configuration.
- **When to prefer it**: Use this model when the object can be fully described as data, ordering does not matter, and you want immutability, serialization friendliness, and easy composition.

### Example:

A server constructor that takes a configuration struct. The constructor applies defaults, validates the input, and returns a fully configured runtime object.

Note: snippets omit `package`/`import`; assume `fmt` and `time` are imported.

#### The declarative config (pure data)

The **Config** is the whole point of this pattern: it’s a data-only description of what you want. It’s easy to build as a struct literal, and it can be loaded from JSON/YAML because it’s just fields.

```go
type Config struct {
	Address  string     `json:"address" yaml:"address"`
	Port     int        `json:"port" yaml:"port"`
	Timeouts Timeouts   `json:"timeouts" yaml:"timeouts"`
	TLS      *TLSConfig `json:"tls,omitempty" yaml:"tls,omitempty"`
}

type Timeouts struct {
	Read  time.Duration `json:"read" yaml:"read"`
	Write time.Duration `json:"write" yaml:"write"`
}

type TLSConfig struct {
	CertFile string `json:"certFile" yaml:"certFile"`
	KeyFile  string `json:"keyFile" yaml:"keyFile"`
}
```

Key idea: the config is **declarative** (no methods, no ordering) and **composable** (nested structs, optional pointers).

#### The runtime object (behavior-ready)

The runtime type is what the rest of your program uses. It can be simpler than the config because it no longer needs to mirror “how users specify it”; it represents “what the program needs at runtime”.

```go
type Server struct {
	Address      string
	ReadTimeout  time.Duration
	WriteTimeout time.Duration
	UseTLS       bool
}
```

Key idea: separate “what users declare” from “what the program runs with”.

### The single-shot constructor (defaults + validation + materialization)

This is the interpreter for your declarative config. It:

1. Applies defaults (for omitted/zero values)
2. Validates (fails early with a clear error)
3. Materializes (builds the final runtime object)

```go
func NewServer(cfg Config) (*Server, error) {
	if cfg.Port == 0 {
		cfg.Port = 8080
	}
	if cfg.Timeouts.Read == 0 {
		cfg.Timeouts.Read = 5 * time.Second
	}
	if cfg.Timeouts.Write == 0 {
		cfg.Timeouts.Write = 10 * time.Second
	}

	if cfg.Address == "" {
		return nil, fmt.Errorf("address is required")
	}

	useTLS := false
	if cfg.TLS != nil {
		if cfg.TLS.CertFile == "" || cfg.TLS.KeyFile == "" {
			return nil, fmt.Errorf("TLS is configured but certFile or keyFile is missing")
		}
		useTLS = true
		if cfg.Port == 8080 {
			cfg.Port = 443
		}
	}

	return &Server{
		Address:      fmt.Sprintf("%s:%d", cfg.Address, cfg.Port),
		ReadTimeout:  cfg.Timeouts.Read,
		WriteTimeout: cfg.Timeouts.Write,
		UseTLS:       useTLS,
	}, nil
}
```

Key idea: the constructor is where **policy** lives (defaults, validation rules, derived fields). Callers just provide data.

### Call site (declarative usage)

The caller describes intent by filling only the parts they care about.

```go
appConfig := Config{
	Address: "api.myservice.com",
	Timeouts: Timeouts{
		Write: 20 * time.Second,
	},
	TLS: &TLSConfig{
		CertFile: "/etc/ssl/certs/service.crt",
		KeyFile:  "/etc/ssl/private/service.key",
	},
}
```

And then does a single build step:

```go
srv, err := NewServer(appConfig)
if err != nil {
	panic(err)
}
fmt.Printf("Server constructed: %+v\n", srv)
```

Example result (showing defaults + derived fields like port selection):

```text
Server constructed: &{Address:api.myservice.com:443 ReadTimeout:5s WriteTimeout:20s UseTLS:true}
```

Key idea: construction is **atomic** (one function call), and once you have the runtime object it’s already **defaulted and validated**.

## Closure-based provider

A closure-based provider encapsulates a single instance inside a function. The shared value lives in the closure’s environment rather than in package-level state.

```go
type Database interface {
	GetPopulation(city string) int
}
```

The concrete implementation is ordinary and unexported.

```go
type databaseImpl struct {
	capitals map[string]int
}

func (db *databaseImpl) GetPopulation(city string) int {
	return db.capitals[city]
}
```

The provider function constructs the instance once and returns a function that provides access to it.

```go
func NewDatabaseProvider() func() Database {
	db := &databaseImpl{
		capitals: map[string]int{
			"Seoul":       17500000,
			"Mexico City": 17400000,
		},
	}

	return func() Database {
		return db
	}
}
```

Every call to the returned function yields the same instance, because all calls close over the same variable.

```go
getDB := NewDatabaseProvider()

db1 := getDB()
db2 := getDB()

_ = db1 == db2 // true
```

The scope of sharing is explicit. Creating a new provider creates a new, independent “singleton.”

```go
a := NewDatabaseProvider()
b := NewDatabaseProvider()

_ = a() == b() // false
```

This approach preserves controlled instance sharing without relying on global state. Lifecycle, visibility, and substitution remain local to the code that owns the provider, making the pattern easy to reason about and test in isolation.
