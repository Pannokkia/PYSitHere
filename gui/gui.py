import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

from gui.booking_gui import BookingWindow
from gui.user_admin_gui import UserAdminWindow
from gui.desk_admin_gui import DeskAdminWindow
from gui.office_admin_gui import OfficeAdminWindow

from logic.user_logic import login
from config.config_loader import get_offices, get_office_by_name
from database.database import init_db   
from config.languages import LANG



class MainWindow:
    
    current_lang = "it"
    global texts
    texts = LANG[current_lang]

    def __init__(self, root):
        self.root = root

        # Tema più vivo
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root.title((texts["title_main_win"]))
        
        self.user_id = None
        self.role = None
        self.office_var = None
        self.floor_var = None
        
        self.build_login()

    # ---------------------------------------------------------
    # LOGIN WINDOW — VERSIONE PROFESSIONALE
    # ---------------------------------------------------------
    def build_login(self):
        self.clear()
        self.root.geometry("700x640")
        self.root.minsize(700, 640)

        frame = ctk.CTkFrame(
            self.root,
            corner_radius=25,
            fg_color="#222831"
        )
        frame.place(relx=0.5, rely=0.5, anchor="center")

        title = ctk.CTkLabel(
            frame,
            text=(texts["label_login_window"]),
            font=("Helvetica", 38, "bold"),
            text_color="#00adb5"
        )
        title.pack(pady=(30, 10))

        subtitle = ctk.CTkLabel(
            frame,
            text=texts["label_subtitle_login_win"],
            font=("Helvetica", 17),
            text_color="#eeeeee"
        )
        subtitle.pack(pady=(0, 25))

        # USERNAME
        self.username = ctk.CTkEntry(
            frame,
            placeholder_text=texts["label_username"],
            width=360,
            height=55,
            corner_radius=18,
            font=("Helvetica", 17),
            fg_color="#393e46",
            border_color="#00adb5",
            border_width=2
        )
        self.username.pack(pady=12)

        # PASSWORD
        self.password = ctk.CTkEntry(
            frame,
            placeholder_text=texts["label_password"],
            show="*",
            width=360,
            height=55,
            corner_radius=18,
            font=("Helvetica", 17),
            fg_color="#393e46",
            border_color="#00adb5",
            border_width=2
        )
        self.password.pack(pady=12)

        # LOGIN BUTTON
        login_btn = ctk.CTkButton(
            frame,
            text=texts["button_login"],
            height=55,
            width=260,
            corner_radius=18,
            font=("Helvetica", 20, "bold"),
            fg_color="#00adb5",
            hover_color="#00adb5",
            text_color="black",
            command=self.do_login
        )
        login_btn.pack(pady=30)

        #Imposto la pressine dell'invio come default sul bottone di login    
        login_btn.focus()
        self.root.bind("<Return>", lambda e: self.do_login())


    def do_login(self):
        result = login(self.username.get(), self.password.get())
        if not result:
            messagebox.showerror("Errore", texts["msg_invalid_credentials"])
            return
        if 'blocked' in result:
            messagebox.showerror("Errore",  texts["msg_blocked_user"])
            return

        self.user_id, self.role = result
        self.build_main_menu()

    # ---------------------------------------------------------
    # MAIN WINDOW — MASSIMIZZATA + UFFICIO + PIANO
    # ---------------------------------------------------------
    def build_main_menu(self):
        self.clear()

        try:
            self.root.state("zoomed")
        except:
            self.root.attributes("-zoomed", True)

        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label=texts["sub_mnu_file_exit"], command=self.root.quit)
        menubar.add_cascade(label=texts["mnu_file"], menu=file_menu)

        if self.role == "superuser":
            admin_menu = tk.Menu(menubar, tearoff=0)
            admin_menu.add_command(label=texts["sub_mnu_admin_manage_users"], command=self.open_user_admin)
            admin_menu.add_command(label=texts["sub_mnu_admin_manage_desk"], command=self.open_desk_admin)
            admin_menu.add_command(label=texts["sub_mnu_admin_manage_office"], command=self.open_office_admin)
            menubar.add_cascade(label=texts["mnu_admin_tools"], menu=admin_menu)

        self.root.config(menu=menubar)

        main_frame = ctk.CTkFrame(self.root, corner_radius=20)
        main_frame.pack(expand=True, fill="both", padx=40, pady=40)

        offices = get_offices()
        office_names = [o["name"] for o in offices]
        self.office_var = ctk.StringVar(value=office_names[0])

        office_row = ctk.CTkFrame(main_frame, corner_radius=15)
        office_row.pack(pady=10)

        ctk.CTkLabel(office_row, text=texts["label_office"],
                     font=("Helvetica", 18)).pack(side="left", padx=10)

        ctk.CTkOptionMenu(
            office_row,
            values=office_names,
            variable=self.office_var,
            width=260,
            height=40
        ).pack(side="left", padx=10)

        # floor combo
        office = get_office_by_name(self.office_var.get())
        floor_names = [f["name"] for f in office["floors"]]
        self.floor_var = ctk.StringVar(value=floor_names[0])

        ctk.CTkLabel(office_row, text="Piano:",
                     font=("Helvetica", 18)).pack(side="left", padx=10)

        ctk.CTkOptionMenu(
            office_row,
            values=floor_names,
            variable=self.floor_var,
            width=200,
            height=40
        ).pack(side="left", padx=10)

        welcome = ctk.CTkLabel(
            main_frame,
            text=texts["welcome_message"] ,
            font=("Helvetica", 34, "bold")
        )
        welcome.pack(pady=40)

        ctk.CTkButton(
            main_frame,
            text=texts["open_booking"],
            font=("Helvetica", 22),
            height=60,
            width=300,
            fg_color="#00adb5",
            hover_color="#00adb5",
            text_color="black",
            corner_radius=18,
            command=self.open_booking
        ).pack(pady=20)

    # ---------------------------------------------------------
    # OPEN WINDOWS
    # ---------------------------------------------------------
    def open_booking(self):
        BookingWindow(
            self.root,
            self.user_id,
            self.role,
            self.office_var.get(),
            self.floor_var.get()
        )

    def open_user_admin(self):
        if self.role != "superuser":
            return
        UserAdminWindow(self.root)

    def open_desk_admin(self):
        if self.role != "superuser":
            return
        DeskAdminWindow(self.root, self.office_var.get(), self.floor_var.get())

    def open_office_admin(self):
        if self.role != "superuser":
            return
        OfficeAdminWindow(self.root)

    # ---------------------------------------------------------
    # CLEAR WINDOW
    # ---------------------------------------------------------
    def clear(self):
        for w in self.root.winfo_children():
            w.destroy()