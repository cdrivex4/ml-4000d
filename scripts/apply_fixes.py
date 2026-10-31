import os

path_boot = 'magic-lantern-1300d/src/boot.h'
with open(path_boot, 'r', encoding='utf-8') as f:
    text_boot = f.read()

old_boot = """#if defined(CONFIG_1300D) || defined(CONFIG_4000D)
// set patch.c (patch_instruction_jump) for more information
// allocate <patch_jump_size> bytes with the lowest address, try static, malloc or gcc_alloca or other.
    extern uint32_t  patch_jump_size __attribute__((weak));
    extern uint32_t *patch_jump_vector __attribute__((weak));
    extern void * _malloc( size_t len ) __attribute__((weak));
    if (&patch_jump_size && &patch_jump_vector && _malloc)
    {
        patch_jump_vector = (uint32_t*)_malloc(patch_jump_size); 
        qprintf("[BOOT] %s allocating jump vector size = %d at = %lx\\n", CAMERA_MODEL, patch_jump_size, patch_jump_vector);
    }
#endif"""

new_boot = """#if defined(CONFIG_1300D) || defined(CONFIG_4000D)
// patch_jump_vector is statically positioned at 0x100 (safe low-RAM gap within 32MB of ROM)
#endif"""

if old_boot in text_boot:
    text_boot = text_boot.replace(old_boot, new_boot, 1)
elif old_boot.replace('\n', '\r\n') in text_boot:
    text_boot = text_boot.replace(old_boot.replace('\n', '\r\n'), new_boot.replace('\n', '\r\n'), 1)
else:
    print('MISSING old_boot')

with open(path_boot, 'w', encoding='utf-8', newline='\n') as f:
    f.write(text_boot)
print('boot.h updated!')

path_patch = 'magic-lantern-1300d/src/patch.c'
with open(path_patch, 'r', encoding='utf-8') as f:
    text_patch = f.read()

old_jv = """#if defined(CONFIG_1300D) || defined(CONFIG_4000D)
// see patch_instruction_jump
uint32_t *patch_jump_vector;
const uint32_t patch_jump_size = 64*3;
typedef struct {
    uint32_t ins_trampoline;// trampoline instruction = LDR PC, [PC,#-4]
    uint32_t new_func_addr; // trampoline address
    uint32_t rom_func_addr; // for later identification
} jump_vector;
jump_vector *jump_vectors;
#endif"""

new_jv = """#if defined(CONFIG_1300D) || defined(CONFIG_4000D)
// see patch_instruction_jump
// Low-RAM gap 0x100..0x400 is untouched by DryOS and within +31.25MB of all ROM addresses
typedef struct {
    uint32_t ins_trampoline;// trampoline instruction = LDR PC, [PC,#-4]
    uint32_t new_func_addr; // trampoline address
    uint32_t rom_func_addr; // for later identification
} jump_vector;
const uint32_t patch_jump_size = 64 * sizeof(jump_vector);
uint32_t *patch_jump_vector = (uint32_t*)0x100;
jump_vector *jump_vectors = (jump_vector*)0x100;
#endif"""

if old_jv in text_patch:
    text_patch = text_patch.replace(old_jv, new_jv, 1)
elif old_jv.replace('\n', '\r\n') in text_patch:
    text_patch = text_patch.replace(old_jv.replace('\n', '\r\n'), new_jv.replace('\n', '\r\n'), 1)
else:
    print('MISSING old_jv')

old_unpatch = """#if defined(CONFIG_1300D) || defined(CONFIG_4000D)
		else
		{
			int logging_slot = -1;
			for (int ii = 0; ii < COUNT(logging_hooks); ii++)
			{
				if (logging_hooks[ii].addr != 0)
				{
					union logging_hook_code * hook = &logging_hooks[ii];
					if (patches[i].addr == &hook->jump_back)
					{
							unpatch_memory(patches[i].addr);
							break;
					}
				}
			}
			p = i;
			break;
		}
#endif"""

if old_unpatch in text_patch:
    text_patch = text_patch.replace(old_unpatch, '', 1)
elif old_unpatch.replace('\n', '\r\n') in text_patch:
    text_patch = text_patch.replace(old_unpatch.replace('\n', '\r\n'), '', 1)
else:
    print('MISSING old_unpatch')

old_init = """#if defined(CONFIG_1300D) || defined(CONFIG_4000D)
    // memset jump_vector
    memset(patch_jump_vector,0,patch_jump_size);

    // align jump_vector
    if (((uint32_t)patch_jump_vector) % 4 !=0)
      patch_jump_vector = (uint32_t *)((((uint32_t)patch_jump_vector)+4) & ~3);

    // initialize jumpvectors
    jump_vectors = (jump_vector *)patch_jump_vector;
#endif"""

new_init = """#if defined(CONFIG_1300D) || defined(CONFIG_4000D)
    if (patch_jump_vector)
    {
        // memset jump_vector in safe low RAM
        memset(patch_jump_vector, 0, patch_jump_size);

        // align jump_vector
        if (((uint32_t)patch_jump_vector) % 4 != 0)
            patch_jump_vector = (uint32_t *)((((uint32_t)patch_jump_vector)+4) & ~3);

        // initialize jumpvectors
        jump_vectors = (jump_vector *)patch_jump_vector;
    }
#endif"""

if old_init in text_patch:
    text_patch = text_patch.replace(old_init, new_init, 1)
elif old_init.replace('\n', '\r\n') in text_patch:
    text_patch = text_patch.replace(old_init.replace('\n', '\r\n'), new_init.replace('\n', '\r\n'), 1)
else:
    print('MISSING old_init')

with open(path_patch, 'w', encoding='utf-8', newline='\n') as f:
    f.write(text_patch)
print('patch.c updated!')
