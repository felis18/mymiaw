# File: gui_export_handlers.py

import tkinter as tk
from tkinter import messagebox, filedialog
import pandas as pd
from datetime import datetime
import database as db # Perlu akses ke fungsi DB untuk ambil data
import logic as lg # Untuk format rupiah jika diperlukan (meski untuk ekspor angka mentah lebih baik)

class ExportHandlers:
    def export_pengeluaran_to_excel(self):
        start_date = self.start_date_filter.get()
        end_date = self.end_date_filter.get()
        pengeluaran_list = db.get_all_pengeluaran_internal(self.conn, start_date, end_date)

        if not pengeluaran_list:
            messagebox.showinfo("Info", "Tidak ada data pengeluaran toko untuk diekspor dalam rentang tanggal ini.", parent=self.root)
            return

        cols = ["ID Pengeluaran", "Tanggal Pengeluaran", "Jumlah (Rp)", "Keterangan"]
        data_for_export = []

        for peng in pengeluaran_list:
            peng_id, tanggal_input, jumlah, keterangan, _ = peng 
            data_for_export.append([peng_id, tanggal_input, jumlah, keterangan]) 

        df = pd.DataFrame(data_for_export, columns=cols)

        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", 
                                                     filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")], 
                                                     title="Simpan Laporan Pengeluaran Toko", 
                                                     initialfile=f"Laporan_Pengeluaran_Toko_{start_date}_sd_{end_date}.xlsx")
            if file_path:
                df.to_excel(file_path, index=False, engine='openpyxl')
                messagebox.showinfo("Sukses", f"Data pengeluaran toko berhasil diekspor ke:\n{file_path}", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error Ekspor", f"Gagal mengekspor data pengeluaran ke Excel: {e}", parent=self.root)

    def export_pinjaman_to_excel(self):
        pinjaman_list = db.get_all_pinjaman_modal(self.conn)
        if not pinjaman_list:
            messagebox.showinfo("Info", "Tidak ada data pinjaman modal untuk diekspor.", parent=self.root)
            return
        cols = ["ID Pinjaman", "Tanggal Pinjam", "Jumlah Pinjam (Rp)", "Keterangan", "Status", "Tanggal Lunas"]
        data_for_export = []
        for pinjam in pinjaman_list:
            pinjam_id, tgl_pinjam, jumlah, keterangan, status, tgl_lunas, _ = pinjam
            tgl_lunas_f = tgl_lunas if tgl_lunas else "-"
            data_for_export.append([pinjam_id, tgl_pinjam, jumlah, keterangan, status, tgl_lunas_f])
        df = pd.DataFrame(data_for_export, columns=cols)
        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")], title="Simpan Laporan Pinjaman Modal", initialfile=f"Laporan_Pinjaman_Modal_{datetime.now().strftime('%Y%m%d')}.xlsx")
            if file_path:
                df.to_excel(file_path, index=False, engine='openpyxl')
                messagebox.showinfo("Sukses", f"Data pinjaman berhasil diekspor ke:\n{file_path}", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error Ekspor", f"Gagal mengekspor data pinjaman ke Excel: {e}", parent=self.root)

    def export_to_excel(self):
        start_date = self.start_date_filter.get()
        end_date = self.end_date_filter.get()
        transactions = db.get_penjualan_by_date_range(self.conn, start_date, end_date)
        if not transactions:
            messagebox.showinfo("Info", "Tidak ada data penjualan untuk diekspor dalam rentang tanggal ini.", parent=self.root)
            return
        cols = ["ID Transaksi", "Tanggal", "Nama Item", "Harga Modal (Rp)", "Harga Jual (Rp)", "Laba (Rp)", "Jenis Pembayaran", "Status Kredit", "Tanggal Pelunasan"]
        data_for_export = []
        for tx in transactions:
            tgl_display = tx[1].split(" ")[0] if " " in tx[1] else tx[1]
            status_display = tx[7] if tx[7] else ("Tunai" if tx[6] == "Tunai" else "-")
            tgl_lunas_display = tx[8] if tx[8] else "-"
            # Ekspor angka mentah untuk Excel agar bisa diolah
            data_for_export.append([tx[0], tgl_display, tx[2], tx[3], tx[4], tx[5], tx[6], status_display, tgl_lunas_display])
        df = pd.DataFrame(data_for_export, columns=cols)
        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")], title="Simpan Laporan Penjualan", initialfile=f"Laporan_Penjualan_{start_date}_sd_{end_date}.xlsx")
            if file_path:
                df.to_excel(file_path, index=False, engine='openpyxl')
                messagebox.showinfo("Sukses", f"Data penjualan berhasil diekspor ke:\n{file_path}", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error Ekspor", f"Gagal mengekspor data penjualan ke Excel: {e}", parent=self.root)

    def export_to_csv(self):
        start_date = self.start_date_filter.get()
        end_date = self.end_date_filter.get()
        transactions = db.get_penjualan_by_date_range(self.conn, start_date, end_date)
        if not transactions:
            messagebox.showinfo("Info", "Tidak ada data penjualan untuk diekspor.", parent=self.root)
            return
        cols_csv = ["ID Transaksi", "Tanggal", "Nama Item", "Harga Modal", "Harga Jual", "Laba", "Jenis Pembayaran", "Status Kredit", "Tanggal Pelunasan"]
        data_for_export_csv = []
        for tx in transactions:
            tgl_display = tx[1].split(" ")[0] if " " in tx[1] else tx[1]
            status_display_csv = tx[7] if tx[7] else ("" if tx[6] == "Tunai" else "")
            tgl_lunas_display_csv = tx[8] if tx[8] else ""
            data_for_export_csv.append([tx[0], tgl_display, tx[2], tx[3], tx[4], tx[5], tx[6], status_display_csv, tgl_lunas_display_csv])
        df = pd.DataFrame(data_for_export_csv, columns=cols_csv)
        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")], title="Simpan Laporan Penjualan (CSV)", initialfile=f"Laporan_Penjualan_{start_date}_sd_{end_date}.csv")
            if file_path:
                df.to_csv(file_path, index=False, encoding='utf-8-sig', sep=';')
                messagebox.showinfo("Sukses", f"Data penjualan berhasil diekspor ke:\n{file_path}", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error Ekspor", f"Gagal mengekspor data penjualan ke CSV: {e}", parent=self.root)