# Arrays, Slices and Maps

Arrays, slices, and maps organize collections differently:

| Collection | Type example | Access | Assignment |
| --- | --- | --- | --- |
| Array | `[4]float64` | Integer index, fixed length | Copies all elements |
| Slice | `[]float64` | Integer index, variable-length view | Copies the view; shares backing elements |
| Map | `map[string]float64` | Unique key | Shares the same map entries |

Assignment copies values; it does not recursively clone objects referenced by their elements.

## Arrays

An array contains a fixed number of elements of one type. Its length is part of its type: `[4]float64` and `[5]float64` are different types.

```go
prices := [4]float64{10.99, 9.99, 45.99, 20.0}

fmt.Println(prices)    // [10.99 9.99 45.99 20]
fmt.Println(prices[2]) // 45.99

prices[1] = 4.3
fmt.Println(prices) // [10.99 4.3 45.99 20]
```

Indexes start at zero and must be smaller than the length. Both `len(prices)` and `cap(prices)` are four; an array does not grow through `append`.

### Initialization and copying

Elements not explicitly initialized receive their type's zero value:

```go
var productNames [4]string
fmt.Println(productNames) // [   ] — four empty strings

productNames = [4]string{"A book"}
fmt.Println(productNames) // [A book   ]
```

An [array value](../99%20Misc/Go%20Internals.md#Arrays) contains its elements, so assigning or passing the array copies those element values:

```go
A := [2]int{10, 20}
B := A
A[0] = 99

fmt.Println(A) // [99 20]
fmt.Println(B) // [10 20]
```

If an element contains a pointer, slice, or map, copying that element still preserves references to the objects it uses; it is not a recursive deep copy.

### Array and slice iteration

`range` yields each index and its element value in index order. The value variable is a copy of the element; assign through the index to replace the stored element.

```go
for index, value := range prices {
    fmt.Println(index, value)
}
```

The same loop form works for slices. Use `_` in place of the index when only the value is needed.

## Slices

A slice is a view into a contiguous part of an array, called its **backing array**. The type `[]T` denotes a slice of elements of type `T`; it does not fix the length in the type. A [slice value](../99%20Misc/Go%20Internals.md#Slices) describes the view rather than containing the elements themselves.

### Slicing arrays and slices

`values[low:high]` includes the element at `low` and excludes the element at `high`. Omitting `low` starts at zero; omitting `high` ends at the current length.

```go
prices := [4]float64{10.99, 9.99, 45.99, 20.0}

fmt.Println(prices[1:3]) // [9.99 45.99]
fmt.Println(prices[:3])  // [10.99 9.99 45.99]
fmt.Println(prices[1:])  // [9.99 45.99 20]
```

Slicing a slice creates another view of the same elements. Index zero in that view refers to its first selected element, not necessarily index zero in the original array:

```go
featuredPrices := prices[1:]
highlightedPrices := featuredPrices[:1]

fmt.Println(highlightedPrices) // [9.99]

highlightedPrices[0] = 199.99
fmt.Println(prices) // [10.99 199.99 45.99 20]
```

The assignment changes `featuredPrices[0]` and `prices[1]` because all three expressions refer to the same array element. Slice indexes are nonnegative and must be smaller than the slice's length.

### `len` and `cap`

A slice's visible elements and its room for growth are different:

- **Length (`len`):** The number of elements currently in the view.
- **Capacity (`cap`):** The maximum length the view can reach by reslicing without replacing its backing array. Capacity is measured from the view's starting position.

```go
fmt.Println(len(featuredPrices), cap(featuredPrices))     // 3 3
fmt.Println(len(highlightedPrices), cap(highlightedPrices)) // 1 3
```

Both slices start at the original array's second element. `featuredPrices` includes all three remaining elements; `highlightedPrices` includes only one but still has room to expose the other two.

Reslicing extends the view without adding or copying elements:

```go
highlightedPrices = highlightedPrices[:3]
fmt.Println(highlightedPrices) // [199.99 45.99 20]
```

- The end of a resliced view must not exceed its capacity.
- Reslicing cannot reach backward before the view's current starting position.
- Increasing length by reslicing exposes existing elements; it does not initialize them again.

### Slice assignment and shared elements

`B := A` copies A's view, not its backing array. The variables have independent lengths and capacities but initially share the same elements.

```go
A := []int{10, 20}
B := A

A[0] = 99
fmt.Println(B) // [99 20]

A = A[:1]
fmt.Println(A) // [99]
fmt.Println(B) // [99 20]
```

- **Element assignment (`A[0] = 99`):** Changes the shared backing element, so B observes it.
- **Slice assignment (`A = A[:1]`):** Changes only A's view; B's length and capacity remain unchanged.

### Creating slices with literals and `make`

A slice literal supplies initial elements. Unlike an array literal, its type has no fixed length:

```go
type Product struct {
    Title string
    ID    int
    Price float64
}

products := []Product{
    {Title: "Wireless Mouse", ID: 101, Price: 19.99},
    {Title: "Mechanical Keyboard", ID: 102, Price: 79.50},
}
fmt.Println(len(products)) // 2
```

`make` creates a slice with a chosen length and optional capacity:

- **`make([]T, length)`:** Length and capacity are equal; the elements contain the zero value of `T`.
- **`make([]T, length, capacity)`:** Reserves backing space beyond the initial length. Length must not exceed capacity.

```go
prices := make([]float64, 16)
prices[0] = 3.2
fmt.Println(len(prices), cap(prices)) // 16 16
```

These sixteen elements already belong to the slice. Appending adds an element after them, not into an unused position within its length:

```go
prices = append(prices, 4.3)
fmt.Println(len(prices)) // 17
fmt.Println(prices[16])  // 4.3
```

> [!note] Nil and empty slices
> `var prices []float64` is nil and has length and capacity zero. `[]float64{}` is empty but non-nil. Both accept `append`.

### Building Dynamic Lists with Slices

Use slices when the number of elements needs to change. `append` returns the resulting slice, so assign its result to keep the updated view:

```go
prices := []float64{10.99, 9.99}
prices = append(prices, 45.99)
fmt.Println(prices) // [10.99 9.99 45.99]
```

Capacity determines whether the resulting slice still shares its old backing array:

- **Enough capacity:** `append` writes the new elements into the existing array and returns a longer view.
- **Insufficient capacity:** `append` allocates a larger array, copies the existing elements, adds the new ones, and returns a view of the new array.

In both cases, assigning the result to A leaves B's length and capacity unchanged. With spare capacity, the elements remain shared and reslicing B exposes the appended value:

```go
A := make([]int, 2, 3)
A[0], A[1] = 10, 20
B := A

A = append(A, 30)
A[0] = 99

fmt.Println(A)     // [99 20 30]
fmt.Println(B)     // [99 20]
fmt.Println(B[:3]) // [99 20 30]
```

Without spare capacity, A's returned slice uses a different array. Later assignments to A's integer elements no longer affect B:

```go
A := []int{10, 20} // length 2, capacity 2
B := A

A = append(A, 30)
A[0] = 99

fmt.Println(A) // [99 20 30]
fmt.Println(B) // [10 20]
```

To avoid reallocating during expected growth, start with length zero and reserve capacity:

```go
prices := make([]float64, 0, 16)
for i := 0; i < 8; i++ {
    prices = append(prices, 45.99)
    fmt.Println(len(prices), cap(prices))
}
```

The length increases from one to eight while capacity stays sixteen. Capacity is not a maximum list size: appending beyond it requests a larger array.

> [!warning] Shared storage and growth
> Appending to a shorter slice can overwrite elements visible through a longer slice of the same array. Do not assume append isolates a slice, and do not rely on capacity doubling or any particular growth sequence.
>
> `append` starts writing immediately after the shorter slice's length. If capacity suffices, it reuses the array even when another slice already includes those positions:
>
> ```go
> B := []int{10, 20, 30}
> A := B[:2] // length 2, capacity 3
>
> A = append(A, 99) // overwrites the shared element at index 2
>
> fmt.Println(A) // [10 20 99]
> fmt.Println(B) // [10 20 99] — the previous 30 was overwritten
> ```
>
> If the append requires a new backing array, B's elements remain unchanged.

### Copying elements into independent storage

Assignment and `copy` are different operations. To separate the backing arrays, first create a destination with enough length, then copy the elements:

```go
A := []int{10, 20}
B := make([]int, len(A))
copied := copy(B, A)
A[0] = 99

fmt.Println(copied, B) // 2 [10 20]
```

`copy` returns the number of elements copied, limited by the smaller of the two lengths. Reserved capacity alone does not create destination elements. The operation copies element values; [cloning referenced state](../04%20Design%20Patterns/04%20Prototype.md#Copying%20slice%20fields) requires additional work when those elements contain pointers, slices, or maps.

## Maps

A map associates unique keys of one type with values of another: `map[K]V`. It supports lookup by key rather than by position.

- **Maps:** Suit collections whose keys are supplied at runtime. Keys are not predefined fields.
- **Structs:** Suit records with named fields fixed by their type; different fields can have different types.

Map keys must support equality comparison. Strings and integers are common choices; slices, maps, and functions are not valid key types. An interface key containing a non-comparable dynamic value causes a runtime panic.

### Creation and size hints

A literal creates an initialized map, either empty or with initial entries:

```go
emptyWebsites := map[string]string{}
websites := map[string]string{
    "Google": "https://google.com",
    "Amazon Web Services": "https://aws.amazon.com",
}
fmt.Println(len(emptyWebsites), len(websites)) // 0 2
```

`make` creates an initialized map and accepts an optional initial size hint:

```go
courseRatings := make(map[string]float64, 20)
fmt.Println(len(courseRatings)) // 0
```

The hint does not insert entries, impose a maximum size, or guarantee twenty insertions without allocation. It guides the initial sizing of [runtime map storage](../99%20Misc/Go%20Internals.md#Maps).

> [!warning] Nil maps
> `var websites map[string]string` is nil. Reads return the value type's zero value and `len` returns zero, but inserting an entry panics. Initialize the map with a literal or `make` before writing.

### Lookup, insertion, and deletion

Indexing reads a value; assigning through a key inserts or replaces it. A missing key returns the value type's zero value, not necessarily nil:

```go
websites := map[string]string{"Google": "https://google.com"}
fmt.Println(websites["Google"])  // https://google.com
fmt.Println(websites["Missing"]) // an empty string

value, exists := websites["Missing"]
fmt.Println(value == "", exists) // true false

websites["LinkedIn"] = "https://linkedin.com"
delete(websites, "Google")
```

Use the two-result form to distinguish an absent key from a stored zero value. Deleting a missing key is a no-op.

### Map assignment and shared entries

Assigning or passing a map does not copy its entries. Both values refer to the same map:

```go
A := map[string]int{"score": 10}
B := A
A["score"] = 99
fmt.Println(B["score"]) // 99

A = make(map[string]int)
fmt.Println(len(A), B["score"]) // 0 99
```

Updating an entry affects shared map contents; assigning a different map to A changes only what A refers to.

### Map iteration

`range` yields each key and value. Order is unspecified and need not be the same across iterations; the loop below does not promise which website prints first.

```go
for key, value := range websites {
    fmt.Println(key, value)
}
```

When the map changes during the same iteration:

- **Deletion:** An entry deleted before being reached is not returned.
- **Insertion:** A new entry may be returned or skipped.
- **Modification:** A modified entry that is subsequently returned exposes its latest value.

Growth must not cause an entry to be returned twice. These rules describe changes during iteration, not permission for unsynchronized access from multiple goroutines.

> [!warning] Concurrent access
> Concurrent accesses to the same map require synchronization when any access writes. Runtime detection of some unsafe accesses does not make map operations synchronized.

### Named map types and aliases

A type definition gives a map a distinct type name:

```go
type floatMap map[string]float64
ratings := floatMap{"Go": 4.5}
fmt.Println(ratings["Go"]) // 4.5
```

An alias uses `=` and names the same type rather than defining a new one:

```go
type RatingMap = map[string]float64
```
