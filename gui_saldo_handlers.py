# File: gui_saldo_handlers.py

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import database as db
import logic as lg
from datetime import datetime
# Asumsi gui_constants.py ada di direktori yang sama atau path yang benar
from gui_constants import *
# Jika Anda ingin lebih spesifik dan menghindari '*' (praktik yang baik):
# from gui_constants import SECONDARY_COLOR, PRIMARY_COLOR, TEXT_COLOR_ON_PRIMARY, ACCENT_COLOR, TEXT_COLOR_DARK, FONT_NORMAL, FONT_BOLD, FONT_INFO_MERAH

class SaldoHandlers:
    def open_input_saldo_window(self):
        self.input_saldo_window = tk.Toplevel(self.root)
        self.input_saldo_window.title("Input Saldo Kas")
        self.input_saldo_window.geometry("450x280")
        self.input_saldo_window.transient(self.root)
        self.input_saldo_window.grab_set()
        self.input_saldo_window.configure(bg=SECONDARY_COLOR)

        frame = ttk.Frame(self.input_saldo_window, padding="20", style="Dialog.TFrame")
        frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(frame, text="Tanggal:", font=FONT_NORMAL, style="Dialog.TLabel").grid(row=0, column=0, padx=5, pady=8, sticky=tk.W)
        self.saldo_tanggal_entry = DateEntry(frame, width=18, date_pattern='yyyy-mm-dd',
                                             background=PRIMARY_COLOR, foreground=TEXT_COLOR_ON_PRIMARY,
                                             headersbackground=PRIMARY_COLOR, headersforeground=TEXT_COLOR_ON_PRIMARY,
                                             selectbackground=ACCENT_COLOR, selectforeground=TEXT_COLOR_DARK)
        self.saldo_tanggal_entry.grid(row=0, column=1, padx=5, pady=8, sticky=tk.EW)

        ttk.Label(frame, text="Jumlah Perubahan (Rp):", font=FONT_NORMAL, style="Dialog.TLabel").grid(row=1, column=0, padx=5, pady=8, sticky=tk.W)
        self.saldo_jumlah_entry = ttk.Entry(frame, width=20, font=FONT_NORMAL)
        self.saldo_jumlah_entry.grid(row=1, column=1, padx=5, pady=8, sticky=tk.EW)
        # Pastikan self.validate_number_input ada di SalesApp (diwariskan dari Validators)
        vcmd_num_saldo = (frame.register(self.validate_number_input), '%P') 
        self.saldo_jumlah_entry.config(validate='key', validatecommand=vcmd_num_saldo)

        ttk.Label(frame, text="Keterangan:", font=FONT_NORMAL, style="Dialog.TLabel").grid(row=2, column=0, padx=5, pady=8, sticky=tk.W)
        self.saldo_keterangan_entry = ttk.Entry(frame, width=20, font=FONT_NORMAL)
        self.saldo_keterangan_entry.grid(row=2, column=1, padx=5, pady=8, sticky=tk.EW)

        button_frame = ttk.Frame(frame, style="Dialog.TFrame")
        button_frame.grid(row=3, column=0, columnspan=2, pady=(20,0))

        save_button = ttk.Button(button_frame, text="Catat Perubahan Saldo", command=self.save_saldo_entry, style="Accent.TButton")
        save_button.pack(side=tk.LEFT, padx=10)
        cancel_button = ttk.Button(button_frame, text="Batal", command=self.input_saldo_window.destroy)
        cancel_button.pack(side=tk.LEFT, padx=10)
        frame.columnconfigure(1, weight=1)

    def save_saldo_entry(self):
        tanggal_referensi = self.saldo_tanggal_entry.get_date().strftime("%Y-%m-%d")
        jumlah_str = self.saldo_jumlah_entry.get()
        keterangan_input = self.saldo_keterangan_entry.get()

        if not jumlah_str:
            messagebox.showerror("Error Input", "Jumlah perubahan tidak boleh kosong.", parent=self.input_saldo_window)
            return
        try:
            jumlah_perubahan = int(jumlah_str) 
        except ValueError:
            messagebox.showerror("Error Input", "Jumlah perubahan harus berupa angka.", parent=self.input_saldo_window)
            return

        if not keterangan_input:
             keterangan = f"Penyesuaian Saldo Manual pada {tanggal_referensi}"
        else:
             keterangan = f"{keterangan_input} (Ref. Tgl: {tanggal_referensi})"

        saldo_entry_id = db.update_saldo(self.conn, jumlah_perubahan, keterangan)

        if saldo_entry_id is not None:
            messagebox.showinfo("Sukses", "Entri perubahan saldo berhasil disimpan dan saldo diperbarui.", parent=self.input_saldo_window)
            self.update_saldo_display() 
            if hasattr(self, 'riwayat_saldo_window') and self.riwayat_saldo_window.winfo_exists():
                self.load_riwayat_saldo_data()
            self.input_saldo_window.destroy()
        else:
            messagebox.showerror("Error Database", "Gagal menyimpan entri perubahan saldo.", parent=self.input_saldo_window)

    def open_riwayat_saldo_window(self):
        self.riwayat_saldo_window = tk.Toplevel(self.root)
        self.riwayat_saldo_window.title("Riwayat dan Edit Saldo Kas")
        self.riwayat_saldo_window.geometry("750x550")
        self.riwayat_saldo_window.transient(self.root)
        self.riwayat_saldo_window.grab_set()
        self.riwayat_saldo_window.configure(bg=SECONDARY_COLOR)

        main_frame = ttk.Frame(self.riwayat_saldo_window, padding="15", style="Dialog.TFrame")
        main_frame.pack(expand=True, fill=tk.BOTH)

        action_frame = ttk.Frame(main_frame, style="Dialog.TFrame")
        action_frame.pack(fill=tk.X, pady=(0,10))
        self.edit_saldo_button = ttk.Button(action_frame, text="Edit Entri Saldo Terpilih", command=self.open_edit_saldo_entry_window, state=tk.DISABLED)
        self.edit_saldo_button.pack(side=tk.LEFT, padx=5)
        self.hapus_saldo_button = ttk.Button(action_frame, text="Hapus Entri Saldo Terpilih", command=self.hapus_saldo_entry_terpilih, state=tk.DISABLED, style="Danger.TButton")
        self.hapus_saldo_button.pack(side=tk.LEFT, padx=5)
        info_label = ttk.Label(action_frame, text="PERHATIAN: Edit/Hapus entri saldo historis dapat\nmerusak integritas data jika tidak hati-hati!", style="Red.TLabel Dialog.TLabel", font=FONT_INFO_MERAH)
        info_label.pack(side=tk.LEFT, padx=10, pady=(5,0))

        cols = ("ID", "Tanggal & Waktu", "Jumlah Saldo (Absolut)", "Keterangan")
        self.tree_saldo = ttk.Treeview(main_frame, columns=cols, show='headings', selectmode="browse", style="Treeview")
        col_widths = {"ID": 50, "Tanggal & Waktu": 180, "Jumlah Saldo (Absolut)": 150, "Keterangan": 300}
        for col in cols:
            self.tree_saldo.heading(col, text=col)
            self.tree_saldo.column(col, width=col_widths[col], anchor=tk.E if col == "Jumlah Saldo (Absolut)" else tk.W)
        
        scrollbar_y = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree_saldo.yview)
        scrollbar_x = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=self.tree_saldo.xview)
        self.tree_saldo.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree_saldo.pack(expand=True, fill=tk.BOTH)
        
        self.tree_saldo.bind("<<TreeviewSelect>>", self.on_saldo_select)
        self.load_riwayat_saldo_data()

    def load_riwayat_saldo_data(self):
        for item in self.tree_saldo.get_children():
            self.tree_saldo.delete(item)
        entries = db.get_all_saldo_entries(self.conn) 
        if entries:
            for entry in entries:
                saldo_id, tanggal, jumlah, keterangan = entry
                jumlah_f = lg.format_rupiah(jumlah)
                values = (saldo_id, tanggal, jumlah_f, keterangan if keterangan else "-") 
                self.tree_saldo.insert("", tk.END, values=values)
        self.on_saldo_select() 

    def on_saldo_select(self, event=None):
        selected_item = self.tree_saldo.focus()
        if selected_item:
            self.edit_saldo_button.config(state=tk.NORMAL)
            self.hapus_saldo_button.config(state=tk.NORMAL)
        else:
            self.edit_saldo_button.config(state=tk.DISABLED)
            self.hapus_saldo_button.config(state=tk.DISABLED)

    def open_edit_saldo_entry_window(self):
        selected_item = self.tree_saldo.focus()
        if not selected_item:
            messagebox.showwarning("Peringatan", "Pilih entri saldo yang akan diedit.", parent=self.riwayat_saldo_window)
            return
        
        item_values = self.tree_saldo.item(selected_item)['values']
        self.current_edit_saldo_id = item_values[0]
        
        saldo_data_db = db.get_saldo_entry_by_id(self.conn, self.current_edit_saldo_id)
        if not saldo_data_db:
            messagebox.showerror("Error", "Data saldo tidak ditemukan di database.", parent=self.riwayat_saldo_window)
            return
        
        _, tgl_db_full, jumlah_db_asli, ket_db_asli = saldo_data_db

        self.edit_saldo_entry_window = tk.Toplevel(self.riwayat_saldo_window)
        self.edit_saldo_entry_window.title(f"Edit Entri Saldo ID {self.current_edit_saldo_id}")
        self.edit_saldo_entry_window.geometry("450x320")
        self.edit_saldo_entry_window.transient(self.riwayat_saldo_window)
        self.edit_saldo_entry_window.grab_set()
        self.edit_saldo_entry_window.configure(bg=SECONDARY_COLOR)
        
        frame = ttk.Frame(self.edit_saldo_entry_window, padding="20", style="Dialog.TFrame")
        frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(frame, text=f"ID Saldo: {self.current_edit_saldo_id}", font=FONT_BOLD, style="Dialog.TLabel").grid(row=0, column=0, columnspan=2, padx=5, pady=(5,10), sticky=tk.W)

        ttk.Label(frame, text="Tanggal & Waktu Asli:", font=FONT_NORMAL, style="Dialog.TLabel").grid(row=1, column=0, padx=5, pady=8, sticky=tk.W)
        ttk.Label(frame, text=tgl_db_full, font=FONT_NORMAL, style="Dialog.TLabel").grid(row=1, column=1, padx=5, pady=8, sticky=tk.EW)

        ttk.Label(frame, text="Jumlah Saldo (Absolut):", font=FONT_NORMAL, style="Dialog.TLabel").grid(row=2, column=0, padx=5, pady=8, sticky=tk.W)
        self.edit_saldo_jumlah_entry = ttk.Entry(frame, width=20, font=FONT_NORMAL)
        self.edit_saldo_jumlah_entry.insert(0, str(jumlah_db_asli)) 
        vcmd_num_edit_saldo = (frame.register(self.validate_number_input), '%P') 
        self.edit_saldo_jumlah_entry.config(validate='key', validatecommand=vcmd_num_edit_saldo)
        self.edit_saldo_jumlah_entry.grid(row=2, column=1, padx=5, pady=8, sticky=tk.EW)

        ttk.Label(frame, text="Keterangan Baru:", font=FONT_NORMAL, style="Dialog.TLabel").grid(row=3, column=0, padx=5, pady=8, sticky=tk.W)
        self.edit_saldo_keterangan_entry = ttk.Entry(frame, width=20, font=FONT_NORMAL)
        self.edit_saldo_keterangan_entry.insert(0, ket_db_asli if ket_db_asli else "")
        self.edit_saldo_keterangan_entry.grid(row=3, column=1, padx=5, pady=8, sticky=tk.EW)

        warning_label = ttk.Label(frame, text="PERHATIAN: Ini mengubah saldo absolut entri ini.\nTidak ada kalkulasi ulang otomatis saldo berikutnya.\nTanggal & Waktu entri ini TIDAK diubah.", style="Red.TLabel Dialog.TLabel", font=FONT_INFO_MERAH)
        warning_label.grid(row=4, column=0, columnspan=2, pady=(10,5))

        button_frame = ttk.Frame(frame, style="Dialog.TFrame")
        button_frame.grid(row=5, column=0, columnspan=2, pady=(15,0))
        save_button = ttk.Button(button_frame, text="Simpan Perubahan", command=self.save_edited_saldo_entry, style="Accent.TButton")
        save_button.pack(side=tk.LEFT, padx=10)
        cancel_button = ttk.Button(button_frame, text="Batal", command=self.edit_saldo_entry_window.destroy)
        cancel_button.pack(side=tk.LEFT, padx=10)
        frame.columnconfigure(1, weight=1)

    def save_edited_saldo_entry(self):
        saldo_id_to_edit = self.current_edit_saldo_id
        
        original_saldo_data = db.get_saldo_entry_by_id(self.conn, saldo_id_to_edit)
        if not original_saldo_data:
            messagebox.showerror("Error", "Data saldo asli tidak ditemukan untuk disimpan.", parent=self.edit_saldo_entry_window)
            return
        tanggal_asli_db = original_saldo_data[1] 

        jumlah_str_baru = self.edit_saldo_jumlah_entry.get()
        keterangan_baru = self.edit_saldo_keterangan_entry.get()

        if not jumlah_str_baru: 
            messagebox.showerror("Error Input", "Jumlah saldo tidak boleh kosong.", parent=self.edit_saldo_entry_window)
            return
        try:
            jumlah_absolut_baru = int(jumlah_str_baru)
        except ValueError:
            messagebox.showerror("Error Input", "Jumlah saldo harus berupa angka.", parent=self.edit_saldo_entry_window)
            return

        if db.edit_saldo_entry(self.conn, saldo_id_to_edit, tanggal_asli_db, jumlah_absolut_baru, keterangan_baru):
            messagebox.showinfo("Sukses", f"Entri saldo ID {saldo_id_to_edit} berhasil diperbarui.", parent=self.edit_saldo_entry_window)
            self.load_riwayat_saldo_data() 
            self.update_saldo_display() 
            self.edit_saldo_entry_window.destroy()
            messagebox.showwarning("Perhatian", "Mengubah riwayat saldo historis dapat membuat saldo aktual tidak konsisten dengan penjumlahan total perubahan jika tidak hati-hati.", parent=self.root)
        else:
            messagebox.showerror("Error Database", f"Gagal memperbarui entri saldo ID {saldo_id_to_edit}.", parent=self.edit_saldo_entry_window)

    def hapus_saldo_entry_terpilih(self):
        selected_item = self.tree_saldo.focus()
        if not selected_item:
            messagebox.showwarning("Peringatan", "Pilih entri saldo yang akan dihapus.", parent=self.riwayat_saldo_window)
            return
        
        item_values = self.tree_saldo.item(selected_item)['values']
        saldo_id_to_delete = int(item_values[0]) # Pastikan integer
        jumlah_saldo_display = item_values[2] 

        pinjaman_ref = db.get_all_pinjaman_modal(self.conn) 
        for p in pinjaman_ref:
            if p[6] is not None and p[6] == saldo_id_to_delete: 
                messagebox.showerror("Error Hapus", f"Gagal menghapus entri saldo ID {saldo_id_to_delete}.\nMasih direferensikan oleh Pinjaman Modal ID {p[0]}.", parent=self.riwayat_saldo_window)
                return
        
        pengeluaran_ref = db.get_all_pengeluaran_internal(self.conn) 
        for peng in pengeluaran_ref:
             if peng[4] is not None and peng[4] == saldo_id_to_delete: 
                messagebox.showerror("Error Hapus", f"Gagal menghapus entri saldo ID {saldo_id_to_delete}.\nMasih direferensikan oleh Pengeluaran Toko ID {peng[0]}.", parent=self.riwayat_saldo_window)
                return

        if messagebox.askyesno("Konfirmasi Hapus", f"Yakin hapus entri saldo ID {saldo_id_to_delete} (Jumlah: {jumlah_saldo_display})?\nINI SANGAT BERISIKO dan dapat mempengaruhi perhitungan saldo berikutnya jika tidak hati-hati.\nPastikan entri ini tidak terkait transaksi lain (penjualan, pinjaman, pengeluaran).", parent=self.riwayat_saldo_window):
            if db.hapus_saldo_entry(self.conn, saldo_id_to_delete):
                messagebox.showinfo("Sukses", f"Entri saldo ID {saldo_id_to_delete} berhasil dihapus.", parent=self.riwayat_saldo_window)
                self.load_riwayat_saldo_data()
                self.update_saldo_display() 
                messagebox.showwarning("Perhatian", "Menghapus riwayat saldo historis dapat membuat saldo aktual tidak konsisten dengan penjumlahan total perubahan jika tidak hati-hati.", parent=self.root)
            else:
                messagebox.showerror("Error Database", f"Gagal menghapus entri saldo ID {saldo_id_to_delete}.", parent=self.riwayat_saldo_window)