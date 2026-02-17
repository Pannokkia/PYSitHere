import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

from database.database import init_db
from logic.logic import get_user_by_username
from gui.booking_gui import BookingWindow
from gui.office_admin_gui import OfficeAdminWindow
from gui.user_admin_gui import UserAdminWindow
from config.languages import LANG
from config.config_loader import get_offices


class LoginWindow:

    current_lang = "it"
    global texts
    texts = LANG[current_lang]

    def __init__(self):
        init_db()  # INIZIALIZZA DB QUI

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.current_lang = "it"  # PReferrd language

        self.win = ctk.CTk()
        self.win.title(texts["title_main_win"])

        self.win.geometry("500x400")
        self.win.configure(fg_color="#222831")

        title = ctk.CTkLabel(
            self.win,
            text=texts["title"],
            font=("Helvetica", 32, "bold"),
            text_color="#00ADB5"
        )
        title.pack(pady=30)

        self.username = ctk.CTkEntry(self.win, placeholder_text=texts["label_username"], width=250)
        self.username.pack(pady=10)

        self.password = ctk.CTkEntry(self.win, placeholder_text=texts["label_password"], show="*", width=250)
        self.password.pack(pady=10)

        ctk.CTkButton(
            self.win,
            text=texts["button_login"],
            fg_color="#00ADB5",
            hover_color="#0097A7",
            text_color="black",
            width=200,
            command=self.login
        ).pack(pady=20)

        self.win.bind("<Return>", self.login_event)
        self.win.mainloop()

    # ---------------------------------------------------------
    # LOGIN
    # ---------------------------------------------------------
    def login(self):
        username = self.username.get().strip()
        password = self.password.get().strip()

        user = get_user_by_username(username)
        if not user:
            messagebox.showerror(texts["msg_invalid_username"])
            return

        user_id, uname, pwd, role, is_blocked = user

        if is_blocked:
            messagebox.showerror(texts["msg_blocked_user"])
            return

        if pwd != password:
            messagebox.showerror(texts["msg_invalid_password"])
            return

        self.open_home(user_id, role)

    def login_event(self, event):
        self.login()

    # ---------------------------------------------------------
    # HOME
    # ---------------------------------------------------------
    def open_home(self, user_id, role):
        self.win.withdraw()

        home = ctk.CTkToplevel()
        home.title(texts["title_main_win"])
        home.geometry("600x500")
        home.configure(fg_color="#222831")

        # ---------------------------------------------------------
        # MENU BAR
        # ---------------------------------------------------------
        menubar = tk.Menu(home)

        # --- FILE ---
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label=texts["sub_mnu_file_exit"], command=home.destroy)
        menubar.add_cascade(label=texts["mnu_file"], menu=file_menu)

        # --- STRUMENTI ---
        tools_menu = tk.Menu(menubar, tearoff=0)

        if role and role.lower() in ("admin", "superuser", "administrator", "super"):
            tools_menu.add_command(
                label=texts["manage_office"],
                command=lambda: OfficeAdminWindow(home)
            )
            tools_menu.add_command(
                label=texts["manage_users"],
                command=lambda: UserAdminWindow(home)
            )

        menubar.add_cascade(label=texts["mnu_admin_tools"], menu=tools_menu)

        home.configure(menu=menubar)

        # ---------------------------------------------------------
        # CONTENUTO HOME
        # ---------------------------------------------------------
        ctk.CTkLabel(
            home,
            text=texts["welcome_message"] + self.username.get(),
            font=("Helvetica", 28, "bold"),
            text_color="#00ADB5"
        ).pack(pady=20)

        # ---------------------------------------------------------
        # SELEZIONE UFFICIO
        # ---------------------------------------------------------
        offices = get_offices()

        if not offices:
            ctk.CTkLabel(
                home,
                text=texts["error_no_offices"],
                font=("Helvetica", 18),
                text_color="#FF5252"
            ).pack(pady=20)
            return

        ctk.CTkLabel(
            home,
            text=texts["label_select_office"],
            font=("Helvetica", 18),
            text_color="#EEEEEE"
        ).pack(pady=10)

        office_labels = [f"{o['id']} — {o['name']}" for o in offices]
        office_var = tk.StringVar(value=office_labels[0])

        office_menu = ctk.CTkOptionMenu(
            home,
            values=office_labels,
            variable=office_var,
            width=300,
            fg_color="#00ADB5",
            button_color="#00ADB5",
            text_color="black"
        )
        office_menu.pack(pady=10)

        # ---------------------------------------------------------
        # SELEZIONE PIANO
        # ---------------------------------------------------------
        ctk.CTkLabel(
            home,
            text=texts["label_select_floor"],
            font=("Helvetica", 18),
            text_color="#EEEEEE"
        ).pack(pady=10)

        floor_var = tk.StringVar(value="")

        def update_floors(choice):
            office_id = choice.split(" — ")[0]
            office = next(o for o in offices if o["id"] == office_id)
            floors = [f["name"] for f in office["floors"]]
            floor_var.set(floors[0] if floors else "")
            floor_menu.configure(values=floors)

        floor_menu = ctk.CTkOptionMenu(
            home,
            values=[],
            variable=floor_var,
            width=300,
            fg_color="#00ADB5",
            button_color="#00ADB5",
            text_color="black"
        )
        floor_menu.pack(pady=10)

        update_floors(office_labels[0])
        office_menu.configure(command=update_floors)

        # ---------------------------------------------------------
        # APRI PRENOTAZIONI
        # ---------------------------------------------------------
        ctk.CTkButton(
            home,
            text=texts["open_booking"],
            fg_color="#00ADB5",
            hover_color="#00ADB5",
            text_color="black",
            width=250,
            command=lambda: BookingWindow(
                home,
                user_id,
                role,
                office_var.get().split(" — ")[0],
                floor_var.get()
            )
        ).pack(pady=20)


if __name__ == "__main__":
    LoginWindow()