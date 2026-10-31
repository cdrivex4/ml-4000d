path = r"d:\Dev\REverSE\4000D\qemu-eos\magiclantern\ml_tests\cam.py"
content = open(path, "r", encoding="utf-8", errors="ignore").read()

for line in content.splitlines():
    if "4000D" in line or "1300D" in line:
        print(line)
