# Functions deep dive

## Functions as values / types

```go
package main

import "fmt"

func main() {
	numbers := []int{1, 5, 2}
	
	doubled := transformNumbers(&numbers, double)
	tripled := transformNumbers(&numbers, triple)

	fmt.Println(doubled)
	fmt.Println(tripled)
}

func transformNumbers(numbers *[]int, transform func(int)int) []int {
	results := make([]int, len(*numbers))

	for index, value := range *numbers {
		results[index] = transform(value)
	}

	return results
}

func double(number int) int {
	return number * 2
}
func triple(number int) int {
	return number * 3
}
```

You can put it on a custom type:

```go
type transformFn func(int) int
```

*   It is useful for more complex function signatures.

## Anonymous function

```go
quadrupled := transformNumbers(&numbers, func(number int) int {
	return number * 4
})
```

### Closure

Produce functions with functions:

```go
func createTransformer(factor int) func(int) int {
	return func(number int) int {
		return number * factor
	}
}
```

## Variadic Functions



In Go, a function can take a variadic (/ˌvɛəriˈædɪk/) parameter, which means it can accept *zero or more* arguments of the same type.

```go
func sum(nums ...int) int {
    total := 0
    for _, n := range nums {
        total += n
    }
    return total
}
```

## Unpacking List Values

```go
numbers := []int{1, 2, 3}
fmt.Println(sum(numbers...)) 
```

#### Works only with variadic functions

This unpacking (`...`) **only works** for functions that declare their last parameter as variadic — like `func foo(args ...T)`.

For example:

```
func printAll(args ...string) {
    for _, s := range args {
        fmt.Println(s)
    }
}

names := []string{"Alice", "Bob", "Charlie"}
printAll(names...) // ✅ works
```

But not:

```
func printTwo(a, b string) { fmt.Println(a, b) }

args := []string{"hi", "there"}
printTwo(args...) // ❌ ERROR
```

Go doesn’t support unpacking into *non-variadic fixed parameters*.