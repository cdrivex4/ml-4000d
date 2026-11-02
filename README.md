# Magic Lantern for Canon EOS 4000D / Rebel T100 / EOS 3000D

[![Platform](https://img.shields.io/badge/Platform-Canon%20DIGIC%204%2B-blue.svg)](https://magiclantern.fm)
[![Firmware](https://img.shields.io/badge/Firmware-1.0.0-green.svg)](https://www.canon.com)
[![Status](https://img.shields.io/badge/Status-Live%20UI%20Verified%20on%20LCD-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-GPLv2-yellow.svg)](LICENSE)

A clean-room, hardware-verified port of **Magic Lantern** to the **Canon EOS 4000D / Rebel T100 / EOS 3000D** (Canon Model ID `0x80000422`, DIGIC 4+ ARM946E-S, Firmware 1.0.0, DryOS 2.3 `#0058+p7`).

---

## 📸 Milestone: Live & Interactive on Physical Hardware

The Magic Lantern user interface is fully booted and operational on physical Canon EOS 4000D hardware:
- **Core Menus Operational:** Shoot, Debug, Display, Customized Buttons, Movie tweaks, and Audio menus render cleanly.
- **Full Interactive Control:** Directional pad navigation, Quick Control (`Q`) editing, and `Av / Trash` / `DISP` toggles are mapped and responsive.
- **Flicker-Free Display:** Resolved Canon Shooting Status (OLC) screen-tearing by suppressing WindowSystem dirty bits at `*(0x3BE8C + 0x3C)` and `+0x30`.
- **2.7" 230k-dot Bezel Geometry:** Repositioned menu help footers to $y=420$ and $y=442$ to prevent bezel cut-off.

---

## 🛡️ Safety & Architecture: 100% Volatile RAM Execution

This port strictly enforces a **100% Volatile RAM Execution model** (`#undef CONFIG_PROP_REQUEST_CHANGE`):
- **Zero Flash Writes:** Magic Lantern executes entirely within dynamic SDRAM. The camera's internal ROM flash chips (`ROM0` and `ROM1`) are never written, erased, or flashed.
- **Unbrickable by Design:** Removing the SD card or flipping the card lock slider immediately restores 100% factory Canon firmware behavior.

---

## 🔬 Reverse Engineering Breakthroughs: Where ML Left Off & How We Solved It

The initial 4000D reverse-engineering efforts began around 2019 on the Magic Lantern forum ([Topic 23369](https://www.magiclantern.fm/forum/index.php?topic=23369.0)) led by `@a1ex` and `ccritix`. While early ROM dumping and initial stubs were mapped, progress halted due to several undocumented DIGIC 4+ hardware quirks and deceptive architectural similarities with the Canon 1300D (Rebel T6).

Here is how our clean-room implementation broke through each barrier:

### 1. The 1300D Architectural Trap (Why Offsets Cannot Be Assumed)
Because both the 1300D and 4000D share the DIGIC 4+ SoC and an 18MP APS-C sensor, previous attempts assumed the 4000D address space mirrored the 1300D. In practice, DryOS memory layouts and hardware mappings diverged significantly:
- **LiveView State Object & YUV Framebuffer:**
  - *The Trap:* On 1300D, `DISPLAY_STATEOBJ` was `0x0002FBB4` with an active YUV buffer pointer at `0x318C8`.
  - *The 4000D Reality:* On 4000D, `DISPLAY_STATEOBJ` moved to `0x0002FBD4`. The active LiveView raster address is **not** static; it is dynamically resolved at runtime via `(*(uint32_t*)(0x2FBD4 + 0xB0))`, with display orientation at `MEM(0x2FBD4 + 0x7C)`. Assuming the 1300D address caused overlays (Zebras, Focus Peaking, Histograms) to read uninitialized memory.
- **OSD Bitmap Plane & Stride:**
  - *The Trap:* 1300D used `0x00056240` for bitmap info structures.
  - *The 4000D Reality:* 4000D relocated `BMP_VRAM_INFO` (`PB_BITMAP_INFO`) to `0x00053360` with a 960-byte stride (active buffer at `0x2087100`), while LiveView descriptors relocated to `0x0005339C`.
- **Card Activity LED (MMIO vs GPIO Table):**
  - *The Trap:* Legacy DIGIC 4 cameras toggled the Card LED directly at MMIO register `0xC0220134`.
  - *The 4000D Reality:* On 4000D, `0xC0220134` is obsolete. Canon routes LED control through an internal GPIO table (pin 77 / `0x4D` at `0xFE7FE250`) mapped to MMIO `0xC022D1E0`, driven by control words `0x0093D800` (LED ON) and `0x0083DC00` (LED OFF).
- **OLC Shooting Screen Tearing:**
  - *The Trap:* Canon's background WindowSystem task aggressively repainted the default shooting status screen every 20–50ms, wiping out Magic Lantern menus.
  - *The Solution:* We hooked `WINSYS_BMP_DIRTY_BIT_NEG` at `MEM(0x3BE8C + 0x3C)` and suppressed redraws at `0x3BE8C + 0x30`, yielding a clean, tear-free OSD.

### 2. The Bootflag Deadlock (FIR HMAC Signatures & The Wi-Fi Solution)
- *The Problem:* The Canon EOS 4000D bootloader enforces cryptographic HMAC-SHA1 signatures on `.FIR` files. Running a modified `.FIR` (like `BOOT4000.FIR`) fails immediately with *"Update file error"*. Compounding this, Canon completely removed the "EOS Utility" USB menu entry from the 4000D firmware, blocking traditional USB PTP pairing.
- *The Breakthrough:* We analyzed the camera's native *"Connect to smartphone"* mode over Wi-Fi, discovering it exposes standard CIPA DC-005 PTP/IP on TCP port 15740. By emulating an iPhone client handshake and sending DryOS PTP event procedures (`PTP 0x9050` / `0x9052` `EnableBootDisk`), we enabled `BOOT=1` non-destructively in seconds without flashing a single byte of ROM.

### 3. Automated Reverse-Engineering Pipeline (`scripts/automate_edmac_mapping.py`)
Rather than relying on tedious manual disassembly for future firmware revisions or related models, we built an autonomous reverse-engineering pipeline:
- Powered by Capstone, it disassembles `ROM1.BIN` in **under 3 seconds**.
- Automatically indexes all 124 `SetEDmac` callsites.
- Extracts hardware write channels (`0xC0F04208` for HD, `0xC0F04308` for LiveView).
- Maps the Shared Resource Memory pool manager (`SRM_MGR = 0x0002F7D4`) and confirms the 31.4 MB raw buffer pool (`SRM_BUFFER_SIZE = 0x01F68000`).

### 4. Dynamic Module Loading & Clean Build Pipeline
- Built [`scripts/generate_sym.py`](scripts/generate_sym.py) to resolve and export all 1,322 core kernel symbols into `t100_100.sym`, enabling dynamic `.mo` module runtime linking.
- Rewrote legacy Python 2 build utilities (`readme2modulestrings.py`, `checkdep.py`) into modern Python 3.
- Stripped all host metadata leaks (`whoami` / `hostname`) to ensure 100% reproducible, zero-PII open-source builds.

---

## 🚀 Quick Start: How to Get It Running

### Prerequisites
- Canon EOS 4000D / Rebel T100 / 3000D running official **Firmware 1.0.0**.
- SD/SDHC memory card $\le 32\text{ GB}$ (FAT32 formatted).
- Fully charged LP-E10 battery.

### Step 1: Enable the Bootflag Safely via Wi-Fi PTP/IP
Because the 4000D validates HMAC signatures on `.FIR` update files, standard FIR-based bootflag installers fail with *"Update file error"*. Instead, we use the camera's native PTP/IP Wi-Fi interface:
1. In the Canon menu, set **Wi-Fi** to **Connect to smartphone** with **Auto IP (DHCP)**.
2. Note the camera's assigned IP address on your network.
3. Run the non-destructive activation script from your PC:
   ```bash
   python scripts/ptp_smartphone_bootflag.py <CAMERA_IP>
   ```
4. Press **[OK]** on the camera LCD when prompted (*"Connect to smartphone?"*). The script calls DryOS `EnableBootDisk` (`PTP 0x9052`) and returns `0x2001 OK`.

*(To disable the bootflag at any time, run `python scripts/ptp_smartphone_disable_bootflag.py <CAMERA_IP>`)*.

### Step 2: Make the SD Card Bootable
Use either the included Windows GUI utility or the cross-platform Python script:

- **Option A (Windows GUI - Recommended):**
  1. Open [`tools/card_prep/EOScard.exe`](tools/card_prep/).
  2. Select your SD card drive letter.
  3. Ensure both **BOOTDISK** and **EOS_DEVELOP** are checked.
  4. Click **Save**.
  > [!IMPORTANT]
  > **Do NOT use the online download buttons inside EOScard!** Those buttons fetch generic ML builds for older models (550D/60D). Use EOScard *solely* to write the bootloader markers, then copy our custom 4000D `autoexec.bin` and `ML/` folder in Step 3.
  *(EOScard is authored by Pel; official website & updates at [https://pel.hu/eoscard/](https://pel.hu/eoscard/))*.

- **Option B (Cross-Platform Python - Linux / macOS / Windows):**
  Run our standalone Python card preparation script:
  ```bash
  python scripts/make_bootable.py <DRIVE_LETTER_OR_DEVICE>
  ```

---

### Step 3: Copy Magic Lantern Files & Sync Discipline
1. **Log Protection & Sync Safety:** If running tests, always use the included [`liveSDCard/Sync-SDCard.ps1`](liveSDCard/Sync-SDCard.ps1) (or `doit.bat`) to sync. It automatically pulls and archives camera logs *first* before pushing updates, preventing accidental deletion of crash dumps. Photos in `DCIM/` are never touched.
2. Copy [`liveSDCard/autoexec.bin`](liveSDCard/autoexec.bin) (SHA-256: `0A5C14EAA8A8A15DA08426BA16E03D7143054A0FA2FA685C79AA01BAA3B29C79`) to the root of the SD card.
3. Copy the complete [`liveSDCard/ML/`](liveSDCard/ML/) directory to the root of the SD card.
4. Safely eject the SD card before removing it from your PC.

### Step 4: Power On & Operating Controls
Turn the power switch to any shooting mode (`M`, `Av`, `Tv`, `P`):
- **Open / Close ML Menu:** Press the **`Av / Trash`** button (or **`DISP`**).
- **Navigate Items:** Use the **Directional Pad**.
- **Edit / Select Setting:** Press the **`Q` (Quick Control)** button or turn the Main Dial.

---

## 🧰 Bundled Tools & Card Preparation Utilities

Everything needed to bootstrap and test the camera is bundled directly in this repository:

| Tool / Script | Location | Purpose & Description |
| :--- | :--- | :--- |
| **`automate_edmac_mapping.py`** | [`scripts/automate_edmac_mapping.py`](scripts/automate_edmac_mapping.py) | Autonomous reverse-engineering disassembler mapping EDMAC DMA channels, display objects, framebuffers, and SRM pools from ROM. |
| **`generate_sym.py`** | [`scripts/generate_sym.py`](scripts/generate_sym.py) | Automated export symbol table generator converting `magiclantern` ELF symbols to `t100_100.sym` for dynamic module loading. |
| **`scan_edmac.py`** | [`scripts/scan_edmac.py`](scripts/scan_edmac.py) | Capstone disassembler analyzing all 124 EDMAC callsites, write registers, and descriptors in firmware. |
| **`EOScard.exe`** | [`tools/card_prep/EOScard.exe`](tools/card_prep/) | Standard Windows GUI utility by Pel ([pel.hu](https://pel.hu/eoscard/)) to format and write ML boot flags to SD cards. |
| **`mlinstall.exe`** | [`tools/card_prep/mlinstall.exe`](tools/card_prep/) | Automated Magic Lantern setup assistant. |
| **`make_bootable.py`** | [`scripts/make_bootable.py`](scripts/make_bootable.py) | Standalone pure-Python script to inject `EOS_DEVELOP` and `BOOTDISK` on Linux, macOS, and Windows. |
| **`ptp_smartphone_bootflag.py`** | [`scripts/ptp_smartphone_bootflag.py`](scripts/ptp_smartphone_bootflag.py) | Non-destructive Wi-Fi PTP/IP script to enable `BOOT=1` on the camera without risky FIR flashing. |
| **`ptp_smartphone_disable_bootflag.py`** | [`scripts/ptp_smartphone_disable_bootflag.py`](scripts/ptp_smartphone_disable_bootflag.py) | Wi-Fi PTP/IP script to disable the bootflag and restore factory `BOOT=0`. |
| **`download_arm_toolchain.py`** | [`scripts/download_arm_toolchain.py`](scripts/download_arm_toolchain.py) | Fetches and unpacks the portable xPack ARM GCC 13.3.1 toolchain for compiling from source. |

---

## 📚 Complete In-Depth Documentation

- 📖 [Stock to Live Setup Guide](docs/guide_stock_to_live.md) — Comprehensive step-by-step setup tutorial.
- 🛟 ["Don't Panic" Troubleshooting Guide](docs/dont_panic_troubleshooting.md) — Solutions for **Err 70**, **Err 11**, FIR update errors, crash points, and the 5-second battery pull.
- 💾 [exFAT Storage Architecture & Roadmap](docs/exfat_roadmap_and_verification.md) — VBR sector differences, bootloader checksums, and the $\ge 64\text{ GB}$ card roadmap.
- 🔬 [Deep Architectural Audit & Crash Resolutions](docs/argon_audit_and_recommendations.md) — Detailed reverse engineering analysis of memory stubs, OLC screen dirty bits, and DryOS tasks.

---

## 🔒 Cryptographic Checksums (Final Binary)

To verify the integrity of the provided release binary:

| File | Size | MD5 | SHA-256 |
| :--- | :--- | :--- | :--- |
| **`liveSDCard/autoexec.bin`** | 404,256 bytes | `69642AFB96C294F270D6779CEF08A75C` | `0A5C14EAA8A8A15DA08426BA16E03D7143054A0FA2FA685C79AA01BAA3B29C79` |
| **`liveSDCard/ML/MODULES/t100_100.sym`** | 34,815 bytes | `D03E39B243D63F8FC9144FBA847964BF` | `D4DACB0F69547B8CBC8C35E309D372BB722A1EE19D33F6AB51B78486AAAEAD02` |

*Full cryptographic hashes table for firmware verification available in [`docs/cryptographic_verification_and_hashes.md`](docs/cryptographic_verification_and_hashes.md).*

---

## ⚖️ Zero Canon Copyrighted Material Policy

This repository hosts **strictly zero proprietary Canon material**.
- No Canon firmware binaries (`.FIR`), ROM dumps (`ROM0.BIN`, `ROM1.BIN`), or copyrighted Canon headers are distributed here.
- Only open-source code, clean-room stubs, build tools, and cryptographic hashes are provided.
- Users must dump their own firmware legally from their own hardware using portable open-source dumping tools.

---

## 🤝 Community Collaboration, Bug Tracking & Mainline Support

- **Bug Reports & Issues:** We welcome community feedback and bug squashing! If you encounter issues, please submit them through [GitHub Issues](https://github.com/cdrivex4/ml-4000d/issues) with relevant log files from `ML/LOGS/` so they can be tracked and resolved.
- **Mainline Alignment:** We are eager to assist the upstream Magic Lantern development team in validating and merging the 4000D target into the official repositories. Note that our hardware validation is specifically based on the physical Canon EOS 4000D (FW 1.0.0) test bench.

---

## 🎖️ Credits & Hall of Fame

This port stands on the shoulders of the remarkable reverse engineering pioneers of the Magic Lantern and CHDK projects. **If they had not started, we would not have been able to get this far:**

- **Alex Dumitrache (`@a1ex`)**: Reverse engineered the portable ROM dumper (`DMP4000D.FIR`), developed early QEMU-EOS emulator support, and established foundational DryOS analysis.
- **Petabyt**: Author of the reference 1300D port (`petabyt/magiclantern`), the cache-lockdown ARM946E-S boot sequence (`boot-d45-ch.c`), and trampoline architecture.
- **`@names_are_hard` (`reticulatedpines`)**: Modernized Magic Lantern architecture, QEMU-EOS maintainer, and author of extensive reverse engineering references.
- **`ccritix`**: Initial 4000D platform definitions and compilation harness.
- **Trammell Hudson**: Creator and founder of Magic Lantern (2009).
- **CHDK Community**: Pioneered DIGIC reverse engineering, state object analysis, and hardware register mapping.
