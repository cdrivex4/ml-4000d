#!/usr/bin/env python3
"""
scripts/verify_bootflag_payload_unicorn.py - Dynamic Unicorn Verification of Bootflag Toggle Payload
Simulates both Enable (BOOT 0 -> 1) and Disable (BOOT 1 -> 0) workflows on ARMv5TE core.
"""

import struct
from unicorn import *
from unicorn.arm_const import *

PAYLOAD_ADDR = 0x001EF930
RAM_BASE     = 0x001E0000
RAM_SIZE     = 128 * 1024
STACK_ADDR   = 0x001E0000

STUB_CARD_INIT          = 0x00101DE4
STUB_CARD_BOOTFLAGS     = 0x00106744
STUB_BOOT_WRITE_SECTOR  = 0x00107030
ROM_ENABLE_BOOT_DISK    = 0xFE116E10
ROM_DISABLE_BOOT_DISK   = 0xFE116E1C
NVRAM_BOOTDISK_ADDR     = 0xF8000004
CARD_LED_ADDR           = 0xC0220134

def run_test(initial_nvram_val):
    print(f"\n=======================================================")
    print(f"[*] Testing Bootflag Toggle with Initial NVRAM = 0x{initial_nvram_val:08X}")
    print(f"=======================================================")

    uc = Uc(UC_ARCH_ARM, UC_MODE_ARM)

    # Map RAM and Stack
    uc.mem_map(0x001C0000, 256 * 1024)

    # Map Stubs (0x00100000)
    uc.mem_map(0x00100000, 64 * 1024)

    # Map NVRAM (0xF8000000)
    uc.mem_map(0xF8000000, 64 * 1024)

    # Map ROM (0xFE110000)
    uc.mem_map(0xFE110000, 64 * 1024)

    # Map MMIO (0xC0220000)
    uc.mem_map(0xC0220000, 64 * 1024)

    # Load compiled binary
    payload = open(r"d:\Dev\REverSE\4000D\firmware\bootflag_payload.bin", "rb").read()
    uc.mem_write(PAYLOAD_ADDR, payload)

    # Set initial NVRAM value
    uc.mem_write(NVRAM_BOOTDISK_ADDR, struct.pack("<I", initial_nvram_val))

    # Install stub returns (BX LR = 0xE12FFF1E)
    bx_lr = struct.pack("<I", 0xE12FFF1E)
    uc.mem_write(STUB_CARD_INIT, bx_lr)
    uc.mem_write(STUB_CARD_BOOTFLAGS, bx_lr)
    uc.mem_write(STUB_BOOT_WRITE_SECTOR, bx_lr)
    uc.mem_write(ROM_ENABLE_BOOT_DISK, bx_lr)
    uc.mem_write(ROM_DISABLE_BOOT_DISK, bx_lr)

    # Tracking metrics
    events = []

    def hook_code(uc, address, size, user_data):
        if address == STUB_CARD_INIT:
            events.append("STUB_CARD_INIT")
        elif address == STUB_CARD_BOOTFLAGS:
            arg = uc.reg_read(UC_ARM_REG_R0)
            events.append(f"card_bootflags({arg})")
        elif address == ROM_ENABLE_BOOT_DISK:
            events.append("ROM_ENABLE_BOOT_DISK")
        elif address == ROM_DISABLE_BOOT_DISK:
            events.append("ROM_DISABLE_BOOT_DISK")
        elif address == STUB_BOOT_WRITE_SECTOR:
            lba = uc.reg_read(UC_ARM_REG_R1)
            buf_ptr = uc.reg_read(UC_ARM_REG_R2)
            data = uc.mem_read(buf_ptr, 64)
            msg_text = bytes(data).split(b'\n')[0].decode('ascii', 'ignore')
            events.append(f"write_sector(lba={lba}, msg={msg_text})")

    def hook_mem(uc, access, address, size, value, user_data):
        if address == CARD_LED_ADDR and access == UC_MEM_WRITE:
            events.append(f"LED={'ON' if value==0x46 else 'OFF'}")
        elif address == NVRAM_BOOTDISK_ADDR and access == UC_MEM_WRITE:
            events.append(f"NVRAM_WRITE=0x{value:08X}")

    uc.hook_add(UC_HOOK_CODE, hook_code)
    uc.hook_add(UC_HOOK_MEM_WRITE, hook_mem)

    # Start emulation for 200,000 instructions
    uc.emu_start(PAYLOAD_ADDR, 0xFFFFFFFF, count=200000)

    final_nvram = struct.unpack("<I", uc.mem_read(NVRAM_BOOTDISK_ADDR, 4))[0]
    print(f"[+] Final NVRAM Value: 0x{final_nvram:08X}")
    print("[+] Recorded Execution Events:")
    for ev in events[:25]:
        print(f"    - {ev}")

    if initial_nvram_val == 0:
        assert final_nvram == 0xFFFFFFFF, "Expected NVRAM to be enabled (0xFFFFFFFF)"
        assert "card_bootflags(1)" in events, "Expected card_bootflags(1)"
        assert "ROM_ENABLE_BOOT_DISK" in events, "Expected ROM_ENABLE_BOOT_DISK"
        print("[+] PASS: Enable Bootflag workflow 100% verified!")
    else:
        assert final_nvram == 0x00000000, "Expected NVRAM to be disabled (0x00000000)"
        assert "card_bootflags(0)" in events, "Expected card_bootflags(0)"
        assert "ROM_DISABLE_BOOT_DISK" in events, "Expected ROM_DISABLE_BOOT_DISK"
        print("[+] PASS: Disable / Revert Bootflag workflow 100% verified!")

if __name__ == "__main__":
    run_test(0x00000000)  # Test Enable
    run_test(0xFFFFFFFF)  # Test Disable
    print("\n[+] ALL TOGGLE MODES MATHEMATICALLY VERIFIED IN UNICORN!")
