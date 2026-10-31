import urllib.request
import json

url = "https://api.github.com/repos/reticulatedpines/magiclantern_simplified/git/trees/dev?recursive=1"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
resp = urllib.request.urlopen(req, timeout=15)
data = json.loads(resp.read().decode('utf-8'))
all_paths = [x['path'] for x in data.get('tree', [])]

build_fir_paths = [p for p in all_paths if any(k in p.lower() for k in ['fir', 'dumper', 'dmp'])]
print("Matching paths in simplified:")
for p in build_fir_paths:
    if any(k in p.lower() for k in ['make', 'build', 'tool', 'py', 'sh', 'c', 'h']):
        print(" ", p)
