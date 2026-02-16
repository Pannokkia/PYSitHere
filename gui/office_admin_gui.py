import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, simpledialog

from config.config_loader import (
    load_config,
    save_config,
    reload_config,
    get_offices,
    get_office_by_name,
    get_floor,
)

GRID_SIZE = 20  # snap-to-grid


class OfficeAdminWindow:
    def __init__(self, master):
        self.win = ctk.CTkToplevel(master)
        self.win.title("Gestione Uffici")

        try:
            self.win.state("zoomed")
        except:
            self.win.attributes("-zoomed", True)

        self.win.configure(fg_color="#222831")
        self.win.lift()
        self.win.focus_force()
        self.win.grab_set()

        self.config = load_config()

        self.current_office = None
        self.current_floor = None
        self.selected_desk = None
        self.dragging_desk = None
        self.drag_offset = (0, 0)

        # ---------------------------------------------------------
        # TITOLO
        # ---------------------------------------------------------
        ctk.CTkLabel(
            self.win,
            text="Gestione Uffici e Piani",
            font=("Helvetica", 32, "bold"),
            text_color="#00E676"
        ).pack(pady=20)

        # ---------------------------------------------------------
        # FRAME PRINCIPALE
        # ---------------------------------------------------------
        main_frame = ctk.CTkFrame(self.win, fg_color="#222831")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # ---------------------------------------------------------
        # SINISTRA — LISTA UFFICI E PIANI
        # ---------------------------------------------------------
        left_frame = ctk.CTkFrame(main_frame, fg_color="#393E46", corner_radius=15)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(
            left_frame,
            text="Uffici",
            font=("Helvetica", 22, "bold"),
            text_color="#00E676"
        ).pack(pady=10)

        self.office_list = tk.Listbox(
            left_frame, width=40, height=15, font=("Helvetica", 14), bg="#EEEEEE"
        )
        self.office_list.pack(pady=10)
        self.office_list.bind("<<ListboxSelect>>", self.on_office_select)

        ctk.CTkButton(
            left_frame,
            text="Nuovo Ufficio",
            fg_color="#00ADB5",
            hover_color="#0097A7",
            text_color="black",
            command=self.add_office
        ).pack(pady=5)

        ctk.CTkLabel(
            left_frame,
            text="Piani",
            font=("Helvetica", 22, "bold"),
            text_color="#00ADB5"
        ).pack(pady=10)

        self.floor_list = tk.Listbox(
            left_frame, width=40, height=15, font=("Helvetica", 14), bg="#EEEEEE"
        )
        self.floor_list.pack(pady=10)
        self.floor_list.bind("<<ListboxSelect>>", self.on_floor_select)

        ctk.CTkButton(
            left_frame,
            text="Nuovo Piano",
            fg_color="#00ADB5",
            hover_color="#0097A7",
            text_color="black",
            command=self.add_floor
        ).pack(pady=5)

        # ---------------------------------------------------------
        # DESTRA — EDITOR SCRIVANIE
        # ---------------------------------------------------------
        right_frame = ctk.CTkFrame(main_frame, fg_color="#393E46", corner_radius=15)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            right_frame,
            text="Editor Scrivanie",
            font=("Helvetica", 22, "bold"),
            text_color="#00ADB5"
        ).pack(pady=10)

        self.canvas = tk.Canvas(right_frame, bg="#222831")
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)

        # Bind per drag & drop
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        # Pulsanti editor
        btn_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(
            btn_frame,
            text="Aggiungi Scrivania",
            fg_color="#00ADB5",
            hover_color="#0097A7",
            text_color="black",
            command=self.add_desk
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="Duplica Scrivania",
            fg_color="#00ADB5",
            hover_color="#0097A7",
            text_color="black",
            command=self.duplicate_desk
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="Elimina Scrivania",
            fg_color="#FF5252",
            hover_color="#D32F2F",
            text_color="black",
            command=self.delete_desk
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="Salva Configurazione",
            fg_color="#00ADB5",
            hover_color="#0097A7",
            text_color="black",
            command=self.save_all
        ).pack(side="left", padx=10)

        self.load_offices()

    # ---------------------------------------------------------
    # CARICAMENTO LISTE
    # ---------------------------------------------------------
    def load_offices(self):
        self.office_list.delete(0, tk.END)
        for office in get_offices():
            label = f"{office.get('id', '')} — {office['name']}"
            self.office_list.insert(tk.END, label)

    def on_office_select(self, event):
        sel = self.office_list.curselection()
        if not sel:
            return

        label = self.office_list.get(sel[0])
        office_id = label.split(" — ")[0].strip()

        self.current_office = get_office_by_name(office_id)

        self.floor_list.delete(0, tk.END)
        for floor in self.current_office["floors"]:
            self.floor_list.insert(tk.END, floor["name"])

    def on_floor_select(self, event):
        sel = self.floor_list.curselection()
        if not sel:
            return

        floor_name = self.floor_list.get(sel[0])
        self.current_floor = get_floor(self.current_office, floor_name)

        self.draw_desks()

    # ---------------------------------------------------------
    # CREAZIONE UFFICIO
    # ---------------------------------------------------------
    def add_office(self):
        name = simpledialog.askstring("Nuovo Ufficio", "Nome ufficio:")
        if not name:
            return

        office_id = simpledialog.askstring("ID Ufficio", "Inserisci ID ufficio (es. HQ-MI):")
        if not office_id:
            return

        self.config["offices"].append({
            "id": office_id,
            "name": name,
            "floors": []
        })

        save_config()
        self.load_offices()

    # ---------------------------------------------------------
    # CREAZIONE PIANO
    # ---------------------------------------------------------
    def add_floor(self):
        if not self.current_office:
            messagebox.showwarning("Attenzione", "Seleziona un ufficio")
            return

        name = simpledialog.askstring("Nuovo Piano", "Nome piano:")
        if not name:
            return

        self.current_office["floors"].append({
            "name": name,
            "desks": []
        })

        save_config()
        self.on_office_select(None)

    # ---------------------------------------------------------
    # EDITOR SCRIVANIE
    # ---------------------------------------------------------
    def draw_desks(self):
        self.canvas.delete("all")

        if not self.current_floor:
            return

        for desk in self.current_floor["desks"]:
            x, y = desk["x"], desk["y"]
            self.canvas.create_oval(x-10, y-10, x+10, y+10, fill="#00E676")
            self.canvas.create_text(x, y-18, text=desk["name"], fill="#EEEEEE")

    def add_desk(self):
        if not self.current_floor:
            messagebox.showwarning("Attenzione", "Seleziona un piano")
            return

        name = simpledialog.askstring("Nuova Scrivania", "Nome scrivania:")
        if not name:
            return

        self.current_floor["desks"].append({
            "name": name,
            "x": 100,
            "y": 100
        })

        self.draw_desks()

    def duplicate_desk(self):
        if not self.selected_desk:
            messagebox.showwarning("Attenzione", "Seleziona una scrivania")
            return

        base = self.selected_desk["name"]
        new_name = self.generate_copy_name(base)

        new_desk = {
            "name": new_name,
            "x": self.selected_desk["x"] + 30,
            "y": self.selected_desk["y"] + 30
        }

        self.current_floor["desks"].append(new_desk)
        self.draw_desks()

    def generate_copy_name(self, base):
        names = [d["name"] for d in self.current_floor["desks"]]
        if base + " (copy)" not in names:
            return base + " (copy)"

        i = 2
        while f"{base} (copy {i})" in names:
            i += 1
        return f"{base} (copy {i})"

    def delete_desk(self):
        if not self.selected_desk:
            messagebox.showwarning("Attenzione", "Seleziona una scrivania")
            return

        self.current_floor["desks"].remove(self.selected_desk)
        self.selected_desk = None
        self.draw_desks()

    # ---------------------------------------------------------
    # DRAG & DROP
    # ---------------------------------------------------------
    def on_click(self, event):
        if not self.current_floor:
            return

        for desk in self.current_floor["desks"]:
            x, y = desk["x"], desk["y"]
            if abs(event.x - x) < 15 and abs(event.y - y) < 15:
                self.selected_desk = desk
                self.dragging_desk = desk
                self.drag_offset = (event.x - x, event.y - y)
                return

    def on_drag(self, event):
        if not self.dragging_desk:
            return

        new_x = event.x - self.drag_offset[0]
        new_y = event.y - self.drag_offset[1]

        self.dragging_desk["x"] = new_x
        self.dragging_desk["y"] = new_y

        self.draw_desks()

    def on_release(self, event):
        if not self.dragging_desk:
            return

        # Snap-to-grid
        x = self.dragging_desk["x"]
        y = self.dragging_desk["y"]

        x = round(x / GRID_SIZE) * GRID_SIZE
        y = round(y / GRID_SIZE) * GRID_SIZE

        self.dragging_desk["x"] = x
        self.dragging_desk["y"] = y

        self.dragging_desk = None
        self.draw_desks()

    # ---------------------------------------------------------
    # SALVATAGGIO
    # ---------------------------------------------------------
    def save_all(self):
        save_config()
        messagebox.showinfo("Salvato", "Configurazione aggiornata")
