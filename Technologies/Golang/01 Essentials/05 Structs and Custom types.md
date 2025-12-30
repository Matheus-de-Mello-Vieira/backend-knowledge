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

```go
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

#### Multiple Embedding and Selector Ambiguity in Go

Go’s struct embedding feature promotes fields and methods from embedded structs, allowing them to be accessed as if they were defined directly on the outer struct. This works well as long as there is no conflict. Problems arise when a struct embeds **multiple structs that expose the same exported field or method name**, because Go has no rule for automatically choosing one over the other.

Consider the following example:

```go
type Person struct {
	Name string
}

type Customer struct {
	Name string
}

type Employee struct {
	Person
	Customer
}

func main() {
	e := Employee{
		Person:   Person{Name: "Alice"},
		Customer: Customer{Name: "Bob"},
	}

	// fmt.Println(e.Name) // ❌ compile-time error: ambiguous selector e.Name
}
```

Both `Person` and `Customer` promote a `Name` field into `Employee`. When you write `e.Name`, the compiler sees two equally valid candidates at the same embedding depth and reports an **ambiguous selector** error. This is not a runtime issue—Go catches it at compile time to prevent unclear or fragile code.

The same rule applies to methods:

```go
type Person struct{}
func (Person) Greet() { fmt.Println("Hello from Person") }

type Customer struct{}
func (Customer) Greet() { fmt.Println("Hello from Customer") }

type Employee struct {
	Person
	Customer
}

func main() {
	var e Employee
	// e.Greet() // ❌ ambiguous selector e.Greet
}
```

Again, the compiler refuses to guess which `Greet` method should be called.

Selector ambiguity is not a limitation of Go; it is a deliberate design choice. Go favors explicitness and predictability over complex resolution rules. When multiple embedded structs expose the same API, the compiler forces you to clarify your intent—either by qualifying access or by reconsidering whether embedding is the right modeling tool in that situation.

##### How to resolve or avoid the problem

1. **Explicit qualification (most common solution)**
   Access the field or method through the embedded struct:

   ```go
   fmt.Println(e.Person.Name)
   fmt.Println(e.Customer.Name)
   
   e.Person.Greet()
   e.Customer.Greet()
   ```

2. **Avoid embedding when concepts overlap**
   If both embedded types represent distinct roles, prefer named fields:

   ```go
   type Employee struct {
       person   Person
       customer Customer
   }
   ```

   This removes promotion entirely and makes access explicit by design.

3. **Define a field or method on the outer struct**
   If `Employee` should expose a single “canonical” name or behavior, define it directly:

   ```go
   type Employee struct {
       Person
       Customer
   }
   
   func (e Employee) Name() string {
       return e.Person.Name
   }
   ```

   This resolves ambiguity and documents intent.

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

### Single-Method Interface Adapters via Function Types

It is common to see interfaces in Go that expose a **single, behavior-focused method**. In these cases, you can create implementations **without declaring verbose structs** by adapting a plain function to satisfy the interface.

```go
type Client interface {
	Do(req string) error
}
```

Instead of defining a struct type and a method, you can declare a **named function type** whose signature matches the interface method and, by attaching a method to that function type, turn it into a valid implementation of the interface.

```go
type clientFunc func(string) error

func (f clientFunc) Do(req string) error {
	return f(req)
}
```

At this point, any function with the appropriate signature can be used as a `Client`.

```go
func send(req string) error {
	println("sending:", req)
	return nil
}

var c Client = clientFunc(send)
c.Do("ping")
```

This approach provides a **lightweight interface adapter**:

- It avoids boilerplate struct declarations.
- It keeps the behavior local to the function itself.
- It is idiomatic for narrow, single-method interfaces.

The trade-off is structural: once the interface grows beyond one method or requires explicit state, this technique stops scaling and a struct-based implementation becomes the clearer choice.
