# Packages and Modules

## Packages

A package in Go is a way to organize and reuse code. Every Go source file (`.go` file) belongs to a package.

*   Every go file need a `package` declaration.

*   A package is simply a collection of Go files in the same directory that share the same `package` declaration at the top.

Example:

```go
package mathutils

import "fmt"

func Add(a, b int) int {
    return a + b
}

func PrintSum(a, b int) {
    fmt.Println("Sum:", Add(a, b))
}
```

Here:

-   The package name is `mathutils`.
-   You can use this package in another Go file by importing it (if it’s part of the same module or available via a module path).

When you run or build your Go code, the compiler groups all files in the same package together.

### Main package

*   The main package is special — it defines an executable program (not a library).
*   A file in the `main` package must have a `func main()` entry point.
*   Other packages are meant to be imported and reused.

Example of a `main` package using `mathutils`:

```go
package main

import (
    "fmt"
    "example.com/myapp/mathutils"
)

func main() {
    result := mathutils.Add(5, 3)
    fmt.Println("Result:", result)
}
```

### Accessing Elements from

Example project structure

```
myapp/
├── go.mod
├── main.go
└── mathutils/
    ├── add.go
    └── sub.go
```

####  Another File, Same Package

If two .go files are in the same folder and have the same package name, they automatically share all their identifiers (functions, variables, types, etc.), even if they are unexported (start with a lowercase letter).

Example

*   `mathutils/add.go`

    ```go
    package mathutils
    
    func Add(a, b int) int {      // uppercase: exported
        return a + b
    }
    
    func AddAndDouble(a, b int) int { // uppercase: exported
        return Add(a, b) * 2
    }
    ```

*   `mathutils/sub.go`

    ```go
    package mathutils
    
    func sub(a, b int) int {
        return a - b
    }
    
    func CombinedOp(a, b int) int {
        return Add(a, b) + sub(a, b) // can access Add() freely
    }
    ```

#### Another Package

When you access code from a *different* package, you must:

1.  Import that package.
2.  Use the exported (capitalized) identifiers from it.
3.  Have a `main` function, to serve as system's entry point.

Example

*   `main.go`

    ```go
    package main
    
    import (
        "fmt"
        "example.com/myapp/mathutils" // module path + folder
    )
    
    func main() {
        sum := mathutils.Add(5, 3)
        fmt.Println(sum)
    
        // mathutils.sub(5,3) ❌ Not allowed (unexported)
    }
    ```

### Standardized library

Go comes with a huge Standardized library of built-in packages: https://pkg.go.dev/std

## Module

A **module** is a collection of related Go packages that are versioned together as a unit.
*   Modules make dependency management and versioning easier.
*   A module is identified by a module path (like `github.com/user/projectname`).
*   Each module has a file named `go.mod` at its root, which defines the module’s path and dependencies.

Example of a `go.mod` file:

```go
module example.com/myapp

go 1.22

require (
    github.com/gin-gonic/gin v1.9.1
)
```

Here:

-   The module path is `example.com/myapp`.
-   The project uses Go 1.22.
-   It depends on the external module `github.com/gin-gonic/gin` (version 1.9.1).

### Creating a new module

````bash
go mod init <module-path>
````

This command creates a `go.mod` file in your project’s root directory.

*   Example:

    ```bash
    go mod init example.com/myapp
    ```


#### Module path

The module path is a unique identifier for your Go module.

*   It tells Go (and other developers) where this module comes from and how to import its packages.
    *   The module path defines the **import base path** for all packages in your project.

Patterns

*   **Local (private or experimental) projects**: If your project is local and not hosted anywhere, you can use any path you like — it just needs to be unique within your workspace.

    ```
    go mod init myapp
    go mod init github.local/myname/myapp
    go mod init example/myapp
    ```

    *   You can then import subpackages relative to that path, e.g.:

        ```go
        import "myapp/mathutils"
        ```

*   **Public / hosted modules (recommended for real projects)**: If you plan to share or publish your module (e.g. on GitHub or a private VCS), the module path should match the repository URL.

    For example, if your code lives at:

    ```
    https://github.com/yourname/myapp
    ```

    then you should initialize it with:

    ```bash
    go mod init github.com/yourname/myapp
    ```

    That way, others can import your code with:

    ```bash
    import "github.com/yourname/myapp/mathutils"
    ```

### Add dependencies

```bash
go get <module-path>@<version>
```

*   Adds or updates a dependency manually.

    *   Example:

        ```bash
        go get github.com/gin-gonic/gin@v1.9.1
        ```

### Upgrade or downgrade a dependency

*   ```bash
    go get <module-path>@latest
    ```
    it resolves what “latest” means at that moment — usually the newest tagged stable release (e.g. `v1.12.3`) — and then **pins** that exact version number in your `go.mod`.

*   ```bash
    go get <module-path>@v1.2.3
	```
	Updates a specific dependency to a desired version.

### Clean up unused dependencies

```bash
go mod tidy
```

*   Removes unused modules and adds any missing ones.
*   Most common and safest command for keeping dependencies up to date.
*   It will
    *   Reads the project’s `go.mod`
    *   Downloads any missing dependencies
    *   Cleans up unused ones
    *   Verifies checksums in `go.sum`

*   If you want to work in a already existent project, this is the command to initialize your workspace

### **Download all dependencies**

```bash
go mod download
```

Downloads all the modules listed in `go.mod` to your local cache, but doesn’t install them.

### Verify module integrity

```bash
go mod verify
```

### List all dependencies

```bash
go list -m all
```

## Building

```bash
go build
```

## Running

You can run a specify file with;

```bash
go run investment_calculator.go
```

Or you can run the current module with a dot (`.`):

```bash
go run .
```

## Basic structuring

A **basic Go project** has a clean and opinionated structure — Go emphasizes simplicity and convention over configuration.

### Typical Project Structure

```
myproject/
│
├── cmd/                    # Main applications for this project
│   └── myapp/
│       └── main.go         # Entry point (package main)
│
├── internal/               # Private packages (cannot be imported outside this module)
│   └── service/
│       └── service.go
│
├── pkg/                    # Public packages (importable by external modules)
│   └── utils/
│       └── strings.go
│
├── api/                    # (optional) API definitions, schemas, or protobufs
│
├── configs/                # Configuration files (YAML, JSON, ENV)
│
├── scripts/                # Helper scripts (build, deploy, etc.)
│
├── test/                   # Integration or e2e tests
│
├── go.mod                  # Module definition (dependencies)
├── go.sum                  # Dependency checksums
└── README.md
```

### Key Concepts

*   **`cmd/`**
     Each folder inside represents a separate executable program.
     Example: `cmd/server/main.go` could start a web server.
    
    *   Project with `cmd/` are applications — web servers, CLIs, daemons, etc.
    
*   **`internal/`**
     Code that **must not** be imported by other modules (Go enforces this).
     Great for encapsulating your business logic or data layers.

*   **`pkg/`**
     Reusable packages meant to be imported elsewhere (optional but common in libraries).

*   **`go.mod`**
     Defines your module name and dependencies.
     Example:

    ```
    module github.com/username/myproject
    
    go 1.22
    ```

*   **`main.go`**

     The entry point of your executable — must declare:

    ```go
    package main
    
    func main() {
        // your app starts here
    }
    ```

## go.mod replace directive

In Go, the `go.mod` file manages modules and dependencies. One of its useful features is the `replace` directive, which allows you to override the source or version of a dependency.

### What `replace` does

The `replace` directive tells Go to use a different module path or version than the one originally declared. This can point to a different version, a fork, or even a local directory.

### Basic syntax

```go
replace [old-module] [old-version] => [new-module] [new-version]
```

If you want to replace with a local path, the syntax is:

```go
replace [old-module] => [local/path/to/module]
```

### Example: replace with a local path

This is useful when developing multiple modules locally.

```go
module github.com/myuser/project

go 1.22

require github.com/myuser/shared v0.2.0

replace github.com/myuser/shared => ../shared
```

This tells Go to use the local folder `../shared` instead of downloading `github.com/myuser/shared@v0.2.0`.

### Example: replace with a different module path

You can point a dependency to a forked repository.

```go
replace github.com/old/dependency => github.com/myfork/dependency v1.4.3
```

This makes Go use your fork instead of the original dependency.

### Example: replace with a specific version

You can override a version requested elsewhere in the dependency graph.

```go
replace github.com/some/lib v1.2.3 => github.com/some/lib v1.3.0
```

This forces Go to use version `v1.3.0` even if another module requires `v1.2.3`.

### Multiple replaces

You can list several `replace` directives in a single block.

```go
replace (
    github.com/a/dependency => ../local/a
    github.com/b/dependency => github.com/myfork/b v1.0.0
)
```

### When to use `replace`

- During local development, when working on multiple modules on your machine.
- When using a fork to fix or modify a dependency.
- When the original source of a module is unavailable or deprecated.

### When not to use `replace`

- Avoid committing local path replaces like `../something` in production code, since they will break for other developers.
- Avoid long-term reliance on `replace`; dependencies should ideally resolve through normal versioning with `go get`.

### How Go handles it

When you run commands such as `go mod tidy` or `go build`, Go processes all `replace` directives first. Replacements always take priority when resolving dependencies.

## Workspaces

Instead of putting `replace` in each module, you can use a **workspace file** to manage them together.

From `/home/user/projects/`, run:

```
go work init ./app ./lib
```

This creates a `go.work` file like:

```
go 1.22

use (
    ./app
    ./lib
)
```

Go automatically understands that when `app` imports `github.com/myuser/lib`, it should use the **local `lib` directory**.

* You **don’t need a `replace` directive** in this case.
* It will bug `go mod tidy` because it ignores workspace, so it will try to search the mod remotely.
  * run `go mod tidy -e`to ignore these errors, and install the rest of the depedencies.