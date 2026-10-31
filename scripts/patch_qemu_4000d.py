import os

qemu_dir = r"d:\Dev\REverSE\4000D\qemu-eos"

# 1. Patch model_list.h
path_h = os.path.join(qemu_dir, "hw", "eos", "model_list.h")
content_h = open(path_h, "r", encoding="utf-8").read()
if "MODEL_NAME_4000D" not in content_h:
    target = '#define MODEL_NAME_2000D "2000D"'
    replacement = '#define MODEL_NAME_2000D "2000D"\n#define MODEL_NAME_4000D "4000D"'
    assert target in content_h, "target not found in model_list.h"
    content_h = content_h.replace(target, replacement, 1)
    open(path_h, "w", encoding="utf-8", newline="").write(content_h)
    print("Patched model_list.h")
else:
    print("model_list.h already patched")

# 2. Patch model_list.c
path_c = os.path.join(qemu_dir, "hw", "eos", "model_list.c")
content_c = open(path_c, "r", encoding="utf-8").read()
if "MODEL_NAME_4000D" not in content_c:
    target_needle = '        .name                   = MODEL_NAME_2000D,'
    assert target_needle in content_c, "2000D needle not in model_list.c"
    
    # find the end of 2000D entry (marked by "    },")
    idx = content_c.find(target_needle)
    idx_end = content_c.find("    },", idx) + len("    },")
    
    entry_4000d = """
    {
        .name                   = MODEL_NAME_4000D,
        .digic_version          = 4,
        .ram_size               = 0x10000000,   /* 256MB */
        .rom0_size              = 0x0,          /* 4000D has single 32MB ROM on ROM1, ROM0 unconnected */
        .rom1_size              = 0x02000000,   /* 32MB */
        .firmware_start         = 0xFE0C0000,
        .dryos_timer_id         = 1,            /* set to 10ms; run with -d io,int,v to find it */
        .dryos_timer_interrupt  = 0x09,         /* enabled right before setting the timer value */
        .mpu_request_register   = 0xC022D0C4,   /* written in mpu_send (run with -d io) */
        .mpu_request_bitmask    = 0x00100000,   /* 0x83DC00 request, 0x93D800 idle */
        .mpu_status_register    = 0xC022F484,   /* read in SIO3_ISR and MREQ_ISR (tst 0x40000) */
        .current_task_addr      = 0x2F53C,
        .sd_driver_interrupt    = 0x4B,
        .sd_dma_interrupt       = 0x32,
        .uart_rx_interrupt      = 0x38,
        .rtc_time_correct       = 0xFD,         /* RTC_TIME_CORRECT_CHANGE */
        .rtc_cs_register        = 0xC022D0B8,   /* GPIO set/cleared in rtc_read */
        .dedicated_movie_mode   = 1,
    },"""
    content_c = content_c[:idx_end] + entry_4000d + content_c[idx_end:]
    open(path_c, "w", encoding="utf-8", newline="").write(content_c)
    print("Patched model_list.c")
else:
    print("model_list.c already patched")

# 3. Patch eos.c
path_eos = os.path.join(qemu_dir, "hw", "eos", "eos.c")
content_eos = open(path_eos, "r", encoding="utf-8").read()
if "eos_4000D_machine_init" not in content_eos:
    # Add machine init
    target_init = "static void eos_2000D_machine_init(MachineClass *mc)\n{\n    mc->desc = \"Canon EOS 2000D\";\n    mc->init = eos_init;\n}"
    target_init_crlf = target_init.replace("\n", "\r\n")
    repl_init = target_init + "\n\nstatic void eos_4000D_machine_init(MachineClass *mc)\n{\n    mc->desc = \"Canon EOS 4000D\";\n    mc->init = eos_init;\n}"
    
    if target_init in content_eos:
        content_eos = content_eos.replace(target_init, repl_init, 1)
    elif target_init_crlf in content_eos:
        content_eos = content_eos.replace(target_init_crlf, repl_init.replace("\n", "\r\n"), 1)
    else:
        raise ValueError("eos_2000D_machine_init not found")
        
    # Add DEFINE_MACHINE
    target_def = "DEFINE_MACHINE(MODEL_NAME_2000D, eos_2000D_machine_init)"
    repl_def = target_def + "\nDEFINE_MACHINE(MODEL_NAME_4000D, eos_4000D_machine_init)"
    if target_def in content_eos:
        content_eos = content_eos.replace(target_def, repl_def, 1)
    else:
        raise ValueError("DEFINE_MACHINE for 2000D not found")
        
    # Add Flash Model ID check in eos_rom_write: 4000D expects 0x003825C2
    target_flash = """    if ((strcmp(s->model->name, MODEL_NAME_1300D) == 0)
        || (strcmp(s->model->name, MODEL_NAME_2000D) == 0)
    )
    {
        if (address == 0xF8000000 && size == 1 && value == 6)
        {
            // Reading flash model ID?
            // Startup code writes to this address, but expects to read
            // different values: C2 25 39, 20 BB 19 or 01 02 19.
            msg = "Flash model ID?";
            uint32_t model_id = 0x003925C2;
            MEM_WRITE_ROM(address, (uint8_t *) &model_id, 4);
            goto end;
        }
    }"""
    target_flash_crlf = target_flash.replace("\n", "\r\n")
    repl_flash = """    if ((strcmp(s->model->name, MODEL_NAME_1300D) == 0)
        || (strcmp(s->model->name, MODEL_NAME_2000D) == 0)
    )
    {
        if (address == 0xF8000000 && size == 1 && value == 6)
        {
            // Reading flash model ID?
            // Startup code writes to this address, but expects to read
            // different values: C2 25 39, 20 BB 19 or 01 02 19.
            msg = "Flash model ID?";
            uint32_t model_id = 0x003925C2;
            MEM_WRITE_ROM(address, (uint8_t *) &model_id, 4);
            goto end;
        }
    }
    else if (strcmp(s->model->name, MODEL_NAME_4000D) == 0)
    {
        if (address == 0xF8000000 && size == 1 && value == 6)
        {
            // 4000D uses Macronix MX25L25635E (ID: 0x003825C2)
            msg = "Flash model ID?";
            uint32_t model_id = 0x003825C2;
            MEM_WRITE_ROM(address, (uint8_t *) &model_id, 4);
            goto end;
        }
    }"""
    if target_flash in content_eos:
        content_eos = content_eos.replace(target_flash, repl_flash, 1)
    elif target_flash_crlf in content_eos:
        content_eos = content_eos.replace(target_flash_crlf, repl_flash.replace("\n", "\r\n"), 1)
    else:
        raise ValueError("Flash model check not found in eos.c")
        
    # Add System check bypass in case 0xF48C
    target_sys = "|| (strcmp(eos_state->model->name, MODEL_NAME_2000D) == 0)"
    repl_sys = "|| (strcmp(eos_state->model->name, MODEL_NAME_2000D) == 0)\n               || (strcmp(eos_state->model->name, MODEL_NAME_4000D) == 0)"
    if target_sys in content_eos:
        content_eos = content_eos.replace(target_sys, repl_sys, 1)
    else:
        raise ValueError("case 0xF48C not found in eos.c")
        
    open(path_eos, "w", encoding="utf-8", newline="").write(content_eos)
    print("Patched eos.c")
else:
    print("eos.c already patched")

# 4. Patch engine.c
path_eng = os.path.join(qemu_dir, "hw", "eos", "engine.c")
content_eng = open(path_eng, "r", encoding="utf-8").read()
if 'strcmp(eos_state->model->name, "4000D") == 0' not in content_eng:
    target_eng = '|| strcmp(eos_state->model->name, "2000D") == 0'
    repl_eng = '|| strcmp(eos_state->model->name, "2000D") == 0\n                    || strcmp(eos_state->model->name, "4000D") == 0'
    content_eng = content_eng.replace(target_eng, repl_eng)
    open(path_eng, "w", encoding="utf-8", newline="").write(content_eng)
    print("Patched engine.c")
else:
    print("engine.c already patched")

# 5. Patch mpu.c
path_mpu = os.path.join(qemu_dir, "hw", "eos", "mpu.c")
content_mpu = open(path_mpu, "r", encoding="utf-8").read()
if "MPU_SPELL_SET_OTHER_CAM(4000D" not in content_mpu:
    target_spell = "    MPU_SPELL_SET_OTHER_CAM(2000D, 600D)"
    repl_spell = "    MPU_SPELL_SET_OTHER_CAM(2000D, 600D)\n    MPU_SPELL_SET_OTHER_CAM(4000D, 600D)"
    content_mpu = content_mpu.replace(target_spell, repl_spell, 1)
    
    target_btn = "    MPU_BUTTON_CODES_OTHER_CAM(2000D, 1200D)"
    repl_btn = "    MPU_BUTTON_CODES_OTHER_CAM(2000D, 1200D)\n    MPU_BUTTON_CODES_OTHER_CAM(4000D, 1200D)"
    content_mpu = content_mpu.replace(target_btn, repl_btn, 1)
    
    open(path_mpu, "w", encoding="utf-8", newline="").write(content_mpu)
    print("Patched mpu.c")
else:
    print("mpu.c already patched")

print("All QEMU-EOS patches applied successfully!")
