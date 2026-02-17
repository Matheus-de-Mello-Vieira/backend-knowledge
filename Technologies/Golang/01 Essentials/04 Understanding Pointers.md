# Understanding Points

Variables that store value addresses instead of values

| **Symbol**            | **Meaning**           | **Example**  | **Description**                                     |
| --------------------- | --------------------- | ------------ | --------------------------------------------------- |
| `&`                   | "address of"          | `p := &x`    | Gives the memory address of variable `x`            |
| `*` (in use)          | "dereference"         | `v := *p`    | Reads the value stored at the address in `p`        |
| `*` (in type)         | "pointer to"          | `var p *int` | Declares `p` as a pointer to an `int` type          |
| `*` (assignment) | "indirect assign" | `*u = p`     | Updates the value at address `u` with value `p` |

## Why pointers

*   Avoid unnecessary value copies
    *   Go creates a copy when passing values to functions.
    *   For very large and complex values, this may take up too much memory space unnecessarily
    *   With pointers, only one value is stored in memory - and the address is passes around.
*   Directly mutate values
    *   Pass a pointer instead of a value to a function
        *   The function can then directly edit the underlying value - no return value is required
        *   Can lead to less code - but also to less understandable code or unexpected behaviors.

### Writing code without Pointers

```go
func main() {
    age := 32 // regular variable

    fmt.Println("Age:", age)

    adultYears := getAdultYears(age)
    fmt.Println(adultYears)
}

func getAdultYears(age int) int {
    return age - 18
}
```

### Creating a pointer

```go
func main() {
	age := 32 // regular variable

	var agePointer *int

	agePointer = &age
	fmt.Println("Age:", age) # 32
	fmt.Println("Age Pointer:", agePointer) # 0xc0000a0040
	fmt.Println("Age:", *agePointer) # 32

	getAdultYears(agePointer)
	fmt.Println(age) # 14
}

func getAdultYears(age *int) {
	*age -= 18
}
```

Caveat: a integer is a super duper small variable, so it doesn't worth all the fuss of working with pointers to avoid its copy.  

## Pointer's Null Value

All values in Go have a so-called **"Null Value"** - i.e., the value that's set as a default if no value is assigned to a variable.

*   For example, the null value of an `int` variable is `0`. Of a `float64`, it would be `0.0`. Of a `string`, it's `""`.

For a pointer, it's `nil` - a special value built-into Go.

*   `nil` represents the absence of an address value - i.e., a pointer pointing at no address / no value in memory.

## Common pitfalls

### Reassigning the Pointer Parameter

**The Scenario**
You pass a pointer to a function intending to modify the object it points to. However, inside the function, you use the assignment operator (`=`) directly on the pointer variable.

**The Code**

```go
package main

import "fmt"

type User struct{
    Name string
}

func changeUser(u *User) {
    // ❌ ERROR: This only reassigns the local pointer 'u'
    // It does NOT change the original 'user' in main
    u = &User{Name: "John"} 
}

func main() {
    var user = User{Name: "Alex"}

    changeUser(&user)

    fmt.Println(user.Name) // Output is still "Alex"
}

```

**Why this fails**
In Go, everything is passed by value—including pointers.

1. When you call `changeUser`, Go creates a **copy** of the pointer address. Let's call the original `user_ptr` and the copy `u`.
2. When you execute `u = &User{...}`, you are telling the **local copy** `u` to point to a new address (where "John" is).
3. The original `user_ptr` in `main` remains untouched, still pointing to "Alex".

**The Fix: Two Correct Approaches**

There are two ways to successfully modify the data, depending on your goal:

**Option A: The Full Overwrite (`*u = ...`)**
If you want to completely replace the object at that address with a new one.

```go
func changeUser(u *User) {
    // Dereference the pointer to overwrite the ENTIRE struct at that address
    *u = User{Name: "John"}
}

```

* **What it does:** It takes the value `User{Name: "John"}` and stuffs it into the memory slot `u` points to.
* **Use case:** Resetting a state or completely replacing an object.

**Option B: The Field Update (`u.Name = ...`)**
If you only want to update specific fields within the existing object.

```go
func changeUser(u *User) {
    // Go automatically dereferences pointers for struct fields
    // This is syntactic sugar for (*u).Name = "John"
    u.Name = "John"
}

```

* **What it does:** It follows the pointer to the struct and only changes the `Name` field, leaving other fields (if any existed) untouched.
* **Use case:** Updating specific properties without creating a whole new struct.

**Important: The "Nil Pointer" Trap**

When you switch from the "Wrong" code to the "Correct" code, you introduce a new risk: **Panics**.

* **The Wrong Way (`u = &User{...}`)**: If you pass `nil` to this function, it is safe. It just assigns a local variable. No crash.
* **The Right Ways (`*u = ...` and `u.Name = ...`)**: If you pass `nil` to these functions, **the program will crash (panic)**.

**Best Practice:** Always check if the pointer is `nil` before using these fixes.

```go
func changeUser(u *User) {
    if u == nil {
        return // or handle error
    }
    *u = User{Name: "John"}
}

```