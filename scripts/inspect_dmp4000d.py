import hashlib
import struct
import os

path = r"d:\Dev\REverSE\4000D\firmware\DMP4000D.FIR"
size = os.path.getsize(path)
data = open(path, "rb").read()

md5 = hashlib.md5(data).hexdigest()
sha1 = hashlib.sha1(data).hexdigest()
sha256 = hashlib.sha256(data).hexdigest()

print(f"File: {path}")
print(f"Size: {size} bytes")
print(f"MD5: {md5}")
print(f"SHA1: {sha1}")
print(f"SHA256: {sha256}")

print("\n--- First 128 bytes (hex & ascii) ---")
for i in range(0, min(128, size), 16):
    chunk = data[i:i+16]
    hex_str = " ".join(f"{b:02x}" for b in chunk)
    ascii_str = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
    print(f"{i:04x}: {hex_str:<48}  {ascii_str}")

# Let's inspect the Canon FIR header structure
# Traditional DIGIC FIR headers:
# 0x00: Model ID / Magic / Header size
# Let's see what model ID is at offset 0 or in the header
if size >= 0x100:
    # Print potential header fields
    print("\n--- Header Fields ---")
    print("0x00 - 0x1F (uint32 LE):", [f"0x{x:08x}" for x in struct.unpack("<8I", data[0:32])])
    print("0x20 - 0x3F (uint32 LE):", [f"0x{x:08x}" for x in struct.unpack("<8I", data[32:64])])

# Search for strings inside the file
print("\n--- Extracted Strings (len >= 6) ---")
import re
strings = re.findall(b"[\x20-\x7e]{6,}", data)
for s in strings[:30]:
    print("  ", s.decode("ascii"))
