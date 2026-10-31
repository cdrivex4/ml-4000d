import urllib.request
import json

url = "https://api.github.com/repos/reticulatedpines/magiclantern_simplified/git/trees/dev?recursive=1"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
resp = urllib.request.urlopen(req, timeout=15)
data = json.loads(resp.read().decode('utf-8'))
all_paths = [x['path'] for x in data.get('tree', [])]

rescue_paths = [p for p in all_paths if any(k in p.lower() for k in ['rescue', 'reboot-dumper', 'dumper', 'boot-d45'])]
print("Matching paths for rescue/dumper:")
for p in rescue_paths:
    print(" ", p)
