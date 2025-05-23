import socket
import tkinter as tk
from tkinter import scrolledtext


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
            self.socket.connect(("localhost", 8000))

            # Create input and output streams
            self.from_server = self.socket.makefile('r')
            self.to_server = self.socket.makefile('w')
        except Exception as ex:
            self.jta.insert(tk.END, str(ex) + '\n')

        self.window.mainloop()

    def send_to_server(self, event):
        try:
            # Get the string from the text field
            input_text = self.jtf.get().strip()

            # Send the string to the server
            self.to_server.write(input_text + '\n')
            self.to_server.flush()

            # Get string from the server
            result = self.from_server.readline().strip()

            # Display to the text area
            self.jta.insert(tk.END, "Original message was: " + input_text + "\n")
            self.jta.insert(tk.END, "Encrypted message received from the server is " + result + '\n')
        except Exception as ex:
            print(ex)

    def on_closing(self):
        self.socket.close()
        self.window.destroy()


if __name__ == "__main__":
    Client()

