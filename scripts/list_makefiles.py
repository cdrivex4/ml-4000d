import json

# Let's search all_paths for Makefiles
import urllib.request
url = "https://api.github.com/repos/reticulatedpines/magiclantern_simplified/git/trees/dev?recursive=1"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
resp = urllib.request.urlopen(req, timeout=15)
data = json.loads(resp.read().decode('utf-8'))
all_paths = [x['path'] for x in data.get('tree', [])]

makefiles = [p for p in all_paths if 'makefile' in p.lower()]
print("Makefiles count:", len(makefiles))
for m in makefiles[:30]:
    print(" ", m)
