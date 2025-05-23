import socket
import threading
import tkinter as tk
import pyuac
import sys

from tkinter import scrolledtext

from win32comext.mapi.mapi import CLEAR_RN_PENDING
from win32comext.shell.shell import CLSID_Internet


class Client:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Client")

        # Panel to hold the label and text field
        self.label = tk.Label(self.window, text="Enter Text to be encrypted by a caesar cipher of shift 3")
        self.label.pack(side=tk.TOP, padx=10, pady=10)

        self.jtf = tk.Entry(self.window, justify='right')
        self.jtf.pack(side=tk.TOP, padx=10, pady=10)

        self.jta = scrolledtext.ScrolledText(self.window, width=80, height=20)
        self.jta.pack(side=tk.TOP, padx=10, pady=10)

        self.jtf.bind("<Return>", self.send_to_server)  # Register listener

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.geometry("800x400")
        self.window.update()

        try:
            # Create a socket to connect to the server
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect(("4.tcp.us-cal-1.ngrok.io", 11390))
            threading.Thread(target=self.listen_to_server, daemon=True).start()
        except Exception as ex:
            self.jta.insert(tk.END, str(ex) + '\n')

        self.window.mainloop()

    def send_to_server(self, event):
        try:
            # Get the string from the text field
            input_text = self.jtf.get().strip()
            buffer = input_text.encode('utf-8')
            self.socket.send(buffer)
        except Exception as ex:
            print(ex)

    def listen_to_server(self):
        try:
            while True:
                data = self.socket.recv(1064)
                if not data:
                    break
                self.jta.after(0, lambda d=data: self.receive_from_server(d))
        except Exception as ex:
            self.jta.insert(tk.END, str(ex) + '\n')

    def receive_from_server(self, text):
        try:
            self.jta.insert(tk.END, text)
        except Exception as ex:
            print(ex)

    def on_closing(self):
        self.socket.close()
        self.window.destroy()


if __name__ == "__main__":
    if not pyuac.isUserAdmin():
        pyuac.runAsAdmin()
        exit()
    Client()
