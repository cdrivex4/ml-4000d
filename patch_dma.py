p = 'magic-lantern-1300d/src/init.c'
s = open(p, 'r', encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in s else '\n'
s = s.replace('\r\n', '\n')

# 1) route all log writes through a DMA-safe helper
s = s.replace('FIO_WriteFile(f, ', 'dbg_fwrite(f, ')

helper = r'''
/* ---- 4000D debug file helpers: write through a DMA (uncached) bounce buffer ----
 * Observed: CRASH.LOG had the right length but stale/garbage content, i.e. the SD
 * DMA did not see the data written by the CPU through the cached alias. */
extern void* _alloc_dma_memory(size_t size);
extern void _free_dma_memory(void* ptr);

static int dbg_fwrite(FILE* f, const void* p, size_t n)
{
    int ret = -1;
    void* d = _alloc_dma_memory(n + 32);
    if (d)
    {
        void* u = UNCACHEABLE(d);
        memcpy(u, p, n);
        ret = FIO_WriteFile(f, u, n);
        _free_dma_memory(d);
    }
    else
    {
        /* no heap: fall back to the uncached alias of the source */
        ret = FIO_WriteFile(f, UNCACHEABLE(p), n);
    }
    return ret;
}

/* writes 3 tiny files, each with a different buffer strategy; the pulled
 * contents tell us which strategy produces correct data on this camera */
static void fio_selftest(void)
{
    static char sbuf[64] = "METHOD A: cached static buffer, direct write\n";
    FILE* f;

    f = FIO_CreateFile("B:/ST_A.LOG");
    if (f) { FIO_WriteFile(f, sbuf, strlen(sbuf)); FIO_CloseFile(f); }

    static char sbuf2[64] = "METHOD B: uncached alias of static buffer\n";
    f = FIO_CreateFile("B:/ST_B.LOG");
    if (f) { FIO_WriteFile(f, UNCACHEABLE(sbuf2), strlen(sbuf2)); FIO_CloseFile(f); }

    static char sbuf3[64] = "METHOD C: DMA bounce buffer\n";
    f = FIO_CreateFile("B:/ST_C.LOG");
    if (f)
    {
        void* d = _alloc_dma_memory(128);
        if (d)
        {
            void* u = UNCACHEABLE(d);
            memcpy(u, sbuf3, strlen(sbuf3));
            FIO_WriteFile(f, u, strlen(sbuf3));
            _free_dma_memory(d);
        }
        FIO_CloseFile(f);
    }
}

'''
marker = 'static char boot_log_buf['
assert marker in s
s = s.replace(marker, helper + marker, 1)

# 2) run selftest first thing in my_big_init_task
t = 'static void my_big_init_task()\n{\n'
assert t in s
s = s.replace(t, t + '#if defined(CONFIG_4000D)\n    fio_selftest();\n#endif\n', 1)

open(p, 'w', encoding='utf-8', newline='').write(s.replace('\n', nl))
print('patched; dbg_fwrite uses:', s.count('dbg_fwrite('))
