# Generate

Code generating code

The `go generate` command has been introduced all the way back [in Go 1.4](https://go.dev/blog/generate), and since then has been widely used in the Go ecosystem. The Go project itself relies on `go generate` in dozens of places; I'll do a quick overview of these use cases later on in the post.

The way `go generate` works is an orchestration between three major players:

- **Generator**: is a program or a script that is invoked by `go generate`. In any given project multiple generators may be invoked, a single generator can be invoked multiple times, etc.
- **Magic comments**: are comments formatted in a special way in `.go` files that specify which generator to invoke and how. Any comment that starts at the very beginning of the line with the text `//go:generate` qualifies.
- `go generate`: is the Go tool that reads Go source files, finds and parses magic comments and runs the generators, as specified.

## A simple example

Lets write a generator:

```go
package main

import (
  "fmt"
  "os"
)

func main() {
  fmt.Printf("Running %s go on %s\n", os.Args[0], os.Getenv("GOFILE"))

  cwd, err := os.Getwd()
  if err != nil {
    panic(err)
  }
  fmt.Printf("  cwd = %s\n", cwd)
  fmt.Printf("  os.Args = %#v\n", os.Args)

  for _, ev := range []string{"GOARCH", "GOOS", "GOFILE", "GOLINE", "GOPACKAGE", "DOLLAR"} {
    fmt.Println("  ", ev, "=", os.Getenv(ev))
  }
}
```

Now lets use in other project:

```
.
├── anotherfile.go
├── go.mod
├── mymod.go
└── mypack
    └── mypack.go
```

Where all the files have:

```go
//go:generate samplegentool arg1 "multiword arg"
```

So:

```bash
$ go generate ./...
Running samplegentool go on anotherfile.go
  cwd = /tmp/mymod
  os.Args = []string{"samplegentool", "arg1", "arg2", "arg3", "arg4"}
   GOARCH = amd64
   GOOS = linux
   GOFILE = anotherfile.go
   GOLINE = 1
   GOPACKAGE = mymod
   DOLLAR = $
Running samplegentool go on mymod.go
  cwd = /tmp/mymod
  os.Args = []string{"samplegentool", "arg1", "arg2", "-flag"}
   GOARCH = amd64
   GOOS = linux
   GOFILE = mymod.go
   GOLINE = 3
   GOPACKAGE = mymod
   DOLLAR = $
Running samplegentool go on mypack.go
  cwd = /tmp/mymod/mypack
  os.Args = []string{"samplegentool", "arg1", "multiword arg"}
   GOARCH = amd64
   GOOS = linux
   GOFILE = mypack.go
   GOLINE = 3
   GOPACKAGE = mypack
   DOLLAR = $
```

`go generate` runs each command from the directory of the source file that declared the directive, the working directory is

https://eli.thegreenplace.net/2021/a-comprehensive-guide-to-go-generate