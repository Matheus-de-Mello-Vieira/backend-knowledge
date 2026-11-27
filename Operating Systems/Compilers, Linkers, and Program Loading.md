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

Concrete implementations expose different parts of this machinery: the [Go runtime](../Technologies/Golang/99%20Misc/Go%20Internals.md#Runtime%20Execution%20Model) manages goroutines and language-specific memory behavior; [Node.js](../Technologies/NodeJS/01%20Basics/02%20Terms%20and%20concepts.md#Node.JS) provides a JavaScript execution environment around V8 and platform APIs; and a [Python implementation](../Technologies/Python/Python%20Internals.md#Source%20to%20code%20object) loads and executes Python representations using an implementation-dependent strategy.

## Compilation and Assembly

A **compiler** translates a program into another representation, such as native machine code or virtual-machine bytecode. The target determines the available instructions and the rules for encoding code and metadata. A bytecode target defines those rules for a software-defined machine rather than a physical CPU. A native artifact must also obey its platform's binary conventions: source compatibility alone does not make a compiled artifact runnable on another platform.

### Front End: Text, Syntax, and Bindings

The front end establishes what the source means before the compiler selects instructions. These tasks depend on one another, but implementations need not perform each as a separate pass or retain every intermediate representation:

1. **Decode and tokenize:** If the source arrives as bytes, decode it to text. Tokenization (lexical analysis) groups text into units such as identifiers, literals, and operators. Which characters form tokens depends on the language.
2. **Parse:** Use the grammar to determine how those units form expressions, statements, and declarations. A parser that builds an **abstract syntax tree (AST)** records the meaningful nesting of constructs, not their evaluated values or active calls. If the language gives multiplication higher precedence than addition, the tree for `a + b * c` makes multiplication a child of addition.
3. **Analyze semantics:** Check rules beyond grammatical structure and determine what the language allows the compiler to resolve in advance. Binding analysis relates uses of names to declarations or scopes; a **symbol table** records information about those names. For an implementation that stores locals in frame slots, knowing the binding lets generated code address the slot directly. The compiler need not know the value in that slot, and names resolved against dynamic environments still require runtime lookup.

### Intermediate Representations and Control Flow

Source structure is convenient for checking language rules but does not directly expose every possible transfer of control. An **intermediate representation (IR)** describes the program between source analysis and final emission. A compiler may use several IRs: a higher-level one preserves source concepts, while a lower-level one makes operations, storage, and transfers explicit.

In a block-level **control-flow graph (CFG)**, the nodes are **basic blocks**: straight-line instruction sequences entered at the start. Edges represent possible transfers between blocks. A conditional branch has edges to its possible successors, and a loop forms a cycle. Making those paths explicit lets an analysis ask which blocks are reachable and which values can reach a use along different paths.

### Lowering and Target Emission

**Lowering** replaces an operation with simpler operations closer to the target. For example, a structured loop can become a test, a conditional branch, and a jump back to the test. Lowering and optimization can alternate as progressively more concrete representations expose different constraints and opportunities.

- **Native emission:** Select and encode instructions for the processor. Assembly language expresses these instructions as readable mnemonics; an assembler converts them to machine-code encodings. A compiler can also emit object code without writing assembly text. The processor operates on architectural resources such as registers and memory addresses, not source-level names.
- **Bytecode emission:** Select operations defined by a virtual machine. If code generation uses symbolic labels or temporary operations, assembly resolves labels to instruction offsets and turns temporary operations into real instructions or metadata. The bytecode format determines what accompanies the instruction stream, such as constant pools, source locations, stack requirements, or exception-handler information.

> [!example] Native Instruction Byte Order
> Memory diagrams use a drawing convention: the lowest address can appear at the top or bottom of a diagram, but address ordering itself does not change. Byte order is also target-dependent. On a little-endian target, the least-significant byte of a multi-byte instruction encoding is stored at the lowest address; for example, `0xE3A00001` occupies memory as `01 00 A0 E3` in increasing-address order.

## Compiler-Generated Code

The compiler is free to transform the program while preserving the language's required observable behavior. The emitted instruction sequence therefore need not mirror the source structure.

- **Constant folding:** Evaluate an expression at compile time when its value is known and doing so preserves the language's required behavior.
- **Dead-code elimination:** Remove unreachable code or unused computations whose removal does not change observable behavior.
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
- **JIT compilation:** The runtime compiles selected portions of the program to native instructions for the current CPU, then executes those instructions. It may first translate the relevant bytecode operations into an intermediate representation.
- **Portability boundary:** The same bytecode can run on systems that provide compatible virtual-machine implementations. It is not itself a native executable: compatibility still depends on the bytecode format and semantics accepted by the runtime, and the runtime must be available for the target platform.

### Code, Callables, and Activations

Compilation produces instructions and metadata, not the live state of future calls. In runtimes that represent function values separately from their compiled code, that separation appears in three layers:

- **Compiled code:** Instructions and static information used to execute or inspect them, such as constants, binding information, and source locations.
- **Function value:** A reference to compiled code, together with any captured environment the function needs. Multiple function values can share the same compiled code while retaining different environments. Where closures capture a shared binding rather than a value, rebinding is visible through that shared environment.
- **Activation:** The live state of one invocation (represented by a frame in many runtimes), including where execution is, its arguments and locals, and any temporary state required by the execution model. Recursive calls use distinct activations even when they invoke the same callable. An implementation that supports suspension retains enough activation state to resume without necessarily preserving a dedicated native thread or stack.

### Operand Stacks and Call Stacks

In a **stack-based virtual machine**, instructions take temporary operands from an operand stack and put results back on it. A binary addition, for example, consumes two operands and pushes one result. A **call stack**, by contrast, tracks active calls and the state needed to resume their callers; a returning callee hands its result back to the caller. These are distinct roles even if their storage is combined. The VM's call stack also need not correspond one-to-one to the native call stack: an interpreter loop can switch between VM frames without making a native call for every VM call.

### Exception Metadata and Unwinding

An exception transfers control away from the ordinary path. In **table-driven exception handling**, the compiler emits metadata mapping protected instruction ranges to handler entries, with any restoration information the implementation needs. Raising an exception triggers a search from the failing instruction or call site. If a handler applies, execution transfers to it with the required state; otherwise propagation unwinds the activation and proceeds outward, carrying out required cleanup along the way.

Moving handler registration into static metadata avoids maintaining a handler stack on ordinary entry to and exit from protected regions. The trade-off is metadata storage and work when an exception is raised, including handler search, state restoration, and cleanup. “Zero-cost” refers to avoiding that normal-path bookkeeping, not to exceptions being free to raise.

### Feedback, Specialization, and Guards

A dynamic operation must handle all operand types or layouts the language permits, but repeated executions at one instruction site may use only a small subset. An adaptive runtime uses **feedback** from execution to select a faster path for the observed case. This is **specialization**: for example, a generic operation can be replaced by a type-specific operation, or a lookup can reuse a cached storage position rather than searching again. Caching a position need not freeze the value stored there.

The fast path is valid only while its assumptions hold. A **guard** tests an assumption at execution time, and some runtimes also invalidate specialized code when a dependency changes. If a guard fails, execution falls back to a path that implements the operation without that assumption; the runtime may later specialize for a different case. Specialization does not require generation of native code. Its benefits depend on whether avoided work outweighs profiling, warm-up, guards, cache storage, and repeated fallback at sites with varied inputs.

### Tracing JIT Compilation

A **tracing JIT** takes a path recorded during execution as its compilation unit. A method-based JIT instead starts from a static unit such as a function body, though it can still use execution feedback. Unlike per-site specialization, trace optimization sees the operations on the recorded path together:

1. Once execution reaches a hot region (one that runs frequently enough to justify more compilation work), the runtime records an actual path through it.
2. The optimizer transforms the recorded sequence and emits native code for it. Seeing several operations together exposes work that cannot be removed safely by optimizing each operation in isolation.
3. On later entries, guards ensure execution still fits that path's assumptions. A failed guard or a branch away from the recorded path takes a **side exit** to another execution path. If optimized state differs from the state expected there, **deoptimization** reconstructs the state needed to resume at the corresponding program point.

A runtime can support JIT compilation without enabling it, or enable it without reaching a region that qualifies. Any speedup depends on reuse of the compiled paths offsetting recording, compilation, and exit costs.

### Execution of Generated Native Code

A JIT that produces native instructions must make those instructions executable before the CPU runs them. This is a security-sensitive boundary: a defect in the runtime's compilation or validation logic can turn attacker-controlled input into unsafe native instructions. Under W^X, the JIT writes generated code through a writable non-executable mapping or phase, then changes permissions before executing it. This prevents a writable code page from being directly executed, but it does not establish that generated code is safe or eliminate flaws in the JIT itself; exact mechanisms are platform-dependent.
