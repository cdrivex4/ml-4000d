    .syntax unified
    .arm
    .section .text, "ax"
    .globl _start

_start:
    /* Polyglot header: works if invoked in either Thumb or ARM state */
    .code 16
    nop
    b       thumb_entry

    .code 32
arm_entry:
    b       main_start

    .code 16
thumb_entry:
    bx      pc
    nop

    .code 32
main_start:
    /* Switch to Supervisor Mode (0x13), disable IRQ and FIQ */
    mrs     r0, cpsr
    bic     r0, r0, #0x3F
    orr     r0, r0, #0xD3
    msr     cpsr, r0

    /* Verified 4000D Hardware Card LED Address from ROM1 (0xFE7FE250) */
    ldr     r0, =0xC022D1E0

    /* Verified 4000D LED Control Values from ROM1 (0xFE3D3234) */
    ldr     r3, =0x0093D800     /* LED ON */
    ldr     r4, =0x0083DC00     /* LED OFF */

blink_loop:
    /* Turn Activity LED ON */
    str     r3, [r0]

    /* Delay ~500ms (approx 35,000,000 cycles) */
    ldr     r2, =35000000
delay_on:
    subs    r2, r2, #1
    bne     delay_on

    /* Turn Activity LED OFF */
    str     r4, [r0]

    /* Delay ~500ms */
    ldr     r2, =35000000
delay_off:
    subs    r2, r2, #1
    bne     delay_off

    /* Repeat forever */
    b       blink_loop
