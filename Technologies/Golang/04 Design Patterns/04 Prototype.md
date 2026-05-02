# Prototype

> A partially or fully initialized object that you copy (clone) and make use of.

## Motivation

- **Problem**: Complex structs often require expensive or error-prone initialization (defaults, derived fields, nested state), making repeated construction via constructors verbose and fragile.
- **Problem**: Small variations of an object (e.g., per-request or per-environment tweaks) lead to constructor explosion or ad-hoc mutation logic scattered across the codebase.
- **Problem**: Clients may need to create new instances without knowing the concrete type, but Go lacks implicit copy semantics or virtual constructors.
- **Why Prototype Helps**: A fully initialized instance serves as a template, allowing new objects to be created by cloning rather than rebuilding state from scratch.
- **Constraint (Go-specific)**: When value semantics can be used (small structs, clear ownership), plain assignment already provides safe copying and Prototype is unnecessary.

  **Why Prototype Helps**: When pointer-based sharing is unavoidable or copying semantics must be explicit, a fully initialized instance serves as a template that can be safely cloned.
- **Technical Benefit**: Cloning centralizes copy semantics, making object creation predictable, testable, and decoupled from initialization logic.
- **Go-Specific Fit**: Because Go favors explicitness, a `Clone` method makes copying intent clear and avoids accidental shallow copies of complex structs.

## Sample code

```go
type Address struct {
    StreetAddress, City, Country string
}

func (a *Address) Clone() *Address {
    if a == nil {
        return nil
    }
    cp := *a
    return &cp
}

type Person struct {
    Name    string
    Address *Address
}

func (p *Person) Clone() *Person {
    if p == nil {
        return nil
    }
    cp := *p
    cp.Address = p.Address.Clone()
    return &cp
}
```

Usage

```go
// define a fully initialized prototype
britishPrototype := &Person{
    Name: "",
    Address: &Address{
        StreetAddress: "221B Baker St",
        City:          "London",
        Country:       "UK",
    },
}

// create independent instances by cloning
john := britishPrototype.Clone()
john.Name = "John Watson"
john.Address.StreetAddress = "10 Downing St"

jane := britishPrototype.Clone()
jane.Name = "Jane Smith"
jane.Address.StreetAddress = "42 Fleet St"
```

## Consequences

- **Reduced construction complexity**: Objects are created by cloning a fully initialized prototype, avoiding repetitive and error-prone setup logic.
- **Explicit copy semantics**: A `Clone` method makes deep-copy behavior intentional and reviewable, preventing accidental shallow copies.
- **Controlled customization**: Variations are applied in a small, well-defined function, limiting where and how mutations can occur.
- **Improved consistency**: All instances derived from a prototype share the same defaults and invariants.
- **Better encapsulation**: Copy logic is localized to the types that own the data, reducing coupling between components.
- **Increased maintenance cost**: Each reference-like field requires deliberate cloning logic, which must be updated as the object graph evolves.
- **Potential performance overhead**: Deep copying can be more expensive than direct construction for simple or short-lived objects.
- **Clearer intent than constructors**: Cloning communicates “copy and specialize” semantics more accurately than overloaded `NewX` functions.

## Implementation

### Deep Copy

When working with structs that contain pointer fields, Go’s default copy behavior can easily introduce subtle bugs. At first glance, assigning one struct to another looks like a full copy, but this is only true for value fields.

```go
john := Person{
    "John",
    &Address{"123 London Rd", "London", "UK"},
}

jane := john
jane.Name = "Jane"
jane.Address.StreetAddress = "321 Baker St"

fmt.Println(john, john.Address) // {John 0xADDR} &{321 Baker St London UK}
fmt.Println(jane, jane.Address) // {Jane 0xADDR} &{321 Baker St London UK}
```

The problem here is that the assignment `jane := john` performs a **shallow copy**. While `Name` is copied correctly, the `Address` field is a pointer, so both `john` and `jane` end up referencing the same `Address` instance. As a result, modifying `jane.Address` also mutates `john.Address`, creating unintended shared state and hidden coupling between the two objects.

The correct approach is to perform a **deep copy**, ensuring that all referenced data is duplicated so each object is fully independent. In Go, this is best expressed explicitly, often via a `Clone` method following the Prototype pattern.

```go
func (p *Person) Clone() *Person {
    cp := *p // copy the struct
    if p.Address != nil {
        addrCopy := *p.Address
        cp.Address = &addrCopy
    }
    return &cp
}

jane := john.Clone()
jane.Name = "Jane"
jane.Address.StreetAddress = "321 Baker St"
```

With a deep copy in place, changes to `jane` no longer affect `john`. The cloning logic clearly documents the intended copy semantics, prevents accidental aliasing, and scales safely as the object graph becomes more complex. This is precisely the kind of problem the Prototype pattern addresses in Go.

### Nested cloning

As object graphs grow, deep-copy logic quickly becomes hard to maintain if it is centralized in a single `Clone` method. The earlier approach already shows the issue: `Person.Clone` must understand how to copy `Address`, creating tight coupling between types.

```go
func (p *Person) Clone() *Person {
    cp := *p
    if p.Address != nil {
        addrCopy := *p.Address
        cp.Address = &addrCopy
    }
    return &cp
}
```

This approach does not scale. Any change to `Address` (additional fields, nested pointers, slices, or maps) forces changes in `Person.Clone`, spreading copy logic and increasing the risk of shallow-copy bugs.

A better solution is **nested cloning**, where each type is responsible for cloning its own state.

```go
func (a *Address) Clone() *Address {
    if a == nil {
        return nil
    }
    cp := *a
    return &cp
}
```

With this in place, higher-level clones delegate instead of reimplementing copy logic:

```go
func (p *Person) Clone() *Person {
    if p == nil {
        return nil
    }
    cp := *p
    cp.Address = p.Address.Clone()
    return &cp
}
```

Nested cloning improves encapsulation, isolates change, and keeps deep-copy semantics explicit and local. In Go, this is the only sustainable way to apply the Prototype pattern once structs contain reference-like fields or grow beyond trivial depth.

### Copying slice fields

Slices require special care when cloning because copying the slice value only duplicates the header, not the underlying data. Whether `copy()` is sufficient or a per-element `Clone` is required depends entirely on the element type.

#### Slice of primitives

For slices of primitive or value-only types, allocating a new slice and using `copy()` produces a correct deep copy:

```go
type Person struct {
    Name string
    Tags []string
}

func (p *Person) Clone() *Person {
    if p == nil {
        return nil
    }
    cp := *p

    if p.Tags != nil {
        cp.Tags = make([]string, len(p.Tags))
        copy(cp.Tags, p.Tags)
    }

    return &cp
}
```

Each element is a value, so no shared state remains.

#### Slice of structs

Using `copy()` on a slice of structs is only safe if the struct is value-only and treated as atomic:

```go
type Address struct {
    Street  string
    City    string
    Country string
}

type Person struct {
    Addresses []Address
}
cp.Addresses = make([]Address, len(p.Addresses))
copy(cp.Addresses, p.Addresses)
```

This works *only* because `Address` contains no reference-like fields. The moment `Address` evolves, this code becomes subtly incorrect.

#### Slice of structs with their own clone logic

For types that are part of a prototype graph or may gain reference fields over time, each element should own its cloning logic and be cloned explicitly:

```go
cp.Addresses = make([]Address, len(p.Addresses))
for i := range p.Addresses {
    cp.Addresses[i] = p.Addresses[i].Clone()
}
```

### Copy through serialization

A generic way to achieve deep copy is to serialize an object and then deserialize it into a new instance. This approach works with encoders such as `encoding/json` and `encoding/gob`, and it guarantees that the resulting object graph does not share references with the original.

Both JSON and gob follow the same fundamental mechanism: flatten the object graph into bytes, then rebuild it from scratch.

**Using `encoding/json`**

```go
func CloneViaJSON[T any](src T) (T, error) {
    var dst T

    data, err := json.Marshal(src)
    if err != nil {
        return dst, err
    }

    err = json.Unmarshal(data, &dst)
    if err != nil {
        return dst, err
    }

    return dst, nil
}
```

- Text-based and human-readable
- Driven by struct tags and exported fields
- Loses concrete type information behind interfaces
- Slow and allocation-heavy

**Using `encoding/gob`**

```go
func CloneViaGob[T any](src T) (T, error) {
    var dst T

    var buf bytes.Buffer
    enc := gob.NewEncoder(&buf)
    dec := gob.NewDecoder(&buf)

    if err := enc.Encode(src); err != nil {
        return dst, err
    }

    if err := dec.Decode(&dst); err != nil {
        return dst, err
    }

    return dst, nil
}
```

- Binary and Go-specific
- Preserves concrete types (with registration for interfaces)
- Broader type coverage than JSON
- Still significantly slower than manual cloning

**What serialization-based copying guarantees**

- No shared memory between source and copy
- Deep copy across pointers, slices, and maps
- No accidental aliasing

**What it does not guarantee**

- Preservation of invariants enforced by constructors
- Copying of unexported fields
- Correct handling of runtime state (mutexes, channels, file handles)
- Compile-time safety (failures occur at runtime)

**When this approach makes sense**

- Tests and prototyping
- Rarely executed clone paths
- Extremely complex object graphs where explicit cloning is impractical

In Go, serialization-based copying should be treated as a **convenience technique**, not a primary implementation strategy:

- Prefer it in **tests, prototypes, or tooling**, where correctness is more important than performance and API clarity.
- Avoid it in **production paths**, hot code, or public APIs, where explicit `Clone` methods provide better performance, stronger guarantees, and clearer intent.

### Prototype Factory

This section is a complement to [Prototype factory](03%20Factories.md#Prototype%20factory), where will be used many utilities functions.

```go
func newPerson(proto *Person, name, street, city string) *Person {
	result := proto.Clone()
	result.Name = name
	result.Address.StreetAddress = street
	if city != "" {
		result.Address.City = city // optional override
	}
	return result
}

func NewBrazilianPerson(name, street, city string) *Person {
	return newPerson(&brazilianPrototype, name, street, city)
}

func NewBritishPerson(name, street, city string) *Person {
	return newPerson(&britishPrototype, name, street, city)
}

func main() {
	ana := NewBrazilianPerson("Ana", "Av. Paulista, 1000", "")         // keeps São Paulo
	oliver := NewBritishPerson("Oliver", "221B Baker St", "")          // keeps London
	liam := NewBritishPerson("Liam", "10 Downing St", "Manchester")    // overrides city

	fmt.Println(ana)
	fmt.Println(oliver)
	fmt.Println(liam)
}
```

* The core value of the Prototype pattern here is not just cloning, but making customization deliberate, constrained, and repeatable.
* Instead of letting callers freely clone a prototype and mutate it arbitrarily, customization is funneled through a small, well-defined function (`newPerson`)
* This achieves several things at once:
  - **Convenience**: Callers don’t need to understand the internal structure of the prototype or how deep copies are performed.
  - **Safety**: Only approved fields are customized; the rest of the prototype remains intact and consistent.
  - **Encapsulation**: Copying logic and mutation logic live together, preventing accidental shallow copies or incomplete initialization.
  - **Consistency**: Every instance derived from a prototype follows the same rules and defaults.

## Go-Idiomatic Alternatives

* [Functional Options](98%20Go-Idiomatic%20patterns.md#Functional%20Options): Prefer when you mostly need flexible configuration (not copying existing state) and want a single constructor without “constructor explosion.”

* **Plain constructors with explicit params**: Prefer when initialization is cheap and there are only a few stable variants; it keeps intent obvious and avoids copy semantics entirely.

* **Value semantics instead of pointers**: Prefer when nested data is small and owned by the parent; assignment then produces an independent copy and removes the need for Prototype entirely.

  ```go
  type Address struct {
      StreetAddress, City, Country string
  }
  
  type Person struct {
      Name    string
      Address Address // value, not *Address
  }
  ```

  With this design:

  ```
  p2 := p1 // full, independent copy
  ```

* **[Prototype Factory](#Prototype%20Factory) without public `Clone`**: Prefer when object creation is copy-based but cloning should remain an internal detail; the factory owns the prototypes, performs the copy, and applies controlled customization, keeping the public API small and preventing misuse.
