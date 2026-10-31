import struct
b = open('firmware/ROM1.BIN','rb').read()
base = 0xFE000000
for off in range(0x200000, 0x300000, 4):
    w = struct.unpack_from('<I', b, off)[0]
    if (w >> 24) in (0xeb,):
        imm = w & 0xFFFFFF
        if imm & 0x800000: imm -= 0x1000000
        tgt = (base+off+8) + imm*4
        if tgt & 0xFFFFFFFF == 0x6644:
            print('call to 0x6644 at', hex(base+off))
