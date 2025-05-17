import tkinter as tk
from gui import SalesApp # Pastikan gui.py ada di direktori yang sama
import database as db # Import database untuk membuat tabel di awal

if __name__ == "__main__":
    # Membuat koneksi database utama di awal dan memastikan tabel ada
    main_conn = db.create_connection()
    if main_conn:
        db.create_tables(main_conn)
        # Koneksi akan di-manage oleh class SalesApp, jadi tidak perlu ditutup di sini

    root = tk.Tk()
    app = SalesApp(root) # SalesApp akan menggunakan koneksi sendiri yang dibuat di __init__
    root.protocol("WM_DELETE_WINDOW", app.on_closing) # Handle penutupan window
    root.mainloop()

    # Setelah mainloop berakhir dan app ditutup, koneksi DB di SalesApp.__del__ atau on_closing akan menutupnya