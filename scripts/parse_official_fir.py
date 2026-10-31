import struct
import os

path = r"d:\Dev\REverSE\4000D\firmware\CCF22110.FIR"
data = open(path, "rb").read()
size = len(data)

def get_u32(off):
    return struct.unpack("<I", data[off:off+4])[0]

print(f"File: {path}")
print(f"Size: {size} bytes (0x{size:x})")

model_id = get_u32(0)
print(f"0x000: Model ID = 0x{model_id:08x} (Model code 0x{model_id & 0xffff:04x} = {model_id & 0xffff})")
version = data[0x10:0x20].rstrip(b"\x00").decode("ascii", errors="replace")
print(f"0x010: Version = {version}")

checksum = get_u32(0x20)
print(f"0x020: Checksum = 0x{checksum:08x}")

up1_hdr = get_u32(0x24)
up1_off = get_u32(0x28)
up2_hdr = get_u32(0x2c)
fw_off = get_u32(0x30)
fw_unk = get_u32(0x34)
embedded_len = get_u32(0x38)

print(f"0x024: Updater1 Header Offset = 0x{up1_hdr:x}")
print(f"0x028: Updater1 Payload Offset = 0x{up1_off:x}")
print(f"0x02c: Updater2 Header Offset = 0x{up2_hdr:x}")
print(f"0x030: Firmware Offset = 0x{fw_off:x}")
print(f"0x034: Field 0x34 = 0x{fw_unk:x}")
print(f"0x038: Embedded File Size = 0x{embedded_len:x} ({embedded_len} bytes)")

sha1_seed = get_u32(0x40)
print(f"0x040: SHA1 Seed = 0x{sha1_seed:08x}")

up1_tot = get_u32(0x60)
fw_len = get_u32(0x64)
print(f"0x060: Updater1 Total = 0x{up1_tot:x}")
print(f"0x064: Firmware Length = 0x{fw_len:x}")
print(f"0x068: Updater1 HMAC-SHA1 = {data[0x68:0x68+20].hex()}")
print(f"0x088: Firmware HMAC-SHA1 = {data[0x88:0x88+20].hex()}")

if up1_hdr < size:
    print(f"\n--- Updater1 Header @ 0x{up1_hdr:x} ---")
    up1_len = get_u32(up1_hdr)
    up1_addr = get_u32(up1_hdr + 4)
    up1_unk = get_u32(up1_hdr + 8)
    up1_seed = get_u32(up1_hdr + 0x0c)
    print(f"  Updater1 Length = 0x{up1_len:x} ({up1_len} bytes)")
    print(f"  Updater1 Load Address = 0x{up1_addr:08x}")
    print(f"  Field 0x08 = 0x{up1_unk:x}")
    print(f"  XOR / Seed = 0x{up1_seed:08x}")

if fw_off < size:
    print(f"\n--- Firmware Section @ 0x{fw_off:x} ---")
    fw_sec_hdr = get_u32(fw_off)
    fw_sec_off = get_u32(fw_off + 4)
    fw_sec_tot = get_u32(fw_off + 8)
    fw_sec_enc = get_u32(fw_off + 0x0c)
    print(f"  Decryption data offset = 0x{fw_sec_hdr:x}")
    print(f"  Encrypted data offset = 0x{fw_sec_off:x}")
    print(f"  Total firmware length = 0x{fw_sec_tot:x} ({fw_sec_tot} bytes)")
    print(f"  Encrypted part length = 0x{fw_sec_enc:x} ({fw_sec_enc} bytes)")
