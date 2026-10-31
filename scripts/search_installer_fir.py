import urllib.request

url = "https://raw.githubusercontent.com/reticulatedpines/magiclantern_simplified/dev/installer/Makefile"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=15) as r:
    txt = r.read().decode('utf-8')
    lines = txt.splitlines()
    for idx, line in enumerate(lines):
        if any(w in line for w in ['INSTALLER_FIR', 'fir', 'build_fir', 'dumper', 'CANON_FIR']):
            print(f"{idx+1}: {line}")
