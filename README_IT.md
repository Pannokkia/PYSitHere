
---

# 🇬🇧 **README.md (English Version)**

```markdown
# 🖥️ PySitHere – Desk Booking System
A complete desktop application for managing office desk reservations.  
Built in **Python** with a modern UI powered by **CustomTkinter**.

License: **MIT**

---

## ✨ Main Features

### 👤 User Management
- Login with roles: **user** and **superuser**
- Create, edit, delete users
- Block/unblock accounts
- Password reset
- User search + filters
- Pagination

---

### 🗺️ Desk Booking
- Select **date** via calendar widget
- Advanced filters:
  - **Day**
  - **Week**
  - **Month**
- Interactive floor mini‑map:
  - **green** desks → available  
  - **red** desks → booked  
- Tooltips (desk name, status, date)
- **Zoom** with mouse wheel
- **Click on mini‑map to select a desk**
- Personal booking list with date and ID
- One‑click booking and cancellation

---

### 🏢 Office & Desk Configuration
- Graphical desk editor:
  - add desk
  - delete desk
  - drag to reposition
- Automatic saving to `config.json`
- Multi‑office and multi‑floor support

---

### 🗄️ Database
- SQLite backend
- Tables:
  - `users`
  - `desks`
  - `bookings`
- Automatic migrations
- Auto‑creation of superuser `admin/admin`

---

## 🧩 Office & Desk Configuration (config.json)

The `config.json` file defines:

- offices
- floors
- desks
- graphical coordinates

### Example:

```json
{
  "offices": [
    {
      "name": "Milan HQ",
      "floors": [
        {
          "name": "Floor 1",
          "desks": [
            { "name": "Desk 1", "x": 120, "y": 80 },
            { "name": "Desk 2", "x": 260, "y": 80 }
          ]
        }
      ]
    }
  ]
}


📦 Required Python Modules
Install:

bash
pip install customtkinter tkcalendar pillow

Modules used:

    - customtkinter

    - tkcalendar

    - Pillow

    - sqlite3 (standard)

    - json (standard)

pip install customtkinter tkcalendar pillow

▶️ Run the application
python main.py