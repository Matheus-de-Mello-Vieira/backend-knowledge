# File Systems

A file system is the method and data structure used by an operating system (OS) to store, organize, and access files on a storage device.

For the security perspective on file systems, see [Endpoint Security](../Security/05%20Architecture%20and%20Infrastructure%20Security/02%20Endpoint%20Security.md).

- **The LBA Foundation:** The Operating System interacts with modern storage drives through Logical Block Addressing (LBA), viewing the device simply as a massive, flat array of numbered blocks.    
- **The File Abstraction:** Human beings (and most application software) do not want to keep track of raw block numbers (e.g., remembering that a specific document is stored starting at block 4,092,110). The **File System** bridges this gap by abstracting that flat array of blocks into named, structured data units called **files**.
- **Directories and Hierarchy:** Beyond just files, the file system introduces folders (directories), allowing users to organize data into a logical, easily navigable tree structure.
- **Metadata (Data About Data):** To manage these files, the file system doesn't just store the file's contents; it must also store metadata.
    - This includes the file's name, size, creation/modification timestamps, and security permissions.
    - **Block Mapping:** Critically, the metadata includes an index (such as an **inode** in Linux) that acts as a map, pointing the OS to the exact, non-sequential LBA block numbers where the file's actual fragmented data is physically stored on the drive.
- **Free Space Management:** The file system is continually responsible for maintaining a ledger of which blocks are currently in use by files and which blocks are free. When you save a new file or expand an existing one, the file system consults this ledger to allocate empty blocks, ensuring data is never accidentally overwritten.

## Basic Concepts

- **Directory (Folder):** The fundamental organizational unit within a file system, which can contain files as well as other directories (subdirectories).
- **File:** A distinct set of information stored on a device. Files possess names and extensions that indicate both their type and their content.
- **File Extension:** The specific set of characters that appears after the filename, serving to indicate the file's type or format.
- **Path:** The exact location or address of a file or directory within the file system.
  - *Absolute Path:* Traces the location starting from the very root of the file system.
  - *Relative Path:* Traces the location starting from the current working directory.
- **File Permissions:** Security controls that define exactly who is allowed to access, read, write, or execute a specific file. These permissions can be individually configured for the file's owner, a specific group of users, and all other users.
- **Disk Formatting:** The initial process of preparing a physical storage device to be used as a file system. This creates the foundational structure needed to store files and directories, and the process can erase all previously existing data on the device.
- **File Fragmentation:** A condition that occurs when a single file is broken into smaller pieces and stored in scattered, non-contiguous parts of the disk. This typically happens when there is not enough continuous free space available to store the file in one place. Fragmentation negatively affects file system performance, resulting in slower read and write operations.

## Common File Systems

- **NTFS (New Technology File System):** The default file system used for Windows operating systems. It allows for the creation of folders and subfolders, as well as the robust management of file and directory permissions.
- **HFS (Hierarchical File System):** The standard file system traditionally used for MacOS. It allows for the organization of files into folders and subfolders, in addition to providing built-in support for large files and data compression.
- **EXT4 (Fourth Extended File System):** The default file system for Linux operating systems. It enables the management of large files and supports both fragmentation and data compression.
- **FAT32 (File Allocation Table 32-bit):** An older, legacy file system that has been widely used for external storage devices and USB flash drives. While it offers high compatibility across many different operating systems, it has strict limitations and does not support large individual files or folders containing a massive number of files.
- **exFAT (Extended File Allocation Table):** A modernized file system designed specifically to bridge the gap between platforms. It allows for seamless compatibility with external storage devices and USB flash drives across different operating systems, while fully supporting the storage of large files that FAT32 cannot handle.
- **Btrfs (B-Tree File System):** A modern, advanced file system designed for Linux that focuses on fault tolerance, simplified administration, and data integrity. It utilizes a copy-on-write (CoW) mechanism and natively supports powerful features like instant system snapshots, pooling multiple drives into a single volume, and continuous data checksumming to automatically detect and repair silent data corruption.
- **tmpfs (Temporary File System):** A specialized file system that resides entirely in volatile system memory (RAM) and swap space, rather than on persistent physical storage like HDDs or SSDs. Because it completely bypasses the latency of storage drives, it offers exceptionally fast read and write speeds for temporary data, but all files stored within it are permanently lost the moment the system reboots or loses power.
