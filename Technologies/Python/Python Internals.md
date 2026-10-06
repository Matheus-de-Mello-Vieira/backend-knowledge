# Python Internals

## Scope and implementation baseline

Python defines a language; CPython implements it using a compiler, runtime, object model, and standard library. Compilation and interpretation are stages, not mutually exclusive identities: CPython compiles source to code objects, executes bytecode, specializes suitable operations, and optionally compiles selected execution traces to native code.

The implementation baseline is **CPython 3.14.7**. Source links use the `v3.14.7` tag; rolling Python 3.14 documentation can describe a later patch. Scope labels apply to the following paragraphs, lists, and tables until another label or heading changes the scope:

- **Language guarantee:** Python semantics, independent of CPython representation.
- **Standard-library contract:** Documented API behavior, with platform/build conditions stated separately.
- **CPython 3.14.7:** Private runtime structures and implementation mechanisms.
- **CPython experimental/optional:** Features requiring a particular build or runtime configuration.
- **OS-specific:** Integration that depends on the operating system.
- **Other implementation:** Explicit portability differences.

**CPython 3.14.7:** Bytecode, private frame layouts, allocator internals, and underscore-prefixed C interfaces are not stable interfaces. Framework deployment, numerical-library internals, and general FFI design are outside this scope. [API stability](https://github.com/python/cpython/blob/v3.14.7/Doc/c-api/stable.rst).

## Process startup and runtime topology

**CPython 3.14.7 / public C API:** After OS [program loading](../../Operating%20Systems/Compilers%2C%20Linkers%2C%20and%20Program%20Loading.md#Executable%20Formats%20and%20Program%20Loading), initialization establishes the runtime before executing an entry point.

1. Preconfiguration establishes early allocator, locale, and encoding choices. Embedders can call `Py_PreInitialize`; configuration operations also preinitialize implicitly where required.
2. Full configuration uses `PyConfig`, or the 3.14 `PyInitConfig` interface, to control interpreter initialization. `PyInitConfig_Create()` starts with isolated defaults.
3. Initialization creates the main interpreter and its `sys`, `builtins`, import state, module dictionary, search path, and `__main__` environment.
4. The launcher executes a script, `-c` command, `-m` module, stdin, or embedded code. These entry modes differ in how source and globals are selected.

Normal configuration permits command-line and environment configuration. Isolated defaults ignore environment variables and argument parsing, disable the user site directory, and avoid installing signal handlers or changing the locale. Embedders can override configuration fields; isolation is not a security sandbox or a separate process. [Initialization configuration](https://github.com/python/cpython/blob/v3.14.7/Doc/c-api/init_config.rst).

**CPython 3.14.7:** Execution state is partitioned by lifetime and association:

- **Runtime state (`_PyRuntimeState`):** Process-global coordination and interpreter management.
- **Interpreter state (`PyInterpreterState`):** An interpreter's modules, builtins, import machinery, and execution configuration.
- **Thread state (`PyThreadState`):** Interpreter association, exception state, and execution bookkeeping for a native thread using Python.

A native thread must have an **attached thread state** to execute Python or use APIs requiring attachment. In the ordinary build, attaching generally requires the associated GIL. Attachment remains necessary in a free-threaded build for interpreter association and GC coordination even when there is no GIL to acquire. [Runtime structures](https://github.com/python/cpython/blob/v3.14.7/Include/internal/pycore_runtime_structs.h), [thread-state rules](https://github.com/python/cpython/blob/v3.14.7/Doc/c-api/threads.rst).

**Public C API / CPython 3.14.7:** `Py_FinalizeEx` performs best-effort shutdown, not orderly application resource management. Module/global clearing and destruction order are not dependable; extension libraries are not generally unloaded, and finalizers can encounter partially torn-down globals. During late finalization only the finalization thread may attach normally; other attachment attempts can block until exit, with some API paths documented as unsafe. Stop workers and close resources before teardown; daemon threads and foreign callbacks must not assume that Python remains available. [Lifecycle](https://github.com/python/cpython/blob/v3.14.7/Doc/c-api/interp-lifecycle.rst), [shutdown implementation](https://github.com/python/cpython/blob/v3.14.7/Python/pylifecycle.c).

## Source to code object

**CPython 3.14.7:** The concrete [compiler pipeline](../../Operating%20Systems/Compilers%2C%20Linkers%2C%20and%20Program%20Loading.md#From%20Source%20Code%20to%20a%20Running%20Process) produces executable metadata before evaluation:

1. Decode source bytes using the declared or default encoding; tokenize names, literals, operators, and indentation.
2. The PEG parser generated from `Grammar/python.gram` consumes tokens and builds the AST defined by `Parser/Python.asdl`.
3. Validate/preprocess the AST and analyze symbols for each scope before emitting bytecode.
4. Generate an instruction sequence from the AST; build basic blocks and a control-flow graph, optimize it, and compute stack requirements.
5. Assemble bytecode, constants, names, local/cell/free-variable metadata, source locations, and exception tables into a code object.

Whole-scope symbol analysis distinguishes local, global, nonlocal, cell, and free names. A captured local binding from an enclosing function scope, resolved as a free variable in the nested function, requires an enclosing cell and an inner free-variable reference; module globals and ordinary class-namespace bindings do not follow this rule. Whole-scope analysis matters because the compiler cannot decide that solely when an individual name executes. [Compiler design](https://github.com/python/cpython/blob/v3.14.7/InternalDocs/compiler.md), [symbol analysis](https://github.com/python/cpython/blob/v3.14.7/Python/symtable.c).

**Language/API distinction, with CPython representation:** These objects answer different questions:

- **Code object:** What compiled instructions and metadata describe the computation? Its Python-visible attributes are immutable, but CPython's private adaptive instructions, caches, instrumentation, and executors change during execution.
- **Function object:** In which environment should that code run? It associates code with globals/builtins, defaults, closure cells, names, and annotation/call machinery. In 3.14, ordinary annotations are deferred through annotate functions rather than necessarily evaluated when the function is defined.
- **Frame:** What is the state of one invocation? It contains the current instruction position, bindings, and evaluation state.

Imports can obtain a serialized code object from a valid `.pyc` instead of compiling source again. That skips compilation, not module execution. [Code layout](https://github.com/python/cpython/blob/v3.14.7/Include/cpython/code.h), [function layout](https://github.com/python/cpython/blob/v3.14.7/Include/cpython/funcobject.h), [3.14 deferred annotations](https://github.com/python/cpython/blob/v3.14.7/Doc/whatsnew/3.14.rst).

## Bytecode evaluation, frames, and calls

**CPython 3.14.7:** Bytecode uses 16-bit code units containing an opcode and argument byte. `EXTENDED_ARG` extends operands; inline-cache units belong to their instruction and are not independent ordinary opcodes. `_PyEval_EvalFrameDefault` executes generated evaluator code derived from `Python/bytecodes.c`; dispatch technique depends on build/platform. [Interpreter design](https://github.com/python/cpython/blob/v3.14.7/InternalDocs/interpreter.md).

An `_PyInterpreterFrame` combines execution references with locals/cells/free-variable slots and a contiguous evaluation stack. The frame records instruction position; the stack pointer identifies occupied evaluation slots; `co_stacksize` contributes to the required frame storage. This stack is not the native C stack.

- **Ordinary calls:** Most frames use per-thread data-stack chunks.
- **Suspended execution:** Generators and coroutines embed a frame that survives suspension.
- **Introspection:** A Python-visible `PyFrameObject` is materialized when needed for inspection/tracing. If it outlives execution, frame storage ownership can transfer to it.

Thus a logical Python call stack need not contain one native C stack frame per Python call. Ordinary Python-to-Python fast paths push an interpreter frame and continue within the evaluator loop; native callbacks and other paths still use the C stack. This is not Python tail-call elimination. [Frame design](https://github.com/python/cpython/blob/v3.14.7/InternalDocs/frames.md).

**CPython 3.14.7 / C API:** A call binds arguments before its body executes. Generic binding matches positional/keyword arguments, installs defaults and variadic collections, and rejects invalid combinations. The resulting local slots belong to the callee frame. On return, the caller receives the result and callee-owned references are cleaned up; suspension retains state instead, while an exception transfers to handler/unwinding logic.

**Vectorcall** passes argument references in an array and keyword names separately for supporting callable types, avoiding mandatory temporary positional tuples and keyword dictionaries. It changes the C calling convention, not Python argument semantics. Specialized calls can bypass generic work only after their guards establish the required conditions. [Call API](https://github.com/python/cpython/blob/v3.14.7/Doc/c-api/call.rst), [binding and evaluation](https://github.com/python/cpython/blob/v3.14.7/Python/ceval.c).

**CPython 3.14.7:** Eval-breaker checks rendezvous with pending work: signals, pending calls, GIL-drop requests, asynchronous exceptions, GC, and build-specific stop-the-world/reference-count/reclamation coordination. They are not a guaranteed preemption point after every opcode. Long native execution can delay servicing pending work. [Pending-work implementation](https://github.com/python/cpython/blob/v3.14.7/Python/ceval_gil.c).

## Adaptive specialization and optional JIT

### Guarded bytecode specialization

**CPython 3.14.7:** Repeated execution provides feedback at bytecode sites. Suitable operations specialize into narrower fast paths guarded by assumptions; failures return to generic behavior, back off, or cause reconsideration. Python semantics remain unchanged.

- **`LOAD_ATTR`:** Caches applicable type/layout/descriptor assumptions so repeated attribute access avoids general lookup.
- **`LOAD_GLOBAL`:** Uses namespace/key information and cached locations rather than repeating the complete global/builtins search.
- **`BINARY_OP`:** Selects guarded operand-specific implementations.
- **`CALL`:** Uses callable/version/argument-shape assumptions for a faster call path.

Inline caches hold family-specific counters and lookup information. Type versions, dictionary-key versions, function versions, and watchers participate where applicable; not every specialization uses every mechanism, and not every mutation invalidates every cache. Failed assumptions must never change the observable result. Tracing/instrumentation affects execution forms; `dis` can expose original/adaptive instructions and caches with its documented options. [Specialization source](https://github.com/python/cpython/blob/v3.14.7/Python/specialize.c), [bytecode definitions](https://github.com/python/cpython/blob/v3.14.7/Python/bytecodes.c), [`dis`](https://github.com/python/cpython/blob/v3.14.7/Doc/library/dis.rst).

### Experimental trace compilation

**CPython experimental/optional — 3.14.7:** JIT availability and enablement are separate. Source builds using `configure` default to `--enable-experimental-jit=no`; official macOS/Windows release binaries include the experimental JIT for opt-in testing with `PYTHON_JIT=1`. Redistributors/build options differ. Free-threaded 3.14 builds do not support JIT compilation. [Build configuration](https://github.com/python/cpython/blob/v3.14.7/Doc/using/configure.rst), [binary-release conditions](https://github.com/python/cpython/blob/v3.14.7/Doc/whatsnew/3.14.rst#binary-releases-for-the-experimental-just-in-time-compiler).

When available and enabled, the optimization path is:

1. A hot backward edge triggers trace construction.
2. Instructions are translated to micro-operations and analyzed/optimized.
3. Construct the executor and compile its native implementation by combining build-generated machine-code stencils and patching runtime values/targets.
4. Install the compiled executor through `ENTER_EXECUTOR`.
5. Guards, exits, and invalidation return control to appropriate interpreter/executor paths when assumptions no longer hold.

Generated instructions require [executable-memory permissions](../../Operating%20Systems/Compilers%2C%20Linkers%2C%20and%20Program%20Loading.md#Runtime%20Compilation). The micro-op interpreter used for JIT development is a distinct configuration, not proof that native compilation is enabled. [JIT design](https://github.com/python/cpython/blob/v3.14.7/InternalDocs/jit.md), [optimizer](https://github.com/python/cpython/blob/v3.14.7/Python/optimizer.c).

The experimental observation APIs distinguish three states:

- **Availability:** `sys._jit.is_available()` checks build capability.
- **Enablement:** `sys._jit.is_enabled()` checks process enablement.
- **Activity:** `sys._jit.is_active()` observes current JIT execution.

Repeated active-state queries can perturb the control flow being measured. None is a Python language guarantee, and no universal speedup follows from enabling the JIT. [JIT diagnostics](https://github.com/python/cpython/blob/v3.14.7/Doc/library/sys.rst).

### Source file to running frame

**CPython 3.14.7 walkthrough; JIT step conditional:**

1. Initialization selects a script/module entry point.
2. For ordinary source import, discovery creates the module and inserts it into `sys.modules` before invoking the loader's execution path. Script execution instead uses the established `__main__` environment. Globals and builtins define the execution namespace.
3. The source loader's execution path obtains code by validating a `.pyc` or compiling source. Decoding, tokenization, PEG parsing, AST/symbol analysis, instruction generation, CFG optimization, and assembly produce the code object; a valid cache bypasses these source stages. Custom loaders need not obtain code this way.
4. `PyEval_EvalCode` establishes the invocation and pushes an interpreter frame; its code is program metadata, while bindings, instruction position, and evaluation stack are live state.
5. Dispatch advances that state. Calls bind arguments and push callee frames; ordinary Python-to-Python paths continue in the evaluator.
6. Hot sites specialize with guarded caches. Failed guards preserve semantics through fallback/reconsideration.
7. Only an available, enabled experimental-JIT configuration can turn a suitable hot edge into a micro-op executor and native code.
8. Return pops/transfers the result; an exception selects handlers or propagates; generator/coroutine suspension retains its embedded frame. Inspection can materialize a frame object without changing these language transitions.

## Object and type machinery

**Language guarantee:** Every object has identity, type, and value. Mutability is a property of the type's semantics, not an instruction to use a particular allocation layout. [Data model](https://github.com/python/cpython/blob/v3.14.7/Doc/reference/datamodel.rst).

**CPython 3.14.7:** The conceptual `PyObject` header contains type and reference-count state. `PyVarObject` adds size for types using that representation; not every variable-length type interprets size identically. Debug/trace-reference/free-threaded builds alter layout; the free-threaded header includes ownership/counting, locking, and GC state. Fixed offsets are not portable.

`PyTypeObject` is itself an object and supplies instance layout/behavior: allocation/deallocation, traversal, attributes, numeric/sequence/mapping slots, calling, hashing, rich comparison, and descriptor operations. Static types and dynamically allocated heap types differ in construction/lifetime; type readiness connects slots and inheritance. Direct structure access couples an extension to the applicable ABI. [Object structures](https://github.com/python/cpython/blob/v3.14.7/Include/object.h), [type structures](https://github.com/python/cpython/blob/v3.14.7/Doc/c-api/typeobj.rst).

### Class construction and attribute lookup

**Language guarantee — default class machinery:** Metaclass selection and namespace preparation precede class-body execution. The metaclass constructs the class; default `type.__new__` establishes its MRO, invokes descriptor `__set_name__`, and calls the parent `__init_subclass__` hook. Custom metaclasses/hooks change the construction path. C3 MRO preserves local base order and monotonic ordering; inconsistent hierarchies are rejected. [Class construction](https://github.com/python/cpython/blob/v3.14.7/Doc/reference/datamodel.rst).

Default instance `__getattribute__` composes storage and descriptors in this precedence order:

1. A **data descriptor** found in the type/MRO (`__set__` or `__delete__` in addition to descriptor access).
2. Instance storage, when the attribute is present there.
3. A **non-data descriptor** or ordinary attribute found in the type/MRO.
4. Lookup failure raises `AttributeError`; the attribute-access machinery then invokes `__getattr__` if defined.

An overridden `__getattribute__` changes this path. For class attributes, default lookup instead checks metaclass data descriptors, then the class MRO, then metaclass non-data/plain attributes; class-MRO descriptors receive `__get__(None, cls)`.

Python functions are non-data descriptors: retrieving one through an instance binds the receiver into a method. **CPython 3.14.7:** Optimized call paths can pass function and receiver separately without allocating a transient bound-method object. `__slots__`, managed dictionaries, inline instance values, and shared-key dictionaries provide different storage arrangements; type/dictionary mutation affects lookup-cache assumptions. [Instance lookup](https://github.com/python/cpython/blob/v3.14.7/Objects/object.c), [class lookup/construction](https://github.com/python/cpython/blob/v3.14.7/Objects/typeobject.c).

## Concrete built-in representations

**Language guarantees versus CPython 3.14.7:** The semantic column describes the values exposed by Python; the representation column is implementation-specific. Headers, payloads, and referents have different allocation/locality costs.

| Type | Semantic contract | CPython representation and consequence |
| --- | --- | --- |
| `int` | Immutable arbitrary-precision integer | Sign/digit count in long metadata; configured 30-bit or 15-bit digits (bases `2**30`/`2**15`). Magnitude changes payload size/work. Cached small values do not establish arbitrary integer identity. |
| `float` | Immutable floating-point value | Boxed C `double`; platform C floating-point behavior matters. Equality does not imply identity. |
| `bool` | `int` subtype with `True`/`False` singletons | Singleton objects; not a model for identity of arbitrary numeric values. |
| `str` | Immutable sequence of Unicode code points | Flexible compact/ASCII representation; 1-, 2-, or 4-byte kind based on maximum code point, stored length/hash and applicable UTF-8 cache. Code points are not grapheme clusters. |
| `bytes` | Immutable byte sequence | Inline variable-length payload, cached hash, and trailing C null outside the logical value. |
| `tuple` | Immutable sequence of references; referents can be mutable | Fixed-size inline pointer array. Exact tuples can be untracked when their initialized elements satisfy the conservative GC test. |
| `list` | Mutable sequence | Separate contiguous pointer array, logical length and allocated capacity. Growth overallocates; exact policy is version-sensitive. Lists remain GC-tracked. |
| `dict` | Mutable mapping preserving insertion order | Compact indices plus dense entries; combined/split layouts and shared Unicode keys for instance namespaces. Dictionaries remain GC-tracked in this baseline. |
| `set` / `frozenset` | Unique hashable elements; mutable/immutable respectively; no guaranteed iteration order | Open-addressed table with cached hashes, empty/dummy slots, perturbation probing, and embedded small table; GC-tracked containers. |

[Numeric headers](https://github.com/python/cpython/blob/v3.14.7/Include/cpython/longintrepr.h), [float layout](https://github.com/python/cpython/blob/v3.14.7/Include/cpython/floatobject.h), [Unicode layout](https://github.com/python/cpython/blob/v3.14.7/Include/cpython/unicodeobject.h), [bytes](https://github.com/python/cpython/blob/v3.14.7/Include/cpython/bytesobject.h), [tuple](https://github.com/python/cpython/blob/v3.14.7/Objects/tupleobject.c), [list](https://github.com/python/cpython/blob/v3.14.7/Objects/listobject.c), [set](https://github.com/python/cpython/blob/v3.14.7/Objects/setobject.c).

**CPython 3.14.7:** A dictionary separates hash-probe positions from insertion-order entries. Its representation supplies several distinct mechanisms:

- **Storage layouts:** Combined tables store key/value entries together; split tables share keys while keeping per-instance values separately.
- **Probing and deletion:** Open addressing preserves the probe chain through deleted slots. Empty, active, dummy, and split-table pending states serve distinct lookup/insertion roles.
    - Free-threaded dictionaries do not reuse dummy slots, unlike ordinary-build paths.
- **Usable capacity:** The capacity function takes floor two-thirds of table size, not a universal live-entry resize threshold after deletions.
- **Cache coordination:** Key versions/watchers support applicable lookup assumptions. [Dictionary layout and probing](https://github.com/python/cpython/blob/v3.14.7/Objects/dictobject.c).

Other execution objects retain graphs rather than just scalar payloads:

- **Functions:** Retain code, globals/builtins, defaults, keyword defaults, annotation/type-parameter machinery, names, closure cells, and vectorcall entry.
- **Cells:** Indirect shared bindings so nested functions/frames observe rebinding of the same captured variable.
- **Generators, native coroutines, and asynchronous generators:** Retain an embedded interpreter frame and execution state. Creating their execution object does not run the body; resumption drives it.
- **Exceptions and tracebacks:** Retain cause/context/traceback links; traceback nodes retain frames and thereby locals/referents.

These reference-carrying objects participate in cyclic-GC machinery; scalar numeric/string/byte payload objects do not require traversal of a Python-reference graph. [Function layout](https://github.com/python/cpython/blob/v3.14.7/Include/cpython/funcobject.h), [generator layout](https://github.com/python/cpython/blob/v3.14.7/Include/cpython/genobject.h), [exception layout](https://github.com/python/cpython/blob/v3.14.7/Include/cpython/pyerrors.h).

A contiguous list/tuple pointer array does not make its referents' payloads contiguous. Boxing, metadata, indirection, and dynamic dispatch affect work and [spatial locality](../../Operating%20Systems/03%20Memory%20Management.md#Spatial%20Locality), but no pointer access guarantees a cache miss or a trip to RAM. Native homogeneous buffers reduce per-element boxing/indirection; kernel implementation, access pattern, and hardware determine any further cache/SIMD benefit.

## Identity, equality, hashing, and interning

**Language guarantee:** `is` compares identity; `==` invokes value-comparison semantics. Default object equality/hash are identity-based; defining `__eq__` without an appropriate hash normally makes the class unhashable through `__hash__ = None`.

- Equal hashable values must have equal hashes; different values can collide.
- Numeric cross-type equalities, such as equal integer/float values, obey that invariant.
- A key's equality/hash must remain suitable while resident in a mapping/set; mutating the relevant state invalidates lookup assumptions.
- Dictionary insertion order does not imply a stable hash-probe order or guaranteed set iteration order.

`id()` is unique among simultaneously existing objects; reuse after an object's lifetime is permitted. **CPython 3.14.7:** It exposes an address-valued identity, not a portable location contract. String/bytes hash randomization affects values between processes; cached hashes are representation details. [Identity/hash semantics](https://github.com/python/cpython/blob/v3.14.7/Doc/reference/datamodel.rst), [`id` contract](https://github.com/python/cpython/blob/v3.14.7/Doc/library/functions.rst).

### Interning and immortality

**CPython 3.14.7:** Interning reuses selected equal strings for implementation efficiency. It is not a reason to compare strings or integers using `is`. In the ordinary build, `sys.intern()` does not itself promise immortality; interned strings include mortal and immortal cases. Free-threaded interned strings are immortal in this implementation. [String interning](https://github.com/python/cpython/blob/v3.14.7/InternalDocs/string_interning.md).

Immortal objects, including `None`, `True`, and `False`, skip ordinary `Py_INCREF`/`Py_DECREF` updates. Eliminating shared reference-count writes motivates reduced [cache coherence](../../Operating%20Systems/04%20Inside%20The%20CPU.md#Cache%20coherency) traffic and improved pre-fork sharing, not guaranteed cache states, timings, or RSS savings. Immortality is CPython bookkeeping, not a new Python language category. [Current refcount operations](https://github.com/python/cpython/blob/v3.14.7/Include/refcount.h), [PEP 683 rationale](https://peps.python.org/pep-0683/).

## Object lifetime and reclamation

### Ownership and reference counting

**Language guarantee:** `del` removes a binding, item, or attribute according to target semantics. It does not command object destruction; other references and implementation lifetime rules remain relevant.

**Public C API / CPython 3.14.7:** Ownership conventions describe responsibilities at API boundaries:

- **New/strong reference:** The owner must eventually release or transfer it.
- **Borrowed reference:** No ownership is acquired; the underlying owner must keep the object alive. Container mutation or arbitrary Python execution can invalidate it.
- **Stolen reference:** A documented API takes ownership; its error-path rules still determine the caller's obligations.

`Py_INCREF` acquires a strong reference; `Py_NewRef` returns one explicitly; `Py_DECREF` releases one; `Py_XDECREF` also accepts `NULL`. In the ordinary build, terminal release of an acyclic mortal object invokes its type-specific deallocator, not necessarily libc `free()`. Decref can run arbitrary finalization/reentrant code, so restore container invariants before releasing a reference. Immortal and free-threaded counting paths differ. `sys.getrefcount()` introduces a temporary reference and is not a uniqueness/lifetime oracle. [Ownership](https://github.com/python/cpython/blob/v3.14.7/Doc/c-api/intro.rst), [reference-count contracts](https://github.com/python/cpython/blob/v3.14.7/Doc/c-api/refcounting.rst).

### Cyclic collection

**CPython 3.14.7:** Reference counts alone do not identify an unreachable cycle whose members retain each other. The cyclic collector operates on tracked reference-carrying containers:

1. `tp_traverse` exposes graph edges without arbitrary application traversal.
2. Subtract references originating inside the candidate graph from temporary count information.
3. Objects with external references, and objects reachable from them, remain live.
4. The isolated remainder proceeds through finalization/resurrection checks and cycle breaking using `tp_clear` where appropriate.

Tracking begins only after an object's traversable fields are safe. Exact tuples can become untracked when their elements pass the conservative tracking test; lists and **3.14.7 dictionaries remain tracked**. Earlier atomic-only dictionary untracking is absent in this baseline. [Collector](https://github.com/python/cpython/blob/v3.14.7/Python/gc.c), [extension GC support](https://github.com/python/cpython/blob/v3.14.7/Doc/c-api/gcsupport.rst).

**CPython 3.14.7 — ordinary GIL build:** Tracked objects use list-based generation cohorts 0, 1, and 2. Survivors are promoted; allocation/deallocation counts and thresholds schedule collections, with additional oldest-generation policy. Full collections clear applicable type free lists. Generation 1 and `threshold2` behavior were restored in 3.14.5: early-3.14 descriptions of their removal are stale for this baseline. [Pinned GC API/change record](https://github.com/python/cpython/blob/v3.14.7/Doc/library/gc.rst), [generation implementation](https://github.com/python/cpython/blob/v3.14.7/Python/gc.c).

**CPython optional — free-threaded 3.14.7:** Collection scans allocator heaps using header state and stop-the-world coordination, rather than ordinary age-partitioned generation lists. Generation arguments/counters do not establish equivalent object cohorts. Automatic scheduling additionally considers heap scale/process-memory growth and buffered per-thread allocation accounting; manual collection is distinct. Threads resume for callbacks/finalizers, then pause again to check resurrection. [Free-threaded collector](https://github.com/python/cpython/blob/v3.14.7/Python/gc_free_threading.c).

### Finalization, weak references, and resources

**Standard-library contract:** A weak reference observes an object without keeping it alive. Calling it returns the referent while the weak reference remains valid, or `None` after it is cleared; a collection callback requires the weakref itself to remain alive. [Weak references](https://github.com/python/cpython/blob/v3.14.7/Doc/library/weakref.rst).

**CPython 3.14.7:** In cyclic-isolate collection, weakrefs are cleared and eligible callbacks run, finalizers execute, resurrection is checked, and surviving unreachable cycles are broken. Reference-count deallocation instead follows the type's own ordering; there is no universal weakref-before-finalizer sequence for every destruction path. `tp_finalize`/`__del__` can resurrect an object, changing whether reclamation proceeds. [GC finalization](https://github.com/python/cpython/blob/v3.14.7/Python/gc.c), [type deallocation](https://github.com/python/cpython/blob/v3.14.7/Objects/typeobject.c), [PEP 442 rationale](https://peps.python.org/pep-0442/).

Ordinary Python cycles containing `__del__` are generally collectable. Legacy extension `tp_del` types can remain uncollectable; `DEBUG_SAVEALL` deliberately retains unreachable objects in `gc.garbage` and is not evidence that all of them were inherently uncollectable.

Retention can arise through tracebacks, closures, tasks, callbacks, module globals, or application caches. Finalizer exceptions without a propagation path are unraisable; shutdown adds partially cleared globals and arbitrary destruction order.

**Language/library resource discipline:** Context managers and explicit `close()` establish resource ownership; collection timing does not define [descriptor lifetime](../../Operating%20Systems/02%20The%20Anatomy%20of%20a%20Process.md#Descriptor%20Operations%20and%20Lifetime). Do not rely on `__del__` for timely release, especially across implementations, cycles, free threading, and shutdown.

## Allocation and resident memory

**Public C API / CPython 3.14.7:** Object death and physical memory release are separate transitions. Python allocations are layered over [virtual memory](../../Operating%20Systems/03%20Memory%20Management.md#Virtual%20Memory), with three allocator domains:

- **Raw (`PyMem_Raw*`):** Low-level storage with APIs usable without attached thread state.
- **Mem (`PyMem_*`):** Python-managed non-object storage; attachment requirements apply.
- **Object (`PyObject_*`):** Python object storage; in free-threaded builds this domain is exclusively for Python objects, and those objects must use it.

Match allocation/free families. Build options, `PYTHONMALLOC`, debug hooks, and custom allocators alter routes; domain contracts remain mandatory. [Memory API](https://github.com/python/cpython/blob/v3.14.7/Doc/c-api/memory.rst).

**CPython 3.14.7 — normal GIL-build allocator configuration:** `pymalloc` handles positive Mem/Object requests up to 512 bytes using size-class blocks within pools within arenas. Its normal arena sizes are 1 MiB on 64-bit builds and 256 KiB on 32-bit builds; these are not OS page sizes. Arena acquisition uses platform/build-specific `mmap`, `VirtualAlloc`, or `malloc` paths. Larger requests fall through to lower allocation machinery. Type-specific free lists, including applicable tuple/list/float paths, add reuse above allocator blocks; the exact set/policy is version-sensitive. [Allocator constants](https://github.com/python/cpython/blob/v3.14.7/Include/internal/pycore_obmalloc.h), [allocator implementation](https://github.com/python/cpython/blob/v3.14.7/Objects/obmalloc.c), [free-list state](https://github.com/python/cpython/blob/v3.14.7/Include/internal/pycore_freelist_state.h).

**CPython optional — free-threaded 3.14.7:** Python objects use `mimalloc`, with separate allocation heaps and stricter domain rules. Quiescent-state-based reclamation (**QSBR**) delays reuse of selected backing structures until readers can no longer access them; it does not delay every object identically. `MIMALLOC_PURGE_DELAY` trades release latency against performance. [Free-threading memory behavior](https://github.com/python/cpython/blob/v3.14.7/Doc/howto/free-threading-python.rst).

**CPython 3.14.7 / OS-specific measurement:** Returning storage to a free list or allocator makes it reusable without necessarily unmapping pages. A `pymalloc` arena must be wholly reclaimable for release; live blocks, fragmentation, allocator policy, native heaps, and dirty/shared pages affect retention.

- **Traced Python allocations:** `tracemalloc` records participating allocator allocations, not all process memory.
- **Shallow object size:** `sys.getsizeof` does not recursively include the referent graph.
- **Tracked object counts:** GC statistics count tracked objects/collections, not heap bytes.
- **RSS:** Resident pages include runtime code/data, native allocations, stacks, mappings, and allocator slack, with shared/private accounting depending on the OS/tool.

Falling traced allocations do not imply falling RSS. Conversely, page eviction or mapping changes can alter RSS without a corresponding change in live Python objects. [Tracing boundaries](https://github.com/python/cpython/blob/v3.14.7/Doc/library/tracemalloc.rst).

### Fresh object allocation to reclamation

**CPython 3.14.7 walkthrough; allocator/build branches explicit:** Cached singleton/value returns and free-list hits bypass parts of this fresh-allocation path.

1. A type computes required fixed/variable storage and requests the appropriate Object-domain allocation.
2. Normal GIL-build small allocations use a `pymalloc` size class; larger requests use lower allocation machinery. Free-threaded objects use `mimalloc` and different header bookkeeping.
3. Initialize the header/type/count state, payload, and traversable references; enable GC tracking only when traversal is safe.
4. Ownership transfers and mutations add/remove graph edges; applicable type/dict caches are invalidated when their assumptions change.
5. Ordinary terminal release of an acyclic mortal object enters type deallocation. A tracked isolated cycle requires GC; immortals skip ordinary counting release, while queued merges, deferred stack-reference accounting, and per-thread count reconciliation can postpone terminal deallocation.
6. In the cyclic-isolate path, weakref callbacks/finalization/resurrection checks precede breaking the remaining isolated graph. Refcount deallocation has type-specific ordering and must also respect resurrection.
7. Reclaimed storage enters a type free list or allocator reuse path; safe-reclamation mechanisms can delay reuse.
8. Only reclaimable allocator structures and lower-layer policy permit page/arena release. The object is gone even if RSS is unchanged.

## Threads, GILs, free threading, and subinterpreters

### Native threads and the ordinary GIL

**CPython 3.14.7:** `threading.Thread` creates [native threads](../../Operating%20Systems/05%20Process%20Management.md#Threads), not user-space Python threads. In a GIL-enabled interpreter, attached execution is serialized by its GIL; native threads still exist and detached native work can execute concurrently.

The GIL uses mutex/condition-variable coordination and eval-breaker drop requests. The default switch-request interval is 5 ms, configurable through `sys.setswitchinterval`; it is not a hard OS timeslice or a bound on when long-running native code yields. Interpreters can share a GIL or use separately configured GILs. [GIL implementation](https://github.com/python/cpython/blob/v3.14.7/Python/ceval_gil.c).

The GIL protects interpreter machinery while held, not arbitrary [shared invariants](../../Backend%20Engineering/Concurrency/01%20Concurrency%20Fundamentals.md#Critical%20Sections). Multi-step updates race; operations can invoke user code or detach thread state. Native code releases the GIL only when it deliberately detaches around work that does not require Python-object/API access; reattach before re-entry. Free-threaded code also detaches around blocking work so GC coordination can progress. [Thread-state API](https://github.com/python/cpython/blob/v3.14.7/Doc/c-api/threads.rst).

**Standard-library contract / CPython implementation:** `ThreadPoolExecutor` supplies native worker threads. It overlaps blocking or GIL-releasing native work, but submission alone does not make Python CPU work parallel within one GIL-enabled interpreter. [Thread executor implementation](https://github.com/python/cpython/blob/v3.14.7/Lib/concurrent/futures/thread.py).

### Free-threaded build

**CPython optional — 3.14.7:** `--disable-gil` builds a distinct free-threaded configuration with `t` ABI suffix. Runtime `-X gil`/`PYTHON_GIL` can enable the GIL; importing an extension without the appropriate support declaration can also enable it. Build capability and current runtime GIL state are different facts.

Removing the global serialization point requires cooperating lifetime/synchronization mechanisms:

- **Biased reference counting:** Owner-local counts avoid shared atomic updates on the owning thread. Cross-thread release can queue merge work; the owner services it through eval-breaker coordination, reconciling local/shared counts before terminal deallocation. That merge can delay destruction.
- **Deferred reference counting:** Selected Python-stack references are omitted from immediate counts. GC accounts for them before reclaiming an apparently zero-count object, so disappearance of an ordinary counted reference is not sufficient to decide its lifetime.
- **Per-thread reference counting:** Selected shared objects aggregate thread-local contributions rather than one globally contended counter. Those contributions must be merged before deallocation at coordinated safepoints, thread exit, or collection, delaying release in some cases.
- **Immortalization:** Selected objects omit ordinary counting updates.
- **Object/container locks:** Protect applicable internal mutations; some reads use optimistic paths with safe reclamation.
- **Stop-the-world GC and QSBR:** Coordinate graph/count reconciliation and safe reuse, respectively; they solve different problems.

Object critical sections support deadlock avoidance by suspending/reacquiring locks around blocking/nested work. They are not uninterrupted application transactions; protecting two objects together requires the relevant two-object facility. Internal builtin locking aims for behavior similar to the GIL build but is not a language-level atomicity guarantee for compound operations.

Extension hazards include direct field access, unchecked macros, borrowed references from concurrently mutable containers, unsynchronized C globals/caches, shared iterators, and inspecting another running thread's `frame.f_locals`. Prefer documented strong-reference getters and synchronization appropriate to the invariant. [Free-threaded extension rules](https://github.com/python/cpython/blob/v3.14.7/Doc/howto/free-threading-extensions.rst), [biased merging](https://github.com/python/cpython/blob/v3.14.7/Python/brc.c).

The pinned guide reports higher memory usage and average single-thread overhead on **pyperformance** ranging from about 1% on macOS aarch64 to 8% on x86-64 Linux in its measurements. This is benchmark/platform evidence, not a bound for every program or hardware configuration. [Measured trade-offs](https://github.com/python/cpython/blob/v3.14.7/Doc/howto/free-threading-python.rst).

### Interpreter isolation

**CPython 3.14.7 / C API:** Subinterpreters have independent interpreter/module/builtins/import state but share one process and its resources. Extension C statics and native-library state can cross that boundary. Interpreter isolation is not process fault isolation.

`Py_NewInterpreterFromConfig` selects shared or own-GIL operation subject to its isolation/extension settings. Own-GIL interpreters permit simultaneous Python execution on different cores; legacy `Py_NewInterpreter()` shares the main GIL. Extension support for multiple interpreters, own-GIL interpreters, and no-GIL operation are independent requirements, not one compatibility flag. [Subinterpreter API](https://github.com/python/cpython/blob/v3.14.7/Doc/c-api/subinterpreters.rst).

**Standard-library contract — 3.14:** `InterpreterPoolExecutor` runs worker threads with separate interpreters and GILs. Submitted callables, arguments, and results cross a pickle boundary; mutable Python objects are not transparently shared. A native crash still affects the shared process. [Interpreter executor](https://github.com/python/cpython/blob/v3.14.7/Doc/library/concurrent.futures.rst).

## Processes and serialization

### Start methods and fork safety

**Standard-library contract / OS-specific — Python 3.14:** Process startup selects how interpreter state is established:

| Start method | State established in child | Default/constraint |
| --- | --- | --- |
| `spawn` | Fresh interpreter imports the required entry/definitions; process state is transferred | Default on Windows/macOS, and fallback where forkserver prerequisites are unavailable |
| `forkserver` | A server forks children from its own state, not the submitting parent's current heap | Default on other supported POSIX platforms with descriptor-passing support |
| `fork` | Snapshot of the calling process via `os.fork()` | Explicit choice on supported POSIX; no platform uses it by default in 3.14 |

Spawn/forkserver require safely importable entry code and suitable top-level definitions; guard process creation with `if __name__ == '__main__'`. `ProcessPoolExecutor` follows its selected context, but `max_tasks_per_child` selects spawn when no explicit context is supplied and is incompatible with explicit fork. [Start-method source](https://github.com/python/cpython/blob/v3.14.7/Lib/multiprocessing/context.py), [process executor](https://github.com/python/cpython/blob/v3.14.7/Lib/concurrent/futures/process.py).

After a multithreaded fork only the calling thread survives, while locks/library state can remain held or inconsistent. Allocator, logging, TLS, and extension state can fail before useful child work starts. Detection of multiple threads has produced the documented fork warning since 3.12. [Multiprocessing contracts and hazards](https://github.com/python/cpython/blob/v3.14.7/Doc/library/multiprocessing.rst).

**CPython 3.14.7 / POSIX consequence:** [Copy-on-write](../../Operating%20Systems/02%20The%20Anatomy%20of%20a%20Process.md#Shared%20and%20Private%20Mapping%20Visibility) applies to inherited private pages, not arbitrary subsequently submitted objects. Reference-count writes, GC, allocator metadata, mutable caches, and application writes erode sharing. In deliberate pre-fork designs, `gc.freeze()` can reduce GC-induced writes to inherited objects; it prevents neither refcount writes nor all copying and is not universal deployment advice. Forkserver inheritance is from the server's ancestry. [Freeze behavior](https://github.com/python/cpython/blob/v3.14.7/Doc/library/gc.rst).

### Object transfer and shared bytes

**Standard-library contract / CPython 3.14.7:** Multiprocessing connects interpreter heaps using [IPC](../../Operating%20Systems/08%20Inter-Process%20Communication.md#Process%20Boundaries%20and%20Communication), not transparent shared-object access.

- **`Connection`:** `send`/`recv` pickle/unpickle objects; `send_bytes`/`recv_bytes` transfer framed bytes without automatic object pickling.
- **`Queue`:** `put` buffers an object locally; a feeder thread later serializes and writes it. Returning from `put` does not establish a completed snapshot. `SimpleQueue` serializes synchronously instead.
- **Pools/executors:** Submitted inputs and returned results/errors must satisfy their serialization/importability rules.

Pickle commonly resolves functions/classes by module/name rather than copying executable closure state. Unpickling reconstructs ordinary mutable values in the receiving heap, but globals, singleton values, and custom reducers prevent a universal “every node is newly allocated” rule. Never unpickle untrusted data; authentication alone does not make a payload safe. [Queue implementation](https://github.com/python/cpython/blob/v3.14.7/Lib/multiprocessing/queues.py), [connection implementation](https://github.com/python/cpython/blob/v3.14.7/Lib/multiprocessing/connection.py), [pickle contracts](https://github.com/python/cpython/blob/v3.14.7/Doc/library/pickle.rst).

Queue ordering is per documented producer/channel rules, not one universal order across producers. Backpressure can stall writers/feeders; joining a producer before draining its queue can deadlock, and terminating it during writes can corrupt the channel. Resource tracking on POSIX spawn/forkserver helps reclaim named resources, not recover arbitrary application state.

**Standard-library contract / OS-specific:** `SharedMemory` exposes shared bytes; `Value`/`Array` expose constrained shared representations with synchronization requirements. Process-local pointers, headers, refcounts, allocators, and interpreter ownership do not become a shared Python container graph. Close each attachment; unlink once when appropriate on POSIX. On Windows, unlink is ignored and deletion follows closing all handles. Independently launched tracked processes can have separate trackers and premature cleanup hazards. [Shared-memory lifecycle](https://github.com/python/cpython/blob/v3.14.7/Doc/library/multiprocessing.shared_memory.rst).

### Queue message to receiving object

**CPython 3.14.7 walkthrough:**

1. The parent calls `Queue.put`; the queue retains the submitted object in a local buffer. The producer must not assume that a mutable payload has already been serialized.
2. The feeder removes it, pickles the serializable graph, and frames the bytes. A direct `Connection.send` instead serializes in its send path.
3. The write crosses user/kernel buffers or platform equivalents and can wait for channel capacity. This is byte transfer, not shared access to the producer's object.
4. The receiving process reads a frame and unpickles it, resolving importable definitions and reconstructing process-local state under its own allocator/lifetime rules.
5. Result/error transfer repeats the boundary. Unpicklable values, missing definitions, closed channels, and broken workers cause failures.

> [!note] Shared-memory alternative
> A shared-memory transfer exchanges a name/handle and layout information instead of reconstructing the payload through this Queue path. Data synchronization, view lifetime, close/unlink, and interpretation remain explicit.

## Coroutines and asyncio

### Coroutine, Task, and Future

**Language guarantee:** Calling a coroutine function (`async def` without `yield` in its body) creates a coroutine without running the body. Calling an asynchronous-generator function instead creates an asynchronous generator. `await` uses the awaitable protocol; it suspends only if the awaited computation yields control. Merely declaring a function async does not make its blocking operations nonblocking.

**CPython 3.14.7:** Generators/coroutines retain instruction position, evaluation state, locals, and references in an embedded interpreter frame. `send`, `throw`, and closing/resumption protocols transition that state; suspension keeps referenced objects alive. [Generator/coroutine design](https://github.com/python/cpython/blob/v3.14.7/InternalDocs/generators.md).

**Standard-library contract:** A Task drives a coroutine; a Future represents eventual result/error and owns completion callbacks. Awaiting an incomplete Future suspends the Task and installs wakeup machinery. Awaiting an already completed Future need not yield.

Callback scheduling distinguishes two categories:

- **Ready callbacks:** `call_soon` schedules loop work; thread-safe scheduling also wakes the loop.
- **Scheduled callbacks:** Timers become eligible according to the loop clock.

Tasks use that scheduling machinery, with separate creation and lifetime constraints:

- **Configuration:** Factories and eager-start options can change when initial coroutine execution begins; contexts are captured/selected according to the API.
- **Ownership:** The loop keeps weak Task references; keep a strong application reference for background work that must remain live.

Future completion schedules callbacks rather than executing them inline. No JavaScript-style universal microtask queue is implied. [Task contracts](https://github.com/python/cpython/blob/v3.14.7/Doc/library/asyncio-task.rst), [Future contracts](https://github.com/python/cpython/blob/v3.14.7/Doc/library/asyncio-future.rst).

### Event-loop iteration and I/O backends

**CPython 3.14.7 — standard asyncio loop implementation:** `_run_once` performs an ordered scheduling cycle:

1. Remove cancelled timer entries as required.
2. Compute the poll timeout: zero when ready work exists or the loop is stopping; otherwise derive it from the next timer, or wait without a timer deadline.
3. Poll the backend and process its events.
4. Append eligible timers to the ready queue, including the implementation's clock-resolution window.
5. Capture the ready-queue length and execute that bounded snapshot; callbacks scheduled during its execution wait for a later iteration.

This is implementation ordering, not a requirement for every custom event loop. [Loop implementation](https://github.com/python/cpython/blob/v3.14.7/Lib/asyncio/base_events.py).

**OS-specific / standard asyncio defaults:** Unix `SelectorEventLoop` uses `selectors` and the best available [readiness](../../Operating%20Systems/07%20Socket%20Management.md#Readiness-Based%20I%2FO) backend. Windows `ProactorEventLoop` uses IOCP [completion](../../Operating%20Systems/07%20Socket%20Management.md#Completion-Based%20I%2FO). Their supported socket/pipe/handle operations differ. Neither choice specifies listener count, worker processes, or a server topology. [Platform behavior](https://github.com/python/cpython/blob/v3.14.7/Doc/library/asyncio-platforms.rst).

### Socket read to Task resumption

**CPython 3.14.7 / OS-specific walkthrough — pending receive path:**

1. A Task advances its coroutine into an awaited socket receive. Selector `sock_recv` first tries a nonblocking receive; immediate success returns without suspension.
2. If it would block, the selector path creates a Future and registers the fd's reader callback **before awaiting** it. The proactor path submits an overlapped receive before awaiting its completion Future.
3. The incomplete Future yields; the Task retains suspended coroutine state, installs a wakeup callback, and returns control to the loop.
4. The loop polls with the scheduling timeout. Readiness lets a callback attempt receive and handle partial data/errors; IOCP reports the submitted operation's completion. Neither establishes a complete application message.
5. Completion stores the Future's result/error and schedules its callbacks. A selector receive callback that completes it during snapshot execution schedules wakeup for a later iteration; IOCP polling can complete it before snapshot capture.
6. At wakeup, success steps the coroutine with `None`; the Future's await iterator returns the stored result. Failure is thrown into the suspended coroutine. The embedded frame continues after `await`.
7. Cancellation instead requests exception injection and cleanup at a resumption opportunity; surrounding structured concurrency determines the eventual outcome.

[Selector receive](https://github.com/python/cpython/blob/v3.14.7/Lib/asyncio/selector_events.py), [Windows completion](https://github.com/python/cpython/blob/v3.14.7/Lib/asyncio/windows_events.py), [Task wakeup](https://github.com/python/cpython/blob/v3.14.7/Lib/asyncio/tasks.py), [Future await](https://github.com/python/cpython/blob/v3.14.7/Lib/asyncio/futures.py).

### Cancellation, flow control, and blocking boundaries

**Standard-library contract:** `Task.cancel()` requests `CancelledError` injection; it is not an immediate stop or proof of completed cancellation. The exception derives from `BaseException`. Use `try/finally` for cleanup; code can delay/suppress cancellation, but suppression can break structured-concurrency assumptions. `TaskGroup` cancels siblings after ordinary failures, waits for them, and groups non-cancellation failures; `KeyboardInterrupt`/`SystemExit` are reraised specially after cleanup. [Cancellation and groups](https://github.com/python/cpython/blob/v3.14.7/Doc/library/asyncio-task.rst).

Streams layer `StreamReader`/`StreamWriter` over public transports/protocols. Write-buffer high/low watermarks drive `pause_writing`/`resume_writing`; `drain()` waits for flow-control resumption/error when paused. It is not an empty-buffer, peer-delivery, or guaranteed-yield operation. Reader buffering separately pauses/resumes transport reads, connecting application consumption to backpressure. [Streams implementation](https://github.com/python/cpython/blob/v3.14.7/Lib/asyncio/streams.py), [transport contracts](https://github.com/python/cpython/blob/v3.14.7/Doc/library/asyncio-protocol.rst).

Blocking work stalls the loop thread unless its implementation integrates nonblocking I/O or offloads execution:

- Ordinary file I/O has no general asyncio async-file API; [regular-file readiness](../../Operating%20Systems/06%20Storage%20Management.md#Readiness%20and%20Completion%20for%20Regular%20Files) does not reveal storage latency.
- Loop `getaddrinfo`/`getnameinfo` use the default thread executor and can queue behind other work.
- Synchronous logging, database drivers, compression, subprocess waiting, native callbacks, and CPU computation retain their blocking behavior unless their specific interface changes it.

`asyncio.to_thread`/`run_in_executor` move the work; they do not turn the underlying function into a nonblocking operation. Thread offload is not default-build Python CPU parallelism. **Standard-library version status:** Event-loop policy APIs are deprecated in 3.14 and scheduled for removal in 3.16; configure `asyncio.run`/`Runner` with a loop factory instead. [Blocking/debug guidance](https://github.com/python/cpython/blob/v3.14.7/Doc/library/asyncio-dev.rst), [policy status](https://github.com/python/cpython/blob/v3.14.7/Doc/library/asyncio-policy.rst).

## Socket wrappers and deferred signals

**Standard-library contract / CPython 3.14.7:** A `socket` object wraps an OS descriptor/handle. Blocking, nonblocking, and timeout modes affect Python operations; timeout-mode sockets use nonblocking underlying state while the wrapper can wait. `BlockingIOError` denotes an operation that cannot proceed as requested. Reads/writes can be partial; protocols must frame messages and retry/continue as appropriate. `recv` produces bytes, while buffer-taking APIs provide different allocation/copy boundaries.

TLS adds protocol/buffering state through SSL transports; raw loop socket functions are not interchangeable with SSL-socket handling. Offloading a blocking socket operation changes which thread waits, not the socket into an asyncio transport. [Socket semantics](https://github.com/python/cpython/blob/v3.14.7/Doc/library/socket.rst), [TLS integration](https://github.com/python/cpython/blob/v3.14.7/Lib/asyncio/sslproto.py).

**CPython 3.14.7 / OS-specific:** The low-level OS handler for supported [signals](../../Operating%20Systems/05%20Process%20Management.md#POSIX%20Signals) marks pending state rather than executing arbitrary Python immediately. Python handlers run later in the main Python thread of the main interpreter; only that thread installs handlers. Long C execution delays delivery unless it checks signals or returns to evaluation. Signals are not Python inter-thread communication.

`signal.set_wakeup_fd` lets low-level handling write a notification byte to a nonblocking fd/supported socket handle so a loop wakes. Pending signal state is not a queued occurrence count: signals can coalesce, and notification buffers can overflow. Consumers can interpret bytes or use the fd just for wakeup, with warning policy chosen accordingly. Installation is main-thread-only; Windows support and signal repertoire differ from POSIX. [Signal contracts](https://github.com/python/cpython/blob/v3.14.7/Doc/library/signal.rst), [pending-state implementation](https://github.com/python/cpython/blob/v3.14.7/Modules/signalmodule.c).

## Exceptions and control transfer

**Language guarantee:** Raising creates/uses a `BaseException` instance and attaches traceback state. Implicit `__context__`, explicit `__cause__`, and context suppression through `raise ... from None` are separate relationships. Exception groups represent multiple failures; `except*` splits matching subgroups rather than treating the group as one ordinary exception. After handlers run, unhandled portions and exceptions raised/reraised by handlers determine the combined outgoing exception/group. [Raise semantics](https://github.com/python/cpython/blob/v3.14.7/Doc/reference/simple_stmts.rst), [exception groups](https://github.com/python/cpython/blob/v3.14.7/Doc/library/exceptions.rst), [`except*` control transfer](https://github.com/python/cpython/blob/v3.14.7/Doc/reference/compound_stmts.rst).

**CPython 3.14.7 / C API:** A thread-state error indicator is distinct from a normal result object. Typical fallible APIs return `NULL`/`-1` with an exception set; callers propagate, translate, or clear it according to contract. Traceback nodes retain frame/offset information and thereby keep object graphs alive.

On opcode failure, the evaluator consults the code object's exception table, restores the required stack depth, and transfers to handler bytecode or propagates out of the frame. `finally`/context-manager cleanup follows compiled control flow; this is not obsolete pre-3.11 block-stack handling or one universal native unwinder action. [Exception implementation](https://github.com/python/cpython/blob/v3.14.7/InternalDocs/exception_handling.md), [evaluator](https://github.com/python/cpython/blob/v3.14.7/Python/ceval.c).

**Standard-library contract:** Errors without a normal propagation route, such as finalizer failures, use `sys.unraisablehook`. Scheduled asyncio callback errors instead normally use the loop's exception handler. Native faults/fatal crashes are a different category from catchable Python exceptions; `faulthandler` supplies diagnostic output, not exception recovery. [Unraisable hook](https://github.com/python/cpython/blob/v3.14.7/Doc/library/sys.rst), [asyncio callback errors](https://github.com/python/cpython/blob/v3.14.7/Lib/asyncio/events.py).

## Imports, bytecode caches, and extension loading

### Module initialization and import coordination

**Language/standard-library import protocol:** Initial loading separates discovery, module identity, and execution:

1. Check `sys.modules`; an existing initialized module normally satisfies the import.
2. Finders on `sys.meta_path` locate a `ModuleSpec` and loader; path-based discovery uses path hooks/importer caches.
3. Create the module and insert it into `sys.modules` before executing its body, enabling recursive imports to find its identity.
4. Execute the module; on initial-load failure remove its failing entry, not successfully imported side-effect modules.
5. Bind loaded submodules into their parent package: `sys.modules['pkg.sub']` and `pkg.sub` refer to the same loaded module.

Parent initialization precedes ordinary submodule loading; namespace packages can combine search locations without an ordinary package body. The filesystem cache and module cache solve different problems. [Import reference](https://github.com/python/cpython/blob/v3.14.7/Doc/reference/import.rst).

**CPython 3.14.7:** Per-module locks and a global coordination lock manage concurrent initialization. Module bodies are not globally serialized throughout execution. Circular imports can encounter partially initialized modules and missing attributes. Reload executes in an existing module namespace and does not generally replace all references to previously imported objects. [Import coordination](https://github.com/python/cpython/blob/v3.14.7/Lib/importlib/_bootstrap.py).

### Compiled caches

**CPython 3.14.7:** A `.pyc` contains format/version magic, flags/invalidation metadata, and a marshalled code object. `__pycache__` names include implementation/cache and applicable optimization tags.

- **Timestamp mode:** Validates source modification time and size.
- **Checked hash mode:** Validates source content by default.
- **Unchecked hash mode:** Normally trusts external freshness management; `--check-hash-based-pycs` overrides hash-check policy.

Sourceless bytecode loading does not have equivalent source freshness validation. A cache stores neither module execution results, dependency objects, open resources, nor process `sys.modules` state; it is not native machine-code persistence. Loading cached code still executes module-level bytecode unless the current interpreter already supplies the module. [Cache loading/invalidation](https://github.com/python/cpython/blob/v3.14.7/Lib/importlib/_bootstrap_external.py).

### Native module initialization

**CPython 3.14.7 / C API / OS-specific:** Extension suffix discovery selects platform [dynamic loading](../../Operating%20Systems/Compilers%2C%20Linkers%2C%20and%20Program%20Loading.md#Dynamic%20Linking) and the applicable `PyInit_modname` entry point. Single-phase initialization returns a module; multi-phase initialization separates a module definition, creation, and execution, enabling per-module state and repeated interpreter initialization.

Process-global C statics are not isolated merely because Python module dictionaries are. Multi-phase slots declare multiple-interpreter compatibility and GIL dependence independently; free-threaded subinterpreters reject incompatible initialization arrangements. [Extension module lifecycle](https://github.com/python/cpython/blob/v3.14.7/Doc/c-api/extension-modules.rst), [module slots](https://github.com/python/cpython/blob/v3.14.7/Doc/c-api/module.rst).

## C API, ABI, and native-memory boundaries

### Compatibility contracts

**CPython public API contracts:** API exposure and binary compatibility are separate dimensions:

| Interface | Contract | Boundary |
| --- | --- | --- |
| Full public C API | Documented extension interfaces | Normal binary compatibility is tied to a minor release and compatible build/platform |
| Limited API | Restricted source-visible subset | Avoids selected layout/version dependencies; does not freeze behavior |
| Stable ABI | Cross-minor binary symbol contract | Includes compatibility symbols; `abi3` packaging still needs actual compliance and platform compatibility |
| Unstable API (`PyUnstable_*`) | Explicitly unstable public interfaces | Can change across minor releases without ordinary deprecation, not ordinary bugfix releases |
| Private API (`_Py*`) | Internal implementation | Can change even in patches; no extension compatibility promise |

**CPython optional — free-threaded 3.14:** Limited API/Stable ABI are not supported; extensions need separate `t`-tagged builds/wheels. `Py_mod_multiple_interpreters` and `Py_mod_gil` are separate multi-phase declarations; omitted slots default to shared-main-GIL interpreter support and GIL dependence, respectively. Single-phase modules use `PyUnstable_Module_SetGIL` for free-threading declarations, not as proof of general subinterpreter safety. Supporting no-GIL execution also requires protecting extension globals and following ownership/domain rules. [API/ABI stability](https://github.com/python/cpython/blob/v3.14.7/Doc/c-api/stable.rst), [free-threaded extension guide](https://github.com/python/cpython/blob/v3.14.7/Doc/howto/free-threading-extensions.rst).

**C API thread/ownership contract:** A foreign-created thread needs the correct attached interpreter/thread state before callbacks into Python. `PyGILState_Ensure` targets the main-interpreter model, not arbitrary subinterpreter selection; use explicit thread-state management for those attachments. Detached work must avoid Python-object/API access except documented exceptions. Callbacks and decref can mutate graphs, raise, or finalize objects, so borrowed-pointer assumptions must be reconsidered afterward. [Thread attachment](https://github.com/python/cpython/blob/v3.14.7/Doc/c-api/threads.rst).

### Python call into native code and back

**CPython 3.14.7 / C API walkthrough:**

1. `CALL` resolves the native callable and uses vectorcall or its applicable C convention; argument ownership follows that API.
2. With thread state attached, the extension validates arguments. Failure sets the error indicator and returns the documented sentinel.
3. If native work is blocking/long-running and does not require Python-object access, the extension deliberately saves/detaches state (`Py_BEGIN_ALLOW_THREADS`/`Py_END_ALLOW_THREADS` express this paired boundary). The ordinary build releases/reacquires the GIL; free-threaded attachment still matters for GC.
4. Detached work operates under native-memory ownership rules. It does not gain permission to manipulate Python objects.
5. Before producing Python objects or invoking a Python callback, reattach the correct state. A callback can invalidate cached/borrowed assumptions and requires normal error handling.
6. Return a strong result reference or an error sentinel with an exception set. The evaluator receives the value or transfers into exception handling.

> [!warning] CPython optional — free-threaded call safety
> Across the entire call lifecycle, declarations alone are insufficient: extension state needs synchronization, safe strong-reference access, and correct allocator domains. An undeclared/incompatible extension can re-enable the GIL.

### Buffers and memoryview

**Public buffer protocol:** A consumer negotiates access to exporter memory through `Py_buffer` and acquisition flags. The view describes logical start/length, item size/format, dimensions/shape, strides/suboffsets, read-only status, and requested contiguity. `len` is the logical contiguous-equivalent payload size, not necessarily a safe linear span from `buf`; honor strides and acquisition guarantees.

Zero-copy means no payload-byte copy **at that boundary**, not no allocations or transformations anywhere. `memoryview.cast()` reinterprets a view without copying payload under its restrictions; downstream conversion or requesting a contiguous representation can copy.

- **Exporter-backed lifetime:** A normal acquired buffer holds the exporter alive; release with `PyBuffer_Release`. A memoryview manages its view/export lifetime, and exporters can reject resizing while exports exist.
- **Foreign allocation lifetime:** Views created from raw memory/buffer interfaces can lack an exporter base. The allocation owner must keep that memory valid; a memoryview does not automatically own an arbitrary native allocation.
- **Concurrent access:** Read-only status is not synchronization. Mutating exporters, dangling pointers, use-after-release, and incorrect format/stride assumptions remain hazards.

[Buffer contract](https://github.com/python/cpython/blob/v3.14.7/Doc/c-api/buffer.rst), [memoryview API](https://github.com/python/cpython/blob/v3.14.7/Doc/c-api/memoryview.rst).

> [!warning] FFI boundary
> **Implementation/interface-specific:** Foreign-call interfaces differ in GIL release, callback attachment, signatures, and native ownership. A compiled call is not automatically parallel, zero-copy, or memory-safe; its documented lifetime/thread rules determine those properties.

## Backend execution consequences

**Application consequence:** WSGI/ASGI specify application/server interfaces, not [listener distribution](../../Backend%20Engineering/Concurrency/02%20Application%20Server%20Concurrency.md#Connection%20Distribution%20Models). The server and configuration choose sockets, acceptors, workers, and offloading. A pre-fork shared listener is not automatically a set of independent `SO_REUSEPORT` listeners.

**CPython 3.14.7 / optional-build comparison:** Runtime choice determines sharing, CPU execution, and blocking scope independently of that listener topology.

| Execution unit | Address space / Python objects | Python CPU parallelism | Transfer/startup and blocking scope | Fault/extension boundary |
| --- | --- | --- | --- | --- |
| Single event loop | One process/interpreter; objects shared among Tasks | One executing loop thread | Low local scheduling cost; blocking callback stalls that loop | Native faults affect process; suits integrated async I/O |
| Native thread pool | One process/interpreter; ordinary objects shared | No parallel Python execution under one enabled GIL | No IPC serialization; blocking occupies worker capacity | Shared invariants/extension state need synchronization; suits blocking offload |
| Processes | Separate ordinary heaps | Across processes | Startup/serialization or explicit shared bytes; blocked worker does not block sibling execution | Address-space isolation, not automatic job recovery; fork/import safety matters |
| Isolated interpreters | One process, distinct interpreter heaps/state | With own GILs | Interpreter startup and serialized submissions; one interpreter's blocking need not stop others | Shared native fault domain; extensions must support interpreter isolation |
| Free-threaded threads | One process, shared objects | When runtime GIL remains disabled | Thread startup/shared-memory access, synchronization and counting costs | Same process fault domain; no-GIL-safe extensions required |
| Native extension kernels | Process/native buffers; ownership API-specific | When detached work executes concurrently | Conversion/copy/offload depends on API; attached long work can block Python progress | Native crash corrupts process; not every kernel releases GIL |

Preloading trades startup/import duplication against inherited state and fork safety. CPython refcount/GC/allocator writes can erode sharing; `gc.freeze()` addresses only its specific GC contribution. No universal worker count follows from these mechanisms.

## Diagnostics and falsifiable investigation

**Standard-library tools / CPython- and OS-specific capabilities as marked:** Select a tool for a question, not as a substitute for [observability](../../Backend%20Engineering/05%20Observability.md#Foundations) or a measurement hypothesis.

| Question | Tool/mechanism | Measurement boundary and perturbation |
| --- | --- | --- |
| Emitted/specialized instructions? | `dis`, `adaptive`, `show_caches` | CPython/version-specific; instrumentation can change executed forms |
| Traced allocation growth? | `tracemalloc` snapshots/diffs/domains | Start before relevant allocations; hook/domain coverage is not all native memory/RSS; tracing adds overhead |
| Shallow size or tracked graph? | `sys.getsizeof`, `gc.get_stats/get_objects/get_referrers`, callbacks/debug flags | Shallow bytes vs tracked objects; inspection adds references and debug retention changes behavior |
| Reference count? | `sys.getrefcount` | Temporary call reference, immortal/free-threaded bookkeeping; no uniqueness/lifetime oracle |
| Function-level timing? | `cProfile`/`profile`, profile/trace hooks | Deterministic event/timing attribution, not automatically CPU-only/native sampling; not an unbiased benchmark timer |
| Selected execution events? | `sys.monitoring` | Configurable lower-impact instrumentation, not zero-overhead sampling |
| Statistical native/Python CPU evidence? | Sampling tools; Linux `perf` with supported `-X perf`/`-X perf_jit` trampolines | Build/unwinding/platform dependent; `perf_jit` profiling support is not the experimental optimizing JIT |
| Specialization/deoptimization counts? | `--enable-pystats`, `-X pystats`/`PYTHONSTATS=1`, `Tools/scripts/summarize_stats.py` | Special build; gathering starts off; internal counters/output are version-sensitive and instrument execution |
| Allocator misuse? | Debug builds, `PYTHONMALLOC=debug`, allocator statistics | Extra checking/overhead, not proof of safety; free-threaded allocator choices are restricted |
| Blocked/misused loop? | Asyncio debug / `PYTHONASYNCIODEBUG`, slow callbacks, never-awaited warnings | Checks/logging alter timing; not production-latency measurement |
| Thread state or hangs? | `sys._current_frames`, explicit `faulthandler` dumps, native debugger | Snapshot races/build visibility; another running thread's `f_locals` is unsafe with free threading |
| Crashes/native stacks? | `faulthandler`, conditional C-stack support; GDB `py-bt/py-list/py-locals` | Fault-path dumps with disabled GIL restrict to current thread; explicit dumps differ. C-stack unwinding is platform/build-dependent and can be slow |
| Import time? | `-X importtime`/`PYTHONPROFILEIMPORTTIME`; value `2` in 3.14 | Also reports already-loaded imports as cached; multithreaded output can be unreliable |
| Sensitive operations? | `sys.addaudithook`, early native `PySys_AddAuditHook` | Specified audit events only; hooks are not a sandbox; early native hooks see broader initialization events |

[Tracing allocations](https://github.com/python/cpython/blob/v3.14.7/Doc/library/tracemalloc.rst), [profiling](https://github.com/python/cpython/blob/v3.14.7/Doc/library/profile.rst), [monitoring](https://github.com/python/cpython/blob/v3.14.7/Doc/library/sys.monitoring.rst), [perf support](https://github.com/python/cpython/blob/v3.14.7/Doc/howto/perf_profiling.rst), [pystats/build options](https://github.com/python/cpython/blob/v3.14.7/Doc/using/configure.rst), [fault handling](https://github.com/python/cpython/blob/v3.14.7/Doc/library/faulthandler.rst), [command-line diagnostics](https://github.com/python/cpython/blob/v3.14.7/Doc/using/cmdline.rst), [audit and runtime inspection](https://github.com/python/cpython/blob/v3.14.7/Doc/library/sys.rst).

**CPython 3.14.7:** `sysconfig.get_config_var('Py_GIL_DISABLED')` describes build capability; `sys._is_gil_enabled()` describes runtime state. JIT capability/enablement/activity are separate. Baseline native profilers cannot generally unwind through experimental JIT frames, so interpreter-only tooling assumptions do not transfer unchanged. [Runtime checks](https://github.com/python/cpython/blob/v3.14.7/Doc/library/sys.rst), [JIT tooling limitation](https://github.com/python/cpython/blob/v3.14.7/Doc/whatsnew/3.14.rst).

A falsifiable investigation follows an ordered decision path:

1. Reproduce with the relevant version/build/workload.
2. Separate wall time, CPU attribution, allocation growth, RSS retention, and blocked-loop/worker hypotheses.
3. Choose the least perturbing tool that observes the proposed mechanism.
4. Correlate Python evidence with OS/backend evidence rather than equating their metrics.
5. Change one mechanism and test the predicted effect; account for observer overhead.

## Portability and upgrade-sensitive mechanisms

> [!warning] Other implementation — PyPy
> PyPy uses tracing GC rather than CPython's prompt refcount destruction and does not expose `sys.getrefcount`. Its documented implementation has a GIL, but that does not make a GIL a Python language requirement. Identity behavior and C-API compatibility/performance differ; a compatibility layer does not make CPython private layouts or binary extensions portable. Use explicit resource/view release instead of relying on destruction timing. [PyPy differences](https://doc.pypy.org/cpython_differences.html), [PyPy FAQ](https://doc.pypy.org/faq.html).

**CPython 3.14.7 version ledger:** Recheck the pinned mechanisms rather than assuming a minor/patch upgrade preserves private behavior.

| Subject | Baseline fact | Stability / source to recheck |
| --- | --- | --- |
| Bytecode | Wordcode, family-specific caches | Private/version-specific: [bytecodes](https://github.com/python/cpython/blob/v3.14.7/Python/bytecodes.c) |
| Frames/calls | Data-stack frames, materialized frame objects, embedded suspended frames | Private/build-specific: [frame design](https://github.com/python/cpython/blob/v3.14.7/InternalDocs/frames.md) |
| Adaptive caches | Guarded specialization, family-specific invalidation | Private: [specialization](https://github.com/python/cpython/blob/v3.14.7/Python/specialize.c) |
| JIT | Optional experimental; configure default absent, selected binaries include opt-in; unsupported in free-threaded 3.14 | Build/distribution-specific: [configure](https://github.com/python/cpython/blob/v3.14.7/Doc/using/configure.rst), [release notes](https://github.com/python/cpython/blob/v3.14.7/Doc/whatsnew/3.14.rst) |
| GC | Ordinary three cohorts restored in 3.14.5; free-threaded heap scan differs; dicts always tracked | Patch/build-sensitive: [ordinary GC](https://github.com/python/cpython/blob/v3.14.7/Python/gc.c), [free-threaded GC](https://github.com/python/cpython/blob/v3.14.7/Python/gc_free_threading.c) |
| Immortality/interning | No ordinary refcount updates for immortals; interned-string lifetime differs by build | Implementation-specific: [interning](https://github.com/python/cpython/blob/v3.14.7/InternalDocs/string_interning.md) |
| Process defaults | Windows/macOS spawn; other eligible POSIX forkserver; executor exceptions | Stdlib/platform/version: [contexts](https://github.com/python/cpython/blob/v3.14.7/Lib/multiprocessing/context.py) |
| Asyncio policies | Deprecated 3.14, scheduled removal 3.16 | Stdlib version: [policies](https://github.com/python/cpython/blob/v3.14.7/Doc/library/asyncio-policy.rst) |
| Free-threaded ABI | Separate `t` build; runtime GIL can be enabled | Optional build: [extension guide](https://github.com/python/cpython/blob/v3.14.7/Doc/howto/free-threading-extensions.rst) |
| Stable ABI | Supported contract for eligible conventional builds; unsupported for free-threaded 3.14 | Public compatibility/build scope: [stability](https://github.com/python/cpython/blob/v3.14.7/Doc/c-api/stable.rst) |
| Subinterpreter GIL | Shared/own-GIL configurations and extension checks | C API configuration: [subinterpreters](https://github.com/python/cpython/blob/v3.14.7/Doc/c-api/subinterpreters.rst) |
| Allocation | Normal GIL build pymalloc; free-threaded objects mimalloc | Build/runtime policy: [memory API](https://github.com/python/cpython/blob/v3.14.7/Doc/c-api/memory.rst) |
| Import cache | Marshalled code/invalidation metadata, not executed module state | CPython cache format: [cache loader](https://github.com/python/cpython/blob/v3.14.7/Lib/importlib/_bootstrap_external.py) |

**Language portability constraint:** Do not infer prompt destruction, address-valued `id`, string/small-integer identity, application atomicity from a GIL, prompt RSS reduction, opcode stability, or fixed C-structure layout. Multiprocessing does not eliminate copying; async syntax does not eliminate blocking; native extensions do not automatically release the GIL; many OS threads do not imply simultaneous Python execution in one GIL-enabled interpreter. These distinctions follow from the ownership, scheduling, and transfer boundaries above.
