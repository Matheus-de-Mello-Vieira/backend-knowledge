# Compilers, Linkers, and Program Loading

## From Source Code to a Running Process

A native executable is produced through distinct stages. Compilation translates source for a target platform, assembly encodes instructions, and linking combines separately produced parts into an artifact. Loading then maps that artifact into an address space and transfers control to its entry point; execution is the CPU running the resulting process image.

1. **Compile source:** Transform source into target-specific code, commonly as an object file.
2. **Assemble instructions:** Encode assembly mnemonics as machine instructions when assembly is an explicit stage. A compiler can emit object code directly without writing an assembly-text file.
3. **Link an artifact:** Resolve references among object files and libraries, then arrange the resulting executable or library.
4. **Load the artifact:** The operating system reads the executable format, establishes the required mappings and initial execution state, and begins at the declared entry point.
5. **Execute the process:** The CPU runs instructions in the process's virtual address space. The resulting live state is a [process](02%20The%20Anatomy%20of%20a%20Process.md#Program%20vs%20Process), not the program artifact on storage.

Native executables are only one way to supply a program. A script, bytecode file, or other runtime-hosted representation also becomes part of a process when its interpreter or runtime loads and executes it.

## Runtime Environments

A **language runtime** is implementation-provided code and state that participates in executing a program according to a language's semantics. It runs inside a process: the operating system creates and schedules that process, while the runtime uses CPU instructions and operating-system services to execute and manage the program. A runtime is therefore neither the operating system nor the process itself.

Its responsibilities depend on the language and implementation:

- **Initialization:** Establish program state and invoke the language's entry point.
- **Execution strategy:** Interpret source or bytecode, compile portions just in time, or begin execution of already-native code.
- **Language services:** Provide mechanisms such as allocation, garbage collection, exception handling, stack management, or user-space scheduling when the implementation requires them.
- **Platform interaction:** Request memory, I/O, threads, timers, and other operating-system services as the program needs them.

An ahead-of-time native program can have a relatively small runtime, such as startup code and support libraries, while a virtual machine or interpreter performs more visible execution work. The standard library is not normally the runtime itself, although library operations can depend on runtime-managed mechanisms.

The word **runtime** is also used more broadly. ["*At runtime*"](#Runtime%20Compilation) means during execution rather than during compilation; ["*runtime binding*"](#Dynamic%20Linking) refers to work that a dynamic linker performs after loading or while the process executes. Neither phrase necessarily denotes a language runtime environment.

Concrete implementations expose different parts of this machinery: the [Go runtime](../Technologies/Golang/99%20Misc/Go%20Internals.md#The%20Go%20Runtime) manages goroutines and language-specific memory behavior; [Node.js](../Technologies/NodeJS/01%20Basics/02%20Terms%20and%20concepts.md#Node.JS) provides a JavaScript execution environment around V8 and platform APIs; and a [Python implementation](../Technologies/Python/Python%20Internals.md#The%20Execution%20Model:%20Interpreted%20at%20Runtime) loads and executes Python representations using an implementation-dependent strategy.

## Compilation and Assembly

A compiler translates source into a representation for a chosen instruction-set architecture. Its output must obey the target architecture's instruction set and the platform's binary conventions; source compatibility alone does not make the resulting native artifact executable on another platform.

Assembly language expresses target instructions as readable mnemonics. An assembler translates those mnemonics into machine-code encodings. The generated instructions operate on architectural resources such as registers and memory addresses rather than source-level variable names.

Memory diagrams use a drawing convention: the lowest address can appear at the top or bottom of a diagram, but address ordering itself does not change. Byte order is also target-dependent. On a little-endian target, the least-significant byte of a multi-byte instruction encoding is stored at the lowest address; for example, `0xE3A00001` occupies memory as `01 00 A0 E3` in increasing-address order.

## Compiler-Generated Code

The compiler is free to transform the program while preserving the language's required observable behavior. The emitted instruction sequence therefore need not mirror the source structure.

- **Constant folding:** The compiler evaluates constant expressions during compilation instead of emitting runtime work for them.
- **Dead-code elimination:** Computation whose result cannot affect the program is removed.
- **Register allocation:** Temporary values are placed in registers when possible; generated code loads from or stores to memory when it must access values outside those registers.
- **Auto-vectorization:** When a loop's dependencies and memory access permit it, the compiler can replace scalar operations with [SIMD](04%20Inside%20The%20CPU.md#Single%20Instruction%2C%20Multiple%20Data%20%28SIMD%29) instructions that operate on several packed lanes at once.

These transformations reduce work or increase throughput, but they also make the generated instructions diverge from source-level control flow and variables. Optimized debugging can therefore show values that have been eliminated, kept only in registers, or moved relative to the source statement.

> [!warning] Optimization Boundaries
> `volatile` in C constrains compiler optimization of accesses to a qualified object, which is important when polling locations such as memory-mapped [device registers](99%20More%20OS%20Concepts.md#Device%20drivers). It does not provide the synchronization required to make concurrent access free of data races. Compiler reordering that preserves single-threaded language semantics can still violate an unsynchronized cross-thread assumption; concurrent code needs the language's synchronization and atomicity mechanisms.

## Object Files, Symbols, and Relocations

<!-- Repository evidence currently supports the pipeline's object-file stage but does not yet support a durable explanation of object-file records, symbol resolution, relocations, or archive selection. -->

## Linking

The linker combines object files and selected library code, resolves references among them, and arranges the output artifact. This makes separate compilation practical: one source unit can be compiled without first combining every other unit into a single source file.

- **Static linking:** The linker incorporates the object code needed from static libraries into the output artifact. It does not copy every member of every library wholesale. The result has fewer runtime library dependencies, but portability still depends on the target architecture, operating-system and ABI expectations, and any remaining runtime assumptions.
- **Dynamic linking:** The output records dependencies and information needed to bind externally supplied code at load or runtime. It does not contain direct pointers to one exact library version. The platform's dynamic-linking conventions determine how compatible library implementations are identified and bound.

## Executable Formats and Program Loading

An executable format packages machine code, data, and metadata so the operating system can construct a process image. PE, ELF, and Mach-O are platform-specific examples. Their exact structure varies, but the loader uses the artifact's metadata to:

- locate loadable material;
- establish initial mappings;
- find the entry point; and
- discover dynamic dependencies where applicable.

Compiler and linker artifacts distinguish **sections** from the **segments** that are mapped into a process. Common sections include:

- **`.data`:** Initialized writable static storage.
- **`.bss`:** Zero-initialized static storage without requiring the same bytes to be stored in the file.
- **`.rodata`:** Read-only constants and string literals.

The linker groups such sections into loadable segments; the loader maps those segments into the process's virtual address space. The exact grouping and addresses are format- and platform-dependent.

The loader applies memory permissions to those mappings. Code is normally mapped readable and executable rather than writable, while mutable data is writable and non-executable. This separation supports **W^X**: a mapping should not be writable and executable at the same time, which prevents injected writable data from being executed directly. [Page-table permission enforcement](03%20Memory%20Management.md#Page-Table%20Entries%20and%20Protection) produces this virtual-memory behavior.

## Dynamic Linking

A dynamically linked executable relies on separately supplied shared libraries. The dynamic-linking metadata describes dependencies and the references that must be bound rather than storing absolute in-process addresses for a particular library image. The operating system and dynamic loader establish the required mappings and bindings according to the platform's conventions.

> [!warning] DLL Hell
> **DLL hell** is a failure mode of shared-library deployment in which different programs require incompatible versions of a library identified by the same name. Replacing a system-wide library to satisfy one program can then cause another program to load an incompatible implementation and fail or behave incorrectly. The term originated on Windows, but the underlying versioning and dependency-resolution problem is not Windows-specific. Platforms mitigate it through mechanisms such as versioned libraries, side-by-side installation, application-private dependencies, and explicit dependency metadata; the available mechanisms and their guarantees are platform-dependent.

Processes still have separate virtual address spaces. When the same compatible shared-library code is mapped by several processes, those mappings can refer to the [same physical frames](03%20Memory%20Management.md#Controlled%20Sharing%20%26%20Concurrency) while each process retains its own virtual-address translations and other process state.

## ABI and Separate Compilation

An **application binary interface (ABI)** defines the binary-level agreements that independently compiled components must share. It includes a calling convention, but is broader than one: calling conventions specify how functions receive arguments, return results, preserve registers, and manage stack-related obligations, while the ABI also constrains other binary-facing details for the platform.

Those agreements let separately compiled code interoperate only when the relevant binary interfaces are compatible. At a call boundary, generated code follows the calling convention so the callee can find its arguments and the caller can interpret the result; the [stack-frame consequences](02%20The%20Anatomy%20of%20a%20Process.md#The%20Stack) follow from those requirements.

## Runtime Compilation

A runtime-hosted program need not be ahead-of-time compiled into a native executable. An implementation can interpret a representation such as source or bytecode, compile portions of it just in time (JIT), or combine both approaches. The language alone does not determine which execution strategy a particular implementation uses.

### Bytecode

**Bytecode** is an instruction representation for a language-specific or runtime-specific virtual machine, rather than for the CPU's instruction-set architecture. A bytecode compiler translates source into bytecode instructions; the runtime then loads that representation and supplies the virtual-machine operations that give those instructions meaning.

- **Interpretation:** The runtime reads bytecode instructions and performs their operations, typically by executing native instructions in an interpreter loop.
- **JIT compilation:** The runtime translates selected bytecode regions into native instructions for the current CPU, then executes that generated code.
- **Portability boundary:** The same bytecode can run on systems that provide compatible virtual-machine implementations. It is not itself a native executable: compatibility still depends on the bytecode format and semantics accepted by the runtime, and the runtime must be available for the target platform.

A JIT that produces native instructions must make those instructions executable before the CPU runs them. This is a security-sensitive boundary: a defect in the runtime's compilation or validation logic can turn attacker-controlled input into unsafe native instructions. Under W^X, the JIT writes generated code through a writable non-executable mapping or phase, then changes permissions before executing it. This prevents a writable code page from being directly executed, but it does not establish that generated code is safe or eliminate flaws in the JIT itself; exact mechanisms are platform-dependent.
