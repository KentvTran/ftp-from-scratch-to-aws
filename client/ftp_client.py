import os
import sys

from client.config import HOST, CONTROL_PORT, BUFFER_SIZE
from client.command_parser import parse_command
from client.connection_handler import ControlConn, open_data_conn
from shared import protocol

def do_ls(ctrl):
    # 기대 응답: "200 OK PORT <p>" → 데이터 소켓으로 목록 → "226 ..."
    ctrl.send_line("LS")
    first = ctrl.recv_line()
    if not first.startswith(protocol.OK):
        print("[ERR]", first)
        return

    # 포트 꺼내기 (형식: 200 OK PORT 20001)
    try:
        parts = first.split()
        p = int(parts[parts.index("PORT") + 1])
    except Exception:
        print("[ERR] Bad LS response:", first)
        return

    try:
        ds = open_data_conn(HOST, p)
        buf = b""
        while True:
            chunk = ds.recv(BUFFER_SIZE)
            if not chunk:
                break
            buf += chunk
        ds.close()
        text = buf.decode("utf-8", errors="replace").strip()
        if text:
            print(text)
        else:
            print("(empty)")
    except Exception as e:
        print("[ERR] LS data error:", e)
        return

    last = ctrl.recv_line()
    if not last.startswith(protocol.DONE):
        print("[WARN] expected 226, got:", last)

def do_get(ctrl, filename):
    # 기대 응답: "200 OK PORT <p> SIZE <n>" → 데이터 소켓으로 n바이트 수신 → "226 ..."
    ctrl.send_line(f"GET {filename}")
    first = ctrl.recv_line()
    if not first.startswith(protocol.OK):
        print("[ERR]", first)
        return

    try:
        parts = first.split()
        p = int(parts[parts.index("PORT") + 1])
        n = int(parts[parts.index("SIZE") + 1])
    except Exception:
        print("[ERR] Bad GET response:", first)
        return

    got = 0
    try:
        ds = open_data_conn(HOST, p)
        out_name = os.path.basename(filename)
        with open(out_name, "wb") as f:
            while got < n:
                chunk = ds.recv(min(BUFFER_SIZE, n - got))
                if not chunk:
                    break
                f.write(chunk)
                got += len(chunk)
        ds.close()
    except Exception as e:
        print("[ERR] GET data error:", e)
        return

    last = ctrl.recv_line()
    if last.startswith(protocol.DONE):
        print(f"[OK] Downloaded '{filename}' ({got} bytes)")
    else:
        print("[WARN] expected 226, got:", last)

def do_put(ctrl, filename):
    # 기대 흐름: "PUT <f> SIZE <n>" → 서버 "200 READY PORT <p>" → 데이터 소켓으로 전송 → "226 ..."
    size = os.path.getsize(filename)
    ctrl.send_line(f"PUT {filename} SIZE {size}")
    first = ctrl.recv_line()
    if not first.startswith(protocol.OK):
        print("[ERR]", first)
        return

    try:
        parts = first.split()
        p = int(parts[parts.index("PORT") + 1])
    except Exception:
        print("[ERR] Bad PUT response:", first)
        return

    sent = 0
    try:
        ds = open_data_conn(HOST, p)
        with open(filename, "rb") as f:
            while True:
                chunk = f.read(BUFFER_SIZE)
                if not chunk:
                    break
                ds.sendall(chunk)
                sent += len(chunk)
        ds.close()
    except Exception as e:
        print("[ERR] PUT data error:", e)
        return

    last = ctrl.recv_line()
    if last.startswith(protocol.DONE):
        print(f"[OK] Uploaded '{filename}' ({sent} bytes)")
    else:
        print("[WARN] expected 226, got:", last)

def repl(host, port):
    try:
        with ControlConn(host, port) as ctrl:
            print(f"Connected to {host}:{port}")
            print("Commands: LS | GET <file> | PUT <file> | EXIT")
            while True:
                try:
                    line = input("> ").strip()
                except (EOFError, KeyboardInterrupt):
                    line = "EXIT"

                cmd, args, err = parse_command(line)
                if err:
                    print("[ERR]", err)
                    continue

                if cmd == "EXIT":
                    ctrl.send_line("EXIT")
                    print("Bye.")
                    break
                elif cmd == "LS":
                    do_ls(ctrl)
                elif cmd == "GET":
                    do_get(ctrl, args["filename"])
                elif cmd == "PUT":
                    do_put(ctrl, args["filename"])
                else:
                    print("[ERR] unsupported:", cmd)
    except Exception as e:
        print("[ERR] Connect/Runtime:", e)

if __name__ == "__main__":
    h = HOST
    p = CONTROL_PORT
    if len(sys.argv) >= 2:
        h = sys.argv[1]
    if len(sys.argv) >= 3:
        p = int(sys.argv[2])
    repl(h, p)
