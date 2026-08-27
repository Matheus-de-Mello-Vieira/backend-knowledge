# Go CLI

The `go` command is the main interface to the Go toolchain. It handles compilation, execution, testing, dependency management, formatting, static analysis, documentation, code generation, workspaces, and diagnostic tools.

Most commands operate on **packages** rather than individual files. In a module-based project, commands such as `go build .`, `go test ./...`, and `go vet ./...` allow the Go toolchain to understand the complete package and module structure.

## Building and Running Programs

### `go build`

`go build` compiles packages and their dependencies.

```bash
go build
```

For a `main` package, it produces an executable:

```bash
go build .
```

The output name can be controlled with `-o`:

```bash
go build -o server ./cmd/server
```

A non-`main` package is compiled to verify that it builds successfully, with the compiled result normally stored through Go's build cache rather than emitted as a standalone file.

`go build` ignores `_test.go` files.

A useful package pattern is:

```bash
go build ./...
```

which attempts to build all packages recursively below the current module directory.

### `go run`

`go run` compiles a `main` package and immediately executes the resulting program.

```bash
go run .
```

It can also run another package:

```bash
go run ./cmd/server
```

Arguments following the package are passed to the program:

```bash
go run . --port 8080
```

`go run` creates a temporary executable as part of compilation, but the executable is not kept as a normal build artifact.

Running the package is generally preferable to naming individual source files:

```bash
go run .
```

This lets Go compile the complete package according to its normal package rules.

### `go install`

`go install` compiles packages and installs executable `main` packages into the Go binary installation directory.

```bash
go install .
```

Executable binaries are normally placed in `$GOBIN`. If `GOBIN` is unset, the usual location is `$GOPATH/bin`, commonly `$HOME/go/bin`.

It is also commonly used to install Go-based developer tools:

```bash
go install example.com/tool@latest
```

A specific version can be installed:

```bash
go install example.com/tool@v1.4.0
```

When a version such as `@latest` or `@v1.4.0` is specified, the command resolves and builds that tool independently of the current module's `go.mod`.

The relationship between the three main execution commands is therefore:

- `go build` compiles a program and keeps the resulting executable.
- `go run` compiles and immediately executes a program.
- `go install` compiles an executable and places it in the Go binary installation directory.

## Modules and Dependencies

A **module** is a collection of related Go packages versioned together. Its root contains a `go.mod` file.

The main files involved in module management are:

- `go.mod`, which describes the module, its Go version, and its dependency requirements.
- `go.sum`, which stores cryptographic checksums associated with downloaded module contents.
- The module cache, which stores downloaded dependency source code locally.

### `go mod`

`go mod` contains commands for maintaining the current module.

#### `go mod init`

Creates a new `go.mod` file:

```bash
go mod init github.com/user/project
```

The supplied value becomes the module path used as the prefix for packages inside the module.

#### `go mod tidy`

Reconciles the module metadata with the packages actually required by the source code:

```bash
go mod tidy
```

It adds missing dependencies, removes unused dependencies, and updates `go.sum` accordingly.

This is commonly used after imports or dependencies change.

#### `go mod download`

Downloads modules into the local module cache:

```bash
go mod download
```

Normal Go commands already download dependencies when necessary, so this is mainly useful when dependencies need to be downloaded explicitly, such as while preparing a build environment or cache.

#### `go mod verify`

Checks that modules stored in the local module cache still contain the expected content:

```bash
go mod verify
```

It detects modifications to dependency files after they were downloaded.

#### `go mod graph`

Prints the module dependency graph:

```bash
go mod graph
```

Each line represents a module requirement relationship.

#### `go mod why`

Explains why a package is reachable from the current module:

```bash
go mod why golang.org/x/text/language
```

For modules:

```bash
go mod why -m golang.org/x/text
```

This is useful when investigating why a dependency exists.

### `go get`

`go get` changes the dependencies required by the current module.

To add a dependency or select its latest version:

```bash
go get example.com/pkg
```

To select a specific version:

```bash
go get example.com/pkg@v1.2.3
```

To upgrade dependencies:

```bash
go get -u ./...
```

To select only newer patch releases:

```bash
go get -u=patch ./...
```

To remove a dependency requirement:

```bash
go get example.com/module@none
```

`go get` resolves the requested versions, updates `go.mod`, and downloads the corresponding source code into the module cache.

## Testing and Code Quality

### `go test`

`go test` compiles and runs tests stored in `_test.go` files.

To test the current package:

```bash
go test
```

To test every package recursively:

```bash
go test ./...
```

Verbose mode prints individual test execution:

```bash
go test -v ./...
```

A specific test can be selected using a regular expression:

```bash
go test -run TestCreateUser
```

Benchmarks can be executed with:

```bash
go test -bench .
```

Go caches successful test results in situations where the test inputs have not changed, allowing repeated test runs to complete quickly.

### `go fmt`

`go fmt` formats Go source according to Go's standard formatting rules.

```bash
go fmt ./...
```

For the current package:

```bash
go fmt
```

It runs `gofmt` over the selected packages and rewrites files whose formatting needs adjustment.

Formatting is intentionally standardized in Go, reducing stylistic differences between projects.

### `go vet`

`go vet` performs static analysis and reports constructs that are syntactically valid Go but are likely to represent mistakes.

```bash
go vet ./...
```

Examples include suspicious formatting calls, invalid struct tags, unreachable patterns recognized by analyzers, and other common correctness problems.

`go vet` does not replace compilation or testing. It analyzes classes of mistakes that the compiler can legally accept.

Modern versions also support applying available suggested fixes:

```bash
go vet -fix ./...
```

A diff can be inspected without modifying the files:

```bash
go vet -diff ./...
```

### `go fix`

`go fix` runs automated source transformations provided by the Go fix framework.

```bash
go fix ./...
```

It is particularly useful when updating code to conventions, APIs, or language/library patterns supported by available fixers.

Available fixes can be inspected with:

```bash
go tool fix help
```

A specific fixer can be examined with:

```bash
go tool fix help <fix-name>
```

Changes can be previewed as a patch without applying them:

```bash
go fix -diff ./...
```

`go fix` is therefore intended for **source rewriting**, while `go vet` is primarily intended for **diagnosis and static analysis**, although vet analyzers may also expose fixes.

## Inspecting Packages and Documentation

### `go list`

`go list` inspects packages and modules known to the Go toolchain.

To print the current package:

```bash
go list
```

To recursively list packages:

```bash
go list ./...
```

To list modules:

```bash
go list -m all
```

To inspect detailed package information:

```bash
go list -json .
```

`go list` is especially useful in scripts and tooling because it exposes the package graph as understood by Go itself.

### `go doc`

`go doc` prints documentation directly from Go packages and symbols.

For the current package:

```bash
go doc
```

For a package:

```bash
go doc net/http
```

For a type:

```bash
go doc http.Client
```

For a method:

```bash
go doc http.Client.Do
```

It reads the documentation comments associated with packages, functions, variables, constants, types, methods, and fields.

Source code can also be displayed:

```bash
go doc -src http.Client.Do
```

This makes `go doc` useful when exploring APIs without leaving the terminal.

### `go version`

`go version` prints information about the installed Go toolchain:

```bash
go version
```

Example output:

```text
go version go1.26.0 linux/amd64
```

It can also inspect a compiled Go binary:

```bash
go version ./server
```

To display embedded module and build information:

```bash
go version -m ./server
```

This can reveal the Go version and module dependencies used to build an executable.

## Environment

### `go env`

`go env` displays the configuration used by the Go toolchain.

```bash
go env
```

Individual values can be inspected:

```bash
go env GOPATH
go env GOROOT
go env GOBIN
go env GOOS
go env GOARCH
go env GOMOD
go env GOMODCACHE
go env GOWORK
```

Some important variables are:

- `GOROOT`: location of the installed Go distribution.
- `GOPATH`: workspace-related storage used for items such as the module cache and default binary directory.
- `GOBIN`: destination for executables installed by `go install`.
- `GOMODCACHE`: directory containing downloaded modules.
- `GOOS`: target operating system.
- `GOARCH`: target CPU architecture.
- `GOMOD`: active `go.mod` file.
- `GOWORK`: active `go.work` workspace file.

Environment defaults can also be persistently configured with:

```bash
go env -w NAME=value
```

For example:

```bash
go env -w GOPROXY=https://proxy.golang.org,direct
```

## Workspaces

### `go work`

A Go **workspace** allows several local modules to participate in the same build.

This is useful when developing multiple modules together. Instead of publishing one module or adding temporary replacements to another module's `go.mod`, a `go.work` file can tell the Go toolchain to treat several local modules as main modules.

Consider:

```text
project/
├── service/
│   └── go.mod
└── library/
    └── go.mod
```

A workspace can be initialized from `project/`:

```bash
go work init ./service ./library
```

This creates a `go.work` file containing `use` directives for those modules.

Another module can be added later:

```bash
go work use ./another-module
```

The active workspace can be inspected with:

```bash
go env GOWORK
```

A typical `go.work` file looks like:

```go
go 1.26

use (
    ./service
    ./library
)
```

The Go toolchain can then resolve imports between these local modules using their workspace versions.

Useful subcommands include:

```bash
go work init
go work use
go work sync
go work edit
go work vendor
```

`go work sync` synchronizes the workspace's selected dependency versions back into the participating modules.

## Code Generation

### `go generate`

`go generate` executes commands declared through `//go:generate` directives in Go source files.

For example:

```go
//go:generate stringer -type=Status

type Status int
```

Running:

```bash
go generate ./...
```

causes Go to locate the directives and execute the declared commands.

The generator does not need to be written in Go. The directive can invoke any executable available to the environment.

Generation is explicit. Commands such as:

```bash
go build
go test
```

do not automatically run `go generate`.

This allows generated source code to remain a deliberate build-development step rather than an implicit side effect of compilation.

Generated Go files conventionally include:

```go
// Code generated ... DO NOT EDIT.
```

to communicate that the file should be regenerated through its generator instead of edited manually.

## Cleaning Build Artifacts and Caches

### `go clean`

`go clean` removes files produced by Go commands from package source directories.

```bash
go clean
```

Go maintains several caches independently, each of which can be explicitly cleared.

Remove the build cache:

```bash
go clean -cache
```

Expire cached test results:

```bash
go clean -testcache
```

Remove downloaded modules:

```bash
go clean -modcache
```

Remove cached fuzzing values:

```bash
go clean -fuzzcache
```

Remove the corresponding artifact previously installed by `go install`:

```bash
go clean -i
```

The build cache normally handles invalidation automatically, so explicitly clearing it is generally a diagnostic or maintenance operation rather than a routine build step.

## Execution Tracing

### `go tool trace`

`go tool trace` analyzes execution traces produced by a Go program.

A trace records events over time, including:

- Goroutine execution and blocking.
- Scheduler activity.
- Operating-system thread activity.
- Network and syscall events.
- Garbage collection.
- Processor utilization.
- Runtime events and synchronization.

This makes tracing particularly useful when studying concurrency and scheduler behavior because it shows **when** events occurred and how goroutines interacted over time.

### Tracing Tests

A test trace can be generated directly:

```bash
go test -trace=trace.out ./...
```

It can then be opened with:

```bash
go tool trace trace.out
```

### Tracing a Normal Program

Programs can create trace files through the `runtime/trace` package:

```go
package main

import (
    "os"
    "runtime/trace"
)

func main() {
    f, err := os.Create("trace.out")
    if err != nil {
        panic(err)
    }
    defer f.Close()

    if err := trace.Start(f); err != nil {
        panic(err)
    }
    defer trace.Stop()

    // Application workload.
}
```

After running the program:

```bash
go run .
```

the generated trace can be inspected with:

```bash
go tool trace trace.out
```

Tracing is useful for questions such as why goroutines are blocked, whether available CPUs are being utilized, how scheduling changes over time, and how runtime activity such as garbage collection interacts with application execution.
