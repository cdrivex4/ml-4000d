# Canon EOS 4000D (Rebel T100 / 3000D) Reverse Engineering & Magic Lantern Port — Handoff Document

**Last Updated:** 2026-11-01 13:40 (+04:00)  
**Workspace Root:** `d:\Dev\REverSE\4000D` (STRICT BOUNDARY: All files, tools, virtualenvs, and outputs reside within this directory)  
**Primary Coordinator Conversation ID:** `6562844d-4251-4d95-9686-70018bc3c2fb`  
**Status:** MILESTONE 4 ACHIEVED — LIVEVIEW BUFFERS MAPPED, AUTOMATED EDMAC DISASSEMBLER, DYNAMIC MODULES LOADED (T100_100.SYM), 100% PII CLEAN, COMMITTED & PUSHED TO GITHUB

---

## 1. Mission & Core Constraints

1. **Goal:** Reverse engineer the Canon EOS 4000D (Model ID `0x80000422` / `0x422`, DIGIC 4+ ARM946E-S / ARMv5TE) firmware using the **REA (`morluto/rea`)** framework, local disassembly/emulation tools (`arm-none-eabi-objdump`, `capstone`, `unicorn`, `qemu-eos`), and Magic Lantern's `1300D` reference port to build a **mathematically verified firmware payload (`.FIR` / `AUTOEXEC.BIN`)** before any non-destructive testing on physical hardware.
2. **Directory Restriction:** Everything resides strictly inside `d:\Dev\REverSE\4000D`.
3. **Worker Subagents Completed:**
   - **[REA Framework & Toolchain Engineer](conversation://2ac084a7-7e5e-47be-a547-5001309f0df5)** (`2ac084a7-7e5e-47be-a547-5001309f0df5`, Model: `flash`) — Idle / Complete.
   - **[Firmware & Dumper Acquisition Specialist](conversation://630c024c-0420-430b-ba9a-f79cf27d0220)** (`630c024c-0420-430b-ba9a-f79cf27d0220`, Model: `flash`) — Idle / Complete.
   - **[Magic Lantern & QEMU-EOS Researcher](conversation://3b120ee2-fa84-4480-8ab0-3b9ca387af9d)** (`3b120ee2-fa84-4480-8ab0-3b9ca387af9d`, Model: `flash`) — Idle / Complete.

---

## 2. Complete Workspace Inventory (`d:\Dev\REverSE\4000D`)

### 2.1 Toolchains & Analysis Frameworks
- **Python RE Virtualenv ([`.venv`](file:///d:/Dev/REverSE/4000D/.venv)):**
  - Python 3.12.10 managed via `uv` (`uv 0.9.22`).
  - Installed packages: `capstone` (5.0.9), `unicorn` (2.1.4), `lief` (1.0.0), `pyelftools` (0.33).
- **REA Framework ([`rea`](file:///d:/Dev/REverSE/4000D/rea)):**
  - Cloned from `https://github.com/morluto/rea` (v6.7.0) and built locally (`npm run build:cached`).
  - Patched [`src/ghidra/GhidraProvider.ts`](file:///d:/Dev/REverSE/4000D/rea/src/ghidra/GhidraProvider.ts#L615-L625) (`inspectWindowsP0TargetSupport`) to permit `raw-binary` with `architecture === "arm"` on Windows.
  - Integrated with portable GNU `objdump` via environment variable:
    `REA_OBJDUMP_COMMAND=d:\Dev\REverSE\4000D\tools\xpack-arm-none-eabi-gcc-13.3.1-1.1\bin\arm-none-eabi-objdump.exe`
  - CLI entry point: `node d:\Dev\REverSE\4000D\rea\scripts\rea.mjs` (`175` CLI commands / `227` MCP tools).
- **Portable GNU ARM Embedded Toolchain ([`tools/xpack-arm-none-eabi-gcc-13.3.1-1.1/bin`](file:///d:/Dev/REverSE/4000D/tools/xpack-arm-none-eabi-gcc-13.3.1-1.1/bin)):**
  - `arm-none-eabi-gcc.exe` (13.3.1), `arm-none-eabi-objdump.exe` (2.42.0), `arm-none-eabi-objcopy.exe`, `arm-none-eabi-nm.exe`, `arm-none-eabi-readelf.exe`.

### 2.2 Firmware & Compiled Binary Artifacts ([`firmware/`](file:///d:/Dev/REverSE/4000D/firmware))
- **[`DMP4000D.FIR`](file:///d:/Dev/REverSE/4000D/firmware/DMP4000D.FIR)** (`67,804 bytes` / `0x108DC`):
  - Official Magic Lantern Portable ROM Dumper for Canon EOS 4000D recovered from Wayback Machine (`20221109180426`).
  - **MD5:** `68978a4b7577d040d7d4367ddebc6e3b`
  - **SHA-256:** `dd66aa847f678b65171c5031555880f045eb54d53610f6d8cb2044edde951e50`
  - **Header:** Model ID `0x80000422`, Version `"1.3.3"`, Checksum `0xff7bf4f3`, Updater1 Header `0xB0`, Payload Offset `0x120`, Payload Length `0x10740` (67,392 bytes), RAM Load Address `0x001ef930`, XOR Seed `0x9cbbb3a1`.
- **[`dmp4000d_payload.bin`](file:///d:/Dev/REverSE/4000D/firmware/dmp4000d_payload.bin)** (`67,392 bytes`):
  - Raw Updater1 payload extracted from `DMP4000D.FIR` (`0x120..0x10860`).
  - **SHA-256:** `2b95fa7b63f5728a3a31c51d56ca3df7aebad7362bb38e55c3c0df98a9fa66b9`
- **[`dmp4000d_decrypted.bin`](file:///d:/Dev/REverSE/4000D/firmware/dmp4000d_decrypted.bin)** (`1,304 bytes`) & **[`dmp4000d_payload.elf`](file:///d:/Dev/REverSE/4000D/firmware/dmp4000d_payload.elf)**:
  - Clean-room reference 4000D rescue dumper compiled from [`scripts/dmp4000d_entry.S`](file:///d:/Dev/REverSE/4000D/scripts/dmp4000d_entry.S) and [`scripts/dmp4000d_payload.c`](file:///d:/Dev/REverSE/4000D/scripts/dmp4000d_payload.c) at `0x001EF930`, inspected with REA (`ev_f017ef5262ddc9aee828dfab0547c2618713af17271aec6485471a3ccc8a9ebd`) and verified in Unicorn ([`scripts/emulate_dmp4000d.py`](file:///d:/Dev/REverSE/4000D/scripts/emulate_dmp4000d.py)).
- **[`v110-t100-3000d-4000d-win.zip`](file:///d:/Dev/REverSE/4000D/firmware/v110-t100-3000d-4000d-win.zip)** (`19,576,871 bytes`) & **[`CCF22110.FIR`](file:///d:/Dev/REverSE/4000D/firmware/CCF22110.FIR)** (`14,512,928 bytes`):
  - Official Canon EOS 4000D / Rebel T100 / 3000D Firmware 1.1.0 update downloaded from Canon CDN (`gdlp01.c-wss.com`).
  - **`CCF22110.FIR` SHA-256:** `05dd9be40ae3cdb129667b04b8c0e4793b78fb84ca4b0a07f374a07d6966c507`
- **[`autoexec_4000d_minimal_hello.bin`](file:///d:/Dev/REverSE/4000D/firmware/autoexec_4000d_minimal_hello.bin)** (`6,496 bytes`):
  - Compiled Magic Lantern `minimal/hello-world` boot binary for `MODEL=4000D` (`0x800000` entry $\to$ `0xC80000` `RESTARTSTART` $\to$ `0xFE0C0000` `ROMBASEADDR`).
  - **MD5:** `2C74CEA720B566CCC96155DACD18CB22`
  - **SHA-256:** `4946ED587048FE0BD3C88E95E541FCB22CFDA136426294B3395FDB853718B0E8`
  - **Verification:** Executed 1,000,000 instructions end-to-end in Unicorn ([`scripts/verify_autoexec_4000d_unicorn.py`](file:///d:/Dev/REverSE/4000D/scripts/verify_autoexec_4000d_unicorn.py)), proving `SIG_4000D_100` (`0x56D44DD6`) validation, CP15 cache lockdown, `cache_fake` hooks at `0xFE0C3B20` and `0xFE0C1B74`, 4,356 VRAM pixel writes to `0x40D07800`, and 5 Card LED toggles at `0xC0220134`.
- **[`autoexec_4000d_full.bin`](file:///d:/Dev/REverSE/4000D/firmware/autoexec_4000d_full.bin)** (`431,072 bytes`):
  - Compiled full Magic Lantern `platform/4000D.100` payload (`431,072 bytes` < `524,288 bytes` 512 KiB `AllocateMemory` reservation) with 32MB ROM `patch_instruction_jump` trampolines and DryOS 2.3 p39 task structs enabled.
  - **MD5:** `C1F71E993D86D0D3CAA3BA1595D23576`
  - **SHA-256:** `D73C317ED281DDF6CA1D353050E7220D60A711C61EF529AF0F968F1B5D9FB98E`

### 2.3 Verification & Automation Scripts ([`scripts/`](file:///d:/Dev/REverSE/4000D/scripts))
- [`pack_4000d_fir.py`](file:///d:/Dev/REverSE/4000D/scripts/pack_4000d_fir.py) — Proves `.FIR` container checksum math (`0xFF7BF4F3`) and reproduces `DMP4000D.FIR` byte-for-byte.
- [`emulate_dmp4000d.py`](file:///d:/Dev/REverSE/4000D/scripts/emulate_dmp4000d.py) — Unicorn ARMv5TE emulator for `dmp4000d_decrypted.bin` (3,600 instructions).
- [`verify_autoexec_4000d_unicorn.py`](file:///d:/Dev/REverSE/4000D/scripts/verify_autoexec_4000d_unicorn.py) — Full 6-stage Unicorn ARM946E-S boot verification harness for `autoexec_4000d_minimal_hello.bin` (1,000,000 instructions).
- [`prepare_4000d_rom_and_resolve_stubs.py`](file:///d:/Dev/REverSE/4000D/scripts/prepare_4000d_rom_and_resolve_stubs.py) — Post-dump automated 32MB `ROM1.BIN` validator (`SIG_4000D_100 = 0x56D44DD6`), 64KB block 1 $\to$ block 511 (`0xFFFF0000`) QEMU boot patcher, and Capstone/signature stub resolver.

### 2.4 Technical Reports ([`docs/`](file:///d:/Dev/REverSE/4000D/docs))
- [`rea_and_toolchain_report.md`](file:///d:/Dev/REverSE/4000D/docs/rea_and_toolchain_report.md) — REA architecture, toolchain inventory, and the 4 formal verification invariants.
- [`rea_dmp4000d_disassembly_and_emulation.md`](file:///d:/Dev/REverSE/4000D/docs/rea_dmp4000d_disassembly_and_emulation.md) — Complete FIR math proof, REA disassembly evidence, Unicorn emulation traces (`DMP4000D.FIR` & `autoexec.bin`), and automated ROM patcher documentation.
- [`firmware_and_threads_report.md`](file:///d:/Dev/REverSE/4000D/docs/firmware_and_threads_report.md) — Analysis of `DMP4000D.FIR` and Magic Lantern forum threads (`23369`, `16534`, `17969`, `19417`).
- [`dmp4000d_payload_analysis.md`](file:///d:/Dev/REverSE/4000D/docs/dmp4000d_payload_analysis.md) — Side-by-side structural comparison of `CCF22110.FIR` (v1.1.0) and `DMP4000D.FIR`.
- [`ml_1300d_4000d_architecture.md`](file:///d:/Dev/REverSE/4000D/docs/ml_1300d_4000d_architecture.md) — Architectural specification for `platform/4000D.100` and `qemu-eos` 4000D machine definition.
- [`ml_4000d_compilation_and_qemu_report.md`](file:///d:/Dev/REverSE/4000D/docs/ml_4000d_compilation_and_qemu_report.md) — Audit of `critix`'s 2019 commits (`056778668`, `0727054e4`), `CONFIG_4000D` 32MB trampoline fixes, `qemu-eos` integration, and compilation logs.

---

## 3. Verified Hardware & Memory Constants for Canon EOS 4000D (FW 1.0.0)

| Symbol / Parameter | Verified Value | Source / Proof |
|---|---|---|
| **Model ID (FIR / USB)** | `0x80000422` (`0x422`) | Verified in `DMP4000D.FIR`, `CCF22110.FIR`, and `Makefile.platform.map` |
| **Firmware Signature (`SIG_4000D_100`)** | `0x56D44DD6` | 256 KiB word-sum at `0xFE0C0000` (`critix` commit `0727054e4` & `verify_autoexec_4000d_unicorn.py`) |
| **Flash SPI Model ID** | `0x003825C2` | Macronix MX25L25635E 32MB SPI NOR (`Topic 23369` & `contrib/qemu/eos/eos.c:327`) |
| **ROM Topology** | Single 32MB ROM1 (`0xFE000000..0xFFFFFFFF`) | ROM0 is unconnected; boot sector at 64KB block 1 (`0x10000`) must be copied to block 511 (`0x1FF0000` / `0xFFFF0000`) for QEMU |
| **`ROMBASEADDR` (Cached)** | `0xFE0C0000` | 32MB mirror `0x100000000 - 0x02000000 = 0xFE000000` (`+0xC0000` text offset); uncached alias is `0xFF0C0000` |
| **`RESTARTSTART`** | `0x00C80000` | 512 KiB carved from `AllocateMemory` (`0x00D00000 -> 0x00C80000`, opcode `0xE3A01734 -> 0xE3A018C8` / `0xE3A01732`) |
| **`DryosDebugMsg`** | `0xFE1171B4` | Verified by `a1ex` in Topic 23369 (1300D was `0xFE11F394`, $\Delta = -\texttt{0x81E0}$) |
| **`task_create`** | `0x00003888` | Verified by `a1ex` in Topic 23369 (1300D was `0x000038FC`, $\Delta = -\texttt{0x74}$) |
| **`CURRENT_TASK`** | `0x0002F53C` | Verified by `a1ex` in Topic 23369 (1300D was `0x00031170`, $\Delta = -\texttt{0x1C34}$) |
| **`CURRENT_ISR`** | `0x0002F540` | `CURRENT_TASK + 4` |
| **`card_bootflags`** | `0x00106744` | Verified in Topic 23369 Rescue log |
| **`boot_read_sector`** | `0x00106F38` | Verified in Topic 23369 Rescue log |
| **`boot_write_sector`** | `0x00107030` | Verified in Topic 23369 Rescue log |
| **`sd_card_init`** | `0x00101DE4` | Verified in Topic 23369 Rescue log (`Card init => 2`) |
| **`PlayMovieGuideApp_handler`** | `0xFE5DDE7C` | Extracted in `critix` commit `0727054e4` |
| **`LiveViewWbApp_handler`** | `0xFE49AA14` | Extracted in `critix` commit `0727054e4` |
| **`SetCFnData`** | `0xFE71C4D0` | Extracted in `critix` commit `0727054e4` |

---

## 4. How to Re-Run the Verification Suite & Next Hardware Steps

### 4.1 Re-Run Full Mathematical & Emulation Verification Suite
```powershell
& "d:\Dev\REverSE\4000D\.venv\Scripts\python.exe" "d:\Dev\REverSE\4000D\scripts\pack_4000d_fir.py"
& "d:\Dev\REverSE\4000D\.venv\Scripts\python.exe" "d:\Dev\REverSE\4000D\scripts\emulate_dmp4000d.py"
& "d:\Dev\REverSE\4000D\.venv\Scripts\python.exe" "d:\Dev\REverSE\4000D\scripts\verify_autoexec_4000d_unicorn.py"
& "d:\Dev\REverSE\4000D\.venv\Scripts\python.exe" "d:\Dev\REverSE\4000D\scripts\prepare_4000d_rom_and_resolve_stubs.py" --self-test
```

### 4.2 Non-Destructive Physical Hardware Workflow & Progress
1. **Step 1 — Non-Destructive ROM Dump via `DMP4000D.FIR` [COMPLETED]:**
   - User ran `DMP4000D.FIR` on physical Canon EOS 4000D.
   - Result: Dumped `ROM0.BIN` (32MB), `ROM1.BIN` (32MB, 16MB SPI flash mirrored), `RESCUE.LOG`.
   - Stored in: `d:\Dev\REverSE\4000D\firmware\romdump\` and `firmware/`.
   - Verified `SIG_4000D_100 = 0x56D44DD6`.
   - Discovered camera bootflag status: `FIR=0 BOOT=0 RAM=-1 UPD=-1`.
2. **Step 2 — Automated ROM Patching & Stub Verification [COMPLETED]:**
   - Ran `prepare_4000d_rom_and_resolve_stubs.py` on physical `ROM1.BIN`.
   - Relocated 64KB boot block (block 1 -> block 511) -> `firmware/ROM1_patched.BIN`.
   - Verified all critical stubs: `cstart` (`0xFE0C3A24`), `HIJACK_CACHE_HACK_INITTASK_ADDR` (`0xFE0C3B20`), `init_task` (`0xFE1296C8`), `DryosDebugMsg` (`0xFE1171B4`), `task_create` (`0x00003888`), `current_task` (`0x0002F53C`), `FIO_OpenFile` (`0xFE2A3F9C`).
3. **Step 3 — SD Card Deployment Package [COMPLETED]:**
   - Created folder: `d:\Dev\REverSE\4000D\liveSDCard\`
   - Deployed:
     - `autoexec.bin` (Unicorn-verified minimal "Hello World" + LED blinker)
     - `autoexec_full.bin` (full Magic Lantern platform payload, 431 KB)
     - `ML/FONTS/` and `ML/CROPMKS/`
     - `DMP4000D.FIR` (portable dumper)
     - `make_bootable.py` (SD card VBR bootflag injector)
     - `README_SDCARD.txt` (operator reference guide)
4. **Step 4 — Wi-Fi PTP/IP Bootflag Activation [MILESTONE COMPLETED!]:**
   - **Crucial Finding:** DIGIC 4+ enforces HMAC-SHA1 on modified `.FIR` files (`BOOT4000.FIR` fails with *"Update file error"*). Furthermore, the 4000D menu completely removes the *"EOS Utility"* icon.
   - **Breakthrough:** Reverse-engineered the camera's native *"Connect to smartphone"* mode, which exposes standard CIPA DC-005 PTP/IP on TCP port `15740`.
   - **CRITICAL REQUIREMENT — AUTO IP (DHCP):** Camera Wi-Fi **MUST** be set to **Auto IP (DHCP)**. Setting a manual static IP caused DryOS socket/gateway state machine failure, resulting in persistent `Err 11: Connection target not found`. Switching to Auto IP resolved this instantly.
   - **Execution:** Ran `scripts/ptp_smartphone_bootflag.py 192.168.1.212`.
   - **Handshake Sequence:**
     - Connected to `192.168.1.212:15740`.
     - Emulated iPhone client (`PTPIP_INIT_COMMAND_REQ`).
     - User pressed `[OK]` on LCD prompt *"Connect to iPhone?"*.
     - Initialized event socket and opened PTP session (`0x1002`).
     - Unlocked DryOS event procedures via 3x `PTP 0x9050` (`PTP_OC_EOS_EnableEventProc`).
     - Dispatched `EnableBootDisk` via `PTP 0x9052` (`PTP_OC_EOS_ExecuteEventProc`).
     - Camera returned `0x2001 OK` and set NVRAM address `0xF8000004` to `0xFFFFFFFF` (`BOOT=1`).
5. **Step 5 — Tools & Reversibility:**
   - **Enabler:** [`scripts/ptp_smartphone_bootflag.py`](file:///d:/Dev/REverSE/4000D/scripts/ptp_smartphone_bootflag.py)
   - **Disabler:** [`scripts/ptp_smartphone_disable_bootflag.py`](file:///d:/Dev/REverSE/4000D/scripts/ptp_smartphone_disable_bootflag.py) (calls `DisableBootDisk` to restore `0xF8000004` to `0x00000000`)
   - **Full Technical Documentation:** [`docs/canon_4000d_wifi_bootflag_procedure.md`](file:///d:/Dev/REverSE/4000D/docs/canon_4000d_wifi_bootflag_procedure.md)
6. **Step 6 — Physical Autoboot & Hardware GPIO Verification [MILESTONE COMPLETED!]:**
   - User inserted prepared SD card with `BOOTDISK` / `EOS_DEVELOP` and bare-metal `autoexec.bin`.
   - **Result:** Camera bootloader successfully loaded `autoexec.bin` into RAM at `0x00800000` and executed it.
   - **Hardware MMIO Discovery:**
     - DIGIC 4 legacy Card LED (`0xC0220134`) was obsolete.
     - Reverse-engineered Canon's official GPIO driver from `ROM1.BIN` at `0xFE119020` and `0xFE3D3000`:
       - `CARD_LED_ADDRESS = 0xC022D1E0` (GPIO table index 77 / `0x4D` at `0xFE7FE250`).
       - `LEDON = 0x0093D800` (ROM1 literal at `0xFE3D3234`).
       - `LEDOFF = 0x0083DC00` (ROM1 literal at `0xFE3D3238`).
     - Display VRAM structure address verified at `0x0005339C` (from `SetBitmapVramAddress` in ROM1 at `0xFE10C380`, replacing the 1300D value `0x56240`).
   - **Physical Confirmation:** Activity LED blinks visibly on physical camera hardware every second!
   - **Clean Boot:** Removing card immediately restores 100% factory Canon UI.

7. **Step 7 — Full Magic Lantern UI Live & Interactive on Physical 4000D LCD [HISTORIC MILESTONE COMPLETED!]:**
   - **Kernel & Memory Resolution:** Corrected stubs in `platform/4000D.100/stubs.S` (`_malloc = 0xFE2934A0`, `_AllocateMemory = 0xFE11D810`, `_FreeMemory = 0xFE11DBAC`, `vsnprintf = 0xFE292FEC`, `MALLOC_STRUCT = 0x000640B4`).
   - **VRAM Display Layer:** Identified true 8-bpp On-Screen Display (OSD) palette plane at `0x53360` (`PB_BITMAP_INFO`) with 960-byte stride, active buffer at `0x2087100` (`+0x70F8`), and 720x480 resolution.
   - **WindowSystem Dirty Bit Suppression:** Overcame Canon Shooting Status OLC display overwrite by updating `WINSYS_BMP_DIRTY_BIT_NEG` to `MEM(0x3BE8C + 0x3C)` and suppressing full refresh at `0x3BE8C + 0x30` in `src/dialog_test.c`.
   - **Physical Control Verification:** Intercepted and mapped key event codes: `0x4C` (`Av / Trash` button for menu toggle), `0x0B` (`DISP`), `0x07` (`MENU`), `0x24` (`Q`).
   - **2.7" LCD Geometry:** Lifted menu help footer lines to $y=420$ and $y=442$ to prevent physical bezel clipping.
   - **Build Hash:** `autoexec.bin` SHA-256 `D0E361E594E67F166F75DE0CC41BC03098063780433978DCEF026C103F36F7B0` (404,256 bytes).
   - **Hardware Photographic Verification:** User confirmed Shoot, Debug, Display, and Customized Buttons menus rendering cleanly on physical camera LCD.
8. **Step 8 — LiveView Framebuffer Mapping, Automated EDMAC Engine & Dynamic Modules [MILESTONE COMPLETED!]:**
   - **LiveView YUV Framebuffer & Display State Object:** Reverse engineered `DISPLAY_STATEOBJ` in `ROM1.BIN` at `0x0002FBD4`. Mapped the active LiveView YUV422 raster pointer dynamically dereferenced at `(*(uint32_t*)(0x2FBD4 + 0xB0))` and orientation at `MEM(0x2FBD4 + 0x7C)`. This fixes LiveView overlays (Zebras, Focus Peaking, and real-time Histograms) which previously read stale uninitialized memory (`0x318C8`).
   - **Automated EDMAC Reverse-Engineering Tool:** Created [`scripts/automate_edmac_mapping.py`](scripts/automate_edmac_mapping.py) using Capstone. Disassembles all 124 EDMAC callsites in `ROM1.BIN` and automatically derives EDMAC write/read channels, registers (`0xC0F04208`, `0xC0F04308`), state objects, and SRM raw buffer allocation pools (`0x01F68000` = 31.4 MB) in under 3 seconds.
   - **Export Symbol Generator (`generate_sym.py`):** Created automated symbol table generator extracting 1,322 resolved kernel stubs and core functions from `magiclantern` ELF to produce `liveSDCard/ML/MODULES/t100_100.sym`.
   - **Dynamic Module Architecture:** Modernized module build tools (`readme2modulestrings.py`, `checkdep.py`) to pure Python 3. Compiled and deployed 10 functional `.mo` modules to `liveSDCard/ML/MODULES/` (`bench.mo`, `dual_iso.mo`, `edmac.mo`, `ettr.mo`, `file_man.mo`, `mlv_lite.mo`, `pic_view.mo`, `raw_diag.mo`, `selftest.mo`, `silent.mo`).
   - **Zero PII & Open-Source Push:** Stripped all host metadata from build tools and `Makefile.src`. Committed and pushed clean codebase, patch `patches/0001-4000D-Port-Magic-Lantern-to-Canon-EOS-4000D-Rebel-T1.patch`, and binaries to public GitHub repository: `https://github.com/cdrivex4/ml-4000d.git`.
   - **Release Binary Checksums:**
     - `liveSDCard/autoexec.bin` (404,384 bytes): MD5 `F8911C0EC5D7B13B805CC29FBD76390B`, SHA-256 `22283EF5464136F62E9B0F2C57DF30F273484F753BD569E09ECC1D56F2DFB8A6`.
     - `liveSDCard/ML/MODULES/t100_100.sym` (34,815 bytes): MD5 `866643AF8B5DC59E1375D07BE1E07449`, SHA-256 `4D7C175DE1CA7555292478A45256E969628037FB008338B0B2FAA9A4AD26E019`.
