import urllib.request
import json

url = "https://web.archive.org/web/timemap/json?url=https://a1ex.magiclantern.fm/debug/portable-rom-dumper/new/DMP4000D.FIR"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read().decode('utf-8'))
        print("Snapshots found:", len(data))
        for row in data:
            print(row)
except Exception as e:
    print("Timemap error:", e)
