# Introduction

Go is an open-source programming language developed by Google

*   Focus on simplicity, clarity and scalability
    *   Inspired by languages like Python
    *   Aims to provide a clean, understandable syntax
*   High performance & Focus on Concurrency
    *   Similar to C and C++
    *   Popular for tasks that benefit from multi-threading
*   Batteries included
    *   Go comes with standard library
    *   Many core features are built-in
*   Static typing
    *   Go is a type-safe language
    *   Allows you to catch many erros early

## Popular use-cases

*   Networking & APIs
*   Microservices
*   CLI Tools

## Local Code Editor Setup

*   Install go, and and extension on your IDE

In a empty folder:

*   `app.go`

    ```go
    package main
    
    import "fmt"
    
    func main() {
    	fmt.Println("Hello World")
    }
    
    ```

*   You execute in a terminal:

    ```go
    $ go run app.go
    Hello World!
    ```

