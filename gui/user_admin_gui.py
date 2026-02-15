import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image
import secrets
import string

from logic.user_logic import (
    register_user,
    list_users,
    remove_user,
    update_password,
    set_block_status
)


class UserAdminWindow:
    def __init__(self, master):
        self.win = ctk.CTkToplevel(master)
        self.win.title("Gestione Utenti")

        # MASSIMIZZA
        try:
            self.win.state("zoomed")
        except:
            self.win.attributes("-zoomed", True)

        self.win.grab_set()
        self.win.configure(fg_color="#222831")

        # PAGINAZIONE
        self.page = 1
        self.page_size = 10
        self.filtered_users = []

        # ICONS
        try:
            self.icon_add = ctk.CTkImage(Image.open("assets/add.png"), size=(24, 24))
            self.icon_delete = ctk.CTkImage(Image.open("assets/delete.png"), size=(24, 24))
        except:
            self.icon_add = self.icon_delete = None

        title = ctk.CTkLabel(
            self.win,
            text="Gestione Utenti",
            font=("Helvetica", 32, "bold"),
            text_color="#00E676"
        )
        title.pack(pady=20)

        # ---------------------------------------------------------
        # BARRA SUPERIORE: AGGIUNTA UTENTE
        # ---------------------------------------------------------
        top = ctk.CTkFrame(self.win, corner_radius=15, fg_color="#393E46")
        top.pack(pady=10, padx=20, fill="x")

        self.username = ctk.CTkEntry(
            top, placeholder_text="Username",
            width=200, height=45, corner_radius=12,
            fg_color="#222831", border_color="#00ADB5", border_width=2
        )
        self.username.pack(side="left", padx=10, pady=10)

        self.password = ctk.CTkEntry(
            top, placeholder_text="Password", show="*",
            width=200, height=45, corner_radius=12,
            fg_color="#222831", border_color="#00ADB5", border_width=2
        )
        self.password.pack(side="left", padx=10, pady=10)

        self.role_var = tk.StringVar(value="user")
        role_menu = ctk.CTkOptionMenu(
            top, values=["user", "superuser"], variable=self.role_var,
            width=150, height=45, fg_color="#00ADB5",
            button_color="#0097A7", text_color="black"
        )
        role_menu.pack(side="left", padx=10)

        ctk.CTkButton(
            top, text="Aggiungi", image=self.icon_add, compound="left",
            height=45, fg_color="#00ADB5", hover_color="#0097A7",
            text_color="black", command=self.add_user
        ).pack(side="left", padx=10)

        # ---------------------------------------------------------
        # FILTRI E RICERCA
        # ---------------------------------------------------------
        filter_frame = ctk.CTkFrame(self.win, corner_radius=15, fg_color="#393E46")
        filter_frame.pack(pady=10, padx=20, fill="x")

        self.search_var = tk.StringVar()
        search_entry = ctk.CTkEntry(
            filter_frame, placeholder_text="Cerca utente...",
            textvariable=self.search_var,
            width=250, height=45, corner_radius=12,
            fg_color="#222831", border_color="#00ADB5", border_width=2
        )
        search_entry.pack(side="left", padx=10, pady=10)
        search_entry.bind("<KeyRelease>", lambda e: self.refresh())

        self.filter_role_var = tk.StringVar(value="Tutti")
        filter_menu = ctk.CTkOptionMenu(
            filter_frame, values=["Tutti", "user", "superuser"],
            variable=self.filter_role_var,
            width=180, height=45, fg_color="#00ADB5",
            button_color="#0097A7", text_color="black",
            command=lambda _: self.refresh()
        )
        filter_menu.pack(side="left", padx=10)

        # ---------------------------------------------------------
        # LISTA UTENTI
        # ---------------------------------------------------------
        self.listbox = tk.Listbox(
            self.win, width=70, height=12,
            font=("Helvetica", 14), bg="#EEEEEE"
        )
        self.listbox.pack(pady=20)

        # ---------------------------------------------------------
        # PAGINAZIONE
        # ---------------------------------------------------------
        pagination = ctk.CTkFrame(self.win, corner_radius=15, fg_color="#393E46")
        pagination.pack(pady=10)

        self.prev_btn = ctk.CTkButton(
            pagination, text="« Precedente",
            width=150, height=40,
            fg_color="#00ADB5", hover_color="#0097A7",
            text_color="black",
            command=self.prev_page
        )
        self.prev_btn.pack(side="left", padx=10)

        self.page_label = ctk.CTkLabel(
            pagination, text="Pagina 1 di 1",
            font=("Helvetica", 16), text_color="#EEEEEE"
        )
        self.page_label.pack(side="left", padx=20)

        self.next_btn = ctk.CTkButton(
            pagination, text="Successivo »",
            width=150, height=40,
            fg_color="#00ADB5", hover_color="#0097A7",
            text_color="black",
            command=self.next_page
        )
        self.next_btn.pack(side="left", padx=10)

        # ---------------------------------------------------------
        # CAMBIO PASSWORD + RESET PASSWORD
        # ---------------------------------------------------------
        pw_frame = ctk.CTkFrame(self.win, corner_radius=15, fg_color="#393E46")
        pw_frame.pack(pady=10, padx=20, fill="x")

        self.new_password = ctk.CTkEntry(
            pw_frame, placeholder_text="Nuova password",
            show="*", width=220, height=45, corner_radius=12,
            fg_color="#222831", border_color="#00ADB5", border_width=2
        )
        self.new_password.pack(side="left", padx=10)

        ctk.CTkButton(
            pw_frame, text="Cambia password",
            height=45, fg_color="#00ADB5", hover_color="#0097A7",
            text_color="black", command=self.change_password
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            pw_frame, text="Reset password",
            height=45, fg_color="#00E676", hover_color="#00C96B",
            text_color="black", command=self.reset_password
        ).pack(side="left", padx=10)

        # ---------------------------------------------------------
        # BLOCCO / SBLOCCO / ELIMINA
        # ---------------------------------------------------------
        block_frame = ctk.CTkFrame(self.win, corner_radius=15, fg_color="#393E46")
        block_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkButton(
            block_frame, text="Blocca account",
            height=45, fg_color="#FF5252", hover_color="#D32F2F",
            text_color="black", command=lambda: self.set_block(True)
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            block_frame, text="Sblocca account",
            height=45, fg_color="#00E676", hover_color="#00C96B",
            text_color="black", command=lambda: self.set_block(False)
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            block_frame, text="Elimina utente",
            image=self.icon_delete, compound="left",
            height=45, fg_color="#FF5252", hover_color="#D32F2F",
            text_color="black", command=self.delete_user
        ).pack(side="left", padx=10)

        self.refresh()

    # ---------------------------------------------------------
    # FUNZIONI
    # ---------------------------------------------------------
    def add_user(self):
        u = self.username.get().strip()
        p = self.password.get().strip()
        r = self.role_var.get()

        if not u or not p:
            messagebox.showwarning("Attenzione", "Username e password obbligatori")
            return

        try:
            register_user(u, p, r)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Errore", str(e))

    def refresh(self):
        all_users = list_users()

        search = self.search_var.get().lower()
        role_filter = self.filter_role_var.get()

        self.filtered_users = []
        for u in all_users:
            user_id, username, role, is_blocked = u

            if search and search not in username.lower():
                continue

            if role_filter != "Tutti" and role != role_filter:
                continue

            self.filtered_users.append(u)

        total = len(self.filtered_users)
        total_pages = max(1, (total + self.page_size - 1) // self.page_size)

        if self.page > total_pages:
            self.page = total_pages

        start = (self.page - 1) * self.page_size
        end = start + self.page_size

        self.listbox.delete(0, tk.END)
        for u in self.filtered_users[start:end]:
            user_id, username, role, is_blocked = u
            status = "BLOCCATO" if is_blocked else "ATTIVO"
            self.listbox.insert(tk.END, f"{user_id} | {username} | {role} | {status}")

        self.page_label.configure(text=f"Pagina {self.page} di {total_pages}")

        self.prev_btn.configure(state="normal" if self.page > 1 else "disabled")
        self.next_btn.configure(state="normal" if self.page < total_pages else "disabled")

    def next_page(self):
        self.page += 1
        self.refresh()

    def prev_page(self):
        self.page -= 1
        self.refresh()

    def delete_user(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        user_id = int(self.listbox.get(sel[0]).split("|")[0].strip())
        remove_user(user_id)
        self.refresh()

    def change_password(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Attenzione", "Seleziona un utente")
            return

        new_pw = self.new_password.get().strip()
        if not new_pw:
            messagebox.showwarning("Attenzione", "Inserisci una nuova password")
            return

        user_id = int(self.listbox.get(sel[0]).split("|")[0].strip())

        update_password(user_id, new_pw)
        messagebox.showinfo("OK", "Password aggiornata correttamente")
        self.new_password.delete(0, tk.END)

    def reset_password(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Attenzione", "Seleziona un utente")
            return

        user_id = int(self.listbox.get(sel[0]).split("|")[0].strip())

        alphabet = string.ascii_letters + string.digits + "!@#$%&*?"
        new_pw = ''.join(secrets.choice(alphabet) for _ in range(10))

        update_password(user_id, new_pw)

        messagebox.showinfo("Password reset",
                            f"La nuova password è:\n\n{new_pw}\n\nCopiala e comunicala all’utente.")

    def set_block(self, block):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Attenzione", "Seleziona un utente")
            return

        user_id = int(self.listbox.get(sel[0]).split("|")[0].strip())
        set_block_status(user_id, block)

        status = "bloccato" if block else "sbloccato"
        messagebox.showinfo("OK", f"Utente {status} correttamente")
        self.refresh()