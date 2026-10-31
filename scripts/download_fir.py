import urllib.request
import os
import hashlib
import time

snapshots = [
    '20220630194417',
    '20221109180426',
    '20250903073756',
    '20240416075829'
]

out_dir = r"d:\Dev\REverSE\4000D\firmware"

for ts in snapshots:
    for mode in ['', 'id_', 'if_']:
        url = f"https://web.archive.org/web/{ts}{mode}/https://a1ex.magiclantern.fm/debug/portable-rom-dumper/new/DMP4000D.FIR"
        print(f"Trying {url} ...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://web.archive.org/'
        }
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = resp.read()
                print(f"  Got {len(data)} bytes, status={resp.status}, content-type={resp.headers.get('Content-Type')}")
                if len(data) > 1000 and b"suspected abusive bot traffic" not in data and b"<html" not in data[:50].lower():
                    # Check if valid FIR or binary
                    target_file = os.path.join(out_dir, "DMP4000D.FIR")
                    with open(target_file, "wb") as f:
                        f.write(data)
                    print(f"SUCCESS! Saved to {target_file}")
                    print(f"Size: {len(data)} bytes")
                    print(f"SHA256: {hashlib.sha256(data).hexdigest()}")
                    print(f"MD5: {hashlib.md5(data).hexdigest()}")
                    print(f"First 64 bytes (hex): {data[:64].hex()}")
                    print(f"First 32 bytes (repr): {data[:32]}")
                    sys.exit(0)
                else:
                    print(f"  Received text/html or block page (sample: {data[:120]})")
        except Exception as e:
            print(f"  Failed: {e}")
        time.sleep(2)
