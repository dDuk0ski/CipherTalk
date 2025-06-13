import socket
import threading
import tkinter as tk
from tkinter import scrolledtext


class Client:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Client")

        self.jtf = tk.Entry(self.window, justify='right', width=80)
        self.jtf.pack(side=tk.BOTTOM, padx=10, pady=20)

        self.jta = scrolledtext.ScrolledText(self.window, width=80, height=20)
        self.jta.pack(side=tk.TOP, padx=10, pady=10)

        self.jtf.bind("<Return>", self.send_to_server)  # Register listener

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.geometry("800x400")
        self.window.update()

        try:
            # Create a socket to connect to the server
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect(("localhost", 8000))
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
            msg = text.decode('utf-8')
            self.jta.insert(tk.END, msg + "\n")
        except Exception as ex:
            print(ex)

    def on_closing(self):
        self.socket.close()
        self.window.destroy()



if __name__ == "__main__":
    Client()