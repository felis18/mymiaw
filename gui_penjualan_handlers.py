# File: gui_penjualan_handlers.py

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import database as db
import logic as lg
from datetime import datetime
# Asumsi gui_constants.py dan gui_validators.py ada di direktori yang sama
from gui_constants import *
# Tidak perlu import gui_validators karena metode validasi akan ada di SalesApp utama
# atau diwariskan ke SalesApp. Jika Validators adalah kelas terpisah, SalesApp harus mewarisinya.

class PenjualanHandlers:
    def open_input_penjualan_window(self):
        self.input_penjualan_window = tk.Toplevel(self.root)
        self.input_penjualan_window.title("Input Transaksi Penjualan")
        self.input_penjualan_window.geometry("500x400")
        self.input_penjualan_window.transient(self.root)
        self.input_penjualan_window.grab_set()
        self.input_penjualan_window.configure(bg=SECONDARY_COLOR)
        frame = ttk.Frame(self.input_penjualan_window, padding="20", style="Dialog.TFrame")
        frame.pack(expand=True, fill=tk.BOTH)
        ttk.Label(frame, text="Tanggal:", font=FONT_NORMAL, style="Dialog.TLabel").grid(row=0, column=0, padx=5, pady=8, sticky=tk.W)
        self.penjualan_tanggal_entry = DateEntry(frame, width=23, date_pattern='yyyy-mm-dd', font=FONT_NORMAL,
                                                 background=PRIMARY_COLOR, foreground=TEXT_COLOR_ON_PRIMARY,
                                                 headersbackground=PRIMARY_COLOR, headersforeground=TEXT_COLOR_ON_PRIMARY,
                                                 selectbackground=ACCENT_COLOR, selectforeground=TEXT_COLOR_DARK)
        self.penjualan_tanggal_entry.grid(row=0, column=1, padx=5, pady=8, sticky=tk.EW)
        ttk.Label(frame, text="Nama Item:", font=FONT_NORMAL, style="Dialog.TLabel").grid(row=1, column=0, padx=5, pady=8, sticky=tk.W)
        self.penjualan_item_entry = ttk.Entry(frame, width=30, font=FONT_NORMAL)
        self.penjualan_item_entry.grid(row=1, column=1, padx=5, pady=8, sticky=tk.EW)
        
        vcmd_positive_num = (frame.register(self.validate_positive_number_input), '%P')
        
        ttk.Label(frame, text="Harga Modal (Rp):", font=FONT_NORMAL, style="Dialog.TLabel").grid(row=2, column=0, padx=5, pady=8, sticky=tk.W)
        self.penjualan_modal_entry = ttk.Entry(frame, width=30, validate='key', validatecommand=vcmd_positive_num, font=FONT_NORMAL)
        self.penjualan_modal_entry.grid(row=2, column=1, padx=5, pady=8, sticky=tk.EW)
        self.penjualan_modal_entry.bind("<KeyRelease>", self.auto_calculate_laba_input)
        
        ttk.Label(frame, text="Harga Jual (Rp):", font=FONT_NORMAL, style="Dialog.TLabel").grid(row=3, column=0, padx=5, pady=8, sticky=tk.W)
        self.penjualan_jual_entry = ttk.Entry(frame, width=30, validate='key', validatecommand=vcmd_positive_num, font=FONT_NORMAL)
        self.penjualan_jual_entry.grid(row=3, column=1, padx=5, pady=8, sticky=tk.EW)
        self.penjualan_jual_entry.bind("<KeyRelease>", self.auto_calculate_laba_input)
        
        ttk.Label(frame, text="Laba (Rp):", font=FONT_NORMAL, style="Dialog.TLabel").grid(row=4, column=0, padx=5, pady=8, sticky=tk.W)
        self.penjualan_laba_label_input = ttk.Label(frame, text="Rp 0", width=30, relief="sunken", font=FONT_NORMAL, anchor=tk.E, padding=(0,0,5,0), style="Dialog.TLabel")
        self.penjualan_laba_label_input.grid(row=4, column=1, padx=5, pady=8, sticky=tk.EW)
        
        ttk.Label(frame, text="Jenis Pembayaran:", font=FONT_NORMAL, style="Dialog.TLabel").grid(row=5, column=0, padx=5, pady=8, sticky=tk.W)
        self.penjualan_jenis_pembayaran_var = tk.StringVar(value="Tunai")
        jenis_pembayaran_options = ["Tunai", "Kredit"]
        self.penjualan_jenis_pembayaran_combo = ttk.Combobox(frame, textvariable=self.penjualan_jenis_pembayaran_var, values=jenis_pembayaran_options, state="readonly", width=28, font=FONT_NORMAL)
        self.penjualan_jenis_pembayaran_combo.grid(row=5, column=1, padx=5, pady=8, sticky=tk.EW)
        
        button_frame = ttk.Frame(frame, style="Dialog.TFrame")
        button_frame.grid(row=6, column=0, columnspan=2, pady=(20,0))
        save_button = ttk.Button(button_frame, text="Simpan Transaksi", command=self.save_penjualan, style="Accent.TButton")
        save_button.pack(side=tk.LEFT, padx=10)
        cancel_button = ttk.Button(button_frame, text="Batal", command=self.input_penjualan_window.destroy)
        cancel_button.pack(side=tk.LEFT, padx=10)
        frame.columnconfigure(1, weight=1)

    def auto_calculate_laba_input(self, event=None):
        try:
            modal = int(self.penjualan_modal_entry.get() or 0)
            jual = int(self.penjualan_jual_entry.get() or 0)
            laba = lg.hitung_laba(jual, modal)
            self.penjualan_laba_label_input.config(text=lg.format_rupiah(laba))
        except ValueError:
            self.penjualan_laba_label_input.config(text="Input Angka Salah")

    def save_penjualan(self):
        tanggal = self.penjualan_tanggal_entry.get_date().strftime("%Y-%m-%d")
        nama_item = self.penjualan_item_entry.get()
        harga_modal_str = self.penjualan_modal_entry.get()
        harga_jual_str = self.penjualan_jual_entry.get()
        jenis_pembayaran = self.penjualan_jenis_pembayaran_var.get()

        if not all([nama_item, harga_modal_str, harga_jual_str]):
            messagebox.showerror("Error Input", "Semua field harus diisi.", parent=self.input_penjualan_window)
            return

        try:
            harga_modal = int(harga_modal_str)
            harga_jual = int(harga_jual_str)
            if harga_modal < 0 or harga_jual < 0: 
                 messagebox.showerror("Error Input", "Harga modal dan harga jual tidak boleh negatif.", parent=self.input_penjualan_window)
                 return
        except ValueError:
            messagebox.showerror("Error Input", "Harga modal dan harga jual harus berupa angka.", parent=self.input_penjualan_window)
            return

        laba = lg.hitung_laba(harga_jual, harga_modal)
        status_kredit = "Belum Lunas" if jenis_pembayaran == "Kredit" else None
        tanggal_db_penjualan = tanggal 

        penjualan_id = db.tambah_penjualan(self.conn, tanggal_db_penjualan, nama_item, harga_modal, harga_jual, laba, jenis_pembayaran, status_kredit)

        if penjualan_id:
            perubahan_saldo = 0
            keterangan_saldo = ""

            if jenis_pembayaran == "Tunai":
                perubahan_saldo = harga_jual - harga_modal 
                keterangan_saldo = (f"Penjualan Tunai: {nama_item} (ID {penjualan_id}). "
                                    f"Modal: {lg.format_rupiah(harga_modal)}, Jual: {lg.format_rupiah(harga_jual)}, "
                                    f"Perubahan Saldo (Laba/Rugi): {lg.format_rupiah(perubahan_saldo)}")
            elif jenis_pembayaran == "Kredit":
                perubahan_saldo = -harga_modal 
                keterangan_saldo = (f"Penjualan Kredit: {nama_item} (ID {penjualan_id}). "
                                    f"Modal Keluar: {lg.format_rupiah(harga_modal)}")

            if perubahan_saldo != 0 or jenis_pembayaran == "Tunai":
                 db.update_saldo(self.conn, perubahan_saldo, keterangan_saldo) 

            messagebox.showinfo("Sukses", "Transaksi penjualan berhasil disimpan dan saldo diperbarui.", parent=self.input_penjualan_window)
            self.apply_filter_and_refresh_dashboard()
            self.input_penjualan_window.destroy()
        else:
            messagebox.showerror("Error Database", "Gagal menyimpan transaksi penjualan.", parent=self.input_penjualan_window)

    def open_edit_penjualan_window(self): 
        active_tree = None
        selected_item = None

        focused_widget = self.root.focus_get()
        if focused_widget == self.tree_global and self.tree_global.focus():
            selected_item = self.tree_global.focus()
            active_tree = self.tree_global
        elif focused_widget == self.tree_kredit_aktif and self.tree_kredit_aktif.focus():
            selected_item = self.tree_kredit_aktif.focus()
            active_tree = self.tree_kredit_aktif
        
        if not selected_item:
            sel_global = self.tree_global.selection()
            if sel_global:
                selected_item = sel_global[0]
                active_tree = self.tree_global
            else:
                sel_kredit = self.tree_kredit_aktif.selection()
                if sel_kredit:
                    selected_item = sel_kredit[0]
                    active_tree = self.tree_kredit_aktif

        if not selected_item or not active_tree:
            messagebox.showwarning("Peringatan", "Pilih transaksi yang akan diedit.", parent=self.root)
            return

        item_details = active_tree.item(selected_item)
        self.current_edit_id = item_details['values'][0]
        self.original_penjualan_data_for_edit = db.get_penjualan_by_id(self.conn, self.current_edit_id)
        
        if not self.original_penjualan_data_for_edit:
            messagebox.showerror("Error", "Data transaksi tidak ditemukan.", parent=self.root)
            return
        
        _, tgl_db, nama_db_original, modal_db, jual_db, _, bayar_db, status_k_db, tgl_lunas_db = self.original_penjualan_data_for_edit

        self.edit_penjualan_window = tk.Toplevel(self.root)
        self.edit_penjualan_window.title(f"Edit Transaksi Penjualan ID {self.current_edit_id}")
        self.edit_penjualan_window.geometry("520x480") 
        self.edit_penjualan_window.transient(self.root)
        self.edit_penjualan_window.grab_set()
        self.edit_penjualan_window.configure(bg=SECONDARY_COLOR)
        frame = ttk.Frame(self.edit_penjualan_window, padding="20", style="Dialog.TFrame")
        frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(frame, text=f"ID Transaksi: {self.current_edit_id}", font=FONT_BOLD, style="Dialog.TLabel").grid(row=0, column=0, columnspan=2, padx=5, pady=(5,10), sticky=tk.W)
        
        ttk.Label(frame, text="Tanggal:", font=FONT_NORMAL, style="Dialog.TLabel").grid(row=1, column=0, padx=5, pady=8, sticky=tk.W)
        self.edit_penjualan_tanggal_entry = DateEntry(frame, width=23, date_pattern='yyyy-mm-dd', font=FONT_NORMAL,
                                             background=PRIMARY_COLOR, foreground=TEXT_COLOR_ON_PRIMARY,
                                             headersbackground=PRIMARY_COLOR, headersforeground=TEXT_COLOR_ON_PRIMARY,
                                             selectbackground=ACCENT_COLOR, selectforeground=TEXT_COLOR_DARK)
        try:
             self.edit_penjualan_tanggal_entry.set_date(datetime.strptime(tgl_db.split(" ")[0], "%Y-%m-%d"))
        except ValueError:
             self.edit_penjualan_tanggal_entry.set_date(datetime.now()) 
        self.edit_penjualan_tanggal_entry.grid(row=1, column=1, padx=5, pady=8, sticky=tk.EW)

        ttk.Label(frame, text="Nama Item:", font=FONT_NORMAL, style="Dialog.TLabel").grid(row=2, column=0, padx=5, pady=8, sticky=tk.W)
        self.edit_penjualan_item_entry = ttk.Entry(frame, width=30, font=FONT_NORMAL)
        self.edit_penjualan_item_entry.insert(0, nama_db_original)
        self.edit_penjualan_item_entry.grid(row=2, column=1, padx=5, pady=8, sticky=tk.EW)

        vcmd_positive_num_edit = (frame.register(self.validate_positive_number_input), '%P')
        
        ttk.Label(frame, text="Harga Modal (Rp):", font=FONT_NORMAL, style="Dialog.TLabel").grid(row=3, column=0, padx=5, pady=8, sticky=tk.W)
        self.edit_penjualan_modal_entry = ttk.Entry(frame, width=30, validate='key', validatecommand=vcmd_positive_num_edit, font=FONT_NORMAL)
        self.edit_penjualan_modal_entry.insert(0, str(modal_db))
        self.edit_penjualan_modal_entry.grid(row=3, column=1, padx=5, pady=8, sticky=tk.EW)
        self.edit_penjualan_modal_entry.bind("<KeyRelease>", self.auto_calculate_laba_edit)

        ttk.Label(frame, text="Harga Jual (Rp):", font=FONT_NORMAL, style="Dialog.TLabel").grid(row=4, column=0, padx=5, pady=8, sticky=tk.W)
        self.edit_penjualan_jual_entry = ttk.Entry(frame, width=30, validate='key', validatecommand=vcmd_positive_num_edit, font=FONT_NORMAL)
        self.edit_penjualan_jual_entry.insert(0, str(jual_db))
        self.edit_penjualan_jual_entry.grid(row=4, column=1, padx=5, pady=8, sticky=tk.EW)
        self.edit_penjualan_jual_entry.bind("<KeyRelease>", self.auto_calculate_laba_edit)

        ttk.Label(frame, text="Laba (Rp):", font=FONT_NORMAL, style="Dialog.TLabel").grid(row=5, column=0, padx=5, pady=8, sticky=tk.W)
        self.edit_penjualan_laba_label = ttk.Label(frame, text="Rp 0", width=30, relief="sunken", font=FONT_NORMAL, anchor=tk.E, padding=(0,0,5,0), style="Dialog.TLabel")
        self.edit_penjualan_laba_label.grid(row=5, column=1, padx=5, pady=8, sticky=tk.EW)
        self.auto_calculate_laba_edit() 

        ttk.Label(frame, text="Jenis Pembayaran:", font=FONT_NORMAL, style="Dialog.TLabel").grid(row=6, column=0, padx=5, pady=8, sticky=tk.W)
        self.edit_penjualan_jenis_pembayaran_var = tk.StringVar(value=bayar_db)
        self.edit_penjualan_jenis_pembayaran_combo = ttk.Combobox(frame, textvariable=self.edit_penjualan_jenis_pembayaran_var, values=["Tunai", "Kredit"], state="readonly", width=28, font=FONT_NORMAL)
        self.edit_penjualan_jenis_pembayaran_combo.grid(row=6, column=1, padx=5, pady=8, sticky=tk.EW)
        self.edit_penjualan_jenis_pembayaran_combo.bind("<<ComboboxSelected>>", self.toggle_status_kredit_edit)

        self.edit_status_kredit_label = ttk.Label(frame, text="Status Kredit:", font=FONT_NORMAL, style="Dialog.TLabel")
        self.edit_penjualan_status_kredit_var = tk.StringVar(value=(status_k_db if status_k_db else "Belum Lunas"))
        self.edit_penjualan_status_kredit_combo = ttk.Combobox(frame, textvariable=self.edit_penjualan_status_kredit_var, values=["Belum Lunas", "Lunas"], state="readonly", width=28, font=FONT_NORMAL)
        
        self.edit_tgl_pelunasan_label = ttk.Label(frame, text="Tgl Pelunasan:", font=FONT_NORMAL, style="Dialog.TLabel")
        self.edit_penjualan_tgl_pelunasan_entry = DateEntry(frame, width=23, date_pattern='yyyy-mm-dd', state='disabled', font=FONT_NORMAL,
                                             background=PRIMARY_COLOR, foreground=TEXT_COLOR_ON_PRIMARY,
                                             headersbackground=PRIMARY_COLOR, headersforeground=TEXT_COLOR_ON_PRIMARY,
                                             selectbackground=ACCENT_COLOR, selectforeground=TEXT_COLOR_DARK)
        if tgl_lunas_db:
             try:
                 self.edit_penjualan_tgl_pelunasan_entry.set_date(datetime.strptime(tgl_lunas_db, "%Y-%m-%d"))
             except ValueError:
                  pass 

        self.toggle_status_kredit_edit() 
        self.edit_penjualan_status_kredit_combo.bind("<<ComboboxSelected>>", self.toggle_tgl_pelunasan_edit)

        button_frame = ttk.Frame(frame, style="Dialog.TFrame")
        button_frame.grid(row=9, column=0, columnspan=2, pady=(20,0)) 

        save_button = ttk.Button(button_frame, text="Simpan Perubahan", command=self.save_edited_penjualan, style="Accent.TButton")
        save_button.pack(side=tk.LEFT, padx=10)
        cancel_button = ttk.Button(button_frame, text="Batal", command=self.edit_penjualan_window.destroy)
        cancel_button.pack(side=tk.LEFT, padx=10)

        frame.columnconfigure(1, weight=1)
        
    def toggle_status_kredit_edit(self, event=None):
        jenis_bayar = self.edit_penjualan_jenis_pembayaran_var.get()
        status_kredit_val = self.edit_penjualan_status_kredit_var.get() 
        if jenis_bayar == "Kredit":
            self.edit_status_kredit_label.grid(row=7, column=0, padx=5, pady=8, sticky=tk.W)
            self.edit_penjualan_status_kredit_combo.grid(row=7, column=1, padx=5, pady=8, sticky=tk.EW)
            self.edit_penjualan_status_kredit_combo.config(state="readonly")

            self.edit_tgl_pelunasan_label.grid(row=8, column=0, padx=5, pady=8, sticky=tk.W)
            self.edit_penjualan_tgl_pelunasan_entry.grid(row=8, column=1, padx=5, pady=8, sticky=tk.EW)

            if status_kredit_val == "Lunas":
                self.edit_penjualan_tgl_pelunasan_entry.config(state='normal')
                # Cek apakah DateEntry punya tanggal, jika tidak dan ada data original, pakai itu
                # atau set ke hari ini jika tidak ada data original tgl lunas.
                current_date_in_entry = None
                try:
                    current_date_in_entry = self.edit_penjualan_tgl_pelunasan_entry.get_date()
                except AttributeError: # Jika .get_date() tidak ada (misal karena entry dikosongkan manual)
                    pass
                
                if not current_date_in_entry:
                     original_tgl_lunas_db = self.original_penjualan_data_for_edit[8] if self.original_penjualan_data_for_edit else None
                     if original_tgl_lunas_db:
                         try:
                             self.edit_penjualan_tgl_pelunasan_entry.set_date(datetime.strptime(original_tgl_lunas_db, "%Y-%m-%d"))
                         except ValueError:
                             self.edit_penjualan_tgl_pelunasan_entry.set_date(datetime.now())
                     else:
                         self.edit_penjualan_tgl_pelunasan_entry.set_date(datetime.now())
            else: 
                self.edit_penjualan_tgl_pelunasan_entry.config(state='disabled')
                self.edit_penjualan_tgl_pelunasan_entry.set_date(None) 
        else: 
            self.edit_status_kredit_label.grid_remove()
            self.edit_penjualan_status_kredit_combo.grid_remove()
            self.edit_tgl_pelunasan_label.grid_remove()
            self.edit_penjualan_tgl_pelunasan_entry.grid_remove()
            self.edit_penjualan_status_kredit_var.set("Belum Lunas") # Default jika kembali ke Kredit nanti
            self.edit_penjualan_tgl_pelunasan_entry.config(state='disabled') 
            self.edit_penjualan_tgl_pelunasan_entry.set_date(None) 

    def toggle_tgl_pelunasan_edit(self, event=None):
        if self.edit_penjualan_status_kredit_var.get() == "Lunas":
            self.edit_penjualan_tgl_pelunasan_entry.config(state='normal')
            current_date_in_entry = None
            try:
                current_date_in_entry = self.edit_penjualan_tgl_pelunasan_entry.get_date()
            except AttributeError:
                pass
            if not current_date_in_entry:
                 self.edit_penjualan_tgl_pelunasan_entry.set_date(datetime.now())
        else: 
            self.edit_penjualan_tgl_pelunasan_entry.config(state='disabled')
            self.edit_penjualan_tgl_pelunasan_entry.set_date(None)


    def auto_calculate_laba_edit(self, event=None):
        try:
            modal = int(self.edit_penjualan_modal_entry.get() or 0)
            jual = int(self.edit_penjualan_jual_entry.get() or 0)
            laba = lg.hitung_laba(jual, modal)
            self.edit_penjualan_laba_label.config(text=lg.format_rupiah(laba))
        except ValueError:
            self.edit_penjualan_laba_label.config(text="Input Angka Salah")

    def save_edited_penjualan(self):
        id_penjualan = self.current_edit_id
        original_data = self.original_penjualan_data_for_edit
        _, _, nama_item_lama, modal_lama, jual_lama, laba_lama_db, bayar_lama, status_k_lama, tgl_lunas_lama = original_data

        tanggal_baru_str_input = self.edit_penjualan_tanggal_entry.get_date().strftime("%Y-%m-%d")
        nama_item_baru = self.edit_penjualan_item_entry.get()
        harga_modal_str_baru = self.edit_penjualan_modal_entry.get()
        harga_jual_str_baru = self.edit_penjualan_jual_entry.get()
        jenis_pembayaran_baru = self.edit_penjualan_jenis_pembayaran_var.get()

        status_kredit_baru = None
        tanggal_pelunasan_baru = None

        if jenis_pembayaran_baru == "Kredit":
            status_kredit_baru = self.edit_penjualan_status_kredit_var.get()
            if status_kredit_baru == "Lunas":
                try:
                    current_tgl_pelunasan_obj = self.edit_penjualan_tgl_pelunasan_entry.get_date()
                    if current_tgl_pelunasan_obj: 
                        tanggal_pelunasan_baru = current_tgl_pelunasan_obj.strftime("%Y-%m-%d")
                    else: 
                        messagebox.showerror("Error Input", "Tanggal pelunasan harus diisi jika status 'Lunas'.", parent=self.edit_penjualan_window)
                        return
                except Exception: 
                     messagebox.showerror("Error Input", "Format tanggal pelunasan tidak valid atau kosong.", parent=self.edit_penjualan_window)
                     return
        elif jenis_pembayaran_baru == "Tunai":
             status_kredit_baru = None
             tanggal_pelunasan_baru = None


        if not all([nama_item_baru, harga_modal_str_baru, harga_jual_str_baru]):
            messagebox.showerror("Error Input", "Semua field item, modal, jual harus diisi.", parent=self.edit_penjualan_window)
            return

        try:
            harga_modal_baru = int(harga_modal_str_baru)
            harga_jual_baru = int(harga_jual_str_baru)
            if harga_modal_baru < 0 or harga_jual_baru < 0:
                 messagebox.showerror("Error Input", "Harga modal dan harga jual tidak boleh negatif.", parent=self.edit_penjualan_window)
                 return
        except ValueError:
            messagebox.showerror("Error Input", "Harga modal dan jual harus angka.", parent=self.edit_penjualan_window)
            return

        laba_baru = lg.hitung_laba(harga_jual_baru, harga_modal_baru)

        perubahan_saldo_balik = 0
        keterangan_balik_list = []

        if bayar_lama == "Tunai":
            efek_saldo_lama_tunai = jual_lama - modal_lama
            perubahan_saldo_balik = -efek_saldo_lama_tunai
            keterangan_balik_list.append(f"Batal Efek Tunai Lama (Perubahan Saldo Awal: {lg.format_rupiah(efek_saldo_lama_tunai)})")
        elif bayar_lama == "Kredit":
            perubahan_saldo_balik = modal_lama 
            keterangan_balik_list.append(f"Batal Kredit Modal Keluar Lama (+{lg.format_rupiah(modal_lama)})")
            if status_k_lama == "Lunas":
                perubahan_saldo_balik -= jual_lama 
                keterangan_balik_list.append(f"Batal Pelunasan Lama (-{lg.format_rupiah(jual_lama)})")

        perubahan_saldo_baru_efek = 0
        keterangan_baru_list = []

        if jenis_pembayaran_baru == "Tunai":
            perubahan_saldo_baru_efek = harga_jual_baru - harga_modal_baru
            keterangan_baru_list.append(f"Terapkan Efek Tunai Baru (Perubahan Saldo: {lg.format_rupiah(perubahan_saldo_baru_efek)})")
        elif jenis_pembayaran_baru == "Kredit":
            perubahan_saldo_baru_efek = -harga_modal_baru
            keterangan_baru_list.append(f"Terapkan Kredit Modal Keluar Baru ({lg.format_rupiah(perubahan_saldo_baru_efek)})") 
            if status_kredit_baru == "Lunas":
                perubahan_saldo_baru_efek += harga_jual_baru 
                keterangan_baru_list.append(f"Terapkan Pelunasan Baru (+{lg.format_rupiah(harga_jual_baru)})")
        
        total_perubahan_saldo = perubahan_saldo_balik + perubahan_saldo_baru_efek
        
        keterangan_gabungan_list_str = []
        if keterangan_balik_list: keterangan_gabungan_list_str.append(f"Pembatalan Efek Lama: [{', '.join(keterangan_balik_list)}]")
        if keterangan_baru_list: keterangan_gabungan_list_str.append(f"Penerapan Efek Baru: [{', '.join(keterangan_baru_list)}]")
        
        keterangan_gabungan = (f"Edit Tx Penjualan ID {id_penjualan} '{nama_item_lama}' -> '{nama_item_baru}'. "
                               f"{'. '.join(keterangan_gabungan_list_str)}. "
                               f"Total Penyesuaian Saldo: {lg.format_rupiah(total_perubahan_saldo)}")


        if db.update_penjualan(self.conn, id_penjualan, tanggal_baru_str_input, nama_item_baru, harga_modal_baru, harga_jual_baru, laba_baru, jenis_pembayaran_baru, status_kredit_baru, tanggal_pelunasan_baru):
            if total_perubahan_saldo != 0 : 
                 db.update_saldo(self.conn, total_perubahan_saldo, keterangan_gabungan) 

            messagebox.showinfo("Sukses", f"Transaksi ID {id_penjualan} diperbarui. Saldo disesuaikan jika ada perubahan finansial.", parent=self.edit_penjualan_window)
            self.apply_filter_and_refresh_dashboard()
            self.edit_penjualan_window.destroy()
        else:
            messagebox.showerror("Error Database", f"Gagal update transaksi ID {id_penjualan}. Saldo tidak diubah.", parent=self.edit_penjualan_window)