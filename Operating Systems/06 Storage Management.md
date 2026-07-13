# Storage Management
## File Systems

A file system is the method and data structure used by an operating system (OS) to store, organize, and access files on a storage device.

For the security perspective on file systems, see [Endpoint Security](../Security/05%20Architecture%20and%20Infrastructure%20Security/02%20Endpoint%20Security.md).

- **The LBA Foundation:** The Operating System interacts with modern storage drives through Logical Block Addressing (LBA), viewing the device simply as a massive, flat array of numbered blocks.    
- **The File Abstraction:** Human beings (and most application software) do not want to keep track of raw block numbers (e.g., remembering that a specific document is stored starting at block 4,092,110). The **File System** bridges this gap by abstracting that flat array of blocks into named, structured data units called **files**.
- **Directories and Hierarchy:** Beyond just files, the file system introduces folders (directories), allowing users to organize data into a logical, easily navigable tree structure.
- **Metadata (Data About Data):** To manage these files, the file system doesn't just store the file's contents; it must also store metadata.
    - This includes the file's name, size, creation/modification timestamps, and security permissions.
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
|**RAID 0**|**Striping only.** Data is sliced and spread across drives.|Maximum performance and storage capacity.|2|**None.** If one drive fails, _all_ data is lost.|
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
	* **SMB/CIFS:** Primarily used by Windows environments.
    - **NFS:** Primarily used by Linux/Unix environments.
- **Use Cases:** General file sharing, user home directories, central backups, and media streaming.
- **Pros/Cons:** Easy to set up and less expensive, but performance is limited by standard network traffic and latency.

#### Storage Area Network (SAN)

A SAN `/sæn/` is a highly specialized, high-speed, dedicated subnetwork that connects servers to a consolidated pool of block-level storage.

- **Block-Level Storage:** Unlike NAS, a SAN does not manage a file system. It exposes raw storage blocks (LUNs) directly to servers. To a connected server, a SAN volume looks and acts like a local internal hard drive (an array of raw LBA blocks). The server's own OS is responsible for formatting it with a file system (like NTFS or EXT4).
- **Common Protocols:** 
	* **Fibre Channel (FC):** Uses dedicated fiber-optic cables and switches for ultra-low latency and massive throughput.
    - **iSCSI:** Runs block-level SCSI commands over standard Ethernet cables, making it a cheaper alternative to Fibre Channel.    
- **Use Cases:** Massive databases (like Oracle or SQL), virtualization clusters (VMware/Hyper-V) requiring fast VM migration, and high-performance transactional applications.
- **Pros/Cons:** Incredibly fast, highly scalable, and ultra-low latency; however, it is highly complex to manage and very expensive to implement.
