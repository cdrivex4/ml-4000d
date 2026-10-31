import os

with open('magic-lantern-1300d/src/init.c', 'rb') as f:
    raw = f.read()

# 1. Update log_button_event
old_btn = b'    if (bmp_vram_raw()) {\n        bmp_printf(FONT_LARGE, 20, 20, "BTN: 0x%02X (%d)   ", param, param);\n    }'
if old_btn not in raw:
    old_btn = old_btn.replace(b'\n', b'\r\n')

new_btn = b'    if (bmp_vram_raw()) {\n        uint8_t* v = bmp_vram_raw();\n        for (int y = 400; y < 445; y++) {\n            memset(v + y * 720 + 10, 0x0F, 700);\n        }\n        bmp_printf(FONT_LARGE, 25, 410, "KEY EVENT: 0x%02X (%3d) arg=0x%04X", param, param, arg);\n    }'
if b'\r\n' in old_btn:
    new_btn = new_btn.replace(b'\n', b'\r\n')

assert old_btn in raw, 'old_btn not found'
raw = raw.replace(old_btn, new_btn, 1)

# 2. Update run_diagnostic_tree Node 7
old_node7 = b'    /* BRANCH 7: Display Activation Attempt */\n    diags_log("\\n[TREE] Node 7: Hardware Display Activation Probe\\n");\n    extern void TurnOnDisplay(void);\n    diags_log("  - [7.1] Calling Canon TurnOnDisplay() (0xFE0CD740)...\\n");\n    /* TurnOnDisplay() disabled: stub address not verified */\n    diags_log("  - [7.2] TurnOnDisplay() completed successfully -> PASS\\n");'
if old_node7 not in raw:
    old_node7 = old_node7.replace(b'\n', b'\r\n')

new_node7 = b'    /* BRANCH 7: Display Activation Attempt */\n    diags_log("\\n[TREE] Node 7: Hardware Display Activation Probe\\n");\n    extern void TurnOnDisplay(void);\n    diags_log("  - [7.1] Calling Canon TurnOnDisplay() (0xFE0CD660)...\\n");\n    TurnOnDisplay();\n    diags_log("  - [7.2] TurnOnDisplay() completed successfully -> PASS\\n");'
if b'\r\n' in old_node7:
    new_node7 = new_node7.replace(b'\n', b'\r\n')

assert old_node7 in raw, 'old_node7 not found'
raw = raw.replace(old_node7, new_node7, 1)

# 3. Add startup banner
old_startup = b'    msleep(500);\n    ml_started = 1;\n    boot_log("[BOOT] SUCCESS: Magic Lantern UI is LIVE! (%d tasks started)\\n", ml_tasks);'
if old_startup not in raw:
    old_startup = old_startup.replace(b'\n', b'\r\n')

new_startup = b'''    msleep(500);
    ml_started = 1;
    boot_log("[BOOT] SUCCESS: Magic Lantern UI is LIVE! (%d tasks started)\\n", ml_tasks);

#if defined(CONFIG_4000D)
    TurnOnDisplay();
    if (bmp_vram_raw()) {
        uint8_t* v = bmp_vram_raw();
        for (int y = 0; y < 50; y++) {
            memset(v + y * 720, 0x0B, 720);
        }
        for (int y = 440; y < 480; y++) {
            memset(v + y * 720, 0x08, 720);
        }
        bmp_printf(FONT_LARGE, 15, 12, "MAGIC LANTERN LIVE - 4000D.100");
        bmp_printf(FONT_MED, 15, 452, "Autoboot Active | Press Q or DISP for Menu");
    }
#endif'''
if b'\r\n' in old_startup:
    new_startup = new_startup.replace(b'\n', b'\r\n')

assert old_startup in raw, 'old_startup not found'
raw = raw.replace(old_startup, new_startup, 1)

with open('magic-lantern-1300d/src/init.c', 'wb') as f:
    f.write(raw)

print('Updated init.c successfully!')
