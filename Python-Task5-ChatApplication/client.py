import socket
import threading
import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

EMOJI_MAP = {
    ":smile:": "😊",
    ":happy:": "😊",
    ":heart:": "❤️",
    ":thumbsup:": "👍",
    ":fire:": "🔥",
    ":wave:": "👋",
    ":laughing:": "😂",
    ":joy:": "😂",
    ":wink:": "😉",
    ":cool:": "😎",
    ":star:": "⭐",
    ":sad:": "😢",
    ":check:": "✅"
}


def replace_emojis(text):
    for code, symbol in EMOJI_MAP.items():
        text = text.replace(code, symbol)
    return text


class ChatClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Application")
        self.root.geometry("450x550")
        self.root.resizable(False, False)
        self.root.configure(bg="#f5f7fa")

        self.sock = None
        self.username = None
        self.current_room = None
        self.is_focused = True
        self.unread_count = 0

        self.root.bind("<FocusIn>", self.on_focus_in)
        self.root.bind("<FocusOut>", self.on_focus_out)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.build_auth_ui()

    def on_focus_in(self, event=None):
        self.is_focused = True
        self.unread_count = 0
        if self.current_room:
            self.root.title(f"Chat Application - #{self.current_room}")
        if hasattr(self, "notif_bar"):
            self.notif_bar.config(text="")

    def on_focus_out(self, event=None):
        self.is_focused = False

    def build_auth_ui(self):
        self.auth_frame = tk.Frame(self.root, bg="#f5f7fa")
        self.auth_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        tk.Label(
            self.auth_frame,
            text="Chat Application",
            font=("Arial", 18, "bold"),
            bg="#f5f7fa",
            fg="#2c3e50"
        ).pack(pady=(10, 20))

        conn_box = tk.LabelFrame(self.auth_frame, text="Server Connection", font=("Arial", 9, "bold"), bg="#ffffff", padx=15, pady=10)
        conn_box.pack(fill=tk.X, pady=8)

        tk.Label(conn_box, text="Host:", font=("Arial", 9), bg="#ffffff").grid(row=0, column=0, sticky="w", pady=4)
        self.host_entry = tk.Entry(conn_box, font=("Arial", 10))
        self.host_entry.insert(0, "127.0.0.1")
        self.host_entry.grid(row=0, column=1, padx=10, pady=4, sticky="ew")

        tk.Label(conn_box, text="Port:", font=("Arial", 9), bg="#ffffff").grid(row=1, column=0, sticky="w", pady=4)
        self.port_entry = tk.Entry(conn_box, font=("Arial", 10))
        self.port_entry.insert(0, "5555")
        self.port_entry.grid(row=1, column=1, padx=10, pady=4, sticky="ew")

        conn_box.columnconfigure(1, weight=1)

        user_box = tk.LabelFrame(self.auth_frame, text="User Credentials", font=("Arial", 9, "bold"), bg="#ffffff", padx=15, pady=10)
        user_box.pack(fill=tk.X, pady=8)

        tk.Label(user_box, text="Username:", font=("Arial", 9), bg="#ffffff").grid(row=0, column=0, sticky="w", pady=4)
        self.username_entry = tk.Entry(user_box, font=("Arial", 10))
        self.username_entry.grid(row=0, column=1, padx=10, pady=4, sticky="ew")

        tk.Label(user_box, text="Password:", font=("Arial", 9), bg="#ffffff").grid(row=1, column=0, sticky="w", pady=4)
        self.password_entry = tk.Entry(user_box, font=("Arial", 10), show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=4, sticky="ew")

        user_box.columnconfigure(1, weight=1)

        btn_row = tk.Frame(self.auth_frame, bg="#f5f7fa")
        btn_row.pack(fill=tk.X, pady=15)

        self.login_btn = tk.Button(
            btn_row,
            text="Login",
            font=("Arial", 10, "bold"),
            bg="#1976d2",
            fg="#ffffff",
            activebackground="#1565c0",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            width=12,
            pady=4,
            command=self.handle_login
        )
        self.login_btn.pack(side=tk.LEFT, expand=True, padx=5)

        self.reg_btn = tk.Button(
            btn_row,
            text="Register",
            font=("Arial", 10, "bold"),
            bg="#2e7d32",
            fg="#ffffff",
            activebackground="#1b5e20",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            width=12,
            pady=4,
            command=self.handle_register
        )
        self.reg_btn.pack(side=tk.RIGHT, expand=True, padx=5)

        self.auth_status = tk.Label(self.auth_frame, text="", font=("Arial", 9), bg="#f5f7fa", fg="#d32f2f")
        self.auth_status.pack(pady=5)

    def connect_server(self):
        if self.sock:
            return True

        host = self.host_entry.get().strip()
        port_str = self.port_entry.get().strip()

        try:
            port = int(port_str)
        except ValueError:
            self.auth_status.config(text="Port must be an integer.", fg="#d32f2f")
            return False

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, port))
            t = threading.Thread(target=self.listen_server, daemon=True)
            t.start()
            return True
        except (socket.error, ConnectionRefusedError) as e:
            self.sock = None
            self.auth_status.config(text=f"Failed to connect to server: {e}", fg="#d32f2f")
            return False

    def send_json(self, data):
        if not self.sock:
            return
        try:
            msg = (json.dumps(data) + "\n").encode("utf-8")
            self.sock.sendall(msg)
        except (socket.error, BrokenPipeError):
            pass

    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            self.auth_status.config(text="Please enter username and password.", fg="#d32f2f")
            return

        if not self.connect_server():
            return

        self.send_json({"type": "login", "username": username, "password": password})

    def handle_register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            self.auth_status.config(text="Please enter username and password.", fg="#d32f2f")
            return

        if not self.connect_server():
            return

        self.send_json({"type": "register", "username": username, "password": password})

    def build_chat_ui(self, initial_rooms):
        self.auth_frame.destroy()
        self.root.geometry("750x550")
        self.root.resizable(True, True)

        main_box = tk.Frame(self.root, bg="#f5f7fa")
        main_box.pack(fill=tk.BOTH, expand=True)

        top_bar = tk.Frame(main_box, bg="#ffffff", bd=1, relief=tk.SOLID, height=35)
        top_bar.pack(fill=tk.X, side=tk.TOP)

        user_badge = tk.Label(
            top_bar,
            text=f"User: {self.username}",
            font=("Arial", 10, "bold"),
            bg="#ffffff",
            fg="#1976d2"
        )
        user_badge.pack(side=tk.LEFT, padx=12, pady=6)

        self.notif_bar = tk.Label(
            top_bar,
            text="",
            font=("Arial", 9, "bold"),
            bg="#ffffff",
            fg="#e65100"
        )
        self.notif_bar.pack(side=tk.RIGHT, padx=12, pady=6)

        content_pane = tk.Frame(main_box, bg="#f5f7fa")
        content_pane.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        sidebar = tk.Frame(content_pane, bg="#ffffff", bd=1, relief=tk.SOLID, width=190)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar,
            text="Rooms",
            font=("Arial", 11, "bold"),
            bg="#ffffff",
            fg="#2c3e50"
        ).pack(anchor="w", padx=10, pady=(10, 4))

        self.rooms_listbox = tk.Listbox(
            sidebar,
            font=("Arial", 10),
            bd=0,
            bg="#fafafa",
            selectbackground="#1976d2",
            selectforeground="#ffffff"
        )
        self.rooms_listbox.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)
        self.rooms_listbox.bind("<<ListboxSelect>>", self.on_select_room)

        self.update_rooms_list(initial_rooms)

        new_room_box = tk.Frame(sidebar, bg="#ffffff")
        new_room_box.pack(fill=tk.X, padx=8, pady=(4, 10))

        self.new_room_entry = tk.Entry(new_room_box, font=("Arial", 9))
        self.new_room_entry.pack(fill=tk.X, pady=(0, 4))

        join_room_btn = tk.Button(
            new_room_box,
            text="Join / Create Room",
            font=("Arial", 8, "bold"),
            bg="#37474f",
            fg="#ffffff",
            relief=tk.FLAT,
            command=self.create_or_join_room
        )
        join_room_btn.pack(fill=tk.X)

        chat_area = tk.Frame(content_pane, bg="#ffffff", bd=1, relief=tk.SOLID)
        chat_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.room_title_label = tk.Label(
            chat_area,
            text="# General",
            font=("Arial", 12, "bold"),
            bg="#ffffff",
            fg="#333333"
        )
        self.room_title_label.pack(anchor="w", padx=12, pady=(10, 4))

        self.chat_display = scrolledtext.ScrolledText(
            chat_area,
            wrap=tk.WORD,
            state="disabled",
            font=("Segoe UI", 10),
            bg="#fafafa",
            bd=1,
            relief=tk.SOLID
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=12, pady=4)

        self.chat_display.tag_config("system", foreground="#757575", font=("Segoe UI", 9, "italic"))
        self.chat_display.tag_config("own", foreground="#1565c0", font=("Segoe UI", 10, "bold"))
        self.chat_display.tag_config("other", foreground="#2e7d32", font=("Segoe UI", 10, "bold"))
        self.chat_display.tag_config("timestamp", foreground="#9e9e9e", font=("Segoe UI", 8))

        input_box = tk.Frame(chat_area, bg="#ffffff")
        input_box.pack(fill=tk.X, padx=12, pady=(4, 6))

        self.msg_entry = tk.Entry(input_box, font=("Segoe UI", 10))
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8), pady=4)
        self.msg_entry.bind("<Return>", self.send_message)

        send_btn = tk.Button(
            input_box,
            text="Send",
            font=("Arial", 10, "bold"),
            bg="#1976d2",
            fg="#ffffff",
            activebackground="#1565c0",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            width=8,
            command=self.send_message
        )
        send_btn.pack(side=tk.RIGHT, pady=4)

        hint_label = tk.Label(
            chat_area,
            text="Emojis supported: :smile:  :heart:  :thumbsup:  :fire:  :wave:  :star:  :wink:",
            font=("Arial", 8),
            bg="#ffffff",
            fg="#888888"
        )
        hint_label.pack(anchor="w", padx=12, pady=(0, 6))

        self.send_json({"type": "join_room", "room": "General"})

    def update_rooms_list(self, rooms):
        self.rooms_listbox.delete(0, tk.END)
        for r in rooms:
            self.rooms_listbox.insert(tk.END, r)

    def on_select_room(self, event=None):
        selection = self.rooms_listbox.curselection()
        if selection:
            target_room = self.rooms_listbox.get(selection[0])
            if target_room != self.current_room:
                self.send_json({"type": "join_room", "room": target_room})

    def create_or_join_room(self):
        new_room = self.new_room_entry.get().strip()
        if new_room:
            self.new_room_entry.delete(0, tk.END)
            self.send_json({"type": "join_room", "room": new_room})

    def append_chat(self, timestamp, sender, content, msg_type="other"):
        self.chat_display.config(state="normal")

        if msg_type == "system":
            self.chat_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
            self.chat_display.insert(tk.END, f"{content}\n", "system")
        else:
            tag = "own" if sender == self.username else "other"
            self.chat_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
            self.chat_display.insert(tk.END, f"{sender}: ", tag)
            self.chat_display.insert(tk.END, f"{content}\n")

        self.chat_display.config(state="disabled")
        self.chat_display.see(tk.END)

    def send_message(self, event=None):
        raw_text = self.msg_entry.get().strip()
        if not raw_text or not self.current_room:
            return

        text = replace_emojis(raw_text)
        self.msg_entry.delete(0, tk.END)
        self.send_json({"type": "message", "room": self.current_room, "content": text})

    def listen_server(self):
        buffer = ""
        while True:
            try:
                data = self.sock.recv(2048).decode("utf-8")
                if not data:
                    break
                buffer += data
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        payload = json.loads(line)
                        self.root.after(0, self.handle_server_message, payload)
                    except json.JSONDecodeError:
                        continue
            except (ConnectionResetError, socket.error):
                break

        self.root.after(0, self.on_server_disconnect)

    def handle_server_message(self, payload):
        msg_type = payload.get("type")

        if msg_type == "register_response":
            success = payload.get("success", False)
            msg = payload.get("message", "")
            if success:
                self.auth_status.config(text=msg, fg="#2e7d32")
            else:
                self.auth_status.config(text=msg, fg="#d32f2f")

        elif msg_type == "login_response":
            success = payload.get("success", False)
            if success:
                self.username = payload.get("username")
                rooms = payload.get("rooms", ["General"])
                self.build_chat_ui(rooms)
            else:
                msg = payload.get("message", "Login failed.")
                self.auth_status.config(text=msg, fg="#d32f2f")

        elif msg_type == "room_joined":
            self.current_room = payload.get("room")
            self.room_title_label.config(text=f"# {self.current_room}")
            self.root.title(f"Chat Application - #{self.current_room}")

            rooms = payload.get("rooms", [])
            if rooms:
                self.update_rooms_list(rooms)

            self.chat_display.config(state="normal")
            self.chat_display.delete("1.0", tk.END)
            self.chat_display.config(state="disabled")

            history = payload.get("history", [])
            for item in history:
                self.append_chat(item["timestamp"], item["sender"], item["content"])

        elif msg_type == "message":
            room = payload.get("room")
            if room == self.current_room:
                sender = payload.get("sender")
                content = payload.get("content")
                ts = payload.get("timestamp")
                self.append_chat(ts, sender, content)

                if sender != self.username:
                    if not self.is_focused:
                        self.unread_count += 1
                        self.root.title(f"({self.unread_count} New) Chat Application - #{self.current_room}")
                        self.root.bell()
                        if hasattr(self, "notif_bar"):
                            self.notif_bar.config(text=f"New message from {sender}")

        elif msg_type == "system":
            room = payload.get("room")
            if room == self.current_room:
                content = payload.get("content")
                ts = payload.get("timestamp")
                self.append_chat(ts, "System", content, msg_type="system")

        elif msg_type == "rooms_list":
            rooms = payload.get("rooms", [])
            self.update_rooms_list(rooms)

    def on_server_disconnect(self):
        messagebox.showerror("Disconnected", "Lost connection to the chat server.")
        self.sock = None

    def on_close(self):
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClientApp(root)
    root.mainloop()
