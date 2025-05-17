# File: logic.py
from datetime import datetime, timedelta
import calendar # Untuk mendapatkan hari terakhir dalam bulan

# Fungsi untuk memformat angka dengan pemisah ribuan
def format_rupiah(angka):
    """Memformat angka menjadi string dengan pemisah ribuan."""
    if angka is None:
        return "Rp 0"
    try:
        return f"Rp {int(angka):,}".replace(',', '.')
    except (ValueError, TypeError):
        return "Rp 0"


# Fungsi untuk menghitung laba
def hitung_laba(harga_jual, harga_modal):
    """Menghitung laba dari harga jual dan harga modal."""
    try:
        return int(harga_jual) - int(harga_modal)
    except ValueError:
        return 0

# Fungsi untuk mendapatkan tanggal dan waktu saat ini dalam format string
def get_current_datetime_str():
    """Mengembalikan tanggal dan waktu saat ini sebagai string."""
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S"), now.strftime("%d %B %Y"), now.strftime("%H:%M:%S")

# --- Fungsi BARU untuk filter tanggal ---
def get_month_range(date_obj=None):
    """
    Mengembalikan tanggal pertama dan terakhir dari bulan untuk tanggal yang diberikan.
    Jika tidak ada tanggal yang diberikan, gunakan bulan saat ini.
    """
    if date_obj is None:
        date_obj = datetime.now()
    
    first_day = date_obj.replace(day=1)
    # Mendapatkan hari terakhir dalam bulan
    # calendar.monthrange(year, month) mengembalikan tuple (weekday of first day, num_days_in_month)
    _, num_days = calendar.monthrange(first_day.year, first_day.month)
    last_day = first_day.replace(day=num_days)
    
    return first_day.strftime("%Y-%m-%d"), last_day.strftime("%Y-%m-%d")

# (Fungsi format_date_for_db tidak lagi digunakan secara luas, bisa dipertahankan atau dihapus)
def format_date_for_db(date_str):
    """Mengonversi format DD/MM/YY atau format lain dari DateEntry ke YYYY-MM-DD."""
    try:
        dt_object = datetime.strptime(date_str, '%d/%m/%y')
    except ValueError:
        try:
            dt_object = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            try:
                dt_object = datetime.strptime(date_str.split(" ")[0], '%Y-%m-%d')
            except:
                return datetime.now().strftime("%Y-%m-%d")
    return dt_object.strftime("%Y-%m-%d")