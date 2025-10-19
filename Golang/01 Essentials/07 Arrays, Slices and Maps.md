# Arrays, Slices and Maps

## Arrays

You can declare a array with `4` slots with:

```go
prices := [4]float64{10.99, 9.99, 45.99, 20.0}

fmt.Println(prices) // [10.99 9.99 45.99 20]
```

*   ```go
    fmt.Println(prices[2]) // 45.99
    ```

*   ```go
    prices[1] = 4.3
    fmt.Println(prices) // [10.99 4.3 45.99 20]
    ```

For structs:

```go
products := []Product{
		{
			title: "Wireless Mouse",
			id:    101,
			price: 19.99,
		},
		{
			title: "Mechanical Keyboard",
			id:    102,
			price: 79.50,
		}}
```

Or, you can initialize the array with the nil values:

```go
var productNames [4]string // 4 empty strings
```

*   ```go
    productNames = [4]string{"A book"}
    fmt.Println(productNames) // [A book   ]
    ```

## Packing List values

In Go, a function can take a **variadic parameter**, which means it can accept *zero or more* arguments of the same type.

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

## `For` loops with arrays

```go
for index, value := range prices {
	fmt.Println(index, value)
}
```

```
0 10.99
1 9.99
2 45.99
3 20
```

## Slices

To get only part of a array:

```
prices := [4]float64{10.99, 9.99, 45.99, 20.0}
```

*  ```go
    fmt.Println(prices[1:3]) // [9.99 45.99]
    ```

*  ```go
    fmt.Println(prices[:3]) // [10.99 9.99 45.99]
    ```

*   ```go
    fmt.Println(prices[1:]) // [9.99 45.99 20]
    ```

*   You can't use negative indexes.

You can get a slice out of a another slice:

```go
featuredPrices := prices[1:]
highlightedPrices := featuredPrices[:1]

fmt.Println(highlightedPrices) // [9.99]
```

The slice is only a window on the original array, the slots are the same pointers:

```go
fmt.Println(prices) // [10.99 9.99 45.99 20]
highlightedPrices[0] = 199.99
fmt.Println(prices) // [10.99 199.99 45.99 20]
```

### `len` and `cap`

```go
fmt.Println(len(featuredPrices), cap(featuredPrices)) // 3 3
fmt.Println(len(highlightedPrices), cap(highlightedPrices)) // 1 3
```

*   On slices, the `cap` will get the maximum length the slice can reach when resliced

    *   if `v` is `nil`, `cap(v)` is zero

    *   the `featuredPrices` cuts only the beginning of the array, so `len == cap`

    *   the `highlightedPrices` cuts the end of the `featuredPrices`, so it can grow until the end of `featuredPrices` until it be resliced.

        *   It means:

            ```go
            prices := [4]float64{10.99, 9.99, 45.99, 20.0}
            
            featuredPrices := prices[1:]
            highlightedPrices := featuredPrices[:1]
            
            highlightedPrices = highlightedPrices[:3]
            fmt.Println(highlightedPrices) // [9.99 45.99 20]
            ```

        *   you can do it towards the end, but can't do it towards the beginning. 

### Building Dynamic Lists with Slices

To create a dynamic slice:

```go
prices := []float64{}
```

*   Or, with initial values:

    ```go
    prices := []float64{10.99, 9.99}
    ```


When the size of the dynamic list surpass it's `cap`, a bigger array is created, the data is copied and the old slice is ditched:

```go
for i := 0; i < 8; i++ {
    prices = append(prices, 45.99)
    fmt.Println(len(prices), cap(prices))
}
```

```
3 4
4 4
5 8
6 8
7 8
8 8
9 16
10 16
```

If you aren't absolutely sure that you would never need resize a array, always use dynamic slice from onset. 

### `Make function`

You can preallocate slots on the slice

```go
prices := make([]float64, 16)
```

It will create a slice with `16` slots with nil value (0).

```go
prices1 = append(prices, 4.3)

fmt.Println(prices1) // [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 4.3]
```

But you can assign the values using index:

```go
prices[0] = 3.2
```

You can pass a third parameter to define the maximum length the slice can reach when resliced:

```go
prices := make([]float64, 0, 16)

for i := 0; i < 8; i++ {
    prices = append(prices, 45.99)
    fmt.Println(len(prices), cap(prices))
}
```

```
1 16
2 16
3 16
4 16
5 16
6 16
7 16
8 16
```

It avoid unnecessary copies

## Maps

Maps are associative arrays

To create a map with key strings and values strings:

```go
websites := map[string]string{}
```

Or, with values:

```go
websites := map[string]string{
    "Google":              "https://google.com",
    "Amazon Web Services": "https://aws.amazon.com",
}
```

*   You can access a element with the key:

    ```go
    websites["Google"]
    ```

    *   If the key doesn't exists, it will return a nil value.

*   You can add more element:

    ```go
    websites["LinkedIn"] = "https://linkedin.com"
    ```

### Maps vs Structs

*   In maps, you can use anything as key
*   You don't need to predefine the keys of maps

### Making Maps

You can use of `make` for preallocate slots on a map:

```go
courseRatings = make(map[string]float64, 20)
```

This way you can place 20 items without memory reallocation. 

### Type Alias

`map` declarations can be a bit long, so you can use type alias:

```go
type floatMap map[string]float64
```

## `for` loops with map

```go
for key, value := range websites {
	fmt.Println(key, value)
}
```

```
Google https://google.com
Amazon Web Services https://aws.amazon.com
```

