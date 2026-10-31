import urllib.request

url = "https://raw.githubusercontent.com/reticulatedpines/magiclantern_simplified/dev/Makefile.caller"
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as r:
        txt = r.read().decode('utf-8')
        for line in txt.splitlines():
            if any(k in line.lower() for k in ['fir', 'dumper', 'installer']):
                print("Caller:", line)
except Exception as e:
    print("Error:", e)
