import re
# stubs: the Canon function at 0xFE292FEC is vsprintf(buf, fmt, ap) - rename it
p = 'magic-lantern-1300d/platform/4000D.100/stubs.S'
s = open(p, 'r', encoding='utf-8', newline='').read()
assert 'NSTUB(0xFE292FEC,  vsnprintf)' in s
s = s.replace('NSTUB(0xFE292FEC,  vsnprintf)',
              'NSTUB(0xFE292FEC,  vsprintf_canon)                          // really vsprintf(buf, fmt, ap) - NO size arg!')
open(p, 'w', encoding='utf-8', newline='').write(s)

p = 'magic-lantern-1300d/src/stdio.c'
s = open(p, 'r', encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in s else '\n'
s = s.replace('\r\n', '\n')
marker = 'int\nsnprintf(\n'
assert marker in s
impl = '''#if defined(CONFIG_4000D)
/* 4000D: the only Canon formatter we found is vsprintf(buf, fmt, ap) (no size).
 * Emulate Canon's vsnprintf semantics: writes at most n chars + NUL (n+1 bytes). */
extern int vsprintf_canon(char* buf, const char* fmt, va_list ap);

int vsnprintf(char* str, size_t n, const char* fmt, va_list ap)
{
    char tmp[640];
    tmp[0] = 0;
    vsprintf_canon(tmp, fmt, ap);
    tmp[sizeof(tmp) - 1] = 0;
    int len = 0;
    while (tmp[len]) len++;
    if (str)
    {
        size_t m = ((size_t)len < n) ? (size_t)len : n;
        for (size_t i = 0; i < m; i++) str[i] = tmp[i];
        str[m] = 0;
    }
    return len;
}
#endif

'''
s = s.replace(marker, impl + marker, 1)
open(p, 'w', encoding='utf-8', newline='').write(s.replace('\n', nl))
print('ok')
