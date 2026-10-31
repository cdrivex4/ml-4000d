import struct

data = open(r"d:\Dev\REverSE\4000D\firmware\DMP4000D.FIR", "rb").read()

# Let's inspect the exact header layout:
# Offset 0: Model ID (0x80000422)
# Offset 0x10: Version string ("1.3.3")
# Let's dump the first 512 bytes in 32-bit words
print("FIR Header analysis:")
for offset in range(0, 0x180, 16):
    words = struct.unpack("<4I", data[offset:offset+16])
    words_hex = " ".join(f"{w:08x}" for w in words)
    print(f"0x{offset:04x}: {words_hex}")

# Total size: 67804 bytes (0x108dc)
print("File length:", len(data), hex(len(data)))
# Notice at offset 0x38: dc 08 01 00 -> 0x000108dc == 67804 bytes!
# Offset 0x30: 60 08 01 00 -> 0x00010860 == 67680 bytes (payload size!)
# Offset 0x24: b0 00 00 00 -> 0x000000b0 == 176 bytes (header size / payload start offset!)
# Let's verify: 0xb0 + 0x00010860 = 0x10910 ? Wait, 0x108dc - 0x7c = 0x10860!
# At offset 0x64: 7c 00 00 00 -> 0x7c == 124 bytes (signature offset or secondary header)
