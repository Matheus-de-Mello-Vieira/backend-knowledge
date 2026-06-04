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
### SIMD (Single Instruction, Multiple Data)

- **Scalar vs Vector:** The standard assembly instructions (like the `add` example above) are **scalar**; they perform one mathematical operation on one set of numbers at a time. SIMD introduces **vector** processing, allowing the CPU's ∂ to execute the exact same instruction on a large batch of data simultaneously within a single clock cycle.    
- **Massive Registers:** To achieve this, modern CPUs include specialized, extra-wide hardware registers (often 128, 256, or even 512 bits wide). Instead of loading a single 32-bit integer into a register, the CPU can pack four, eight, or sixteen integers into one giant SIMD register.
    - _Architecture Note:_ On x86 processors, these SIMD extensions are known as **SSE** or **AVX**. On modern ARM processors, the SIMD architecture is called **NEON**.
- **Auto-Vectorization (Compiler Optimization):** You rarely write SIMD assembly by hand. If you write a simple `for` loop in C that adds two large arrays together, an optimizing compiler will recognize the pattern. Through a process called auto-vectorization, the compiler completely rips out your scalar loop and replaces it with SIMD machine code, processing the arrays in massive parallel chunks to drastically improve execution speed.
- **Use Cases:** SIMD is heavily utilized for workloads that require repetitive, predictable math on large datasets, such as graphics rendering, video encoding, cryptography, and machine learning matrices.
### Assembling into Machine Code

 While assembly language is incredibly low-level, it is still text designed for humans to read. The CPU hardware cannot natively execute a string of characters like `add r3, r0, r1`. A tool called an **Assembler** must translate these textual mnemonics into raw binary machine code (opcodes)—the actual sequence of 1s and 0s that trigger the CPU's physical electrical circuits.
 
|Assembly Instruction|Binary Machine Code|Hexadecimal|
|---|---|---|
|`mov r0, #1`|`11100011 10100000 00000000 00000001`|`0xE3A00001`|
|`mov r1, #3`|`11100011 10100000 00010000 00000011`|`0xE3A01003`|
|`add r3, r0, r1`|`11100000 10000000 00110000 00000001`|`0xE0803001`|

- **Direct-to-Binary (Skipping the Assembly File):** While compilation is conceptually a multi-step pipeline (Source Code -> Assembly -> Machine Code), modern compilers (like Clang or GCC) often skip generating a physical, intermediate assembly text file. To optimize the build process and reduce disk I/O, they translate the high-level code directly into binary object files in memory.
- **Read-Only Text Segment (Security & Caching):** Once the machine code (the Text/Code segment) is loaded into virtual memory, the OS enforces strict hardware-level protection marking that region as **read-only** and **executable** (a principle known as Write XOR Execute, or W^X).
	- **Security:** If an application could write to its own code segment, malicious actors could exploit bugs (like buffer overflows) to inject and execute their own rogue machine instructions.
	- **Cache Coherency:** Because the CPU knows the instructions will never change, it can aggressively load them into the L1 cache without ever worrying about complex cache coherency issues or invalidating the data.
- **Just-In-Time (JIT) and Interpreted Languages:** The traditional ahead-of-time (AOT) assembly step is bypassed entirely by languages like Python, JavaScript, and Java. Instead of pre-compiling a static executable bound to a specific CPU architecture, these languages rely on a runtime engine. The engine either interprets the code line-by-line or uses a JIT compiler to generate the necessary raw machine instructions on the fly, right as the program is executing.
	- **The JIT Memory Challenge:** The runtime engine uses a JIT compiler to generate raw machine instructions on the fly. Because of the strict read-only security rule mentioned above, the JIT compiler has to constantly juggle memory permissions—requesting writable memory from the OS to generate the new machine code, and then explicitly changing that memory's permission to read-only/executable before the CPU is allowed to run it.
- **Memory Representation (Top vs. Bottom):** The first instruction is always stored at the lowest memory address. If you are looking at an academic memory diagram where the lowest address is drawn at the bottom, the machine code is represented **bottom-to-top**. However, if you are looking at a real-world debugger or hex editor where the lowest address starts at the top, it is read **top-to-bottom**.
- **Little-Endian Storage:** Many CPU architectures (including most x86 and ARM chips) use a format called **Little-Endian**, meaning the least significant _byte_ is stored at the lowest memory address. This means that while humans read the 32-bit instruction `0xE3A00001` left-to-right, physical RAM stores its byte-chunks in reverse order (`01 00 A0 E3`).

## The Stack

- **LIFO Structure:** The Stack in memory operates strictly as a Last-In, First-Out (LIFO) data structure.
- **Downward Growth:** As established in the memory layout, the stack starts at the highest memory address of its designated virtual space and grows _downwards_ toward the heap.
- **Function Frames:** Every time a function is called, it gets its own dedicated block of memory on the stack called a **Stack Frame**. This frame stores the function's local variables and execution context.
- **The "Top" of the Stack:** The currently active function is always located at the active edge (conceptually called the "top" of the stack, even though it sits at the lowest physical memory address). Because functions strictly follow LIFO, no process can accidentally touch or corrupt the frames of paused, parent functions sitting higher up the stack.
- **Contiguous Memory & Caching:** Stack space is strictly contiguous (sequential). Because the data is packed tightly together, it maximizes **spatial locality**. This makes it incredibly easy for the CPU to predict and load stack data into the ultra-fast L1/L2 caches, making stack memory significantly faster to access than heap memory.
- **Size Limits:** Stack space is strictly limited in size (typically a few megabytes per thread) because it must remain a continuous block of virtual memory.

### Stack Pointer (`sp`)

- **Definition:** A dedicated CPU register that holds the memory address of the very edge (the lowest address) of the currently active frame.
- **Allocation via Math:** Creating local variables doesn't require complex system calls. The compiled code simply subtracts bytes from the `sp` to "grow" the frame downwards, reserving the necessary space.
- **Lazy Deallocation:** When a function finishes, the CPU doesn't waste time physically deleting or wiping the old data. It simply moves the `sp` back upwards. The old data remains in RAM (as garbage) and will just be naturally overwritten the next time the stack grows downwards.
- **Intra-Frame Deallocation:** Deallocating individual variables inside an active frame is rarely done. The CPU simply waits for the function to return and deallocates the entire frame at once by moving the `sp`.

### Base Pointer (`bp` / Frame Pointer)

- **Definition:** Another dedicated CPU register that holds the starting address (the highest address) of the currently active frame.
- **The Anchor:** Because the Stack Pointer (`sp`) constantly moves up and down as local variables are pushed or popped, it is a terrible reference point for finding specific data. The Base Pointer (`bp`) solves this by acting as a fixed anchor for the duration of the function.
- **Variable Referencing:** Once the `bp` is set, the compiler can reliably find any local variable using fixed offsets (e.g., `bp - 8 bytes` or `bp - 16 bytes`), regardless of what the `sp` is currently doing.
- **Frame Pointer Omission (FPO):** While the Base Pointer is the standard anchor, it is not strictly mandatory. If a function's stack frame has a fixed, known size at compile time, modern compilers can track all local variables simply by calculating offsets directly from the moving Stack Pointer (`sp`). Through an aggressive optimization called Frame Pointer Omission, the compiler discards the Base Pointer entirely, freeing up that valuable CPU register for general computation to improve execution speed—though this trade-off makes debugging and reading stack traces significantly more difficult.
### Nested Calls & Context Switching

When an active function (`func1`) calls a new function (`func2`), `func2` must become the new active frame. The machine code executes a specific sequence to preserve the state safely:

1. **Save the Return Address:** The system saves the exact instruction address where `func1` left off, so it knows exactly where to resume later.
    - _Architecture Note:_ On x86 processors, it is pushed directly into the stack memory. On ARM processors, this is stored in a dedicated CPU register called the **Link Register (LR)** - see [Nested Calls in ARM.](#Nested%20Calls%20in%20ARM%20(The%20Link%20Register%20Problem))
2. **Save the Old Base Pointer:** The current value of `bp` (which anchors `func1`) is pushed onto the stack inside the new `func2` frame.
3. **Update Pointers:** The `bp` is updated to match the current `sp` (establishing the new anchor for `func2`), and the `sp` is moved down to allocate space for `func2`'s local variables.

**When `func2` returns:**

1. The CPU completely collapses `func2`'s frame by setting the `sp` back to the current `bp`.
2. It pops the saved `func1` base pointer off the stack and puts it back into the `bp` register, restoring `func1` as the active frame.
3. It takes the saved Return Address and loads it into the **Instruction Pointer**, seamlessly resuming `func1`'s execution exactly where it paused.
#### Nested Calls in ARM

- **The Link Register Bottleneck:** ARM processors use a single hardware Link Register (LR) to store the return address when a function is called. If `func1` calls `func2`, the LR holds the return address for `func1`. If `func2` then calls `func3`, the hardware will overwrite the LR, permanently losing the way back to `func1`.
- **Leaf vs. Non-Leaf Functions:**
	* A **Leaf Function** is a function that does not call any other functions (it is the end of the branch). It can safely leave its return address in the ultra-fast LR hardware register and use it to return.
    - A **Non-Leaf Function** (like `func2` in our example) _does_ call other functions.
- **Spilling to the Stack:** To prevent the return address from being destroyed, the compiled machine code for a non-leaf function will immediately push the current value of the LR onto the Stack the moment the function starts (in a phase called the function prologue). It gets stored in the memory frame right alongside the Base Pointer.
- **The Return:** When `func2` is finally ready to return to `func1`, it doesn't look at the physical LR hardware register anymore. Instead, it pops the original return address directly off the stack memory and loads it into the Instruction Pointer to safely resume execution.
### Stack Overflow

- **The Cause:** Because stack memory is a fixed, contiguous block, it has a strict size limit. If a program enters an infinite loop of nested function calls (infinite recursion) or tries to allocate massively oversized local variables inside a single frame, the Stack Pointer (`sp`) will continuously move downwards until it entirely runs out of allocated space.
- **The OS Limit:** The maximum size of the stack is primarily enforced by the Operating System (e.g., typically 8MB on Linux), though the compiler/linker can embed a requested stack size into the executable's format headers during the build process.
- **The Guard Page (Protection):** To prevent the downward-growing stack from silently crashing into the upward-growing heap and corrupting application data, the kernel sets up a trap. It places a special, inaccessible memory page at the very boundary of the stack's allowed virtual memory space, known as a **Guard Page**.
- **The Crash (Segmentation Fault):** If the Stack Pointer (`sp`) reaches the limit and attempts to write data into the Guard Page, the CPU's Memory Management Unit (MMU) instantly detects a permission violation. The hardware triggers an interrupt, and the kernel ruthlessly kills the process to protect the rest of the system memory. This fatal crash is the infamous "Stack Overflow."

## The Data Section

- **Definition & Size:** This section of virtual memory stores global and static variables. Because the compiler knows exactly how many global variables exist in the code, the total size of the Data section is strictly fixed at compile time.
- **Memory Placement:** It resides in memory immediately above the Text/Code segment.
- **The Compiler Split (`.data`, `.bss`, `.rodata`):** The OS actually divides this region into optimized sub-sections:
    - **`.data`:** Stores initialized global variables (e.g., `int x = 100;`). This section is Read/Write.
    - **`.bss`:** Stores _uninitialized_ global variables (e.g., `int y;`). To save space in the executable file, the OS just zeroes out this memory when the program launches.
    - **`.rodata` (Read-Only Data):** Stores constants and string literals (e.g., `"Hello World"` or `const int z = 5;`). The hardware strictly enforces this as read-only.
- **Addressing:** Unlike local stack variables (which are found using offsets from the moving Stack/Base pointers), variables in the Data section reside at fixed, static memory addresses.
- **Cache Coherency Penalty:** While reading global variables is fast, _writing_ to them in a modern multi-core system is costly. If Core A updates a global variable, the hardware must instantly trigger "cache invalidation" signals to Cores B, C, and D, forcing them to flush their local caches and fetch the newly updated value from RAM to avoid data corruption.

### Spatial Locality and Caching

Because the Data section is packed sequentially, it heavily benefits from CPU caching behavior.

```armasm
// Assuming r2 holds the base memory address of the Data section
ldr r0, [r2, #0]   // Load the first variable into r0
ldr r1, [r2, #4]   // Load the adjacent variable (4 bytes away) into r1
```

- **The Cache Line:** When the first instruction (`ldr r0`) executes, the CPU doesn't just fetch 4 bytes from RAM. It fetches an entire **Cache Line** (typically 64 bytes of contiguous memory) and stores it in the ultra-fast L1 Cache.
- **The "Free" Read:** When the second instruction executes, the CPU realizes the data at `[r2, #4]` was already pulled into the L1 Cache during the previous step. This results in a "Cache Hit," meaning the second variable is loaded almost instantly with zero RAM latency.
