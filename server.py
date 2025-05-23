import socket
import threading

clients = []

def handle_client(conn, addr):
    print(f"New connection from {addr}")
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break
            # Broadcast received message to all other clients
            for client in clients:
                if client != conn:
                    client.sendall(data)
        except:
            break
    print(f"Connection closed from {addr}")
    clients.remove(conn)
    conn.close()

def main():
    host = 'localhost'  # Listen on all interfaces
    port = 8000
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((host, port))
        server.listen()
        print(f"Server listening on {host}:{port}")
        while True:
            conn, addr = server.accept()
            clients.append(conn)
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()
