import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image

from config.config_loader import get_office_by_name, get_floor, save_config


class DeskAdminWindow:
    def __init__(self, master, office_name, floor_name):
        self.office_name = office_name
        self.floor_name = floor_name

        self.win = ctk.CTkToplevel(master)
        self.win.title(f"Gestione scrivanie — {office_name} / {floor_name}")

        try:
            self.win.state("zoomed")
        except:
            self.win.attributes("-zoomed", True)

        self.win.grab_set()
        self.win.configure(fg_color="#222831")

        # Icone
        try:
            self.icon_add = ctk.CTkImage(Image.open("assets/add.png"), size=(24, 24))
            self.icon_delete = ctk.CTkImage(Image.open("assets/delete.png"), size=(24, 24))
        except:
            self.icon_add = self.icon_delete = None

        title = ctk.CTkLabel(
            self.win,
            text=f"Gestione scrivanie\n{office_name} — {floor_name}",
            font=("Helvetica", 30, "bold"),
            text_color="#00ADB5"
        )
        title.pack(pady=20)

        main_frame = ctk.CTkFrame(self.win, corner_radius=15, fg_color="#222831")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Sinistra: canvas
        left = ctk.CTkFrame(main_frame, corner_radius=15, fg_color="#393E46")
        left.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(left, bg="#222831")
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)

        # Destra: pannello dettagli
        right = ctk.CTkFrame(main_frame, corner_radius=15, fg_color="#393E46")
        right.pack(side="right", fill="y", padx=10, pady=10)

        ctk.CTkLabel(
            right, text="Dettagli scrivania", font=("Helvetica", 20, "bold"), text_color="#EEEEEE"
        ).pack(pady=10)

        self.desk_name_var = tk.StringVar()
        self.desk_name_entry = ctk.CTkEntry(
            right,
            placeholder_text="Nome scrivania",
            textvariable=self.desk_name_var,
            width=220,
            height=40,
            corner_radius=12,
            fg_color="#222831",
            border_color="#00ADB5",
            border_width=2
        )
        self.desk_name_entry.pack(pady=10)

        ctk.CTkButton(
            right,
            text="Aggiungi scrivania",
            image=self.icon_add,
            compound="left",
            height=40,
            fg_color="#00ADB5",
            hover_color="#0097A7",
            text_color="black",
            command=self.add_desk
        ).pack(pady=10)

        ctk.CTkButton(
            right,
            text="Elimina scrivania selezionata",
            image=self.icon_delete,
            compound="left",
            height=40,
            fg_color="#FF5252",
            hover_color="#D32F2F",
            text_color="black",
            command=self.delete_desk
        ).pack(pady=10)

        ctk.CTkButton(
            right,
            text="Salva modifiche",
            height=40,
            fg_color="#00ADB5",
            hover_color="#00ADB5",
            text_color="black",
            command=self.save
        ).pack(pady=20)

        ctk.CTkLabel(
            right,
            text="Suggerimento:\nTrascina le scrivanie sul canvas\nper riposizionarle.",
            font=("Helvetica", 13),
            text_color="#EEEEEE",
            justify="left"
        ).pack(pady=10)

        # Carica config
        self.office = get_office_by_name(self.office_name)
        self.floor = get_floor(self.office, self.floor_name)
        self.desks = self.floor["desks"]

        self.desk_items = {}  # id_canvas -> dict scrivania
        self.selected_item = None
        self.drag_data = {"x": 0, "y": 0}

        self.draw_desks()
        self.bind_canvas()

    def draw_desks(self):
        self.canvas.delete("all")
        self.desk_items.clear()

        for d in self.desks:
            x = d["x"]
            y = d["y"]
            name = d["name"]

            r = 20
            item = self.canvas.create_rectangle(
                x - r, y - r, x + r, y + r,
                fill="#00ADB5", outline="#0097A7", width=2
            )
            text = self.canvas.create_text(
                x, y - 25, text=name, fill="#EEEEEE", font=("Helvetica", 10, "bold")
            )

            self.desk_items[item] = {"data": d, "text": text}

    def bind_canvas(self):
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def on_click(self, event):
        item = self.canvas.find_closest(event.x, event.y)[0]
        if item in self.desk_items:
            self.selected_item = item
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

            d = self.desk_items[item]["data"]
            self.desk_name_var.set(d["name"])

    def on_drag(self, event):
        if self.selected_item is None:
            return

        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]

        self.canvas.move(self.selected_item, dx, dy)
        text_id = self.desk_items[self.selected_item]["text"]
        self.canvas.move(text_id, dx, dy)

        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_release(self, event):
        if self.selected_item is None:
            return

        x1, y1, x2, y2 = self.canvas.coords(self.selected_item)
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2

        d = self.desk_items[self.selected_item]["data"]
        d["x"] = int(cx)
        d["y"] = int(cy)

    def add_desk(self):
        name = self.desk_name_var.get().strip()
        if not name:
            messagebox.showwarning("Attenzione", "Inserisci un nome per la scrivania")
            return

        new_desk = {"name": name, "x": 100, "y": 100}
        self.desks.append(new_desk)
        self.draw_desks()
        self.desk_name_var.set("")

    def delete_desk(self):
        if self.selected_item is None:
            messagebox.showwarning("Attenzione", "Seleziona una scrivania dal canvas")
            return

        d = self.desk_items[self.selected_item]["data"]
        self.desks.remove(d)
        self.draw_desks()
        self.selected_item = None
        self.desk_name_var.set("")

    def save(self):
        # salva nel config.json tramite config_loader
        save_config()
        messagebox.showinfo("Salvato", "Configurazione scrivanie aggiornata")