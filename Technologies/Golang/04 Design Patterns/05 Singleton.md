# Singleton

> A component which is instantiated only once.

> When discussing which patterns to drop, we found that we still love them all. (Not really—I'm in favor of dropping Singleton. Its use is almost always a design smell.)
>
> — *Erich Gamma*

## Motivation

- Some components should exist only once in the system
  - Database connection or repository
  - Centralized object factory

- Creation is expensive
  - The instance is initialized a single time
  - All consumers share the same instance

- Additional instances must be prevented
  - Construction is controlled and not publicly exposed

- Lazy initialization is required
  - The instance is created only when first needed

## Consequences

- **Global access**: The instance is reachable from anywhere in the program, which simplifies access but increases coupling.
- **Implicit dependencies**: Callers may rely on the singleton without declaring it in function signatures, reducing dependency visibility.
- **Initialization ordering concerns**: Designs with lazy or explicit initialization introduce ordering rules that must be respected to avoid panics or inconsistent behavior.
- **Configuration rigidity**: A singleton naturally pushes toward a single, process-wide configuration and resists per-scope variation.
- **Concurrency safety requirements**: Shared access requires careful synchronization during initialization and mutation.
- **Test friction**: Global state complicates isolation and often requires indirection or stubs to test behavior deterministically.
- **Lifetime simplicity**: The instance typically lives for the entire process, eliminating the need for explicit teardown or lifecycle management.
- **Overuse risk**: Treating the singleton as a default dependency can hide architectural boundaries and discourage explicit composition.

## Sample code

Given

```go
import "sync"

type Database interface {
	GetPopulation(city string) int
}
```

The singleton

```go
type singletonDatabase struct {
	capitals map[string]int
}

func (db *singletonDatabase) GetPopulation(city string) int {
	return db.capitals[city]
}


var (
	dbOnce   sync.Once
	dbShared Database
)

func GetDatabase() Database {
	dbOnce.Do(func() {
		dbShared = &singletonDatabase{
			capitals: map[string]int{
				"Seoul":       17500000,
				"Mexico City": 17400000,
			},
		}
	})
	return dbShared
}
```

Usage

```go
func TotalPopulation(db Database, cities ...string) int {
	total := 0
	for _, city := range cities {
		total += db.GetPopulation(city)
	}
	return total
}

func main() {
	db := GetDatabase()
	_ = TotalPopulation(db, "Seoul", "Mexico City")
}
```

## Implementation

## Implementation

### Instance control

The singleton guarantee is enforced structurally: the concrete type is unexported and the only public access point is a package-level accessor. No language-level restriction is required.

```go
type singletonDatabase struct {
	capitals map[string]int
}

func GetDatabase() Database { /* ... */ }
```

Because the concrete type cannot be named outside the package, additional instances cannot be created by consumers.

### Lazy initialization

Construction is deferred until the first access. If the database is never requested, it is never created.

```go
func GetDatabase() Database {
	dbOnce.Do(func() {
		dbShared = &singletonDatabase{capitals: /* ... */}
	})
	return dbShared
}
```

This avoids paying initialization cost during startup when the component is unused.

### Concurrency safety

Exactly-once initialization under concurrent access is provided by `sync.Once`. No explicit locking or double-checked patterns are required.

```go
var dbOnce sync.Once
```

All goroutines observe the same fully initialized instance after the first call completes.

### Construction ownership

All creation logic lives inside the accessor. There is a single place where the instance can be constructed.

```go
dbOnce.Do(func() {
	dbShared = &singletonDatabase{capitals: /* ... */}
})
```

This prevents accidental duplication and makes construction policy explicit.

### Global state containment

The shared instance exists at package scope, but its use is confined. Core logic does not reach out to the global accessor directly.

```go
func TotalPopulation(db Database, cities ...string) int { /* ... */ }
```

The singleton is treated as a wiring concern rather than pervasive global state.

### Interface boundary

Clients depend on an interface, not on the singleton’s concrete type or accessor.

```go
type Database interface {
	GetPopulation(city string) int
}
```

This keeps the singleton replaceable and limits coupling to global state.

### Test substitution

Tests provide their own implementation without interacting with the singleton instance.

```go
type StubDatabase struct {
	data map[string]int
}
TotalPopulation(StubDatabase{data: map[string]int{"a": 1}}, "a")
```

The singleton remains unused in test paths.

### Usage discipline

Direct calls to `GetDatabase()` are confined to composition boundaries such as `main` or setup code.

```go
db := GetDatabase()
TotalPopulation(db, "Seoul")
```

Business logic remains parameterized, preventing the singleton from spreading implicitly through the codebase.

### Eager singleton via package-level initialization

This variant preserves the “single instance” and concurrency safety by relying on package initialization, but it gives up lazy construction: the instance is created as soon as the package is initialized.

The shared instance is constructed at package scope:

```go
var dbShared Database = &singletonDatabase{
	capitals: map[string]int{
		"Seoul":       17500000,
		"Mexico City": 17400000,
	},
}

func GetDatabase() Database {
	return dbShared
}
```

Concurrency safety is preserved because callers only read an already-initialized reference.

* What you gain with package-level init

  - **Fixed initialization timing**: The instance exists as soon as the package finishes init, so there’s no “first call” path to reason about.

  - **Less moving parts**: No `sync.Once`, no closure, no partial initialization concerns inside the accessor.

  - **Failure surfaces earlier**: If construction can fail (or panic), it happens during package init rather than deep into runtime on the first access.

* What you give up

  - **No lazy load**: Initialization cost is paid even when the singleton is never used.

  - **Less test control**: The instance is created before tests can substitute it if production code reaches for the accessor instead of taking a `Database` parameter.


### Configuration strategies for singletons

#### Eager, package-level value

Initialization happens during package load. The instance exists before any call site can observe it, so there is no “first-use” path and no initialization protocol.

```go
var db = &databaseImpl{
	endpoint: "db.prod.internal",
}

func GetDatabase() *databaseImpl { return db }
```

- **Keeps**: explicit configuration ownership, local use-site transparency, no hidden global dependencies.
- **Loses**: lazy initialization.

#### Explicit `InitX(cfg)` + `GetX()`

Configuration is applied once through an explicit initializer. Access is separated from configuration, which makes ownership visible, but introduces a lifecycle rule: `InitX` must run before `GetX`.

```go
var (
	initMu sync.Mutex
	db     *databaseImpl
)

func InitDatabase(cfg DatabaseConfig) {
	initMu.Lock()
	defer initMu.Unlock()

	if db != nil {
		panic("database already initialized")
	}
	db = &databaseImpl{endpoint: cfg.Endpoint}
}

func GetDatabase() *databaseImpl {
	if db == nil {
		panic("database not initialized")
	}
	return db
}
```

- **Keeps**: explicit configuration ownership, no hidden global dependencies.
- **Partially keeps**: local use-site transparency (use sites are simple, but correctness depends on `InitDatabase` having happened).
- **Often loses**: lazy initialization.

#### Lazy `GetX(opts...)` with `sync.Once`

Construction is deferred until first access and guarded with `sync.Once`. Accepting options at the accessor preserves laziness, but configuration authority becomes implicit: whichever call triggers initialization defines global behavior.

```go
var (
	once sync.Once
	db   *databaseImpl
)

func GetDatabase(opts ...DatabaseOption) *databaseImpl {
	once.Do(func() {
		db = NewDatabase(opts...)
	})
	return db
}
```

- **Keeps**: lazy initialization.
- **Loses**: explicit configuration ownership (ownership is implicit), local use-site transparency (“first caller wins” ambiguity).
- **Partially keeps**: no hidden global dependencies (configuration is explicit at the call that wins, but not globally enforceable).

#### Lazy `GetX()` that reads `globalConfig()`

Construction remains lazy, but configuration is pulled from ambient global state during initialization. This avoids passing configuration through call chains and can preserve centralized ownership, but it introduces an implicit dependency that call sites do not reveal.

```go
var (
	once sync.Once
	db   *databaseImpl
)

func GetDatabase() *databaseImpl {
	once.Do(func() {
		cfg := GlobalConfig()
		db = &databaseImpl{endpoint: cfg.Endpoint}
	})
	return db
}
```

- **Keeps**: lazy initialization.
- **Often keeps**: explicit configuration ownership (if configuration is truly centralized).
- **Loses**: no hidden global dependencies (ambient global dependency).
- **Usually weakens**: local use-site transparency (behavior is not clear at use sites).

## Go-Idiomatic Alternatives

* **Package-level value**: A `var` at package scope addresses “single shared instance” with the least machinery, and is preferred when lazy initialization is not needed.
  * The same implementation as an eager singleton via package-level initialization, described from a Go-native perspective rather than a GoF pattern perspective.
* [Closure-based provider](98%20Go-Idiomatic%20patterns.md#closure-based-provider): A closure-based provider offers controlled instance sharing without relying on package-level state. 
  * Instead of enforcing a single global instance, it scopes “singleness” to the owner of the provider, improving locality, testability, and dependency clarity.
  * This approach addresses the same problem as a singleton while aligning more closely with Go’s preference for explicit dependencies and bounded state.

## Known Uses

- **Go standard library – `log.Default()`**: Exposes a package-level shared logger instance intended to be used process-wide.
- **Go standard library – `http.DefaultServeMux`**: A global request multiplexer used when no custom mux is provided, effectively acting as a singleton router.
- **Go standard library – `http.DefaultClient`**: A shared HTTP client instance used by convenience functions such as `http.Get`.
- **Go standard library – `time.Local`**: A package-level variable representing the local timezone, initialized once and shared globally.
- **Go standard library – `rand.Reader`**: A shared, concurrency-safe source of cryptographically secure randomness.
- **Uber Go – `zap.L()`**: Returns a process-wide global logger intended for application-level use.
- **Prometheus – default registry**: The default metrics registry is a global singleton used unless an explicit registry is supplied.
