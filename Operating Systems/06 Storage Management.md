# Storage Management

## Storage

Some data must survive process termination, system shutdowns, and power loss. Because RAM is **volatile**, it cannot provide this persistence by itself. Computers therefore use non-volatile storage such as **magnetic tape, HDDs, SSDs, and flash-based devices**.

Persistent storage is generally much slower than RAM, especially in terms of access latency. The performance difference is particularly important for storage technologies such as HDDs, where accessing data may require physical mechanical movement.

### HDD

A **Hard Disk Drive (HDD)** is a non-volatile storage device that stores data magnetically on rotating disks called **platters**. HDDs historically became the dominant form of secondary storage because they could provide large capacities at a relatively low cost per byte.

Unlike RAM or SSDs, an HDD is partly mechanical. Reading data may require moving a physical arm and waiting for the desired portion of a spinning platter to reach the read/write head. This mechanical behavior explains many of the characteristic performance properties of HDDs.

> [!note] Why HDDs Are Called “Hard”
>
> The term **“hard”** in **hard disk drive (HDD)** refers to the rigid platters used to store data. This originally distinguished HDDs from **floppy disks**, whose magnetic storage medium was physically flexible.
>
> HDD platters are typically made from rigid materials such as aluminum or glass and coated with a magnetic material. Modern devices such as SSDs are also physically rigid, so the word **hard** is mainly a historical distinction that survived after floppy disks disappeared from common use.

#### Physical Geometry and CHS

An HDD contains one or more **platters** mounted on a spindle and rotating at a fixed speed. Each recording surface is accessed by a **read/write head** positioned extremely close to the platter. The heads are attached to the same actuator assembly, so moving the actuator changes the radial position of all heads together.

Each platter surface is organized into concentric circles called **tracks**, and each track is divided into **sectors** containing chunks of data. Tracks at the same radial position across the different platter surfaces form a **cylinder**.

Early systems exposed this geometry directly through **CHS (Cylinder, Head, Sector)** addressing. A location was identified using three values:

- **Cylinder:** selects the radial position of the actuator.
- **Head:** selects a particular recording surface.
- **Sector:** selects a region of the track as the platter rotates.

CHS therefore reflected the physical organization of early disks relatively closely. However, as HDDs became more sophisticated, their internal geometry stopped mapping cleanly to a simple fixed number of tracks and sectors. For example, modern drives can place more sectors on outer tracks because those tracks have a greater circumference.

This made exposing physical disk geometry to software increasingly inconvenient and eventually led to the adoption of **Logical Block Addressing**.

#### Data Access

HDDs are **block devices**: software addresses storage in blocks rather than requesting arbitrary individual bytes directly from the device.

At the hardware level, HDDs traditionally used **512-byte sectors**, while modern drives commonly use **4 KiB physical sectors**, known as **Advanced Format**. Some drives expose those 4 KiB sectors directly, while others maintain compatibility by exposing 512-byte **logical sectors** even though the underlying physical sector is 4 KiB.

This distinction matters for writes. If a drive has 4 KiB physical sectors but software requests an unaligned modification smaller than 4 KiB, the drive may need to read the existing physical sector, modify the relevant portion, and write the entire sector again. This is a **read-modify-write** operation and adds additional I/O.

The mechanical nature of HDDs has an even larger effect on performance. Accessing a block generally involves two important delays:

- **Seek time:** moving the actuator so that the head reaches the correct track.
- **Rotational latency:** waiting for the desired sector to rotate underneath the head.

Once the head is correctly positioned, contiguous sectors can be transferred rapidly as they pass beneath it. Consequently, HDD performance depends strongly on the access pattern.

With **sequential access**, nearby blocks can be read or written with relatively little additional mechanical movement. With **random access**, the drive may repeatedly seek between distant tracks and wait for different sectors to rotate into position. Random I/O is therefore dramatically slower than sequential I/O on HDDs.

This distinction means that two workloads transferring the same number of bytes can have very different performance depending on how those bytes are distributed across the disk.

#### Logical Block Addressing (LBA)

Exposing CHS geometry forced software to understand details of the physical disk layout. **Logical Block Addressing (LBA)** replaces this interface with a much simpler abstraction.

Under LBA, the disk is presented as a linear sequence of fixed-size logical blocks such as `LBA 0, LBA 1, LBA 2, ...`. Software therefore requests a block by its number rather than specifying a cylinder, head, and sector.

The drive's internal controller and firmware determine where each logical block is physically stored. The mapping does not need to correspond to a simple CHS calculation: modern drives can internally reorganize storage, compensate for differences in track geometry, and transparently replace defective sectors with spare sectors.

This indirection allows the physical implementation of the drive to evolve independently from the interface exposed to the operating system. The OS only needs to understand a linear address space of logical blocks, while the HDD manages its actual physical geometry internally.

The same abstraction also makes **bad-sector remapping** possible. If a physical sector becomes unreliable, the drive can redirect its LBA to a spare physical sector while continuing to expose the same logical address to the operating system. From the software's perspective, the location of the block has not changed.

> [!note] LBA Blocks and Virtual Memory Pages
>
> **LBA logical blocks** and **[virtual memory](03%20Memory%20Management.md#Virtual%20Memory)** are independent abstractions, but having compatible sizes is convenient for operations such as **swapping**.
>
> The kernel swaps memory in page-sized units. If the system uses 4 KiB virtual-memory pages and the storage device exposes 4 KiB logical blocks, one swapped page can conceptually fit into one LBA block. If the device instead exposes 512-byte logical blocks, the same 4 KiB page simply spans eight consecutive LBAs.
>
> The operating system therefore does not require `1 VM page = 1 LBA block`. It normally manages swapping in **page-sized swap slots**, while the block layer translates those slots into however many logical blocks the storage device requires.
>
> Matching or well-aligned granularities are still useful because they can simplify I/O and avoid inefficient partial operations. This is one reason sizes such as **4 KiB** appear repeatedly across virtual memory, filesystems, and storage devices, even though each layer chooses its granularity independently.
> [!note] Logical vs. Physical Sector Size
>
> **LBA (Logical Block Addressing)** identifies blocks in the logical address space exposed by the storage device to the operating system. An LBA is an **address**, while the **logical sector size** describes how many bytes each address represents.
>
> Internally, the device may operate using a different **physical sector size**. The physical location corresponding to logical data is sometimes described using a **Physical Block Address (PBA)**, although the exact internal addressing scheme is device-specific and normally hidden from the host.
>
> The logical and physical sizes do not need to match. For example, a **512e** HDD may expose 512-byte logical sectors while internally using 4 KiB physical sectors, so `8 × 512 B logical sectors → 1 × 4 KiB physical sector`.
>
> A **4Kn** drive instead exposes 4 KiB logical sectors directly, making the logical and physical sector sizes equal.
>
> This distinction is possible because the storage controller translates the host-visible LBA space into the device's internal physical organization.
>
#### File Fragmentation and Defragmentation

Filesystems generally try to allocate the logical blocks belonging to a file close together. Over time, however, files are created, extended, modified, and deleted, leaving available regions of different sizes throughout the filesystem. When there is not enough contiguous free space for a file, the filesystem may split it into multiple non-contiguous **extents**. This is known as **file fragmentation**.

Fragmentation is particularly expensive on an HDD because sequential file access can turn into multiple mechanical seeks. Suppose a large file consists of three extents located in distant regions of the disk. Reading each extent internally may be sequential, but when the read reaches the end of one extent, the actuator may need to move to another track and wait for the correct sector to rotate under the head before continuing.

A logically sequential operation can therefore become a sequence of smaller, partially random operations: `Extent A → seek → Extent B → seek → Extent C`

The more fragmented the file is, the more often the HDD may pay **seek time** and **rotational latency** instead of continuously transferring data.

**Defragmentation** attempts to reverse this process. The filesystem or defragmentation utility moves file extents so that the logical blocks belonging to the same files become more contiguous. It may also consolidate free space, making it easier for future files to receive contiguous allocations.

After defragmentation, reading a file can require fewer seeks and allow the HDD to spend more time performing efficient sequential transfers. This can significantly improve workloads involving large fragmented files or systems where fragmentation has accumulated for a long time.

Because software operates through LBA, it does not directly control the exact physical platter coordinates. Defragmentation therefore primarily makes the file's **logical blocks** contiguous. HDD firmware generally maps nearby sequential LBAs to nearby physical locations, so this still tends to preserve physical locality, although internal remapping such as bad-sector replacement can prevent the correspondence from being perfect.

### SSD

A **Solid-State Drive (SSD)** is a non-volatile storage device built primarily from **NAND flash memory**. Unlike HDDs, SSDs have no moving mechanical parts: data is accessed electronically rather than by moving a head over a rotating platter. This gives SSDs much lower access latency and makes **random reads and writes** dramatically faster than on HDDs.

However, NAND flash has an important constraint that shapes the entire architecture of an SSD: **reading, programming, and erasing operate at different granularities**. Data is read and programmed in relatively small units called **pages**, but pages cannot normally be overwritten in place. Before previously programmed flash can be reused, a much larger group of pages must be erased together.

The SSD controller therefore sits between the host and the raw NAND chips, maintaining mappings and continuously reorganizing physical storage so that the device can still expose the simple linear block interface expected by the operating system.

#### NAND Pages and Physical Blocks

NAND flash is organized hierarchically. The smallest unit normally read or programmed is a **page**, commonly several KiB to tens of KiB in modern NAND. Many pages are grouped into a much larger **physical block**, which is the smallest unit that NAND can erase.

This creates an important asymmetry:

- **Read:** operates on pages.
- **Program/write:** operates on pages.
- **Erase:** operates on entire physical blocks containing many pages.

A physical block can contain hundreds or even thousands of pages depending on the NAND generation. Because erase operations happen at this larger granularity, individual pages cannot simply be erased and reused independently.

> [!note] Page and Block Terminology
>
> **Page** and **block** are heavily overloaded terms in computer systems. In storage, a **logical block** refers to a unit in the LBA address space exposed to the operating system, while a NAND **physical block** refers to an erase unit containing many flash pages.
>
> In these notes, **logical block** refers to storage addressed through LBA, while **physical block** refers to the NAND erase unit inside an SSD.

This read/program/erase asymmetry is the fundamental reason SSDs need mechanisms such as the **Flash Translation Layer**, out-of-place writes, garbage collection, and wear leveling.

#### Flash Translation Layer

The operating system does not address NAND flash directly. An SSD exposes a **Logical Block Addressing (LBA)** interface, presenting storage as a linear sequence of logical blocks.

The SSD controller bridges this logical address space and the physical NAND through the **Flash Translation Layer (FTL)**. A useful simplified model is to imagine that each logical block maps to one physical NAND page: `Logical block → Physical NAND page`

For example, `LBA 100 → Page P40`: Under this model, when the host reads `LBA 100`, the FTL looks up its mapping and retrieves the data from physical page `P40`.

The important property of the mapping is that it is **dynamic rather than permanent**. Because NAND pages cannot normally be overwritten in place, updating a logical block may cause the SSD to write the new value into another free physical page and then change the mapping.

For example, `LBA 100 → P40` may later become `LBA 100 → P93`. The logical address visible to the operating system has not changed, but its physical location inside the NAND has.

This indirection is fundamental to SSD operation. It allows the controller to perform [out-of-place writes](#Out-of-Place%20Writes), relocate data during [garbage collection](#Garbage%20Collection), and distribute writes through [wear leveling](#Wear%20Leveling) without changing the LBA addresses exposed to the host.

As a consequence, consecutive logical blocks do not necessarily remain physically adjacent, and a logical block does not have a permanent physical NAND location.

The FTL must maintain metadata describing these logical-to-physical mappings. Because the mappings are necessary to reconstruct the drive's state after power loss, authoritative metadata must ultimately be persisted in non-volatile storage. SSDs commonly cache frequently accessed mapping information in **DRAM**, while smaller amounts of SRAM are used internally by the controller. DRAM-less SSDs rely more heavily on NAND metadata or, in some designs, host memory.

> [!note] The One-LBA-to-One-Page Model Is a Simplification
>
> Treating the FTL as `1 logical block → 1 physical NAND page` is a convenient model for understanding SSD behavior, but it is not a requirement of the hardware.
>
> The **LBA logical block size** exposed to the host and the internal **NAND page size** are independent. For example, an SSD may expose 4 KiB logical blocks while using 16 KiB NAND pages internally. Several logical blocks may therefore share one physical page, and controllers may buffer, combine, or reorganize writes before programming NAND.
>
> Real FTLs may also use more complex mapping schemes to reduce the amount of metadata they must maintain.
>
> The essential abstraction remains the same: the FTL translates the **host-visible logical address space** into **physical locations within NAND**. The one-to-one model is useful for reasoning about this translation without implying that the underlying granularities must actually match.
>
#### States of a Page

From the SSD controller's perspective, a NAND page can usually be understood as being in one of three logical states:

- **Free / erased:** the page belongs to an erased physical block and is available to receive new data.
- **Valid:** the page contains the current physical representation of some logical data and is referenced by the FTL.
- **Invalid / stale:** the page still physically contains old data, but the FTL no longer references it because that logical data was updated or discarded.

The distinction between **valid** and **invalid** therefore depends on the FTL mapping rather than on whether bits are physically present in the page.

A crucial constraint is that an invalid page cannot simply transition back to **free** by itself. NAND erase operations apply to an entire physical block, so invalid pages become reusable only after the whole block containing them is erased.

As updates accumulate, physical blocks gradually become mixtures of valid and invalid pages. Reclaiming the space occupied by those invalid pages is the purpose of garbage collection.

#### Out-of-Place Writes

Because NAND pages cannot normally be overwritten directly, SSD updates use **out-of-place writes**.

- Suppose logical block `LBA 100` currently maps to physical page `P40`: `LBA 100 → P40`
- If the host updates that logical block, the SSD does not overwrite `P40`. Instead, the controller finds a free page such as `P93`, writes the new data there, and changes the FTL mapping: `LBA 100 → P93`
- The old page `P40` is then considered **invalid** because no logical block references it anymore.

The update therefore follows this sequence:

1. Find a free physical page.
2. Program the new data into that page.
3. Update the FTL mapping.
4. Mark the previous physical page as invalid.

Out-of-place writes avoid performing an expensive block erase for every small update. However, they gradually consume free pages and leave invalid pages distributed throughout physical blocks. Those invalid pages must eventually be reclaimed before the underlying space can be reused.

#### Garbage Collection

Because NAND can erase only entire physical blocks, the SSD cannot independently reclaim individual invalid pages. A physical block may also contain valid pages that must be preserved before the block can be erased.

When the controller needs additional reusable space, it performs **Garbage Collection (GC)**. It selects a physical block containing invalid pages, copies any remaining valid pages into free locations elsewhere, updates their FTL mappings, and erases the original physical block.

For example, suppose a physical block contains 100 pages:

- 80 invalid pages
- 20 valid pages

The SSD can copy the 20 valid pages elsewhere and then erase the entire physical block. After the erase, all 100 pages become free again.

Garbage collection therefore converts fragmented invalid space into reusable erased blocks. The trade-off is that the SSD must perform additional internal reads and writes that were never explicitly requested by the host.

Garbage collection is particularly expensive when the drive has little free space. If candidate blocks contain many valid pages, the controller must relocate more data before it can reclaim a block.

#### Write Amplification

Garbage collection and other internal relocation operations mean that the amount of data physically written to NAND can exceed the amount requested by the host. This effect is called **write amplification**.

It can be expressed as: `Write Amplification = NAND bytes written / Host bytes written`

For example, if the host writes 1 GiB but the SSD internally writes 1.5 GiB because it also needs to relocate existing pages, the write amplification factor is: `1.5 GiB / 1 GiB = 1.5`

Write amplification matters for two reasons. First, additional internal writes consume NAND bandwidth and can reduce sustained write performance. Second, NAND cells tolerate only a finite number of program/erase cycles, so unnecessary writes also consume part of the drive's endurance.

Garbage collection, filesystem access patterns, free-space availability, over-provisioning, and the efficiency of the FTL all influence write amplification.

#### TRIM

When a file is deleted, the filesystem usually does not overwrite all of its previous data. It simply updates its own metadata and considers the corresponding logical blocks available for reuse.

Without additional information, the SSD cannot know that those logical blocks are no longer useful. From the drive's perspective, their physical pages may still appear valid because they remain mapped by the FTL.

The **TRIM** command allows the operating system to tell the SSD that specific logical blocks are no longer needed.

The controller can then invalidate the corresponding mappings and treat their physical pages as stale. During future garbage collection, those pages no longer need to be copied elsewhere.

TRIM therefore communicates filesystem knowledge to the SSD, reducing unnecessary data movement and potentially lowering write amplification.

> [!note] TRIM Extends the Basic LBA Abstraction
>
> A minimal **LBA** interface only needs to let the host **read** and **write** logical blocks. It does not communicate whether the data currently stored at an LBA is still useful.
>
> This was usually sufficient for traditional HDDs because a sector can simply be overwritten later. NAND flash is different: an SSD cannot overwrite a programmed page in place, so knowing that some logical data has been discarded allows the controller to treat the corresponding physical pages as invalid instead of preserving them during garbage collection.
>
> **TRIM** therefore extends the basic block-device interface with an additional semantic operation: the host can tell the device that it no longer cares about the contents of a range of logical blocks.
>
> Conceptually, the interface becomes:
>
> - `read(LBA)`
> - `write(LBA, data)`
> - `discard(LBA range)`
>
> **TRIM** is the ATA name for this operation. Other storage interfaces provide equivalent mechanisms, such as **SCSI UNMAP** and **NVMe deallocation**. The more general concept is usually called **discard** or **block deallocation**.
>
> Although this mechanism became especially important with SSDs, it is not inherently SSD-specific. Thin-provisioned storage, virtual disks, and other storage systems can also use discard information to reclaim underlying resources.
>
#### Wear Leveling

NAND flash has limited endurance. A physical block can tolerate only a finite number of **program/erase cycles** before its cells become unreliable.

Workloads also tend to access data unevenly. Some pages are rewritten frequently, while others remain unchanged for long periods. SSD terminology often describes these as:

- **Hot pages:** data that is updated frequently.
- **Cold pages:** data that changes rarely or remains static for long periods.

If the controller always reused the same convenient physical blocks for hot data, those blocks would accumulate erase cycles much faster than blocks holding cold data. Some parts of the NAND could therefore wear out while others had experienced relatively little use.

SSDs avoid this through **wear leveling**, which distributes program/erase cycles across the available physical blocks. The indirection provided by the FTL makes this possible because logical addresses are not permanently tied to particular physical locations.

Wear leveling generally has two forms:

- **Dynamic wear leveling:** when writing or relocating hot data, the controller prefers physical blocks with lower erase counts. This spreads future writes across blocks that have experienced less wear.
- **Static wear leveling:** the controller may also relocate cold data. A physical block containing cold pages might otherwise remain occupied for years while hotter blocks are repeatedly erased. Moving that cold data into a more heavily worn block frees the less-worn block so it can participate in future writes.

Static wear leveling is therefore somewhat counterintuitive: the SSD may deliberately move data that has not changed at all. The purpose is not to improve that data's access performance, but to prevent cold data from permanently reserving the least-worn physical blocks.

Wear leveling trades additional internal data movement for a more uniform distribution of wear across the NAND, increasing the usable lifetime of the drive.

#### Over-Provisioning

An SSD usually contains more physical NAND capacity than it exposes to the operating system. The portion that is deliberately kept outside the host-visible LBA address space is called **over-provisioning**.

For example, an SSD might physically contain more NAND than its advertised usable capacity. The operating system can never allocate this reserved space directly, so the SSD controller can rely on it as a permanent pool of spare physical pages and blocks.

This matters because SSD writes are **out-of-place**. When the host updates data, the controller needs a free physical page where it can write the new version before invalidating the old one. Garbage collection also needs temporary free space when it copies valid pages out of a physical block before erasing that block.

Without enough free space, these operations become increasingly difficult. The controller may need to perform garbage collection before it can satisfy a new write, and it may be forced to choose physical blocks containing many valid pages. That means more pages must be copied simply to reclaim a small amount of reusable space.

Over-provisioning prevents the host from consuming all physical NAND, giving the controller additional freedom to:

- satisfy out-of-place writes without first performing expensive cleanup,
- choose better victim blocks during garbage collection,
- relocate fewer valid pages when reclaiming space,
- reduce **write amplification**,
- distribute writes more effectively for **wear leveling**,
- keep spare physical blocks available to replace worn or defective ones.

The effect can be understood by considering a nearly full SSD. If almost every physical page contains valid data, reclaiming one physical block may require copying nearly all of its pages elsewhere before erasing it. With additional over-provisioned space, the controller has more free pages and more candidate blocks to work with, making it more likely that it can reclaim blocks containing mostly invalid data.

Over-provisioning therefore does not directly make NAND faster. Instead, it gives the SSD controller **working space to manage NAND efficiently**, which improves sustained write performance, reduces internal data movement, and helps extend the lifetime of the flash.

There is also a related but distinct effect when the user leaves filesystem space unused. If the operating system communicates that unused space through **TRIM**, the SSD can treat the corresponding physical pages as reclaimable and use them similarly to additional spare space. Unlike factory over-provisioning, however, this space is not permanently reserved: the host may allocate it again later.

#### SSD Performance Characteristics

SSDs eliminate the **seek time** and **rotational latency** that dominate random-access performance on HDDs. Accessing physically distant NAND pages therefore does not incur the same mechanical penalty as jumping between distant locations on a disk platter.

As a result, SSDs provide much higher random I/O performance and much lower latency than HDDs.

However, SSD access is not completely uniform. Reads are generally cheaper than writes, and writes can become significantly more expensive when the drive must perform garbage collection or erase physical blocks. Large sequential operations can also achieve higher throughput than small random operations because they make more efficient use of the SSD controller, NAND channels, and internal parallelism.

The performance model is therefore different from an HDD rather than completely free of locality effects. HDD performance is dominated by mechanical positioning, while SSD performance is strongly influenced by **NAND parallelism, free-space availability, garbage collection, write amplification, and the read/program/erase asymmetry of flash memory**.

#### Fragmentation and Defragmentation on SSDs

The [file fragmentation](#File%20Fragmentation%20and%20Defragmentation) described for HDDs also exists at the filesystem level on SSDs: a file can still be split across multiple non-contiguous extents. What changes is the performance consequence.

On an HDD, defragmentation improves locality because reading separated extents may require expensive mechanical seeks and rotational waiting. An SSD has no equivalent mechanical movement, so accessing distant logical addresses is much closer in cost to accessing adjacent ones. Fragmentation therefore has a much smaller effect on read performance.

The **Flash Translation Layer (FTL)** weakens the value of filesystem-level contiguity even further. Consecutive logical blocks do not necessarily correspond to consecutive physical NAND pages because the FTL continuously remaps and relocates data through out-of-place writes, garbage collection, and wear leveling. Making a file contiguous in the LBA address space therefore does not guarantee physical contiguity inside the NAND.

Traditional defragmentation can instead be counterproductive on an SSD because it requires **moving and rewriting large amounts of data**. From the filesystem's perspective, the operation is reorganizing extents; to the SSD, those relocations are ordinary writes. The FTL must allocate new physical pages, invalidate the old pages, and eventually reclaim them through garbage collection.

These operations consume NAND endurance while providing little of the locality benefit that justified defragmentation on HDDs.

### Other Storage Devices

- **Magnetic Tape:** Stores data magnetically on a long strip of tape. It offers very high capacity and low cost per byte, but access is fundamentally sequential because the tape must be physically wound to the desired position. It is therefore mainly used for backups and long-term archival storage rather than interactive workloads.
- **Optical Discs:** Devices such as **CDs, DVDs, and Blu-ray discs** store data as physical or optical changes on a rotating disc that are read with a laser. They provide removable, non-volatile storage, but have relatively low capacity and performance compared with modern HDDs and SSDs.
- **USB Flash Drives:** Portable storage devices built from NAND flash memory and connected through USB. Internally they use many of the same principles as SSDs, including a controller and flash translation, but usually have simpler controllers, less parallelism, and lower endurance and sustained performance.
- **SD and microSD Cards:** Small removable NAND flash devices commonly used in cameras, smartphones, embedded systems, and other portable devices. Like USB flash drives, they contain a controller that hides the physical NAND organization behind a logical block interface, but their performance and endurance vary significantly between product classes.
- **eMMC:** An embedded storage package combining NAND flash and a controller in a single chip. It is soldered directly onto the device rather than being removable and is commonly found in inexpensive embedded systems and older mobile devices. It provides a simple block-device interface but generally offers less parallelism and performance than modern SSDs.
- **UFS (Universal Flash Storage):** An embedded NAND-based storage technology designed as a higher-performance successor to eMMC. Unlike eMMC's more limited command model, UFS supports features such as command queuing and simultaneous reads and writes, making it better suited to modern smartphones and embedded systems.
- **Persistent Memory / NVRAM:** Technologies that retain data without power while providing access characteristics closer to memory than conventional block storage. Some designs can be accessed directly through the CPU's memory address space rather than through traditional block I/O, partially blurring the distinction between **memory** and **storage**.

## File Systems

A **file system** is the set of data structures and rules an operating system uses to organize persistent data on a storage device.

At the block-device level, storage is exposed as a flat **Logical Block Addressing (LBA)** space: essentially a large sequence of numbered logical blocks. This interface is convenient for the operating system but not for applications or users, which generally want to work with concepts such as **files, directories, paths, names, and permissions** rather than raw block numbers.

The file system provides this higher-level abstraction. It determines which logical blocks belong to each file, maintains the directory hierarchy used to locate files by name, records metadata about them, tracks which storage regions are free, and coordinates reads and writes to persistent storage.

A file therefore does not need to occupy one contiguous region of the device. The filesystem maintains metadata describing which logical blocks contain its contents, allowing a logically continuous file to be assembled from multiple physical regions.

### Basic Concepts

- **File:** A named logical sequence of data managed by the filesystem. The filesystem associates the file's contents with metadata describing properties such as its size, ownership, permissions, and timestamps.
- **Directory (Folder):** A structure that associates names with files and other directories, allowing files to be organized hierarchically. A directory is therefore not merely a visual container; it is part of the filesystem's name-resolution mechanism.
- **Path:** A sequence of directory names used to locate a filesystem object.
    - **Absolute Path:** Identifies an object starting from the filesystem's root
    - **Relative Path:** Identifies an object starting from some current directory.
- **File Extension:** A suffix such as `.txt`, `.jpg`, or `.exe` conventionally used to indicate a file's format or intended interpretation. The extension is normally just part of the filename; the filesystem itself does not necessarily use it to determine the actual type of the file.
- **File Permissions:** Metadata controlling which users or processes may perform operations such as reading, writing, or executing a file. The exact permission model depends on the filesystem and operating system. Unix-like systems, for example, commonly distinguish permissions for an owner, a group, and other users. [security permissions](../Security/05%20Architecture%20and%20Infrastructure%20Security/02%20Endpoint%20Security.md) build on this metadata to enforce access control.

### Mapping Files to Logical Blocks

Applications work with files as logical sequences of bytes, while the storage device exposes a flat **LBA address space**. The filesystem bridges these views by dividing file data into allocation units and maintaining metadata that records where those units are stored.

A file therefore does not need to occupy one contiguous region of the device. Its contents can be distributed across multiple logical-block ranges while still appearing to the application as one continuous byte sequence.

#### Filesystem Blocks

Filesystems commonly introduce their own allocation unit called a **filesystem block**. This is distinct from the logical block size exposed by the storage device through LBA.

For example, if the device exposes `LBA logical sector = 512 B` and the filesystem uses `Filesystem block = 4 KiB`, then one filesystem block spans eight consecutive logical sectors: `1 filesystem block → 8 × 512 B logical sectors`. If the device instead exposes 4 KiB logical sectors, the relationship may be `1 filesystem block → 1 × 4 KiB logical sector`.

The filesystem block size is normally chosen when the filesystem is **created during formatting**. Tools such as `mkfs` may allow it to be configured explicitly, although they usually select a sensible default. Changing the block size later generally requires recreating the filesystem.

The first constraint comes from the storage device's **logical sector size**. Because filesystem I/O is ultimately translated into LBA operations, a filesystem block must be representable as an integer number of logical sectors.

The filesystem should also align its blocks with the device's **physical sector size** when possible. For example, on a drive with `Logical sector = 512 B` and `Physical sector = 4 KiB`, a 4 KiB filesystem block can map cleanly to eight logical sectors while also fitting exactly inside one physical sector: `1 × 4 KiB filesystem block → 8 × 512 B logical sectors → 1 × 4 KiB physical sector`.

This is efficient because a filesystem block can be updated without unnecessarily touching multiple physical sectors.

A smaller filesystem block may still be valid. For example, a 1 KiB filesystem block can be represented by two 512-byte logical sectors. However, four such filesystem blocks share the same 4 KiB physical sector. Updating only one of them may require the storage device to preserve the rest of the physical sector, potentially introducing a **read-modify-write** operation.

Block **boundaries** matter as well as block size. Even a 4 KiB filesystem block can be poorly aligned if it begins in the middle of a 4 KiB physical sector, causing one filesystem block to span parts of two physical sectors. Partitioning and filesystem creation tools therefore normally align filesystem structures to the device's reported physical geometry.

Once these storage constraints are satisfied, the filesystem can choose among its supported block sizes according to workload characteristics.

In the conventional allocation model, a data block allocated to one file is not reused by another unrelated file. If the file does not completely fill its final block, the remaining bytes become **slack space**, a form of internal fragmentation.

For example, with 4 KiB filesystem blocks, a `6 KiB file → 4 KiB full block + 2 KiB used in another 4 KiB block`. The remaining 2 KiB in the second block is unused by that file and normally unavailable to unrelated files.

This creates a secondary trade-off:

- **Smaller filesystem blocks** reduce slack space for workloads containing many small files, but large files require more allocation units and potentially more mapping metadata.
- **Larger filesystem blocks** reduce the number of allocation units needed for large files and can simplify large sequential allocations, but may waste more space in partially filled final blocks.

Some filesystems reduce this waste using techniques such as **inline data**, **tail packing**, or shared blocks through mechanisms such as reflinks or deduplication.

For general-purpose systems, **4 KiB is a common choice** because it aligns well with several common granularities, including 4 KiB physical sectors, 4Kn logical sectors, and 4 KiB virtual-memory pages. These are still independent abstractions, however; their sizes do not need to be identical.

A filesystem block is primarily an **allocation and mapping unit**. It does not restrict applications to reading or writing exactly one block at a time. Applications can request arbitrary byte ranges, while the filesystem, page cache, and block layer translate those requests into the necessary underlying operations.

#### Extents

Instead of recording every filesystem block individually, modern filesystems often group adjacent blocks into **extents**.

An extent represents a contiguous range of file data stored in a contiguous range of filesystem blocks or logical blocks. For example, rather than storing mappings for 1,000 adjacent blocks separately, the filesystem can describe them as one extent containing a starting location and length.

A file may contain multiple extents when sufficient contiguous free space is unavailable or when the file grows over time. This is the mechanism behind [file fragmentation](https://chatgpt.com/g/g-p-6a7a84d6766881919bab2085541ba9fd/c/6a908492-3274-83e9-9907-211602a49160#File%20Fragmentation%20and%20Defragmentation): one logical file becomes distributed across several non-contiguous extents.

#### Inodes and Directory Entries

Different filesystems use different structures to record these mappings. In Unix-like filesystems, the central per-file structure is the **inode**.

An inode stores information about a filesystem object together with references to the blocks or extents containing its data. Directories provide the naming layer by storing entries that associate human-readable filenames with inode numbers.

This produces a resolution path such as `Filename → Inode → Extents / Filesystem Blocks → LBAs → File Data`.

When an application accesses a path, the filesystem traverses directory entries until it reaches the target inode. It then uses the inode's extent or block mappings to determine which regions of the LBA address space contain the requested portion of the file.

The filename and inode are separate filesystem objects. This separation is what allows multiple names to refer to the same underlying file.

> [!info] Hard vs. Soft Links Under the Hood
>
> Because filenames are separate from inodes, Unix-like filesystems can implement two different linking mechanisms.
>
> - **Hard Links (`ln`):** Multiple directory entries reference the **same inode**. There is no privileged "original" filename; each hard link is an equal name for the same filesystem object. Removing one name does not delete the underlying data while other hard links remain. The inode and its data can be reclaimed once its link count reaches zero and no process still holds the file open.
>
> - **Soft/Symbolic Links (`ln -s`):** A symbolic link is a separate filesystem object with its **own inode**. Rather than referring directly to the target inode, it stores a pathname that the filesystem resolves when the link is followed. If that pathname no longer resolves to an existing object, the symbolic link becomes **dangling**.

### Metadata

A filesystem must store information not only about file contents, but also about **how those contents and filesystem objects are organized, located, interpreted, and protected**. This information is called **metadata**.

The inode and directory entries described above are examples of filesystem metadata, but metadata exists at several levels.

Per-file metadata can include:

- file type and size,
- ownership and permissions,
- creation, modification, and access timestamps,
- references to filesystem blocks or extents.

Other filesystem metadata includes:

- directory entries and name mappings,
- free-space tracking structures,
- allocation indexes,
- filesystem-wide configuration,
- consistency and recovery information.

Metadata is essential because the underlying block device exposes only numbered logical blocks containing bytes. Those blocks do not intrinsically reveal which bytes belong to a particular file, what that file is called, how its pieces are arranged, who may access it, or which regions are available for reuse.

The filesystem's metadata gives meaning and structure to that otherwise flat LBA space.

Because metadata describes how file contents are located, corruption of metadata can make otherwise intact data difficult or impossible to recover. This is why filesystems devote significant machinery to maintaining metadata consistency, especially when writes are interrupted by crashes or power loss.

### Free Space Management

The filesystem must also know which logical blocks are already occupied and which are available for new data.

When creating or extending a file, the filesystem's allocator searches its free-space metadata for suitable regions and assigns them to the file. When data is deleted, those logical blocks become available for future allocations.

Filesystems use structures such as **bitmaps, free-space trees, or extent-based indexes** to maintain this information efficiently.

Allocation policy has an important effect on performance. When possible, the filesystem tries to place logically related data near each other so that files require fewer extents and storage accesses have better locality.

Over time, however, repeated creation, deletion, and expansion of files can leave available space scattered throughout the filesystem. New files may then need to be split across several extents, producing [file fragmentation](#File%20Fragmentation%20and%20Defragmentation).

### Caching

Filesystems also integrate closely with the operating system's **page cache**. Accessing RAM is far faster than accessing persistent storage, so recently or frequently accessed file data can be retained in memory.

When an application reads a file, the kernel can first check whether the requested data already exists in the page cache. If it does, the read can be satisfied from RAM without accessing the storage device.

Writes are also frequently buffered. Instead of immediately sending every small modification to storage, the kernel can modify cached pages and later flush those **dirty pages** to the device in larger and more efficient operations.

Caching therefore provides several benefits:

- repeated reads can avoid storage I/O,
- small writes can be combined,
- sequential access can be detected and prefetched,
- applications can benefit from shared cached data.

The trade-off is that data acknowledged in memory may not yet have reached persistent storage. Filesystems and applications therefore provide synchronization mechanisms when durability must be guaranteed.

### Filesystem I/O vs. Raw Block Access

Applications normally access storage through files, allowing the filesystem to manage naming, permissions, allocation, and the mapping between file offsets and logical blocks.

Some applications, particularly databases, use [Direct I/O (`O_DIRECT`)](03%20Memory%20Management.md#Direct%20I/O%20(`O_DIRECT`)) to bypass the operating system's **page cache** and manage caching themselves. However, Direct I/O does **not** bypass the filesystem. The application still opens a file, and the filesystem still resolves its metadata and translates file offsets into storage operations.

Bypassing the filesystem entirely is also possible by accessing a **raw block device**. In that case, the application operates directly on the device's logical block address space rather than storing its data inside ordinary filesystem files.

This gives the application complete control over the storage layout, but it also means taking responsibility for functionality normally provided by the filesystem, such as **space allocation, metadata organization, consistency, and recovery**. Raw block access is therefore much less common than using filesystem files, even among applications that bypass the page cache.

### Disk Formatting

**Formatting** prepares a storage region for use with a particular filesystem. During formatting, the filesystem creates its initial metadata structures, such as the root directory, free-space tracking structures, allocation metadata, and other filesystem-specific information.

Formatting usually operates on a **partition or logical volume**, rather than necessarily on an entire physical device.

A **quick format** may primarily recreate filesystem metadata and mark existing storage regions as free without immediately overwriting their previous contents. A more thorough format may additionally scan or overwrite storage. Therefore, formatting makes previous files inaccessible through the old filesystem structures, but it does not necessarily erase every underlying byte immediately.

### FAT32

**FAT32 (File Allocation Table 32)** is an older filesystem that remains common on removable storage because of its broad compatibility across operating systems, firmware, cameras, game consoles, and other devices.

FAT32 organizes file data using **clusters**, its filesystem allocation unit. A cluster groups one or more consecutive logical sectors from the underlying LBA address space.

For example: `Logical sector = 512 B` and `Cluster = 8 logical sectors`. therefore: `Cluster size = 4 KiB`.

The filesystem allocates storage to files in whole clusters rather than individual logical sectors.

To keep track of which clusters belong to each file, FAT32 maintains a large **File Allocation Table (FAT)**. Conceptually, the FAT is an array indexed by cluster number whose values identify the next cluster in the same file: `FAT[cluster] = next cluster`.

A directory entry stores metadata about a file, including its name, size, and **first cluster**. From that starting point, the filesystem follows entries in the FAT until it reaches an end-of-chain marker: `Directory entry → First cluster → FAT → Next cluster → ... → End of chain`.

For example: `FAT[120] = 121`, `FAT[121] = 450`, and `FAT[450] = EOF`.

A file beginning at cluster `120` therefore occupies clusters `120`, `121`, and `450`. Each cluster can then be translated into the corresponding range of LBAs when the filesystem performs storage I/O.

This linked structure makes FAT32 conceptually simple, but it also means that finding data deep inside a fragmented file may require following a chain of FAT entries unless the filesystem caches that information.

Each FAT32 entry occupies **32 bits**, but only the lower **28 bits** are available for identifying clusters. The remaining bits are reserved. Some values from the usable range are also reserved to represent states such as **free cluster**, **bad cluster**, and **end of chain**.

Using clusters is important because each FAT entry can represent considerably more storage than if it represented only one logical sector. With roughly 28 bits available for cluster identifiers, FAT32 can represent on the order of: `2^28 clusters`. If each cluster contained only one 512-byte logical sector, this would correspond to roughly: `2^28 × 512 B ≈ 128 GiB`.

With 32 KiB clusters instead: `2^28 × 32 KiB ≈ 8 TiB`.

The practical maximum FAT32 volume size is lower and depends on filesystem and operating-system restrictions, but the mechanism is important: **increasing the cluster size increases how much storage the same number of FAT entries can represent**.

The cost is **internal fragmentation**. In the conventional FAT32 allocation model, a cluster allocated to one file cannot simultaneously store unrelated file data. If a file does not completely fill its final cluster, the remaining capacity becomes **slack space**.

For example, with 32 KiB clusters: `1 KiB file → 1 × 32 KiB cluster`.

Most of that cluster remains unused.

Cluster size therefore creates a trade-off:

- **Smaller clusters** reduce slack space, particularly when storing many small files, but require more FAT entries to represent the same volume.
- **Larger clusters** allow the filesystem to represent larger volumes with fewer allocation entries, but increase internal fragmentation.

Clusters are FAT32's implementation of the more general **filesystem block/allocation-unit** concept: they determine the granularity at which storage is assigned to files.

> [!note] Why FAT32 Has a 4 GiB File-Size Limit
> 
> FAT32's maximum individual file size is **not caused by the FAT cluster chain itself**.
> 
> The FAT determines **which clusters are allocated to a file**, but it does not record the exact byte at which the file ends inside its final cluster. FAT32 therefore stores the file's total logical length separately in a **32-bit `FileSize` field** inside the directory entry.
> 
> This makes operations such as checking a file's size or determining its logical EOF very cheap, because the filesystem can read the value directly instead of traversing the entire FAT chain and counting clusters.
> 
> The trade-off is that a 32-bit byte counter can represent at most:
> 
> `2^32 - 1 bytes = 4 GiB - 1 byte`
> 
> This is the actual origin of FAT32's maximum file-size limit.
> 
> The limitation is therefore a **metadata format decision**, not an inherent property of linked-cluster allocation. A differently designed filesystem could store the number of bytes used in the final cluster and derive the total size from the chain length, or simply use a larger file-size field.
### Common File Systems

- **NTFS (New Technology File System):** The primary filesystem used by modern Windows installations. It supports large files and volumes, journaling, access-control lists (ACLs), compression, encryption, hard links, symbolic links, and other features expected from a general-purpose desktop and server filesystem.
- **APFS (Apple File System):** The default filesystem for modern macOS, iOS, and other Apple operating systems. It was designed primarily for flash storage and uses **copy-on-write (CoW)** metadata. APFS supports features such as snapshots, cloning, encryption, and space sharing between multiple volumes inside the same container.
- **HFS+ (Hierarchical File System Plus):** Apple's previous primary filesystem, used by macOS before APFS replaced it. HFS+ supports journaling, large files, permissions, and hierarchical directories, but is now mainly relevant for compatibility with older Apple systems and storage devices.
- **ext4 (Fourth Extended File System):** A widely used general-purpose Linux filesystem and the default choice in many Linux distributions. It uses journaling for crash recovery and **extents** to efficiently represent contiguous file regions. ext4 supports large files and volumes but does not natively provide features such as transparent compression, snapshots, or checksumming of file data.
- **XFS:** A high-performance journaling filesystem commonly used on Linux servers, particularly for workloads involving very large files, large filesystems, and high levels of parallel I/O. It uses extent-based allocation and B-tree structures extensively to scale filesystem metadata operations.
- **Btrfs (B-Tree File System):** A modern Linux filesystem built around **copy-on-write (CoW)**. It supports snapshots, subvolumes, checksumming of data and metadata, compression, and integrated management of multiple storage devices. Checksums allow Btrfs to detect silent corruption, and when another valid copy of the data is available through redundancy, it may use that copy to repair the damaged data.
- **FAT32:** An older and relatively simple filesystem whose broad support makes it useful for removable media and compatibility between devices. Its major limitations include a maximum individual file size of approximately **4 GiB** and fewer features for permissions, reliability, and large-volume management than modern filesystems.
- **exFAT (Extended File Allocation Table):** A filesystem designed primarily for removable flash storage. It retains much of FAT's simplicity and broad cross-platform compatibility while supporting much larger files and volumes than FAT32, making it common on SD cards, USB drives, and external storage exchanged between different operating systems.
- **tmpfs (Temporary File System):** A memory-backed filesystem commonly found on Unix-like systems. File contents reside primarily in virtual memory and may be moved to **swap** under memory pressure, rather than being persistently stored on an HDD or SSD. This makes tmpfs useful for temporary data that benefits from normal filesystem semantics without requiring persistent storage. Its contents disappear when the filesystem is unmounted or the system shuts down or reboots.

====

## Network Storage and Redundancy

While local file systems manage how data is organized on an individual operating system, enterprise environments require advanced methods for combining multiple physical drives for reliability and sharing storage across networks.

### RAID (Redundant Array of Independent Disks)

RAID (`/reɪd/`) is a technology used to combine multiple physical hard drives into a single logical unit. The primary goals of RAID are to provide **fault tolerance** (protecting against drive failures) and/or to increase **performance** (speeding up read/write operations).

- **Striping (Performance):** Splitting data across multiple drives. This allows the OS to read or write to multiple disks simultaneously, drastically increasing speed. However, it offers zero data protection.
- **Mirroring (Redundancy):** Duplicating the exact same data onto two or more drives. If one drive dies, the system keeps running smoothly using the mirror.
- **Parity (Balance):** A mathematical calculation used to reconstruct lost data if a drive fails. It provides redundancy without requiring the 100% capacity overhead of mirroring.

#### Common RAID Levels

|**RAID Level**|**Description**|**Key Advantage**|**Minimum Drives**|**Fault Tolerance**|
|---|---|---|---|---|
|**RAID 0**|**Striping only.** Data is sliced and spread across drives.|Maximum performance and storage capacity.|2|**None.** If one drive fails, *all* data is lost.|
|**RAID 1**|**Mirroring only.** Data is written identically to two drives.|High fault tolerance; simple data recovery.|2|Can survive 1 drive failure.|
|**RAID 5**|**Striping with distributed parity.** Data and parity blocks are spread across all disks.|Great balance of performance, capacity, and fault tolerance.|3|Can survive 1 drive failure.|
|**RAID 6**|**Striping with dual distributed parity.** Similar to RAID 5 but writes two blocks of parity.|Extremely robust; ideal for large, modern hard drives.|4|Can survive **2 concurrent** drive failures.|
|**RAID 10**|**A hybrid (1+0).** Mirrors data first, then stripes those mirrored sets.|Combines the speed of RAID 0 with the security of RAID 1.|4|Can survive multiple failures (as long as they aren't in the same mirror set).|

### Networked Storage Architectures: NAS vs. SAN

When storage needs to be accessed by multiple servers or users over a network, organizations rely on two primary architectures: **Network-Attached Storage (NAS)** and **Storage Area Network (SAN)**.

#### Network-Attached Storage (NAS)

NAS (`/næz/` or `/næs/`) is a dedicated, file-sharing storage device connected to a standard local area network (LAN). Think of it as a specialized, high-powered shared folder sitting on your network.

- **File-Level Storage:** The NAS manages its own file system (like EXT4 or Btrfs). It exposes files and folders to clients using network protocols.
- **Common Protocols:**
    - **SMB/CIFS:** Primarily used by Windows environments.
    - **NFS:** Primarily used by Linux/Unix environments.
- **Use Cases:** General file sharing, user home directories, central backups, and media streaming.
- **Pros/Cons:** Easy to set up and less expensive, but performance is limited by standard network traffic and latency.

#### Storage Area Network (SAN)

A SAN `/sæn/` is a highly specialized, high-speed, dedicated subnetwork that connects servers to a consolidated pool of block-level storage.

- **Block-Level Storage:** Unlike NAS, a SAN does not manage a file system. It exposes raw storage blocks (LUNs) directly to servers. To a connected server, a SAN volume looks and acts like a local internal hard drive (an array of raw [LBA](#Logical%20Block%20Addressing%20(LBA)) blocks). The server's own OS is responsible for formatting it with a file system (like NTFS or EXT4).
- **Common Protocols:**
    - **Fibre Channel (FC):** Uses dedicated fiber-optic cables and switches for ultra-low latency and massive throughput.
    - **iSCSI:** Runs block-level SCSI commands over standard Ethernet cables, making it a cheaper alternative to Fibre Channel.
- **Use Cases:** Massive databases (like Oracle or SQL), virtualization clusters (VMware/Hyper-V) requiring fast VM migration, and high-performance transactional applications.
- **Pros/Cons:** Incredibly fast, highly scalable, and ultra-low latency; however, it is highly complex to manage and very expensive to implement.

## I/O Pressure Stall Information (PSI)

When managing sockets, network-attached storage, or databases, threads often have to wait for hardware to return data. I/O PSI (`/proc/pressure/io`) measures exactly how much time your threads spend physically blocked by block storage or network I/O devices.

- **Reading I/O PSI:** `cat /proc/pressure/io`
- **`some` (The Asynchronous Ideal):** At least one thread is blocked waiting for an I/O device (like a socket read or a database disk fetch). However, because you have enough concurrent threads, the OS scheduler seamlessly switches the CPU to do other work. High `some` is normal in heavily concurrent network apps.
- **`full` (The I/O Bottleneck):** Every single active thread in your application is blocked waiting for I/O (e.g., the network queue is totally saturated, or the disk ran out of IOPS). The CPU is sitting completely idle. Adding more CPU cores or RAM will not help; you must either upgrade your networking/storage hardware or add a caching layer (like Redis) to bypass the I/O bottleneck.
