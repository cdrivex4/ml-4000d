import urllib.request
import os

files_to_fetch = [
    ("reticulatedpines/magiclantern_hg_02", "master", "pack-fir.c"),
    ("reticulatedpines/magiclantern_hg_02", "master", "dumper.c"),
    ("reticulatedpines/magiclantern_hg_02", "master", "dumper_entry.S"),
    ("reticulatedpines/magiclantern_hg_02", "master", "firmware.h"),
    ("reticulatedpines/magiclantern_simplified", "dev", "platform/1300D.110/Makefile"),
    ("reticulatedpines/magiclantern_simplified", "dev", "platform/1300D.110/consts.h"),
    ("reticulatedpines/magiclantern_simplified", "dev", "platform/1300D.110/stubs.S"),
    ("reticulatedpines/magiclantern_simplified", "dev", "platform/1300D.110/internals.h"),
]

docs_dir = r"d:\Dev\REverSE\4000D\docs"

for repo, branch, path in files_to_fetch:
    raw_url = f"https://raw.githubusercontent.com/{repo}/{branch}/{path}"
    print(f"Fetching {raw_url} ...")
    try:
        req = urllib.request.Request(raw_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read()
            safe_name = path.replace("/", "_")
            out_file = os.path.join(docs_dir, safe_name)
            with open(out_file, "wb") as f:
                f.write(content)
            print(f"Saved {len(content)} bytes to {out_file}")
    except Exception as e:
        print(f"Failed {path}: {e}")
