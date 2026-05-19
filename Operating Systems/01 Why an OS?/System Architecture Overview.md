# System Architecture

* Every system have a set of resources - and those are scarce - so they need to be managed.
* The kernel is OS core component - everything else are built on top of that.
* The Kernel manages the resources
* OS has more tools on top of Kernel for usability.
## CPU
Where the actual execution happen - so it is a very valuable resource. 

It is very critical that the values accessed frequently be as close to the CPU as possible. It isn't memory level, it is actually inside the CPU.

The closest is the L1 level, followed by L2 and L3 - the first two are one-per-core, while the latter often is shared by all the cores of the CPU. 
```mermaid
block-beta

columns 7

  

block:core2:2

columns 1

c2title["CPU Core #2"]

c2alu["ALU"]

c2cu["CU"]

c2reg["Registers"]

space

c2mmu["MMU"]

c2l1["L1"]

end

  

space:3

  

block:core1:2

columns 1

c1title["CPU Core #1"]

c1alu["ALU"]

c1cu["CU"]

c1reg["Registers"]

space

c1mmu["MMU"]

c1l1["L1"]

end

  

c2l2["L2"]:2

space:3

c1l2["L2"]:2

  

l3["Shared L3 Cache"]:7

  

c2reg --> c2mmu

c2mmu --> c2reg

c1reg --> c1mmu

c1mmu --> c1reg

  

c2l1 --> c2l2

c1l1 --> c1l2

c2l2 --> l3

c1l2 --> l3  

class core1,core2 core

class c1alu,c1cu,c2alu,c2cu compute

class c1reg,c2reg register

class c1mmu,c2mmu mmu

class c1l1,c2l1,c1l2,c2l2,l3 cache

class c1title,c2title title
```
Notice that the fact that L1 and L2 caches are individual by core, it creates a whole slew of problem about cache syntonization


Each core has a clock speed.