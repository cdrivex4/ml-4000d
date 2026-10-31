# exFAT Support & Storage Architecture Roadmap: Canon EOS 4000D

**Document ID:** `DOC-ML-4000D-EXFAT-ROADMAP`  
**Target Hardware:** Canon EOS 4000D / Rebel T100 / EOS 3000D (DIGIC 4+, Firmware 1.0.0)

---

## 1. Storage Architecture Overview

Canon EOS cameras partition and format SD media based on card capacity according to SD Association specifications:
- **Cards $\le 32\text{ GB}$ (SDSC / SDHC):** Formatted by the camera as **FAT32**.
- **Cards $\ge 64\text{ GB}$ (SDXC):** Formatted by the camera as **exFAT**.

### 1.1 Current Verification Status
- **FAT32 Support ($\le 32\text{ GB}$):** **100% OPERATIONAL & VERIFIED.** Magic Lantern autoboot, execution, menu rendering, configuration persistence, and logging function flawlessly.
- **exFAT Support ($\ge 64\text{ GB}$):** **UNDER ACTIVE INVESTIGATION.** Because the volume boot record (VBR) structure and bootloader marker offsets differ between FAT32 and exFAT, SDXC cards formatted as exFAT require specialized sector formatting before the camera's early bootloader will execute `autoexec.bin`.

---

## 2. Boot Sector Differences: FAT32 vs exFAT

### 2.1 FAT32 Boot Record Layout
On standard FAT32 cards:
- Byte `0x00..0x02`: `EB 58 90` (x86 JMP instruction)
- Byte `0x03..0x0A`: OEM Name string (e.g. `MSDOS5.0`)
- Byte `0x40..0x4A`: Magic Lantern boot token: **`EOS_DEVELOP`** (11 bytes ASCII)
- Byte `0x44..0x4B` (or `0x5A`): Volume token: **`BOOTDISK`**

### 2.2 exFAT Boot Record Layout
On exFAT formatted cards:
- Byte `0x00..0x02`: `EB 76 90` (x86 JMP instruction)
- Byte `0x03..0x0A`: File system identifier: **`EXFAT   `** (8 bytes ASCII, space-padded)
- Sector `0..10`: Main Boot Region (exFAT specifies an 11-sector boot region plus a checksum sector at sector 11).
- In DIGIC 4/5/4+ bootloaders, Canon's boot ROM checks for `EOS_DEVELOP` and `BOOTDISK` at shifted offsets (typically `0x40` or `0x5A` within the first sector of the VBR). If the sector 11 boot checksum is invalid, the boot ROM will discard the boot sector.

---

## 3. DryOS Kernel exFAT Capability

Reverse engineering of `firmware/ROM1.BIN` confirms that **the Canon DryOS 2.3 kernel contains native exFAT read/write routines**:
- The exFAT filesystem driver is compiled into the main firmware image alongside the SDXC controller driver (`0xFE27C000..0xFE27E000`).
- Once DryOS boots and initializes the card driver (`sd_driver_interrupt` at `0x4B`), file operations (`_FIO_OpenFile`, `_FIO_ReadFile`, `_FIO_WriteFile`) seamlessly handle exFAT cluster allocation tables and files larger than 4 GiB.
- The challenge is strictly bounded to the **pre-RTOS secondary bootloader**: ensuring the camera's initial bootloader reads `autoexec.bin` off an exFAT partition before the kernel starts.

---

## 4. Actionable exFAT Testing Roadmap

1. **Phase 1: Boot Sector Flag Calibration (Non-Destructive):**
   - Format a 64GB / 128GB SDXC card as exFAT using the camera's internal format function.
   - Inspect sector 0 using a hex editor.
   - Inject `EOS_DEVELOP` at `0x40` and `BOOTDISK` at `0x5A` while recalculating the mandatory exFAT 12-sector VBR checksum (using `EOScard` or a dedicated Python script).
   - Test if the 4000D bootloader reads `autoexec.bin` and blinks the Card Activity LED (`0xC022D1E0`).
2. **Phase 2: Cluster Contiguity Verification:**
   - If `autoexec.bin` fails to load, confirm whether the early bootloader assumes a contiguous cluster chain. Ensure `autoexec.bin` is written as the very first file to unfragmented media.
3. **Phase 3: Workaround for Large Cards (FAT32 Formatting):**
   - In the interim, users wishing to use 64GB or 128GB cards can format them as **FAT32 with 32KB clusters** using tools like `GUIFormat` or `fat32format`. The 4000D bootloader and DryOS will mount large FAT32 volumes without issues.
