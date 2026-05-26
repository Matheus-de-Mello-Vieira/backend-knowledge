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

## Process