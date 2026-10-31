#!/usr/bin/env python3
"""
scripts/emulate_dmp4000d.py - Unicorn Emulation Harness for Canon EOS 4000D Dumper
Simulates the execution of dmp4000d_decrypted.bin on an ARMv5TE core (DIGIC 4+).

Mocks:
  - RAM payload mapping at 0x001EF930
  - Flasher low-level stubs:
      * 0x00101DE4: Card init (returns 2 for SDHC/SDXC TRAN mode)
      * 0x00106744: card_bootflags
      * 0x00106F38: boot_read_sector
      * 0x00107030: boot_write_sector
  - MMIO Registers:
      * 0xC0220134: Activity LED GPIO (0x46=ON, 0x44=OFF)
  - VRAM Display Buffer:
      * 0x40D07800: Framebuffer string output
  - ROM Regions:
      * 0xFF0C0000: Uncached ROM entry
      * 0xFE0C0000: Cached ROM mirror
      * 0xF8000000: Flash Model ID (0x003825C2)
"""

import os
import sys
import struct
from unicorn import *
from unicorn.arm_const import *
import capstone

# Memory Addresses
PAYLOAD_LOAD_ADDR   = 0x001EF930
RAM_BASE            = 0x001E0000
RAM_SIZE            = 128 * 1024        # 128 KB
STACK_BASE          = 0x001C0000
STACK_SIZE          = 128 * 1024        # 128 KB
STACK_ADDR          = 0x001E0000

STUBS_BASE          = 0x00100000
STUBS_SIZE          = 64 * 1024         # 64 KB
STUB_CARD_INIT      = 0x00101DE4
STUB_CARD_BOOTFLAGS = 0x00106744
STUB_READ_SECTOR    = 0x00106F38
STUB_WRITE_SECTOR   = 0x00107030

MMIO_BASE           = 0xC0220000
MMIO_SIZE           = 64 * 1024         # 64 KB
CARD_LED_ADDR       = 0xC0220134

VRAM_BASE           = 0x40D00000
VRAM_SIZE           = 1024 * 1024       # 1 MB
VRAM_BUF_ADDR       = 0x40D07800

ROM_UNCACHED_BASE   = 0xFF0C0000
ROM_UNCACHED_SIZE   = 256 * 1024        # 256 KB
ROM_CACHED_BASE     = 0xFE0C0000
ROM_CACHED_SIZE     = 256 * 1024        # 256 KB
FLASH_ID_BASE       = 0xF8000000
FLASH_ID_SIZE       = 64 * 1024         # 64 KB

class DumperEmulator:
    def __init__(self, payload_path):
        self.payload_path = payload_path
        self.payload_bytes = open(payload_path, "rb").read()
        self.uc = Uc(UC_ARCH_ARM, UC_MODE_ARM)
        self.cs = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_ARM)
        self.led_states = []
        self.vram_output = bytearray()
        self.instructions_executed = 0
        self.max_instructions = 10000
        self.sectors_written = []

        self._setup_memory()
        self._setup_stubs()
        self._setup_hooks()

    def _setup_memory(self):
        # 0. Stack Memory
        self.uc.mem_map(STACK_BASE, STACK_SIZE)

        # 1. Payload RAM
        self.uc.mem_map(RAM_BASE, RAM_SIZE)
        self.uc.mem_write(PAYLOAD_LOAD_ADDR, self.payload_bytes)

        # 2. Flasher Stubs Region
        self.uc.mem_map(STUBS_BASE, STUBS_SIZE)

        # 3. MMIO Registers
        self.uc.mem_map(MMIO_BASE, MMIO_SIZE)

        # 4. VRAM Framebuffer
        self.uc.mem_map(VRAM_BASE, VRAM_SIZE)

        # 5. Flash Model ID
        self.uc.mem_map(FLASH_ID_BASE, FLASH_ID_SIZE)
        # Store Macronix MX25L25635E Flash Model ID: 0x003825C2
        self.uc.mem_write(FLASH_ID_BASE, struct.pack("<I", 0x003825C2))

        # 6. ROM Regions
        self.uc.mem_map(ROM_UNCACHED_BASE, ROM_UNCACHED_SIZE)
        self.uc.mem_map(ROM_CACHED_BASE, ROM_CACHED_SIZE)
        # Populate mock ROM entry instructions
        rom_header = struct.pack("<4I", 0xEA000002, 0xE3A00000, 0xE12FFF1E, 0x80000422)
        self.uc.mem_write(ROM_UNCACHED_BASE, rom_header)
        self.uc.mem_write(ROM_CACHED_BASE, rom_header)

        # Setup initial CPU registers
        self.uc.reg_write(UC_ARM_REG_SP, STACK_ADDR)
        self.uc.reg_write(UC_ARM_REG_PC, PAYLOAD_LOAD_ADDR)
        # CPSR: Supervisor mode (0x13), IRQ/FIQ disabled (0xD3)
        self.uc.reg_write(UC_ARM_REG_CPSR, 0xD3)

    def _setup_stubs(self):
        # ARM instructions:
        # mov r0, #2; bx lr -> 0xE3A00002, 0xE12FFF1E
        stub_card_init = struct.pack("<2I", 0xE3A00002, 0xE12FFF1E)
        self.uc.mem_write(STUB_CARD_INIT, stub_card_init)

        # bx lr -> 0xE12FFF1E
        stub_bx_lr = struct.pack("<I", 0xE12FFF1E)
        self.uc.mem_write(STUB_CARD_BOOTFLAGS, stub_bx_lr)

        # mov r0, #0; bx lr -> 0xE3A00000, 0xE12FFF1E
        stub_success = struct.pack("<2I", 0xE3A00000, 0xE12FFF1E)
        self.uc.mem_write(STUB_READ_SECTOR, stub_success)
        self.uc.mem_write(STUB_WRITE_SECTOR, stub_success)

    def _setup_hooks(self):
        # Code execution tracing hook
        self.uc.hook_add(UC_HOOK_CODE, self._hook_code)
        # Memory write hook to intercept MMIO and VRAM
        self.uc.hook_add(UC_HOOK_MEM_WRITE, self._hook_mem_write)

    def _hook_code(self, uc, address, size, user_data):
        self.instructions_executed += 1
        
        # Intercept write sector stub to record sector buffer contents
        if address == STUB_WRITE_SECTOR:
            drive = uc.reg_read(UC_ARM_REG_R0)
            lba = uc.reg_read(UC_ARM_REG_R1)
            buf_ptr = uc.reg_read(UC_ARM_REG_R2)
            sector_data = uc.mem_read(buf_ptr, 512)
            self.sectors_written.append((lba, bytes(sector_data)))
            print(f"  [*] [STUB HOOK] boot_write_sector(drive={drive}, lba={lba}, buf=0x{buf_ptr:08X})")

        # Break early once in the post-dump blink loop
        if self.instructions_executed > 500:
            dump_done = uc.mem_read(0x001F0054, 4)
            if struct.unpack("<I", dump_done)[0] == 1:
                # Stop emulation after dumping completes and enters loop
                print("  [+] Payload completed dump sequence (g_dump_complete == 1). Halting.")
                uc.emu_stop()

        if self.instructions_executed >= self.max_instructions:
            print("  [!] Max instruction budget reached. Halting.")
            uc.emu_stop()

    def _hook_mem_write(self, uc, access, address, size, value, user_data):
        if address == CARD_LED_ADDR:
            state = "ON (0x46)" if value == 0x46 else ("OFF (0x44)" if value == 0x44 else hex(value))
            self.led_states.append((self.instructions_executed, value, state))
            print(f"  [*] [MMIO WRITE] LED Register 0x{address:08X} = 0x{value:02X} -> LED {state}")
        elif VRAM_BASE <= address < VRAM_BASE + VRAM_SIZE:
            char_val = value & 0xFF
            if 32 <= char_val <= 126 or char_val in (10, 13):
                self.vram_output.append(char_val)

    def run(self):
        print(f"[*] Starting Unicorn ARMv5TE Emulation of {self.payload_path}...")
        print(f"    Entry Point: 0x{PAYLOAD_LOAD_ADDR:08X}, Initial SP: 0x{STACK_ADDR:08X}")
        try:
            self.uc.emu_start(PAYLOAD_LOAD_ADDR, PAYLOAD_LOAD_ADDR + len(self.payload_bytes), timeout=5000000)
        except UcError as e:
            # Check if execution stopped cleanly
            if self.instructions_executed > 50:
                print(f"[*] Emulation terminated gracefully: {e}")
            else:
                print(f"[-] Emulation error: {e}")
                raise

        print(f"\n[+] Emulation Finished. Total instructions executed: {self.instructions_executed}")

        # Extract captured VRAM text output
        vram_str = self.vram_output.decode("ascii", errors="replace")
        print("\n=== Captured VRAM Rescue Display Output ===")
        print(vram_str)
        print("===========================================")

        # Check Global Variable State
        rombase = struct.unpack("<I", self.uc.mem_read(0x001F004C, 4))[0]
        card_init = struct.unpack("<I", self.uc.mem_read(0x001F0050, 4))[0]
        dump_done = struct.unpack("<I", self.uc.mem_read(0x001F0054, 4))[0]

        print("\n=== Verified Global Diagnostic Invariants ===")
        print(f"  - Detected ROM Base:   0x{rombase:08X} (Expected: 0xFF0C0000)")
        print(f"  - Card Init Status:    {card_init} (Expected: 2)")
        print(f"  - Dump Complete Flag:  {dump_done} (Expected: 1)")
        print(f"  - Total LED Switches:  {len(self.led_states)}")
        for step, val, state in self.led_states:
            print(f"      Step {step}: LED {state}")

        if self.sectors_written:
            lba, sdata = self.sectors_written[0]
            print(f"\n=== Verified SD Card Sector Output (LBA {lba}) ===")
            print(f"  Content: {repr(sdata[:64])}")

        assert rombase == 0xFF0C0000, "ROM Base mismatch!"
        assert card_init == 2, "Card init return code mismatch!"
        assert dump_done == 1, "Dump complete flag not set!"
        print("\n[+] ALL FORMAL VERIFICATION INVARIANTS PASSED!")
        return 0

def main():
    payload_bin = r"d:\Dev\REverSE\4000D\firmware\dmp4000d_decrypted.bin"
    if not os.path.exists(payload_bin):
        print(f"Error: {payload_bin} not found.")
        return 1
    emu = DumperEmulator(payload_bin)
    return emu.run()

if __name__ == "__main__":
    sys.exit(main())
