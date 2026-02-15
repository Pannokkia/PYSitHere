import customtkinter as ctk
from database.database import init_db
from gui.gui import MainWindow


# ---------------------------------------------------------
# TEMA GRAFICO GLOBALE
# ---------------------------------------------------------
def setup_theme():
    # Modalità scura moderna
    ctk.set_appearance_mode("dark")

    # Tema con colori vivi (puoi usare: "green", "blue", "dark-blue")
    ctk.set_default_color_theme("green")

    # Palette aziendale (solo come riferimento)
    # primary:        #00ADB5
    # primary_hover:  #0097A7
    # accent:         #00E676
    # bg_dark:        #222831
    # bg_field:       #393E46
    # text_light:     #EEEEEE


# ---------------------------------------------------------
# AVVIO APPLICAZIONE
# ---------------------------------------------------------
def main():
    # Inizializza database (crea tabelle, migra colonne, importa scrivanie)
    init_db()

    # Applica tema globale
    setup_theme()

    # Crea finestra principale
    root = ctk.CTk()
    root.title("Desk Booking System")

    # Avvia GUI principale
    MainWindow(root)

    # Loop principale
    root.mainloop()


if __name__ == "__main__":
    main()