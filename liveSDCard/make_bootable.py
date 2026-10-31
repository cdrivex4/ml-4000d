"""
Make SD card bootable for Magic Lantern (Canon EOS 4000D / Rebel T100).
Writes EOS_DEVELOP at 0x47 and BOOTDISK at 0x5C in the Volume Boot Record.
Usage:
    python make_bootable.py [drive_letter]
Example:
    python make_bootable.py W
Note: Requires Administrator privileges to write directly to \\.\W:
"""
import sys

def make_bootable(drive_letter="W"):
    drive = drive_letter.rstrip(":\\/").upper()
    dev_path = rf"\\.\{drive}:"
    print(f"[*] Opening raw volume: {dev_path}")
    
    try:
        with open(dev_path, "r+b") as f:
            vbr = bytearray(f.read(512))
            if len(vbr) < 512:
                print("[-] Failed to read 512 bytes from VBR.")
                return False
                
            cur_eos = vbr[0x47:0x47+11].decode("latin1", errors="replace")
            cur_boot = vbr[0x5C:0x5C+8].decode("latin1", errors="replace")
            print(f"[*] Current status:")
            print(f"    Offset 0x47 (EOS_DEVELOP): '{cur_eos}'")
            print(f"    Offset 0x5C (BOOTDISK)   : '{cur_boot}'")
            
            if cur_eos == "EOS_DEVELOP" and cur_boot == "BOOTDISK":
                print("[+] CARD IS ALREADY BOOTABLE! Canon bootloader will load autoexec.bin.")
                return True
                
            print("[*] Injecting boot flags into sector 0...")
            vbr[0x47:0x47+11] = b"EOS_DEVELOP"
            vbr[0x5C:0x5C+8]  = b"BOOTDISK"
            
            f.seek(0)
            f.write(vbr)
            f.flush()
            print("[+] SUCCESS: Injected 'EOS_DEVELOP' and 'BOOTDISK' into Volume Boot Record!")
            print("[+] SD card is now 100% bootable for Magic Lantern.")
            return True
            
    except PermissionError:
        print("[-] Access Denied! Raw volume write requires Administrator rights.")
        print("    Right-click cmd.exe -> 'Run as administrator', then rerun this script.")
        return False
    except Exception as e:
        print(f"[-] Error: {e}")
        return False

if __name__ == "__main__":
    drv = sys.argv[1] if len(sys.argv) > 1 else "W"
    make_bootable(drv)
