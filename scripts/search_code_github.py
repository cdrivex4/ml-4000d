import urllib.request
import json

# Let's search github api for "Card init =>" or "card_bootflags" or "boot_read/write_sector"
queries = [
    "https://api.github.com/search/code?q=ROMBASEADDR+repo:reticulatedpines/magiclantern_simplified",
    "https://api.github.com/search/code?q=card_bootflags+repo:reticulatedpines/magiclantern_simplified",
    "https://api.github.com/search/code?q=boot_read_sector+repo:reticulatedpines/magiclantern_simplified"
]

for q in queries:
    req = urllib.request.Request(q, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode('utf-8'))
            print("Matches for", q.split("=")[1].split("+")[0], ":", data.get("total_count"))
            for item in data.get("items", [])[:5]:
                print("  ", item["path"])
    except Exception as e:
        print("Error:", e)
