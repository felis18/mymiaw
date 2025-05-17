# File: gui.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import database as db
import logic as lg
import pandas as pd
from datetime import datetime, timedelta
import calendar

# Impor dari file-file yang telah dipecah
from gui_constants import *
from gui_validators import Validators
from gui_saldo_handlers import SaldoHandlers
from gui_penjualan_handlers import PenjualanHandlers
from gui_pinjaman_handlers import PinjamanHandlers
from gui_pengeluaran_handlers import PengeluaranHandlers
from gui_tab_builders import TabBuilderHandlers
from gui_export_handlers import ExportHandlers

class SalesApp(
    Validators, 
    SaldoHandlers, 
    PenjualanHandlers, 
    PinjamanHandlers, 
    PengeluaranHandlers, 
    TabBuilderHandlers, 
    ExportHandlers
):
    def __init__(self, root):
        self.root = root
        self.root.title("AR STORE - Aplikasi Penjualan By. Andi (Modern Look V4 Refactored)")
        self.root.geometry("1250x850")
        self.root.configure(bg=SECONDARY_COLOR)

        self.conn = db.create_connection()
        db.create_tables(self.conn) # Memastikan semua tabel ada, termasuk yang baru

        start_month, end_month = lg.get_month_range()
        self.start_date_filter = tk.StringVar(value=start_month)
        self.end_date_filter = tk.StringVar(value=end_month)

        self.setup_styles()
        self.create_widgets() # Metode ini sekarang akan memanggil metode dari mixin jika perlu
        self.update_dashboard_datetime()
        self.load_initial_dashboard_data()

    def setup_styles(self):
        style = ttk.Style(self.root)
        style.theme_use("clam") 

        style.configure(".", background=SECONDARY_COLOR, foreground=TEXT_COLOR_DARK, font=FONT_NORMAL)
        style.configure("Main.TFrame", background=SECONDARY_COLOR)
        style.configure("ContentPage.TFrame", background="#FFFFFF", relief=tk.SOLID, borderwidth=1) 
        style.configure("Header.TFrame", background=PRIMARY_COLOR)
        style.configure("DashboardInfo.TFrame", background="#FFFFFF") 
        style.configure("Dialog.TFrame", background=SECONDARY_COLOR) 
        style.configure("SubContent.TFrame", background=SECONDARY_COLOR) 

        style.configure("TLabelFrame", font=FONT_LABEL_FRAME_TITLE, padding=(10, 5, 10, 10), background=SECONDARY_COLOR, relief=tk.GROOVE, borderwidth=1, lightcolor=PRIMARY_COLOR, darkcolor=PRIMARY_COLOR)
        style.configure("TLabelFrame.Label", font=FONT_LABEL_FRAME_TITLE, foreground=PRIMARY_COLOR, background=SECONDARY_COLOR, padding=(0,0,0,5)) 

        style.configure("TLabel", font=FONT_NORMAL, background=SECONDARY_COLOR, foreground=TEXT_COLOR_DARK)
        style.configure("Header.TLabel", font=FONT_DATETIME_HEADER, background=PRIMARY_COLOR, foreground=TEXT_COLOR_ON_PRIMARY)
        style.configure("SaldoDisplay.TLabel", font=FONT_SALDO_UTAMA, background="#FFFFFF", foreground=PRIMARY_COLOR)
        style.configure("DashboardValue.TLabel", font=FONT_BOLD, background="#FFFFFF", foreground=TEXT_COLOR_MEDIUM)
        style.configure("DashboardKey.TLabel", font=FONT_NORMAL, background="#FFFFFF", foreground=TEXT_COLOR_LIGHT)
        style.configure("Red.TLabel", foreground="red", background=SECONDARY_COLOR) 
        style.configure("Blue.TLabel", foreground="blue", background=SECONDARY_COLOR)
        style.configure("Green.TLabel", foreground="green", background=SECONDARY_COLOR)
        style.configure("Yellow.TLabel", foreground="#B8860B", background=SECONDARY_COLOR)
        style.configure("Orange.TLabel", foreground="#FF8C00", background=SECONDARY_COLOR)
        style.configure("DashboardValueOrange.TLabel", font=FONT_BOLD, background="#FFFFFF", foreground="#FF8C00")
        style.configure("DashboardValueRed.TLabel", font=FONT_BOLD, background="#FFFFFF", foreground="#D32F2F")


        style.configure("Dialog.TLabel", background=SECONDARY_COLOR, font=FONT_NORMAL) 

        style.configure("TButton", font=FONT_BUTTON, padding=(10, 5)) 
        style.configure("Accent.TButton", font=(FONT_BUTTON[0], FONT_BUTTON[1], "bold"), background=ACCENT_COLOR, foreground=TEXT_COLOR_DARK) 
        style.map("Accent.TButton", background=[('active', '#FF8A65'), ('pressed', '#FF7043')], foreground=[('active', TEXT_COLOR_DARK)])
        style.configure("Danger.TButton", font=FONT_BUTTON, background="#E53935", foreground=TEXT_COLOR_ON_PRIMARY) 
        style.map("Danger.TButton", background=[('active', '#D32F2F'), ('pressed', '#C62828')])

        style.configure("TEntry", font=FONT_NORMAL, padding=5)
        style.configure("TCombobox", font=FONT_NORMAL, padding=5)
        style.map("TEntry", fieldbackground=[('focus', "#E3F2FD")]) 

        style.configure("TNotebook", background=SECONDARY_COLOR, tabmargins=[2, 5, 2, 0])
        style.configure("TNotebook.Tab", font=FONT_NORMAL, padding=[10, 5]) 
        style.map("TNotebook.Tab", background=[("selected", "#FFFFFF"), ('active', "#E0E0E0")], foreground=[("selected", PRIMARY_COLOR), ('active', TEXT_COLOR_DARK)])

        style.configure("Treeview", font=FONT_TREEVIEW_ROW, rowheight=28, fieldbackground="#FFFFFF") 
        style.configure("Treeview.Heading", font=FONT_TREEVIEW_HEADING, background=PRIMARY_COLOR, foreground=TEXT_COLOR_ON_PRIMARY, padding=5)
        style.map("Treeview.Heading", background=[('active', "#283593"), ('pressed', '#1A237E')])

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10", style="Main.TFrame")
        main_frame.pack(expand=True, fill=tk.BOTH)

        header_frame = ttk.Frame(main_frame, style="Header.TFrame", padding=(0,0,0,10))
        header_frame.pack(fill=tk.X, pady=(0,10))
        app_title_label = ttk.Label(header_frame, text="AR STORE - Aplikasi Penjualan", font=FONT_TITLE_HEADER, style="Header.TLabel")
        app_title_label.pack(side=tk.LEFT, padx=15, pady=10)
        self.datetime_label = ttk.Label(header_frame, text="", style="Header.TLabel")
        self.datetime_label.pack(side=tk.RIGHT, padx=15, pady=10)

        dashboard_container_frame = ttk.LabelFrame(main_frame, text="Dasbor Informasi", padding=(15,10,15,15))
        dashboard_container_frame.pack(fill=tk.X, pady=5)

        saldo_frame_left = ttk.Frame(dashboard_container_frame, style="DashboardInfo.TFrame")
        saldo_frame_left.pack(side=tk.LEFT, padx=(0, 15), fill=tk.Y)
        ttk.Label(saldo_frame_left, text="Saldo Aktual Kas:", style="DashboardKey.TLabel").pack(anchor=tk.W, pady=(0,3))
        self.saldo_label = ttk.Label(saldo_frame_left, text="Rp 0", style="SaldoDisplay.TLabel")
        self.saldo_label.pack(anchor=tk.W)

        info_frame_right = ttk.Frame(dashboard_container_frame, style="DashboardInfo.TFrame")
        info_frame_right.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        ttk.Label(info_frame_right, text="Total Kredit (Semua Belum Lunas):", style="DashboardKey.TLabel").grid(row=0, column=0, sticky=tk.W, padx=5, pady=3)
        self.total_kredit_label = ttk.Label(info_frame_right, text="Rp 0", style="DashboardValue.TLabel Red.TLabel")
        self.total_kredit_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=3)
        ttk.Label(info_frame_right, text="Total Modal (Filter):", style="DashboardKey.TLabel").grid(row=0, column=2, sticky=tk.W, padx=(20,5), pady=3)
        self.total_modal_label = ttk.Label(info_frame_right, text="Rp 0", style="DashboardValue.TLabel Yellow.TLabel")
        self.total_modal_label.grid(row=0, column=3, sticky=tk.W, padx=5, pady=3)
        ttk.Label(info_frame_right, text="Total Pinjaman Aktif:", style="DashboardKey.TLabel").grid(row=0, column=4, sticky=tk.W, padx=(20,5), pady=3)
        self.total_pinjaman_aktif_label = ttk.Label(info_frame_right, text="Rp 0", style="DashboardValueOrange.TLabel")
        self.total_pinjaman_aktif_label.grid(row=0, column=5, sticky=tk.W, padx=5, pady=3)

        ttk.Label(info_frame_right, text="Total Laba (Filter):", style="DashboardKey.TLabel").grid(row=1, column=0, sticky=tk.W, padx=5, pady=3)
        self.laba_label = ttk.Label(info_frame_right, text="Rp 0", style="DashboardValue.TLabel Blue.TLabel")
        self.laba_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=3)
        ttk.Label(info_frame_right, text="Total Jual (Filter):", style="DashboardKey.TLabel").grid(row=1, column=2, sticky=tk.W, padx=(20,5), pady=3)
        self.total_jual_label = ttk.Label(info_frame_right, text="Rp 0", style="DashboardValue.TLabel Green.TLabel")
        self.total_jual_label.grid(row=1, column=3, sticky=tk.W, padx=5, pady=3)
        ttk.Label(info_frame_right, text="Total Pengeluaran Toko (Filter):", style="DashboardKey.TLabel").grid(row=1, column=4, sticky=tk.W, padx=(20,5), pady=3)
        self.total_pengeluaran_label = ttk.Label(info_frame_right, text="Rp 0", style="DashboardValue.TLabel Red.TLabel")
        self.total_pengeluaran_label.grid(row=1, column=5, sticky=tk.W, padx=5, pady=3)

        info_frame_right.columnconfigure(1, weight=1)
        info_frame_right.columnconfigure(3, weight=1)
        info_frame_right.columnconfigure(5, weight=1)

        control_frame = ttk.LabelFrame(main_frame, text="Kontrol & Aksi", padding="10")
        control_frame.pack(fill=tk.X, pady=10)

        filter_subframe = ttk.Frame(control_frame, style="SubContent.TFrame")
        filter_subframe.pack(side=tk.LEFT, padx=(0,10), fill=tk.X, expand=True)

        ttk.Label(filter_subframe, text="Filter Laporan Dari:", style="TLabel").grid(row=0, column=0, padx=(0,5), pady=5, sticky=tk.W)
        self.start_date_entry_filter = DateEntry(filter_subframe, width=12, date_pattern='yyyy-mm-dd',
                                                 textvariable=self.start_date_filter, font=FONT_NORMAL,
                                                 background=PRIMARY_COLOR, foreground=TEXT_COLOR_ON_PRIMARY,
                                                 headersbackground=PRIMARY_COLOR, headersforeground=TEXT_COLOR_ON_PRIMARY,
                                                 selectbackground=ACCENT_COLOR, selectforeground=TEXT_COLOR_DARK,
                                                 disabledbackground=SECONDARY_COLOR)
        self.start_date_entry_filter.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(filter_subframe, text="Sampai:", style="TLabel").grid(row=0, column=2, padx=(10,5), pady=5, sticky=tk.W)
        self.end_date_entry_filter = DateEntry(filter_subframe, width=12, date_pattern='yyyy-mm-dd',
                                               textvariable=self.end_date_filter, font=FONT_NORMAL,
                                               background=PRIMARY_COLOR, foreground=TEXT_COLOR_ON_PRIMARY,
                                               headersbackground=PRIMARY_COLOR, headersforeground=TEXT_COLOR_ON_PRIMARY,
                                               selectbackground=ACCENT_COLOR, selectforeground=TEXT_COLOR_DARK,
                                               disabledbackground=SECONDARY_COLOR)
        self.end_date_entry_filter.grid(row=0, column=3, padx=5, pady=5)

        self.filter_button = ttk.Button(filter_subframe, text="Terapkan Filter", command=self.apply_filter_and_refresh_dashboard, style="Accent.TButton")
        self.filter_button.grid(row=0, column=4, padx=15, pady=5, ipady=2)

        action_buttons_subframe = ttk.Frame(control_frame, style="SubContent.TFrame")
        action_buttons_subframe.pack(side=tk.LEFT, padx=10)
        self.open_input_saldo_button = ttk.Button(action_buttons_subframe, text="Input Saldo Kas", command=self.open_input_saldo_window)
        self.open_input_saldo_button.pack(side=tk.LEFT, padx=5)
        self.open_riwayat_saldo_button = ttk.Button(action_buttons_subframe, text="Riwayat Saldo Kas", command=self.open_riwayat_saldo_window)
        self.open_riwayat_saldo_button.pack(side=tk.LEFT, padx=5)
        self.open_input_penjualan_button = ttk.Button(action_buttons_subframe, text="Input Penjualan Baru", command=self.open_input_penjualan_window, style="Accent.TButton")
        self.open_input_penjualan_button.pack(side=tk.LEFT, padx=5, ipady=2)
        
        self.open_input_pengeluaran_button = ttk.Button(action_buttons_subframe, text="Input Pengeluaran Toko", command=self.open_input_pengeluaran_window)
        self.open_input_pengeluaran_button.pack(side=tk.LEFT, padx=5)
        
        self.open_input_pinjaman_button = ttk.Button(action_buttons_subframe, text="Input Pinjaman Modal", command=self.open_input_pinjaman_window)
        self.open_input_pinjaman_button.pack(side=tk.LEFT, padx=5)
        self.open_riwayat_pinjaman_button = ttk.Button(action_buttons_subframe, text="Riwayat Pinjaman Modal", command=self.open_riwayat_pinjaman_window)
        self.open_riwayat_pinjaman_button.pack(side=tk.LEFT, padx=5)

        self.notebook = ttk.Notebook(main_frame, style="TNotebook")
        self.notebook.pack(expand=True, fill=tk.BOTH, pady=(5,0))
        
        self.tab_global = ttk.Frame(self.notebook, style="ContentPage.TFrame", padding=10)
        self.notebook.add(self.tab_global, text="Riwayat Transaksi Global (Lunas & Tunai)")
        self.create_global_transactions_tab()

        self.tab_kredit_aktif = ttk.Frame(self.notebook, style="ContentPage.TFrame", padding=10)
        self.notebook.add(self.tab_kredit_aktif, text="Transaksi Kredit Belum Lunas (Filter Tanggal)")
        self.create_kredit_aktif_tab()

        self.tab_pinjaman = ttk.Frame(self.notebook, style="ContentPage.TFrame", padding=10)
        self.notebook.add(self.tab_pinjaman, text="Riwayat Pinjaman Modal")
        self.create_riwayat_pinjaman_tab()
        
        self.tab_pengeluaran_internal = ttk.Frame(self.notebook, style="ContentPage.TFrame", padding=10)
        self.notebook.add(self.tab_pengeluaran_internal, text="Riwayat Pengeluaran Toko")
        self.create_riwayat_pengeluaran_internal_tab()

        export_frame = ttk.LabelFrame(main_frame, text="Ekspor Data", padding="10")
        export_frame.pack(fill=tk.X, pady=10, side=tk.BOTTOM)
        self.export_excel_button = ttk.Button(export_frame, text="Ekspor Penjualan ke Excel", command=self.export_to_excel)
        self.export_excel_button.pack(side=tk.LEFT, padx=5)
        self.export_csv_button = ttk.Button(export_frame, text="Ekspor Penjualan ke CSV", command=self.export_to_csv)
        self.export_csv_button.pack(side=tk.LEFT, padx=5)
        self.export_pinjaman_excel_button = ttk.Button(export_frame, text="Ekspor Pinjaman ke Excel", command=self.export_pinjaman_to_excel)
        self.export_pinjaman_excel_button.pack(side=tk.LEFT, padx=5)
        self.export_pengeluaran_excel_button = ttk.Button(export_frame, text="Ekspor Pengeluaran ke Excel", command=self.export_pengeluaran_to_excel)
        self.export_pengeluaran_excel_button.pack(side=tk.LEFT, padx=5)

    # --- Metode Inti Aplikasi yang Mungkin Tetap di Kelas Utama ---
    def update_dashboard_datetime(self):
        full_dt_str, date_str, time_str = lg.get_current_datetime_str()
        self.datetime_label.config(text=f"{date_str} | {time_str}")
        self.root.after(1000, self.update_dashboard_datetime)

    def load_initial_dashboard_data(self):
        self.update_saldo_display()
        self.update_pinjaman_aktif_display() 
        self.update_total_kredit_belum_lunas_display() 
        self.apply_filter_and_refresh_dashboard() 

    def update_saldo_display(self):
        saldo_terakhir = db.get_saldo_terakhir(self.conn)
        self.saldo_label.config(text=f"{lg.format_rupiah(saldo_terakhir)}")

    def update_pinjaman_aktif_display(self):
        total_pinjaman_aktif = db.get_total_pinjaman_aktif(self.conn)
        self.total_pinjaman_aktif_label.config(text=f"{lg.format_rupiah(total_pinjaman_aktif)}")

    def update_total_kredit_belum_lunas_display(self):
        kredit_belum_lunas_all = db.get_kredit_belum_lunas_all(self.conn)
        total_kredit_belum_lunas_val = sum(sale[4] for sale in kredit_belum_lunas_all) if kredit_belum_lunas_all else 0 
        self.total_kredit_label.config(text=f"{lg.format_rupiah(total_kredit_belum_lunas_val)}")

    def apply_filter_and_refresh_dashboard(self):
        start_date = self.start_date_filter.get()
        end_date = self.end_date_filter.get()
        if not start_date or not end_date:
            messagebox.showwarning("Filter Tidak Lengkap", "Silakan pilih tanggal mulai dan tanggal akhir untuk filter.")
            return
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Format Tanggal Salah", "Format tanggal filter tidak valid. Gunakan YYYY-MM-DD.")
            return

        all_sales_in_filter = db.get_penjualan_by_date_range(self.conn, start_date, end_date)
        total_laba_val_filter = sum(sale[5] for sale in all_sales_in_filter) if all_sales_in_filter else 0 
        total_modal_val_filter = sum(sale[3] for sale in all_sales_in_filter) if all_sales_in_filter else 0 
        total_jual_val_filter = sum(sale[4] for sale in all_sales_in_filter) if all_sales_in_filter else 0 

        self.laba_label.config(text=f"{lg.format_rupiah(total_laba_val_filter)}")
        self.total_modal_label.config(text=f"{lg.format_rupiah(total_modal_val_filter)}")
        self.total_jual_label.config(text=f"{lg.format_rupiah(total_jual_val_filter)}")
        
        all_pengeluaran_in_filter = db.get_all_pengeluaran_internal(self.conn, start_date, end_date)
        total_pengeluaran_val_filter = sum(peng[2] for peng in all_pengeluaran_in_filter) if all_pengeluaran_in_filter else 0 
        self.total_pengeluaran_label.config(text=f"{lg.format_rupiah(total_pengeluaran_val_filter)}")

        self.update_total_kredit_belum_lunas_display()
        self.update_pinjaman_aktif_display()
        self.update_saldo_display() 

        self.load_global_transactions() 
        self.load_kredit_aktif_transactions() 
        self.load_riwayat_pinjaman_data()
        self.load_riwayat_pengeluaran_internal_data() 

        self.on_global_select() 
        self.on_kredit_select() 
        self.on_pinjaman_select()
        self.on_pengeluaran_internal_select() 

    def hapus_transaksi_terpilih(self):
        # Placeholder: tampilkan pesan info, ganti dengan logika hapus transaksi jika diperlukan
        from tkinter import messagebox
        messagebox.showinfo("Info", "Fitur hapus transaksi terpilih belum diimplementasikan.", parent=self.root)

    def lunasi_kredit_terpilih(self):
        selected_item = self.tree_kredit.focus()
        if not selected_item:
            from tkinter import messagebox
            messagebox.showwarning("Peringatan", "Pilih kredit yang akan dilunasi.", parent=self.root)
            return

        item_details = self.tree_kredit.item(selected_item)
        kredit_id = item_details['values'][0]

        import database as db
        from tkinter import messagebox
        from datetime import datetime
        import logic as lg

        kredit_data = db.get_kredit_by_id(self.conn, kredit_id)
        if not kredit_data:
            messagebox.showerror("Error", f"Data kredit ID {kredit_id} tidak ditemukan.", parent=self.root)
            return

        # Asumsi urutan field: (id, tanggal, nama, jumlah, keterangan, status, id_saldo, tanggal_lunas)
        _, _, nama_kredit, jumlah_kredit, keterangan_kredit, status_kredit, _, _ = kredit_data

        if status_kredit == 'Lunas':
            messagebox.showinfo("Info", f"Kredit ID {kredit_id} ('{nama_kredit}') sudah lunas.", parent=self.root)
            self.load_riwayat_kredit_data()
            return

        if messagebox.askyesno(
            "Konfirmasi Pelunasan",
            f"Yakin melunasi kredit '{nama_kredit}' (ID: {kredit_id}) sebesar {lg.format_rupiah(jumlah_kredit)}?",
            parent=self.root
        ):
            tanggal_pelunasan = datetime.now().strftime("%Y-%m-%d")
            if db.lunasi_kredit(self.conn, kredit_id, tanggal_pelunasan):
                db.update_saldo(self.conn, -jumlah_kredit, f"Pelunasan Kredit: {nama_kredit} (ID {kredit_id}) (-{lg.format_rupiah(jumlah_kredit)})")
                messagebox.showinfo("Sukses", f"Kredit ID {kredit_id} ('{nama_kredit}') berhasil dilunasi.", parent=self.root)
                self.apply_filter_and_refresh_dashboard()
            else:
                messagebox.showerror("Error Database", f"Gagal melunasi kredit ID {kredit_id}.", parent=self.root)

    def create_kredit_aktif_tab(self):
        parent_frame = ttk.Frame(self.tab_kredit_aktif, style="ContentPage.TFrame")
        parent_frame.pack(expand=True, fill=tk.BOTH)
        tree_kredit = ttk.Treeview(parent_frame, columns=("ID", "Nama", "Jumlah", "Status"), show="headings")
        tree_kredit.heading("ID", text="ID")
        tree_kredit.heading("Nama", text="Nama")
        tree_kredit.heading("Jumlah", text="Jumlah")
        tree_kredit.heading("Status", text="Status")
        tree_kredit.pack(expand=True, fill=tk.BOTH)
        self.tree_kredit = tree_kredit
        self.tree_kredit_aktif = tree_kredit

    def on_closing(self):
        if self.conn:
            self.conn.close()
        self.root.destroy()

# if __name__ == "__main__":
#     root = tk.Tk()
#     app = SalesApp(root)
#     root.protocol("WM_DELETE_WINDOW", app.on_closing)
#     root.mainloop()