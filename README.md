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
1. Format your SD card ($\le 32\text{ GB}$) as **FAT32** with the volume label **`BOOTDISK`**.
2. Write the string **`EOS_DEVELOP`** at byte offset `0x40` (and `BOOTDISK` at offset `0x44`) of the boot sector (using `EOScard` or standard `dd`).

### Step 3: Copy Magic Lantern Files
1. Copy the precompiled [`liveSDCard/autoexec.bin`](liveSDCard/autoexec.bin) to the root of the SD card.
2. Copy the complete [`liveSDCard/ML/`](liveSDCard/ML/) directory to the root of the SD card.
3. Safely eject the SD card and insert it into your 4000D.

### Step 4: Power On & Operating Controls
Turn the power switch to any shooting mode (`M`, `Av`, `Tv`, `P`):
- **Open / Close ML Menu:** Press the **`Av / Trash`** button (or **`DISP`**).
- **Navigate Items:** Use the **Directional Pad**.
- **Edit / Select Setting:** Press the **`Q` (Quick Control)** button or turn the Main Dial.

For complete in-depth documentation, see:
- 📖 [Stock to Live Setup Guide](docs/guide_stock_to_live.md)
- 🛟 ["Don't Panic" Troubleshooting Guide](docs/dont_panic_troubleshooting.md)
- 💾 [exFAT Storage Architecture & Roadmap](docs/exfat_roadmap_and_verification.md)
- 🔬 [Deep Architectural Audit & Crash Resolutions](docs/argon_audit_and_recommendations.md)

---

## 🔒 Cryptographic Checksums (Final Binary)

To verify the integrity of the provided release binary:

| File | Size | MD5 | SHA-256 |
| :--- | :--- | :--- | :--- |
| **`liveSDCard/autoexec.bin`** | 404,256 bytes | `FFD53F4949492379A78571F436C1269C` | `D0E361E594E67F166F75DE0CC41BC03098063780433978DCEF026C103F36F7B0` |

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
