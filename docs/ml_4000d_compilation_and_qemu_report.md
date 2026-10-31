# Canon EOS 4000D (Rebel T100 / 3000D) — Architecture, QEMU-EOS Machine & ML Build Verification Report

**Author:** Antigravity Reverse Engineering Team  
**Date:** 2026-10-25  
**Workspace:** `d:\Dev\REverSE\4000D`  
**Target Hardware:** Canon EOS 4000D / Rebel T100 / EOS 3000D  
**Model ID:** `0x80000422` (`0x422`)  
**Core Processor:** DIGIC 4+ (ARM946E-S / ARMv5TE architecture)  
**Toolchain:** xPack GNU Arm Embedded GCC 13.3.1-1.1 (`d:\Dev\REverSE\4000D\tools\xpack-arm-none-eabi-gcc-13.3.1-1.1\bin`)  
**Build System:** GNU Make 4.2.1 (`D:\Qt\Tools\mingw1310_64\bin\mingw32-make.exe`)

---

## 1. Executive Summary

This engineering investigation audited the `critix-4000d` branch, identified critical omissions in the original 1300D clone, resolved the 32MB ROM relative-branch trampoline and DryOS task structure guards across `src/`, brought `qemu-eos` up to full parity with verified 4000D hardware constants, and successfully built **both** the minimal test payload and the full Magic Lantern platform build for the Canon EOS 4000D.

---

## 2. In-Depth Audit of `critix` 4000D Commits & Core `src/` Guards

### 2.1 Commit Audit (`critix` Commits `056778668` & `0727054e4`)
- **Initial Clone (`056778668`):** Blindly duplicated `platform/1300D.110/` to `platform/4000D.100/`.
- **Partial Stub Update (`0727054e4`):**
  - Updated FIR metadata (`CANON_NAME_FIR = 4000D100.FIR`, `FIRMWARE_ID = 0x80000422`).
  - Disabled persistent properties (`#undef CONFIG_PROP_REQUEST_CHANGE`).
  - Added RAW dynamic ranges: `{1073, 1082, 1042, 1002, 926, 837, 728, 642}`.
  - Adjusted a small set of GUI handlers (`PlayMovieGuideApp_handler = 0xFE5DDE7C`, `SetCFnData = 0xfe71c4d0`, `LiveViewWbApp_handler = 0xFE49AA14`).
- **Critical Vulnerability Uncovered:**
  - `critix` left core OS stubs pointing to 1300D firmware addresses (`DryosDebugMsg = 0xFE11F394`, `current_task = 0x31170`, `task_create = 0x38FC`).
  - Verification against `a1ex`'s physical hardware execution (`DMP4000D.FIR` rescue dumper) confirmed non-uniform offsets:
    - `DebugMsg`: `0xFE1171B4` (shift: `-0x81E0`)
    - `task_create`: `0x00003888` (shift: `-0x74`)
    - `current_task`: `0x0002F53C` (shift: `-0x1C34`)

### 2.2 Core `src/` Guard Resolution (32MB ROM Trampoline & DryOS 2.3 Task Structures)
Because the 4000D shares the atypical single 32MB SPI flash architecture (`0xFE0C0000` text section) and DryOS 2.3 p39 kernel with the 1300D, the relative jump range of ARM `B`/`BL` instructions ($\pm 32\text{ MB}$) is exceeded when jumping between RAM AllocateMemory pool (`0xC80000`) and upper flash (`0xFE0C0000`). The 1300D uses a 2-stage trampoline (`patch_instruction_jump` / `patch_jump_vector`) and extended `struct task` with `uint32_t unknown_08` at offset `0x44`.

The following files were patched so `CONFIG_4000D` receives identical treatment:
1. **`src/boot.h` (Line 117):** Guarded dynamic `patch_jump_vector` allocation with weak symbol safety:
   ```c
   #if defined(CONFIG_1300D) || defined(CONFIG_4000D)
       extern uint32_t  patch_jump_size __attribute__((weak));
       extern uint32_t *patch_jump_vector __attribute__((weak));
       extern void * _malloc( size_t len ) __attribute__((weak));
       if (&patch_jump_size && &patch_jump_vector && _malloc)
       {
           patch_jump_vector = (uint32_t*)_malloc(patch_jump_size);
           qprintf("[BOOT] %s allocating jump vector size = %d at = %lx\n", CAMERA_MODEL, patch_jump_size, patch_jump_vector);
       }
   #endif
   ```
2. **`src/patch.h` (Line 159):** Declared `patch_instruction_jump` for `CONFIG_4000D`.
3. **`src/patch.c` (Lines 78, 537, 597, 1006, 1046, 1078, 1497):**
   - Enabled `jump_vector` array and `patch_instruction_jump` implementation.
   - Bypassed 32MB jump range assertion in `patch_hook_function` for 4000D.
   - Handled double-jump unpatching and `patch_simple_init` vector alignment.
4. **`src/tasks.h` (Lines 34, 99, 130, 155):**
   - Declared `get_task_info_by_id` and `_get_task_info_by_id`.
   - Included `uint32_t unknown_08` field at `0x44` in `struct task`.
   - Configured `struct task_attr_str` member order (`char *name` at `0x34`).
5. **`src/flexinfo.c` (Line 387):** Enabled 4000D OLC display entries.
6. **`src/fps-engio.c` (Line 1000):** Included 4000D in movie FPS toggle sequence.
7. **`src/raw.c` (Lines 155, 188, 222, 452, 535, 1041):**
   - Configured `DEFAULT_RAW_BUFFER` (`MEM(MEM(0x37930 + 0x30))`, 8MB).
   - Configured `RAW_LV_EDMAC` (`0xC0F26008`) and `RAW_PHOTO_EDMAC` (`0xC0F04208`).
   - Defined `CAM_COLORMATRIX1` and `dynamic_ranges: {1073, 1082, 1042, 1002, 926, 837, 728, 642}`.
   - Made `_raw_lv_get_iso_post_gain()` available unconditionally.

---

## 3. Platform Definition Synchronization (`platform/4000D.100`)

Both repositories (`magic-lantern-1300d` and `magic-lantern`) contain:
- **`Makefile.platform.default`:**
  - `ROMBASEADDR = 0xFE0C0000`, `PLATFORM_ARCH = armv5te`, `FIRMWARE_ID = 0x80000422`, `CANON_NAME_FIR = 4000D100.FIR`.
  - `RESTARTSTART = 0xC80000`, `ML_BOOT_OBJ = boot-d45-ch.o`, `ML_SRC_EXTRA_OBJS += function_overrides.o`.
- **`platform/4000D.100/Makefile`:** Corrected `MODEL=4000D`.
- **`internals.h` & `gui.h`:**
  - `#undef CONFIG_PROP_REQUEST_CHANGE` (zero persistent writes).
  - `#define CONFIG_MENU_WITH_AV` (mapped for 4000D body without dedicated trash button).
- **`consts.h`:** Added `SRM_BUFFER_SIZE = 0x1F68000` (18MP raw buffer), `DISPLAY_BATTERY_POS_X/Y`, `DISPLAY_DATE_POS_X/Y`.
- **`stubs.S`:**
  - `firmware_entry = 0xFE0C0000`
  - `DryosDebugMsg = 0xFE1171B4`
  - `current_task = 0x2F53C`
  - `task_create = 0x3888`
  - `card_bootflags = 0x106744`
  - `boot_read_sector = 0x106F38`
  - `boot_write_sector = 0x107030`
  - `sd_card_init = 0x101DE4`
  - `PlayMovieGuideApp_handler = 0xFE5DDE7C`
  - `LiveViewWbApp_handler = 0xFE49AA14`
  - `SetCFnData = 0xfe71c4d0`

---

## 4. QEMU-EOS 4000D Machine Definition (`qemu-eos`)

On branch `2000d_test`:
1. **`hw/eos/model_list.h`:** Defined `MODEL_NAME_4000D "4000D"`.
2. **`hw/eos/model_list.c`:** Registered 4000D machine with `rom0_size = 0x0`, `rom1_size = 0x02000000` (32MB), `firmware_start = 0xFE0C0000`, `current_task_addr = 0x2F53C`.
3. **`hw/eos/eos.c`:**
   - Registered `eos_4000D_machine_init` & `DEFINE_MACHINE(MODEL_NAME_4000D, ...)`.
   - In `eos_rom_write`: Return SPI flash model ID `0x003825C2` (Macronix MX25L25635E).
   - In GPIO `0xF48C`: Added 4000D to system check bypass.
4. **`hw/eos/engine.c` & `hw/eos/mpu.c`:**
   - Added 4000D to JPCORE bypass (`0x1010000`) and interrupt handling (`0x400`).
   - Linked MPU spell set to 600D and button codes to 1200D.

---

## 5. Binary Artifacts & Verification

Both targets were compiled cleanly using the portable toolchain and copied to `d:\Dev\REverSE\4000D\firmware\`:

| Artifact | File Path | Size | MD5 | SHA-256 |
|---|---|---|---|---|
| **Minimal Target** | `firmware/autoexec_4000d_minimal_hello.bin` | `6,496 bytes` | `2C74CEA720B566CCC96155DACD18CB22` | `4946ED587048FE0BD3C88E95E541FCB22CFDA136426294B3395FDB853718B0E8` |
| **Full ML Target** | `firmware/autoexec_4000d_full.bin` | `431,072 bytes` | `C1F71E993D86D0D3CAA3BA1595D23576` | `D73C317ED281DDF6CA1D353050E7220D60A711C61EF529AF0F968F1B5D9FB98E` |

### Disassembly & Structure Verification
- **Boot Preambles:** Both binaries feature the ARM/Thumb polyglot preamble (`0x46c0 / 0xe001 / 0xea000000 / 0xf000 e800`) executing `xor_check`.
- **Reset Vector:** Embedded vector at offset `+0x28` points to `ROMBASEADDR` `0xFE0C0000`.
- **Heap Allocation Patch:** Both binaries contain the `0xe3a01732` instruction (`mov r1, #0xc80000`) dynamically patching Canon's AllocateMemory pool in ITCM cache.
- **Full Payload Size:** `magiclantern.bin` is `427,444 bytes`, packing the complete suite of ML menus, raw video engines, debug tools, and TCC runtime.
