# Processes

## Program vs Process

- **Program:** A static, compiled executable file sitting dormant on your storage drive.
- **Process:** An active, running instance of that program. It is a "program in motion." When the OS launches a program, it creates a process by allocating it a unique identifier (PID) and its own isolated virtual address space to store its state and active data.
- **One-to-Many Relationship:** A single program can spawn multiple distinct processes. For example, opening three separate terminal windows launches three completely independent processes that all originate from the exact same underlying executable file.
- **Executable Formats:** Executables are structured in strict formats dictated by the OS (such as **PE** for Windows, **ELF** for Linux, and **Mach-O** for macOS). These formats are not just raw machine code; they contain essential metadata and headers that tell the OS exactly how to load the file into memory, where execution should start, and what external libraries are required.

## Program

- **Definition:** A program is a static, executable file containing code that has been explicitly compiled and linked for a specific CPU.
- **Compilation:** The process of transforming human-readable programming languages into raw machine code. Because every CPU family has its own unique set of machine-level instructions, the compilation process is highly dependent on the target CPU architecture (e.g., x86 vs. ARM). Consequently, a compiled program will _only_ work on the specific architecture it was built for.
- **Linking:** The final step of the build process that connects your compiled code with the external software libraries it relies on.
    - **Static Linking:** Embeds a complete, physical copy of all used libraries directly into your final executable file. This makes the resulting file larger, but entirely self-contained and portable across systems with the same CPU architecture.
    - **Dynamic Linking:** Instead of embedding the actual code, the executable only includes references (pointers) to a specific version of a library. The OS resolves these references and loads the library into memory when the program is executed. On Windows, these external files are known as **DLLs** (Dynamic Link Libraries), while Linux refers to them as Shared Objects (`.so`).
- **Executable Formats:** The final output of the compilation and linking process is packaged into a structured executable format (such as PE for Windows or ELF for Linux). This format contains the essential headers and metadata the OS needs to correctly load the program's machine code into memory.

## Process Execution and State

- **Virtual Memory Layout:** When an active process lives in memory, it operates within a completely isolated, private virtual address space spanning from a minimum to a maximum address. This space is divided into distinct regions:
    - **Text/Code:** The region starting near the minimum address where the actual compiled machine instructions are loaded.
    - **Data/Static:** Stores initialized and uninitialized global variables.
    - **Heap:** Starts just after the data segment and grows _upwards_. It is used for dynamic memory allocation (e.g., when a program requests more memory at runtime).
    - **Stack:** Starts at the maximum address and grows _downwards_ (towards the heap). It stores local variables, function calls, and execution context.
- **Process Identification (PID) & Namespaces:**
    - **PID Wraparound:** Every process is uniquely identified by an ID. The kernel increments this sequentially. Once the OS hits its maximum PID limit (e.g., 32,768 on default Linux), it wraps around and _reuses_ available PIDs from dead processes. Security is maintained because the kernel completely destroys the old process's page tables upon termination, ensuring no residual data can be accessed.
    - **Namespaces:** The kernel uses Namespaces to isolate PID lists. This allows multiple processes across different Docker containers and the host system to all possess the exact same PID (e.g., PID `700`) simultaneously. The kernel internally pairs the Namespace + PID to uniquely isolate and identify them, completely hiding them from one another.
- **Instruction Pointer (Program Counter):**
    - The Instruction Pointer (IP) tracks the exact virtual address of the next instruction to be executed from the Text/Code segment.
    - **Hardware Register Execution:** The IP is an ultra-fast hardware register located physically inside the CPU. Because it is a CPU register, it increments automatically with every single execution cycle at zero performance penalty.
- **Process Control Block (PCB):**
    - The PCB is a vital data structure residing securely in Kernel Space memory. It acts as the process's master metadata record, storing its PID, open file descriptors, memory limits, and state.
    - **Context Switching Overhead:** Because the PCB lives in system memory (RAM), reading and writing to it involves latency. When the kernel performs a context switch, it must physically copy the current value of the CPU's Instruction Pointer register—and all other working registers—into the PCB in memory to save the process's state. This RAM-dependent save/load cycle is a primary reason context switching is computationally expensive.

## Producing machine code

During compilation, high-level human-readable code is translated into low-level assembly language. Given this C code:
```c
#include <stdio.h>

int main ()
{
    int a = 1;
    int b = 3;
    int c = a + b;
    printf("a + b = %d", c);

    return 0;
}
```
This assembly represents the exact, step-by-step machine instructions the target CPU architecture will execute.

```armasm
mov r0, #1
mov r1, #3
add r3, r0, r1
str r3, #0xffeeddcc
```

- **CPU Registers (`r0`, `r1`, `r3`):** Notice that the assembly code does not use variable names like `a` or `b`. Instead, it uses **registers**. These are the ultra-fast, temporary storage locations physically built directly into the CPU core. Before the CPU can do math on data, that data must be loaded into a register.
- **Instruction Breakdown**
	- `mov r0, #1` **and** `mov r1, #3`: The `mov` (move) instruction loads the literal, hardcoded numbers (`#1` and `#3`) directly into the CPU registers `r0` and `r1`.
	- `add r3, r0, r1`: The CPU's computation hardware (the ALU) reads the values held inside `r0` and `r1`, adds them together, and immediately saves the resulting sum into a new register, `r3`.
	- `str r3, #0xffeeddcc`: The `str` (store) instruction takes the computed result out of the CPU's internal register (`r3`) and writes it out to system memory. The sequence `#0xffeeddcc` is a hexadecimal virtual memory address. 
### Compiler Optimization
In the previous example, `a` and `b` are hardcoded constants (`1` and `3`). A modern compiler will realize that there is no reason to force the CPU to calculate `1 + 3` every single time the program runs. Instead, the compiler does the math itself _during_ the compilation phase. It simply "folds" the constants together into the final value of `4`.    
- **Dead Code Elimination:** Because the original variables `a` and `b` are never used again after `c` is calculated, the compiler won't even bother wasting CPU registers or stack memory on them. It completely strips those steps out of the final executable.

```armasm
mov r3, #4
str r3, #0xffeeddcc
```

By doing this work at compile time, the resulting program is smaller (takes up less disk space and memory) and faster (requires fewer execution cycles from the CPU's ALU) while producing the exact same final output.

> [!note] The Side Effects of Compiler Optimization
> While optimizations make programs faster and smaller, altering the underlying machine code can introduce unintended consequences, particularly in low-level systems programming.
> - **Debugging Nightmares:** Because the compiler fundamentally changes the structure of the code—removing variables entirely or rearranging logic—the resulting assembly no longer maps 1:1 with your human-readable source code. If you try to step through a highly optimized program with a debugger, variables you want to inspect may simply not exist in memory or CPU registers, making troubleshooting extremely difficult.    
> - **Breaking Hardware Polling:** As noted in the [Device Drivers](System%20Architecture%20Overview.md#Device%20Drivers) section, high-speed hardware often relies on "polling," where the CPU constantly checks a specific memory address for new data. If you write a loop that constantly checks a variable (e.g., `while(status == 0)`), an aggressive compiler will assume that since the _software_ isn't changing `status` inside the loop, the check is redundant. It will optimize the read away, breaking the driver. To prevent this, developers must use the `volatile` keyword in C, which strictly forbids the compiler from optimizing reads and writes to that specific memory location.
  > - **Instruction Reordering in Concurrency:** Compilers often rearrange the order of machine instructions to maximize CPU efficiency. In an isolated, single-threaded process, this is perfectly safe. However, if multiple threads are running concurrently across different CPU cores, this reordering can cause disastrous synchronization bugs (data races) if one thread depends on memory being updated in the exact sequential order written in the original source code.
### Assembling into Machine Code

 While assembly language is incredibly low-level, it is still text designed for humans to read. The CPU hardware cannot natively execute a string of characters like `add r3, r0, r1`. A tool called an **Assembler** must translate these textual mnemonics into raw binary machine code (opcodes)—the actual sequence of 1s and 0s that trigger the CPU's physical electrical circuits.
 
|Assembly Instruction|Binary Machine Code|Hexadecimal|
|---|---|---|
|`mov r0, #1`|`11100011 10100000 00000000 00000001`|`0xE3A00001`|
|`mov r1, #3`|`11100011 10100000 00010000 00000011`|`0xE3A01003`|
|`add r3, r0, r1`|`11100000 10000000 00110000 00000001`|`0xE0803001`|

- **Direct-to-Binary (Skipping the Assembly File):** While compilation is conceptually a multi-step pipeline (Source Code -> Assembly -> Machine Code), modern compilers (like Clang or GCC) often skip generating a physical, intermediate assembly text file. To optimize the build process and reduce disk I/O, they translate the high-level code directly into binary object files in memory.
- **Just-In-Time (JIT) and Interpreted Languages:** The traditional ahead-of-time (AOT) assembly step is bypassed entirely by languages like Python, JavaScript, and Java. Instead of pre-compiling a static executable bound to a specific CPU architecture, these languages rely on a runtime engine. The engine either interprets the code line-by-line or uses a JIT compiler to generate the necessary raw machine instructions on the fly, right as the program is executing.