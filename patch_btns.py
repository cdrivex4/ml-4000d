with open('d:/Dev/REverSE/4000D/magic-lantern-1300d/src/init.c', 'rb') as f:
    content = f.read()

target = b"""void log_gui_event(int type, int param, int arg, void* obj)
{
    static int evt_counter = 0;
    if (evt_counter < 100) {
        evt_counter++;
        boot_log("[EVENT #%d] type=%d param=0x%04X (%5d) arg=0x%04X obj=%p\\n",
                 evt_counter, type, param, param, arg, obj);
    }
}"""

replacement = b"""static char btn_log_buf[8192] = "";
static int btn_log_len = 0;

void log_button_event(int param, int arg)
{
    char tmp[128];
    int n = snprintf(tmp, sizeof(tmp), "[BTN] param=0x%02X (%3d) arg=0x%04X\\n",
                     param, param, arg);
    if (n > 0 && btn_log_len + n < (int)sizeof(btn_log_buf) - 1) {
        memcpy(btn_log_buf + btn_log_len, tmp, n);
        btn_log_len += n;
        btn_log_buf[btn_log_len] = '\\0';
        FILE* f = FIO_CreateFile("B:/BUTTONS.LOG");
        if (!f) f = FIO_CreateFile("A:/BUTTONS.LOG");
        if (!f) f = FIO_CreateFile("BUTTONS.LOG");
        if (f) {
            dbg_fwrite(f, btn_log_buf, btn_log_len);
            FIO_CloseFile(f);
        }
    }
    if (bmp_vram_raw()) {
        bmp_printf(FONT_LARGE, 20, 20, "BTN: 0x%02X (%d)   ", param, param);
    }
}"""

content_norm = content.replace(b'\r\n', b'\n')
assert target in content_norm, 'target not found'
content_norm = content_norm.replace(target, replacement)
with open('d:/Dev/REverSE/4000D/magic-lantern-1300d/src/init.c', 'wb') as f:
    f.write(content_norm.replace(b'\n', b'\r\n'))
print('Successfully patched src/init.c')
