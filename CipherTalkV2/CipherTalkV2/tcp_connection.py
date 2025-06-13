import socket

class TCPConnection:
    @staticmethod
    def send(ip: str, port: int, data: bytes):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip, port))
            s.sendall(data)

    @staticmethod
    def start_listener(port: int, handler):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', port))
            s.listen()
            while True:
                conn, addr = s.accept()
                handler(conn, addr)