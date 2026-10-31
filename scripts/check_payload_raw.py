import struct

path = r"d:\Dev\REverSE\4000D\firmware\DMP4000D.FIR"
data = open(path, "rb").read()

print("File size:", len(data))

# Let's inspect bytes at 0x120
raw_payload = data[0x120:0x120 + 0x10740]
print("Raw payload length:", len(raw_payload))

print("\n--- First 64 bytes of raw payload at 0x120 ---")
print(raw_payload[:64].hex())

# Let's check entropy of raw_payload
import math
def entropy(b):
    if not b: return 0
    counts = [0]*256
    for x in b: counts[x] += 1
    ent = 0
    for c in counts:
        if c:
            p = c / len(b)
            ent -= p * math.log2(p)
    return ent

print("Entropy of raw payload:", entropy(raw_payload))
print("Entropy of first 1024 bytes:", entropy(raw_payload[:1024]))

# Let's check if the payload has an unencrypted header or structure
print("\n--- Inspecting 0x00 to 0x120 in detail ---")
for i in range(0, 0x120, 16):
    chunk = data[i:i+16]
    hex_str = " ".join(f"{b:02x}" for b in chunk)
    asc_str = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
    print(f"0x{i:04x}: {hex_str:<48} {asc_str}")
