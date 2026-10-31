import re

path = r"d:\Dev\REverSE\4000D\qemu-eos\hw\eos\eos.c"
content = open(path, "r", encoding="utf-8", errors="ignore").read()

matches = []
for line in content.splitlines():
    if any(k in line.lower() for k in ['fir', 'flasher', 'dumper', '0x800', 'bootflags']):
        matches.append(line.strip())

print(f"Matches in eos.c: {len(matches)}")
for m in matches[:40]:
    print(" ", m)
