# Real-Time Chat Application

A multi-room desktop chat application built with Python using TCP sockets, threading, Tkinter GUI, and SQLite database storage.

## Overview

This project consists of a server and a graphical client that allows multiple users to register, log in, chat in real time across multiple rooms, view past message history, and use emoji shortcodes.

## Features

- User Authentication: Secure registration and login system with passwords hashed using SHA-256.
- Real-Time Messaging: Bidirectional communication between connected clients using sockets and threading.
- Multiple Chat Rooms: Users can join default rooms (General, Tech, Random) or create custom rooms.
- Message History: Past messages for a room are automatically loaded from SQLite when a user joins.
- Timestamped Messages: Messages display the sender name and a timestamp prefix (for example: [14:35] Alice: Hello).
- In-App Notifications: Highlights unread messages, updates the window title, and sounds an alert when the application window is not focused.
- Emoji Shortcodes: Automatically converts common shortcodes (such as :smile:, :heart:, :thumbsup:, :fire:, :wave:) into Unicode symbols.
- Graceful Disconnection: Notifies other users in the room when a user leaves or disconnects.

## Security Transparency

As part of security awareness and transparency:

- Password Security: Passwords are never saved in plain text. They are hashed using SHA-256 before saving to the database.
- Message Storage: Chat messages are stored in plain text inside the server SQLite database file (chat_server.db) to support room history.
- Network Transmission: Messages and login credentials are transmitted over plain TCP sockets without TLS/SSL encryption.
- No End-to-End Encryption: The server processes and reads message contents to store history and broadcast to room members, meaning messages are not end-to-end encrypted.

## Requirements

- Python 3.x

The standard library modules used are socket, threading, json, sqlite3, hashlib, datetime, and tkinter. No third-party packages are required.

## How to Run

### Step 1: Start the Server

Open a terminal or command prompt in the project folder and start the server:

```bash
python server.py
```

The server will initialize the SQLite database and listen on 127.0.0.1:5555.

### Step 2: Start the Client

Open another terminal or command prompt in the same folder and launch the client:

```bash
python client.py
```

To test multi-user chat, open additional terminals and launch another client instance:

```bash
python client.py
```

### Step 3: Register and Chat

1. On the client window, enter a username and password.
2. Click "Register" to create your account.
3. Click "Login" to enter the chat interface.
4. Select a room from the sidebar or type a new room name and click "Join / Create Room".
5. Type your message in the bottom entry field and press Enter or click "Send".
