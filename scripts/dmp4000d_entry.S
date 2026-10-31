/*
 * scripts/dmp4000d_entry.S - Low-Level ARM Bootstrap Entry for Canon EOS 4000D Dumper
 *
 * Targets ARM946E-S / ARMv5TE core in DIGIC 4+ processor.
 * Executed directly by Canon flasher routine after RAM loading at 0x001EF930.
 */

    .syntax unified
    .arm
    .section .text.entry, "ax"
    .globl _start

_start:
    /* Polyglot entry: Handle potential Thumb state invocation */
    .code 16
    nop                 /* In ARM: and r4, r1, r0, asr #13 (harmless) */
    b       thumb_entry

    .code 32
arm_entry:
    b       init_cpu

    .code 16
thumb_entry:
    bx      pc          /* Transition from Thumb mode to 32-bit ARM mode */
    nop

    .code 32
init_cpu:
    /* Set Supervisor Mode (M=10011) and disable IRQ (I=1) and FIQ (F=1) */
    mrs     r0, cpsr
    bic     r0, r0, #0x3F       /* Clear I, F, T and mode bits */
    orr     r0, r0, #0xD3       /* Set Mode=0x13 (Supervisor), I=1, F=1 */
    msr     cpsr, r0

    /* Set up a safe execution stack below payload */
    ldr     sp, =0x001E0000

    /* Clear BSS segment */
    ldr     r0, =__bss_start
    ldr     r1, =__bss_end
    mov     r2, #0
clear_bss_loop:
    cmp     r0, r1
    strlt   r2, [r0], #4
    blt     clear_bss_loop

    /* Branch to main C dumper implementation */
    b       dumper_main

    /* Fallback safety trap */
halt_loop:
    b       halt_loop
