# `swaggo/swag`

[`swaggo/swag`](https://github.com/swaggo/swag) is a Go library + CLI tool that **auto-generates Swagger documentation from Go comments**.

You write normal Go code for your HTTP API (Gin, Echo, Chi, Fiber, etc.), and add structured comments above your handlers and models. Then you run `swag init`, and it produces:

- A `docs/` package containing:
  - `swagger.json` / `swagger.yaml`
  - `docs.go` (the Go wrapper that exposes Swagger metadata)
- You can then serve a beautiful interactive Swagger UI inside your app.

## How it works

1. **You annotate your code** using special comment tags (`@Summary`, `@Description`, `@Param`, etc.).
2. The `swag` CLI parses your source files, extracts these annotations, and generates OpenAPI definitions.
3. You serve the documentation with a Swagger UI handler from `swaggo/files` and your router’s integration middleware.

## Installation

```bash
go install github.com/swaggo/swag/cmd/swag@latest

# Middleware for your router
go get github.com/swaggo/files
go get github.com/swaggo/gin-swagger@latest    # Gin
# or
go get github.com/swaggo/echo-swagger@latest   # Echo
# or
go get github.com/swaggo/http-swagger@latest   # Chi, net/http, Fiber, etc.
```

## Example Setup (Gin)

### Step 1: Add project-level annotations

```go
// Package main Example API server.
//
// @title           Example API
// @version         1.0
// @description     This is a sample server using swaggo/swag.
// @contact.name    API Support
// @contact.email   support@example.com
// @BasePath        /api/v1
package main
```

### Step 2: Annotate your handler

```go
type User struct {
    ID    int    `json:"id" example:"1"`
    Name  string `json:"name" example:"Alice"`
    Email string `json:"email" example:"alice@example.com"`
}

// GetUser godoc
// @Summary      Get a user by ID
// @Description  Returns a single user
// @Tags         users
// @Param        id   path      int  true  "User ID"
// @Produce      json
// @Success      200  {object}  User
// @Failure      404  {object}  map[string]string
// @Router       /users/{id} [get]
func GetUser(c *gin.Context) {
    id := c.Param("id")
    c.JSON(http.StatusOK, User{ID: 1, Name: "Alice", Email: "alice@example.com", ID: id})
}
```

### Step 3: Generate docs

```bash
swag init
```

This creates a `/docs` folder with Swagger files.

### Step 4: Serve the Swagger UI

```go
import (
    "github.com/gin-gonic/gin"
    swaggerFiles "github.com/swaggo/files"
    ginSwagger "github.com/swaggo/gin-swagger"
    _ "yourmodule/docs"
)

func main() {
    r := gin.Default()
    r.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))
    r.Run(":8080")
}
```

Then open:  http://localhost:8080/swagger/index.html

## Common Annotations

| Tag            | Description            | Example                               |
| -------------- | ---------------------- | ------------------------------------- |
| `@Summary`     | Short one-line summary | `@Summary Get user info`              |
| `@Description` | Longer text            | `@Description Returns a user by ID`   |
| `@Tags`        | Logical grouping       | `@Tags users`                         |
| `@Param`       | Input parameter        | `@Param id path int true "User ID"`   |
| `@Success`     | Successful response    | `@Success 200 {object} User`          |
| `@Failure`     | Error response         | `@Failure 400 {object} ErrorResponse` |
| `@Router`      | Route definition       | `@Router /users/{id} [get]`           |
| `@Accept`      | Input format           | `@Accept json`                        |
| `@Produce`     | Output format          | `@Produce json`                       |
| `@BasePath`    | API root path          | `@BasePath /api/v1`                   |

### `@Param`

`@Param` is an annotation tag used in your Go comments to **describe request parameters** for your API endpoints when generating Swagger (OpenAPI) documentation with [`swaggo/swag`](https://github.com/swaggo/swag).

It tells Swagger:

> “This endpoint expects a parameter — here’s its name, location, type, whether it’s required, and what it means.”

#### Syntax

```
@Param <name> <in> <type> <required> "<description>" [format or schema]
```

| Field             | Description                                                  | Example                          |
| ----------------- | ------------------------------------------------------------ | -------------------------------- |
| `<name>`          | Parameter name                                               | `id`, `q`, `Authorization`, etc. |
| `<in>`            | Where the parameter is located (`path`, `query`, `header`, `body`, `formData`) | `path`                           |
| `<type>`          | Parameter type (`string`, `int`, `boolean`, `file`, or a struct for body params) | `int`                            |
| `<required>`      | Whether it’s required (`true` or `false`)                    | `true`                           |
| `<description>`   | Short description (must be inside quotes `"..."`)            | `"User ID"`                      |
| `[format/schema]` | (optional) Struct type or schema reference for body parameters | `CreateUserReq`                  |

#### Examples by parameter type

##### Path parameters

Used for variables in your URL (e.g. `/users/{id}`)

```go
// @Param id path int true "User ID"
// @Router /users/{id} [get]
```

* means the endpoint requires an integer `id` in the path.
*  Example request: `/users/42`

##### Query parameters

Used for `?key=value` pairs in URLs

```go
// @Param q query string false "Search query"
// @Param page query int false "Page number"
```

* Example request: `/users?q=alice&page=2`

##### Header parameters

Used for HTTP headers (like tokens, language codes, etc.)

```go
// @Param Authorization header string true "Bearer token"
```

* Example header: `Authorization: Bearer eyJhbGciOiJIUzI1NiIs...`

##### Body parameters (JSON payload)

Used for POST/PUT requests with JSON data.

```go
type CreateUserReq struct {
    Name  string `json:"name" example:"Alice"`
    Email string `json:"email" example:"alice@example.com"`
}

// @Param user body CreateUserReq true "User payload"
```

* Tells Swagger: The request body is a JSON object matching the `CreateUserReq` struct.

### Form parameters (form-data or urlencoded)

Used for file uploads or HTML form submissions.

```go
// @Param file formData file true "Profile picture"
// @Param username formData string true "Username"
```

* Used with `multipart/form-data` or `application/x-www-form-urlencoded`.

## Tips & Best Practices

- Add `example:` struct tags in struct field tags

  ```go
  type User struct {
      ID    int    `json:"id" example:"1"`
      Name  string `json:"name" example:"Alice"`
      Email string `json:"email" example:"alice@example.com"`
  }
  ```

- Commit the `docs/` folder so others don’t need to run `swag init`.

- Use `swag fmt` to validate your comment syntax.

- You can output YAML (`swagger.yaml`) with `swag init --output docs --generatedTime=false --parseDependency`.

- Works great in CI/CD pipelines (just rerun `swag init` on build).

## Ecosystem

- **`swaggo/swag`** – the generator
- **`swaggo/files`** – static Swagger UI assets
- **Router integrations:**
  - `swaggo/gin-swagger`
  - `swaggo/echo-swagger`
  - `swaggo/http-swagger`
  - `swaggo/fiber-swagger`

## Example Project Structure

```
myapp/
 ├── main.go
 ├── handlers/
 │    └── user.go
 ├── models/
 │    └── user.go
 ├── docs/              ← generated by swag init
 │    ├── docs.go
 │    ├── swagger.json
 │    └── swagger.yaml
 ├── go.mod
 └── go.sum
```