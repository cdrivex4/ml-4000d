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

## 4. Total Reversal: Restoring 100% Factory Canon Operation

To return the camera to its absolute factory state:
1. **Temporary:** Simply insert a standard, unbootable SD card (or format the current card as standard FAT32 without the `EOS_DEVELOP` marker). The camera will ignore `autoexec.bin` and boot standard Canon firmware.
2. **Permanent Bootflag Removal (Optional):**
   Connect the camera to Wi-Fi in smartphone mode and run:
   ```bash
   python scripts/ptp_smartphone_disable_bootflag.py 192.168.1.xxx
   ```
   This clears the persistent bootflag (`BOOT=0`).
