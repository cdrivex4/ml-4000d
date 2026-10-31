import urllib.request
import json

urls_to_check = [
    "http://gdlp01.c-wss.com/*v110-t100*",
    "http://gdlp01.c-wss.com/*CCF22110*",
    "*v110-t100-3000d-4000d-win.zip*"
]

for u in urls_to_check:
    cdx = f"https://web.archive.org/cdx/search/cdx?url={u}&output=json&limit=10"
    print(f"Checking CDX for {u} ...")
    try:
        req = urllib.request.Request(cdx, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read().decode('utf-8'))
            print("Results:", len(data))
            for row in data:
                print(" ", row)
    except Exception as e:
        print("CDX error:", e)
