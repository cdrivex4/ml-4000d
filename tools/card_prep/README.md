# SD Card Preparation Tools & Utilities

This directory contains the essential utilities required to prepare, format, and configure SD cards for Magic Lantern execution on the Canon EOS 4000D / Rebel T100 / EOS 3000D.

---

## 🛠️ Included Utilities

### 1. `EOScard.exe` (Windows GUI)
- **Author:** Pel ([https://pel.hu/eoscard/](https://pel.hu/eoscard/))
- **Description:** The community-standard standalone Windows utility designed specifically to make SD cards bootable for Magic Lantern. It automatically handles FAT32 partition alignment, volume naming (`BOOTDISK`), and injecting the required boot flags (`EOS_DEVELOP`) into sector 0.
- **Companion Libraries:** Requires `libeay32.dll` and `ssleay32.dll` (included in this directory) for secure network lookups.

#### How to Use EOScard:
1. Insert your SD card ($\le 32\text{ GB}$) into your PC card reader.
2. Launch `EOScard.exe`.
3. Select your SD card drive letter from the dropdown.
4. Ensure the **BOOTDISK** and **EOS_DEVELOP** checkboxes are enabled.
5. Click **Save** (or apply).

> [!WARNING]
> **CRITICAL ORDER OF OPERATIONS — DO NOT OVERWRITE `autoexec.bin`:**
> `EOScard` has built-in buttons to download official Magic Lantern builds from the internet. **Do not download or extract generic builds through EOScard!** The 4000D requires our custom DIGIC 4+ DryOS 2.3 payload. If `EOScard` writes an `autoexec.bin` to your card, it is an incompatible build for older cameras.
> **Rule:** Use `EOScard` *only* to write the boot sector markers (`BOOTDISK` / `EOS_DEVELOP`). **Always copy our custom 4000D `liveSDCard/autoexec.bin` and `ML/` folder AFTER running EOScard!**

---

## 🔄 The 3-Stage Sync Discipline: What to Sync, When, and Why

During development and field testing, getting fresh logs without accidentally clobbering them or booting stale code is critical. This is why we created [`liveSDCard/Sync-SDCard.ps1`](../../liveSDCard/Sync-SDCard.ps1):

1. **Stage 1 — PULL FIRST (Never Overwrite Blindly):**
   - The camera writes diagnostic logs (`BOOT.LOG`, `DIAGS.LOG`, `BUTTONS.LOG`, `ST_*.LOG`) to the root of the card.
   - **Hazard:** Naive scripts using `robocopy /PURGE` or `/MIR` will wipe the camera's new logs off the SD card before anyone can read them!
   - **Rule:** The sync tool *always* pulls logs from the SD card to the PC archive first and snapshots them with a timestamp before performing any write operations.
   - **Photo Safety:** The sync tool never touches or modifies the camera's `DCIM/` folder.

2. **Stage 2 — PUSH & VERIFY (Preventing the Stale-Build Trap):**
   - If Windows caches file writes or if a file copy fails silently, the camera boots the old binary, leading the developer to believe their new code failed when it never actually executed.
   - **Rule:** The sync tool computes the SHA-256 hash of `autoexec.bin` on the PC and compares it directly against the SHA-256 of the binary on the SD card, verifying that the card binary is 100% identical.

3. **Stage 3 — FINALIZE & ARCHIVE (Timestamp Rigor):**
   - Old logs on the card are moved into `W:\ML\LOGS\archive\`. This guarantees that on the next boot, any log file on the card has a fresh timestamp relative to the latest flash time (`[FRESH: +XXXXs after build flash]`), eliminating ambiguity.

4. **Stage 4 — SAFELY EJECT:**
   - FAT32 volume dirty bits: Always safely eject the SD card before removing it from the card reader. Pulling a card during pending writes can leave the filesystem dirty, causing the 4000D bootloader to refuse to boot `autoexec.bin`.

---

### 2. `mlinstall.exe` (Windows Assistant)
- **Description:** Automated Magic Lantern SD card installer and setup utility.

---

### 3. Cross-Platform Alternative: `scripts/make_bootable.py` (Linux / macOS / Windows)
If you are on Linux, macOS, or prefer a non-GUI script, a standalone pure-Python implementation is provided in the repository:
```bash
python scripts/make_bootable.py <DRIVE_LETTER_OR_DEVICE>
```
This writes the `EOS_DEVELOP` string at offset `0x40` and `BOOTDISK` at offset `0x44` of sector 0.

---

## 🔒 Checksums for Verification

| File | Size (Bytes) | MD5 | SHA-256 |
| :--- | :--- | :--- | :--- |
| **`EOScard.exe`** | 2,731,520 | `0681E89887448C59EB58158D685249F7` | `0F453B5FD008341405A360A88BE0CD2CF5362DE751170793531B06AFB804D844` |
| **`mlinstall.exe`** | 1,257,984 | `4285F4A22852ED8577EC5D1DD1EE11F4` | `E356F4176ADB77815453C2607A65AE96DC301128CF3ED8E0877144D1E41B3AE1` |
| **`libeay32.dll`** | 1,380,864 | `FA5DEF992198121D4BB5FF3BDE39FDC9` | `5264A4A478383F501961F2BD9BEB1F77A43A487B76090561BBA2CBFE951E5305` |
| **`ssleay32.dll`** | 337,920 | `2117E31688AEF8ECF267978265BFCDCD` | `0A4031AB00664CC5E202C8731798800F0475EF76800122CEBD71D249655D725F` |

---

## 🎖️ Credits
- **Pel ([pel.hu](https://pel.hu/))** for creating and hosting `EOScard` for the Magic Lantern community.
