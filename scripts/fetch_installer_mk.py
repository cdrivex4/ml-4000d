import urllib.request
import os

installers = [
    "installer/1100D.105/Makefile",
    "installer/600D.102/Makefile",
    "installer/Makefile.installer"
]

docs_dir = r"d:\Dev\REverSE\4000D\docs"

for path in installers:
    url = f"https://raw.githubusercontent.com/reticulatedpines/magiclantern_simplified/dev/{path}"
    print(f"Fetching {url} ...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read()
            out_file = os.path.join(docs_dir, os.path.basename(path).replace(".","_") + "_" + path.replace("/", "_"))
            with open(out_file, "wb") as f:
                f.write(content)
            print(f"Saved {len(content)} bytes to {out_file}")
            print(content.decode("utf-8", errors="replace"))
    except Exception as e:
        print(f"Failed {path}: {e}")
