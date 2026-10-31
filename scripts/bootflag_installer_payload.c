/*
 * scripts/bootflag_installer_payload.c - Canon EOS 4000D Bootflag Toggle Utility (Install / Uninstall)
 *
 * Runs via Canon Firmware Update menu at RAM address 0x001EF930.
 * Smart Toggle Behavior:
 *   - If BOOT == 0 (Currently Disabled):
 *       -> Enables BOOT flag (calls EnableBootDisk / card_bootflags(1)).
 *       -> Signals ENABLED with 10 rapid double-blinks.
 *   - If BOOT != 0 (Currently Enabled):
 *       -> Disables BOOT flag (calls DisableBootDisk / card_bootflags(0)).
 *       -> Signals DISABLED/REVERTED with 5 long slow blinks.
 * Writes audit log to SD card sector 120.
 */

#include <stdint.h>
#include <stddef.h>

#define CARD_LED_ADDRESS        0xC0220134
#define LEDON                   0x46
#define LEDOFF                  0x44

#define STUB_CARD_INIT          0x00101DE4
#define STUB_CARD_BOOTFLAGS     0x00106744
#define STUB_BOOT_WRITE_SECTOR  0x00107030

#define ROM_ENABLE_BOOT_DISK    0xFE116E10
#define ROM_DISABLE_BOOT_DISK   0xFE116E1C
#define NVRAM_BOOTDISK_ADDR     0xF8000004

typedef int (*card_init_fn)(void);
typedef int (*bootflag_fn)(int);
typedef int (*boot_write_fn)(uint32_t drive, uint32_t lba, void *buf);
typedef void (*evproc_fn)(void);

static void set_led(uint32_t state)
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

void dumper_main(void)
{
    /* 1. Turn LED solid ON immediately upon payload start */
    set_led(LEDON);

    /* 2. Initialize SD card hardware */
    card_init_fn card_init = (card_init_fn)STUB_CARD_INIT;
    card_init();

    /* 3. Check current bootflag state in camera EEPROM / NVRAM */
    volatile uint32_t *bootflag_ptr = (volatile uint32_t *)NVRAM_BOOTDISK_ADDR;
    uint32_t initial_state = *bootflag_ptr;

    bootflag_fn card_boot = (bootflag_fn)STUB_CARD_BOOTFLAGS;
    boot_write_fn write_sector = (boot_write_fn)STUB_BOOT_WRITE_SECTOR;
    static char log_buf[512];
    for (int i = 0; i < 512; i++) log_buf[i] = 0;

    if (initial_state == 0)
    {
        /* ========================================================
         * ACTION: ENABLE BOOTFLAG (BOOT=0 -> BOOT=1)
         * ======================================================== */
        /* Call flasher card_bootflags(1) */
        card_boot(1);

        /* Call ROM EnableBootDisk() eventprocedure (0xFE116E10) */
        evproc_fn enable_boot = (evproc_fn)ROM_ENABLE_BOOT_DISK;
        enable_boot();

        /* Redundant NVRAM write */
        *bootflag_ptr = 0xFFFFFFFF;

        /* Write audit log to SD card sector 120 */
        const char *msg = "4000D BOOTFLAG: ENABLED (Was 0 -> Now 1). Magic Lantern ready.\n";
        for (int i = 0; msg[i]; i++) log_buf[i] = msg[i];
        write_sector(0, 120, (void *)log_buf);

        /* Success Pattern: 10 rapid double-blinks */
        for (int k = 0; k < 10; k++)
        {
            set_led(LEDOFF); busy_delay(150000);
            set_led(LEDON);  busy_delay(150000);
            set_led(LEDOFF); busy_delay(150000);
            set_led(LEDON);  busy_delay(150000);
            set_led(LEDOFF); busy_delay(400000);
        }

        /* Steady heartbeat blink */
        while (1)
        {
            set_led(LEDON);  busy_delay(150000);
            set_led(LEDOFF); busy_delay(1350000);
        }
    }
    else
    {
        /* ========================================================
         * ACTION: DISABLE BOOTFLAG (BOOT!=0 -> BOOT=0 / UNINSTALL)
         * ======================================================== */
        /* Call flasher card_bootflags(0) */
        card_boot(0);

        /* Call ROM DisableBootDisk() eventprocedure (0xFE116E1C) */
        evproc_fn disable_boot = (evproc_fn)ROM_DISABLE_BOOT_DISK;
        disable_boot();

        /* Redundant NVRAM write */
        *bootflag_ptr = 0x00000000;

        /* Write audit log to SD card sector 120 */
        const char *msg = "4000D BOOTFLAG: DISABLED (Was 1 -> Now 0). Restored to 100% factory.\n";
        for (int i = 0; msg[i]; i++) log_buf[i] = msg[i];
        write_sector(0, 120, (void *)log_buf);

        /* Uninstalled Pattern: 5 long slow steady blinks (800ms on, 800ms off) */
        for (int k = 0; k < 5; k++)
        {
            set_led(LEDOFF); busy_delay(800000);
            set_led(LEDON);  busy_delay(800000);
        }
        set_led(LEDOFF);

        /* Off state: LED stays OFF with a very faint blip every 3 seconds */
        while (1)
        {
            set_led(LEDON);  busy_delay(30000);
            set_led(LEDOFF); busy_delay(3000000);
        }
    }
}
