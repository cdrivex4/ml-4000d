import os
import re

qemu_dir = r"d:\Dev\REverSE\4000D\qemu-eos"

matches = []
keywords = [b"1300D", b"4000D", b"0x80000422", b"0x80000404", b"106744", b"106f38", b"card_bootflags", b"DMP4000D"]

for root, dirs, files in os.walk(qemu_dir):
    for f in files:
        if f.endswith(('.c', '.h', '.S', '.py', '.sh', '.md', '.txt')):
            p = os.path.join(root, f)
            try:
                content = open(p, "rb").read()
                for kw in keywords:
                    if kw in content:
                        matches.append((p, kw))
            except Exception as e:
                pass

print(f"Total matches found in qemu-eos: {len(matches)}")
for p, kw in set(matches):
    print(f"  {kw.decode('utf-8', errors='ignore')} in {os.path.relpath(p, qemu_dir)}")
