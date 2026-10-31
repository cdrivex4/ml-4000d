import urllib.request
import json

# Query heptapod API for files in magic-lantern/magic-lantern
# Project ID or path
url = "https://foss.heptapod.net/api/v4/projects/magic-lantern%2Fmagic-lantern/repository/tree?recursive=true&per_page=100"
headers = {'User-Agent': 'Mozilla/5.0'}
try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as r:
        items = json.loads(r.read().decode('utf-8'))
        print("Found items on Heptapod:", len(items))
        for it in items:
            if any(k in it['path'].lower() for k in ['dumper', 'fir', 'card_bootflags', 'rescue']):
                print(" ", it['path'])
except Exception as e:
    print("Error:", e)
