with open('d:/Dev/REverSE/4000D/magic-lantern-1300d/src/gui.c', 'rb') as f:
    content = f.read()

target = b"""            if (event->type == 0)
            {
                if (handle_buttons(event) == 0) { // ML button/event handler"""

replacement = b"""            if (event->type == 0)
            {
                #if defined(CONFIG_4000D)
                extern void log_button_event(int param, int arg);
                log_button_event(event->param, event->arg);
                #endif
                if (handle_buttons(event) == 0) { // ML button/event handler"""

content_norm = content.replace(b'\r\n', b'\n')
assert target in content_norm, 'target not found'
content_norm = content_norm.replace(target, replacement)
with open('d:/Dev/REverSE/4000D/magic-lantern-1300d/src/gui.c', 'wb') as f:
    f.write(content_norm.replace(b'\n', b'\r\n'))
print('Successfully patched src/gui.c')
