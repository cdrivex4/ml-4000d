path = r"d:\Dev\REverSE\4000D\qemu-eos\hw\eos\model_list.c"
content = open(path, "r", encoding="utf-8", errors="ignore").read()

idx = content.find("MODEL_NAME_1300D")
if idx != -1:
    print(content[idx : idx+1200])
