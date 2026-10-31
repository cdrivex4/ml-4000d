#!/usr/bin/env python3
"""
scripts/pack_4000d_fir.py - Canon EOS 4000D FIR Container Packer & Checksum Verifier
Clean-room implementation of the Canon EOS 4000D FIR container mathematics.

Container Specifications:
  - Header Size: 288 bytes (0x120)
  - Model ID: 0x80000422 (Canon EOS 4000D / Rebel T100 / EOS 3000D)
  - Embedded Version: "1.3.3"
  - Header Checksum Formula: ~sum(all bytes except 0x20..0x24) & 0xFFFFFFFF
  - Updater1 Descriptor: Offset 0x24 -> 0xB0; Length 0x10740, RAM Load 0x001EF930, Seed 0x9CBBB3A1
  - Updater2 / Footer: Offset 0x30 -> 0x10860, Length 0x7C (124 bytes)
  - Total Container File Size: 67,804 bytes (0x108DC)
"""

import os
import sys
import struct
import hashlib

def pack_fir(payload_bytes, footer_bytes, model_id=0x80000422, version_str="1.3.3", load_addr=0x001EF930, xor_seed=0x9CBBB3A1, header_template=None):
    """
    Constructs a complete Canon .FIR container from payload and footer components.
    """
    header_len = 0x120
    payload_len = len(payload_bytes)
    footer_len = len(footer_bytes)
    total_len = header_len + payload_len + footer_len

    if header_template and len(header_template) == header_len:
        header = bytearray(header_template)
    else:
        header = bytearray(header_len)
        # Model ID
        struct.pack_into("<I", header, 0x00, model_id)
        # Version string (padded with zeros)
        ver_bytes = version_str.encode("ascii")
        header[0x10:0x10 + len(ver_bytes)] = ver_bytes
        # Section pointers
        struct.pack_into("<I", header, 0x24, 0xB0)           # Updater1 header offset
        struct.pack_into("<I", header, 0x28, 0x120)          # Updater1 payload offset
        struct.pack_into("<I", header, 0x2C, 0xFFFFFFFF)     # Unused / terminator
        struct.pack_into("<I", header, 0x30, 0x120 + payload_len) # Updater2 / Footer offset
        struct.pack_into("<I", header, 0x34, 0xFFFFFFFF)     # Unused / terminator
        struct.pack_into("<I", header, 0x38, total_len)      # Total file length
        # Sub-header at 0xB0
        struct.pack_into("<I", header, 0xB0, payload_len)    # Updater1 length
        struct.pack_into("<I", header, 0xB4, load_addr)      # Execution load address in RAM
        struct.pack_into("<I", header, 0xB8, 0)
        struct.pack_into("<I", header, 0xBC, xor_seed)       # Keystream seed

    # Ensure header lengths and offsets match current payload
    struct.pack_into("<I", header, 0x00, model_id)
    ver_bytes = version_str.encode("ascii")
    header[0x10:0x20] = b'\x00' * 16
    header[0x10:0x10 + len(ver_bytes)] = ver_bytes
    struct.pack_into("<I", header, 0x24, 0xB0)
    struct.pack_into("<I", header, 0x28, 0x120)
    struct.pack_into("<I", header, 0x30, 0x120 + payload_len)
    struct.pack_into("<I", header, 0x38, total_len)
    struct.pack_into("<I", header, 0xB0, payload_len)
    struct.pack_into("<I", header, 0xB4, load_addr)

    # Zero checksum field before computation
    header[0x20:0x24] = b'\x00\x00\x00\x00'

    # Compute container checksum
    # Invariant: checksum = ~sum(all_bytes) & 0xFFFFFFFF
    full_buffer = header + payload_bytes + footer_bytes
    chk = (~sum(full_buffer)) & 0xFFFFFFFF
    struct.pack_into("<I", header, 0x20, chk)

    return bytes(header) + payload_bytes + footer_bytes, chk

def main():
    fir_path = r"d:\Dev\REverSE\4000D\firmware\DMP4000D.FIR"
    if not os.path.exists(fir_path):
        print(f"Error: {fir_path} not found.")
        return 1

    orig = open(fir_path, "rb").read()
    orig_header = orig[:0x120]
    orig_payload = orig[0x120:0x10860]
    orig_footer = orig[0x10860:]
    orig_chk = struct.unpack("<I", orig[0x20:0x24])[0]

    rebuilt, calc_chk = pack_fir(orig_payload, orig_footer, header_template=orig_header)

    print("=== Canon EOS 4000D FIR Container Verification ===")
    print(f"Original FIR Size:      {len(orig)} bytes")
    print(f"Rebuilt FIR Size:       {len(rebuilt)} bytes")
    print(f"Original Checksum:      0x{orig_chk:08X}")
    print(f"Calculated Checksum:    0x{calc_chk:08X}")
    print(f"Original SHA-256:       {hashlib.sha256(orig).hexdigest()}")
    print(f"Rebuilt SHA-256:        {hashlib.sha256(rebuilt).hexdigest()}")

    if rebuilt == orig:
        print("[+] VERIFICATION PASSED: Byte-for-byte exact 100% cryptographic match!")
        return 0
    else:
        print("[-] VERIFICATION FAILED: Mismatch in rebuilt FIR container.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
