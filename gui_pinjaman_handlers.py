# File: gui_pinjaman_handlers.py

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import database as db
import logic as lg
from datetime import datetime
from gui_constants import *

class PinjamanHandlers:
    def open_input_pinjaman_window(self):
        self.input_pinjaman_window = tk.Toplevel(self.root)
        self.input_pinjaman_window.title("Input Pinjaman Modal Baru")
        self.input_pinjaman_window.geometry("450x300")
        self.input_pinjaman_window.transient(self.root)
        self.input_pinjaman_window.grab_set()
        self.input_pinjaman_window.configure(bg=SECONDARY_COLOR)

        frame = ttk.Frame(self.input_pinjaman_window, padding="20", style="Dialog.TFrame")
        frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(frame, text="Tanggal Pinjam:", font=FONT_NORMAL, style="Dialog.TLabel").grid(row=0, column=0, padx=5, pady=8, sticky=tk.W)
        self.pinjaman_tanggal_entry = DateEntry(frame, width=18, date_pattern='yyyy-mm-dd',
                                                background=PRIMARY_COLOR, foreground=TEXT_COLOR_ON_PRIMARY,
                                                headersbackground=PRIMARY_COLOR, headersforeground=TEXT_COLOR_ON_PRIMARY,
                                                selectbackground=ACCENT_COLOR, selectforeground=TEXT_COLOR_DARK)
        self.pinjaman_tanggal_entry.grid(row=0, column=1, padx=5, pady=8, sticky=tk.EW)

        ttk.Label(frame, text="Jumlah Pinjam (Rp):", font=FONT_NORMAL, style="Dialog.TLabel").grid(row=1, column=0, padx=5, pady=8, sticky=tk.W)
        self.pinjaman_jumlah_entry = ttk.Entry(frame, width=20, font=FONT_NORMAL)
        self.pinjaman_jumlah_entry.grid(row=1, column=1, padx=5, pady=8, sticky=tk.EW)
        vcmd_positive_num_pinjam = (frame.register(self.validate_positive_number_input), '%P')
        self.pinjaman_jumlah_entry.config(validate='key', validatecommand=vcmd_positive_num_pinjam)

        ttk.Label(frame, text="Keterangan:", font=FONT_NORMAL, style="Dialog.TLabel").grid(row=2, column=0, padx=5, pady=8, sticky=tk.W)
        self.pinjaman_keterangan_entry = ttk.Entry(frame, width=20, font=FONT_NORMAL)
        self.pinjaman_keterangan_entry.grid(row=2, column=1, padx=5, pady=8, sticky=tk.EW)

        button_frame = ttk.Frame(frame, style="Dialog.TFrame")
        button_frame.grid(row=3, column=0, columnspan=2, pady=(20,0))

        save_button = ttk.Button(button_frame, text="Simpan Pinjaman", command=self.save_pinjaman, style="Accent.TButton")
        save_button.pack(side=tk.LEFT, padx=10)
        cancel_button = ttk.Button(button_frame, text="Batal", command=self.input_pinjaman_window.destroy)
        cancel_button.pack(side=tk.LEFT, padx=10)
        frame.columnconfigure(1, weight=1)

    def save_pinjaman(self):
        tanggal_pinjam_input = self.pinjaman_tanggal_entry.get_date().strftime("%Y-%m-%d")
        jumlah_str = self.pinjaman_jumlah_entry.get()
        keterangan = self.pinjaman_keterangan_entry.get()

        if not jumlah_str or not keterangan:
            messagebox.showerror("Error Input", "Jumlah dan keterangan pinjaman tidak boleh kosong.", parent=self.input_pinjaman_window)
            return
        try:
            jumlah_pinjam = int(jumlah_str)
            if jumlah_pinjam <= 0:
                 messagebox.showerror("Error Input", "Jumlah pinjaman harus angka positif lebih dari nol.", parent=self.input_pinjaman_window)
                 return
        except ValueError:
            messagebox.showerror("Error Input", "Jumlah pinjaman harus berupa angka.", parent=self.input_pinjaman_window)
            return

        keterangan_saldo_pinjam = f"Pinjaman Modal Diterima: {keterangan} ({lg.format_rupiah(jumlah_pinjam)})"
        saldo_entry_id = db.update_saldo(self.conn, jumlah_pinjam, keterangan_saldo_pinjam) 

        if saldo_entry_id is not None:
            pinjaman_id = db.tambah_pinjaman_modal(self.conn, tanggal_pinjam_input, jumlah_pinjam, keterangan, saldo_entry_id)
            if pinjaman_id:
                messagebox.showinfo("Sukses", f"Pinjaman modal ID {pinjaman_id} berhasil disimpan.", parent=self.input_pinjaman_window)
                self.apply_filter_and_refresh_dashboard()
                self.input_pinjaman_window.destroy()
            else: 
                if saldo_entry_id:
                     db.update_saldo(self.conn, -jumlah_pinjam, f"Pembatalan Saldo (Gagal Input Pinjaman ID Saldo Awal: {saldo_entry_id})")
                     messagebox.showerror("Error Database", "Gagal menyimpan data pinjaman. Penambahan saldo kas telah dibatalkan.", parent=self.input_pinjaman_window)
                else:
                     messagebox.showerror("Error Database", "Gagal menyimpan data pinjaman (dan gagal update saldo awal).", parent=self.input_pinjaman_window)
        else:
             messagebox.showerror("Error Database", "Gagal mengupdate saldo kas untuk pinjaman.", parent=self.input_pinjaman_window)

    def lunasi_pinjaman_terpilih(self):
        selected_item = self.tree_pinjaman.focus()
        if not selected_item:
            messagebox.showwarning("Peringatan", "Pilih pinjaman modal yang akan dilunasi.", parent=self.root)
            return

        item_details = self.tree_pinjaman.item(selected_item)
        pinjaman_id = item_details['values'][0] 
        
        pinjaman_data = db.get_pinjaman_modal_by_id(self.conn, pinjaman_id)
        if not pinjaman_data:
            messagebox.showerror("Error", f"Data pinjaman ID {pinjaman_id} tidak ditemukan.", parent=self.root)
            return

        _, _, jumlah_pinjam_asli, keterangan_pinjam, status_pinjam, _, _ = pinjaman_data

        if status_pinjam == 'Lunas':
             messagebox.showinfo("Info", f"Pinjaman ID {pinjaman_id} ('{keterangan_pinjam}') sudah lunas.", parent=self.root)
             self.load_riwayat_pinjaman_data() 
             return

        if messagebox.askyesno("Konfirmasi Pelunasan", f"Yakin melunasi pinjaman '{keterangan_pinjam}' (ID: {pinjaman_id}) sebesar {lg.format_rupiah(jumlah_pinjam_asli)}?", parent=self.root):
            tanggal_pelunasan_sekarang = datetime.now().strftime("%Y-%m-%d") 
            if db.lunasi_pinjaman_modal(self.conn, pinjaman_id, tanggal_pelunasan_sekarang):
                db.update_saldo(self.conn, -jumlah_pinjam_asli, f"Pelunasan Pinjaman Modal: {keterangan_pinjam} (ID {pinjaman_id}) (-{lg.format_rupiah(jumlah_pinjam_asli)})")
                messagebox.showinfo("Sukses", f"Pinjaman ID {pinjaman_id} ('{keterangan_pinjam}') berhasil dilunasi.", parent=self.root)
                self.apply_filter_and_refresh_dashboard()
            else:
                messagebox.showerror("Error Database", f"Gagal melunasi pinjaman ID {pinjaman_id}.", parent=self.root)

    def open_riwayat_pinjaman_window(self):
        # Placeholder: tampilkan pesan info, ganti dengan implementasi riil jika perlu
        from tkinter import messagebox
        messagebox.showinfo("Info", "Fitur Riwayat Pinjaman Modal belum diimplementasikan.", parent=self.root)