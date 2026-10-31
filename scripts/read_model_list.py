path = r"d:\Dev\REverSE\4000D\qemu-eos\hw\eos\model_list.c"
content = open(path, "r", encoding="utf-8", errors="ignore").read()

idx = content.find("1300D")
if idx != -1:
    print(content[max(0, idx-200) : min(len(content), idx+800)])
else:
    print("Not found")
