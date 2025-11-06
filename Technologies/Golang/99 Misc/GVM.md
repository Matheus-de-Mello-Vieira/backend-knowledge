# What is gvm?

`gvm` lets you install and switch between multiple Go versions on the same machine. It also supports isolated package sets so projects don’t step on each other’s dependencies.

## Install gvm

```bash
bash < <(curl -s -S -L https://raw.githubusercontent.com/moovweb/gvm/master/binscripts/gvm-installer)
source ~/.gvm/scripts/gvm
```

Add it to you `˜/.bashrc`:

```bash
[[ -s "$HOME/.gvm/scripts/gvm" ]] && source "$HOME/.gvm/scripts/gvm"
```

## Core workflow

1. **List available versions**
   ```bash
   gvm listall
   ```

1. **Install a Go version**
   ```bash
   gvm install go1.22.5
   # optional: build with race or custom flags
   gvm install go1.22.5 --with-race
   ```

1. **Use a version (current shell)**
   
   ```bash
   gvm use go1.22.5
   ```
   
1. **Set a default version (new shells)**
   ```bash
   gvm use go1.22.5 --default
   ```

1. **See what you have installed**
   ```bash
   gvm list
   ```

1. **Uninstall a version**
   ```bash
   gvm uninstall go1.21.0
   ```

1. **Fall back to the system Go**
   ```bash
   gvm use system
   ```

## Project-level isolation with pkgsets

Pkgsets let you keep dependencies separate per project.

* create a pkgset under the currently active Go

  ```bash
  gvm pkgset create myproj
  ```

* use it

  ```bash
  gvm pkgset use myproj
  ```

* list pkgsets

  ```bash
  gvm pkgset list
  ```

* delete a pkgset

  ```bash
  gvm pkgset delete myproj
  ```

Tip: many teams activate a Go version and pkgset in a project’s shell init or a small helper script:

```bash
gvm use go1.22.5
gvm pkgset use myproj
```

## Handy extras

* Show where the current Go toolchain lives
  ```go
  gvm which go
  ```
* Print environment for the active version/pkgset
  ```go
  gvm env
  ```
* Update gvm itself (pull latest scripts)
  ```go
  gvm update
  ```
