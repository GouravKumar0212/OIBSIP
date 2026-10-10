import string
import secrets
import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip

history = []


def get_character_pools():
    ambiguous = set("0Ool1I|")
    exclude = exclude_ambiguous_var.get()

    pools = {}

    if use_upper_var.get():
        chars = string.ascii_uppercase
        if exclude:
            chars = "".join(c for c in chars if c not in ambiguous)
        if chars:
            pools["upper"] = chars

    if use_lower_var.get():
        chars = string.ascii_lowercase
        if exclude:
            chars = "".join(c for c in chars if c not in ambiguous)
        if chars:
            pools["lower"] = chars

    if use_digits_var.get():
        chars = string.digits
        if exclude:
            chars = "".join(c for c in chars if c not in ambiguous)
        if chars:
            pools["digits"] = chars

    if use_symbols_var.get():
        chars = "!@#$%^&*()-_=+[]{}|;:,.<>?"
        if exclude:
            chars = "".join(c for c in chars if c not in ambiguous)
        if chars:
            pools["symbols"] = chars

    return pools


def evaluate_strength(password, types_count):
    length = len(password)
    if length < 10 or types_count < 3:
        return "Weak", "#d32f2f", 75
    elif length < 14 or types_count == 3:
        return "Medium", "#f57c00", 150
    else:
        return "Strong", "#2e7d32", 230


def generate_password():
    pools = get_character_pools()

    if len(pools) < 2:
        messagebox.showwarning("Invalid Selection", "Please select at least 2 character types.")
        return

    length = int(length_slider.get())
    if length < 8:
        messagebox.showerror("Invalid Length", "Password length must be at least 8 characters.")
        return

    password_chars = [secrets.choice(pool) for pool in pools.values()]

    combined_pool = "".join(pools.values())
    for _ in range(length - len(password_chars)):
        password_chars.append(secrets.choice(combined_pool))

    secrets.SystemRandom().shuffle(password_chars)
    password = "".join(password_chars)

    password_var.set(password)

    try:
        pyperclip.copy(password)
        status_label.config(text="Password generated and copied to clipboard!", fg="#2e7d32")
    except Exception:
        root.clipboard_clear()
        root.clipboard_append(password)
        status_label.config(text="Password generated and copied to clipboard!", fg="#2e7d32")

    level, color, bar_width = evaluate_strength(password, len(pools))
    strength_label.config(text=f"Strength: {level}", fg=color)
    strength_canvas.delete("all")
    strength_canvas.create_rectangle(0, 0, bar_width, 10, fill=color, outline="")

    history.insert(0, password)
    if len(history) > 5:
        history.pop()

    history_listbox.delete(0, tk.END)
    for pwd in history:
        history_listbox.insert(tk.END, pwd)


def copy_to_clipboard():
    password = password_var.get()
    if not password:
        messagebox.showwarning("Clipboard", "No password to copy. Generate a password first.")
        return

    try:
        pyperclip.copy(password)
    except Exception:
        root.clipboard_clear()
        root.clipboard_append(password)

    status_label.config(text="Password copied to clipboard!", fg="#2e7d32")


def copy_from_history(event):
    selected = history_listbox.curselection()
    if selected:
        pwd = history_listbox.get(selected[0])
        password_var.set(pwd)
        try:
            pyperclip.copy(pwd)
        except Exception:
            root.clipboard_clear()
            root.clipboard_append(pwd)
        status_label.config(text="Selected password copied to clipboard!", fg="#2e7d32")


def update_slider_label(val):
    slider_label.config(text=f"Password Length: {int(float(val))}")


root = tk.Tk()
root.title("Random Password Generator")
root.geometry("460x650")
root.resizable(False, False)
root.configure(bg="#f5f7fa")

tk.Label(
    root,
    text="Random Password Generator",
    font=("Arial", 16, "bold"),
    bg="#f5f7fa",
    fg="#2c3e50"
).pack(pady=(15, 10))

display_frame = tk.Frame(root, bg="#ffffff", bd=1, relief=tk.SOLID)
display_frame.pack(padx=20, pady=5, fill=tk.X)

password_var = tk.StringVar()
password_entry = tk.Entry(
    display_frame,
    textvariable=password_var,
    font=("Courier", 13, "bold"),
    justify="center",
    state="readonly",
    readonlybackground="#ffffff",
    relief=tk.FLAT,
    width=28
)
password_entry.pack(side=tk.LEFT, padx=10, pady=10, expand=True, fill=tk.X)

copy_icon_btn = tk.Button(
    display_frame,
    text="Copy",
    font=("Arial", 9, "bold"),
    bg="#2e7d32",
    fg="#ffffff",
    activebackground="#1b5e20",
    activeforeground="#ffffff",
    relief=tk.FLAT,
    command=copy_to_clipboard
)
copy_icon_btn.pack(side=tk.RIGHT, padx=10, pady=10)

strength_frame = tk.Frame(root, bg="#f5f7fa")
strength_frame.pack(pady=4)

strength_label = tk.Label(
    strength_frame,
    text="Strength: None",
    font=("Arial", 10, "bold"),
    bg="#f5f7fa",
    fg="#666666"
)
strength_label.pack()

strength_canvas = tk.Canvas(strength_frame, width=230, height=10, bg="#e0e0e0", highlightthickness=0)
strength_canvas.pack(pady=4)

status_label = tk.Label(
    root,
    text="Select criteria and click Generate",
    font=("Arial", 9),
    bg="#f5f7fa",
    fg="#666666"
)
status_label.pack(pady=(2, 6))

controls_frame = tk.Frame(root, bg="#ffffff", bd=1, relief=tk.SOLID)
controls_frame.pack(padx=20, pady=5, fill=tk.X)

slider_label = tk.Label(
    controls_frame,
    text="Password Length: 16",
    font=("Arial", 10, "bold"),
    bg="#ffffff",
    fg="#333333"
)
slider_label.pack(anchor="w", padx=15, pady=(10, 2))

length_slider = tk.Scale(
    controls_frame,
    from_=8,
    to=32,
    orient=tk.HORIZONTAL,
    bg="#ffffff",
    highlightthickness=0,
    command=update_slider_label
)
length_slider.set(16)
length_slider.pack(fill=tk.X, padx=15, pady=(0, 10))

options_label = tk.Label(
    controls_frame,
    text="Character Types (Select at least 2):",
    font=("Arial", 10, "bold"),
    bg="#ffffff",
    fg="#333333"
)
options_label.pack(anchor="w", padx=15, pady=(4, 2))

use_upper_var = tk.BooleanVar(value=True)
use_lower_var = tk.BooleanVar(value=True)
use_digits_var = tk.BooleanVar(value=True)
use_symbols_var = tk.BooleanVar(value=True)
exclude_ambiguous_var = tk.BooleanVar(value=False)

cb_frame = tk.Frame(controls_frame, bg="#ffffff")
cb_frame.pack(fill=tk.X, padx=15, pady=4)

tk.Checkbutton(cb_frame, text="Uppercase Letters (A-Z)", variable=use_upper_var, font=("Arial", 9), bg="#ffffff").grid(row=0, column=0, sticky="w", pady=2)
tk.Checkbutton(cb_frame, text="Lowercase Letters (a-z)", variable=use_lower_var, font=("Arial", 9), bg="#ffffff").grid(row=1, column=0, sticky="w", pady=2)
tk.Checkbutton(cb_frame, text="Numbers (0-9)", variable=use_digits_var, font=("Arial", 9), bg="#ffffff").grid(row=0, column=1, sticky="w", padx=10, pady=2)
tk.Checkbutton(cb_frame, text="Symbols (!@#$...)", variable=use_symbols_var, font=("Arial", 9), bg="#ffffff").grid(row=1, column=1, sticky="w", padx=10, pady=2)

tk.Checkbutton(
    controls_frame,
    text="Exclude Ambiguous Characters (0, O, l, 1, I)",
    variable=exclude_ambiguous_var,
    font=("Arial", 9),
    bg="#ffffff"
).pack(anchor="w", padx=15, pady=(4, 10))

action_frame = tk.Frame(root, bg="#f5f7fa")
action_frame.pack(pady=8)

generate_btn = tk.Button(
    action_frame,
    text="Generate Password",
    font=("Arial", 11, "bold"),
    bg="#1976d2",
    fg="#ffffff",
    activebackground="#1565c0",
    activeforeground="#ffffff",
    relief=tk.FLAT,
    width=18,
    pady=4,
    command=generate_password
)
generate_btn.grid(row=0, column=0, padx=6)

copy_btn = tk.Button(
    action_frame,
    text="Copy to Clipboard",
    font=("Arial", 11, "bold"),
    bg="#2e7d32",
    fg="#ffffff",
    activebackground="#1b5e20",
    activeforeground="#ffffff",
    relief=tk.FLAT,
    width=18,
    pady=4,
    command=copy_to_clipboard
)
copy_btn.grid(row=0, column=1, padx=6)

history_frame = tk.Frame(root, bg="#ffffff", bd=1, relief=tk.SOLID)
history_frame.pack(padx=20, pady=(6, 15), fill=tk.BOTH, expand=True)

tk.Label(
    history_frame,
    text="Session History (Last 5 Passwords - Click to copy):",
    font=("Arial", 9, "bold"),
    bg="#ffffff",
    fg="#555555"
).pack(anchor="w", padx=10, pady=(8, 4))

history_listbox = tk.Listbox(
    history_frame,
    font=("Courier", 10),
    height=5,
    bg="#fafafa",
    bd=1,
    relief=tk.SOLID
)
history_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 8))
history_listbox.bind("<Double-Button-1>", copy_from_history)
history_listbox.bind("<<ListboxSelect>>", copy_from_history)

if __name__ == "__main__":
    root.mainloop()
