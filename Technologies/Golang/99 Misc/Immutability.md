# Immutability

Go doesn’t have language-level immutability, but you can design immutable types with a few disciplined patterns.

1.  Hide state (encapsulation)
    *   Keep fields **unexported** (lowercase).
    *   Provide a **constructor** and **getters** only.
    *   Offer “withers” that **return a new value** instead of mutating.

2.  Prefer **value semantics**
    *   Make your type small and copyable; use **value receivers**.
    	* be careful because it is a shallow copy 
    *   Avoid exposing pointers to internal state.

3.  **Defensive copies** for reference types
    *   Slices, maps, and pointers are mutable references.
    *   In the constructor: **copy inputs**.
    *   In getters: **return copies**, never the original.
    *   Internally: treat them as read-only.

3.  Expose **read-only interfaces**
    * Publish an interface with only getters/queries; keep the concrete type private.

4.  Separate I/O structs from domain models
    *   Use exported structs for JSON/db (mutable DTOs).
    *   Convert to an **internal immutable** domain type.

5.  Concurrency mindset
    * Prefer **share-nothing + message passing** (channels).
    
        * >   Don’t share memory to communicate; communicate to share memory.
        * Instead of multiple goroutines accessing the same variable, each goroutine *owns* its own data and communicates via **channels**.
    
    * For shared snapshots (e.g., config), replace the **entire immutable value** atomically (e.g., `atomic.Value`), not fields in place.
    
        ```go
        package main
        
        import (
            "fmt"
            "sync/atomic"
            "time"
        )
        
        type Config struct {
            Version int
            Features []string
        }
        
        var config atomic.Value // holds Config
        
        func loadInitialConfig() {
            cfg := Config{
                Version: 1,
                Features: []string{"A", "B"},
            }
            config.Store(cfg) // store immutable snapshot
        }
        
        func getConfig() Config {
            return config.Load().(Config) // readers get a copy by value
        }
        
        func updateConfig(newFeatures []string) {
            old := getConfig()
            // Create a new copy — don’t mutate the existing one
            cfg := Config{
                Version:  old.Version + 1,
                Features: append([]string(nil), newFeatures...), // copy slice
            }
            config.Store(cfg) // atomically replace snapshot
        }
        
        func main() {
            loadInitialConfig()
        
            // Reader goroutine
            go func() {
                for {
                    cfg := getConfig()
                    fmt.Println("Reader sees config:", cfg)
                    time.Sleep(500 * time.Millisecond)
                }
            }()
        
            // Writer goroutine updates config safely
            go func() {
                for i := 2; i <= 3; i++ {
                    time.Sleep(1 * time.Second)
                    updateConfig([]string{"A", "B", fmt.Sprint("New-", i)})
                }
            }()
        
            time.Sleep(3 * time.Second)
        }
        ```
    
        *   `atomic.Value` ensures **atomic replacement** of the whole config struct.
        *   Readers always get a **consistent snapshot** — no locks, no partial updates.
        *   The config struct is **immutable**: readers can safely use it without worrying that it will change underneath them.