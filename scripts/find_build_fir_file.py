import urllib.request
import json

# search for build_fir.py across repos
urls = [
    "https://api.github.com/search/code?q=filename:build_fir.py",
    "https://raw.githubusercontent.com/reticulatedpines/magiclantern_simplified/dev/dumper/build_fir.py"
]

req = urllib.request.Request("https://raw.githubusercontent.com/reticulatedpines/magiclantern_simplified/dev/dumper/build_fir.py", headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=10) as r:
        print("Found in simplified /dumper/build_fir.py!")
        data = r.read()
        open(r"d:\Dev\REverSE\4000D\docs\build_fir.py", "wb").write(data)
        print("Length:", len(data))
except Exception as e:
    print("Simplified error:", e)
