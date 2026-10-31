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
5. Click the **Magic Lantern** logo or **Save** button.
6. Once completed, your card is ready for `autoexec.bin`.

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
