# Canon EOS 4000D: Cryptographic Verification & Hashes

**Document ID:** `DOC-ML-4000D-CRYPTO-HASHES`  
**Target Hardware:** Canon EOS 4000D / Rebel T100 / EOS 3000D  
**Policy Statement:** **Zero Canon Copyrighted Material.** This repository does not host, redistribute, or mirror any proprietary Canon firmware binaries, ROM dumps, or decrypted operating system code. This document provides cryptographic hashes (SHA-256 and MD5) solely for integrity verification, security research, and clean-room reproducibility.

---

## 1. Official & Dumper Firmware Hashes

Users must acquire or dump their own firmware images using legal, non-infringing methods (e.g. running the portable ROM dumper on their personally owned hardware).

| Artifact / Description | Size (Bytes) | MD5 Checksum | SHA-256 Checksum |
| :--- | :--- | :--- | :--- |
| **`CCF22110.FIR`**<br>(Official Canon FW 1.1.0 Update) | 14,512,928 | `5E6BD219718390381A316C9A3E15B79F` | `05DD9BE40AE3CDB129667B04B8C0E4793B78FB84CA4B0A07F374A07D6966C507` |
| **`DMP4000D.FIR`**<br>(a1ex Portable ROM Dumper) | 67,804 | `68978A4B7577D040D7D4367DDEBC6E3B` | `DD66AA847F678B65171C5031555880F045EB54D53610F6D8CB2044EDDE951E50` |
| **`ROM0.BIN`**<br>(Unconnected / Dummy on 4000D) | 33,554,432 | `387D96A501C80EE5A1291E6A4BBBB636` | `776CA15C7C087423135729A606FCF961F4E3F77A9BDD01113AE4F7FB69343557` |
| **`ROM1.BIN`**<br>(Physical 32MB Flash Dump) | 33,554,432 | `7E270A21864011368F573CC3EAA3E67B` | `DF32E2F004070FF8E7DEA771EFEA12EF97F9F2B4BA1027534E3DC69A8A797D59` |

> [!NOTE]
> On the Canon EOS 4000D, `ROM0` is not physically connected to the memory bus. `ROM1.BIN` represents the complete 32 MiB system flash containing bootloader and DryOS operating system routines.

---

## 2. Magic Lantern Milestone Binary Hashes

The following open-source binaries are compiled from this repository:

| Binary / Build Target | Size (Bytes) | MD5 Checksum | SHA-256 Checksum | Verification Status |
| :--- | :--- | :--- | :--- | :--- |
| **`autoexec.bin`** (Milestone 1)<br>(Minimal Hello-World Target) | 6,496 | `2C74CEA720B566CCC96155DACD18CB22` | `4946ED587048FE0BD3C88E95E541FCB22CFDA136426294B3395FDB853718B0E8` | Hardware LED Verified |
| **`autoexec.bin`** (Current Live Build)<br>(Full UI & Dialogs, Clean OSD) | 404,256 | `FFD53F4949492379A78571F436C1269C` | `D0E361E594E67F166F75DE0CC41BC03098063780433978DCEF026C103F36F7B0` | **Hardware LCD Verified** |

---

## 3. How to Legally Dump Your Own 4000D ROM

1. Obtain a FAT32-formatted SD card ($\le 32\text{ GB}$).
2. Place `DMP4000D.FIR` in the root of the card.
3. Insert the card into the camera and run the standard Canon Firmware Update routine from the setup menu.
4. The portable dumper executes in RAM and writes `ROM0.BIN` and `ROM1.BIN` to your SD card.
5. Verify the SHA-256 checksum of your dump using:
   ```bash
   sha256sum ROM1.BIN
   ```
   (or in PowerShell: `Get-FileHash -Algorithm SHA256 ROM1.BIN`).

---

## 4. Credits & Research Acknowledgments

We express our gratitude to the developers whose open-source tools made this possible:
- **Alex Dumitrache (`@a1ex`)**: Reverse engineering of portable ROM dumpers, DryOS structure, and QEMU-EOS.
- **Petabyt**: Author of the 1300D tree (`petabyt/magiclantern`) and ARM946E-S cache-lockdown bootloader shim (`boot-d45-ch.c`).
- **`@names_are_hard` (`reticulatedpines`)**: Modernized Magic Lantern architecture and QEMU-EOS development.
- **`ccritix`**: Initial 4000D platform definitions and build infrastructure.
- **Trammell Hudson**: Founder of Magic Lantern (2009).
- **CHDK Community**: Pioneered DIGIC reverse engineering and register discovery.
