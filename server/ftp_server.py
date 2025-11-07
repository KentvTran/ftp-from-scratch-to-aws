import os, socket, threading, time

HOST = "127.0.0.1"  # localhost
CONTROL_PORT = 2121  # Local testing port
BUFFER_SIZE = 4096

BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "server_files")
os.makedirs(os.path.abspath(BASE_DIR), exist_ok=True)

def send_line(sock, s):
    if not s.endswith("\n"):
        s += "\n"
    sock.sendall(s.encode("utf-8"))

def open_data_listener():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))      # 빈 포트 자동 할당
    s.listen(1)
    return s, s.getsockname()[1]

def handle_ls(ctrl):
    d, port = open_data_listener()
    send_line(ctrl, f"200 OK PORT {port}")
    data_sock, _ = d.accept()
    try:
        rows = []
        for name in os.listdir(BASE_DIR):
            path = os.path.join(BASE_DIR, name)
            if os.path.isfile(path):
                size = os.path.getsize(path)
                mtime = int(os.path.getmtime(path))
                rows.append(f"{name} {size} {mtime}")
        text = ("\n".join(rows) + "\n") if rows else ""
        data_sock.sendall(text.encode("utf-8"))
    finally:
        data_sock.close()
        d.close()
    send_line(ctrl, "226 Listing complete")

def handle_get(ctrl, fn):
    name = os.path.basename(fn)
    path = os.path.join(BASE_DIR, name)
    if not os.path.isfile(path):
        send_line(ctrl, "550 File not found")
        return
    size = os.path.getsize(path)
    d, port = open_data_listener()
    send_line(ctrl, f"200 OK PORT {port} SIZE {size}")
    data_sock, _ = d.accept()
    try:
        with open(path, "rb") as f:
            while True:
                chunk = f.read(BUFFER_SIZE)
                if not chunk:
                    break
                data_sock.sendall(chunk)
    finally:
        data_sock.close()
        d.close()
    send_line(ctrl, "226 Transfer complete")

def handle_put(ctrl, fn, nbytes):
    name = os.path.basename(fn)
    path = os.path.join(BASE_DIR, name)
    n = int(nbytes)
    d, port = open_data_listener()
    send_line(ctrl, f"200 READY PORT {port}")
    data_sock, _ = d.accept()
    got = 0
    try:
        with open(path, "wb") as f:
            while got < n:
                chunk = data_sock.recv(min(BUFFER_SIZE, n - got))
                if not chunk:
                    break
                f.write(chunk)
                got += len(chunk)
    finally:
        data_sock.close()
        d.close()
    if got == n:
        send_line(ctrl, "226 File stored")
    else:
        send_line(ctrl, "550 Incomplete upload")

def handle_client(c, addr):
    try:
        # Send welcome message
        send_line(c, "220 Welcome to Simple FTP Server")
        
        while True:
            buf = b""
            while not buf.endswith(b"\n"):
                part = c.recv(BUFFER_SIZE)
                if not part:
                    return
                buf += part
            line = buf.decode("utf-8").strip()
            if not line:
                continue
            parts = line.split()
            cmd = parts[0].upper()
            if cmd == "LS":
                handle_ls(c)
            elif cmd == "GET" and len(parts) >= 2:
                handle_get(c, parts[1])
            elif cmd == "PUT" and len(parts) >= 4 and parts[2].upper() == "SIZE":
                handle_put(c, parts[1], parts[3])
            elif cmd == "EXIT":
                send_line(c, "221 Goodbye")
                return
            else:
                # Echo back the received command
                send_line(c, f"200 Echo: {line}")
    finally:
        try: c.close()
        except: pass

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, CONTROL_PORT))
        s.listen(5)
        print(f"[SERVER] Listening on {HOST}:{CONTROL_PORT}")
        while True:
            c, addr = s.accept()
            t = threading.Thread(target=handle_client, args=(c, addr), daemon=True)
            t.start()

if __name__ == "__main__":
    main()