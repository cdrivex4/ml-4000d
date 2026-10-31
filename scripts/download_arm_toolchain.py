import os
import sys
import urllib.request
import zipfile

URL = "https://github.com/xpack-dev-tools/arm-none-eabi-gcc-xpack/releases/download/v13.3.1-1.1/xpack-arm-none-eabi-gcc-13.3.1-1.1-win32-x64.zip"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "tools"))
ZIP_PATH = os.path.join(TOOLS_DIR, "arm-none-eabi-gcc.zip")

def download_file(url, dest):
    print(f"Downloading {url} to {dest}...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resp, open(dest, 'wb') as out_file:
        total_size = int(resp.headers.get('content-length', 0))
        downloaded = 0
        chunk_size = 1024 * 1024 # 1 MB
        while True:
            chunk = resp.read(chunk_size)
            if not chunk:
                break
            out_file.write(chunk)
            downloaded += len(chunk)
            if total_size > 0:
                percent = (downloaded / total_size) * 100
                sys.stdout.write(f"\rDownloaded {downloaded // (1024*1024)}MB / {total_size // (1024*1024)}MB ({percent:.1f}%)")
                sys.stdout.flush()
    print("\nDownload complete.")

def extract_zip(zip_path, extract_to):
    print(f"Extracting {zip_path} to {extract_to}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print("Extraction complete.")

if __name__ == "__main__":
    if not os.path.exists(ZIP_PATH):
        download_file(URL, ZIP_PATH)
    else:
        print(f"Zip file already exists at {ZIP_PATH}")
    extract_zip(ZIP_PATH, TOOLS_DIR)
    
    # Check for arm-none-eabi-gcc.exe
    found = []
    for root, dirs, files in os.walk(TOOLS_DIR):
        for f in files:
            if f.startswith("arm-none-eabi-"):
                found.append(os.path.join(root, f))
    print(f"\nFound {len(found)} arm-none-eabi binaries.")
    for b in found[:10]:
        print("  -", b)
