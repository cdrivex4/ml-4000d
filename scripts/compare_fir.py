import urllib.request
import struct

url = "https://raw.githubusercontent.com/reticulatedpines/magiclantern_simplified/dev/platform/1100D.105/ML-SETUP.FIR"
fir_data = None
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as r:
        fir_data = r.read()
        print("Fetched ML-SETUP.FIR for 1100D! Length:", len(fir_data))
except Exception as e:
    print("Error:", e)

if fir_data:
    print("Model ID:", hex(struct.unpack("<I", fir_data[0:4])[0]))
    print("Version:", fir_data[0x10:0x20])
    up1_hdr = struct.unpack("<I", fir_data[0x24:0x28])[0]
    up1_off = struct.unpack("<I", fir_data[0x28:0x2c])[0]
    print(f"Updater1 hdr: 0x{up1_hdr:x}, off: 0x{up1_off:x}")
    print("Payload bytes at up1_off:")
    print(fir_data[up1_off : up1_off + 32].hex())
