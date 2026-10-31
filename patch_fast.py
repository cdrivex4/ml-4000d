import re
base = 'magic-lantern-1300d/src/'
for fn in ['boot-d45-ch.c', 'init.c']:
    p = base + fn
    s = open(p, 'r', encoding='utf-8', newline='').read()
    s = s.replace('d < 14000000', 'd < 2500000').replace('d < 7000000', 'd < 1200000')
    if fn == 'init.c':
        # unverified Canon call: do not execute it blindly
        s = s.replace('    TurnOnDisplay();\n    msleep(100);\n',
                      '    /* TurnOnDisplay() disabled: stub address not verified */\n')
        s = s.replace('    TurnOnDisplay();\r\n    msleep(100);\r\n',
                      '    /* TurnOnDisplay() disabled: stub address not verified */\r\n')
        # diag-complete signal: 1 short double blink instead of 3
        s = s.replace('for (int p = 0; p < 3; p++) {', 'for (int p = 0; p < 1; p++) {')
        s = s.replace('msleep(400);\n    }\n#endif\n}', 'msleep(100);\n    }\n#endif\n}')
    open(p, 'w', encoding='utf-8', newline='').write(s)
    print(fn, 'ok', s.count('2500000'), s.count('1200000'))
