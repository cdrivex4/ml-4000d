import urllib.request
import os

files = [
    "installer/5DC.111/build_scripts/eos_tools_v11/decrypt_fw2/decrypt_fw2.c",
    "installer/5DC.111/build_scripts/eos_tools_v11/decrypt_40D105_flasher/decrypt_40D105_flasher.c",
    "modules/io_crypt/io_decrypt.c"
]

docs_dir = r"d:\Dev\REverSE\4000D\docs"

for path in files:
    url = f"https://raw.githubusercontent.com/reticulatedpines/magiclantern_simplified/dev/{path}"
    print(f"Fetching {url} ...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read()
            out_file = os.path.join(docs_dir, os.path.basename(path))
            with open(out_file, "wb") as f:
                f.write(content)
            print(f"Saved {len(content)} bytes to {out_file}")
    except Exception as e:
        print(f"Failed {path}: {e}")
