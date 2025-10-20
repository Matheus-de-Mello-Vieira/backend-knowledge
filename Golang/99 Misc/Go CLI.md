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