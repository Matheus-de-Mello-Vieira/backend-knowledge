# Data Structures

## Radix Tree

A **radix tree** is a tree in which portions of the key directly determine which branch to follow. Unlike a comparison-based tree such as a Binary Search Tree, the tree does not repeatedly compare the requested key with values stored in its nodes. Instead, each level consumes part of the key and interprets it directly as an index.

The model used here is a **fixed-stride, uncompressed radix tree**. Every level consumes the same number of bits, and every node contains a fixed-size array of child entries. This model is particularly useful because [multi-level page tables](Operating%20Systems/03%20Memory%20Management.md#The%20Page%20Table%20%26%20Hardware%20Translation) closely resemble it.

A larger stride consumes more of the key at each level. This makes the tree shallower, reducing the number of dependent node accesses required for an operation, but it also makes every node larger. A smaller stride creates smaller nodes but requires a deeper tree.

> [!note]- Notation  
> The base variables are:
>
> - (w) = key width in bits
>
> - (r) = key bits consumed at each level
>
> - (n) = number of stored keys
>
>
> From them, the branching factor is:
>
> $$
> B=2^r  
> $$
>
> and the maximum tree height is:
>
> $$
> h=  
> \left\lceil  
> \frac{w}{r}  
> \right\rceil  
> $$
>
> For example, with a 12-bit key and a stride of 4 bits:
>
> $$
> B=2^4=16  
> $$
>
> and:
>
> $$
> h=\frac{12}{4}=3  
> $$
>
> The key:
>
> `1011 0010 1110`
>
> therefore produces the indexes:
>
> `11 → 2 → 14`

### Operations

#### Lookup

A lookup consumes one portion of the key at each level. The extracted bits identify exactly which child entry to follow, so there is no search or comparison among the node's children.

- A successful lookup follows the path until the complete key has been consumed. An unsuccessful lookup can stop earlier as soon as a required branch does not exist.
- The number of stored keys does not inherently make a lookup path longer. Its length is determined primarily by the key width and the number of key bits consumed at each level.

> [!note]- Complexity: Lookup  
> A successful lookup visits every level:
>
> $$
> \Theta(h)  
> $$
>
> Expanding the derived height:
>
> $$
>
> \boxed{  
> \Theta(h)
>
> \Theta\left(  
>
> \left\lceil\frac{w}{r}\right\rceil  
> \right)
>
> \Theta\left(\frac{w}{r}\right)  
> }  
> $$
>
> Therefore, successful lookup has the same tight bound in its best, mean, and worst cases:
>
> $$
> \boxed{  
> \Theta\left(\frac{w}{r}\right)  
> }  
> $$
>
> An unsuccessful lookup can terminate earlier.
>
> Best case, when the first required branch is absent:
>
> $$
> \boxed{\Theta(1)}  
> $$
>
> Worst case, when failure is discovered only at the final level:
>
> $$
>
> \boxed{  
> \Theta(h)
>
> \Theta\left(\frac{w}{r}\right)  
> }  
> $$
>
> There is no universal mean unsuccessful-lookup bound more precise than these without assuming a distribution of stored and requested keys.
>
> If (w) and (r) are treated as fixed machine parameters, lookup depth does not grow with (n), so with respect to (n):
>
> $$
> \boxed{\Theta(1)}  
> $$
>
> An iterative lookup uses:
>
> $$
> \boxed{\Theta(1)}  
> $$
>
> additional memory.

#### Insert

Insertion follows the same path as lookup. Existing nodes are reused for as long as the required prefix already exists.

- When the operation encounters a missing branch, it creates the remaining part of the path and stores the value at the final location.
- This makes prefix sharing important for memory usage. Inserting a key near existing keys may reuse almost the entire hierarchy, while inserting a key in an unrelated part of the key space can require a mostly new branch.

> [!note]- Complexity: Insert  
> Insertion processes every key level, either by traversing an existing node or creating a missing one:
>
> $$
> \Theta(h)  
> $$
>
> Expanding (h):
>
> $$
>
> \boxed{  
> \Theta(h)
>
> \Theta\left(\frac{w}{r}\right)  
> }  
> $$
>
> Under the fixed-stride model, best, mean, and worst insertion time therefore have the same tight bound:
>
> $$
> \boxed{  
> \Theta\left(\frac{w}{r}\right)  
> }  
> $$
>
> The number of **new nodes** differs.
>
> If the hierarchy already exists:
>
> $$
> \boxed{0\text{ new nodes}}  
> $$
>
> may be required.
>
> In the worst case, insertion creates:
>
> $$
> \Theta(h)  
> $$
>
> nodes:
>
> $$
>
> \boxed{  
> \Theta(h)
>
> \Theta\left(\frac{w}{r}\right)  
> }  
> $$
>
> Since each node contains:
>
> $$
> B=2^r  
> $$
>
> child entries, the worst-case newly allocated node-array storage is:
>
> $$
> \Theta(hB)  
> $$
>
> which expands to:
>
> $$
>
> \boxed{  
> \Theta(hB)
>
> \Theta\left(  
> \frac{w}{r}2^r  
> \right)  
> }  
> $$
>
> There is no universal mean allocation cost without assumptions about how much prefix sharing exists between inserted keys.

#### Update

Updating an existing key first follows its normal lookup path. Once the final location is reached, the stored value is replaced.

Because the key itself does not change, the tree structure normally remains unchanged.

> [!note]- Complexity: Update  
> Lookup requires:
>
> $$
> \Theta(h)  
> $$
>
> and replacing the value requires:
>
> $$
> \Theta(1)  
> $$
>
> Therefore:
>
> $$
>
> \boxed{  
> \Theta(h)
>
> \Theta\left(\frac{w}{r}\right)  
> }  
> $$
>
> Best, mean, and worst successful updates have the same tight traversal bound because the full key must be resolved.
>
> Updating an existing value requires:
>
> $$
> \boxed{\Theta(1)}  
> $$
>
> additional structural memory.
>
> If (w) and (r) are fixed, update does not grow with (n):
>
> $$
> \boxed{\Theta(1)}  
> $$
>
> with respect to the number of stored keys.
>
> If a missing update behaves as an **upsert**, that case follows the insertion bounds instead.

#### Delete

Deletion first follows the key to its stored value and removes it.

Afterward, the implementation can walk backward through the path and reclaim nodes that no longer contain a value and no longer lead to another stored key. Shared prefix nodes remain because other keys still depend on them.

> [!note]- Complexity: Delete  
> Locating an existing key requires:
>
> $$
> \Theta(h)  
> $$
>
> Cleanup examines at most the same path:
>
> $$
> O(h)  
> $$
>
> Therefore successful deletion is tightly:
>
> $$
>
> \boxed{  
> \Theta(h)
>
> \Theta\left(\frac{w}{r}\right)  
> }  
> $$
>
> Best, mean, and worst successful deletion time therefore share the same asymptotic bound.
>
> The amount of reclaimed structure varies from:
>
> $$
> \boxed{0\text{ nodes}}  
> $$
>
> when the path remains shared, to:
>
> $$
>
> \boxed{  
> \Theta(h)
>
> \Theta\left(\frac{w}{r}\right)  
> }  
> $$
>
> nodes when the deleted key owns a private suffix.
>
> Deleting a missing key behaves like an unsuccessful lookup.
>
> Best case:
>
> $$
> \boxed{\Theta(1)}  
> $$
>
> Worst case:
>
> $$
>
> \boxed{  
> \Theta(h)
>
> \Theta\left(\frac{w}{r}\right)  
> }  
> $$

#### Traversal

A complete traversal is different from key-based operations because there is no single path to follow. Every allocated node and its child entries must be inspected.

The cost therefore depends on the size of the populated structure, not only on the width of one key.

> [!note]- Complexity: Traversal  
> Let:
>
> $$
> N=\text{number of allocated radix-tree nodes}  
> $$
>
> Each node contains:
>
> $$
> B=2^r  
> $$
>
> entry slots.
>
> Inspecting every slot therefore requires:
>
> $$
> \Theta(NB)  
> $$
>
> or:
>
> $$
>
> \boxed{  
> \Theta(NB)
>
> \Theta(N2^r)  
> }  
> $$
>
> Unlike (h), (N) cannot be reduced to one universal tight function of (w), (r), and (n), because it depends on prefix sharing.
>
> One terminal node can represent at most (B) final key positions, while reaching populated terminal nodes also requires the hierarchy above them. Therefore:
>
> $$
> N=  
> \Omega\left(  
> h+\frac{n}{B}  
> \right)  
> $$
>
> while each key can introduce at most (h) nodes:
>
> $$
> N=O(nh)  
> $$
>
> Expanding (h) and (B):
>
> $$
> \boxed{  
> \Omega\left(  
> \frac{w}{r}+\frac{n}{2^r}  
> \right)  
> \leq  
> N  
> \leq  
> O\left(  
> n\frac{w}{r}  
> \right)  
> }  
> $$
>
> Therefore:
>
> $$
> \boxed{  
> \Omega\left(  
> \frac{w}{r}2^r+n  
> \right)  
> \leq  
> T_{\text{traversal}}  
> \leq  
> O\left(  
> n\frac{w}{r}2^r  
> \right)  
> }  
> $$
>
> If (w) and (r) are fixed, this simplifies with respect to (n) to:
>
> $$
> \boxed{\Theta(n)}  
> $$
>
> A recursive traversal of a tree containing a full-depth key also requires:
>
> $$
>
> \boxed{  
> \Theta(h)
>
> \Theta\left(\frac{w}{r}\right)  
> }  
> $$
>
> stack depth.

### Memory Usage

A radix tree is particularly useful when the possible key space is enormous but only a small portion of it is populated.

A direct array allocates storage for every possible key position. A radix tree instead allocates only the branches necessary to reach stored keys.

Keys with common prefixes share the same upper nodes, so clustering keys together can substantially reduce structural memory. Keys spread across unrelated prefixes require more independent branches.

The radix determines a fundamental trade-off. Consuming more bits per level creates fewer levels but exponentially larger nodes. Consuming fewer bits creates smaller nodes but requires more dependent memory accesses during traversal.

> [!note]- Complexity: Total Memory  
> With:
>
> $$
> N=\text{allocated nodes}  
> $$
>
> and:
>
> $$
> B=2^r  
> $$
>
> entries per node, physical node-array memory is:
>
> $$
> S=\Theta(NB)  
> $$
>
> or:
>
> $$
> \boxed{  
> S=  
> \Theta(N2^r)  
> }  
> $$
>
> Since:
>
> $$
> \Omega\left(  
> h+\frac{n}{B}  
> \right)  
> \leq  
> N  
> \leq  
> O(nh)  
> $$
>
> multiplying by (B) gives:
>
> $$
> \Omega(hB+n)  
> \leq  
> S  
> \leq  
> O(nhB)  
> $$
>
> Expanding the derived variables:
>
> $$
> \boxed{  
> \Omega\left(  
> \frac{w}{r}2^r+n  
> \right)  
> \leq  
> S  
> \leq  
> O\left(  
> n\frac{w}{r}2^r  
> \right)  
> }  
> $$
>
> There is no universal tighter expression without assumptions about prefix sharing.
>
> The radix trade-off follows from:
>
> $$
> B=2^r  
> $$
>
> and:
>
> $$
> h=  
> \left\lceil  
> \frac{w}{r}  
> \right\rceil  
> $$
>
> Therefore increasing (r) grows each node exponentially while reducing the number of levels:
>
> $$
> r\uparrow  
> \Rightarrow  
> B\uparrow  
> \Rightarrow  
> h\downarrow  
> $$
