"""
Canon EOS 4000D Smartphone-Mode PTP/IP Bootflag Disabler
Emulates Canon Camera Connect client over TCP port 15740,
unlocks event procedures, and disables the internal Magic Lantern bootflag (BOOT=0).
"""

import sys
import socket
import struct
import time

HOST = "192.168.1.212"
PORT = 15740

# Protocol Constants
PTPIP_INIT_COMMAND_REQ = 1
PTPIP_INIT_COMMAND_ACK = 2
PTPIP_INIT_EVENT_REQ = 3
PTPIP_INIT_EVENT_ACK = 4
PTPIP_COMMAND_REQUEST = 6
PTPIP_COMMAND_RESPONSE = 7
PTPIP_DATA_PACKET_START = 9
PTPIP_DATA_PACKET_END = 12

PTP_RC_OK = 0x2001
PTP_OC_OpenSession = 0x1002
PTP_OC_CloseSession = 0x1003
PTP_OC_EOS_EnableEventProc = 0x9050
PTP_OC_EOS_ExecuteEventProc = 0x9052

def main():
    target_ip = HOST
    if len(sys.argv) > 1:
        target_ip = sys.argv[1]

    print("=" * 64)
    print("   Canon EOS 4000D Smartphone-Mode PTP Bootflag DISABLER")
    print(f"   Target:      {target_ip}:{PORT}")
    print("   Action:      DisableBootDisk (BOOT=0)")
    print("=" * 64)

    client_guid = bytes.fromhex("42400001deadbeefcafebabe00000001")
    client_name = "iPhone\x00".encode("utf-16le")
    version = 0x00010000

    pkt_len = 8 + 16 + len(client_name) + 4
    pkt = struct.pack("<II16s", pkt_len, PTPIP_INIT_COMMAND_REQ, client_guid) + client_name + struct.pack("<I", version)

    s_cmd = None
    print(f"\n[*] Actively probing {target_ip}:{PORT}... (Turn on camera Wi-Fi / 'Connect to smartphone')")
    sys.stdout.flush()

    start_time = time.time()
    attempt = 0
    while time.time() - start_time < 300:
        attempt += 1
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.3)
        try:
            s.connect((target_ip, PORT))
            s_cmd = s
            break
        except Exception:
            s.close()
            if attempt % 5 == 0:
                elapsed = int(time.time() - start_time)
                sys.stdout.write(f"\r[*] Probing {target_ip}:{PORT}... [{elapsed}s/300s] (Waiting for camera Wi-Fi) ")
                sys.stdout.flush()
            time.sleep(0.2)

    if s_cmd is None:
        print("\n[-] Timeout waiting for camera connection.")
        sys.exit(1)

    print(f"\n\n[+] TCP CONNECTED TO CAMERA AT {target_ip}:{PORT}!")
    sys.stdout.flush()

    # Set 3-minute timeout for user to press [OK] on the camera
    s_cmd.settimeout(180.0)
    s_cmd.sendall(pkt)
    print(f"[+] Sent Init_Command_Req ({len(pkt)} bytes).")

    print("\n" + ">" * 64)
    print(" [!] CHECK CAMERA SCREEN: It should say 'Connect to iPhone?'")
    print("     PRESS THE [OK] / [SET] BUTTON ON THE CAMERA NOW!")
    print("     (Socket is holding open and waiting for your button press...)")
    print("<" * 64 + "\n")
    sys.stdout.flush()

    try:
        hdr = s_cmd.recv(8)
    except socket.timeout:
        print("[-] Timed out waiting for button press.")
        s_cmd.close()
        sys.exit(1)

    if len(hdr) < 8:
        print("[-] Socket closed by camera.")
        s_cmd.close()
        sys.exit(1)

    resp_len, resp_type = struct.unpack("<II", hdr)
    if resp_type != PTPIP_INIT_COMMAND_ACK:
        print(f"[-] Unexpected packet type {resp_type} (expected ACK)")
        s_cmd.close()
        sys.exit(1)

    ack_data = s_cmd.recv(resp_len - 8)
    conn_num = struct.unpack("<I", ack_data[:4])[0]
    cam_name = ack_data[20:-4].decode("utf-16le", errors="ignore").rstrip("\x00")
    print(f"\n[+] CAMERA ACK RECEIVED! Connected to '{cam_name}', Connection #{conn_num}")
    sys.stdout.flush()

    # Connect Event channel
    print("[*] Opening event channel...")
    s_evt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_evt.settimeout(10.0)
    s_evt.connect((target_ip, PORT))

    evt_req = struct.pack("<III", 12, PTPIP_INIT_EVENT_REQ, conn_num)
    s_evt.sendall(evt_req)
    evt_hdr = s_evt.recv(8)
    evt_len, evt_type = struct.unpack("<II", evt_hdr)
    if evt_type != PTPIP_INIT_EVENT_ACK:
        print(f"[-] Event channel failed with type {evt_type}")
        sys.exit(1)
    print("[+] Event channel established successfully!")
    sys.stdout.flush()

    # Open PTP Session
    tid = 1
    print(f"[*] Opening PTP Session (Session ID: 1, TID: {tid})...")
    s_cmd.sendall(struct.pack("<IIIHII", 22, PTPIP_COMMAND_REQUEST, 1, PTP_OC_OpenSession, tid, 1))
    resp = s_cmd.recv(1024)
    if len(resp) >= 10:
        code = struct.unpack("<H", resp[8:10])[0]
        if code != PTP_RC_OK:
            print(f"[-] OpenSession returned {hex(code)}")
            sys.exit(1)
    print("[+] PTP Session opened successfully (Response: 0x2001 OK)!")
    sys.stdout.flush()

    # Unlock Event Procedures (0x9050 x3)
    print("[*] Unlocking Canon Event Procedures (PTP 0x9050 x3)...")
    for i in range(1, 4):
        tid += 1
        s_cmd.sendall(struct.pack("<IIIHI", 18, PTPIP_COMMAND_REQUEST, 1, PTP_OC_EOS_EnableEventProc, tid))
        resp = s_cmd.recv(1024)
        code = struct.unpack("<H", resp[8:10])[0] if len(resp) >= 10 else 0
        print(f"    Pass {i}/3: Response {hex(code)}")
        sys.stdout.flush()

    # Execute DisableBootDisk (0x9052)
    tid += 1
    payload = b"DisableBootDisk\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    print(f"\n[*] Executing internal Event Procedure 'DisableBootDisk' (PTP 0x9052)...")
    sys.stdout.flush()
    s_cmd.sendall(struct.pack("<IIIHIII", 26, PTPIP_COMMAND_REQUEST, 2, PTP_OC_EOS_ExecuteEventProc, tid, 0, 0))
    s_cmd.sendall(struct.pack("<IIIQ", 20, PTPIP_DATA_PACKET_START, tid, len(payload)))
    s_cmd.sendall(struct.pack("<III", 12 + len(payload), PTPIP_DATA_PACKET_END, tid) + payload)

    resp = s_cmd.recv(1024)
    if len(resp) >= 10:
        code = struct.unpack("<H", resp[8:10])[0]
        if code == PTP_RC_OK:
            print("\n" + "=" * 64)
            print(" [SUCCESS] MAGIC LANTERN BOOTFLAG DISABLED! (BOOT=0)")
            print("=" * 64)
            print("\n[!] The internal camera NVRAM has been restored:")
            print("    Address 0xF8000004 set to 0x00000000 (BOOT=0)")
            print("    The camera will now boot purely stock firmware ignoring autoexec.bin.")
        else:
            print(f"[-] Execution returned response code: {hex(code)}")
    else:
        print("[-] Malformed response from camera.")

    try:
        tid += 1
        s_cmd.sendall(struct.pack("<IIIHI", 18, PTPIP_COMMAND_REQUEST, 1, PTP_OC_CloseSession, tid))
    except Exception:
        pass
    s_cmd.close()
    s_evt.close()
    print("\n[*] PTP Session closed. Done!")
    sys.stdout.flush()

if __name__ == "__main__":
    main()
