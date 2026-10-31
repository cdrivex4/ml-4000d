path = r"d:\Dev\REverSE\4000D\qemu-eos\hw\eos\model_list.c"
content = open(path, "r", encoding="utf-8", errors="ignore").read()

idx = content.find("2000D")
if idx != -1:
    print("Found 2000D:")
    print(content[idx : idx+600])
else:
    print("2000D not in model_list.c")
