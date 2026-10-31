import urllib.request
import zipfile
import hashlib
import os

url = "https://gdlp01.c-wss.com/gds/5/0400008525/01/v110-t100-3000d-4000d-win.zip"
firmware_dir = r"d:\Dev\REverSE\4000D\firmware"
zip_path = os.path.join(firmware_dir, "v110-t100-3000d-4000d-win.zip")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://th.canon/en/support/0400852502'
}

print(f"Downloading official Canon firmware from {url}...")
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=60) as resp, open(zip_path, 'wb') as f:
    total = int(resp.headers.get('Content-Length', 0))
    downloaded = 0
    chunk_size = 65536
    while True:
        chunk = resp.read(chunk_size)
        if not chunk:
            break
        f.write(chunk)
        downloaded += len(chunk)

print(f"Downloaded {downloaded} bytes to {zip_path}")
zip_md5 = hashlib.md5(open(zip_path, 'rb').read()).hexdigest()
zip_sha256 = hashlib.sha256(open(zip_path, 'rb').read()).hexdigest()
print(f"ZIP MD5: {zip_md5}")
print(f"ZIP SHA256: {zip_sha256}")

print("\nExtracting ZIP contents...")
with zipfile.ZipFile(zip_path, 'r') as z:
    for info in z.infolist():
        print(f"  {info.filename} ({info.file_size} bytes)")
        z.extract(info, firmware_dir)

fir_path = os.path.join(firmware_dir, "CCF22110.FIR")
if os.path.exists(fir_path):
    fir_data = open(fir_path, 'rb').read()
    print(f"\nCCF22110.FIR extracted successfully: {len(fir_data)} bytes")
    print(f"FIR MD5: {hashlib.md5(fir_data).hexdigest()}")
    print(f"FIR SHA1: {hashlib.sha1(fir_data).hexdigest()}")
    print(f"FIR SHA256: {hashlib.sha256(fir_data).hexdigest()}")
else:
    print("CCF22110.FIR not found in root of extracted files, checking subdirs...")
    for root, dirs, files in os.walk(firmware_dir):
        for fl in files:
            if fl.upper().endswith(".FIR"):
                print("Found FIR:", os.path.join(root, fl))
