import socket
from client.config import BUFFER_SIZE, TIMEOUT

class ControlConn:
    def __init__(self, host, port):
        self.addr = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(TIMEOUT)

    def __enter__(self):
        self.sock.connect(self.addr)
        return self

    def __exit__(self, a, b, c):
        try:
            self.sock.close()
        except:
            pass

    def send_line(self, text):
        if not text.endswith("\n"):
            text += "\n"
        self.sock.sendall(text.encode("utf-8"))

    def recv_line(self):
        data = b""
        # 서버가 줄바꿈으로 한 줄씩 주는 걸 가정합니다.
        while not data.endswith(b"\n"):
            chunk = self.sock.recv(BUFFER_SIZE)
            if not chunk:
                break
            data += chunk
        return data.decode("utf-8").strip()

def open_data_conn(host, port):
    # 파일 주고받는 데이터 소켓 여는 함수
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(TIMEOUT)
    s.connect((host, port))
    return s