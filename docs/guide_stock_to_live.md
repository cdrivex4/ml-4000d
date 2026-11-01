# Canon EOS 4000D / Rebel T100 / EOS 3000D: Stock to Live Magic Lantern Guide

**Document ID:** `DOC-ML-4000D-STOCK-TO-LIVE`  
**Target Hardware:** Canon EOS 4000D / Rebel T100 / EOS 3000D (Model ID `0x80000422`, DIGIC 4+ ARM946E-S)  
**Firmware Baseline:** Version `1.0.0` (DryOS 2.3 `#0058+p7`)  
**Safety Guarantee:** 100% Volatile RAM Execution (`#undef CONFIG_PROP_REQUEST_CHANGE`). Zero flash ROM writes. Removing the SD card immediately restores pure factory Canon firmware.

---

## 1. Prerequisites & Equipment

1. **Camera:** Canon EOS 4000D / Rebel T100 / 3000D running official firmware `1.0.0`.
2. **SD Card:** Standard SD/SDHC card $\le 32\text{ GB}$ formatted as FAT32 (exFAT $\ge 64\text{ GB}$ support is currently in development; see [`docs/exfat_roadmap_and_verification.md`](file:///d:/Dev/REverSE/4000D/docs/exfat_roadmap_and_verification.md)).
3. **Computer / Card Reader:** PC with an SD card reader and Python 3.x.
4. **Local Wi-Fi Connection:** Camera and PC connected to the same Wi-Fi network (or direct smartphone hotspot mode).

---

## 2. Step-by-Step Procedure

### Step 1: Enable the Camera Bootflag Safely via Wi-Fi PTP/IP
Because the 4000D firmware validates HMAC-SHA1 signatures on `.FIR` files, standard FIR-based bootflag installers fail with *"Update file error"*. Instead, we use Canon's standard PTP/IP interface to enable bootdisk support via DryOS Event Procedures:

1. On the camera, open the Canon menu and navigate to **Wi-Fi function**.
2. Select **Connect to smartphone** and choose **Auto IP (DHCP)** (Note: Do not use manual static IP; DryOS requires DHCP for proper routing).
3. Connect the camera to your local Wi-Fi network (or connect your PC directly to the camera's access point).
4. Note the camera's IP address (e.g., `192.168.1.xxx`).
5. Run the provided Python activation script:
   ```bash
   python scripts/ptp_smartphone_bootflag.py 192.168.1.xxx
   ```
6. When prompted on the camera LCD (*"Connect to smartphone?"*), press **[OK]**.
7. The script performs the DC-005 PTP/IP handshake, enables event procedures (`PTP 0x9050`), and calls `EnableBootDisk` (`PTP 0x9052`). The camera returns `0x2001 OK`.
8. Turn the camera off.

> [!NOTE]
> This sets the persistent bootflag (`BOOT=1`). If you ever wish to disable this flag in the future, run:
> ```bash
> python scripts/ptp_smartphone_disable_bootflag.py 192.168.1.xxx
> ```

---

### Step 2: Prepare the SD Card
Canon's bootloader inspects the master boot record / volume boot record for specific Magic Lantern markers before loading `autoexec.bin`:

1. Format the SD card ($\le 32\text{ GB}$) as **FAT32**.
2. **Using the Bundled Windows GUI Utility (`EOScard`):**
   - Launch [`tools/card_prep/EOScard.exe`](tools/card_prep/) (authored by Pel, [https://pel.hu/eoscard/](https://pel.hu/eoscard/)).
   - Select your SD card drive letter.
   - Verify that **BOOTDISK** and **EOS_DEVELOP** are checked.
   - Click **Save**.
   - > [!WARNING]
     > **Do NOT use the online download buttons inside EOScard!** Those buttons fetch generic ML builds for older models (550D/60D). If an `autoexec.bin` is placed on your card by EOScard, delete it or overwrite it with our custom 4000D binary in Step 3.
3. **Using the Bundled Cross-Platform Python Script (Linux / macOS / Windows):**
   - Run from terminal:
     ```bash
     python scripts/make_bootable.py <DRIVE_LETTER_OR_DEVICE>
     ```
4. Alternatively, on Linux/macOS using raw `dd`:
   ```bash
   echo -n "EOS_DEVELOP" | dd of=/dev/sdX bs=1 seek=64 count=11 conv=notrunc
   echo -n "BOOTDISK"    | dd of=/dev/sdX bs=1 seek=76 count=8 conv=notrunc
   ```

---

### Step 3: Install Magic Lantern Files & The 3-Stage Sync Discipline
When deploying builds and pulling logs, the order of operations is critical:

1. **Pull Logs Before Writing (Stage 1):**
   - If the camera previously ran, it created logs (`BOOT.LOG`, `DIAGS.LOG`, `BUTTONS.LOG`) in the root.
   - **Never run a blind sync (like `robocopy /PURGE`)** before copying those logs to your PC; otherwise, the crash dumps and diagnostics will be wiped!
   - Our launcher [`liveSDCard/Sync-SDCard.ps1`](liveSDCard/Sync-SDCard.ps1) (or `doit.bat`) handles this automatically by pulling and archiving logs first.
   - User photos in `DCIM/` are strictly preserved and never modified.
2. **Push & Verify Payload (Stage 2):**
   - Copy [`liveSDCard/autoexec.bin`](liveSDCard/autoexec.bin) (SHA-256: `D0E361E594E67F166F75DE0CC41BC03098063780433978DCEF026C103F36F7B0`) to the root of the SD card.
   - Copy the complete [`liveSDCard/ML/`](liveSDCard/ML/) directory to the root of the SD card.
   - Verify that the card's `autoexec.bin` matches the SHA-256 hash of the repo build to ensure no stale cached binary is booted.
3. **Archive Old Logs on Card (Stage 3):**
   - Old logs on the card are moved into `ML/LOGS/archive/` so that the subsequent camera boot starts with clean timestamps.
4. **Safely Eject (Stage 4):**
   - Always safely unmount/eject the SD card before removing it from the PC. Dirty FAT32 volume flags will cause the camera bootloader to skip `autoexec.bin`.
5. Your SD card root structure should look like:
   ```
   W:\
   ├── autoexec.bin
   └── ML/
       ├── FONTS/
       │   └── ...
       ├── SETTINGS/
       └── LOGS/
   ```

---

### Step 4: Booting & Operating the Camera
1. Ensure the camera battery is charged.
2. Insert the prepared SD card into the 4000D and close the battery/card door.
3. Turn the power switch to any shooting mode (e.g. `M`, `P`, `Av`, `Tv`).
4. The red Card Activity LED will pulse as `autoexec.bin` executes the ARM946E-S cache lockdown and initializes Magic Lantern in RAM.
5. Within ~2 seconds, the camera will start normally.

### Step 5: Opening & Navigating the Magic Lantern Menu
Due to the simplified button layout of the 4000D, physical buttons are mapped as follows:
- **Open / Close ML Menu:** Press the **`Av / Trash`** button (or press **`DISP`** depending on menu context).
- **Navigate Items:** Use the **Directional Pad** (Up / Down / Left / Right).
- **Toggle / Edit Value:** Press the **`Q` (Quick Control)** button or turn the Main Dial.
- **Select Submenu / Action:** Press **`SET`**.

---

## 3. Contributing, Mainline Alignment & Issue Tracking

- **Public Repository:** [https://github.com/cdrivex4/ml-4000d](https://github.com/cdrivex4/ml-4000d)
- **Bug Reporting & Support:** All bug reports, logs, and feature requests should be submitted directly to the [GitHub Issues tracker](https://github.com/cdrivex4/ml-4000d/issues) for collaborative tracking.
- **Upstream Collaboration:** We are committed to collaborating with the upstream Magic Lantern development team to help merge and validate the 4000D / Rebel T100 / 3000D target into the official mainline trees. Please note that hardware validation can only be confirmed for the specific physical EOS 4000D (FW 1.0.0) hardware in our test environment.

---

## 4. Credits & Acknowledgments

This port would not have been possible without the pioneering engineering of the Magic Lantern and CHDK communities:
- **Alex Dumitrache (`@a1ex`)**: Reverse engineered the portable ROM dumper (`DMP4000D.FIR`), established early QEMU-EOS models, and laid the foundations of modern DryOS reverse engineering.
- **Petabyt**: Author of the reference 1300D port (`petabyt/magiclantern`), the ARM946E-S cache lockdown bootloader shim, and the low-RAM trampoline jump architecture.
- **`@names_are_hard` (`reticulatedpines`)**: Mainline Magic Lantern architect, maintainer of QEMU-EOS, and author of comprehensive DIGIC reverse engineering documentation.
- **`ccritix`**: Contributed initial 4000D platform definitions and makefiles.
- **Trammell Hudson**: Original creator and architect of Magic Lantern (2009).
- **CHDK Community**: Pioneered DIGIC reverse engineering, state object analysis, and hardware register mappings.
