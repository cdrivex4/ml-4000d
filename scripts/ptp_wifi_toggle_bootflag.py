"""
PTP/IP Wi-Fi Bootflag Installer & Toggle for Canon EOS 4000D
Connects to the camera via PTP/IP over Wi-Fi (Port 15740),
unlocks Canon EOS event procedures (0x9050), and executes
EnableBootDisk / DisableBootDisk (0x9052) to toggle the internal
camera bootflag (0xF8000004 -> BOOT=1 / BOOT=0).
"""

import sys
import time
import socket
import struct
import argparse

# Protocol Constants
PTPIP_INIT_COMMAND_REQ  = 1
PTPIP_INIT_COMMAND_ACK  = 2
PTPIP_INIT_EVENT_REQ    = 3
PTPIP_INIT_EVENT_ACK    = 4
PTPIP_INIT_FAIL         = 5
PTPIP_COMMAND_REQUEST   = 6
PTPIP_COMMAND_RESPONSE  = 7
PTPIP_EVENT             = 8
PTPIP_DATA_PACKET_START = 9
PTPIP_DATA_PACKET       = 10
PTPIP_CANCEL_TRANSACTION= 11
PTPIP_DATA_PACKET_END   = 12
PTPIP_PING              = 13
PTPIP_PONG              = 14

PTP_RC_OK               = 0x2001
PTP_OC_OpenSession      = 0x1002
PTP_OC_CloseSession     = 0x1003
PTP_OC_GetDeviceInfo    = 0x1001
PTP_OC_EOS_EnableEventProc  = 0x9050
PTP_OC_EOS_ExecuteEventProc = 0x9052
PTP_OC_EOS_GetEventProcReturnData = 0x9053

# Consistent Client GUID for pairing persistence
CLIENT_GUID = b'\x42\x00\x00\x40\x00\x00\x00\x01\xde\xad\xbe\xef\xca\xfe\xba\xbe'
CLIENT_NAME = "EOS-PC\x00"

def build_evproc_payload(command_name: str) -> bytes:
    """
    Constructs Canon EventProc argument frame:
    <command_name NUL> <uint32 argc=0> <uint32 str_table_len=0>
    """
    name_bytes = command_name.encode('ascii') + b'\x00'
    argc = 0
    str_len = 0
    return name_bytes + struct.pack('<II', argc, str_len)

class PtpIpClient:
    def __init__(self, host: str, port: int = 15740, timeout: float = 45.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.s_cmd = None
        self.s_evt = None
        self.conn_num = None
        self.camera_name = "Unknown"
        self.camera_guid = b""
        self.transaction_id = 0

    def next_tid(self) -> int:
        self.transaction_id += 1
        return self.transaction_id

    def connect(self) -> bool:
        sys.stdout.write(f"[*] Connecting to {self.host}:{self.port}...\n")
        sys.stdout.flush()
        
        self.s_cmd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s_cmd.settimeout(2.0)
        self.s_cmd.connect((self.host, self.port))
        
        # Connected! Set timeout for handshake / pairing prompt
        self.s_cmd.settimeout(self.timeout)

        client_name_bytes = CLIENT_NAME.encode('utf-16le')

        # CIPA DC-005 standard PTPIP_INIT_COMMAND_REQ:
        # uint32 length, uint32 type (1), uint8 guid[16], wchar client_name[N]
        pkt_len = 8 + 16 + len(client_name_bytes)
        pkt = struct.pack('<II16s', pkt_len, PTPIP_INIT_COMMAND_REQ, CLIENT_GUID) + client_name_bytes
        self.s_cmd.sendall(pkt)
        
        sys.stdout.write(f"[+] Sent Init_Command_Req ({len(pkt)} bytes). Waiting for camera ACK...\n")
        sys.stdout.write("    [!] IF CAMERA LCD ASKS TO CONNECT / PAIR: PRESS [SET] ON CAMERA!\n")
        sys.stdout.flush()

        # Receive PTPIP_INIT_COMMAND_ACK
        hdr = self._recv_exact(self.s_cmd, 8)
        resp_len, resp_type = struct.unpack('<II', hdr)
        if resp_type == PTPIP_INIT_FAIL:
            sys.stdout.write("[-] Camera sent PTPIP_INIT_FAIL (Pairing declined or busy).\n")
            return False
        elif resp_type != PTPIP_INIT_COMMAND_ACK:
            sys.stdout.write(f"[-] Unexpected command response type: {resp_type}\n")
            return False

        ack_data = self._recv_exact(self.s_cmd, resp_len - 8)
        self.conn_num = struct.unpack('<I', ack_data[:4])[0]
        self.camera_guid = ack_data[4:20]
        self.camera_name = ack_data[20:-4].decode('utf-16le', errors='ignore').rstrip('\x00')
        sys.stdout.write(f"[+] Connected! Camera: '{self.camera_name}', Conn #{self.conn_num}\n")
        sys.stdout.flush()

        # Connect Event channel
        self.s_evt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s_evt.settimeout(self.timeout)
        self.s_evt.connect((self.host, self.port))

        # PTPIP_INIT_EVENT_REQ
        evt_req = struct.pack('<III', 12, PTPIP_INIT_EVENT_REQ, self.conn_num)
        self.s_evt.sendall(evt_req)

        evt_hdr = self._recv_exact(self.s_evt, 8)
        evt_len, evt_type = struct.unpack('<II', evt_hdr)
        if evt_type != PTPIP_INIT_EVENT_ACK:
            sys.stdout.write(f"[-] Unexpected event response type: {evt_type}\n")
            return False

        sys.stdout.write("[+] Event channel established successfully!\n")
        sys.stdout.flush()
        return True

    def open_session(self, session_id: int = 1) -> bool:
        tid = self.next_tid()
        sys.stdout.write(f"[*] Opening PTP Session (Session ID: {session_id}, TID: {tid})...\n")
        sys.stdout.flush()
        pkt = struct.pack('<IIIHII', 22, PTPIP_COMMAND_REQUEST, 1, PTP_OC_OpenSession, tid, session_id)
        self.s_cmd.sendall(pkt)

        code, r_tid, _ = self._read_response()
        if code == PTP_RC_OK:
            sys.stdout.write("[+] PTP Session opened (Response: 0x2001 OK)!\n")
            sys.stdout.flush()
            return True
        else:
            sys.stdout.write(f"[-] OpenSession returned response code: {hex(code)}\n")
            sys.stdout.flush()
            return False

    def enable_event_procedures(self) -> bool:
        sys.stdout.write("[*] Unlocking Canon Event Procedures (PTP 0x9050 x3)...\n")
        sys.stdout.flush()
        for i in range(1, 4):
            tid = self.next_tid()
            pkt = struct.pack('<IIIHI', 18, PTPIP_COMMAND_REQUEST, 1, PTP_OC_EOS_EnableEventProc, tid)
            self.s_cmd.sendall(pkt)
            code, r_tid, _ = self._read_response()
            sys.stdout.write(f"    Pass {i}/3: TID {tid} -> Response {hex(code)}\n")
            sys.stdout.flush()
        return True

    def execute_event_procedure(self, proc_name: str) -> bool:
        tid = self.next_tid()
        payload = build_evproc_payload(proc_name)
        sys.stdout.write(f"[*] Executing Event Procedure: '{proc_name}' (TID: {tid})...\n")
        sys.stdout.flush()

        # 1. PTPIP_COMMAND_REQUEST with Data Phase = 2 (DATA OUT)
        cmd_pkt = struct.pack('<IIIHIII', 26, PTPIP_COMMAND_REQUEST, 2, PTP_OC_EOS_ExecuteEventProc, tid, 0, 0)
        self.s_cmd.sendall(cmd_pkt)

        # 2. PTPIP_DATA_PACKET_START
        start_pkt = struct.pack('<IIIQ', 20, PTPIP_DATA_PACKET_START, tid, len(payload))
        self.s_cmd.sendall(start_pkt)

        # 3. PTPIP_DATA_PACKET_END
        end_pkt = struct.pack('<III', 12 + len(payload), PTPIP_DATA_PACKET_END, tid) + payload
        self.s_cmd.sendall(end_pkt)

        # 4. PTPIP_COMMAND_RESPONSE
        code, r_tid, params = self._read_response()
        sys.stdout.write(f"[+] Response for '{proc_name}': Code = {hex(code)} ({'OK' if code == PTP_RC_OK else 'FAIL'})\n")
        sys.stdout.flush()
        return code == PTP_RC_OK

    def close(self):
        try:
            if self.s_cmd:
                tid = self.next_tid()
                pkt = struct.pack('<IIIHI', 18, PTPIP_COMMAND_REQUEST, 1, PTP_OC_CloseSession, tid)
                self.s_cmd.sendall(pkt)
        except Exception:
            pass
        finally:
            if self.s_cmd:
                try: self.s_cmd.close()
                except: pass
            if self.s_evt:
                try: self.s_evt.close()
                except: pass

    def _read_response(self):
        hdr = self._recv_exact(self.s_cmd, 8)
        resp_len, resp_type = struct.unpack('<II', hdr)
        if resp_type != PTPIP_COMMAND_RESPONSE:
            raise RuntimeError(f"Unexpected packet type {resp_type} waiting for response (expected {PTPIP_COMMAND_RESPONSE})")
        data = self._recv_exact(self.s_cmd, resp_len - 8)
        code = struct.unpack('<H', data[:2])[0]
        tid = struct.unpack('<I', data[2:6])[0]
        params = []
        for i in range(6, len(data), 4):
            if i + 4 <= len(data):
                params.append(struct.unpack('<I', data[i:i+4])[0])
        return code, tid, params

    def _recv_exact(self, sock, num_bytes):
        buf = bytearray()
        while len(buf) < num_bytes:
            chunk = sock.recv(num_bytes - len(buf))
            if not chunk:
                raise ConnectionResetError("Socket closed prematurely while waiting for data")
            buf.extend(chunk)
        return bytes(buf)

def auto_latch_loop(host: str, port: int, action: str, target_state: str, max_duration: int = 120):
    print("=" * 64)
    print("   Canon EOS 4000D Wi-Fi PTP/IP Fast Auto-Latch Utility")
    print(f"   Target:      {host}:{port}")
    print(f"   Action:      {action} -> {target_state}")
    print("   Mode:        Continuous Scanning & Instant Execution")
    print("=" * 64)
    print("\n[*] Listening for camera on the network... Turn on camera / Wi-Fi now!\n")

    start_time = time.time()
    last_print = 0

    while time.time() - start_time < max_duration:
        now = time.time()
        elapsed = int(now - start_time)
        if now - last_print >= 5:
            sys.stdout.write(f"\r[*] Scanning {host}:{port}... [{elapsed}s/{max_duration}s] (Activate camera Wi-Fi now) ")
            sys.stdout.flush()
            last_print = now

        client = PtpIpClient(host=host, port=port, timeout=30.0)
        try:
            # Fast probe (0.25s)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.25)
            s.connect((host, port))
            s.close()
        except (socket.timeout, ConnectionRefusedError, OSError):
            time.sleep(0.1)
            continue

        # Port is open! Instantly connect full client!
        print(f"\n\n[!!!] CAMERA DETECTED AT {host}:{port}! Latching on...")
        try:
            if not client.connect():
                print("[-] Handshake was not completed. Resuming scan...")
                time.sleep(0.5)
                continue

            if not client.open_session(1):
                print("[-] OpenSession rejected. Resuming scan...")
                time.sleep(0.5)
                continue

            client.enable_event_procedures()

            success = client.execute_event_procedure(action)
            if success:
                print("\n" + "=" * 64)
                print(f" [SUCCESS] Bootflag successfully set to: {target_state}!")
                print("=" * 64)
                if action == "EnableBootDisk":
                    print("\n[!] SUCCESSFUL ACTIVATION:")
                    print("    1. Turn camera power switch OFF.")
                    print("    2. Insert your 2GB SD card (with autoexec.bin and ML files).")
                    print("    3. Flip camera power switch ON.")
                    print("    -> Camera bootstraps Magic Lantern automatically!")
                else:
                    print("\n[!] Camera is now restored to stock Canon bootloader behavior.")
                return True
            else:
                print(f"\n[-] Execution of '{action}' returned error.")
                return False
        except Exception as e:
            print(f"\n[-] Exception during latch: {e}. Resuming scan...")
            time.sleep(0.5)
        finally:
            client.close()

    print("\n\n[-] Scan timed out after max duration.")
    return False

def main():
    parser = argparse.ArgumentParser(description="Canon EOS 4000D Wi-Fi Bootflag Utility")
    parser.add_argument("--host", default="192.168.1.212", help="Camera IP address")
    parser.add_argument("--port", type=int, default=15740, help="PTP/IP port")
    parser.add_argument("--enable", action="store_true", default=True, help="Enable bootflag (EnableBootDisk)")
    parser.add_argument("--disable", action="store_true", help="Disable bootflag (DisableBootDisk)")
    parser.add_argument("--duration", type=int, default=120, help="Scan duration in seconds")
    args = parser.parse_args()

    action = "DisableBootDisk" if args.disable else "EnableBootDisk"
    target_state = "DISABLED (BOOT=0)" if args.disable else "ENABLED (BOOT=1)"

    success = auto_latch_loop(args.host, args.port, action, target_state, max_duration=args.duration)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
