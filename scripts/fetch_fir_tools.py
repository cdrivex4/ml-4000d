import urllib.request
import os

tools = [
    "tools/indy/dump_fir.py",
    "tools/indy/fir_tool2.py",
    "tools/indy/ofir_tool.py",
    "tools/firmware/compute_sig.py"
]

docs_dir = r"d:\Dev\REverSE\4000D\docs"

for t in tools:
    url = f"https://raw.githubusercontent.com/reticulatedpines/magiclantern_simplified/dev/{t}"
    print(f"Fetching {url} ...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read()
            out_file = os.path.join(docs_dir, os.path.basename(t))
            with open(out_file, "wb") as f:
                f.write(content)
            print(f"Saved {len(content)} bytes to {out_file}")
    except Exception as e:
        print(f"Failed {t}: {e}")
