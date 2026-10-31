import os

repos = [
    r"d:\Dev\REverSE\4000D\magic-lantern-1300d",
    r"d:\Dev\REverSE\4000D\magic-lantern"
]

for repo in repos:
    print(f"\n--- Patching {os.path.basename(repo)} ---")
    
    # 1. Makefile.platform.default
    p_def = os.path.join(repo, "platform", "4000D.100", "Makefile.platform.default")
    if os.path.exists(p_def):
        content = open(p_def, "r", encoding="utf-8").read()
        new_content = """# 4000D 1.0.0

CANON_NAME_FIR      = 4000D100.FIR
FIRMWARE_ID         = 0x80000422

# 4000D uses single 32MB SPI flash mapped at 0xFE000000
ROMBASEADDR         = 0xFE0C0000
PLATFORM_ARCH       = armv5te

# Load ML at the end of the AllocateMemory pool
# Default 0x2D0000 - 0xD00000, patched to 0x2D0000 - 0xC80000 (512K for us).
RESTARTSTART        = 0xC80000
ML_BOOT_OBJ         = boot-d45-ch.o
ML_SRC_EXTRA_OBJS  += function_overrides.o
"""
        open(p_def, "w", encoding="utf-8", newline="").write(new_content)
        print("Updated Makefile.platform.default")

    # 2. internals.h
    p_int = os.path.join(repo, "platform", "4000D.100", "internals.h")
    if os.path.exists(p_int):
        c_int = open(p_int, "r", encoding="utf-8").read()
        # Ensure CONFIG_PROP_REQUEST_CHANGE is undef
        if "#define CONFIG_PROP_REQUEST_CHANGE" in c_int:
            c_int = c_int.replace("#define CONFIG_PROP_REQUEST_CHANGE", "#undef CONFIG_PROP_REQUEST_CHANGE")
        if "Camera internals for 1300D" in c_int:
            c_int = c_int.replace("Camera internals for 1300D 1.1.0", "Camera internals for 4000D 1.0.0")
        if "CONFIG_MENU_WITH_AV" not in c_int:
            c_int += "\n/** 4000D menu access via AV button (no dedicated trash button) **/\n#define CONFIG_MENU_WITH_AV\n"
        open(p_int, "w", encoding="utf-8", newline="").write(c_int)
        print("Updated internals.h")

    # 3. stubs.S
    p_stubs = os.path.join(repo, "platform", "4000D.100", "stubs.S")
    if os.path.exists(p_stubs):
        c_stubs = open(p_stubs, "r", encoding="utf-8").read()
        # Replace unverified 1300D addresses with 4000D verified addresses
        replacements = [
            ("NSTUB(0xFE11F394,  DryosDebugMsg)", "NSTUB(0xFE1171B4,  DryosDebugMsg)                           /* 4000D verified */"),
            ("NSTUB(   0x31170,  current_task)", "NSTUB(   0x2F53C,  current_task)                            /* 4000D verified */"),
            ("NSTUB(    0x38FC,  task_create)",  "NSTUB(    0x3888,  task_create)                             /* 4000D verified */"),
            ("NSTUB(0xFE5E7BDC,  PlayMovieGuideApp_handler)", "NSTUB(0xFE5DDE7C,  PlayMovieGuideApp_handler)"),
            ("// NSTUB(0xFE49AA14,  LiveViewWbApp_handler)", "NSTUB(0xFE49AA14,  LiveViewWbApp_handler)"),
            ("NSTUB(0xFE71C4D0,  SetCFnData)", "NSTUB(0xfe71c4d0,  SetCFnData)"),
        ]
        for old, new in replacements:
            if old in c_stubs:
                c_stubs = c_stubs.replace(old, new)
        
        # Add card_bootflags / boot sector stubs if not present
        if "card_bootflags" not in c_stubs:
            c_stubs += "\n/** Boot & Card I/O stubs (verified by a1ex in DMP4000D rescue log) **/\n"
            c_stubs += "NSTUB(  0x106744,  card_bootflags)\n"
            c_stubs += "NSTUB(  0x106F38,  boot_read_sector)\n"
            c_stubs += "NSTUB(  0x107030,  boot_write_sector)\n"
            c_stubs += "NSTUB(  0x101DE4,  sd_card_init)\n"
            
        open(p_stubs, "w", encoding="utf-8", newline="").write(c_stubs)
        print("Updated stubs.S")

    # 4. src/raw.c
    p_raw = os.path.join(repo, "src", "raw.c")
    if os.path.exists(p_raw):
        c_raw = open(p_raw, "r", encoding="utf-8").read()
        if "CONFIG_4000D" not in c_raw:
            # RAW_LV_EDMAC
            c_raw = c_raw.replace(
                "defined(CONFIG_1300D)\n#define RAW_LV_EDMAC 0xC0F26008",
                "defined(CONFIG_1300D) || defined(CONFIG_4000D)\n#define RAW_LV_EDMAC 0xC0F26008"
            )
            # RAW_PHOTO_EDMAC
            c_raw = c_raw.replace(
                "defined(CONFIG_1300D)\n#define RAW_PHOTO_EDMAC 0xc0f04008",
                "defined(CONFIG_1300D) || defined(CONFIG_4000D)\n#define RAW_PHOTO_EDMAC 0xc0f04008"
            )
            # CAM_COLORMATRIX1
            colormatrix_4000d = """#ifdef CONFIG_4000D
    #define CAM_COLORMATRIX1                       \\
      6461, 10000,     -907, 10000,    -882, 10000,\\
    -4300, 10000,    12184, 10000,    2378, 10000, \\
     -819, 10000,     1944, 10000,    5931, 10000
#endif
"""
            if "#ifdef CONFIG_1300D" in c_raw:
                idx = c_raw.find("#ifdef CONFIG_1300D")
                c_raw = c_raw[:idx] + colormatrix_4000d + c_raw[idx:]
            
            # dynamic ranges
            dr_4000d = """#ifdef CONFIG_4000D
static int dynamic_ranges[] = {1073, 1082, 1042, 1002, 926, 837, 728, 642};
#endif
"""
            if "#ifdef CONFIG_1300D" in c_raw:
                idx = c_raw.rfind("#ifdef CONFIG_1300D")
                c_raw = c_raw[:idx] + dr_4000d + c_raw[idx:]
                
            open(p_raw, "w", encoding="utf-8", newline="").write(c_raw)
            print("Updated src/raw.c")
        else:
            print("src/raw.c already has CONFIG_4000D")

    # 5. src/edmac-memcpy.c
    p_edmac = os.path.join(repo, "src", "edmac-memcpy.c")
    if os.path.exists(p_edmac):
        c_edmac = open(p_edmac, "r", encoding="utf-8").read()
        if "CONFIG_4000D" not in c_edmac:
            c_edmac = c_edmac.replace(
                "#elif defined(CONFIG_1300D)\nuint32_t edmac_read_chan = 0x19;",
                "#elif defined(CONFIG_1300D) || defined(CONFIG_4000D)\nuint32_t edmac_read_chan = 0x19;"
            )
            open(p_edmac, "w", encoding="utf-8", newline="").write(c_edmac)
            print("Updated src/edmac-memcpy.c")
        else:
            print("src/edmac-memcpy.c already has CONFIG_4000D")

    # 6. src/fw-signature.h
    p_sig = os.path.join(repo, "src", "fw-signature.h")
    if os.path.exists(p_sig):
        c_sig = open(p_sig, "r", encoding="utf-8").read()
        if "SIG_4000D_100" not in c_sig:
            c_sig = c_sig.replace(
                "#define SIG_1300D_110 0x3d8461b5",
                "#define SIG_1300D_110 0x3d8461b5\n#define SIG_4000D_100 0x56d44dd6"
            )
            open(p_sig, "w", encoding="utf-8", newline="").write(c_sig)
            print("Updated src/fw-signature.h")
        else:
            print("src/fw-signature.h already has SIG_4000D_100")

    # 7. src/propvalues.h
    p_prop = os.path.join(repo, "src", "propvalues.h")
    if os.path.exists(p_prop):
        c_prop = open(p_prop, "r", encoding="utf-8").read()
        if "MODEL_EOS_4000D" not in c_prop:
            c_prop = c_prop.replace(
                "#define MODEL_EOS_1300D  0x80000404",
                "#define MODEL_EOS_1300D  0x80000404\n#define MODEL_EOS_4000D  0x80000422"
            )
            open(p_prop, "w", encoding="utf-8", newline="").write(c_prop)
            print("Updated src/propvalues.h")
        else:
            print("src/propvalues.h already has MODEL_EOS_4000D")

print("\nFinished patching ML repositories.")
