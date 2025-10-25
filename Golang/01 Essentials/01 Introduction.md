# Introduction

Go is an open-source programming language developed by Google

*   Focus on simplicity, clarity and scalability
    *   Inspired by languages like Python
    *   Aims to provide a clean, understandable syntax
    *   normally there is only one way to do something, so it is a lot more readable.
*   High performance & Focus on Concurrency
    *   Similar to C and C++
        *   However, its go compilation is way faster, and we don't need to care about memory dellocation. 
    *   Popular for tasks that benefit from multi-threading
    *   When languages like Python and Java were created, computers typically had only a single CPU core. These languages were later adapted to support multicore processors. In contrast, Go was designed from the ground up with concurrency and multicore processing in mind.
*   Batteries included
    *   Go comes with standard library
    *   Many core features are built-in
    *   For example, go includes it's test's framework, profiling tools, race conditions dectector. 
*   Static typing
    *   Go is a type-safe language
    *   Allows you to catch many erros early

## Popular use-cases

*   Networking & APIs
*   Microservices
*   CLI Tools

## History
1. **2007 – Conception of Go**  
    - The Go programming language was conceived at Google by **Robert Griesemer**, **Rob Pike**, and **Ken Thompson**.  
    - The goal was to create a language that combined the **efficiency of compiled languages (like C++)** with the **ease of programming of interpreted languages (like Python)**.  

2. **2008 – Development Begins**  
    - Active development of Go started at Google.  
    - The team aimed to improve software development speed for large-scale, networked systems and multi-core hardware.  

3. **2009 – Public Announcement**  
    - Go was officially **announced as an open-source project** on **November 10, 2009**.  
    - The initial release included a compiler, standard library, and documentation.  
    - The language quickly gained attention for its simplicity, concurrency model (via goroutines), and fast compilation.  

4. **2010 – First Stable Version (Go 1.0 Preview)**  
    - The community began contributing actively to the open-source project.  
    - Early adopters praised Go for its performance and clean syntax.  

5. **2012 – Go 1.0 Released**  
    - The first stable version, **Go 1.0**, was officially released on **March 28, 2012**.  
    - This version established the foundation and **backward compatibility promise**, ensuring future versions wouldn’t break existing code.
      - It guarantees long-term code safety and stability, allowing developers to use Go without fear of future incompatibility.
    
6. **2013–2015 – Growing Ecosystem**  
    - Go gained popularity in web development, cloud services, and DevOps tools.  
    - Tools like **Docker** (written in Go) contributed massively to its adoption.  

7. **2015 – Introduction of Go 1.5**  
    - The Go compiler was rewritten in Go itself (bootstrapping).  
    - This version also introduced a fully concurrent garbage collector and improvements to performance.  

8. **2017 – Go 1.9 and Type Aliases**  
    - Type aliases were introduced, improving backward compatibility for package refactoring.  
    - The Go team continued to enhance tooling, including `go fmt`, `go vet`, and `go test`.  

9. **2018 – Go Modules Introduced (Go 1.11)**  
    - Go Modules replaced GOPATH, offering a **modern dependency management system**.  
    - This was a major milestone for large-scale project management.  

10. **2020 – Go 1.14–1.15 Enhancements**  
    - Performance and runtime improvements, particularly in the garbage collector and scheduler.  
    - Widespread adoption in cloud infrastructure and backend systems.  

11. **2021 – Go 1.17–1.18: Generics Arrive**  
    - After years of discussion, **generics** were added in **Go 1.18 (March 2022)**.  
    - This was one of the most significant updates since Go 1.0, greatly enhancing flexibility in code reuse.  

12. **2022–2025 – Continued Evolution**  
    - Go continues to evolve with performance, developer tooling, and language features.  
    - Versions like **Go 1.21 and 1.22** refined generics, improved memory management, and introduced new standard library capabilities.  
    - Go remains a core language for cloud infrastructure, microservices, and DevOps tooling.  

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

