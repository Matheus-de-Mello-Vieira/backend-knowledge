# Understanding Points

Variables that store value addresses instead of values

| Symbol        | Meaning       | Example       | Description                           |
| ------------- | ------------- | ------------- | ------------------------------------- |
| `&`           | "address of"  | `p := &x`     | Gives the address of variable `x`     |
| `*` (in use)  | "dereference" | `value := *p` | Accesses the value pointed to by `p`  |
| `*` (in type) | "pointer to"  | `var p *int`  | Declares `p` as a pointer to an `int` |

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