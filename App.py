import streamlit as st
import pandas as pd
import re

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(page_title="SalesPintar v2.0", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .metric-card { background-color: #0F172A; padding: 20px; border-radius: 10px; border-left: 5px solid #FF6B35; color: white; margin-bottom: 10px; }
    .metric-value { font-size: 1.8rem; font-weight: bold; color: #10B981; }
    .metric-title { font-size: 0.9rem; color: #CBD5E1; }
    </style>
""", unsafe_allow_html=True)

hari_ini = pd.to_datetime('today').normalize()

def tentukan_status(tanggal_terakhir):
    if pd.isna(tanggal_terakhir): return '⚪ Data Kosong'
    selisih_hari = (hari_ini - tanggal_terakhir).days
    if selisih_hari <= 30: return '🟢 Current'
    elif selisih_hari <= 60: return '🟡 Aktif'
    elif selisih_hari <= 90: return '🟠 Dormant'
    else: return '🔴 Tidak Aktif'

# ==========================================
# 2. FUNGSI SMART SCANNER (Deteksi Kolom Otomatis)
# ==========================================
def temukan_kolom(df, kata_kunci_list):
    """Mencari kolom berdasarkan kemiripan kata kunci"""
    for col in df.columns:
        col_bersih = re.sub(r'[^a-zA-Z0-9]', '', str(col).lower())
        for keyword in kata_kunci_list:
            if keyword in col_bersih:
                return col
    return None

# ==========================================
# 3. MENU SIDEBAR
# ==========================================
st.sidebar.image("https://img.icons8.com/fluency/96/000000/lightning-bolt.png", width=50)
st.sidebar.markdown("<h2 style='color: #FF6B35;'>SalesPintar</h2>", unsafe_allow_html=True)
st.sidebar.write("---")

st.sidebar.subheader("📂 1. Upload Data")
file_excel = st.sidebar.file_uploader("Upload Data Penjualan", type=['xlsx', 'xls', 'csv'])

st.sidebar.write("---")
st.sidebar.subheader("🔐 2. Login Akses")
role = st.sidebar.radio("Pilih Mode:", ["👔 Mode Manajer", "🚶‍♂️ Mode Sales"])

# ==========================================
# 4. LOGIKA APLIKASI UTAMA
# ==========================================
if file_excel is None:
    st.markdown("<h1>⚡ Sales<span style='color:#FF6B35;'>Pintar</span></h1>", unsafe_allow_html=True)
    st.info("👈 **Upload file Excel Anda lewat menu di sebelah kiri.** Sistem Smart Scanner kami akan otomatis mendeteksi kolom data Anda.")
else:
    try:
        # Membaca data
        if file_excel.name.endswith('.csv'):
            df_mentah = pd.read_csv(file_excel)
        else:
            df_mentah = pd.read_excel(file_excel)
            
        # PROSES SMART MAPPING
        col_toko = temukan_kolom(df_mentah, ['toko', 'outlet', 'pelanggan', 'nama', 'customer'])
        col_wilayah = temukan_kolom(df_mentah, ['wilayah', 'area', 'cabang', 'rayon', 'kota', 'lokasi'])
        col_sales = temukan_kolom(df_mentah, ['sales', 'pic', 'karyawan', 'petugas'])
        col_tanggal = temukan_kolom(df_mentah, ['terakhir', 'tanggal', 'order', 'date', 'waktu', 'tgl'])
        col_omzet = temukan_kolom(df_mentah, ['omzet', 'penjualan', 'total', 'rupiah', 'rp', 'value'])

        # Jika kolom penting (Tanggal & Toko) tidak ketemu sama sekali
        if not col_tanggal or not col_toko:
            st.error("❌ **Sistem gagal mendeteksi struktur data.** Pastikan Excel Anda setidaknya memiliki kolom yang berisi 'Nama Toko' dan 'Tanggal Order'.")
            st.write("Kolom yang terdeteksi di file Anda:", list(df_mentah.columns))
        else:
            # Standarisasi nama kolom secara internal
            df = df_mentah.copy()
            mapping_kolom = {col_toko: 'Nama Outlet', col_wilayah: 'Wilayah', col_sales: 'Sales PIC', col_tanggal: 'Terakhir Order', col_omzet: 'Total Omzet'}
            # Hapus nilai None dari dictionary mapping (jika ada kolom opsional yang tidak ketemu)
            mapping_kolom = {k: v for k, v in mapping_kolom.items() if k is not None}
            df = df.rename(columns=mapping_kolom)
            
            # Jika wilayah/sales tidak ada, beri nilai default
            if 'Wilayah' not in df.columns: df['Wilayah'] = 'Area Umum'
            if 'Sales PIC' not in df.columns: df['Sales PIC'] = 'Tim Sales'
            if 'Total Omzet' not in df.columns: df['Total Omzet'] = 0

            # Konversi dan Kalkulasi
            df['Terakhir Order'] = pd.to_datetime(df['Terakhir Order'], errors='coerce')
            df['Hari Sejak Order'] = (hari_ini - df['Terakhir Order']).dt.days
            df['Status Outlet'] = df['Terakhir Order'].apply(tentukan_status)
            
            # Isi kolom numerik yang kosong dengan 0
            df['Total Omzet'] = pd.to_numeric(df['Total Omzet'], errors='coerce').fillna(0)

            st.success(f"🤖 **Smart Scanner Aktif:** Berhasil membaca data dari {len(df)} toko secara otomatis!")

            # ----------------------------------------
            # HALAMAN: MODE MANAJER
            # ----------------------------------------
            if role == "👔 Mode Manajer":
                st.markdown("<h1>📊 Dasbor Manajer: <span style='color:#FF6B35;'>Produktivitas Outlet</span></h1>", unsafe_allow_html=True)
