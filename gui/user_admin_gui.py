import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, simpledialog

from database.database import get_connection


class UserAdminWindow:
    def __init__(self, master):
        self.win = ctk.CTkToplevel(master)
        self.win.title("Gestione Utenti")
        self.win.geometry("700x600")
        self.win.configure(fg_color="#222831")

        self.win.lift()
        self.win.focus_force()
        self.win.grab_set()

        ctk.CTkLabel(
            self.win,
            text="Gestione Utenti",
            font=("Helvetica", 32, "bold"),
            text_color="#00E676"
        ).pack(pady=20)

        self.listbox = tk.Listbox(
            self.win,
            width=60,
            height=20,
            font=("Helvetica", 14),
            bg="#EEEEEE"
        )
        self.listbox.pack(pady=10)

        btn_frame = ctk.CTkFrame(self.win, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(
            btn_frame,
            text="Aggiungi Utente",
            fg_color="#00ADB5",
            hover_color="#0097A7",
            text_color="black",
            command=self.add_user
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="Blocca/Sblocca",
            fg_color="#FF5252",
            hover_color="#D32F2F",
            text_color="black",
            command=self.toggle_block
        ).pack(side="left", padx=10)

        self.load_users()

    # ---------------------------------------------------------
    # CARICA UTENTI
    # ---------------------------------------------------------
    def load_users(self):
        self.listbox.delete(0, tk.END)

        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT id, username, role, is_blocked FROM users ORDER BY username")
        rows = c.fetchall()
        conn.close()

        for uid, uname, role, blocked in rows:
            status = "BLOCCATO" if blocked else "ATTIVO"
            self.listbox.insert(tk.END, f"{uid} — {uname} — {role} — {status}")

    # ---------------------------------------------------------
    # AGGIUNGI UTENTE
    # ---------------------------------------------------------
    def add_user(self):
        username = simpledialog.askstring("Nuovo Utente", "Username:")
        if not username:
            return

        password = simpledialog.askstring("Nuovo Utente", "Password:")
        if not password:
            return

        role = simpledialog.askstring("Nuovo Utente", "Ruolo (user/admin):", initialvalue="user")
        if role not in ("user", "admin"):
            messagebox.showerror("Errore", "Ruolo non valido")
            return

        conn = get_connection()
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password, role, is_blocked) VALUES (?, ?, ?, 0)",
                  (username, password, role))
        conn.commit()
        conn.close()

        self.load_users()

    # ---------------------------------------------------------
    # BLOCCA / SBLOCCA
    # ---------------------------------------------------------
    def toggle_block(self):
        sel = self.listbox.curselection()
        if not sel:
            return

        row = self.listbox.get(sel[0])
        uid = int(row.split(" — ")[0])

        conn = get_connection()
        c = conn.cursor()

        c.execute("SELECT is_blocked FROM users WHERE id = ?", (uid,))
        blocked = c.fetchone()[0]

        new_status = 0 if blocked else 1

        c.execute("UPDATE users SET is_blocked = ? WHERE id = ?", (new_status, uid))
        conn.commit()
        conn.close()

        self.load_users()
