import socket
import threading
import json
import sqlite3
import hashlib
from datetime import datetime

HOST = "127.0.0.1"
PORT = 5555
DB_NAME = "chat_server.db"

clients = {}
client_rooms = {}
lock = threading.Lock()


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room TEXT NOT NULL,
            sender TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def register_user(username, password):
    if not username or not password:
        return False, "Username and password cannot be empty."

    pwd_hash = hash_password(password)
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, pwd_hash))
        conn.commit()
        conn.close()
        return True, "Registration successful."
    except sqlite3.IntegrityError:
        return False, "Username already exists."
    except sqlite3.Error as e:
        return False, f"Database error: {e}"


def login_user(username, password):
    pwd_hash = hash_password(password)
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ? AND password_hash = ?", (username, pwd_hash))
        row = cursor.fetchone()
        conn.close()
        if row:
            return True, "Login successful."
        return False, "Invalid username or password."
    except sqlite3.Error as e:
        return False, f"Database error: {e}"


def save_message(room, sender, content, timestamp):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (room, sender, content, timestamp) VALUES (?, ?, ?, ?)",
            (room, sender, content, timestamp),
        )
        conn.commit()
        conn.close()
    except sqlite3.Error:
        pass


def get_room_history(room, limit=30):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT sender, content, timestamp
            FROM messages
            WHERE room = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (room, limit),
        )
        rows = cursor.fetchall()
        conn.close()
        rows.reverse()
        history = [{"sender": r[0], "content": r[1], "timestamp": r[2]} for r in rows]
        return history
    except sqlite3.Error:
        return []


def get_active_rooms():
    with lock:
        rooms = set(client_rooms.values())
    rooms.add("General")
    rooms.add("Tech")
    rooms.add("Random")
    return sorted(list(rooms))


def send_json(sock, data):
    try:
        raw = (json.dumps(data) + "\n").encode("utf-8")
        sock.sendall(raw)
    except (socket.error, BrokenPipeError):
        pass


def broadcast_to_room(room, data, exclude_sock=None):
    with lock:
        recipients = [s for s, r in client_rooms.items() if r == room and s != exclude_sock]

    for s in recipients:
        send_json(s, data)


def handle_client(sock, addr):
    username = None
    current_room = None

    buffer = ""

    try:
        while True:
            data = sock.recv(2048).decode("utf-8")
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
                except json.JSONDecodeError:
                    continue

                action = payload.get("type")

                if action == "register":
                    req_user = payload.get("username", "").strip()
                    req_pwd = payload.get("password", "").strip()
                    success, msg = register_user(req_user, req_pwd)
                    send_json(sock, {"type": "register_response", "success": success, "message": msg})

                elif action == "login":
                    req_user = payload.get("username", "").strip()
                    req_pwd = payload.get("password", "").strip()
                    success, msg = login_user(req_user, req_pwd)
                    if success:
                        username = req_user
                        with lock:
                            clients[sock] = username
                        send_json(
                            sock,
                            {
                                "type": "login_response",
                                "success": True,
                                "message": msg,
                                "username": username,
                                "rooms": get_active_rooms(),
                            },
                        )
                    else:
                        send_json(sock, {"type": "login_response", "success": False, "message": msg})

                elif action == "join_room":
                    if not username:
                        continue

                    new_room = payload.get("room", "General").strip() or "General"
                    now_str = datetime.now().strftime("%H:%M")

                    if current_room:
                        broadcast_to_room(
                            current_room,
                            {
                                "type": "system",
                                "room": current_room,
                                "content": f"{username} left the room.",
                                "timestamp": now_str,
                            },
                            exclude_sock=sock,
                        )

                    current_room = new_room
                    with lock:
                        client_rooms[sock] = current_room

                    history = get_room_history(current_room)
                    send_json(
                        sock,
                        {
                            "type": "room_joined",
                            "room": current_room,
                            "history": history,
                            "rooms": get_active_rooms(),
                        },
                    )

                    broadcast_to_room(
                        current_room,
                        {
                            "type": "system",
                            "room": current_room,
                            "content": f"{username} joined the room.",
                            "timestamp": now_str,
                        },
                        exclude_sock=sock,
                    )

                elif action == "message":
                    if not username or not current_room:
                        continue

                    content = payload.get("content", "").strip()
                    if not content:
                        continue

                    now_str = datetime.now().strftime("%H:%M")
                    save_message(current_room, username, content, now_str)

                    msg_data = {
                        "type": "message",
                        "room": current_room,
                        "sender": username,
                        "content": content,
                        "timestamp": now_str,
                    }
                    broadcast_to_room(current_room, msg_data)

                elif action == "get_rooms":
                    send_json(sock, {"type": "rooms_list", "rooms": get_active_rooms()})

    except (ConnectionResetError, socket.error):
        pass
    finally:
        with lock:
            if sock in clients:
                del clients[sock]
            if sock in client_rooms:
                room_left = client_rooms[sock]
                del client_rooms[sock]
            else:
                room_left = None

        if username and room_left:
            now_str = datetime.now().strftime("%H:%M")
            broadcast_to_room(
                room_left,
                {
                    "type": "system",
                    "room": room_left,
                    "content": f"{username} disconnected.",
                    "timestamp": now_str,
                },
            )

        sock.close()


def start_server():
    init_db()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(10)
    print(f"Chat server running on {HOST}:{PORT}")

    try:
        while True:
            client_sock, client_addr = server.accept()
            t = threading.Thread(target=handle_client, args=(client_sock, client_addr), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print("\nShutting down server.")
    finally:
        server.close()


if __name__ == "__main__":
    start_server()
