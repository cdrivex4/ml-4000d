import urllib.request
import re

url = "https://rodrigopolo.com/2019/09/25/canon-eos-r-firmware-version-1-4-0/"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=10) as r:
        txt = r.read().decode('utf-8')
        links = re.findall(r'https?://gdlp01\.c-wss\.com/gds/[^\s"\'<>]+', txt)
        print("Found links:", links)
except Exception as e:
    print("Error:", e)
