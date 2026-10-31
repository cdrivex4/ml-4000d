import zlib
import struct

path = r"d:\Dev\REverSE\4000D\firmware\DMP4000D.FIR"
data = open(path, "rb").read()

raw_payload = data[0x120:0x120 + 0x10740]

print("Trying zlib decompress...")
for offset in range(0, min(128, len(raw_payload))):
    try:
        dec = zlib.decompress(raw_payload[offset:])
        print(f"Success at offset {offset}! Decompressed {len(dec)} bytes")
        break
    except:
        pass
else:
    print("Not standard zlib.")

# Let's check if fir_tool2 xor_decode with other seeds or offsets produces anything
# In fir_tool2.py:
# t512 and t513
# Let's inspect fir_tool2.py:
# xorSeed = getLongLE( m, updater1header + 0xc )
# What was updater1header?
# 0xb0:
# 0xb0: updater1len (0x10740)
# 0xb4: 0x001ef930
# 0xb8: 0x00000000
# 0xbc: 0x9cbbb3a1
# But wait! What if updater1header is NOT 0xb0?
# In FIR header:
# 0x24: 0xb0 (updater1header)
# 0x28: 0x120 (updater1 offset)
# 0x2c: 0xffffffff (updater2header)
# 0x30: 0x10860 (firmware offset)
print("Header fields checked.")
