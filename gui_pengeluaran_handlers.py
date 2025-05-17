# File: gui_pengeluaran_handlers.py

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import database as db
import logic as lg
from datetime import datetime
from gui_constants import *

class PengeluaranHandlers:
    def open_input_pengeluaran_window(self):
        self.input_pengeluaran_window = tk.Toplevel(self.root)
        self.input_pengeluaran_window.title("Input Pengeluaran Toko")
        self.input_pengeluaran_window.geometry("450x300")
        self.input_pengeluaran_window.transient(self.root)
        self.input_pengeluaran_window.grab_set()
        self.input_pengeluaran_window.configure(bg=SECONDARY_COLOR)

        frame = ttk.Frame(self.input_pengeluaran_window, padding="20", style="Dialog.TFrame")
        frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(frame, text="Tanggal Pengeluaran:", font=FONT_NORMAL, style="Dialog.TLabel").grid(row=0, column=0, padx=5, pady=8, sticky=tk.W)
        self.pengeluaran_tanggal_entry = DateEntry(frame, width=18, date_pattern='yyyy-mm-dd',
                                                background=PRIMARY_COLOR, foreground=TEXT_COLOR_ON_PRIMARY,
                                                headersbackground=PRIMARY_COLOR, headersforeground=TEXT_COLOR_ON_PRIMARY,
                                                selectbackground=ACCENT_COLOR, selectforeground=TEXT_COLOR_DARK)
        self.pengeluaran_tanggal_entry.grid(row=0, column=1, padx=5, pady=8, sticky=tk.EW)

        ttk.Label(frame, text="Jumlah (Rp):", font=FONT_NORMAL, style="Dialog.TLabel").grid(row=1, column=0, padx=5, pady=8, sticky=tk.W)
        self.pengeluaran_jumlah_entry = ttk.Entry(frame, width=20, font=FONT_NORMAL)
        self.pengeluaran_jumlah_entry.grid(row=1, column=1, padx=5, pady=8, sticky=tk.EW)
        vcmd_positive_num_pengeluaran = (frame.register(self.validate_positive_number_input), '%P')
        self.pengeluaran_jumlah_entry.config(validate='key', validatecommand=vcmd_positive_num_pengeluaran)


        ttk.Label(frame, text="Keterangan:", font=FONT_NORMAL, style="Dialog.TLabel").grid(row=2, column=0, padx=5, pady=8, sticky=tk.W)
        self.pengeluaran_keterangan_entry = ttk.Entry(frame, width=20, font=FONT_NORMAL)
        self.pengeluaran_keterangan_entry.grid(row=2, column=1, padx=5, pady=8, sticky=tk.EW)

        button_frame = ttk.Frame(frame, style="Dialog.TFrame")
        button_frame.grid(row=3, column=0, columnspan=2, pady=(20,0))

        save_button = ttk.Button(button_frame, text="Simpan Pengeluaran", command=self.save_pengeluaran_internal, style="Accent.TButton")
        save_button.pack(side=tk.LEFT, padx=10)
        cancel_button = ttk.Button(button_frame, text="Batal", command=self.input_pengeluaran_window.destroy)
        cancel_button.pack(side=tk.LEFT, padx=10)
        frame.columnconfigure(1, weight=1)

    def save_pengeluaran_internal(self):
        tanggal_pengeluaran_input = self.pengeluaran_tanggal_entry.get_date().strftime("%Y-%m-%d")
        jumlah_str = self.pengeluaran_jumlah_entry.get()
        keterangan = self.pengeluaran_keterangan_entry.get()

        if not jumlah_str or not keterangan:
            messagebox.showerror("Error Input", "Jumlah dan keterangan pengeluaran tidak boleh kosong.", parent=self.input_pengeluaran_window)
            return
        try:
            jumlah_pengeluaran = int(jumlah_str)
            if jumlah_pengeluaran <= 0:
                 messagebox.showerror("Error Input", "Jumlah pengeluaran harus angka positif lebih dari nol.", parent=self.input_pengeluaran_window)
                 return
        except ValueError:
            messagebox.showerror("Error Input", "Jumlah pengeluaran harus berupa angka.", parent=self.input_pengeluaran_window)
            return

        perubahan_saldo = -jumlah_pengeluaran 
        keterangan_saldo = f"Pengeluaran Toko: {keterangan} (-{lg.format_rupiah(jumlah_pengeluaran)})"
        
        saldo_entry_id = db.update_saldo(self.conn, perubahan_saldo, keterangan_saldo) 

        if saldo_entry_id is not None:
            pengeluaran_id = db.tambah_pengeluaran_internal(self.conn, tanggal_pengeluaran_input, jumlah_pengeluaran, keterangan, saldo_entry_id)

            if pengeluaran_id:
                messagebox.showinfo("Sukses", f"Pengeluaran toko ID {pengeluaran_id} berhasil disimpan.", parent=self.input_pengeluaran_window)
                self.apply_filter_and_refresh_dashboard()
                self.input_pengeluaran_window.destroy()
            else:
                if saldo_entry_id:
                     db.update_saldo(self.conn, -perubahan_saldo, f"Pembatalan Saldo (Gagal Input Pengeluaran ID Saldo Awal: {saldo_entry_id})")
                     messagebox.showerror("Error Database", "Gagal menyimpan data pengeluaran. Perubahan saldo kas telah dibatalkan.", parent=self.input_pengeluaran_window)
                else:
                     messagebox.showerror("Error Database", "Gagal menyimpan data pengeluaran (dan gagal update saldo awal).", parent=self.input_pengeluaran_window)
        else:
             messagebox.showerror("Error Database", "Gagal mengupdate saldo kas untuk pengeluaran.", parent=self.input_pengeluaran_window)

    def open_edit_pengeluaran_window(self):
        selected_item = self.tree_pengeluaran_internal.focus()
        if not selected_item:
            messagebox.showwarning("Peringatan", "Pilih data pengeluaran yang akan diedit.", parent=self.root)
            return

        item_details = self.tree_pengeluaran_internal.item(selected_item)
        self.current_edit_pengeluaran_id = item_details['values'][0]
        
        self.original_pengeluaran_data = db.get_pengeluaran_internal_by_id(self.conn, self.current_edit_pengeluaran_id)
        if not self.original_pengeluaran_data:
            messagebox.showerror("Error", "Data pengeluaran tidak ditemukan.", parent=self.root)
            return
        
        _, tgl_db_input, jumlah_db_asli, ket_db_asli, self.original_saldo_entry_id_pengeluaran = self.original_pengeluaran_data

        self.edit_pengeluaran_window = tk.Toplevel(self.root)
        self.edit_pengeluaran_window.title(f"Edit Pengeluaran Toko ID {self.current_edit_pengeluaran_id}")
        self.edit_pengeluaran_window.geometry("450x300") 
        self.edit_pengeluaran_window.transient(self.root)
        self.edit_pengeluaran_window.grab_set()
        self.edit_pengeluaran_window.configure(bg=SECONDARY_COLOR)
        
        frame = ttk.Frame(self.edit_pengeluaran_window, padding="20", style="Dialog.TFrame")
        frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(frame, text=f"ID Pengeluaran: {self.current_edit_pengeluaran_id}", font=FONT_BOLD, style="Dialog.TLabel").grid(row=0, column=0, columnspan=2, padx=5, pady=(5,10), sticky=tk.W)

        ttk.Label(frame, text="Tanggal Pengeluaran:", font=FONT_NORMAL, style="Dialog.TLabel").grid(row=1, column=0, padx=5, pady=8, sticky=tk.W)
        self.edit_pengeluaran_tanggal_entry = DateEntry(frame, width=18, date_pattern='yyyy-mm-dd', font=FONT_NORMAL,
                                             background=PRIMARY_COLOR, foreground=TEXT_COLOR_ON_PRIMARY,
                                             headersbackground=PRIMARY_COLOR, headersforeground=TEXT_COLOR_ON_PRIMARY,
                                             selectbackground=ACCENT_COLOR, selectforeground=TEXT_COLOR_DARK)
        try:
             self.edit_pengeluaran_tanggal_entry.set_date(datetime.strptime(tgl_db_input, "%Y-%m-%d"))
        except ValueError: 
             self.edit_pengeluaran_tanggal_entry.set_date(datetime.now()) 
        self.edit_pengeluaran_tanggal_entry.grid(row=1, column=1, padx=5, pady=8, sticky=tk.EW)

        ttk.Label(frame, text="Jumlah (Rp):", font=FONT_NORMAL, style="Dialog.TLabel").grid(row=2, column=0, padx=5, pady=8, sticky=tk.W)
        self.edit_pengeluaran_jumlah_entry = ttk.Entry(frame, width=20, font=FONT_NORMAL)
        self.edit_pengeluaran_jumlah_entry.insert(0, str(jumlah_db_asli))
        vcmd_positive_num_edit_pengeluaran = (frame.register(self.validate_positive_number_input), '%P')
        self.edit_pengeluaran_jumlah_entry.config(validate='key', validatecommand=vcmd_positive_num_edit_pengeluaran)
        self.edit_pengeluaran_jumlah_entry.grid(row=2, column=1, padx=5, pady=8, sticky=tk.EW)

        ttk.Label(frame, text="Keterangan:", font=FONT_NORMAL, style="Dialog.TLabel").grid(row=3, column=0, padx=5, pady=8, sticky=tk.W)
        self.edit_pengeluaran_keterangan_entry = ttk.Entry(frame, width=20, font=FONT_NORMAL)
        self.edit_pengeluaran_keterangan_entry.insert(0, ket_db_asli)
        self.edit_pengeluaran_keterangan_entry.grid(row=3, column=1, padx=5, pady=8, sticky=tk.EW)
        
        info_label = ttk.Label(frame, text="Mengedit akan menyesuaikan saldo kas terkait.", style="Red.TLabel Dialog.TLabel", font=FONT_INFO_MERAH)
        info_label.grid(row=4, column=0, columnspan=2, pady=(10,5))

        button_frame = ttk.Frame(frame, style="Dialog.TFrame")
        button_frame.grid(row=5, column=0, columnspan=2, pady=(15,0))
        save_button = ttk.Button(button_frame, text="Simpan Perubahan", command=self.save_edited_pengeluaran, style="Accent.TButton")
        save_button.pack(side=tk.LEFT, padx=10)
        cancel_button = ttk.Button(button_frame, text="Batal", command=self.edit_pengeluaran_window.destroy)
        cancel_button.pack(side=tk.LEFT, padx=10)
        frame.columnconfigure(1, weight=1)

    def save_edited_pengeluaran(self):
        pengeluaran_id_to_edit = self.current_edit_pengeluaran_id
        jumlah_lama_asli = self.original_pengeluaran_data[2]
        keterangan_lama_asli = self.original_pengeluaran_data[3]
        saldo_entry_id_lama = self.original_saldo_entry_id_pengeluaran

        tanggal_baru_input = self.edit_pengeluaran_tanggal_entry.get_date().strftime("%Y-%m-%d")
        jumlah_str_baru = self.edit_pengeluaran_jumlah_entry.get()
        keterangan_baru = self.edit_pengeluaran_keterangan_entry.get()

        if not jumlah_str_baru or not keterangan_baru:
            messagebox.showerror("Error Input", "Jumlah dan keterangan tidak boleh kosong.", parent=self.edit_pengeluaran_window)
            return
        try:
            jumlah_baru_asli = int(jumlah_str_baru)
            if jumlah_baru_asli <= 0:
                messagebox.showerror("Error Input", "Jumlah pengeluaran harus positif.", parent=self.edit_pengeluaran_window)
                return
        except ValueError:
            messagebox.showerror("Error Input", "Jumlah pengeluaran harus angka.", parent=self.edit_pengeluaran_window)
            return

        perubahan_saldo_netto_untuk_kas = jumlah_lama_asli - jumlah_baru_asli
        
        keterangan_saldo_edit = (f"Edit Pengeluaran Toko ID {pengeluaran_id_to_edit}: '{keterangan_lama_asli}' ({lg.format_rupiah(jumlah_lama_asli)}) -> "
                                 f"'{keterangan_baru}' ({lg.format_rupiah(jumlah_baru_asli)}). "
                                 f"Penyesuaian Saldo: {lg.format_rupiah(perubahan_saldo_netto_untuk_kas)}")

        if db.update_pengeluaran_internal(self.conn, pengeluaran_id_to_edit, tanggal_baru_input, jumlah_baru_asli, keterangan_baru):
            if perubahan_saldo_netto_untuk_kas != 0:
                 db.update_saldo(self.conn, perubahan_saldo_netto_untuk_kas, keterangan_saldo_edit)
            
            messagebox.showinfo("Sukses", f"Pengeluaran ID {pengeluaran_id_to_edit} berhasil diperbarui.", parent=self.edit_pengeluaran_window)
            self.apply_filter_and_refresh_dashboard()
            self.edit_pengeluaran_window.destroy()
        else:
            messagebox.showerror("Error Database", f"Gagal memperbarui pengeluaran ID {pengeluaran_id_to_edit}.", parent=self.edit_pengeluaran_window)

    def hapus_pengeluaran_terpilih(self):
        selected_item = self.tree_pengeluaran_internal.focus()
        if not selected_item:
            messagebox.showwarning("Peringatan", "Pilih data pengeluaran yang akan dihapus.", parent=self.root)
            return

        item_details = self.tree_pengeluaran_internal.item(selected_item)
        pengeluaran_id_to_delete = int(item_details['values'][0]) # Pastikan integer
        
        original_pengeluaran_data = db.get_pengeluaran_internal_by_id(self.conn, pengeluaran_id_to_delete)
        if not original_pengeluaran_data:
            messagebox.showerror("Error", f"Data pengeluaran ID {pengeluaran_id_to_delete} tidak ditemukan untuk dihapus.", parent=self.root)
            return
        
        _, _, jumlah_dihapus_asli, keterangan_dihapus, saldo_entry_id_terkait = original_pengeluaran_data

        if messagebox.askyesno("Konfirmasi Hapus", f"Yakin hapus pengeluaran '{keterangan_dihapus}' (ID: {pengeluaran_id_to_delete}) sebesar {lg.format_rupiah(jumlah_dihapus_asli)}?\nSaldo kas akan disesuaikan (dikembalikan).", parent=self.root):
            perubahan_saldo_akibat_hapus = jumlah_dihapus_asli 
            keterangan_saldo_hapus = f"Pembatalan Pengeluaran Toko: {keterangan_dihapus} (ID {pengeluaran_id_to_delete}). Saldo dikembalikan +{lg.format_rupiah(jumlah_dihapus_asli)}"

            if db.hapus_pengeluaran_internal(self.conn, pengeluaran_id_to_delete):
                db.update_saldo(self.conn, perubahan_saldo_akibat_hapus, keterangan_saldo_hapus)
                
                messagebox.showinfo("Sukses", f"Pengeluaran ID {pengeluaran_id_to_delete} dihapus dan saldo disesuaikan.", parent=self.root)
                self.apply_filter_and_refresh_dashboard()
            else:
                messagebox.showerror("Error Database", f"Gagal menghapus pengeluaran ID {pengeluaran_id_to_delete}. Saldo tidak diubah.", parent=self.root)