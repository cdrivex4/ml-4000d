import os

src_dir = r"d:\Dev\REverSE\4000D\magic-lantern-1300d\src"

def patch_file(rel_path, target, replacement):
    full_path = os.path.join(src_dir, rel_path)
    content = open(full_path, "r", encoding="utf-8").read()
    if target in content:
        content = content.replace(target, replacement, 1)
        open(full_path, "w", encoding="utf-8", newline="").write(content)
        print(f"Patched {rel_path}: '{target[:30]}...' -> '{replacement[:30]}...'")
    elif target.replace("\n", "\r\n") in content:
        content = content.replace(target.replace("\n", "\r\n"), replacement.replace("\n", "\r\n"), 1)
        open(full_path, "w", encoding="utf-8", newline="").write(content)
        print(f"Patched (CRLF) {rel_path}: '{target[:30]}...' -> '{replacement[:30]}...'")
    else:
        print(f"ALREADY PATCHED or NOT FOUND in {rel_path}: '{target[:30]}...'")

# 1. src/boot.h
patch_file("boot.h",
    "#ifdef CONFIG_1300D\n// set patch.c (patch_instruction_jump)",
    "#if defined(CONFIG_1300D) || defined(CONFIG_4000D)\n// set patch.c (patch_instruction_jump)"
)

# 2. src/patch.h
patch_file("patch.h",
    "#ifdef CONFIG_1300D\n/* use this patch on 1300D",
    "#if defined(CONFIG_1300D) || defined(CONFIG_4000D)\n/* use this patch on 1300D and 4000D"
)

# 3. src/patch.c
# 3.1 Line 78
patch_file("patch.c",
    "#ifdef CONFIG_1300D\n// see patch_instruction_jump\nuint32_t *patch_jump_vector;",
    "#if defined(CONFIG_1300D) || defined(CONFIG_4000D)\n// see patch_instruction_jump\nuint32_t *patch_jump_vector;"
)
# 3.2 Line 537
patch_file("patch.c",
    "#ifdef CONFIG_1300D\n\t\telse\n\t\t{\n\t\t\tint logging_slot = -1;",
    "#if defined(CONFIG_1300D) || defined(CONFIG_4000D)\n\t\telse\n\t\t{\n\t\t\tint logging_slot = -1;"
)
# 3.3 Line 597
patch_file("patch.c",
    "#ifdef CONFIG_1300D\n   // check is this patch was an double jump",
    "#if defined(CONFIG_1300D) || defined(CONFIG_4000D)\n   // check is this patch was an double jump"
)
# 3.4 Line 1006
patch_file("patch.c",
    "#ifndef CONFIG_1300D\n    /* check the jumps we are going to use */",
    "#if !defined(CONFIG_1300D) && !defined(CONFIG_4000D)\n    /* check the jumps we are going to use */"
)
# 3.5 Line 1046
patch_file("patch.c",
    "#ifdef CONFIG_1300D\n    /* Make the hooking code \"jump_back\" to use double jumping  */",
    "#if defined(CONFIG_1300D) || defined(CONFIG_4000D)\n    /* Make the hooking code \"jump_back\" to use double jumping  */"
)
# 3.6 Line 1078
patch_file("patch.c",
    "#ifdef CONFIG_1300D\n\n#define JUMP_BL 0\n#define JUMP_B  1\n\nint patch_instruction_jump",
    "#if defined(CONFIG_1300D) || defined(CONFIG_4000D)\n\n#define JUMP_BL 0\n#define JUMP_B  1\n\nint patch_instruction_jump"
)
# 3.7 Line 1497
patch_file("patch.c",
    "#ifdef CONFIG_1300D\n    // memset jump_vector",
    "#if defined(CONFIG_1300D) || defined(CONFIG_4000D)\n    // memset jump_vector"
)

# 4. src/tasks.h
# 4.1 Line 34
patch_file("tasks.h",
    "\t#ifdef CONFIG_1300D\n\t\tint get_task_info_by_id(int, void*);",
    "\t#if defined(CONFIG_1300D) || defined(CONFIG_4000D)\n\t\tint get_task_info_by_id(int, void*);"
)
# 4.2 Line 99
patch_file("tasks.h",
    "#if defined(CONFIG_DIGIC_78) || defined(CONFIG_1300D) // Maybe D678X?",
    "#if defined(CONFIG_DIGIC_78) || defined(CONFIG_1300D) || defined(CONFIG_4000D) // Maybe D678X?"
)
# 4.3 Line 130
patch_file("tasks.h",
    "#if defined(CONFIG_DIGIC_678) || defined(CONFIG_1300D)",
    "#if defined(CONFIG_DIGIC_678) || defined(CONFIG_1300D) || defined(CONFIG_4000D)"
)
# 4.4 Line 155
patch_file("tasks.h",
    "#ifdef CONFIG_1300D\n  char *name;                   // 0x34\n  unsigned int unknown_04;      // 0x38\n#else",
    "#if defined(CONFIG_1300D) || defined(CONFIG_4000D)\n  char *name;                   // 0x34\n  unsigned int unknown_04;      // 0x38\n#else"
)

# 5. src/flexinfo.c line 387
patch_file("flexinfo.c",
    "defined(CONFIG_1100D) || defined(CONFIG_1300D)\n    /* entry 1, max AUTO ISO */",
    "defined(CONFIG_1100D) || defined(CONFIG_1300D) || defined(CONFIG_4000D)\n    /* entry 1, max AUTO ISO */"
)

# 6. src/fps-engio.c line 1000
patch_file("fps-engio.c",
    "#if defined(CONFIG_1100D) || defined(CONFIG_1200D) || defined(CONFIG_1300D)\n                    f0 == 25 ? 30 :",
    "#if defined(CONFIG_1100D) || defined(CONFIG_1200D) || defined(CONFIG_1300D) || defined(CONFIG_4000D)\n                    f0 == 25 ? 30 :"
)

# 7. src/raw.c
# 7.1 Line 155
patch_file("raw.c",
    "#ifdef CONFIG_1300D\n#define DEFAULT_RAW_BUFFER MEM(MEM(0x37930 + 0x30))",
    "#if defined(CONFIG_1300D) || defined(CONFIG_4000D)\n#define DEFAULT_RAW_BUFFER MEM(MEM(0x37930 + 0x30))"
)
# 7.2 Line 222
patch_file("raw.c",
    "|| defined(CONFIG_7D) || defined(CONFIG_1300D)\n#define RAW_PHOTO_EDMAC 0xc0f04208",
    "|| defined(CONFIG_7D) || defined(CONFIG_1300D) || defined(CONFIG_4000D)\n#define RAW_PHOTO_EDMAC 0xc0f04208"
)
# 7.3 Line 452
patch_file("raw.c",
    "#ifdef CONFIG_1300D\n\t// PLACEHOLDER DATA FROM 600D TO BUILD HELLOWORLD",
    "#if defined(CONFIG_1300D) || defined(CONFIG_4000D)\n\t// PLACEHOLDER DATA FROM 600D TO BUILD HELLOWORLD"
)
# 7.4 Line 1041
patch_file("raw.c",
    "defined(CONFIG_1200D) || defined(CONFIG_1300D)\n        skip_left = 142;\n        skip_top = 52;",
    "defined(CONFIG_1200D) || defined(CONFIG_1300D) || defined(CONFIG_4000D)\n        skip_left = 142;\n        skip_top = 52;"
)

print("All src/ patches executed.")
