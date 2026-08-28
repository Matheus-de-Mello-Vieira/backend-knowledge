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

Under LBA, the disk is presented as a linear sequence of fixed-size logical blocks:

`LBA 0, LBA 1, LBA 2, ...`

Software therefore requests a block by its number rather than specifying a cylinder, head, and sector.

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

====

## File Systems

A file system is the method and data structure used by an operating system (OS) to store, organize, and access files on a storage device.

- **The LBA Foundation:** The Operating System interacts with modern storage drives through Logical Block Addressing (LBA), viewing the device simply as a massive, flat array of numbered blocks.
- **The File Abstraction:** Human beings (and most application software) do not want to keep track of raw block numbers (e.g., remembering that a specific document is stored starting at block 4,092,110). The **File System** bridges this gap by abstracting that flat array of blocks into named, structured data units called **files**.
- **Directories and Hierarchy:** Beyond just files, the file system introduces folders (directories), allowing users to organize data into a logical, easily navigable tree structure.
- **Metadata (Data About Data):** To manage these files, the file system doesn't just store the file's contents; it must also store metadata.
    - This includes the file's name, size, creation/modification timestamps, and [security permissions](../Security/05%20Architecture%20and%20Infrastructure%20Security/02%20Endpoint%20Security.md).
    - **Block Mapping:** Critically, the metadata includes an index (such as an **inode** in Linux) that acts as a map, pointing the OS to the exact, non-sequential LBA block numbers where the file's actual fragmented data is physically stored on the drive.
- **Free Space Management:** The file system is continually responsible for maintaining a ledger of which blocks are currently in use by files and which blocks are free. When you save a new file or expand an existing one, the file system consults this ledger to allocate empty blocks, ensuring data is never accidentally overwritten.

### Basic Concepts

- **Directory (Folder):** The fundamental organizational unit within a file system, which can contain files as well as other directories (subdirectories).
- **File:** A distinct set of information stored on a device. Files possess names and extensions that indicate both their type and their content.
- **File Extension:** The specific set of characters that appears after the filename, serving to indicate the file's type or format.
- **Path:** The exact location or address of a file or directory within the file system.
    - *Absolute Path:* Traces the location starting from the very root of the file system.
    - *Relative Path:* Traces the location starting from the current working directory.
- **File Permissions:** Security controls that define exactly who is allowed to access, read, write, or execute a specific file. These permissions can be individually configured for the file's owner, a specific group of users, and all other users.
- **Disk Formatting:** The initial process of preparing a physical storage device to be used as a file system. This creates the foundational structure needed to store files and directories, and the process can erase all previously existing data on the device.
- **File Fragmentation:** A condition that occurs when a single file is broken into smaller pieces and stored in scattered, non-contiguous parts of the disk. This typically happens when there is not enough continuous free space available to store the file in one place. Fragmentation negatively affects file system performance, resulting in slower read and write operations.

### Common File Systems

- **NTFS (New Technology File System):** The default file system used for Windows operating systems. It allows for the creation of folders and subfolders, as well as the robust management of file and directory permissions.
- **HFS (Hierarchical File System):** The standard file system traditionally used for MacOS. It allows for the organization of files into folders and subfolders, in addition to providing built-in support for large files and data compression.
- **EXT4 (Fourth Extended File System):** The default file system for Linux operating systems. It enables the management of large files and supports both fragmentation and data compression.
- **FAT32 (File Allocation Table 32-bit):** An older, legacy file system that has been widely used for external storage devices and USB flash drives. While it offers high compatibility across many different operating systems, it has strict limitations and does not support large individual files or folders containing a massive number of files.
- **exFAT (Extended File Allocation Table):** A modernized file system designed specifically to bridge the gap between platforms. It allows for seamless compatibility with external storage devices and USB flash drives across different operating systems, while fully supporting the storage of large files that FAT32 cannot handle.
- **Btrfs (B-Tree File System):** A modern, advanced file system designed for Linux that focuses on fault tolerance, simplified administration, and data integrity. It utilizes a copy-on-write (CoW) mechanism and natively supports powerful features like instant system snapshots, pooling multiple drives into a single volume, and continuous data checksumming to automatically detect and repair silent data corruption.
- **tmpfs (Temporary File System):** A specialized file system that resides entirely in volatile system memory (RAM) and swap space, rather than on persistent physical storage like HDDs or SSDs. Because it completely bypasses the latency of storage drives, it offers exceptionally fast read and write speeds for temporary data, but all files stored within it are permanently lost the moment the system reboots or loses power.

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
