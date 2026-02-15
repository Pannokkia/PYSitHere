import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import json
from config.config_loader import load_config, CONFIG_PATH

class OfficeAdminWindow:
    def __init__(self, master):
        self.win = ctk.CTkToplevel(master)
        self.win.title("Gestione Uffici")
        self.win.geometry("800x600")
        self.win.grab_set()

        self.desks = []

        title = ctk.CTkLabel(self.win, text="Nuovo Ufficio",
                             font=("Helvetica", 26, "bold"))
        title.pack(pady=20)

        form = ctk.CTkFrame(self.win, corner_radius=15)
        form.pack(pady=10, padx=20, fill="x")

        self.name = ctk.CTkEntry(form, placeholder_text="Nome ufficio", width=250)
        self.name.pack(pady=10)

        self.floor_name = ctk.CTkEntry(form, placeholder_text="Nome piano (es. Piano Terra)",
                                       width=250)
        self.floor_name.pack(pady=10)

        self.total_seats = ctk.CTkEntry(form, placeholder_text="Posti totali", width=250)
        self.total_seats.pack(pady=10)

        desk_frame = ctk.CTkFrame(self.win, corner_radius=15)
        desk_frame.pack(pady=10, padx=20, fill="x")

        self.desk_name = ctk.CTkEntry(desk_frame, placeholder_text="Nome scrivania", width=200)
        self.desk_name.pack(side="left", padx=5, pady=10)

        self.desk_x = ctk.CTkEntry(desk_frame, placeholder_text="X", width=80)
        self.desk_x.pack(side="left", padx=5)

        self.desk_y = ctk.CTkEntry(desk_frame, placeholder_text="Y", width=80)
        self.desk_y.pack(side="left", padx=5)

        ctk.CTkButton(desk_frame, text="Aggiungi scrivania",
                      command=self.add_desk).pack(side="left", padx=10)

        self.listbox = tk.Listbox(self.win, width=60, height=10)
        self.listbox.pack(pady=10)

        ctk.CTkButton(self.win, text="Salva ufficio",
                      command=self.save_office, height=45).pack(pady=20)

    def add_desk(self):
        name = self.desk_name.get().strip()
        x = self.desk_x.get().strip()
        y = self.desk_y.get().strip()
        if not name or not x or not y:
            messagebox.showwarning("Attenzione", "Compila tutti i campi scrivania")
            return
        try:
            dx = int(x)
            dy = int(y)
        except ValueError:
            messagebox.showwarning("Attenzione", "X e Y devono essere numeri")
            return

        desk = {"name": name, "x": dx, "y": dy}
        self.desks.append(desk)
        self.listbox.insert(tk.END, f"{name} ({dx},{dy})")

        self.desk_name.delete(0, tk.END)
        self.desk_x.delete(0, tk.END)
        self.desk_y.delete(0, tk.END)

    def save_office(self):
        name = self.name.get().strip()
        floor_name = self.floor_name.get().strip()
        total_seats = self.total_seats.get().strip()

        if not name or not floor_name or not total_seats:
            messagebox.showwarning("Attenzione", "Compila tutti i campi ufficio/piano")
            return
        if not self.desks:
            messagebox.showwarning("Attenzione", "Aggiungi almeno una scrivania")
            return

        try:
            total = int(total_seats)
        except ValueError:
            messagebox.showwarning("Attenzione", "Posti totali deve essere un numero")
            return

        config = load_config()

        new_office = {
            "id": name.replace(" ", "-"),
            "name": name,
            "floors": [
                {
                    "name": floor_name,
                    "total_seats": total,
                    "desks": self.desks
                }
            ],
            "appearance": config["offices"][0]["appearance"],
            "desk_settings": config["offices"][0]["desk_settings"]
        }

        config["offices"].append(new_office)

        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)

        messagebox.showinfo("OK", "Ufficio salvato in config.json")
        self.win.destroy()