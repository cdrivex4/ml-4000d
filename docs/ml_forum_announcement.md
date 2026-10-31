# Draft Magic Lantern Forum Announcement

**Target Topic:** [Canon EOS 4000D / 3000D / Rebel T100 (Topic #23369)](https://www.magiclantern.fm/forum/index.php?topic=23369.0)  
**Subject:** Canon EOS 4000D / Rebel T100 / 3000D — Magic Lantern UI Live & Operational on Physical Hardware!

---

### Forum Post Body

Hi everyone,

First and foremost, a massive thank you to **@a1ex**, **@Petabyt**, **@names_are_hard**, **@ccritix**, **Trammell Hudson**, and the entire **Magic Lantern and CHDK communities**. If you had not laid the foundation with the portable ROM dumpers, QEMU-EOS, reverse engineering notes, and the 1300D tree, we would never have been able to get this far.

We are excited to share that **Magic Lantern is now booting, rendering, and fully interactive on physical Canon EOS 4000D (Rebel T100 / EOS 3000D) hardware**!

The menus (Shoot, Debug, Display, Customized Buttons, Movie tweaks) render cleanly on the 2.7" LCD, physical button events are handled, configuration files persist, and the system runs in a **100% Volatile RAM Execution model (`#undef CONFIG_PROP_REQUEST_CHANGE`)**—meaning **zero ROM/flash writes**; simply removing the SD card restores 100% factory Canon operation.

---

### What Roadblocks Were Overcome?

Earlier porting attempts stalled at the 5th boot LED blink or encountered blank screens. Here are the key hardware and firmware discrepancies we identified and resolved:

1. **The Allocator Stubs Shift:**
   - Previous stubs mapped `_AllocateMemory` to `0xFE11D6A0`, which is actually the internal 2-argument helper `AllocateMemory_pool(struct mem_pool *pool, size_t size)`. Calling it with one argument caused an immediate data abort.
   - The true 1-argument public system heap allocator is at **`0xFE11D810`** (and `_FreeMemory` is at **`0xFE11DBAC`**).
   - Core libc stubs were corrected: `_malloc` = **`0xFE2934A0`**, `_free` = **`0xFE2934F8`**, and `vsnprintf` = **`0xFE292FEC`**.

2. **The True OSD VRAM Plane (`0x53360`):**
   - Pointing Magic Lantern at `0x5339C` lands in the LiveView sensor YUV buffer.
   - The true 8-bpp palette On-Screen Display bitmap layer is at **`0x53360`** (`PB_BITMAP_INFO`).
   - Hardware stride is 960 bytes, with the active 720x480 raster beginning at offset `+0x70F8` (`0x2087100`).

3. **WindowSystem OLC Screen Refresh Overwrite:**
   - On the 4000D, Canon's `gui_main_task` continuously refreshed the background Shooting Status display, fighting with the ML dialogs.
   - By disassembling `firmware/ROM1.BIN` at `0xFE3DFB0C` (`refresh partly`), we discovered that the WindowSystem dirty bit lives at **`*(0x3BE8C + 0x3C)`** (and full refresh at **`+0x30`**). Suppressing these flags while ML menus are open completely cured all screen tearing and flickering!

4. **2.7" 230k-dot Bezel Geometry:**
   - The physical bezel of the 4000D cuts off anything below $y \approx 460$.
   - We repositioned the menu help footers to $y = 420$ and $y = 442$, providing a crisp, completely visible layout.

5. **Safe Wi-Fi PTP Bootflag Activation:**
   - Because the 4000D enforces HMAC-SHA1 validation on `.FIR` files (causing `BOOT4000.FIR` to fail with *"Update file error"*), we leveraged the camera's native *"Connect to smartphone"* PTP/IP interface to call DryOS `EnableBootDisk` via standard event procedures—no flash writing or risk involved.

---

### Public Repository & Community Collaboration

We have published the complete open-source code, clean diffs, and documentation here:
**GitHub Repository:** [https://github.com/cdrivex4/ml-4000d](https://github.com/cdrivex4/ml-4000d)

- **Bug Tracking:** We are open to helping squash bugs and polish features! Please submit any issues or logs directly to the [GitHub Issues tracker](https://github.com/cdrivex4/ml-4000d/issues) so we can track and resolve them systematically.
- **Mainline Alignment:** We would love to collaborate with the core Magic Lantern team to get the 4000D target upstreamed into the official repositories. We are glad to assist with testing and hardware validation on the physical 4000D (FW 1.0.0) hardware we have available.

Thank you again to everyone who kept the Magic Lantern project alive. We hope this breathes new life into one of the most accessible DSLRs out there!
