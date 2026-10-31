# Canon EOS 4000D / Rebel T100 / EOS 3000D (DIGIC 4+)
## Wi-Fi PTP/IP Magic Lantern Bootflag Enablement Guide & Technical Writeup

**Target Camera:** Canon EOS 4000D / EOS Rebel T100 / EOS 3000D  
**Model ID:** `0x80000422` (`0x422`)  
**Architecture:** DIGIC 4+ (ARM946E-S core)  
**Firmware Version:** 1.0.0  
**Target Bootflag Address:** NVRAM `0xF8000004` (`BOOT=1` -> `0xFFFFFFFF`, `BOOT=0` -> `0x00000000`)  
**Payload File:** `autoexec.bin` loaded from FAT32 SD card at boot  

---

## Executive Summary

On older Canon DSLRs (DIGIC 2, 3, 4, 5), Magic Lantern was historically installed by loading an unofficial `.FIR` update file via the Canon menu, which executed an in-memory installer to flip the camera's persistent bootflag in NVRAM.

On the **EOS 4000D (DIGIC 4+)**, Canon implemented strict HMAC-SHA1 signature verification for firmware update packages. Custom `.FIR` installers fail signature validation with a yellow screen error: `"Update file error. Please check the memory card and reload the battery"`.

This guide documents the **Wi-Fi PTP/IP Exploit & Event Procedure Execution Method** that permanently enables the Magic Lantern bootflag **without touching Canon ROM or needing a signed FIR**.

---

> [!CRITICAL]
> ### MANDATORY CAMERA WI-FI SETTING: AUTO IP (DHCP) ONLY
>
> When configuring the camera Wi-Fi connection to your home network / access point:
> - **MUST USE: "Auto setting" (DHCP)**
> - **DO NOT USE: "Manual setting" (Static IP)**
>
> **Technical Reason / DryOS Failure Analysis:**  
> When the EOS 4000D network stack is configured with a **Manual IP**, Canon's internal DryOS networking subsystem fails to complete its gateway routing and socket binding state transitions. The pairing daemon fails to initialize listener handles properly, repeatedly throwing **`Err 11: Connection target not found`** on the LCD screen, even when pingable.
>
> When configured with **Auto setting (DHCP)**, DryOS completes DHCP lease negotiation, binds TCP port `15740` cleanly, activates SSDP/UPnP discovery, and transitions smoothly into the pairing approval state where the prompt `"Connect to iPhone?"` appears on screen.

---

## Technical Background: Why Previous Methods Failed

### 1. FIR HMAC-SHA1 Signature Verification
The EOS 4000D bootloader and DryOS firmware update routines verify cryptographic signatures against Canon's internal public keys in `ROM0`/`ROM1`. The `DMP4000D.FIR` memory dumper (which had a valid signature or exploited an older unpacker vulnerability) succeeded in dumping memory, but modified FIR files (`BOOT4000.FIR`) were immediately rejected by hardware with an error.

### 2. Physical USB Port & Cable Bottlenecks
Standard Canon DSLRs support USB PTP via mini-USB. However, many consumer mini-USB cables lack data lines (charge-only), and driver conflicts with Windows MTP drivers frequently prevent raw PTP framing over USB.

### 3. The 4000D Wi-Fi Menu Anomaly
Higher-tier Canon bodies (e.g. 70D, 80D, 1300D) have an explicit **"Connect to EOS Utility"** option in their Wi-Fi function menu. The budget EOS 4000D **completely removes the EOS Utility icon**, offering only 4 options:
1. Transfer images between cameras
2. **Connect to smartphone**
3. Print from Wi-Fi printer
4. Upload to Web service

### 4. Reverse Engineering "Connect to smartphone"
By analyzing the DryOS network task binaries in `ROM1.BIN`, we confirmed that the **"Connect to smartphone"** service uses the standard **CIPA DC-005 PTP/IP protocol on TCP port 15740**, identical to Canon Camera Connect on iOS and Android. By emulating a smartphone client, we can open a full PTP command channel directly to the camera's event procedure engine.

---

## PTP/IP Exploit Mechanism

### Step 1: PTP/IP Command Handshake
The client establishes a TCP connection to `camera_ip:15740` and transmits `PTPIP_INIT_COMMAND_REQ`:
- Packet Length: 42 bytes (`0x2A`)
- Packet Type: `0x00000001` (`PTPIP_INIT_COMMAND_REQ`)
- Client GUID: 16-byte UUID (`42400001-dead-beef-cafe-babe00000001`)
- Client Friendly Name: UTF-16LE string `"iPhone\0"`
- PTP/IP Version: `0x00010000` (1.0)

Once transmitted, the camera screen displays:
```
Connect to iPhone?
[Cancel]   [OK]
```
The user presses **[OK] / [SET]** on the camera. The camera responds with `PTPIP_INIT_COMMAND_ACK` containing the dynamic Connection ID.

### Step 2: Event Channel Handshake
The client opens a second TCP connection to `camera_ip:15740` and transmits `PTPIP_INIT_EVENT_REQ` with the Connection ID received in Step 1. The camera acknowledges with `PTPIP_INIT_EVENT_ACK`.

### Step 3: PTP Session Initialization
The client issues standard PTP command `OpenSession` (`0x1002`) with Session ID `1`. The camera responds with `0x2001` (`PTP_RC_OK`).

### Step 4: Canon Event Procedure Unlock Sequence
Canon DryOS restricts internal debug procedures. In Canon firmware, vendor opcode `0x9050` (`PTP_OC_EOS_EnableEventProc`) must be called **3 consecutive times**:
- Call 1: `PTP 0x9050` (TID: 2) -> Response `0x2005` (Access Denied / Unlocking)
- Call 2: `PTP 0x9050` (TID: 3) -> Response `0x2005` (Unlocking)
- Call 3: `PTP 0x9050` (TID: 4) -> Response `0x2005` (Procedure table unlocked!)

### Step 5: Executing `EnableBootDisk`
Once unlocked, opcode `0x9052` (`PTP_OC_EOS_ExecuteEventProc`) allows arbitrary execution of registered ROM functions by name.
We pass payload:
```c
"EnableBootDisk\0" + 8 bytes of zero padding (arguments)
```
The camera executes `EnableBootDisk`:
- Accesses camera EEPROM/NVRAM at address `0xF8000004`.
- Overwrites `0x00000000` with `0xFFFFFFFF` (`-1`).
- Returns PTP response `0x2001` (`PTP_RC_OK`).

The bootflag is now **permanently set to 1 in camera NVRAM**.

---

## Step-by-Step Instructions

### Phase 1: Camera Wi-Fi Setup
1. Turn on the EOS 4000D.
2. In the Menu, navigate to **Wi-Fi / NFC** -> Enable.
3. Select **Wi-Fi function**.
4. Select the second icon: **Connect to smartphone**.
5. Select **Review/change settings** -> **Change set.** -> **Connect to Wi-Fi network**.
6. Select **Find network** and connect to your 2.4 GHz home Wi-Fi access point (enter your password).
7. **CRITICAL STEP:** When prompted for IP Address setting:
   - Select **Auto setting** (DHCP).
   - **DO NOT choose Manual setting.**
8. Note the camera's assigned IP address (e.g. `192.168.1.212`) from your router's client list or the camera screen.
9. When the screen displays *"Waiting to connect..."*, proceed to Phase 2.

### Phase 2: Run the Bootflag Enabler Script
Run the script from any computer on the same local network:

```powershell
python scripts/ptp_smartphone_bootflag.py 192.168.1.212
```

**Expected Terminal Output:**
```text
================================================================
   Canon EOS 4000D Smartphone-Mode PTP Bootflag Enabler
   Target:      192.168.1.212:15740
   Action:      EnableBootDisk (BOOT=1)
================================================================

[*] Actively probing 192.168.1.212:15740...
[+] TCP CONNECTED TO CAMERA AT 192.168.1.212:15740!
[+] Sent Init_Command_Req (42 bytes).

>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
 [!] CHECK CAMERA SCREEN: It should say 'Connect to iPhone?'
     PRESS THE [OK] / [SET] BUTTON ON THE CAMERA NOW!
     (Socket is holding open and waiting for your button press...)
<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

[+] CAMERA ACK RECEIVED! Connected to 'EOS4000D', Connection #1
[*] Opening event channel...
[+] Event channel established successfully!
[*] Opening PTP Session (Session ID: 1, TID: 1)...
[+] PTP Session opened successfully (Response: 0x2001 OK)!
[*] Unlocking Canon Event Procedures (PTP 0x9050 x3)...
    Pass 1/3: Response 0x2005
    Pass 2/3: Response 0x2005
    Pass 3/3: Response 0x2005

[*] Executing internal Event Procedure 'EnableBootDisk' (PTP 0x9052)...

================================================================
 [SUCCESS] MAGIC LANTERN BOOTFLAG ENABLED! (BOOT=1)
================================================================

[!] The internal camera NVRAM has been modified:
    Address 0xF8000004 set to 0xFFFFFFFF (BOOT=1)

[*] PTP Session closed. Done!
```

---

### Phase 3: SD Card Preparation (Bootloader)
To bootstrap Magic Lantern from the SD card:
1. Format a high quality SD / SDHC card (2GB to 32GB recommended) as **FAT32** (or FAT16 for <=2GB).
2. Set the volume boot flags using `EOScard.exe` or `make_bootable.py`:
   - Offset `0x047`: `"EOS_DEVELOP"` (11 bytes)
   - Offset `0x05C`: `"BOOTDISK"` (8 bytes)
3. Copy the Magic Lantern binaries:
   - Root: `autoexec.bin`
   - Subdirectories: `ML/`, `ML/FONTS/`, `ML/CROPMKS/`, `ML/SETTINGS/`
4. Safely eject the card from your PC.

### Phase 4: First Boot Verification
1. Turn camera power **OFF**.
2. Insert the prepared SD card into the camera.
3. Close the battery/card door.
4. Flip the power dial to **ON**.
5. The red card activity LED will flash, and the display will show the Magic Lantern greeting screen.

---

## How to Revert / Disable Bootflag

If you ever wish to completely remove the Magic Lantern bootflag and return NVRAM to factory state (`BOOT=0`):

1. Turn on camera Wi-Fi and select "Connect to smartphone" (Auto IP / DHCP).
2. Run the disabler script:
```powershell
python scripts/ptp_smartphone_disable_bootflag.py 192.168.1.212
```
3. Press **[OK]** on the camera screen.
4. The script executes `DisableBootDisk` via PTP `0x9052`, writing `0x00000000` to NVRAM `0xF8000004`.
5. The camera now ignores `autoexec.bin` completely and boots purely stock Canon firmware.

---

## Technical Reference & Protocol Specification

| Parameter | Value | Description |
|---|---|---|
| **Port** | `15740` (TCP) | Standard CIPA DC-005 PTP/IP port |
| **Client Name** | `"iPhone\0"` (UTF-16LE) | Accepted without Canon pairing code |
| **Opcode 0x1002** | `PTP_OC_OpenSession` | Initializes transaction state |
| **Opcode 0x9050** | `PTP_OC_EOS_EnableEventProc` | Unlocks Canon DryOS internal function dispatch |
| **Opcode 0x9052** | `PTP_OC_EOS_ExecuteEventProc` | Calls named function directly in DryOS context |
| **Enable Function** | `"EnableBootDisk"` | Sets `*(uint32_t*)0xF8000004 = 0xFFFFFFFF` |
| **Disable Function** | `"DisableBootDisk"` | Sets `*(uint32_t*)0xF8000004 = 0x00000000` |
| **NVRAM Location** | `0xF8000004` | Canon EEPROM boot flag read by `boot-d45.c` |
