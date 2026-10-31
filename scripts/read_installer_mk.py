import urllib.request

url = "https://raw.githubusercontent.com/reticulatedpines/magiclantern_simplified/dev/installer/Makefile"
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as r:
        txt = r.read().decode('utf-8')
        print("installer/Makefile:")
        print(txt)
except Exception as e:
    print("Error:", e)
