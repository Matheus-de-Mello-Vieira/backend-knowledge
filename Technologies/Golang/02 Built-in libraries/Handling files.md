## files

### Writing files

```go
func main() {
	balance := 104.1
	balanceText := fmt.Sprint(balance)
	os.WriteFile("balance.txt", []byte(balanceText), 0644)
}
```

* If you know that is a string:

  ```go
  func main() {
  	balance := 104.1
  	balanceText := fmt.Sprint(balance)
  
  	// Create or truncate the file
  	file, err := os.Create("balance.txt")
  	if err != nil {
  		fmt.Println("Error creating file:", err)
  		return
  	}
  	defer file.Close()
  
  	// Write the string to the file
  	_, err = file.WriteString(balanceText)
  	if err != nil {
  		fmt.Println("Error writing to file:", err)
  		return
  	}
  }
  ```

### Reading files

```go
func main() {
	data, _ := os.ReadFile("balance.txt")

	balanceText := string(data)
	balance, _ := strconv.ParseFloat(balanceText, 64)

	fmt.Println(balance)
}
```

### Read bytes at a time

To read 10 bytes by 10 bytes

```go
file, err := os.Open("file.txt")
if err != nil {
    panic(err)
}

reader := bufio.NewReader(file)
buffer := make([]byte, 10)

for {
    n, err := reader.Read(buffer)
    if err != nil {
        break
    }
    fmt.Println(string(buffer[:n]))
}
```

### Read line by line

to read a file line-by-line in Go, you can use the `bufio` package along with `os.Open`. Here’s a simple and idiomatic example:

```go
package main

import (
    "bufio"
    "fmt"
    "log"
    "os"
)

func main() {
    // Open the file
    file, err := os.Open("prices.txt")
    if err != nil {
        log.Fatalf("Failed to open file: %v", err)
    }
    defer file.Close()

    // Create a new scanner to read line by line
    scanner := bufio.NewScanner(file)

    for scanner.Scan() {
        line := scanner.Text()
        fmt.Println(line)
    }

    // Check for errors during scanning
    if err := scanner.Err(); err != nil {
        log.Fatalf("Error reading file: %v", err)
    }
}
```

To define a size 
