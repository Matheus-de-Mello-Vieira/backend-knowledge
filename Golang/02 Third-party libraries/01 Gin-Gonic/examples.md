# gin-gonic/gin

Gin is built **on top of Go’s standard `net/http` package**, meaning it’s fully compatible with Go’s built-in HTTP features. However, it provides a much more convenient and efficient way to define routes, handle requests, and manage middleware.

*   https://github.com/gin-gonic/gin

## Basic Example

```go
package main

import "github.com/gin-gonic/gin"

func main() {
    r := gin.Default() // includes Logger and Recovery middleware by default

    r.GET("/ping", func(c *gin.Context) {
        c.JSON(200, gin.H{
            "message": "pong",
        })
    })

    r.Run(":8080") // listen and serve on 0.0.0.0:8080
}
```

## Not so basic example

```go
myapp/
├── cmd/
│   └── server/
│       └── main.go
├── internal/
│   ├── handlers/
│   │   └── user_handler.go
│   ├── routes/
│   │   └── router.go
│   ├── services/
│   │   └── user_service.go
│   └── models/
│       └── user.go
└── go.mod
```

*   `cmd/server/main.go`

    ```go
    package main
    
    import (
    	"github.com/yourusername/myapp/internal/routes"
    )
    
    func main() {
    	r := routes.SetupRouter()
    	r.Run(":8080")
    }
    ```

*   `internal/routes/route.go`

    ```go
    package routes
    
    import (
    	"github.com/gin-gonic/gin"
    	"myapp/golearning/internal/handlers"
    	"myapp/golearning/internal/middleware"
    )
    
    func SetupRouter() *gin.Engine {
    	r := gin.Default()
    
    
    	api := r.Group("/api")
    	api.Use(middleware.AuthMiddleware())
    	{
    		users := api.Group("/users")
    		{
    			users.GET("", handlers.ListUsers)
    			users.GET("/:id", handlers.GetUserByID)
    		}
    	}
    
    	return r
    }
    ```
    
*   `internal/middleware/auth.go`

    ```go
    package middleware
    
    import "github.com/gin-gonic/gin"
    
    func AuthMiddleware() gin.HandlerFunc {
    	return func(c *gin.Context) {
    		token := c.GetHeader("Authorization")
    		if token != "secret" {
    			c.AbortWithStatusJSON(401, gin.H{"error": "unauthorized"})
    			return
    		}
    		c.Next()
    	}
    }
    ```

*   `internal/handlers/user_handlers.go`

    ```go
    package handlers
    
    import (
    	"github.com/gin-gonic/gin"
    	"myapp/golearning/internal/services"
    	"net/http"
    	"strconv"
    )
    
    func GetUserByID(c *gin.Context) {
    	idStr := c.Param("id")
    	id, err := strconv.Atoi(idStr)
    	if err != nil {
    		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid id"})
    		return
    	}
    
    	user := services.GetUserByID(id)
    	if user == nil {
    		c.JSON(http.StatusNotFound, gin.H{"error": "user not found"})
    		return
    	}
    
    	c.JSON(http.StatusOK, user)
    }
    
    func ListUsers(c *gin.Context) {
    	users := services.ListUsers()
    	c.JSON(http.StatusOK, users)
    }
    ```

*   `internal/services/user_service.go`

    ```go
    package services
    
    import "myapp/golearning/internal/models"
    
    var mockUsers = []models.User{
    	{ID: 1, Name: "Alice", Email: "alice@example.com"},
    	{ID: 2, Name: "Bob", Email: "bob@example.com"},
    }
    
    func GetUserByID(id int) *models.User {
    	for _, u := range mockUsers {
    		if u.ID == id {
    			return &u
    		}
    	}
    	return nil
    }
    
    func ListUsers() []models.User {
    	return mockUsers
    }
    ```

*   `internal/models/user.go`

    ```go
    package models
    
    type User struct {
    	ID    int    `json:"id"`
    	Name  string `json:"name"`
    	Email string `json:"email"`
    }
    ```

    