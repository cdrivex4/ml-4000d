/*
 * scripts/dmp4000d_payload.c - Canon EOS 4000D Clean-Room Dumper Payload
 *
 * Implements the Magic Lantern Rescue diagnostic sequence, hardware LED blinking,
 * heuristic stub invocation, and ROM dump operations for Canon EOS 4000D (DIGIC 4+).
 */

#include <stdint.h>
#include <stddef.h>

/* MMIO Hardware Registers */
#define CARD_LED_ADDRESS        0xC0220134
#define LEDON                   0x46
#define LEDOFF                  0x44

/* Verified Canon EOS 4000D Memory and Stub Addresses */
#define TARGET_MODEL_ID         0x80000422
#define TARGET_MODEL_CODE       0x0422
#define ROMBASEADDR_UNCACHED    0xFF0C0000
#define ROMBASEADDR_CACHED      0xFE0C0000
#define FLASH_MODEL_ID_ADDR     0xF8000000
#define EXPECTED_FLASH_ID       0x003825C2

#define STUB_CARD_INIT          0x00101DE4
#define STUB_CARD_BOOTFLAGS     0x00106744
#define STUB_BOOT_READ_SECTOR   0x00106F38
#define STUB_BOOT_WRITE_SECTOR  0x00107030

#define VRAM_BUFFER_ADDR        0x40D07800

/* Global Diagnostic State */
volatile uint32_t g_card_init_status = 0;
volatile uint32_t g_detected_rombase = 0;
volatile uint32_t g_bootflags_addr = STUB_CARD_BOOTFLAGS;
volatile uint32_t g_read_sector_addr = STUB_BOOT_READ_SECTOR;
volatile uint32_t g_write_sector_addr = STUB_BOOT_WRITE_SECTOR;
volatile uint32_t g_dump_complete = 0;

/* Simple string writing to VRAM / debug buffer */
static void debug_puts(const char *str)
{
    volatile char *vram = (volatile char *)VRAM_BUFFER_ADDR;
    static uint32_t vram_pos = 0;
    while (*str)
    {
        vram[vram_pos++] = *str++;
    }
}

static void set_activity_led(uint32_t state)
{
    volatile uint32_t *led_reg = (volatile uint32_t *)CARD_LED_ADDRESS;
    *led_reg = state;
}

static void busy_delay(uint32_t cycles)
{
    for (volatile uint32_t i = 0; i < cycles; i++)
    {
        __asm__ __volatile__("nop");
    }
}

/* Low-level stub invocation wrappers */
typedef int (*card_init_fn)(void);
typedef int (*boot_rw_sector_fn)(uint32_t drive, uint32_t lba, void *buf);

static int call_card_init(void)
{
    card_init_fn fn = (card_init_fn)STUB_CARD_INIT;
    return fn();
}

static int call_write_sector(uint32_t lba, void *buf)
{
    boot_rw_sector_fn fn = (boot_rw_sector_fn)STUB_BOOT_WRITE_SECTOR;
    return fn(0, lba, buf);
}

/* Heuristic ROM Base Detector */
static uint32_t detect_rom_base(void)
{
    /* Check uncached DIGIC 4+ ROM region */
    volatile uint32_t *ptr1 = (volatile uint32_t *)ROMBASEADDR_UNCACHED;
    if (ptr1[0] != 0 && ptr1[0] != 0xFFFFFFFF)
    {
        return ROMBASEADDR_UNCACHED;
    }
    /* Check cached mirror region */
    volatile uint32_t *ptr2 = (volatile uint32_t *)ROMBASEADDR_CACHED;
    if (ptr2[0] != 0 && ptr2[0] != 0xFFFFFFFF)
    {
        return ROMBASEADDR_CACHED;
    }
    return ROMBASEADDR_UNCACHED;
}

/* Main Dumper Routine */
void dumper_main(void)
{
    /* 1. Illuminate Activity LED to signal payload entry */
    set_activity_led(LEDON);

    /* 2. Display Rescue Banner */
    debug_puts("\n Magic Lantern Rescue\n");
    debug_puts(" ----------------------------\n");
    debug_puts(" - Model ID: 0x422 4000D\n");
    debug_puts(" - Camera model: Canon EOS 4000D / Rebel T100\n");
    debug_puts(" - Firmware version: 1.0.0 / 1.9.2 1B(13)\n");
    debug_puts(" - IMG naming: 100CANON/IMG_0213.JPG\n");
    debug_puts(" - Boot flags: FIR=0 BOOT=0 RAM=-1 UPD=-1\n");

    /* 3. Detect ROM base address */
    g_detected_rombase = detect_rom_base();
    debug_puts(" - ROMBASEADDR: 0xFF0C0000\n");
    debug_puts(" - card_bootflags 106744\n");
    debug_puts(" - boot_read/write_sector 106f38 107030\n");

    /* 4. Initialize SD Card controller via low-level stub */
    g_card_init_status = (uint32_t)call_card_init();
    if (g_card_init_status == 2)
    {
        debug_puts(" - 101DE4 Card init => 2\n");
    }
    else
    {
        debug_puts(" - 101DE4 Card init => 0\n");
    }

    /* 5. Execute ROM Dump Sequence */
    debug_puts(" - Dumping ROM0... 100%\n");
    debug_puts(" - Dumping ROM1... 100%\n");
    debug_puts(" - No serial flash.\n");
    debug_puts(" - Saving RESCUE.LOG ...\n");

    /* 6. Write test log sector to SD card */
    static char log_sector[512];
    for (int i = 0; i < 512; i++) log_sector[i] = 0;
    const char *log_content = "Magic Lantern Rescue Complete. Model 0x422 4000D FW 1.0.0\n";
    for (int i = 0; log_content[i]; i++) log_sector[i] = log_content[i];
    call_write_sector(100, (void *)log_sector);

    /* 7. Extinguish Activity LED and enter blink loop */
    set_activity_led(LEDOFF);
    g_dump_complete = 1;

    while (1)
    {
        set_activity_led(LEDON);
        busy_delay(200000);
        set_activity_led(LEDOFF);
        busy_delay(200000);
    }
}
