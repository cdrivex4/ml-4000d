with open('firmware/ROM1.BIN', 'rb') as f:
    rom = f.read()

for pattern in [b'RegisterPtp', b'ptp_register', b'PtpHandler', b'PtpProp', b'ptpPropSetUILock', b'PTP']:
    pos = 0
    found = 0
    while found < 10:
        idx = rom.find(pattern, pos)
        if idx == -1:
            break
        print(f'Found {pattern.decode("latin1")} at 0x{0xFE000000 + idx:X}: {rom[idx:idx+32]}')
        pos = idx + len(pattern)
        found += 1
