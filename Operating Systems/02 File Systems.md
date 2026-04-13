# File Systems

A file system is the method and data structure used by an operating system (OS) to store, organize, and access files on a storage device.

For the security perspective on file systems, see [02 Endpoint Security.md](../Security/Information%20Security/02%20Endpoint%20Security.md#filesystem-security).

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
