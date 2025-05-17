# File: database.py
import sqlite3
from datetime import datetime

# Fungsi untuk membuat koneksi ke database
def create_connection():
    """Membuat koneksi ke database SQLite."""
    conn = None
    try:
        conn = sqlite3.connect('penjualan.db') # Membuat file database jika belum ada
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
    return conn

# Fungsi untuk membuat tabel-tabel yang dibutuhkan
def create_tables(conn):
    """Membuat tabel saldo, penjualan, pinjaman_modal, dan pengeluaran_internal jika belum ada."""
    try:
        cursor = conn.cursor()
        # Tabel Saldo
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS saldo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tanggal TEXT NOT NULL,
                jumlah INTEGER NOT NULL, -- Ini adalah saldo absolut setelah perubahan
                keterangan TEXT
            );
        """)
        # Tabel Penjualan
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS penjualan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tanggal TEXT NOT NULL,
                nama_item TEXT NOT NULL,
                harga_modal INTEGER NOT NULL,
                harga_jual INTEGER NOT NULL,
                laba INTEGER NOT NULL,
                jenis_pembayaran TEXT NOT NULL CHECK(jenis_pembayaran IN ('Tunai', 'Kredit')),
                status_kredit TEXT DEFAULT NULL, -- 'Belum Lunas', 'Lunas'
                tanggal_pelunasan TEXT DEFAULT NULL
            );
        """)
        # Tabel Pinjaman Modal
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pinjaman_modal (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tanggal_pinjam TEXT NOT NULL,
                jumlah_pinjam INTEGER NOT NULL,
                keterangan TEXT,
                status TEXT NOT NULL CHECK(status IN ('Aktif', 'Lunas')),
                tanggal_lunas TEXT DEFAULT NULL,
                saldo_entry_id INTEGER, -- FK ke tabel saldo
                FOREIGN KEY (saldo_entry_id) REFERENCES saldo(id)
            );
        """)
        # Tabel BARU: Pengeluaran Internal
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pengeluaran_internal (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tanggal TEXT NOT NULL,
                jumlah INTEGER NOT NULL,
                keterangan TEXT NOT NULL,
                saldo_entry_id INTEGER, -- FK ke tabel saldo (saat pengeluaran mengurangi saldo)
                FOREIGN KEY (saldo_entry_id) REFERENCES saldo(id)
            );
        """)

        conn.commit()
    except sqlite3.Error as e:
        print(f"Error creating tables: {e}")

# --- Fungsi Saldo (tidak berubah, tetap sama) ---
def tambah_saldo_awal(conn, tanggal, jumlah, keterangan):
    """Menambahkan data saldo awal ke tabel saldo."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM saldo")
        count = cursor.fetchone()[0]
        if count > 0:
             print("Warning: Saldo awal sudah ada. Gunakan update_saldo untuk perubahan.")
             cursor.execute("SELECT id FROM saldo ORDER BY id DESC LIMIT 1")
             result = cursor.fetchone()
             return result[0] if result else None
        cursor.execute("""
            INSERT INTO saldo (tanggal, jumlah, keterangan)
            VALUES (?, ?, ?)
        """, (tanggal, jumlah, keterangan))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Error adding initial balance: {e}")
        return None

def get_saldo_terakhir(conn):
    """Mengambil jumlah saldo terakhir."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT jumlah FROM saldo ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        return result[0] if result else 0
    except sqlite3.Error as e:
        print(f"Error fetching last balance: {e}")
        return 0

def update_saldo(conn, perubahan_jumlah, keterangan):
    """Mengupdate saldo terakhir dengan menambahkan entri baru berdasarkan perubahan."""
    try:
        saldo_sebelumnya = get_saldo_terakhir(conn)
        saldo_baru = saldo_sebelumnya + perubahan_jumlah
        tanggal_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO saldo (tanggal, jumlah, keterangan)
            VALUES (?, ?, ?)
        """, (tanggal_sekarang, saldo_baru, keterangan))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Error updating balance: {e}")
        return None

def get_all_saldo_entries(conn):
    """Mengambil semua entri dari tabel saldo, diurutkan dari yang terbaru."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, tanggal, jumlah, keterangan FROM saldo ORDER BY tanggal DESC, id DESC")
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error fetching all balance entries: {e}")
        return []

def get_saldo_entry_by_id(conn, saldo_id):
    """Mengambil satu entri saldo berdasarkan ID."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, tanggal, jumlah, keterangan FROM saldo WHERE id = ?", (saldo_id,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        print(f"Error fetching balance entry by ID: {e}")
        return None

def edit_saldo_entry(conn, saldo_id, tanggal, jumlah, keterangan):
    """Memperbarui entri saldo yang sudah ada."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE saldo
            SET tanggal = ?, jumlah = ?, keterangan = ?
            WHERE id = ?
        """, (tanggal, jumlah, keterangan, saldo_id))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error editing balance entry: {e}")
        return False

def hapus_saldo_entry(conn, saldo_id):
    """Menghapus entri saldo berdasarkan ID."""
    try:
        cursor = conn.cursor()
        # PERHATIAN: Cek apakah saldo_entry_id ini digunakan oleh pinjaman_modal atau pengeluaran_internal
        # Sebaiknya jangan hapus jika masih direferensikan, atau tangani FOREIGN KEY constraint.
        # Untuk simplicity, kita asumsikan pengguna tahu konsekuensinya.
        # Atau tambahkan logika untuk membersihkan referensi jika diperlukan.
        cursor.execute("DELETE FROM saldo WHERE id = ?", (saldo_id,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error deleting balance entry: {e}")
        return False

# --- Fungsi Penjualan (tidak berubah, tetap sama) ---
def tambah_penjualan(conn, tanggal, nama_item, harga_modal, harga_jual, laba, jenis_pembayaran, status_kredit=None):
    """Menambahkan data transaksi penjualan baru."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO penjualan (tanggal, nama_item, harga_modal, harga_jual, laba, jenis_pembayaran, status_kredit)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (tanggal, nama_item, harga_modal, harga_jual, laba, jenis_pembayaran, status_kredit))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Error adding sales transaction: {e}")
        return None

def get_penjualan_by_id(conn, id_penjualan):
    """Mengambil data penjualan berdasarkan ID."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, tanggal, nama_item, harga_modal, harga_jual, laba, jenis_pembayaran, status_kredit, tanggal_pelunasan
            FROM penjualan
            WHERE id = ?
        """, (id_penjualan,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        print(f"Error fetching sales by ID: {e}")
        return None

def update_penjualan(conn, id_penjualan, tanggal, nama_item, harga_modal, harga_jual, laba, jenis_pembayaran, status_kredit, tanggal_pelunasan):
    """Memperbarui data transaksi penjualan."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE penjualan
            SET tanggal = ?,
                nama_item = ?,
                harga_modal = ?,
                harga_jual = ?,
                laba = ?,
                jenis_pembayaran = ?,
                status_kredit = ?,
                tanggal_pelunasan = ?
            WHERE id = ?
        """, (tanggal, nama_item, harga_modal, harga_jual, laba, jenis_pembayaran, status_kredit, tanggal_pelunasan, id_penjualan))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error updating sales transaction: {e}")
        return False

def hapus_penjualan(conn, id_penjualan):
    """Menghapus data transaksi penjualan berdasarkan ID."""
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM penjualan WHERE id = ?", (id_penjualan,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error deleting sales transaction: {e}")
        return False

def get_penjualan_by_date_range(conn, start_date, end_date):
    '''Mengambil semua penjualan dalam rentang tanggal tertentu.'''
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, tanggal, nama_item, harga_modal, harga_jual, laba, jenis_pembayaran, status_kredit, tanggal_pelunasan
            FROM penjualan
            WHERE DATE(SUBSTR(tanggal, 1, 10)) BETWEEN ? AND ?
            ORDER BY tanggal DESC, id DESC
        ''', (start_date, end_date)) # Pastikan tanggal di SUBSTR jika formatnya YYYY-MM-DD HH:MM:SS
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error fetching sales by date range: {e}")
        return []

def get_global_transactions(conn, start_date, end_date):
    '''
    Mengambil semua transaksi tunai dan kredit yang sudah lunas
    dalam rentang tanggal tertentu untuk ditampilkan di riwayat global.
    '''
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, tanggal, nama_item, harga_modal, harga_jual, laba, jenis_pembayaran, status_kredit, tanggal_pelunasan
            FROM penjualan
            WHERE DATE(SUBSTR(tanggal, 1, 10)) BETWEEN ? AND ? AND
                  (jenis_pembayaran = 'Tunai' OR (jenis_pembayaran = 'Kredit' AND status_kredit = 'Lunas'))
            ORDER BY tanggal DESC, id DESC
        ''', (start_date, end_date))
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error fetching global transactions: {e}")
        return []

def get_kredit_belum_lunas(conn, start_date, end_date):
    '''
    Mengambil transaksi kredit yang belum lunas dalam rentang tanggal transaksi tertentu.
    '''
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, tanggal, nama_item, harga_modal, harga_jual, status_kredit
            FROM penjualan
            WHERE jenis_pembayaran = 'Kredit' AND status_kredit = 'Belum Lunas'
                  AND DATE(SUBSTR(tanggal, 1, 10)) BETWEEN ? AND ?
            ORDER BY tanggal ASC, id ASC
        ''', (start_date, end_date))
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error fetching unpaid credit transactions by date range: {e}")
        return []

def get_kredit_belum_lunas_all(conn):
    '''
    Mengambil SEMUA transaksi kredit yang belum lunas.
    '''
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, tanggal, nama_item, harga_modal, harga_jual, status_kredit
            FROM penjualan
            WHERE jenis_pembayaran = 'Kredit' AND status_kredit = 'Belum Lunas'
            ORDER BY tanggal ASC, id ASC
        ''')
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error fetching all unpaid credit transactions: {e}")
        return []

def lunasi_transaksi_kredit(conn, transaksi_id, tanggal_pelunasan):
    '''Mengupdate status transaksi kredit menjadi 'Lunas' dan mencatat tanggal pelunasan.'''
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE penjualan
            SET status_kredit = 'Lunas', tanggal_pelunasan = ?
            WHERE id = ? AND jenis_pembayaran = 'Kredit' AND status_kredit = 'Belum Lunas'
        """, (tanggal_pelunasan, transaksi_id))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error updating credit transaction to paid: {e}")
        return False

def get_kredit_by_id(conn, kredit_id):
    cur = conn.cursor()
    cur.execute("SELECT * FROM kredit WHERE id=?", (kredit_id,))
    return cur.fetchone()

def lunasi_kredit(conn, kredit_id, tanggal_lunas):
    cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE kredit SET status='Lunas', tanggal_lunas=? WHERE id=? AND status!='Lunas'",
            (tanggal_lunas, kredit_id)
        )
        conn.commit()
        return cur.rowcount > 0
    except Exception:
        return False

# --- Fungsi Pinjaman Modal (tidak berubah, tetap sama) ---
def tambah_pinjaman_modal(conn, tanggal_pinjam, jumlah_pinjam, keterangan, saldo_entry_id=None):
    """Menambahkan data pinjaman modal baru."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO pinjaman_modal (tanggal_pinjam, jumlah_pinjam, keterangan, status, tanggal_lunas, saldo_entry_id)
            VALUES (?, ?, ?, 'Aktif', NULL, ?)
        """, (tanggal_pinjam, jumlah_pinjam, keterangan, saldo_entry_id))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Error adding loan transaction: {e}")
        return None

def lunasi_pinjaman_modal(conn, pinjaman_id, tanggal_lunas):
    """Mengupdate status pinjaman modal menjadi 'Lunas'."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE pinjaman_modal
            SET status = 'Lunas', tanggal_lunas = ?
            WHERE id = ? AND status = 'Aktif'
        """, (tanggal_lunas, pinjaman_id))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error updating loan to paid: {e}")
        return False

def get_all_pinjaman_modal(conn):
    """Mengambil semua entri dari tabel pinjaman_modal, diurutkan dari yang terbaru."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, tanggal_pinjam, jumlah_pinjam, keterangan, status, tanggal_lunas, saldo_entry_id FROM pinjaman_modal ORDER BY tanggal_pinjam DESC, id DESC")
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error fetching all loan entries: {e}")
        return []

def get_pinjaman_modal_by_id(conn, pinjaman_id):
    """Mengambil satu entri pinjaman modal berdasarkan ID."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, tanggal_pinjam, jumlah_pinjam, keterangan, status, tanggal_lunas, saldo_entry_id FROM pinjaman_modal WHERE id = ?", (pinjaman_id,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        print(f"Error fetching loan entry by ID: {e}")
        return None

def get_total_pinjaman_aktif(conn):
    """Menghitung total jumlah pinjaman modal dengan status 'Aktif'."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(jumlah_pinjam) FROM pinjaman_modal WHERE status = 'Aktif'")
        result = cursor.fetchone()
        return result[0] if result and result[0] is not None else 0
    except sqlite3.Error as e:
        print(f"Error fetching total active loans: {e}")
        return 0

# --- Fungsi BARU untuk Pengeluaran Internal ---
def tambah_pengeluaran_internal(conn, tanggal, jumlah, keterangan, saldo_entry_id=None):
    """Menambahkan data pengeluaran internal baru."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO pengeluaran_internal (tanggal, jumlah, keterangan, saldo_entry_id)
            VALUES (?, ?, ?, ?)
        """, (tanggal, jumlah, keterangan, saldo_entry_id))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Error adding internal expense: {e}")
        return None

def get_all_pengeluaran_internal(conn, start_date=None, end_date=None):
    """
    Mengambil semua entri dari tabel pengeluaran_internal.
    Jika start_date dan end_date diberikan, filter berdasarkan rentang tanggal.
    """
    try:
        cursor = conn.cursor()
        query = "SELECT id, tanggal, jumlah, keterangan, saldo_entry_id FROM pengeluaran_internal"
        params = []
        if start_date and end_date:
            query += " WHERE DATE(SUBSTR(tanggal, 1, 10)) BETWEEN ? AND ?"
            params.extend([start_date, end_date])
        query += " ORDER BY tanggal DESC, id DESC"
        
        cursor.execute(query, params)
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error fetching all internal expenses: {e}")
        return []

def get_pengeluaran_internal_by_id(conn, pengeluaran_id):
    """Mengambil satu entri pengeluaran internal berdasarkan ID."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, tanggal, jumlah, keterangan, saldo_entry_id FROM pengeluaran_internal WHERE id = ?", (pengeluaran_id,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        print(f"Error fetching internal expense by ID: {e}")
        return None

def update_pengeluaran_internal(conn, pengeluaran_id, tanggal, jumlah, keterangan):
    """Memperbarui data pengeluaran internal."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE pengeluaran_internal
            SET tanggal = ?, jumlah = ?, keterangan = ?
            WHERE id = ?
        """, (tanggal, jumlah, keterangan, pengeluaran_id))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error updating internal expense: {e}")
        return False

def hapus_pengeluaran_internal(conn, pengeluaran_id):
    """Menghapus data pengeluaran internal berdasarkan ID."""
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pengeluaran_internal WHERE id = ?", (pengeluaran_id,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error deleting internal expense: {e}")
        return False