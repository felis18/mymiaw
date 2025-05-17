# File: gui_tab_builders.py

import tkinter as tk
from tkinter import ttk
import logic as lg
import database as db
# Asumsi gui_constants.py ada di direktori yang sama
from gui_constants import *

class TabBuilderHandlers:
    def create_global_transactions_tab(self):
        action_frame_global = ttk.Frame(self.tab_global, style="ContentPage.TFrame")
        action_frame_global.pack(fill=tk.X, pady=(0,5), padx=0) 
        # Pastikan self.open_edit_penjualan_window didefinisikan di SalesApp atau di mixin yang diwarisinya
        self.edit_button_global = ttk.Button(action_frame_global, text="Edit Terpilih", command=self.open_edit_penjualan_window, state=tk.DISABLED)
        self.edit_button_global.pack(side=tk.LEFT, padx=(0,5))
        self.delete_button_global = ttk.Button(action_frame_global, text="Hapus Terpilih", command=self.hapus_transaksi_terpilih, state=tk.DISABLED, style="Danger.TButton")
        self.delete_button_global.pack(side=tk.LEFT, padx=5)
        
        cols = ("ID", "Tanggal", "Item", "Modal", "Jual", "Laba", "Bayar", "Status", "Tgl Lunas")
        self.tree_global = ttk.Treeview(self.tab_global, columns=cols, show='headings', selectmode="browse", style="Treeview")
        col_widths = {"ID": 40, "Tanggal": 110, "Item": 200, "Modal": 100, "Jual": 100, "Laba": 100, "Bayar": 80, "Status": 100, "Tgl Lunas":110}
        for col in cols:
            self.tree_global.heading(col, text=col)
            self.tree_global.column(col, width=col_widths[col], anchor=tk.W if col in ["Item", "Bayar", "Status"] else tk.E)
        
        scrollbar_y = ttk.Scrollbar(self.tab_global, orient=tk.VERTICAL, command=self.tree_global.yview)
        scrollbar_x = ttk.Scrollbar(self.tab_global, orient=tk.HORIZONTAL, command=self.tree_global.xview)
        self.tree_global.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree_global.pack(expand=True, fill=tk.BOTH)
        
        self.tree_global.tag_configure('tunai', foreground='#00695C') 
        self.tree_global.tag_configure('lunas', foreground=TEXT_COLOR_DARK) 
        
        self.tree_global.bind("<<TreeviewSelect>>", self.on_global_select)
        self.tree_global.bind("<Double-1>", lambda e: self.open_edit_penjualan_window()) 

    def load_global_transactions(self):
        for item in self.tree_global.get_children():
            self.tree_global.delete(item)
        start_date = self.start_date_filter.get()
        end_date = self.end_date_filter.get()
        transactions = db.get_global_transactions(self.conn, start_date, end_date)
        if transactions:
            for tx in transactions:
                tx_id, tanggal, item, modal, jual, laba, bayar, status, tgl_lunas = tx
                modal_f = lg.format_rupiah(modal)
                jual_f = lg.format_rupiah(jual)
                laba_f = lg.format_rupiah(laba)
                tgl_display = tanggal.split(" ")[0] if " " in tanggal else tanggal
                tgl_lunas_f = tgl_lunas if tgl_lunas else "-"
                status_display = status if status else "-"
                
                tag_to_apply = ()
                if bayar == "Tunai":
                    tag_to_apply = ('tunai',)
                elif bayar == "Kredit" and status == "Lunas":
                    tag_to_apply = ('lunas',)
                
                values = (tx_id, tgl_display, item, modal_f, jual_f, laba_f, bayar, status_display, tgl_lunas_f)
                self.tree_global.insert("", tk.END, values=values, tags=tag_to_apply)
        self.on_global_select()

    def on_global_select(self, event=None):
        selected_item = self.tree_global.focus()
        if selected_item:
            self.edit_button_global.config(state=tk.NORMAL)
            self.delete_button_global.config(state=tk.NORMAL)
        else:
            self.edit_button_global.config(state=tk.DISABLED)
            self.delete_button_global.config(state=tk.DISABLED)

    def create_kredit_aktif_tab(self):
        action_frame = ttk.Frame(self.tab_kredit_aktif, style="ContentPage.TFrame") 
        action_frame.pack(fill=tk.X, pady=(0,5), padx=0)
        lunasi_button = ttk.Button(action_frame, text="Lakukan Pelunasan Terpilih", command=self.lunasi_kredit_terpilih, state=tk.DISABLED, style="Accent.TButton")
        self.lunasi_button = lunasi_button
        lunasi_button.pack(side=tk.LEFT, padx=(0,5), ipady=2) 
        
        cols_kredit = ("ID", "Tanggal", "Item", "Modal", "Jual", "Status")
        self.tree_kredit_aktif = ttk.Treeview(self.tab_kredit_aktif, columns=cols_kredit, show='headings', selectmode="browse", style="Treeview")
        col_widths_kredit = {"ID": 40, "Tanggal": 110, "Item": 250, "Modal": 100, "Jual": 100, "Status": 100}
        for col in cols_kredit:
            self.tree_kredit_aktif.heading(col, text=col)
            self.tree_kredit_aktif.column(col, width=col_widths_kredit[col], anchor=tk.W if col in ["Item", "Status"] else tk.E)
        
        scrollbar_y_kredit = ttk.Scrollbar(self.tab_kredit_aktif, orient=tk.VERTICAL, command=self.tree_kredit_aktif.yview)
        scrollbar_x_kredit = ttk.Scrollbar(self.tab_kredit_aktif, orient=tk.HORIZONTAL, command=self.tree_kredit_aktif.xview)
        self.tree_kredit_aktif.configure(yscrollcommand=scrollbar_y_kredit.set, xscrollcommand=scrollbar_x_kredit.set)
        scrollbar_y_kredit.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x_kredit.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree_kredit_aktif.pack(expand=True, fill=tk.BOTH)
        
        self.tree_kredit_aktif.tag_configure('kredit_belum_lunas', foreground='#D32F2F') 
        
        self.tree_kredit_aktif.bind("<<TreeviewSelect>>", self.on_kredit_select)
        self.tree_kredit_aktif.bind("<Double-1>", lambda e: self.open_edit_penjualan_window())

    def on_kredit_select(self, event=None):
        selected_item = self.tree_kredit_aktif.focus()
        self.lunasi_button.config(state=tk.NORMAL if selected_item else tk.DISABLED)

    def load_kredit_aktif_transactions(self):
        for item in self.tree_kredit_aktif.get_children():
            self.tree_kredit_aktif.delete(item)
        start_date = self.start_date_filter.get()
        end_date = self.end_date_filter.get()
        transactions_kredit = db.get_kredit_belum_lunas(self.conn, start_date, end_date)
        if transactions_kredit:
            for tx in transactions_kredit:
                tx_id, tanggal, item, modal, jual, status = tx
                modal_f = lg.format_rupiah(modal)
                jual_f = lg.format_rupiah(jual)
                tgl_display = tanggal.split(" ")[0] if " " in tanggal else tanggal
                values = (tx_id, tgl_display, item, modal_f, jual_f, status)
                self.tree_kredit_aktif.insert("", tk.END, values=values, tags=('kredit_belum_lunas',))
        self.on_kredit_select()

    def create_riwayat_pinjaman_tab(self):
        action_frame = ttk.Frame(self.tab_pinjaman, style="ContentPage.TFrame") 
        action_frame.pack(fill=tk.X, pady=(0,5), padx=0)
        self.lunasi_pinjaman_button = ttk.Button(action_frame, text="Lunasi Pinjaman Terpilih", command=self.lunasi_pinjaman_terpilih, state=tk.DISABLED, style="Accent.TButton")
        self.lunasi_pinjaman_button.pack(side=tk.LEFT, padx=(0,5), ipady=2)

        cols_pinjaman = ("ID", "Tgl Pinjam", "Jumlah Pinjam", "Keterangan", "Status", "Tgl Lunas")
        self.tree_pinjaman = ttk.Treeview(self.tab_pinjaman, columns=cols_pinjaman, show='headings', selectmode="browse", style="Treeview")
        col_widths_pinjaman = {"ID": 40, "Tgl Pinjam": 110, "Jumlah Pinjam": 120, "Keterangan": 300, "Status": 80, "Tgl Lunas":110}
        for col in cols_pinjaman:
            self.tree_pinjaman.heading(col, text=col)
            self.tree_pinjaman.column(col, width=col_widths_pinjaman[col], anchor=tk.W if col in ["Keterangan", "Status"] else tk.E)
        
        scrollbar_y_pinjaman = ttk.Scrollbar(self.tab_pinjaman, orient=tk.VERTICAL, command=self.tree_pinjaman.yview)
        scrollbar_x_pinjaman = ttk.Scrollbar(self.tab_pinjaman, orient=tk.HORIZONTAL, command=self.tree_pinjaman.xview)
        self.tree_pinjaman.configure(yscrollcommand=scrollbar_y_pinjaman.set, xscrollcommand=scrollbar_x_pinjaman.set)
        scrollbar_y_pinjaman.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x_pinjaman.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree_pinjaman.pack(expand=True, fill=tk.BOTH)
        
        self.tree_pinjaman.tag_configure('aktif', foreground='#FF8C00') 
        self.tree_pinjaman.tag_configure('lunas', foreground='#006400') 
        
        self.tree_pinjaman.bind("<<TreeviewSelect>>", self.on_pinjaman_select)

    def load_riwayat_pinjaman_data(self):
        for item in self.tree_pinjaman.get_children():
            self.tree_pinjaman.delete(item)
        pinjaman_list = db.get_all_pinjaman_modal(self.conn) 
        if pinjaman_list:
            for pinjam in pinjaman_list:
                pinjam_id, tgl_pinjam, jumlah, keterangan, status, tgl_lunas, saldo_entry_id = pinjam
                jumlah_f = lg.format_rupiah(jumlah)
                tgl_lunas_f = tgl_lunas if tgl_lunas else "-"
                tag_to_apply = ('aktif',) if status == 'Aktif' else ('lunas',)
                values = (pinjam_id, tgl_pinjam, jumlah_f, keterangan, status, tgl_lunas_f)
                self.tree_pinjaman.insert("", tk.END, values=values, tags=tag_to_apply)
        self.on_pinjaman_select()

    def on_pinjaman_select(self, event=None):
        selected_item = self.tree_pinjaman.focus()
        if selected_item:
            item_details = self.tree_pinjaman.item(selected_item)
            status = item_details['values'][4] 
            self.lunasi_pinjaman_button.config(state=tk.NORMAL if status == 'Aktif' else tk.DISABLED)
        else:
            self.lunasi_pinjaman_button.config(state=tk.DISABLED)

    def create_riwayat_pengeluaran_internal_tab(self):
        action_frame = ttk.Frame(self.tab_pengeluaran_internal, style="ContentPage.TFrame") 
        action_frame.pack(fill=tk.X, pady=(0,5), padx=0)
        
        self.edit_pengeluaran_button = ttk.Button(action_frame, text="Edit Pengeluaran Terpilih", command=self.open_edit_pengeluaran_window, state=tk.DISABLED)
        self.edit_pengeluaran_button.pack(side=tk.LEFT, padx=(0,5))
        self.hapus_pengeluaran_button = ttk.Button(action_frame, text="Hapus Pengeluaran Terpilih", command=self.hapus_pengeluaran_terpilih, state=tk.DISABLED, style="Danger.TButton")
        self.hapus_pengeluaran_button.pack(side=tk.LEFT, padx=5)

        cols_pengeluaran = ("ID", "Tanggal", "Jumlah", "Keterangan")
        self.tree_pengeluaran_internal = ttk.Treeview(self.tab_pengeluaran_internal, columns=cols_pengeluaran, show='headings', selectmode="browse", style="Treeview")
        col_widths_pengeluaran = {"ID": 40, "Tanggal": 120, "Jumlah": 150, "Keterangan": 400}
        for col in cols_pengeluaran:
            self.tree_pengeluaran_internal.heading(col, text=col)
            self.tree_pengeluaran_internal.column(col, width=col_widths_pengeluaran[col], anchor=tk.E if col == "Jumlah" else tk.W)

        scrollbar_y_pengeluaran = ttk.Scrollbar(self.tab_pengeluaran_internal, orient=tk.VERTICAL, command=self.tree_pengeluaran_internal.yview)
        scrollbar_x_pengeluaran = ttk.Scrollbar(self.tab_pengeluaran_internal, orient=tk.HORIZONTAL, command=self.tree_pengeluaran_internal.xview)
        self.tree_pengeluaran_internal.configure(yscrollcommand=scrollbar_y_pengeluaran.set, xscrollcommand=scrollbar_x_pengeluaran.set)
        scrollbar_y_pengeluaran.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x_pengeluaran.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree_pengeluaran_internal.pack(expand=True, fill=tk.BOTH)
        
        self.tree_pengeluaran_internal.tag_configure('pengeluaran', foreground='#BF360C') 

        self.tree_pengeluaran_internal.bind("<<TreeviewSelect>>", self.on_pengeluaran_internal_select)
        self.tree_pengeluaran_internal.bind("<Double-1>", lambda e: self.open_edit_pengeluaran_window())

    def load_riwayat_pengeluaran_internal_data(self):
        for item in self.tree_pengeluaran_internal.get_children():
            self.tree_pengeluaran_internal.delete(item)

        start_date = self.start_date_filter.get()
        end_date = self.end_date_filter.get()
        pengeluaran_list = db.get_all_pengeluaran_internal(self.conn, start_date, end_date)

        if pengeluaran_list:
            for peng in pengeluaran_list:
                peng_id, tanggal_input, jumlah, keterangan, saldo_entry_id = peng
                jumlah_f = lg.format_rupiah(jumlah)
                values = (peng_id, tanggal_input, jumlah_f, keterangan) 
                self.tree_pengeluaran_internal.insert("", tk.END, values=values, tags=('pengeluaran',))
        
        self.on_pengeluaran_internal_select()

    def on_pengeluaran_internal_select(self, event=None):
        selected_item = self.tree_pengeluaran_internal.focus()
        if selected_item:
            self.edit_pengeluaran_button.config(state=tk.NORMAL)
            self.hapus_pengeluaran_button.config(state=tk.NORMAL)
        else:
            self.edit_pengeluaran_button.config(state=tk.DISABLED)
            self.hapus_pengeluaran_button.config(state=tk.DISABLED)