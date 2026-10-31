import urllib.request
import json

paths = json.load(open(r"d:\Dev\REverSE\4000D\scripts\search_simplified.py")) if False else None

# Let's search tree of simplified for any tools or fir
url = "https://api.github.com/repos/reticulatedpines/magiclantern_simplified/git/trees/dev?recursive=1"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
resp = urllib.request.urlopen(req, timeout=15)
data = json.loads(resp.read().decode('utf-8'))
all_paths = [x['path'] for x in data.get('tree', [])]

fir_tools = [p for p in all_paths if any(k in p.lower() for k in ['fir', 'decrypt', 'unpack', 'disarm'])]
print("FIR-related paths in magiclantern_simplified:")
for p in fir_tools:
    print(" ", p)
