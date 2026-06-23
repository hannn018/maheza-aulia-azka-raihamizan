"""
SISTEM AKADEMIK - Aplikasi Manajemen Data Mahasiswa
Bahasa: Python
Database: CSV
Struktur Data: Linked List (riwayat transaksi) + Hash Map (index pencarian cepat)
Operasi: CRUD (Create, Read, Update, Delete)
Fitur Searching & Sorting
"""

import csv
import os
import sys
from datetime import datetime


# ============================================================
# STRUKTUR DATA 1: LINKED LIST
# Digunakan untuk menyimpan riwayat aktivitas/log sistem
# ============================================================
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class LinkedList:
    """Linked List untuk menyimpan riwayat aktivitas sistem."""

    def __init__(self):
        self.head = None
        self.size = 0

    def append(self, data):
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
        self.size += 1

    def display(self, limit=10):
        """Tampilkan riwayat aktivitas (default 10 terakhir)."""
        items = []
        current = self.head
        while current:
            items.append(current.data)
            current = current.next
        # Ambil N terakhir
        return items[-limit:] if len(items) > limit else items

    def __len__(self):
        return self.size


# ============================================================
# STRUKTUR DATA 2: HASH MAP
# Digunakan untuk index pencarian cepat O(1) berdasarkan NIM
# ============================================================
class HashMap:
    """Hash Map untuk pencarian mahasiswa berdasarkan NIM."""

    def __init__(self, capacity=100):
        self.capacity = capacity
        self.buckets = [[] for _ in range(capacity)]
        self.count = 0

    def _hash(self, key):
        return hash(key) % self.capacity

    def put(self, key, value):
        idx = self._hash(key)
        bucket = self.buckets[idx]
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))
        self.count += 1

    def get(self, key):
        idx = self._hash(key)
        for k, v in self.buckets[idx]:
            if k == key:
                return v
        return None

    def delete(self, key):
        idx = self._hash(key)
        bucket = self.buckets[idx]
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket.pop(i)
                self.count -= 1
                return True
        return False

    def keys(self):
        result = []
        for bucket in self.buckets:
            for k, v in bucket:
                result.append(k)
        return result

    def values(self):
        result = []
        for bucket in self.buckets:
            for k, v in bucket:
                result.append(v)
        return result

    def __len__(self):
        return self.count


# ============================================================
# SORTING ALGORITHM: Merge Sort
# Digunakan untuk sorting data mahasiswa
# ============================================================
def merge_sort(arr, key_func, reverse=False):
    """Merge Sort O(n log n) untuk sorting list mahasiswa."""
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid], key_func, reverse)
    right = merge_sort(arr[mid:], key_func, reverse)
    return merge(left, right, key_func, reverse)


def merge(left, right, key_func, reverse):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        cond = key_func(left[i]) <= key_func(right[j])
        if reverse:
            cond = not cond
        if cond:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


# ============================================================
# SEARCHING: Binary Search
# Digunakan untuk pencarian berdasarkan NIM (data terurut)
# ============================================================
def binary_search(sorted_list, target_nim):
    """Binary Search O(log n) pada list yang sudah diurutkan by NIM."""
    low, high = 0, len(sorted_list) - 1
    while low <= high:
        mid = (low + high) // 2
        mid_nim = sorted_list[mid]['nim']
        if mid_nim == target_nim:
            return mid
        elif mid_nim < target_nim:
            low = mid + 1
        else:
            high = mid - 1
    return -1


# ============================================================
# SISTEM AKADEMIK UTAMA
# ============================================================
class SistemAkademik:
    CSV_FILE = 'mahasiswa.csv'
    MATKUL_FILE = 'mata_kuliah.csv'
    NILAI_FILE = 'nilai.csv'
    FIELDNAMES_MHS = ['nim', 'nama', 'prodi', 'angkatan', 'ipk', 'status']
    FIELDNAMES_MK = ['kode_mk', 'nama_mk', 'sks', 'dosen']
    FIELDNAMES_NILAI = ['nim', 'kode_mk', 'nilai_angka', 'nilai_huruf', 'semester']

    def __init__(self):
        self.riwayat = LinkedList()          # Struktur Data 1: Linked List
        self.index_mahasiswa = HashMap()     # Struktur Data 2: Hash Map
        self._init_csv()
        self._load_index()
        self._log("Sistem Akademik diinisialisasi.")

    # ---- INISIALISASI CSV ----
    def _init_csv(self):
        for file, fields in [
            (self.CSV_FILE, self.FIELDNAMES_MHS),
            (self.MATKUL_FILE, self.FIELDNAMES_MK),
            (self.NILAI_FILE, self.FIELDNAMES_NILAI),
        ]:
            if not os.path.exists(file):
                with open(file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fields)
                    writer.writeheader()

    def _load_index(self):
        """Load semua mahasiswa ke HashMap untuk pencarian cepat."""
        self.index_mahasiswa = HashMap()
        for mhs in self._read_all(self.CSV_FILE):
            self.index_mahasiswa.put(mhs['nim'], mhs)

    def _log(self, pesan):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.riwayat.append(f"[{timestamp}] {pesan}")

    # ---- HELPER CSV ----
    def _read_all(self, file):
        if not os.path.exists(file):
            return []
        with open(file, 'r', encoding='utf-8') as f:
            return list(csv.DictReader(f))

    def _write_all(self, file, data, fieldnames):
        with open(file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

    # ===========================================================
    # MODUL 1: CRUD MAHASISWA
    # ===========================================================

    def tambah_mahasiswa(self):
        """CREATE - Tambah data mahasiswa baru."""
        print("\n" + "="*50)
        print("  TAMBAH DATA MAHASISWA")
        print("="*50)

        nim = input("NIM          : ").strip()
        if not nim:
            print("[!] NIM tidak boleh kosong.")
            return

        # Cek duplikat via HashMap O(1)
        if self.index_mahasiswa.get(nim):
            print(f"[!] NIM {nim} sudah terdaftar.")
            return

        nama = input("Nama Lengkap : ").strip()
        prodi = input("Program Studi: ").strip()
        angkatan = input("Angkatan     : ").strip()
        ipk = input("IPK (0.00-4.00): ").strip()
        status = input("Status (Aktif/Cuti/Lulus): ").strip()

        try:
            ipk_val = float(ipk)
            assert 0.0 <= ipk_val <= 4.0
        except (ValueError, AssertionError):
            print("[!] IPK tidak valid. Harus angka antara 0.00 - 4.00.")
            return

        data = {
            'nim': nim, 'nama': nama, 'prodi': prodi,
            'angkatan': angkatan, 'ipk': ipk, 'status': status
        }

        with open(self.CSV_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES_MHS)
            writer.writerow(data)

        self.index_mahasiswa.put(nim, data)
        self._log(f"CREATE: Mahasiswa {nim} - {nama} ditambahkan.")
        print(f"\n[✓] Mahasiswa {nama} (NIM: {nim}) berhasil ditambahkan!")

    def lihat_mahasiswa(self):
        """READ - Tampilkan semua data mahasiswa."""
        data = self._read_all(self.CSV_FILE)
        print("\n" + "="*85)
        print(f"  DAFTAR MAHASISWA  (Total: {len(data)} mahasiswa)")
        print("="*85)
        if not data:
            print("  [!] Belum ada data mahasiswa.")
        else:
            print(f"{'No':<4} {'NIM':<12} {'Nama':<25} {'Prodi':<20} {'Angkatan':<10} {'IPK':<6} {'Status'}")
            print("-"*85)
            for i, m in enumerate(data, 1):
                print(f"{i:<4} {m['nim']:<12} {m['nama']:<25} {m['prodi']:<20} {m['angkatan']:<10} {m['ipk']:<6} {m['status']}")
        print("="*85)
        self._log("READ: Daftar mahasiswa ditampilkan.")

    def cari_mahasiswa(self):
        """SEARCH - Cari mahasiswa (HashMap O(1) by NIM, atau linear by nama)."""
        print("\n" + "="*50)
        print("  CARI MAHASISWA")
        print("="*50)
        print("1. Cari by NIM  (Hash Map - O(1))")
        print("2. Cari by Nama (Linear Search)")
        print("3. Cari by NIM  (Binary Search - data terurut)")
        pilihan = input("Pilih metode [1/2/3]: ").strip()

        if pilihan == '1':
            nim = input("Masukkan NIM: ").strip()
            hasil = self.index_mahasiswa.get(nim)
            if hasil:
                self._tampil_detail_mhs(hasil)
                self._log(f"SEARCH: NIM {nim} ditemukan via HashMap.")
            else:
                print(f"[!] Mahasiswa NIM {nim} tidak ditemukan.")

        elif pilihan == '2':
            kata = input("Masukkan nama (sebagian): ").strip().lower()
            data = self._read_all(self.CSV_FILE)
            hasil = [m for m in data if kata in m['nama'].lower()]
            if hasil:
                print(f"\n[✓] Ditemukan {len(hasil)} mahasiswa:")
                for m in hasil:
                    self._tampil_detail_mhs(m)
            else:
                print("[!] Tidak ada mahasiswa dengan nama tersebut.")
            self._log(f"SEARCH: Pencarian nama '{kata}' selesai.")

        elif pilihan == '3':
            nim = input("Masukkan NIM: ").strip()
            data = self._read_all(self.CSV_FILE)
            sorted_data = merge_sort(data, key_func=lambda x: x['nim'])
            idx = binary_search(sorted_data, nim)
            if idx >= 0:
                self._tampil_detail_mhs(sorted_data[idx])
                self._log(f"SEARCH: NIM {nim} ditemukan via Binary Search.")
            else:
                print(f"[!] Mahasiswa NIM {nim} tidak ditemukan.")
        else:
            print("[!] Pilihan tidak valid.")

    def _tampil_detail_mhs(self, m):
        print("\n  ┌─────────────────────────────────┐")
        print(f"  │ NIM      : {m['nim']}")
        print(f"  │ Nama     : {m['nama']}")
        print(f"  │ Prodi    : {m['prodi']}")
        print(f"  │ Angkatan : {m['angkatan']}")
        print(f"  │ IPK      : {m['ipk']}")
        print(f"  │ Status   : {m['status']}")
        print("  └─────────────────────────────────┘")

    def update_mahasiswa(self):
        """UPDATE - Perbarui data mahasiswa."""
        print("\n" + "="*50)
        print("  UPDATE DATA MAHASISWA")
        print("="*50)
        nim = input("Masukkan NIM mahasiswa yang akan diupdate: ").strip()

        data = self._read_all(self.CSV_FILE)
        ditemukan = False
        for i, m in enumerate(data):
            if m['nim'] == nim:
                ditemukan = True
                print(f"\nData saat ini:")
                self._tampil_detail_mhs(m)
                print("\nKosongkan input untuk tidak mengubah field.")
                nama_baru = input(f"Nama baru [{m['nama']}]: ").strip() or m['nama']
                prodi_baru = input(f"Prodi baru [{m['prodi']}]: ").strip() or m['prodi']
                angkatan_baru = input(f"Angkatan baru [{m['angkatan']}]: ").strip() or m['angkatan']
                ipk_baru = input(f"IPK baru [{m['ipk']}]: ").strip() or m['ipk']
                status_baru = input(f"Status baru [{m['status']}]: ").strip() or m['status']

                data[i] = {
                    'nim': nim, 'nama': nama_baru, 'prodi': prodi_baru,
                    'angkatan': angkatan_baru, 'ipk': ipk_baru, 'status': status_baru
                }
                break

        if not ditemukan:
            print(f"[!] Mahasiswa NIM {nim} tidak ditemukan.")
            return

        self._write_all(self.CSV_FILE, data, self.FIELDNAMES_MHS)
        self._load_index()
        self._log(f"UPDATE: Data mahasiswa NIM {nim} diperbarui.")
        print(f"\n[✓] Data mahasiswa {nim} berhasil diperbarui!")

    def hapus_mahasiswa(self):
        """DELETE - Hapus data mahasiswa."""
        print("\n" + "="*50)
        print("  HAPUS DATA MAHASISWA")
        print("="*50)
        nim = input("Masukkan NIM mahasiswa yang akan dihapus: ").strip()

        data = self._read_all(self.CSV_FILE)
        data_baru = [m for m in data if m['nim'] != nim]

        if len(data_baru) == len(data):
            print(f"[!] Mahasiswa NIM {nim} tidak ditemukan.")
            return

        konfirmasi = input(f"Yakin hapus mahasiswa NIM {nim}? (y/n): ").strip().lower()
        if konfirmasi != 'y':
            print("[!] Penghapusan dibatalkan.")
            return

        self._write_all(self.CSV_FILE, data_baru, self.FIELDNAMES_MHS)
        # Hapus juga nilai-nilai mahasiswa ini
        nilai = self._read_all(self.NILAI_FILE)
        nilai_baru = [n for n in nilai if n['nim'] != nim]
        self._write_all(self.NILAI_FILE, nilai_baru, self.FIELDNAMES_NILAI)

        self.index_mahasiswa.delete(nim)
        self._log(f"DELETE: Mahasiswa NIM {nim} dihapus.")
        print(f"\n[✓] Mahasiswa NIM {nim} berhasil dihapus!")

    # ===========================================================
    # MODUL 2: CRUD MATA KULIAH
    # ===========================================================

    def tambah_matkul(self):
        print("\n" + "="*50)
        print("  TAMBAH MATA KULIAH")
        print("="*50)
        kode = input("Kode MK   : ").strip().upper()
        nama = input("Nama MK   : ").strip()
        sks = input("SKS       : ").strip()
        dosen = input("Dosen     : ").strip()

        data = self._read_all(self.MATKUL_FILE)
        if any(m['kode_mk'] == kode for m in data):
            print(f"[!] Kode MK {kode} sudah ada.")
            return

        baru = {'kode_mk': kode, 'nama_mk': nama, 'sks': sks, 'dosen': dosen}
        with open(self.MATKUL_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES_MK)
            writer.writerow(baru)
        self._log(f"CREATE: Mata Kuliah {kode} - {nama} ditambahkan.")
        print(f"\n[✓] Mata Kuliah {nama} ({kode}) berhasil ditambahkan!")

    def lihat_matkul(self):
        data = self._read_all(self.MATKUL_FILE)
        print("\n" + "="*70)
        print(f"  DAFTAR MATA KULIAH (Total: {len(data)})")
        print("="*70)
        if not data:
            print("  [!] Belum ada mata kuliah.")
        else:
            print(f"{'No':<4} {'Kode':<10} {'Nama MK':<30} {'SKS':<5} {'Dosen'}")
            print("-"*70)
            for i, m in enumerate(data, 1):
                print(f"{i:<4} {m['kode_mk']:<10} {m['nama_mk']:<30} {m['sks']:<5} {m['dosen']}")
        print("="*70)
        self._log("READ: Daftar mata kuliah ditampilkan.")

    def hapus_matkul(self):
        kode = input("Kode MK yang dihapus: ").strip().upper()
        data = self._read_all(self.MATKUL_FILE)
        data_baru = [m for m in data if m['kode_mk'] != kode]
        if len(data_baru) == len(data):
            print(f"[!] Kode MK {kode} tidak ditemukan.")
            return
        self._write_all(self.MATKUL_FILE, data_baru, self.FIELDNAMES_MK)
        self._log(f"DELETE: Mata Kuliah {kode} dihapus.")
        print(f"[✓] Mata Kuliah {kode} dihapus.")

    # ===========================================================
    # MODUL 3: CRUD NILAI
    # ===========================================================

    def _angka_ke_huruf(self, nilai):
        if nilai >= 85: return 'A'
        elif nilai >= 80: return 'A-'
        elif nilai >= 75: return 'B+'
        elif nilai >= 70: return 'B'
        elif nilai >= 65: return 'B-'
        elif nilai >= 60: return 'C+'
        elif nilai >= 55: return 'C'
        elif nilai >= 50: return 'D'
        else: return 'E'

    def input_nilai(self):
        print("\n" + "="*50)
        print("  INPUT NILAI MAHASISWA")
        print("="*50)
        nim = input("NIM Mahasiswa: ").strip()
        if not self.index_mahasiswa.get(nim):
            print(f"[!] Mahasiswa NIM {nim} tidak ditemukan.")
            return

        kode_mk = input("Kode MK      : ").strip().upper()
        matkul = self._read_all(self.MATKUL_FILE)
        if not any(m['kode_mk'] == kode_mk for m in matkul):
            print(f"[!] Kode MK {kode_mk} tidak ditemukan.")
            return

        semester = input("Semester     : ").strip()
        try:
            nilai_angka = float(input("Nilai (0-100): ").strip())
            assert 0 <= nilai_angka <= 100
        except (ValueError, AssertionError):
            print("[!] Nilai tidak valid.")
            return

        nilai_huruf = self._angka_ke_huruf(nilai_angka)
        baru = {
            'nim': nim, 'kode_mk': kode_mk,
            'nilai_angka': nilai_angka, 'nilai_huruf': nilai_huruf,
            'semester': semester
        }
        with open(self.NILAI_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES_NILAI)
            writer.writerow(baru)
        self._log(f"CREATE: Nilai {nim}/{kode_mk} = {nilai_angka} ({nilai_huruf}).")
        print(f"\n[✓] Nilai berhasil disimpan! Nilai Huruf: {nilai_huruf}")

    def lihat_nilai_mahasiswa(self):
        nim = input("NIM Mahasiswa: ").strip()
        nilai = self._read_all(self.NILAI_FILE)
        hasil = [n for n in nilai if n['nim'] == nim]
        mhs = self.index_mahasiswa.get(nim)
        nama = mhs['nama'] if mhs else nim

        print(f"\n{'='*60}")
        print(f"  TRANSKRIP NILAI: {nama} ({nim})")
        print("="*60)
        if not hasil:
            print("  [!] Belum ada nilai.")
        else:
            print(f"{'No':<4} {'Kode MK':<12} {'Nilai':<8} {'Huruf':<8} {'Semester'}")
            print("-"*60)
            for i, n in enumerate(hasil, 1):
                print(f"{i:<4} {n['kode_mk']:<12} {n['nilai_angka']:<8} {n['nilai_huruf']:<8} {n['semester']}")
            # Hitung rata-rata
            rata = sum(float(n['nilai_angka']) for n in hasil) / len(hasil)
            print("-"*60)
            print(f"  Rata-rata Nilai: {rata:.2f} ({self._angka_ke_huruf(rata)})")
        print("="*60)
        self._log(f"READ: Nilai mahasiswa {nim} ditampilkan.")

    # ===========================================================
    # MODUL 4: SORTING & STATISTIK
    # ===========================================================

    def sorting_mahasiswa(self):
        print("\n" + "="*50)
        print("  SORTING MAHASISWA (Merge Sort)")
        print("="*50)
        print("Sort berdasarkan:")
        print("1. IPK (Tertinggi ke Terendah)")
        print("2. Nama (A-Z)")
        print("3. NIM (Ascending)")
        print("4. Angkatan")
        pilihan = input("Pilih [1-4]: ").strip()

        data = self._read_all(self.CSV_FILE)
        if not data:
            print("[!] Tidak ada data.")
            return

        if pilihan == '1':
            sorted_data = merge_sort(data, key_func=lambda x: float(x['ipk'] or 0),
