import subprocess
import re
import os

READELF = r"tools\xpack-arm-none-eabi-gcc-13.3.1-1.1\bin\arm-none-eabi-readelf.exe"
ELF_PATH = r"magic-lantern-1300d\platform\4000D.100\magiclantern"
OUT_SYM = r"liveSDCard\ML\MODULES\t100_100.sym"

cmd = [READELF, "-sW", ELF_PATH]
res = subprocess.run(cmd, capture_output=True, text=True, check=True)

symbols = []
# Example readelf line:
#   Num:    Value  Size Type    Bind   Vis      Ndx Name
#    45: 00c80120    44 FUNC    GLOBAL DEFAULT    1 my_func
for line in res.stdout.splitlines():
    if "GLOBAL" not in line or " UND " in line:
        continue
    parts = line.split()
    if len(parts) >= 8:
        val = parts[1]
        stype = parts[3]
        name = parts[7]
        
        if stype in ('FUNC', 'OBJECT', 'ABS', 'NOTYPE'):
            if name.startswith('__config_') or re.match(r'^_[a-zA-Z]', name):
                continue
            try:
                addr = int(val, 16)
                symbols.append((addr, val, name))
            except ValueError:
                pass

symbols.sort(key=lambda x: (x[0], x[2]))

os.makedirs(os.path.dirname(OUT_SYM), exist_ok=True)
with open(OUT_SYM, 'w', newline='\n') as f:
    for addr, val, name in symbols:
        # format: <hex_address> <symbol_name>
        f.write(f"{addr:08x} {name}\n")

print(f"Generated {len(symbols)} symbols in {OUT_SYM}")
print("First 10 symbols:")
for s in symbols[:10]:
    print(f"  {s[1]} {s[2]}")
print("Last 10 symbols:")
for s in symbols[-10:]:
    print(f"  {s[1]} {s[2]}")
