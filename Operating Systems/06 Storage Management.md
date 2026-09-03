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
> **LBA logical blocks** and **[[03 Memory Management#Virtual Memory|virtual memory]]** are independent abstractions, but having compatible sizes is convenient for operations such as **swapping**.
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

This indirection is fundamental to SSD operation. It allows the controller to perform [[#Out-of-Place Writes|out-of-place writes]], relocate data during [[#Garbage Collection|garbage collection]], and distribute writes through [[#Wear Leveling|wear leveling]] without changing the LBA addresses exposed to the host.

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

The [[#File Fragmentation and Defragmentation|file fragmentation]] described for HDDs also exists at the filesystem level on SSDs: a file can still be split across multiple non-contiguous extents. What changes is the performance consequence.

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
### Partitions

A **partition** divides a block device's [Logical Block Addressing (LBA)](#Logical%20Block%20Addressing%20(LBA)) space into logical regions. Instead of exposing the entire disk as one storage region, the operating system can treat each partition as an independent block device.

Partition boundaries are defined in terms of the storage device's logical blocks. Conceptually, a partition occupies a contiguous range of LBAs with a beginning and a length or ending LBA.

For example, a disk may contain a partition whose storage region begins at LBA `2048` and ends at LBA `1,000,447`. Reads and writes to that partition are ultimately translated into accesses within that range of the underlying disk.

The exact representation depends on the **partition-table format**. GPT, for example, records the first and last LBA belonging to each partition, while older MBR partition entries describe a starting LBA and a number of sectors.

Partitioning therefore provides **logical segmentation**, not another physical storage technology. The blocks still belong to the same underlying HDD, SSD, or other block device; the partition table simply describes which ranges are assigned to which logical regions.

A partition can then be used in different ways. A common use is to create a filesystem on it, but a partition can instead contain swap space, participate in a volume-management system, or be accessed as a raw block device.

When a filesystem is created on a partition, that filesystem manages only the block-address range exposed by that partition. Different partitions can therefore contain completely different filesystems.

For example, one disk could contain an ext4 partition and an NTFS partition. Each filesystem independently creates its own metadata structures and chooses its own supported [filesystem block](#Filesystem%20Blocks) size.

The filesystem block size is distinct from both the partition size and the underlying LBA logical-sector size. For example, a device might expose 512-byte logical sectors while one partition contains an ext4 filesystem using 4 KiB filesystem blocks. Another partition on the same device could use a filesystem with a different allocation-unit size.

Partition boundaries are normally aligned to suitable storage boundaries. Modern partitioning tools commonly choose boundaries such as multiples of 1 MiB, which align cleanly with common logical-sector, physical-sector, filesystem-block, and SSD erase-related granularities. Poor alignment can cause one higher-level write to span multiple lower-level storage units and introduce unnecessary work.

The important hierarchy is therefore:

- the **storage device** exposes an LBA address space;
- the **partition table** assigns ranges of that LBA space to partitions;
- each partition is exposed as its own logical block device;
- a **filesystem** may be created inside that partition and introduce its own filesystem-block and metadata structures.

These layers have related boundaries, but their granularities are independent.
#### Partition Alignment

A partition can begin at any logical-sector boundary allowed by the partition table, but not every starting LBA is equally efficient. **Partition alignment** means choosing the partition's starting LBA so that higher-level structures such as filesystem blocks align cleanly with the storage device's underlying physical boundaries.

This matters when the device exposes a smaller **logical sector size** than its actual **physical sector size**. A common example is a **512e** drive, which exposes 512-byte logical sectors while internally reading and writing 4 KiB physical sectors.

Because:

`4 KiB / 512 B = 8`

each 4 KiB physical sector corresponds to eight logical sectors. A partition whose starting LBA is divisible by `8` begins on a 4 KiB physical-sector boundary.

If the filesystem inside that partition also uses 4 KiB blocks, a properly aligned filesystem block can fit completely inside one physical sector. A write to that block can therefore be handled as one physical-sector update.

With an **improperly aligned partition**, the filesystem may still create perfectly regular 4 KiB blocks relative to the beginning of the partition, but those blocks are shifted relative to the device's physical-sector boundaries. A single 4 KiB filesystem block may consequently overlap two different 4 KiB physical sectors.

Updating that one filesystem block can then require the storage device to preserve portions of both physical sectors. On devices that cannot update those portions independently, this can introduce additional **read-modify-write** work: the device reads the affected physical sectors, modifies the relevant portions, and writes them back.

Partition alignment is therefore about aligning **boundaries between abstraction layers**. The filesystem reasons about offsets relative to the beginning of its partition, while the storage device reasons about physical sectors relative to the beginning of the disk. If the partition itself begins at an unsuitable offset, every filesystem structure created inside it can inherit that displacement.

Modern partitioning tools commonly align partitions on **1 MiB boundaries**. With 512-byte logical sectors:

`1 MiB / 512 B = 2048 logical sectors`

so LBA `2048` is a common starting point for the first partition. A 1 MiB boundary is divisible by many common sector and allocation sizes, making it a practical alignment choice across devices with different internal granularities.

Alignment can matter beyond physical sectors as well. Storage stacks may contain other granularities such as RAID stripe sizes or SSD internal allocation units. There is no single partition boundary that exposes and perfectly matches every internal implementation detail, but using sufficiently large, regularly aligned boundaries such as 1 MiB avoids the most common misalignment problems.

Partition alignment does **not** require the filesystem block size to equal the physical-sector size. Different layers may use different granularities. The important requirement is that their boundaries interact cleanly enough that a higher-level operation does not unnecessarily span additional lower-level units.
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
- **File Permissions:** Metadata controlling which users or processes may perform operations such as reading, writing, or executing a file. The exact permission model depends on the filesystem and operating system. Unix-like systems, for example, commonly distinguish permissions for an owner, a group, and other users. [[../Security/05 Architecture and Infrastructure Security/02 Endpoint Security|security permissions]] build on this metadata to enforce access control.

### Opening Files and File Descriptors

Ordinary file-content I/O on Unix-like systems generally begins by **opening** a file. A call such as `open()` resolves a pathname, checks the requested access against filesystem permissions, creates or reuses the kernel state needed for the open file, and returns a small integer called a **file descriptor** to the process.

Subsequent operations such as `read()`, `write()`, and `fsync()` use the file descriptor rather than resolving the pathname again for every operation. The open file also carries state such as the current file offset and status flags that affect later I/O. When the process no longer needs that reference, it releases it with `close()`.

This is different from the `mode` argument sometimes passed to `open()`. When a new file is created, that argument describes its initial permission bits. Behaviors such as append-only positioning, synchronous writes, or Direct I/O are selected using **open flags**.

#### Open Flags

An `open()` call includes an access mode such as `O_RDONLY`, `O_WRONLY`, or `O_RDWR`, describing whether the descriptor can read, write, or do both. Additional flags modify the behavior of operations performed through that open file.

Common examples include:

- **`O_APPEND`:** before each `write()`, the kernel positions the open file offset at the current end of the file and performs the offset adjustment and write as one operation. This allows multiple writes to append without each caller separately seeking to the current end first.
- **`O_DIRECT`:** requests [[#Direct I/O (`O_DIRECT`)|Direct I/O]]), so transferred file data generally bypasses the normal page-cache path.
- **`O_SYNC`:** gives writes synchronized file-integrity completion semantics: a successful `write()` does not return until the written data and the metadata required by the stronger synchronization guarantee have been committed as required by the storage stack.
- **`O_DSYNC`:** provides the narrower data-integrity form of synchronous writing. It waits for the written data and metadata necessary to retrieve that data, without requiring unrelated metadata updates to become durable as part of every write.

These flags control different properties and can be conceptually independent. For example, `O_DIRECT` controls whether transferred file data normally participates in the page cache, while `O_SYNC` and `O_DSYNC` control what durability work must complete before a write returns.

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

A file may contain multiple extents when sufficient contiguous free space is unavailable or when the file grows over time. This is the mechanism behind [[#File Fragmentation and Defragmentation|file fragmentation]]: one logical file becomes distributed across several non-contiguous extents.

#### Inodes and Directory Entries

Different filesystems use different structures to record these mappings. In Unix-like filesystems, the central per-file structure is the **inode**.

An inode stores information about a filesystem object together with references to the blocks or extents containing its data. Directories provide the naming layer by storing entries that associate human-readable filenames with inode numbers.

This produces a resolution path such as `Filename → Inode → Extents / Filesystem Blocks → LBAs → File Data`.

When an application accesses a path, the filesystem traverses directory entries until it reaches the target inode. It then uses the inode's extent or block mappings to determine which regions of the LBA address space contain the requested portion of the file.

The filename and inode are separate filesystem objects. This separation is what allows multiple names to refer to the same underlying file.

##### Storing and Locating Inodes

An **inode number** identifies a filesystem object, but the number is not itself a memory address or storage location. The filesystem must maintain metadata that maps that identifier to the persistent **inode record** containing the object's metadata and references to its data blocks or extents.

How this collection of inode records is organized depends on the filesystem. There is therefore no universal operating-system-wide "inode table" shared by every filesystem. Some Unix-like filesystems use fixed-size inode records stored in dedicated filesystem metadata regions, while other filesystems use different indexing structures.

**ext4** provides a useful concrete example. Instead of keeping all filesystem metadata in one enormous region, ext4 divides the filesystem into **block groups**. Each block group contains metadata for managing resources associated with that part of the filesystem, including:

- an **inode bitmap**, which records which inode numbers in the group are allocated or free;
- an **inode table**, which stores the fixed-size inode records belonging to that group;
- block-allocation metadata and the data blocks themselves.

The filesystem's metadata records where each block group's inode table is located. Because ext4 also knows how many inodes belong to each group, it can determine where an inode should be found directly from its inode number.

For an inode number `i`, with `N` inodes per block group, ext4 can conceptually calculate: `block group = (i - 1) / N`.

and: `index within inode table = (i - 1) % N`.

The subtraction is necessary because inode numbers begin at `1`, while array-like indexes begin at `0`.

For example, suppose each block group contains `8,192` inodes and the filesystem needs inode `20,000`. `block group = (20,000 - 1) / 8,192 = 2` and `index = (20,000 - 1) % 8,192 = 3,615`.

The inode therefore belongs to block group `2` and occupies entry `3,615` in that group's inode table. Once the filesystem knows the beginning of that inode table and the size of each inode record, it can calculate the record's byte offset within the table.

This lookup is fundamentally different from following a filename. A directory entry first maps a **filename** to an **inode number**. The filesystem then uses its internal inode-storage structures to locate the corresponding inode record. That inode contains the metadata and mappings needed to locate the file's [[#Extents|extents]] or blocks.

The **inode bitmap** serves a different purpose from the inode table. The inode table stores the inode records themselves, while the bitmap tracks which inode slots are currently allocated. When creating a new filesystem object, ext4 can search the bitmap for an available inode slot, mark it as allocated, and initialize the corresponding record in the inode table.

This separation also explains why deleting a filename does not necessarily immediately free an inode. Directory entries provide names for an inode, while the inode separately tracks information such as its link count. Only when the filesystem determines that the inode is no longer referenced and no open use prevents reclamation can its inode slot and associated data blocks be returned to the filesystem's free-space structures.

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

Over time, however, repeated creation, deletion, and expansion of files can leave available space scattered throughout the filesystem. New files may then need to be split across several extents, producing [[#File Fragmentation and Defragmentation|file fragmentation]].

### Caching

Filesystems integrate closely with the operating system's **page cache**, which uses available RAM to retain file contents. Normal buffered reads and writes generally pass through this cache rather than interacting synchronously with the storage device for every operation.

When an application reads part of a file, the kernel first looks for the corresponding file region in the page cache. On a **cache hit**, the data can be returned directly from RAM. On a **cache miss**, the filesystem reads the data from storage and normally keeps it in the page cache so later accesses can reuse it.

The page cache is system-wide rather than private to one application. If two processes read the same region of the same file, the second process can generally reuse the pages already cached by the first instead of causing another storage read.

Sequential access can also trigger **read-ahead**. If the kernel observes that an application is reading consecutive regions of a file, it may load upcoming data into the page cache before it is explicitly requested, hiding part of the storage latency.

Caching therefore allows the operating system to exploit both **temporal locality**—reusing recently accessed data—and **spatial locality**—predicting that nearby file data will soon be accessed.

#### Writes, Writeback, and Durability

Buffered writes also pass through the page cache.

When an application writes to a file, the kernel locates or creates the corresponding page-cache entry, modifies the data in RAM, and marks that cached page as **dirty**. A successful `write()` therefore does not normally mean that the corresponding bytes have already reached persistent storage.

Conceptually: `Application → Dirty Page Cache → Storage`.

The dirty pages are later persisted by the kernel through **writeback**. Writeback can happen because pages have remained dirty for some time, because the amount of dirty memory has grown sufficiently large, because memory needs to be reclaimed, or because an application explicitly requests synchronization.

This delayed-write design decouples the application's write pattern from the storage device's write pattern. An application may perform several small writes because that is convenient for its logic, while the kernel can accumulate those changes in memory and later issue larger or fewer storage operations.

For example, instead of immediately performing: `write 100 B → device`, `write 200 B → device`, and `write 300 B → device`.

multiple modifications may first accumulate in cached pages and later participate in a larger writeback operation.

This should not be understood simply as the operating system assuming that application developers will write inefficient code. The abstraction deliberately allows applications to express writes according to their own semantics while the kernel handles device-level batching, scheduling, and locality. Even well-designed applications often have legitimate reasons to issue many small logical updates.

However, delayed writeback creates a distinction between **written** and **durable** data. If the operating system crashes or loses power while a page is still dirty, the version present only in RAM is lost.

Applications that need a durability boundary can call **`fsync()`**. For a regular file, `fsync()` forces the file's dirty data and required metadata toward persistent storage and blocks until the storage stack reports completion.

The storage device may itself contain another cache. HDDs and SSDs commonly have controller-managed **write-back caches** that allow the device to acknowledge a write before the data has reached its final non-volatile location.

The complete write path can therefore look approximately like: `Application → Page Cache → Device Write Cache → Non-volatile Storage`.

A proper `fsync()` must account for this additional layer. The filesystem and block layer issue the necessary synchronization operations so that relevant data does not remain only in a volatile device cache when `fsync()` successfully returns.

This means that `fsync()` is considerably more expensive than an ordinary buffered `write()`: it deliberately breaks the normal asynchronous batching behavior and introduces a durability barrier that the application may need to wait for.

##### Synchronous Writes: `O_SYNC` and `O_DSYNC`

Instead of performing ordinary buffered writes and explicitly calling `fsync()` at selected durability boundaries, an application can request synchronized write semantics when it opens the file.

With **`O_SYNC`**, each `write()` waits for **synchronized file-integrity completion** before returning. Conceptually, it provides durability semantics similar to performing the write and then synchronizing the file with `fsync()`: the written data and the associated metadata required by the full synchronization guarantee must be committed before the operation is considered complete.

**`O_DSYNC`** provides the narrower **data-integrity** form. The write waits for the data itself and metadata necessary to retrieve that data, such as a file-size change when the write extends the file, but does not need to force unrelated metadata such as a modification timestamp as part of every operation. Its role is therefore comparable to performing a write followed by `fdatasync()` rather than the stronger `fsync()`.

These flags do not mean that the page cache is bypassed or that the entire system cache is flushed after every write. They change the completion guarantee of writes made through that open file. This is fundamentally different from [[#Direct I/O (`O_DIRECT`)|`O_DIRECT`]]), which controls page-cache participation rather than durability.

Synchronous writes can be expensive because each write may introduce a durability wait that prevents the application and operating system from freely batching many updates behind one later synchronization point. They are useful when each write, or each deliberately constructed write operation, must itself establish the required persistence guarantee.

Append-oriented durability structures such as [[../Databases/00 Overview#Write-Ahead Logging (WAL)|Write-Ahead Logging (WAL)]]) are an important example of where these primitives can be useful. A database must ensure that required log records become durable before it treats dependent state as safely committed, but it can implement that boundary in different ways: it may use synchronized open flags such as `O_SYNC` or `O_DSYNC`, or perform ordinary writes followed by explicit `fsync()` or `fdatasync()` calls so that several writes can be grouped before synchronization.

> [!example] Firefox 3 and Excessive `fsync()`
>
> During the development of **Firefox 3 in 2008**, Mozilla received [Bug 421482](https://bugzilla.mozilla.org/show_bug.cgi?id=421482), titled *Firefox 3 uses fsync excessively*. A reporter tracing Firefox's system calls observed roughly **eight `fsync()` calls while loading a new page** and reported severe responsiveness problems when the system was already performing other intensive disk I/O.
>
> The problem involved Firefox's SQLite-backed storage. Firefox was performing many small database transactions, and committing those transactions caused SQLite to request durability barriers repeatedly. At the time, SQLite's `synchronous=FULL` behavior could perform multiple synchronization operations during a transaction.
>
> This defeated one of the major advantages of buffered writing. Instead of allowing many changes to accumulate and eventually be persisted together, repeated synchronization points forced the storage stack to establish durability again and again. Because `fsync()` waits for the required storage operations to complete, these barriers could become visible directly as application latency.
>
> Mozilla investigated reducing the synchronization frequency and approved a change that made its storage connections default to SQLite's `synchronous=NORMAL` mode. In one test discussed in the bug, `NORMAL` reduced the number of synchronization calls by roughly one third compared with `FULL`.
>
> The lesson is not that `fsync()` should be avoided. Durability-sensitive software such as databases needs explicit synchronization at carefully chosen points. The problem is **unnecessarily frequent durability barriers**: an application that calls `fsync()` after every tiny modification can destroy write batching and turn storage latency into application latency.

Buffered writes can also expose crash-atomicity limits below the page cache. The storage stack does not generally promise that an arbitrarily large application-level structure will reach persistent storage as one indivisible operation. If one logical update spans several lower-level writes, a crash or power loss can leave only part of that update durable.

This problem is independent of whether the data passed through the page cache: bypassing buffered I/O does not automatically make a larger logical update atomic. Higher-level software that requires crash consistency must therefore design its own recovery protocol around the atomicity and ordering guarantees provided by the storage stack.

#### Direct I/O (`O_DIRECT`)

For most applications, buffered I/O provides a useful default. Some applications, however, maintain their own long-lived cache of file data and have workload-specific information that the kernel's generic page-cache policy does not have.

With buffered I/O, the same underlying file data can then exist in both the page cache and an application-managed cache. The two layers consume memory independently and may make different decisions about what to retain, evict, prefetch, or write back.

On systems such as Linux, an application can request **Direct I/O** using `O_DIRECT`. File data then generally bypasses the normal page-cache path and is transferred between the storage stack and application-provided memory buffers.

Conceptually: `Buffered I/O: Application ↔ Page Cache ↔ Filesystem / Block Layer ↔ Device` and `Direct I/O: Application Buffer ↔ Filesystem / Block Layer ↔ Device`.

Direct I/O does **not** bypass the filesystem or the kernel. The filesystem still resolves the file, manages its metadata and allocation, translates file offsets into underlying storage locations, and submits operations through the block-device stack. What is primarily avoided is caching the transferred file contents in the normal page cache.

Bypassing the page cache also means giving up some services that buffered I/O normally provides. The application may lose automatic caching and read-ahead, and Direct I/O can impose alignment requirements on memory buffers, file offsets, and I/O sizes. The exact restrictions depend on the operating system, filesystem, kernel version, and storage device.

`O_DIRECT` also does **not by itself provide the durability guarantee of `fsync()` or `O_SYNC`**. Avoiding the page cache and forcing data to stable storage are separate decisions; the storage device may still contain volatile caches and the filesystem may still need to synchronize metadata.

`O_DIRECT` is therefore not inherently faster. It is useful when an application has enough knowledge of its workload to take responsibility for caching and I/O policy more effectively than the generic page cache. For ordinary applications, bypassing the page cache can instead increase storage accesses and reduce performance.

> [!example] When Direct I/O Makes Sense
>
> Consider an application that keeps a large cache of fixed-size records in its own memory. It already decides which records should remain resident, which should be evicted, and which regions should be prefetched based on application-specific access patterns.
>
> With buffered I/O, the underlying file data may also remain in the operating system's page cache. The application and kernel would then maintain two independent caches for the same data and compete for the same physical RAM.
>
> Direct I/O allows the application to avoid the normal page-cache copy and make its own cache the primary long-lived copy. This can be useful when the application has deliberately taken responsibility for the caching work that the kernel would otherwise perform.
>
> The important point is not that Direct I/O is a faster mode by itself. It is useful when **moving cache ownership from the kernel to the application** is a good architectural trade-off.
> [!example] Kafka Takes the Opposite Approach
>
> High-performance software does not always benefit from owning its own file cache. **Apache Kafka** generally takes the opposite approach and relies heavily on the operating system's page cache for its log-segment files.
>
> Kafka's workload is well suited to this design. Log data is written and read largely as files, access commonly has strong sequential locality, and recently used regions can remain cached in system memory without Kafka maintaining an equivalent large cache inside the JVM heap.
>
> Keeping that cache outside the Kafka process also means a process restart does not necessarily discard the cached file pages; the operating system can retain them independently of the JVM's lifetime.
>
> Kafka can then combine this page-cache-oriented design with zero-copy file-to-network techniques when serving data. The result illustrates the opposite side of the Direct I/O decision: sometimes the generic page cache already provides the behavior an application needs, so bypassing it would remove useful functionality rather than improve the design.
> [!note] Direct I/O vs. Raw Block Access
>
> **Direct I/O** bypasses the normal page-cache path but still operates through the filesystem. The filesystem continues to manage filenames, permissions, allocation, metadata, and the mapping from file offsets to logical blocks.
>
> **Raw block access** bypasses the filesystem itself. An application opens the block device directly and operates on its LBA address space, taking responsibility for storage layout and other functionality that a filesystem would normally provide.
>
> Therefore: `Direct I/O = filesystem without normal page-cache caching` and `Raw block access = block device without filesystem abstraction`.
>
### Disk Formatting

**Formatting** prepares a block device for use with a particular filesystem by creating that filesystem's initial on-disk data structures.

The target is commonly a [partition](#Partitions) or logical volume rather than an entire physical disk. From the filesystem's perspective, that target is simply the block-device address space it is allowed to manage.

During formatting, the filesystem initializes structures such as:

- filesystem-wide metadata and configuration;
- free-space tracking structures;
- inode or equivalent file-metadata structures;
- the root directory;
- allocation metadata and other filesystem-specific indexes.

Formatting also establishes filesystem-level parameters such as the supported **filesystem block size**. This choice is independent from the partition size and from the logical-sector size exposed by the underlying storage device, although compatible alignment between these layers is important for efficient I/O.

For example, a disk may expose 512-byte logical sectors, while one partition on that disk is formatted as ext4 using 4 KiB filesystem blocks. Another partition on the same disk could be formatted with a different filesystem and use a different allocation-unit size.

Formatting therefore does not create the partition itself. **Partitioning defines which range of the underlying block device belongs to a logical region; formatting defines how a filesystem organizes the blocks inside that region.**

A **quick format** generally recreates the filesystem's metadata structures and marks data regions as available without overwriting every previously stored byte. The previous filesystem's files become inaccessible through the newly created metadata, but remnants of their data may remain on storage until those blocks are reused.

A more thorough formatting or sanitization operation may additionally overwrite, discard, or otherwise process the underlying storage. This is separate from the basic act of creating a filesystem.
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
> The trade-off is that a 32-bit byte counter can represent at most: `2^32 - 1 bytes = 4 GiB - 1 byte`.
> This is the actual origin of FAT32's maximum file-size limit.
>
> The limitation is therefore a **metadata format decision**, not an inherent property of linked-cluster allocation. A differently designed filesystem could store the number of bytes used in the final cluster and derive the total size from the chain length, or simply use a larger file-size field.
>
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

> [!example] Allegro — Migrating Kafka from ext4 to XFS
>
> In 2024, Allegro investigated large **tail-latency spikes** in its main Kafka cluster. Although median produce latency was only a few milliseconds, p99 latency could reach roughly **1 second** and p999 roughly **3 seconds**.
>
> Using eBPF tracing, the engineers traced many of the slow requests back to filesystem writes on **ext4**. In particular, periodic ext4 journal commits could occasionally make individual writes much slower. Because Kafka serializes some work around its log files, even an isolated slow filesystem operation could create contention and cause a cascade of slow produce requests.
>
> Allegro first experimented with ext4 itself. Changing the journaling mode to `data=writeback` reduced produce p999 latency from about **3 seconds to 800 milliseconds**, while enabling ext4 fast commits reduced it to about **500 milliseconds**.
>
> They then migrated one Kafka broker from **ext4 to XFS**. XFS was especially notable not merely for lower latency, but for much more **consistent tail latency**: brokers using the ext4 configurations continued to experience periodic p999 spikes, while the XFS broker running with its default configuration had only a few such spikes.
>
> After testing the configuration for several weeks, Allegro migrated the entire Kafka cluster to XFS. The final result was an **82% reduction in produce requests exceeding their 65 ms SLO**.
>
> This illustrates that the filesystem is not merely a neutral container for application files. Different filesystems use different allocation, locking, writeback, and journaling mechanisms, and those implementation choices can interact strongly with a workload. Kafka's append-heavy log storage benefited substantially from XFS's behavior in Allegro's particular environment; this does not imply that XFS universally outperforms ext4 for every workload.

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

- **Block-Level Storage:** Unlike NAS, a SAN does not manage a file system. It exposes raw storage blocks (LUNs) directly to servers. To a connected server, a SAN volume looks and acts like a local internal hard drive (an array of raw [[#Logical Block Addressing (LBA)|LBA]]) blocks). The server's own OS is responsible for formatting it with a file system (like NTFS or EXT4).
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
