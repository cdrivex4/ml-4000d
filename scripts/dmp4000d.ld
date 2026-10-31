/*
 * scripts/dmp4000d.ld - Linker Script for Canon EOS 4000D Dumper Payload
 * Load and Execution Address: 0x001EF930 (as specified in FIR header offset 0xB4)
 * Target Architecture: ARMv5TE (DIGIC 4+ ARM946E-S)
 */

OUTPUT_FORMAT("elf32-littlearm", "elf32-bigarm", "elf32-littlearm")
OUTPUT_ARCH(arm)
ENTRY(_start)

MEMORY
{
    PAYLOAD_RAM (rwx) : ORIGIN = 0x001EF930, LENGTH = 0x10740
}

SECTIONS
{
    . = 0x001EF930;

    .text : {
        *(.text.entry)
        *(.text)
        *(.text.*)
    } > PAYLOAD_RAM

    .rodata : {
        *(.rodata)
        *(.rodata.*)
    } > PAYLOAD_RAM

    .data : {
        *(.data)
        *(.data.*)
    } > PAYLOAD_RAM

    .bss : {
        __bss_start = .;
        *(.bss)
        *(.bss.*)
        *(COMMON)
        __bss_end = .;
    } > PAYLOAD_RAM

    /DISCARD/ : {
        *(.comment)
        *(.note*)
        *(.ARM.*)
    }
}
