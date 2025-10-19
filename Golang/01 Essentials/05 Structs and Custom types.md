# Structs & Custom Types

Go is not a “pure” object-oriented language — it doesn’t have classes or inheritance.
However, it does support many OOP concepts like:

*   Encapsulation
*   Composition (instead of inheritance)
*   Polymorphism (via interfaces)

So you can write clean, modular, object-oriented-style code in Go, just using different constructs.

## Structs

In Go, instead of *classes*, you use structs to define data types, and methods attached to them.

```go
package main

import "fmt"

type User struct {
    Name  string
    Email string
}

// Method with receiver
func (u User) Greet() {
    fmt.Printf("Hello, %s!\n", u.Name)
}

func main() {
    user := User{Name: "Alice", Email: "alice@example.com"}
    user.Greet() // Output: Hello, Alice!
}
```

*   Alternatively, you can declare:

    ```go
    user := User{"Alice", "alice@example.com"}
    ```

    Paying attention on the order of the parameters.

### Encapsulation

Go controls visibility using **uppercase/lowercase naming**:

-   **Exported (public)** → Starts with an uppercase letter.
-   **Unexported (private)** → Starts with a lowercase letter.

```go
type account struct {
    balance float64
}

func (a *account) Deposit(amount float64) {
    a.balance += amount
}

func (a *account) Balance() float64 {
    return a.balance
}
```

### Passing struct values as arguments

```go
type User struct {
	Name  string
	Email string
}

func main() {
	user := User{"Alice", "alice@example.com"}
	printEmail(user)
}

func printEmail(user User) { // copying user
	fmt.Println(user.Email)
}
```

To avoid the copying, you can pass a pointer:

```go
func main() {
	user := User{"Alice", "alice@example.com"}
	printEmail(&user)
}

func printEmail(user *User) {
	fmt.Println(user.Email)
}
```

That’s just a *standalone* function — it doesn’t “belong” to anything.

### Function

```go
func (a *account) Deposit(amount float64) {
    a.balance += amount
}
```

Now it’s a **method** — a function *associated with the type* `account`.
 The part before the function name — `(a *account)` — is called the **receiver**.

So you can call it like this:

```go
acc := account{}
acc.Deposit(100)
```

Instead of:

```go
Deposit(&acc, 100)
```

You can choose between **value receivers** or **pointer receivers** depending on whether you want to modify the original object.

| Type                 | Syntax                           | Behavior                                  |
| -------------------- | -------------------------------- | ----------------------------------------- |
| **Value Receiver**   | `func (a account) Deposit(...)`  | Works on a (shallow) *copy* of the struct |
| **Pointer Receiver** | `func (a *account) Deposit(...)` | Modifies the *original* struct            |

#### Value Receivers

When you use:

```go
func (a Account) Deposit(amount float64)
```

Go (shallowly) copies the entire struct when the method is called.

That means:

-   Any changes you make inside the method affect **only that copy**.
-   The original struct remains unchanged.
-   This can be **expensive** if your struct is large (because every call duplicates data).

**Caveat:** Even if you *don’t* modify the struct, using value receivers for large structs can hurt performance due to copying.

Use for:

-   Small, immutable structs.
-   Read-only helper methods (e.g., `Display()`, `ToString()`).

####  Pointer Receivers

When you use:

```
func (a *Account) Deposit(amount float64)
```

Go passes the **memory address**, not a copy.

So:

-   You can modify the original struct directly.
-   No extra copying happens — good for performance.
-   But you must be careful about **nil pointer** cases.

Go makes method calls look simple by automatically taking the address when needed:

```go
a := Account{}
a.Deposit(100) // Works even if Deposit has a pointer receiver!
```

The compiler silently does:

```go
(&a).Deposit(100)
```

**Caveat:** Calling a pointer receiver on a `nil` pointer will **panic** if you try to access fields inside it.

*   Example:

    ```go
    var a *Account
    a.Deposit(100) // panic if Deposit dereferences fields
    ```
   
    * It happens because go automatically converts it to `(&a).Deposit(100)`

Use for:

-   Methods that mutate state.
-   Large structs (to avoid copies).
-   Methods that must satisfy an interface using pointer receivers.

### Constructor Functions Pattern

There is no build-in constructors in go, but normally is made standalone factory functions

```go
func newUser(name, email string) User {
	return User{
		Name: name,
		Email: email,
	}
}
```

Or, returning a pointer:

```go
func newUser(name, email string) *User {
	return &User{
		Name:  name,
		Email: email,
	}
}
```

#### advantageous

##### validation:

```go
func newUser(name, email string) (*User, error) {
	name = strings.TrimSpace(name)
	email = strings.TrimSpace(email)

	if name == "" {
		return nil, errors.New("name cannot be empty")
	}

	// Simple email validation using regex
	emailRegex := `^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$`
	matched, _ := regexp.MatchString(emailRegex, email)
	if !matched {
		return nil, errors.New("invalid email address")
	}

	return &User{
		Name:  name,
		Email: email,
	}, nil
}
```
If you don't want return a pointer:

```
func newUser(name, email string) (User, error) {
	...
	if name == "" {
		return User{}, errors.New("name cannot be empty")
	}
    ...
    
    return User{
		Name:  name,
		Email: email,
	}, nil
}
```



#### access from other packages

Imagine the situation:

*   `user/user.go`

    ```go
    package user
    
    type User struct {
    	name  string
    	email string
    }
    ```

*   `main.go`

    ```go
    import (
    	"example.com/user"
    )
    
    func main() {
    	user := user.User{name: "Alice", email: "alice@example.com"} // ❌ Error: cannot refer to unexported field name in struct literal of type user.User
    }
    ```
    

That error happens because 'name' isn't capitalized, so it can't be settled from another package.

To solve it, you can:

*   Make those attributes public:

    ```go
    type User struct {
    	Name  string
    	Email string
    }
    ```

*   Create a constructor

    *   `user/user.go`

        ```go
        type User struct {
        	name  string
        	email string
        }
        
        func New(name, email string) *User {
        	return &User{name: name, email: email}
        }
        ```

    *   `main.go`

        ```go
        package main
        
        import (
        	"example.com/user"
        )
        
        func main() {
        	user := user.New("Alice", "alice@example.com")
        }
        ```

    *   By convention, you should name the constructor function as `New

### Embedding

In Go, struct embedding lets one struct include another directly, without giving it a field name.

*   This provides automatic promotion of fields and methods — effectively letting you “inherit” behavior, but in a simpler and more flexible way.

```go
package main

import "fmt"

type Person struct {
    Name string
}

func (p Person) Greet() {
    fmt.Println("Hello, my name is", p.Name)
}

type Employee struct {
    Person  // embedded struct (no field name)
    Company string
}

func main() {
    e := Employee{
        Person:  Person{Name: "Alice"},
        Company: "OpenAI",
    }

    // Accessing promoted field
    fmt.Println(e.Name) // from Person

    // Accessing promoted method
    e.Greet() // behaves as if Employee had Greet()
}
```

Internally:

*   `Employee` has an anonymous field of type `Person`.

*   Go automatically promotes its fields and methods to the outer type.

*   So when you write `e.Greet()`, Go translates it to:

    ```go
    e.Person.Greet()
    ```

### overriding

-   Methods of the embedded type are **promoted** to the embedding type **unless overridden**.
-   You can **override** a promoted method by defining a method with the same name on the outer struct.
-   You can still access the embedded one explicitly via `Outer.Inner.Method()`.

## Custom types

You can declare new types using `type`

```go
package main

import "fmt"

type str string

func (text str) log() {
	fmt.Println(text)
}

func main() {
	var name str = "Matheus"
	name.log()
}
```



## Immutability

Great question. Go doesn’t have language-level immutability, but you can design immutable types with a few disciplined patterns.

1.  Hide state (encapsulation)
    *   Keep fields **unexported** (lowercase).
    *   Provide a **constructor** and **getters** only.
    *   Offer “withers” that **return a new value** instead of mutating.

2.  Prefer **value semantics**
    *   Make your type small and copyable; use **value receivers**.
    	* be careful because it is a shallow copy 
    *   Avoid exposing pointers to internal state.

3.  **Defensive copies** for reference types
    *   Slices, maps, and pointers are mutable references.
    *   In the constructor: **copy inputs**.
    *   In getters: **return copies**, never the original.
    *   Internally: treat them as read-only.

3.  Expose **read-only interfaces**
    * Publish an interface with only getters/queries; keep the concrete type private.

4.  Separate I/O structs from domain models
    *   Use exported structs for JSON/db (mutable DTOs).
    *   Convert to an **internal immutable** domain type.

5.  Concurrency mindset
    * Prefer **share-nothing + message passing** (channels).
    
        * >   Don’t share memory to communicate; communicate to share memory.
        * Instead of multiple goroutines accessing the same variable, each goroutine *owns* its own data and communicates via **channels**.
    
    * For shared snapshots (e.g., config), replace the **entire immutable value** atomically (e.g., `atomic.Value`), not fields in place.
    
        ```go
        package main
        
        import (
            "fmt"
            "sync/atomic"
            "time"
        )
        
        type Config struct {
            Version int
            Features []string
        }
        
        var config atomic.Value // holds Config
        
        func loadInitialConfig() {
            cfg := Config{
                Version: 1,
                Features: []string{"A", "B"},
            }
            config.Store(cfg) // store immutable snapshot
        }
        
        func getConfig() Config {
            return config.Load().(Config) // readers get a copy by value
        }
        
        func updateConfig(newFeatures []string) {
            old := getConfig()
            // Create a new copy — don’t mutate the existing one
            cfg := Config{
                Version:  old.Version + 1,
                Features: append([]string(nil), newFeatures...), // copy slice
            }
            config.Store(cfg) // atomically replace snapshot
        }
        
        func main() {
            loadInitialConfig()
        
            // Reader goroutine
            go func() {
                for {
                    cfg := getConfig()
                    fmt.Println("Reader sees config:", cfg)
                    time.Sleep(500 * time.Millisecond)
                }
            }()
        
            // Writer goroutine updates config safely
            go func() {
                for i := 2; i <= 3; i++ {
                    time.Sleep(1 * time.Second)
                    updateConfig([]string{"A", "B", fmt.Sprint("New-", i)})
                }
            }()
        
            time.Sleep(3 * time.Second)
        }
        ```
    
        *   `atomic.Value` ensures **atomic replacement** of the whole config struct.
        *   Readers always get a **consistent snapshot** — no locks, no partial updates.
        *   The config struct is **immutable**: readers can safely use it without worrying that it will change underneath them.