# Factories

> A component responsible solely for the wholesale (not piecewise) creation of objects.

## Motivation

- Object creation logic can become complex and error-prone.

- Structs with many fields require all values to be initialized correctly, increasing the risk of mistakes.

- Centralizing object creation in a single place improves consistency and maintainability.

- When objects are created all at once (as opposed to step-by-step, like the Builder pattern), this logic can be moved into a dedicated factory function (often called a constructor).

- This factory function may live alongside the type itself or be grouped into a separate factory structure when creation logic grows more complex.


## Sample code

The struct

```go
type Person struct {
	Name     string
	Age      int
	EyeCount int
}

func NewPerson(name string, age int) Person {
	return Person{
		Name:     name,
		Age:      age,
		EyeCount: 2, // default
	}
}
```

Usage

```go
func NewPerson(name string, age int) Person {
	return Person{
		Name:     name,
		Age:      age,
		EyeCount: 2, // default
	}
}
```

## Consequences

- **Centralized construction**: Object creation logic lives in one place, reducing duplication and preventing inconsistent initialization.
- **Stronger invariants**: Defaults and validation enforced by the factory ensure that created objects start in a valid state.
- **Reduced coupling**: Callers depend on the factory interface or function signature, not on concrete construction details.
- **Clear ownership of creation rules**: Business rules related to object creation have an explicit and discoverable home.
- **Improved readability at call sites**: Factory usage expresses intent (“create a Manager”, “hire via this factory”) instead of low-level field assignment.
- **Easier evolution of creation logic**: Changes to defaults, validation, or derived fields are localized to the factory.
- **Risk of over-abstraction**: Introducing factories too early can add unnecessary indirection when direct construction would suffice.
- **Pattern choice matters**: Functional factories favor simplicity and decoupling by signature, while structural factories favor extensibility and explicit state.

## Implementation

### Default value

The `Person` struct includes the field `EyeCount`, which in most cases should default to `2`. Since Go does not support default values for struct fields, this behavior is can be implemented using a factory (a.k.a. constructor) function:

```go
func NewPerson(name string, age int) *Person {
    return &Person{name, age, 2}
}

func main() {
    p := NewPerson("John", 33)
    p.EyeCount = 1
}
```

### Validation enforcement 

A factory function also provides a natural place to enforce validation rules during object creation:

```go
func NewPerson(name string, age int) (*Person, error) {
	if age < 16 {
		return nil, errors.New("age must be at least 16")
	}
	return &Person{name, age, 2}, nil
}
```

### Interface factory

A factory function can return an interface instead of a concrete type, hiding the underlying struct and decoupling callers from the implementation.

```go
type Person interface {
	SayHello() string
}

// hidden implementation
type person struct {
	name string
	age  int
}

func (p person) SayHello() string {
	return fmt.Sprintf(
		"Hi, my name is %s, I am %d years old",
		p.name,
		p.age,
	)
}

// factory
func NewPerson(name string, age int) Person {
	return person{
		name: name,
		age:  age,
	}
}

// usage
p := NewPerson("John", 33)
fmt.Println(p.SayHello())
```

- The concrete struct fields are now fully encapsulated behind the `Person` interface.

- Callers cannot access or modify internal state (`name`, `age`) directly.

- Interaction is restricted to the behavior exposed by the interface.

- The underlying implementation can change without affecting callers.

  ```go
  type person struct {
  	name      string
  	birthYear int
  }
  
  func (p person) SayHello() string {
  	age := time.Now().Year() - p.birthYear
  	return fmt.Sprintf(
  		"Hi, my name is %s, I am %d years old",
  		p.name,
  		age,
  	)
  }
  
  func NewPerson(name string, age int) Person {
  	return person{
  		name:      name,
  		birthYear: time.Now().Year() - age,
  	}
  }
  
  // the caller still unchanged
  p := NewPerson("John", 33)
  fmt.Println(p.SayHello())
  ```

- Multiple concrete implementations can satisfy the same interface and be used interchangeably (polymorphism).

  ```go
  type adult struct {
  	name string
  }
  
  func (a adult) SayHello() string {
  	return "Hello, I am an adult. My name is " + a.name
  }
  
  type child struct {
  	name string
  }
  
  func (c child) SayHello() string {
  	return "Hi! I'm " + c.name
  }
  
  func NewPerson(name string, age int) Person {
  	if age < 18 {
  		return child{name: name}
  	}
  	return adult{name: name}
  }
  ```

- Defaults, validation, and construction rules remain centralized in the factory.

- This reduces coupling and enforces stronger invariants.

- The design shifts from exposing data to exposing behavior, which scales better as the codebase grows.

### Factory Generator

This pattern allows you create factories depending on settings. It main purpose is avoid making the client set directly attributes after the creation of the object:

```go
func main() {
    p := NewPerson("John", 33)
    p.EyeCount = 1
}
```

There are two approaches to handle this matter: **functional** and **structural**. Both approaches achieve the same goal by centralizing and standardizing object creation, but they offer different trade-offs in terms of flexibility, readability, and extensibility.

As context, take:

```go
type Employee struct {
    Name, Position string
    AnnualIncome   int
}
```

#### Funcional approach

The **functional approach** uses a function that returns another function. The outer function captures the fixed configuration (such as position and salary), while the returned function is responsible for creating employees. This style is concise, emphasizes immutability, and works well when the factory has simple, fixed parameters.

```go
func NewEmployeeFactory(position string, annualIncome int) func(name string) *Employee {
	return func(name string) *Employee {
		return &Employee{
			Name:         name,
			Position:     position,
			AnnualIncome: annualIncome,
		}
	}
}
```

Usage:

```go
	developerFactory := NewEmployeeFactory("Developer", 120000)
	managerFactory := NewEmployeeFactory("Manager", 150000)

	// Use factories to create employees
	alice := developerFactory("Alice")
	bob := developerFactory("Bob")
	carol := managerFactory("Carol")

	fmt.Println(alice)
	fmt.Println(bob)
	fmt.Println(carol)
```

advantages:

* The functional approach is often more idiomatic and simpler, and is a good starting point. The structural approach should be introduced when creation logic grows or when additional behavior and extensibility are required.

* Because factories are first-class values, they can be passed as arguments to other functions. With the functional approach, consumers rely only on the factory’s function signature, using it without any knowledge of its internal structure, captured state, or implementation details.

  ```go
  // This function does not know *how* employees are created.
  // It only knows it receives a factory.
  func Hire(
  	names []string,
  	factory func(string) *Employee,
  ) []*Employee {
  	employees := make([]*Employee, 0, len(names))
  	for _, name := range names {
  		employees = append(employees, factory(name))
  	}
  	return employees
  }
  
  func main() {
  	developerFactory := NewEmployeeFactory("Developer", 120_000)
  	managerFactory := NewEmployeeFactory("Manager", 150_000)
  
  	devNames := []string{"Alice", "Bob"}
  	mgrNames := []string{"Carol"}
  
  	developers := Hire(devNames, developerFactory)
  	managers := Hire(mgrNames, managerFactory)
  
  	fmt.Println("Developers:", developers)
  	fmt.Println("Managers:", managers)
  }
  ```

#### Structural approach

The **structural approach** models the factory as a struct with fields holding the configuration and a method responsible for object creation. This approach is more explicit, easier to extend, and better suited when the factory needs additional behavior, state, or multiple creation methods.

```go
type EmployeeFactory struct {
	Position     string
	AnnualIncome int
}

func (f *EmployeeFactory) Create(name string) *Employee {
	return &Employee{
		Name:         name,
		Position:     f.Position,
		AnnualIncome: f.AnnualIncome,
	}
}

func NewEmployeeFactory(position string, annualIncome int) *EmployeeFactory {
	return &EmployeeFactory{
		Position:     position,
		AnnualIncome: annualIncome,
	}
}
```

Usage

```go
developerFactory := NewEmployeeFactory("Developer", 120_000)

alice := developerFactory.Create("Alice")
bob := developerFactory.Create("Bob")
```

Advantages:

* With a structural factory, configuration is stored as explicit fields on a struct. This makes the factory’s state visible, inspectable, and easy to modify or extend.

  ```go
  type EmployeeFactory struct {
  	Position     string
  	AnnualIncome int
  	Bonus        int
  }
  
  func (f *EmployeeFactory) SetBonus(bonus int) {
  	f.Bonus = bonus
  }
  
  func (f *EmployeeFactory) Create(name string) *Employee {
  	return &Employee{
  		Name:         name,
  		Position:     f.Position,
  		AnnualIncome: f.AnnualIncome + f.Bonus,
  	}
  }
  
  // usage
  factory := NewEmployeeFactory("Developer", 120_000)
  factory.SetBonus(10_000)
  ```

* Adding new parameters, defaults, or derived values is straightforward:

  * you introduce new fields or methods without changing the factory’s public usage.
  * In contrast, functional factories rely on closures, which implicitly capture state.
    * While concise, this hidden state becomes harder to reason about and evolve as complexity increases.
  * See above example, where we added the field `Bonus`.

* The structural approach also supports multiple creation methods on the same factory.

  * A single factory struct can expose several methods, each responsible for creating a different variation of an object.

    ```go
    // Create a full-time employee
    func (f *EmployeeFactory) CreateFullTime(name string) *Employee {
    	return &Employee{
    		Name:         name,
    		Position:     f.Position,
    		AnnualIncome: f.BaseIncome,
    		ContractType: "full-time",
    	}
    }
    
    // Create a contractor
    func (f *EmployeeFactory) CreateContractor(name string) *Employee {
    	return &Employee{
    		Name:         name,
    		Position:     f.Position,
    		AnnualIncome: f.BaseIncome / 2,
    		ContractType: "contractor",
    	}
    }
    ```

  * This is difficult to express cleanly with a single returned function, and often leads to additional nested functions or duplicated logic in the functional style.

* behavioral extension: Structural factories can implement interfaces, embed other structs, or be decorated and composed using standard Go techniques.

  * This enables polymorphism, testing with mocks, and substitution of different factory implementations.
  * Functional factories can be passed around as values, but they cannot naturally expose multiple behaviors or participate in richer type hierarchies.

* When validation rules, logging, metrics, or caching related to **object creation** need to be added, the factory struct provides a natural home for that logic.

  * ```go
    func NewEmployeeFactory(position string, annualIncome int) (*EmployeeFactory, error) {
    	if position == "" {
    		return nil, errors.New("position cannot be empty")
    	}
    	if annualIncome < 30_000 {
    		return nil, errors.New("annual income below minimum")
    	}
    
    	return &EmployeeFactory{
    		Position:     position,
    		AnnualIncome: annualIncome,
    	}, nil
    }
    
    func (f *EmployeeFactory) Create(name string) (*Employee, error) {
    	if name == "" {
    		return nil, errors.New("employee name cannot be empty")
    	}
    
    	return &Employee{
    		Name:         name,
    		Position:     f.Position,
    		AnnualIncome: f.AnnualIncome,
    	}, nil
    }
    ```

  * With functional factories, these concerns tend to leak into the closure or require rewriting the factory’s signature, increasing cognitive load and coupling.

    * "leak into the closure" means "end up inside the returned anonymous function, because there is nowhere else to put them."

    ```go
    func NewEmployeeFactory(
    	position string,
    	annualIncome int,
    ) (func(name string) (*Employee, error), error) {
    
    	// validate factory configuration once
    	if position == "" {
    		return nil, errors.New("position cannot be empty")
    	}
    	if annualIncome < 30_000 {
    		return nil, errors.New("annual income below minimum")
    	}
    
    	return func(name string) (*Employee, error) {
    		// validate per-employee input
    		if name == "" {
    			return nil, errors.New("employee name cannot be empty")
    		}
    
    		return &Employee{
    			Name:         name,
    			Position:     position,
    			AnnualIncome: annualIncome,
    		}, nil
    	}, nil
    }
    ```

### Prototype factory

A Prototype Factory creates new objects by copying (cloning) preconfigured prototype instances, instead of constructing them from scratch each time.

Given

```go
package factories

import "fmt"

type Employee struct {
  Name, Position string
  AnnualIncome int
}
```

We can define the preconfigured prototype instances

```go
const (
  Developer = iota
  Manager
)

var prototypes = map[int]Employee{
	Developer: {"", "Developer", 60000},
	Manager:   {"", "Manager", 80000},
}

func NewEmployee(role int) *Employee {
	p, ok := prototypes[role]
	if !ok {
		panic("unsupported role")
	}
	return &p // copy
}
```

* Using constants:
  - Prevents magic numbers
  - Makes valid options explicit
  - Centralizes the list of supported variants

So the usage:

```go
func main() {
  m := NewEmployee(Manager)
  m.Name = "Sam"
  fmt.Println(m)
}
```

## Go-Idiomatic Alternatives

* [Functional Options](98%20Go-Idiomatic%20patterns.md#functional-options): Represent optional creation rules as functions that are applied during factory execution, enabling flexible configuration without multiplying factory functions.

## Known Uses

- **Go standard library (`net/http`)**: Factory functions create fully initialized HTTP objects while applying internal defaults.

  - `http.NewRequest`

    ```
    req, err := http.NewRequest("GET", "https://example.com", nil)
    if err != nil { /* handle */ }
    
    req.Header.Set("User-Agent", "MyClient/1.0")
    req.Header.Set("Accept", "application/json")
    req = req.WithContext(ctx) // staged, incremental configuration
    
    resp, err := http.DefaultClient.Do(req) // final usage
    ```

  - `http.NewServeMux()`

    ```
    mux := http.NewServeMux()
    mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
      w.Write([]byte("hello"))
    })
    ```

  - Factory, not builder: `http.NewRequest` and `http.NewServeMux` return fully constructed, immediately usable objects in a single call; subsequent method calls mutate runtime state rather than perform stepwise construction, which disqualifies them from being Builder patterns.

- **Go standard library (`log`)**: `log.New` acts as a factory that returns a configured logger without exposing its internal setup.

  ```go
  logger := log.New(os.Stdout, "[api] ", log.LstdFlags|log.Lshortfile)
  logger.Println("service started")
  ```

- **Docker (`moby/moby`)**: Client constructors act as factories that assemble complex runtime objects from configuration and defaults.

  ```go
  cli, err := client.NewClientWithOpts(
    client.FromEnv,
    client.WithAPIVersionNegotiation(),
  )
  if err != nil {
    log.Fatal(err)
  }
  ```

- **Kubernetes (`client-go`)**: Factory-style functions centralize validation and setup of API clients.

  ```go
  config, err := rest.InClusterConfig()
  if err != nil {
    log.Fatal(err)
  }
  
  clientset, err := kubernetes.NewForConfig(config)
  if err != nil {
    log.Fatal(err)
  }
  ```

- **gRPC-Go (`google.golang.org/grpc`)**: Factory functions materialize ready-to-use servers and connections from declarative options.

  ```go
  server := grpc.NewServer(
    grpc.MaxRecvMsgSize(1024 * 1024),
  )
  
  conn, err := grpc.Dial(
    "localhost:50051",
    grpc.WithInsecure(),
  )
  if err != nil {
    log.Fatal(err)
  }
  ```
