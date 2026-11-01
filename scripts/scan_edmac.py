import capstone
import struct
import os

ROM_PATH = 'firmware/ROM1.BIN'
ROM_BASE = 0xFE000000
SET_EDMAC_ADDR = 0xFE276E40
CONNECT_WRITE_ADDR = 0xFE277340
CONNECT_READ_ADDR = 0xFE276FDC

with open(ROM_PATH, 'rb') as f:
    rom = f.read()

md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_ARM)
md.detail = True

def read_u32(addr):
    if ROM_BASE <= addr < ROM_BASE + len(rom):
        off = addr - ROM_BASE
        return struct.unpack('<I', rom[off:off+4])[0]
    return None

def find_string_near(addr, search_range=256):
    # Search backwards and forwards for ASCII strings
    start = max(0, addr - ROM_BASE - search_range)
    end = min(len(rom), addr - ROM_BASE + search_range)
    chunk = rom[start:end]
    strings = []
    curr = []
    for b in chunk:
        if 32 <= b <= 126:
            curr.append(chr(b))
        else:
            if len(curr) >= 4:
                s = "".join(curr)
                strings.append(s)
            curr = []
    return strings

def analyze_callsites(target_addr, target_name):
    print(f"\n=======================================================")
    print(f" Scanning calls to {target_name} (0x{target_addr:08X})")
    print(f"=======================================================")
    
    callsites = []
    for off in range(0, len(rom), 4):
        w = struct.unpack('<I', rom[off:off+4])[0]
        if (w >> 24) == 0xEB:
            imm24 = w & 0x00FFFFFF
            if imm24 & 0x00800000:
                imm24 -= 0x01000000
            pc = ROM_BASE + off + 8
            dest = pc + (imm24 << 2)
            if dest == target_addr:
                callsites.append(ROM_BASE + off)
                
    print(f"Total callsites found: {len(callsites)}")
    
    results = []
    for call_pc in callsites:
        # Disassemble 16 instructions before call
        call_off = call_pc - ROM_BASE
        start_off = max(0, call_off - 16 * 4)
        insns = list(md.disasm(rom[start_off:call_off+4], ROM_BASE + start_off))
        
        # Simple register state simulation
        regs = {}
        for insn in insns[:-1]: # up to the BL
            m = insn.mnemonic
            op = insn.op_str
            # mov rX, #val
            if m == 'mov':
                parts = op.split(',')
                if len(parts) == 2:
                    dst = parts[0].strip()
                    val_str = parts[1].strip()
                    if val_str.startswith('#'):
                        try:
                            regs[dst] = int(val_str[1:], 0)
                        except: pass
            # ldr rX, [pc, #off] or =val
            elif m == 'ldr':
                parts = op.split(',')
                if len(parts) == 2:
                    dst = parts[0].strip()
                    src = parts[1].strip()
                    if '[pc' in src:
                        # parse PC relative
                        # e.g. [pc, #0x123] or [pc, #-0x12]
                        try:
                            imm = 0
                            if '#' in src:
                                imm_str = src.split('#')[1].rstrip(']')
                                imm = int(imm_str, 0)
                            target_val_addr = insn.address + 8 + imm
                            val = read_u32(target_val_addr)
                            if val is not None:
                                regs[dst] = val
                        except: pass
                        
        r0 = regs.get('r0', None)
        r1 = regs.get('r1', None)
        r2 = regs.get('r2', None)
        
        # Nearby strings
        nearby_strings = find_string_near(call_pc, 128)
        keywords = [s for s in nearby_strings if any(k in s.lower() for k in ['evf', 'vram', 'yuv', 'live', 'raw', 'srm', 'edmac', 'disp', 'image', 'movie', 'rec', 'shoot'])]
        
        results.append({
            'pc': call_pc,
            'r0': r0,
            'r1': r1,
            'r2': r2,
            'keywords': keywords
        })
        
    # Print interesting callsites
    for res in results:
        pc_str = f"0x{res['pc']:08X}"
        r0_str = f"ch=0x{res['r0']:02X} ({res['r0']})" if res['r0'] is not None else "ch=?"
        r1_str = f"addr=0x{res['r1']:08X}" if res['r1'] is not None else "addr=?"
        r2_str = f"desc=0x{res['r2']:08X}" if res['r2'] is not None else "desc=?"
        kw_str = ", ".join(res['keywords'][:3]) if res['keywords'] else ""
        if res['keywords'] or (res['r0'] is not None and res['r0'] < 16):
            print(f"[{pc_str}] {r0_str:16s} | {r1_str:18s} | {r2_str:18s} | {kw_str}")

if __name__ == '__main__':
    analyze_callsites(SET_EDMAC_ADDR, "SetEDmac")
    analyze_callsites(CONNECT_WRITE_ADDR, "ConnectWriteEDmac")
    analyze_callsites(CONNECT_READ_ADDR, "ConnectReadEDmac")
