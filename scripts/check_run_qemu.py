path = r"d:\Dev\REverSE\4000D\qemu-eos\magiclantern\run_qemu.py"
content = open(path, "r", encoding="utf-8", errors="ignore").read()

for line in content.splitlines()[:60]:
    print(line)
