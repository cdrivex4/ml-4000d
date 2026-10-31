import os
import struct

fir_path = r"d:\Dev\REverSE\4000D\firmware\DMP4000D.FIR"
payload_path = r"d:\Dev\REverSE\4000D\firmware\dmp4000d_payload.bin"

data = open(fir_path, "rb").read()

# Extract raw executable ARM binary payload from DMP4000D.FIR
# Offset 0x120, length 0x10740 (67,392 bytes)
payload = data[0x120 : 0x120 + 0x10740]

with open(payload_path, "wb") as f:
    f.write(payload)

print(f"Extracted payload to {payload_path}")
print(f"Size: {len(payload)} bytes (0x{len(payload):x})")

# Let's inspect the payload
print("\nFirst 32 bytes (hex):", payload[:32].hex())
print("Last 32 bytes (hex):", payload[-32:].hex())
