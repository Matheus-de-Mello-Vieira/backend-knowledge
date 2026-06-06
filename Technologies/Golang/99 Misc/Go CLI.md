# basic Go CLI (Command Line Interface) commands

Sure! Let’s go over the **basic Go CLI (Command Line Interface) commands** that you’ll use frequently when developing in Go.

The Go tool (`go`) is a powerful command-line utility that helps you **build, run, test, format, and manage Go code**. Below are the most common commands you’ll use:

## `go build`

**Purpose:** Compiles the source code of your package or module.

**Usage:**

```bash
go build
```

**Details:**

-   If you run this inside a directory containing a `main` package, it compiles it and creates an executable in the current directory.

-   If the directory contains a non-main package, it compiles it but doesn’t produce an output file.

-   You can specify a file or package path:

    ```bash
    go build main.go
    go build ./cmd/app
    ```

**Example:**

```bash
go build -o myapp
```

→ Builds the current program and outputs a binary named `myapp`.

------

## `go run`

**Purpose:** Compiles and runs Go code directly — without leaving a binary file behind.

**Usage:**

```bash
go run main.go
```

**Details:**

-   Great for quick testing or running small programs.

-   You can pass multiple source files:

    ```bash
    go run main.go utils.go
    ```

-   You can also run entire packages:

    ```bash
    go run ./cmd/server
    ```

## `go mod`

**Purpose:** Manages modules (dependencies) for your project.

**Common subcommands:**

```bash
go mod init <module-name>  # Initialize a new module
go mod tidy                # Add missing and remove unused dependencies
go mod download            # Download modules to local cache
go mod verify              # Verify dependencies have not been tampered with
```

**Example:**

```bash
go mod init github.com/username/myproject
```

## `go test`

**Purpose:** Runs tests written in `_test.go` files.

**Usage:**

```bash
go test
go test ./...
```

**Details:**

-   The `./...` pattern runs tests recursively in all subdirectories.

-   Add `-v` for verbose output:

    ```bash
    go test -v
    ```

## `go fmt`

**Purpose:** Automatically formats your Go code according to Go’s standard style.

**Usage:**

```bash
go fmt
go fmt ./...
```

**Example:**

```bash
go fmt main.go
```

**Details:** This is crucial because Go enforces a consistent coding style (via `gofmt`), which helps keep all Go codebases uniform.

## `go install`

**Purpose:** Builds and installs the binary into your `$GOPATH/bin` or `$GOBIN` directory.

**Usage:**

```bash
go install
```

**Example:**

```bash
go install github.com/user/tool@latest
```

**Details:** This is how you install third-party Go tools or distribute your own CLI programs.

## `go get`

**Purpose:** Downloads and installs dependencies or modules.

**Usage:**

```bash
go get github.com/some/package
```

**Example:**

```bash
go get github.com/gin-gonic/gin
```

**Note:** Since Go 1.17+, `go install` is preferred for installing binaries, while `go get` is mainly for adding libraries to your module.

## `go list`

**Purpose:** Lists information about packages.

**Usage:**

```bash
go list
go list all
go list ./...
```

**Example:**

```bash
go list -m all
```

→ Lists all modules used by the current module.

## `go env`

**Purpose:** Prints Go environment information.

**Usage:**

```bash
go env
```

**Example:**

```bash
go env GOPATH
go env GOROOT
```

**Details:** Useful for checking where your Go installation, workspace, and binaries live.

## `go clean`

**Purpose:** Removes object files, cached build files, and binaries.

**Usage:**

```bash
go clean
```

**Example:**

```bash
go clean -i
```

→ Removes installed binaries as well.

## `go tool trace`

`go tool trace` is a **powerful profiling and visualization tool** in the Go toolchain.

*   It helps you **see what your Go program was doing over time** — especially how goroutines, threads, and the scheduler interact.

It provides a **timeline view** of:

-   Goroutine creation and execution
-   Network, syscall, and GC (garbage collection) events
-   Scheduler activity
-   Processor usage and work-stealing behavior

You use `go tool trace` to:

-   **Understand performance bottlenecks**
-   **Visualize concurrency** (when and how goroutines run)
-   **Debug scheduling issues** (e.g., goroutines blocked on channels or syscalls)
-   **See GC pauses**
-   **Inspect parallelism** and CPU utilization

### Basic Workflow

Here’s how you typically use it:

#### 1. Generate a trace file

You run your Go program with tracing enabled:

```
go test -trace trace.out
```

or, for a normal Go program:

```
go run main.go
```

(inside your code, you can also manually start a trace — more on that below.)

####  2. View the trace

Then, use the tool to analyze it:

```
go tool trace trace.out
```

This launches an **interactive web UI** in your browser that looks similar to Chrome’s performance tools.
