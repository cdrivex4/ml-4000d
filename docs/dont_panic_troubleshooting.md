# The "Don't Panic" Guide — Safe Failure Modes & Recovery on Canon EOS 4000D

**Document ID:** `DOC-ML-4000D-DONT-PANIC`  
**Target Platform:** Canon EOS 4000D / Rebel T100 / EOS 3000D (DIGIC 4+, Firmware 1.0.0)

---

## 1. The Core Invariant: Why You Cannot Brick Your Camera

The single most important principle of this Magic Lantern port is:
> **100% Volatile RAM Execution (`#undef CONFIG_PROP_REQUEST_CHANGE`)**

- **Zero Flash Writes:** The Magic Lantern payload never modifies, erases, or flashes the camera's internal ROM (`ROM0` or `ROM1`).
- **RAM-Only Lifecycle:** `autoexec.bin` is read from the SD card into temporary SDRAM at camera startup. Every hook, menu structure, and patch exists exclusively in volatile memory.
- **Instant Clean Recovery:** If anything goes wrong, removing the SD card or flipping the SD write-protect switch cuts off the payload completely. On power-on, the camera boots 100% untouched factory Canon firmware.

---

## 2. The Golden Rule: The 5-Second Battery Pull

If the camera ever locks up, refuses to wake from sleep, or experiences an unhandled DryOS exception:
1. Turn the power switch to **OFF**.
2. Open the battery door and **remove the battery**.
3. Wait **5 seconds** for all internal capacitors to drain.
4. Reinsert the battery and turn the camera back **ON**.

Because no non-volatile flash was altered, a battery pull completely clears the camera's SDRAM state.

---

## 3. Common "Don't Panic" Scenarios & Fixes

### Scenario A: Screen Remains Black, No Card Activity LED
- **Cause 1:** SD card lock switch is in the "Lock" position. Flip it back to read-write.
- **Cause 2:** Card/battery door is not fully latched (the physical microswitch at the door cut-off disconnects the main power rail).
- **Cause 3:** Battery voltage is below the minimum threshold. Charge the LP-E10 battery.

---

### Scenario B: Red LED Blinks Continuously or Freezes on Boot
- **Cause:** The camera's bootloader detected the `BOOTDISK` flag on the card, but failed to load or validate `autoexec.bin`.
- **Fix:**
  1. Remove the SD card and insert it into your computer.
  2. Verify that `autoexec.bin` is located directly in the root directory (not inside a subfolder).
  3. Verify the file size and SHA-256 checksum against the verified release table.
  4. If the card was improperly unmounted, run a filesystem check (`chkdsk` on Windows or `fsck.vfat` on Linux) to clear dirty volume flags.

---

### Scenario C: Camera Crashes After Changing an Experimental Setting
- **Cause:** A corrupt or incompatible setting was saved to disk.
- **Fix:**
  1. Insert the SD card into your computer.
  2. Navigate to `ML/SETTINGS/`.
  3. Delete all `.CFG` and `.SET` files (or delete the entire `SETTINGS` folder).
  4. Reinsert the card into the camera. Magic Lantern will regenerate all settings with safe factory defaults.

---

### Scenario D: "Camera Was Not Shut Down Cleanly — Skipping Module Loading"
- **Cause:** If the camera battery was removed while running, a temporary lock file (`ML/MODULES/LOADING.LCK`) was left on the card. To protect the camera from crash-loops, Magic Lantern displays this warning and bypasses module loading.
- **Fix:** This is completely harmless. On the next clean shutdown, the lock file is automatically cleared. You can also manually delete `ML/MODULES/LOADING.LCK` on your computer.

---

### Scenario E: Canon Shooting Status Bar (OLC) Flashes Over the ML Menu
- **Cause:** Canon's `gui_main_task` attempted to refresh the background exposure screen.
- **Fix:** In our verified build, WindowSystem dirty bits at `*(0x3BE8C + 0x3C)` and `+0x30` are suppressed. If this occurs after switching shooting modes, simply press the `Av/Trash` button to toggle the menu off and back on.

---

### Scenario F: Canon "Err 70" (Shooting Engine & Task Watchdog Timeout)
- **What it looks like:** The LCD displays a standard Canon error screen: `"Err 70: Shooting is not possible due to an error. Turn the camera off and on again or re-install the battery."`
- **What causes it:**
  1. **CPU Spin-Loop Starvation:** Early bootloader spin-loops (`boot-d45-ch.c` or blocking LED delay loops) stalled the CPU for $> 5\text{ seconds}$ before Canon's `init_task` finished setting up peripherals, tripping the MPU communication watchdog.
  2. **DryOS Task Deadlocks:** A task took a semaphore without releasing it, or an invalid stub jumped into mid-instruction space, causing a core DryOS task (`gui_main_task`, `JobMgr`, `DispSwCon`) to freeze.
  3. **Heap Header Corruption:** Calling misidentified memory functions (like the internal 2-argument `AllocateMemory_pool` instead of `_AllocateMemory`) corrupted the `MALLOC_STRUCT` (`0x000640B4`) chunk table.
- **How to recover:**
  - **Err 70 is 100% volatile.** Turn the camera OFF, perform the 5-second battery pull, and reinsert.
  - If developing new code: avoid long busy-wait loops during startup, ensure all semaphores and locks balance, and verify all memory stubs.
  - If you remove the SD card, the camera will immediately boot standard Canon firmware without error.

---

### Scenario G: Canon "Err 11" (Connection Target Not Found during Wi-Fi PTP Setup)
- **What it looks like:** During Step 1 of the bootflag setup in "Connect to smartphone" mode, the camera screen displays `"Err 11: Connection target not found"`.
- **What causes it:** The camera was configured with a **Manual Static IP** address. Canon DryOS's internal socket and routing state machine fails to bind properly without a dynamic DHCP handshake.
- **How to fix:**
  1. Go into Canon Menu -> **Wi-Fi function**.
  2. Change the IP address setting from Manual to **Auto IP (DHCP)**.
  3. Reconnect to your Wi-Fi network. The camera will immediately acquire a valid lease and allow [`scripts/ptp_smartphone_bootflag.py`](../scripts/ptp_smartphone_bootflag.py) to connect without error.

---

### Scenario H: "Update file error" when Selecting `.FIR` in Canon Firmware Menu
- **What it looks like:** The camera detects an update file on the SD card, begins reading it, and immediately aborts with the message `"Update file error"`.
- **What causes it:** The DIGIC 4+ bootloader enforces strict HMAC-SHA1 cryptographic signature verification on `.FIR` containers. Modified FIR files (like `BOOT4000.FIR`) fail validation because the private HMAC key is held exclusively by Canon.
- **How to fix:**
  - Do **not** attempt to flash custom or modified `.FIR` files.
  - We bypass FIR flashing entirely by enabling the camera's bootdisk flag over Wi-Fi PTP/IP using Canon's built-in, authorized event procedures (`PTP 0x9050` / `0x9052`).

---

### Scenario I: Red Activity LED Pulses 5 Times and Freezes (The Post-5-Blink Crash)
- **What it looks like:** On power-on, the card activity LED blinks 5 distinct times (Cache lockdown -> Init task -> ML Init), but the LCD never turns on, and the camera freezes.
- **What causes it:** A deterministic crash in `my_big_init_task` caused by unported stubs:
  - `_AllocateMemory` mapped to the 2-argument pool function `0xFE11D6A0` (treated `size` as a struct pointer -> Data Abort).
  - `_malloc` (`0xFE2C6BAC` from 1300D) jumping into mid-instruction code.
  - `vsnprintf` (`0xFE2BC8A4` from 1300D) executing coprocessor instruction `cdp2 p3...` -> Undefined Instruction abort.
- **How to fix:** Ensure you are running our verified release binary [`liveSDCard/autoexec.bin`](../liveSDCard/autoexec.bin) (SHA-256: `D0E361E594E67F16...`), where all 4000D stubs are corrected.

---

### Scenario J: Debug Strings Overlaying the Screen ("No submenu, fall back to edit mode")
- **What it looks like:** White monospace debug text overlays the Canon shooting display or ML menus.
- **What causes it:** Magic Lantern's `module_load_symbols()` failed to locate `t100_100.sym` on the SD card and automatically called `console_show()`. Once `console_visible = 1`, all internal `printf()` calls are printed directly onto the active VRAM bitmap layer.
- **How to fix:** This is completely neutralized in our verified build by setting `module_autoload_disabled = 1` and sleeping `console_task`. If modifying source, ensure `console_show()` is not triggered on missing symbol files.

---

## 4. Total Reversal: Restoring 100% Factory Canon Operation

To return the camera to its absolute factory state:
1. **Temporary:** Simply insert a standard, unbootable SD card (or format the current card as standard FAT32 without the `EOS_DEVELOP` marker). The camera will ignore `autoexec.bin` and boot standard Canon firmware.
2. **Permanent Bootflag Removal (Optional):**
   Connect the camera to Wi-Fi in smartphone mode and run:
   ```bash
   python scripts/ptp_smartphone_disable_bootflag.py 192.168.1.xxx
   ```
   This clears the persistent bootflag (`BOOT=0`).
