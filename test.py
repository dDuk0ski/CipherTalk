#!/usr/bin/env python3
import socket

HOST = "localhost"   # or the pwnat‐client’s IP
PORT = 8001          # your pwnat proxy port

with socket.socket() as sock:
    sock.connect((HOST, PORT))
    print(f"Connected to {HOST}:{PORT}")
    sock.sendall(b"Hello over pwnat!\n")
    # Try to receive a response (if you have echoing enabled)
    try:
        data = sock.recv(1024)
        print("Received back:", data)
    except:
        pass
