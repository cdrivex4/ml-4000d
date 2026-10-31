with open('firmware/ROM1.BIN', 'rb') as f:
    rom = f.read()

for term in [b'ErrForCamera', b'DlgErrForCamera', b'Err 70', b'Err70', b'AJ_DIALOG.HANDLER_DlgErrForCamera', b'ErrCardForLVApp', b'ShootOlcApp', b'PlayMain', b'LiveViewApp']:
    pos = 0
    while True:
        idx = rom.find(term, pos)
        if idx == -1:
            break
        print(f'Found {term.decode("latin1")} at 0x{0xFE000000 + idx:X}')
        pos = idx + len(term)
