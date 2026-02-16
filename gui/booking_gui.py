import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
from PIL import Image
from datetime import timedelta

from logic.logic import (
    get_free_desks,
    get_booked_desks,
    get_booked_desks_with_user,
    book_desk,
    cancel_booking,
    get_user_bookings,
)

from config.config_loader import (
    get_office_by_name,
    get_floor,
    reload_config
)


# ---------------------------------------------------------
# TOOLTIP
# ---------------------------------------------------------
class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip = None

        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, event=None):
        if self.tip:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20

        self.tip = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.configure(bg="#393E46")

        label = tk.Label(
            tw,
            text=self.text,
            bg="#393E46",
            fg="#EEEEEE",
            relief="solid",
            borderwidth=1,
            font=("Helvetica", 10)
        )
        label.pack(ipadx=5, ipady=3)

    def hide(self, event=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None


# ---------------------------------------------------------
# BOOKING WINDOW
# ---------------------------------------------------------
class BookingWindow:
    def __init__(self, master, user_id, role, office_id, floor_name):
        self.user_id = user_id
        self.role = role
        self.office_id = office_id
        self.floor_name = floor_name

        self.win = ctk.CTkToplevel(master)
        self.win.title(f"Prenotazioni — {office_id} / {floor_name}")

        try:
            self.win.state("zoomed")
        except:
            self.win.attributes("-zoomed", True)

        self.win.configure(fg_color="#222831")
        self.win.lift()
        self.win.focus_force()
        self.win.grab_set()

        # 🔄 Refresh automatico
        self.win.bind("<FocusIn>", lambda e: self.refresh_config())

        # Zoom mini‑mappa
        self.zoom_factor = 1.0

        # Icone
        try:
            self.icon_book = ctk.CTkImage(Image.open("assets/book.png"), size=(24, 24))
            self.icon_delete = ctk.CTkImage(Image.open("assets/delete.png"), size=(24, 24))
            self.icon_calendar = ctk.CTkImage(Image.open("assets/calendar.png"), size=(24, 24))
        except:
            self.icon_book = self.icon_delete = self.icon_calendar = None

        title = ctk.CTkLabel(
            self.win,
            text=f"Prenotazione Scrivanie\n{office_id} — {floor_name}",
            font=("Helvetica", 32, "bold"),
            text_color="#00E676"
        )
        title.pack(pady=20)

        # ---------------------------------------------------------
        # BARRA SUPERIORE
        # ---------------------------------------------------------
        top_frame = ctk.CTkFrame(self.win, corner_radius=15, fg_color="#393E46")
        top_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(
            top_frame, text="Data:", font=("Helvetica", 18), text_color="#EEEEEE"
        ).pack(side="left", padx=10)

        self.date = DateEntry(top_frame, date_pattern="yyyy-mm-dd")
        self.date.pack(side="left", padx=10)
        self.date.bind("<<DateEntrySelected>>", lambda e: self.load())

        self.filter_var = tk.StringVar(value="Giorno")
        filter_menu = ctk.CTkOptionMenu(
            top_frame,
            values=["Giorno", "Settimana", "Mese"],
            variable=self.filter_var,
            width=150,
            height=45,
            fg_color="#00ADB5",
            button_color="#0097A7",
            text_color="black",
            command=lambda _: self.load()
        )
        filter_menu.pack(side="left", padx=10)

        ctk.CTkButton(
            top_frame,
            text="Carica scrivanie",
            image=self.icon_calendar,
            compound="left",
            height=45,
            fg_color="#00ADB5",
            hover_color="#0097A7",
            text_color="black",
            command=self.load
        ).pack(side="left", padx=20)

        # ---------------------------------------------------------
        # FRAME PRINCIPALE
        # ---------------------------------------------------------
        main_frame = ctk.CTkFrame(self.win, corner_radius=15, fg_color="#222831")
        main_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # ---------------------------------------------------------
        # SINISTRA — LISTA SCRIVANIE
        # ---------------------------------------------------------
        left_frame = ctk.CTkFrame(main_frame, corner_radius=15, fg_color="#393E46")
        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            left_frame, text="Scrivanie", font=("Helvetica", 22, "bold"), text_color="#00E676"
        ).pack(pady=10)

        self.listbox = tk.Listbox(
            left_frame, width=45, height=20, font=("Helvetica", 14), bg="#EEEEEE"
        )
        self.listbox.pack(pady=10, fill="both", expand=True)

        button_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        button_frame.pack(pady=10)

        ctk.CTkButton(
            button_frame,
            text="Prenota",
            image=self.icon_book,
            compound="left",
            width=180,
            height=45,
            fg_color="#00ADB5",
            hover_color="#0097A7",
            text_color="black",
            command=self.book
        ).pack(pady=5)

        ctk.CTkButton(
            button_frame,
            text="Cancella",
            image=self.icon_delete,
            compound="left",
            width=180,
            height=45,
            fg_color="#FF5252",
            hover_color="#D32F2F",
            text_color="black",
            command=self.cancel
        ).pack(pady=5)

        # ---------------------------------------------------------
        # CENTRO — MINI‑MAPPA
        # ---------------------------------------------------------
        center_frame = ctk.CTkFrame(main_frame, corner_radius=15, fg_color="#393E46")
        center_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            center_frame,
            text="Mappa piano",
            font=("Helvetica", 22, "bold"),
            text_color="#00E676"
        ).pack(pady=10)

        self.canvas = tk.Canvas(center_frame, bg="#222831")
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)

        self.canvas.bind("<MouseWheel>", self.on_zoom)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # ---------------------------------------------------------
        # DESTRA — MIE PRENOTAZIONI
        # ---------------------------------------------------------
        right_frame = ctk.CTkFrame(main_frame, corner_radius=15, fg_color="#393E46")
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            right_frame,
            text="Le mie prenotazioni",
            font=("Helvetica", 22, "bold"),
            text_color="#00E676"
        ).pack(pady=10)

        self.my_bookings = tk.Listbox(
            right_frame, width=45, height=20, font=("Helvetica", 14), bg="#EEEEEE"
        )
        self.my_bookings.pack(pady=10, fill="both", expand=True)

        # ---------------------------------------------------------
        # CONFIG PIANO
        # ---------------------------------------------------------
        self.refresh_config()
        self.load_my_bookings()
        self.load()

    # ---------------------------------------------------------
    # REFRESH CONFIG
    # ---------------------------------------------------------
    def refresh_config(self):
        reload_config()
        self.office = get_office_by_name(self.office_id)
        self.floor = get_floor(self.office, self.floor_name)
        self.desks_cfg = self.floor["desks"]

    # ---------------------------------------------------------
    # CALCOLO RANGE DATE
    # ---------------------------------------------------------
    def _get_dates_for_filter(self):
        selected_date = self.date.get_date()
        mode = self.filter_var.get()

        if mode == "Giorno":
            return [selected_date.strftime("%Y-%m-%d")]

        elif mode == "Settimana":
            start = selected_date - timedelta(days=selected_date.weekday())
            return [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

        elif mode == "Mese":
            start = selected_date.replace(day=1)
            next_month = (start.replace(day=28) + timedelta(days=4)).replace(day=1)
            days = (next_month - start).days
            return [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]

        return [selected_date.strftime("%Y-%m-%d")]

    # ---------------------------------------------------------
    # CARICA SCRIVANIE
    # ---------------------------------------------------------
    def load(self):
        dates = self._get_dates_for_filter()
        selected_date_str = self.date.get_date().strftime("%Y-%m-%d")

        booked_with_user = get_booked_desks_with_user(selected_date_str)
        booked_map = {desk: user for desk, user in booked_with_user}

        booked_names = set()
        for d in dates:
            for _, name in get_booked_desks(d):
                booked_names.add(name)

        self.listbox.delete(0, tk.END)

        self.listbox.insert(tk.END, f"DATA: {selected_date_str}")
        self.listbox.insert(tk.END, "LIBERE:")
        for d in self.desks_cfg:
            if d["name"] not in booked_names:
                self.listbox.insert(tk.END, f"FREE | {d['name']} | {selected_date_str}")

        self.listbox.insert(tk.END, "")
        self.listbox.insert(tk.END, "OCCUPATE:")
        for d in self.desks_cfg:
            if d["name"] in booked_names:
                self.listbox.insert(tk.END, f"BOOKED | {d['name']} | {selected_date_str}")

        self.win.after(50, lambda: self.draw_minimap(booked_names, booked_map))

    # ---------------------------------------------------------
    # MINI‑MAPPA
    # ---------------------------------------------------------
    def draw_minimap(self, booked_names, booked_map):
        self.canvas.delete("all")
        self.desk_positions = {}

        if not self.desks_cfg:
            return

        xs = [d["x"] for d in self.desks_cfg]
        ys = [d["y"] for d in self.desks_cfg]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        w = max(self.canvas.winfo_width(), 300)
        h = max(self.canvas.winfo_height(), 200)

        dx = max_x - min_x if max_x != min_x else 1
        dy = max_y - min_y if max_y != min_y else 1

        margin = 40 * self.zoom_factor
        r = 10 * self.zoom_factor

        for d in self.desks_cfg:
            name = d["name"]
            x = d["x"]
            y = d["y"]

            nx = (x - min_x) / dx
            ny = (y - min_y) / dy

            cx = margin + nx * (w - 2 * margin)
            cy = margin + ny * (h - 2 * margin)

            if name in booked_names:
                fill = "#FF5252"
                outline = "#D32F2F"
            else:
                fill = "#00E676"
                outline = "#00C96B"

            self.canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                fill=fill, outline=outline, width=2
            )

            self.canvas.create_text(
                cx, cy - 18 * self.zoom_factor,
                text=name,
                fill="#EEEEEE",
                font=("Helvetica", max(7, int(9 * self.zoom_factor)), "bold")
            )

            if name in booked_map:
                self.canvas.create_text(
                    cx, cy + 18 * self.zoom_factor,
                    text=booked_map[name],
                    fill="#FF5252",
                    font=("Helvetica", max(7, int(8 * self.zoom_factor)), "bold")
                )

            frame = tk.Frame(self.canvas, width=20, height=20)
            self.canvas.create_window(cx, cy, window=frame)

            if name in booked_map:
                Tooltip(
                    frame,
                    f"{name}\nPrenotata da: {booked_map[name]}\nGiorno: {self.date.get_date()}"
                )
            else:
                Tooltip(
                    frame,
                    f"{name}\nLibera\nGiorno: {self.date.get_date()}"
                )

            self.desk_positions[name] = (cx, cy)

    # ---------------------------------------------------------
    # ZOOM
    # ---------------------------------------------------------
    def on_zoom(self, event):
        if event.delta > 0:
            self.zoom_factor = min(2.5, self.zoom_factor + 0.1)
        else:
            self.zoom_factor = max(0.5, self.zoom_factor - 0.1)
        self.load()

    # ---------------------------------------------------------
    # CLICK SU MINI‑MAPPA
    # ---------------------------------------------------------
    def on_canvas_click(self, event):
        if not self.desk_positions:
            return

        closest_name = None
        closest_dist = None

        for name, (cx, cy) in self.desk_positions.items():
            dist = (cx - event.x) ** 2 + (cy - event.y) ** 2
            if closest_dist is None or dist < closest_dist:
                closest_dist = dist
                closest_name = name

        if closest_name is None:
            return

        for i in range(self.listbox.size()):
            text = self.listbox.get(i)
            if f"| {closest_name} |" in text:
                self.listbox.selection_clear(0, tk.END)
                self.listbox.selection_set(i)
                self.listbox.see(i)
                break

    # ---------------------------------------------------------
    # MIE PRENOTAZIONI
    # ---------------------------------------------------------
    def load_my_bookings(self):
        self.my_bookings.delete(0, tk.END)
        rows = get_user_bookings(self.user_id)

        for booking_id, desk_name, date in rows:
            formatted = f"{date} — {desk_name}  (ID: {booking_id})"
            self.my_bookings.insert(tk.END, formatted)

    # ---------------------------------------------------------
    # PRENOTA
    # ---------------------------------------------------------
    def book(self):
        sel = self.listbox.curselection()
        if not sel:
            return

        text = self.listbox.get(sel[0])
        if not text.startswith("FREE"):
            messagebox.showwarning("Attenzione", "Seleziona una scrivania libera")
            return

        parts = [p.strip() for p in text.split("|")]
        if len(parts) < 3:
            messagebox.showerror("Errore", "Formato riga non valido")
            return

        desk_name = parts[1]
        date_str = parts[2]

        free = get_free_desks(date_str)
        desk_id = None
        for d in free:
            if d[1] == desk_name:
                desk_id = d[0]
                break

        if desk_id is None:
            messagebox.showerror("Errore", "Scrivania non trovata nel database")
            return

        if not book_desk(self.user_id, desk_id, date_str):
            messagebox.showerror("Errore", "Scrivania già prenotata")
            return

        self.load()
        self.load_my_bookings()

    # ---------------------------------------------------------
    # CANCELLA
    # ---------------------------------------------------------
    def cancel(self):
        sel = self.my_bookings.curselection()
        if not sel:
            return

        row = self.my_bookings.get(sel[0])
        booking_id = int(row.split("(ID: ")[1].replace(")", ""))

        cancel_booking(booking_id, is_superuser=(self.role == "admin"))

        self.load()
        self.load_my_bookings()
