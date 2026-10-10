import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt

DB_NAME = "bmi_records.db"


def init_db():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS bmi_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                weight REAL NOT NULL,
                height REAL NOT NULL,
                bmi REAL NOT NULL,
                category TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
            """
        )
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Failed to initialize database: {e}")


def save_record(name, weight, height, bmi, category):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            """
            INSERT INTO bmi_history (name, weight, height, bmi, category, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (name, weight, height, bmi, category, now),
        )
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Failed to save record: {e}")


def calculate_bmi():
    name = name_entry.get().strip()
    weight_text = weight_entry.get().strip()
    height_text = height_entry.get().strip()

    if not name:
        messagebox.showerror("Input Error", "Please enter a user name.")
        return

    try:
        weight = float(weight_text)
        height = float(height_text)
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numeric values for weight and height.")
        return

    if weight <= 0:
        messagebox.showerror("Input Error", "Weight must be greater than 0.")
        return

    if height <= 0:
        messagebox.showerror("Input Error", "Height must be greater than 0.")
        return

    bmi = round(weight / (height ** 2), 2)

    if bmi < 18.5:
        category = "Underweight"
        color = "#1565c0"
    elif 18.5 <= bmi <= 24.9:
        category = "Normal"
        color = "#2e7d32"
    elif 25.0 <= bmi <= 29.9:
        category = "Overweight"
        color = "#ef6c00"
    else:
        category = "Obese"
        color = "#c62828"

    result_label.config(
        text=f"BMI: {bmi:.2f}\nCategory: {category}",
        fg=color
    )

    save_record(name, weight, height, bmi, category)


def clear_fields():
    name_entry.delete(0, tk.END)
    weight_entry.delete(0, tk.END)
    height_entry.delete(0, tk.END)
    result_label.config(text="", fg="#000000")


def delete_history():
    name = name_entry.get().strip()

    if name:
        confirm_text = f"Are you sure you want to delete all history for user '{name}'?"
    else:
        confirm_text = "Are you sure you want to delete all history records?"

    confirm = messagebox.askyesno("Confirm Delete", confirm_text)
    if not confirm:
        return

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        if name:
            cursor.execute("DELETE FROM bmi_history WHERE LOWER(name) = LOWER(?)", (name,))
        else:
            cursor.execute("DELETE FROM bmi_history")
        conn.commit()
        deleted_count = cursor.rowcount
        conn.close()

        if deleted_count > 0:
            messagebox.showinfo("Success", "History deleted successfully.")
        else:
            messagebox.showinfo("History", "No records found to delete.")
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Failed to delete history: {e}")


def view_history():
    name = name_entry.get().strip()

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        if name:
            cursor.execute(
                """
                SELECT id, timestamp, name, weight, height, bmi, category
                FROM bmi_history
                WHERE LOWER(name) = LOWER(?)
                ORDER BY id DESC
                """,
                (name,),
            )
        else:
            cursor.execute(
                """
                SELECT id, timestamp, name, weight, height, bmi, category
                FROM bmi_history
                ORDER BY id DESC
                """
            )
        records = cursor.fetchall()
        conn.close()
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Failed to read database records: {e}")
        return

    if not records:
        messagebox.showinfo("History", "No records found.")
        return

    history_window = tk.Toplevel(root)
    history_window.title("BMI History")
    history_window.geometry("700x420")
    history_window.configure(bg="#f5f5f5")

    title_text = f"Records for '{name}'" if name else "All User Records"
    tk.Label(history_window, text=title_text, font=("Arial", 12, "bold"), bg="#f5f5f5", fg="#333333").pack(pady=10)

    columns = ("ID", "Timestamp", "Name", "Weight (kg)", "Height (m)", "BMI", "Category")
    tree = ttk.Treeview(history_window, columns=columns, show="headings", height=10)

    tree.heading("ID", text="ID")
    tree.heading("Timestamp", text="Date & Time")
    tree.heading("Name", text="User")
    tree.heading("Weight (kg)", text="Weight (kg)")
    tree.heading("Height (m)", text="Height (m)")
    tree.heading("BMI", text="BMI")
    tree.heading("Category", text="Category")

    tree.column("ID", width=45, anchor="center")
    tree.column("Timestamp", width=140, anchor="center")
    tree.column("Name", width=95, anchor="center")
    tree.column("Weight (kg)", width=80, anchor="center")
    tree.column("Height (m)", width=80, anchor="center")
    tree.column("BMI", width=65, anchor="center")
    tree.column("Category", width=95, anchor="center")

    for row in records:
        tree.insert("", tk.END, values=row)

    scrollbar = ttk.Scrollbar(history_window, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    tree_frame = tk.Frame(history_window, bg="#f5f5f5")
    tree_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))

    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    action_frame = tk.Frame(history_window, bg="#f5f5f5")
    action_frame.pack(pady=(0, 15))

    def delete_selected():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a record from the table to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected record?")
        if not confirm:
            return

        record_id = tree.item(selected[0])["values"][0]
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM bmi_history WHERE id = ?", (record_id,))
            conn.commit()
            conn.close()
            tree.delete(selected[0])
            messagebox.showinfo("Success", "Record deleted successfully.")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to delete record: {e}")

    def delete_all():
        confirm_text = f"Are you sure you want to delete all records for '{name}'?" if name else "Are you sure you want to delete all history records?"
        confirm = messagebox.askyesno("Confirm Delete", confirm_text)
        if not confirm:
            return

        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            if name:
                cursor.execute("DELETE FROM bmi_history WHERE LOWER(name) = LOWER(?)", (name,))
            else:
                cursor.execute("DELETE FROM bmi_history")
            conn.commit()
            conn.close()
            for item in tree.get_children():
                tree.delete(item)
            messagebox.showinfo("Success", "Records deleted successfully.")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to delete records: {e}")

    del_sel_btn = tk.Button(
        action_frame,
        text="Delete Selected",
        font=("Arial", 9, "bold"),
        bg="#c62828",
        fg="#ffffff",
        activebackground="#b71c1c",
        activeforeground="#ffffff",
        relief=tk.FLAT,
        command=delete_selected
    )
    del_sel_btn.pack(side=tk.LEFT, padx=6)

    del_all_btn = tk.Button(
        action_frame,
        text="Delete All",
        font=("Arial", 9, "bold"),
        bg="#d32f2f",
        fg="#ffffff",
        activebackground="#c62828",
        activeforeground="#ffffff",
        relief=tk.FLAT,
        command=delete_all
    )
    del_all_btn.pack(side=tk.LEFT, padx=6)


def view_trend():
    name = name_entry.get().strip()

    if not name:
        messagebox.showerror("Input Error", "Please enter a user name to view the trend chart.")
        return

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT timestamp, bmi
            FROM bmi_history
            WHERE LOWER(name) = LOWER(?)
            ORDER BY id ASC
            """,
            (name,),
        )
        records = cursor.fetchall()
        conn.close()
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Failed to read records for chart: {e}")
        return

    if not records:
        messagebox.showinfo("Trend Chart", f"No records found for user '{name}'.")
        return

    timestamps = [row[0] for row in records]
    bmis = [row[1] for row in records]

    plt.figure(figsize=(9, 5))
    plt.plot(timestamps, bmis, marker="o", color="#1976d2", linewidth=2, label="BMI")
    plt.axhline(y=18.5, color="#0288d1", linestyle="--", label="Underweight (< 18.5)")
    plt.axhline(y=24.9, color="#2e7d32", linestyle="--", label="Normal (18.5 - 24.9)")
    plt.axhline(y=29.9, color="#ef6c00", linestyle="--", label="Overweight (25 - 29.9)")

    plt.title(f"BMI Trend for {name}", fontsize=14, fontweight="bold")
    plt.xlabel("Date & Time")
    plt.ylabel("BMI Value")
    plt.xticks(rotation=25, ha="right")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="upper right")
    plt.tight_layout()
    plt.show()


root = tk.Tk()
root.title("BMI Calculator")
root.geometry("420x560")
root.resizable(False, False)
root.configure(bg="#f5f7fa")

header_label = tk.Label(
    root,
    text="BMI Calculator",
    font=("Arial", 18, "bold"),
    bg="#f5f7fa",
    fg="#2c3e50"
)
header_label.pack(pady=(20, 15))

form_frame = tk.Frame(root, bg="#ffffff", bd=1, relief=tk.SOLID)
form_frame.pack(padx=25, pady=5, fill=tk.X)

tk.Label(form_frame, text="User Name:", font=("Arial", 10, "bold"), bg="#ffffff", fg="#333333").grid(row=0, column=0, sticky="w", padx=15, pady=(15, 8))
name_entry = tk.Entry(form_frame, font=("Arial", 11), width=22)
name_entry.grid(row=0, column=1, padx=15, pady=(15, 8))

tk.Label(form_frame, text="Weight (kg):", font=("Arial", 10, "bold"), bg="#ffffff", fg="#333333").grid(row=1, column=0, sticky="w", padx=15, pady=8)
weight_entry = tk.Entry(form_frame, font=("Arial", 11), width=22)
weight_entry.grid(row=1, column=1, padx=15, pady=8)

tk.Label(form_frame, text="Height (m):", font=("Arial", 10, "bold"), bg="#ffffff", fg="#333333").grid(row=2, column=0, sticky="w", padx=15, pady=(8, 15))
height_entry = tk.Entry(form_frame, font=("Arial", 11), width=22)
height_entry.grid(row=2, column=1, padx=15, pady=(8, 15))

btn_frame = tk.Frame(root, bg="#f5f7fa")
btn_frame.pack(pady=15)

calc_btn = tk.Button(
    btn_frame,
    text="Calculate BMI",
    font=("Arial", 10, "bold"),
    bg="#1976d2",
    fg="#ffffff",
    activebackground="#1565c0",
    activeforeground="#ffffff",
    relief=tk.FLAT,
    width=14,
    command=calculate_bmi
)
calc_btn.grid(row=0, column=0, padx=6, pady=4)

clear_btn = tk.Button(
    btn_frame,
    text="Clear",
    font=("Arial", 10, "bold"),
    bg="#757575",
    fg="#ffffff",
    activebackground="#616161",
    activeforeground="#ffffff",
    relief=tk.FLAT,
    width=10,
    command=clear_fields
)
clear_btn.grid(row=0, column=1, padx=6, pady=4)

history_btn = tk.Button(
    btn_frame,
    text="View History",
    font=("Arial", 10, "bold"),
    bg="#37474f",
    fg="#ffffff",
    activebackground="#263238",
    activeforeground="#ffffff",
    relief=tk.FLAT,
    width=14,
    command=view_history
)
history_btn.grid(row=1, column=0, padx=6, pady=4)

chart_btn = tk.Button(
    btn_frame,
    text="View Trend",
    font=("Arial", 10, "bold"),
    bg="#00796b",
    fg="#ffffff",
    activebackground="#00695c",
    activeforeground="#ffffff",
    relief=tk.FLAT,
    width=10,
    command=view_trend
)
chart_btn.grid(row=1, column=1, padx=6, pady=4)

delete_btn = tk.Button(
    btn_frame,
    text="Delete History",
    font=("Arial", 10, "bold"),
    bg="#c62828",
    fg="#ffffff",
    activebackground="#b71c1c",
    activeforeground="#ffffff",
    relief=tk.FLAT,
    width=26,
    command=delete_history
)
delete_btn.grid(row=2, column=0, columnspan=2, padx=6, pady=(6, 4))

result_frame = tk.Frame(root, bg="#ffffff", bd=1, relief=tk.SOLID, height=85)
result_frame.pack(padx=25, pady=(5, 15), fill=tk.X)
result_frame.pack_propagate(False)

result_label = tk.Label(
    result_frame,
    text="Enter details and click Calculate",
    font=("Arial", 12, "bold"),
    bg="#ffffff",
    fg="#666666"
)
result_label.pack(expand=True)

init_db()

if __name__ == "__main__":
    root.mainloop()
