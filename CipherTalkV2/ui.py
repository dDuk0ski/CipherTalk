import tkinter as tk
from tkinter import *

from code_service import CodeService
from friend_service import FriendService
from run import show_friends


class Client:
    def __init__(self, root):
        self.root = root
        self.root.title("CipherTalk ≽ܫ≼")
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.geometry("600x400")
        self.root.resizable(False, False)

        self.username_string = ""
        self.ip_string = ""

        self.sidebar = tk.Frame(self.root, bg="light gray")
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, ipady=5, ipadx=5)

        self.content_frame = tk.Frame(self.root, bg="black")
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.ui_side_bar()
        self.ui_content_frame()

    def ui_side_bar(self):
        self.clear_frame()

        friend_list = show_friends()
        for c in friend_list:
            icon = "🟢" if getattr(c, "online", False) else "⚪"
            tk.Button(self.sidebar, text=f"{icon} {c.username} @ {c.ip}:{c.port}", width=20)

        tk.Button(self.sidebar, text=f"Add friends", width=20, command=self.ui_show_friends).pack(side=tk.BOTTOM, pady=2)

    def ui_content_frame(self):
        self.animation_label = tk.Label(self.content_frame, text="Developing za cat animation", bg="black", fg="lime")
        self.animation_label.pack(expand=True)
        self.content_frame.after(3000, self.clear_text)

        self.ui_user()
        self.ui_generate_friend_code()

    def ui_generate_friend_code(self):
        def generate_code():
            ip_entry = tk.Entry(self.content_frame, width=40, bg="white")
            ip_entry.pack(expand=True, side=tk.BOTTOM, pady=60)
            placeholder = "Enter your public IP: "
            ip_entry.insert(0, placeholder)

            def on_focus_in(event):
                if ip_entry.get() == placeholder:
                    ip_entry.delete(0, tk.END)

            ip_entry.bind("<FocusIn>", on_focus_in)

            def on_focus_out(event):
                if ip_entry.get() == "":
                    ip_entry.insert(0, placeholder)

            ip_entry.bind("<FocusOut>", on_focus_out)

            def create_key(event):
                self.ip_string = ip_entry.get().strip()
                ip_entry.destroy()
                ip = tk.Label(self.content_frame, text=f"{self.ip_string}", bg="white")
                ip.place(x=360, y=45)

                # this shidded is broken
                if self.username_string != "":
                    scrollbar = tk.Scrollbar(self.content_frame)
                    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

                    generated_code_string = CodeService.generate_code(self.username_string, self.ip_string, 9000)
                    generated_code_entry = tk.Text(self.content_frame, width=40, height=3, wrap=tk.WORD, yscrollcommand=scrollbar.set)
                    generated_code_entry.pack(side=tk.BOTTOM, pady=50, fill=tk.Y)

                    scrollbar.config(command=generated_code_entry.yview)

                    generated_code_entry.insert(tk.END, generated_code_string)
                    generated_code_entry.config(state=tk.DISABLED)
                else:
                    set_user_before_ip = tk.Label(text="Set your nickname first!")
                    set_user_before_ip.place(x=400, y=45)
                    self.content_frame.after(5000, set_user_before_ip.destroy())

                code = tk.Text(self.content_frame, width=40, height=10, bg="white")

            ip_entry.bind("<Return>", create_key)

        tk.Button(self.content_frame, text="Generate ID code", width=20, command=generate_code).pack(side=tk.BOTTOM, pady=20)



    def ui_user(self):
        user_entry = tk.Entry(self.content_frame, width=40, bg="white")
        user_entry.pack(expand=True, side=tk.BOTTOM, pady=60)
        placeholder = "🔑 Enter your nickname: "
        user_entry.insert(0, placeholder)

        def on_focus_in(event):
            if user_entry.get() == placeholder:
                user_entry.delete(0, tk.END)
        user_entry.bind("<FocusIn>", on_focus_in)

        def on_focus_out(event):
            if user_entry.get() == "":
                user_entry.insert(0, placeholder)
        user_entry.bind("<FocusOut>", on_focus_out)

        def create_user(event):
            self.username_string = user_entry.get().strip()
            user_entry.destroy()
            username = tk.Label(self.content_frame, text=f"{self.username_string}", bg="white")
            username.place(x=360, y=10)

        user_entry.bind("<Return>", create_user)

    def ui_show_friends(self):
        friend_list = show_friends()
        for c in friend_list:
            icon = "🟢" if getattr(c, "online", False) else "⚪"
            # need to add chat window here
            tk.Button(self.sidebar, text=f"{icon} {c.username} \n @ {c.ip}:{c.port}", )

        self.sidebar_add_friend()

    def sidebar_add_friend(self):
        self.clear_frame()

        return_button = tk.Button(self.sidebar, text="<-", command=self.ui_side_bar)
        return_button.place(x=7, y=7)

        friend_id_text = tk.Entry(self.sidebar, width=20)
        placeholder = "Paste friend's ID code: "
        friend_id_text.place(x=17, y=40)
        friend_id_text.insert(0, placeholder)

        def on_focus_in(event):
            if friend_id_text.get() == placeholder:
                friend_id_text.delete(0, tk.END)
        friend_id_text.bind("<FocusIn>", on_focus_in)

        def on_focus_out(event):
            if friend_id_text.get() == "":
                friend_id_text.insert(0, placeholder)
        friend_id_text.bind("<FocusOut>", on_focus_out)

        def add_friend(event=None):
            friend_code = friend_id_text.get().strip()
            decoded = CodeService.decode_code(friend_code)
            try:
                FriendService.add_friend(decoded['username'], decoded['ip'], int(decoded['port']), decoded['public_key'])
                result = tk.Label(self.sidebar, text=f"Friend added succesfuly", wraplength=120, justify=tk.LEFT, width=20)
                result.place(x=7, y=65)
            except Exception as e:
                error = tk.Label(self.sidebar, text=f"\n❌ Invalid code: {e}\n", wraplength=120, justify=tk.LEFT, width=20)
                error.place(x=7, y=65)
        friend_id_text.bind("<Return>", add_friend)

    def clear_text(self):
        self.animation_label.config(text="")
    #     this is potentially redundant, I can just alter the text after a certain period
    #     im going to probably use a if loop that loops the animation only if there is no chat menu selected

    def clear_frame(self):
        for widget in self.sidebar.winfo_children():
            widget.destroy()

    def close(self):
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = Client(root)
    root.mainloop()
