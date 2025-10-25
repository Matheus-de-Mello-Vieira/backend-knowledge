# JSON

## Demo context

We will use the API `https://jsonplaceholder.typicode.com/`

Where:

*   `GET todos/`

    ```json
    [
       {
          "userId":1,
          "id":1,
          "title":"delectus aut autem",
          "completed":false
       },
       {
          "userId":1,
          "id":2,
          "title":"quis ut nam facilis et officia qui",
          "completed":false
       },
       {
          "userId":1,
          "id":3,
          "title":"fugiat veniam minus",
          "completed":false
       },
       {
          "userId":1,
          "id":4,
          "title":"et porro tempora",
          "completed":true
       },
       ...
    ]
    ```

*   `GET todos/1`

    ```json
    {
       "userId":1,
       "id":1,
       "title":"delectus aut autem",
       "completed":false
    }
    ```

## Demo

```go
package main

import (
	"fmt"
	"io"
	"log"
	"net/http"
)

func main() {
	url := "https://jsonplaceholder.typicode.com/todos/1/"

	response, err := http.Get(url)

	if err != nil {
		log.Fatal(err)
	}
	defer response.Body.Close()

	if response.StatusCode != http.StatusOK {
		log.Fatalf("unexpected HTTP status: got %d, expected %d", response.StatusCode, http.StatusOK)

	}

	bodyBytes, err := io.ReadAll(response.Body)

	if err != nil {
		log.Fatal(err)
	}

	data := string(bodyBytes)
	fmt.Println(data)
}
```

We I get:

```json
{
  "userId": 1,
  "id": 1,
  "title": "delectus aut autem",
  "completed": false
}
```

But we converted to `string`, what makes difficult to access it's attributes

## Unmarshal

Instead of converting to `string`, you can:

```go
type Todo struct {
	UserID    int    `json:"userId"`
	ID        int    `json:"id"`
	Title     string `json:"title"`
	Completed bool   `json:"completed"`
}
```

*   Notice that the case of the words of our struct and the delivered data differ, the Go handle it automatically as long you spec the JSON struct tags (these `json:...` thingies).

*   

    Notice that all attributes are public, it is necessary to Unmarshal work.
    
    *   Naturally, because a private field is only visible to the own package.

To convert the json into that object, you can use [Unmarshal](https://pkg.go.dev/encoding/json#Unmarshal).

```go
func main() {
	...

	todoItem := Todo{}

	json.Unmarshal(bodyBytes, &todoItem)

	fmt.Printf("Data from API: %+v\n", todoItem)
}
```

*   You can also declare `todoItem` with `var todoItem Todo`:

    ```go
    var todoItem Todo
    
    json.Unmarshal(bodyBytes, &todoItem)
    ```

The result will be:

```go
Data from API: {UserID:1 ID:1 Title:delectus aut autem Completed:false}
```

the `Unmarshal` doesn't have one ""`DisallowUnknownFields()`" as the decoder have.

### Array

unmarshaling an array of objects from JSON is straightforward — you define a slice of structs that match the JSON structure, and then use json.Unmarshal() from the standard library.

```go
url := "https://jsonplaceholder.typicode.com/todos"
...

var todos []Todo

json.Unmarshal(bodyBytes, &todos)

fmt.Printf("Data from API: %+v\n", todos)
```

You will get:

```
Data from API: [{UserID:0 ID:0 Title:delectus aut autem Completed:false} {UserID:0 ID:0 Title:quis ut nam facilis et officia qui Completed:false} {UserID:0 ID:0 Title:fugiat veniam minus Completed:false} {UserID:0 ID:0 Title:et porro tempora Completed:true} {UserID:0 ID:0 Title:laboriosam mollitia et enim quasi adipisci quia provident illum Completed:false} {UserID:0 ID:0 Title:qui ullam ratione quibusdam voluptatem quia omnis Completed:false}...
```

## Decoder

An alternative of Unmarshal is decoder

```go
todoItem := Todo{}

json.NewDecoder(response.Body).Decode(&todoItem)

fmt.Printf("Data from API: %+v\n", todoItem
```

*   the `json.NewDecoder` receives a `r io.Reader`, in case, `response.Body`
*   it removed the need for `bodyBytes, err := io.ReadAll(response.Body)`

### `DisallowUnkownFields()`

If we comment out one field of `Todo` struct:

```go
type Todo struct {
	UserID    int    `json:"userId"`
	ID        int    `json:"id"`
	Title     string `json:"title"`
	// Completed bool   `json:"completed"`
}
```

The code still running:

```
Data from API: {UserID:1 ID:1 Title:delectus aut autem}
```

And maybe we don't want that, to avoid that, you can use `DisallowUnknownFields()`

```go
todoItem := Todo{}

decoder := json.NewDecoder(response.Body)
decoder.DisallowUnknownFields()

if err := decoder.Decode(&todoItem); err != nil {
	log.Fatal("Decode error", err)
}

fmt.Printf("Data from API: %+v\n", todoItem)
```

So:

```go
2025/10/18 15:13:34 Decode errorjson: unknown field "completed"
exit status 1
```

### Array

```go
var todos []Todo

decoder := json.NewDecoder(response.Body)

if err := decoder.Decode(&todos); err != nil {
log.Fatal("Decode error", err)
}

fmt.Printf("Data from API: %+v\n", todos)
```

#### decode incrementally

```go
decoder := json.NewDecoder(response.Body)

// Read the opening bracket '['
token, _ := decoder.Token()
fmt.Printf("Start of array: %v\n", token)

for decoder.More() {
	var todo Todo
	if err := decoder.Decode(&todo); err != nil {
		log.Fatal("Decode error", err)
	}
	fmt.Println(todo)
}

// Read the closing bracket ']'
token, _ = decoder.Token()
fmt.Printf("End of array: %v\n", token)
```

You will have:

```
Start of array: [
{0 0 delectus aut autem false}
{0 0 quis ut nam facilis et officia qui false}
{0 0 fugiat veniam minus false}
{0 0 et porro tempora true}
...
{0 0 quis eius est sint explicabo true}
{0 0 numquam repellendus a magnam true}
{0 0 ipsam aperiam voluptates qui false}
End of array: ]
```

## Marshal

```go
todo, err := json.Marshal(todoItem)
if err != nil {
log.Fatal("Marshal error", err)
}

fmt.Println(string(todo))
```

You will get:

```go
{"userId":1,"id":1,"title":"delectus aut autem","completed":false}
```

### `MarshalIndent`

You can transform the data into a indented json too:

```go
todo, err := json.MarshalIndent(todoItem, "", "\t")
if err != nil {
log.Fatal("Marshal error", err)
}

fmt.Println(string(todo))
```
* `""` is the prefix
* `"\t" is the indent

We will get:

```go
{
        "userId": 1,
        "id": 1,
        "title": "delectus aut autem",
        "completed": false
}
```

### Excluding fields

To exclude fields, you have specify `'json:"-"'` 

```go
package main

import (
	"encoding/json"
	"fmt"
	"log"
)

type Todo struct {
	UserID    int    `json:"-"`
	ID        int    `json:"-"`
	Title     string `json:"title"`
	Completed bool   `json:"completed"`
}

func main() {
	todoItem := Todo{
		UserID:    1,
		ID:        1,
		Title:     "delectus aut autem",
		Completed: false,
	}

	// convert back to Json
	todo, err := json.MarshalIndent(todoItem, "", "\t")
	if err != nil {
		log.Fatal("Marshal error", err)
	}

	fmt.Println(string(todo))
}
```

You will get:

```go
{
        "title": "delectus aut autem",
        "completed": false
}
```

### Omitting fields with empty values

On the previous code, if we have:

```go
todoItem := Todo{
UserID:    1,
ID:        1,
Title:     "",
Completed: false,
}
```

The result will be:

```go
{
        "title": "",
        "completed": false
}
```

To omit empty values, you can flag `omitempty` on the JSON struct tag:

```go
type Todo struct {
	UserID    int    `json:"-"`
	ID        int    `json:"-"`
	Title     string `json:"title,omitempty"`
	Completed bool   `json:"completed"`
}
```

So you will have:

```go
{
        "completed": false
}
```

https://www.youtube.com/watch?v=Tgg-ChT4IZE&list=TLPQMTgxMDIwMjWAD1y_tIfalw&index=1
