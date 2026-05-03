import streamlit as st
import pandas as pd
from datetime import date, timedelta

# ==========================================
# 1. KONFIGURASI HALAMAN & BRANDING
# ==========================================
st.set_page_config(page_title="SalesPintar v2.0", page_icon="⚡", layout="wide")

# Custom CSS untuk mempercantik metrik
st.markdown("""
    <style>
    .metric-card {
        background-color: #0F172A;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #FF6B35;
        color: white;
    }
    .metric-value { font-size: 2rem; font-weight: bold; color: #10B981; }
    .metric-title { font-size: 1rem; color: #CBD5E1; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. GENERATE DATA DUMMY (SIMULASI DATABASE)
# ==========================================
# Simulasi tanggal hari ini
hari_ini = date.today()

# Membuat data outlet dengan riwayat transaksi yang bervariasi
@st.cache_data
def load_data():
    data = {
        'ID Toko': ['TK-001', 'TK-002', 'TK-003', 'TK-004', 'TK-005', 'TK-006'],
        'Nama Outlet': ['Toko Makmur Jaya', 'Bengkel Sentosa', 'Bintang Motor', 'Maju Bersama', 'Sumber Rejeki', 'Karya Mandiri'],
        'Wilayah': ['Tanah Bumbu', 'Batulicin', 'Tanah Bumbu', 'Batulicin', 'Tanah Bumbu', 'Batulicin'],
        'Sales PIC': ['Rahmat', 'Budi', 'Rahmat', 'Siti', 'Budi', 'Siti'],
        # Simulasi selisih hari dari transaksi terakhir
        'Terakhir Order': [
            hari_ini - timedelta(days=15),  # Current
            hari_ini - timedelta(days=45),  # Aktif
            hari_ini - timedelta(days=75),  # Dormant
            hari_ini - timedelta(days=120), # Tidak Aktif
            hari_ini - timedelta(days=5),   # Current
            hari_ini - timedelta(days=85)   # Dormant
        ],
        'Total Omzet (Bulan Ini)': [5500000, 2000000, 0, 0, 8500000, 0]
    }
    return pd.DataFrame(data)

df = load_data()

# ==========================================
# 3. FUNGSI LOGIKA STATUS OUTLET
# ==========================================
def tentukan_status(tanggal_terakhir):
    selisih_hari = (hari_ini - tanggal_terakhir).days
    
    if selisih_hari <= 30:
        return '🟢 Current'
    elif selisih_hari <= 60:
        return '🟡 Aktif'
    elif selisih_hari <= 90:
        return '🟠 Dormant'
    else:
        return '🔴 Tidak Aktif'

# Terapkan logika ke dalam kolom baru di DataFrame
df['Hari Sejak Order'] = (hari_ini - df['Terakhir Order']).dt.days
df['Status Outlet'] = df['Terakhir Order'].apply(tentukan_status)

# ==========================================
# 4. SISTEM NAVIGASI & LOGIN
# ==========================================
st.sidebar.image("https://img.icons8.com/fluency/96/000000/lightning-bolt.png", width=50)
st.sidebar.markdown("<h2 style='color: #FF6B35;'>SalesPintar</h2>", unsafe_allow_html=True)
st.sidebar.markdown("**Rute Benar, Target Lancar!**")
st.sidebar.write("---")

st.sidebar.subheader("Login Sebagai:")
role = st.sidebar.radio("Pilih Akses:", ["👔 Mode Manajer", "🚶‍♂️ Mode Sales"])

# ==========================================
# 5. HALAMAN: MODE MANAJER (DASHBOARD ANALITIK)
# ==========================================
if role == "👔 Mode Manajer":
    st.markdown("<h1>📊 Dasbor Manajer: <span style='color:#FF6B35;'>Produktivitas Outlet</span></h1>", unsafe_allow_html=True)
    st.write("Pantau kesehatan transaksi dan pergerakan status outlet secara real-time.")
    
    # --- Top KPI Metrics ---
    st.write("### 📈 Ringkasan Performa")
    col1, col2, col3, col4 = st.columns(4)
    
    total_omzet = df['Total Omzet (Bulan Ini)'].sum()
    jml_current = len(df[df['Status Outlet'] == '🟢 Current'])
    jml_dormant = len(df[df['Status Outlet'] == '🟠 Dormant'])
    jml_mati = len(df[df['Status Outlet'] == '🔴 Tidak Aktif'])
    
    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-title'>Total Omzet Berjalan</div><div class='metric-value'>Rp {total_omzet:,.0f}</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card' style='border-color: #10B981;'><div class='metric-title'>Outlet Current</div><div class='metric-value' style='color:#10B981;'>{jml_current} Toko</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card' style='border-color: #F59E0B;'><div class='metric-title'>Outlet Dormant</div><div class='metric-value' style='color:#F59E0B;'>{jml_dormant} Toko</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='metric-card' style='border-color: #EF4444;'><div class='metric-title'>Outlet Tidak Aktif</div><div class='metric-value' style='color:#EF4444;'>{jml_mati} Toko</div></div>", unsafe_allow_html=True)
        
    st.write("---")
    
    # --- Filter & Tabel Data Utama ---
    st.write("### 🗂️ Pemetaan Status Outlet")
    
    # Filter interaktif untuk Manajer
    filter_wilayah = st.selectbox("Filter Wilayah:", ["Semua Area"] + list(df['Wilayah'].unique()))
    
    if filter_wilayah != "Semua Area":
        df_tampil = df[df['Wilayah'] == filter_wilayah]
    else:
        df_tampil = df
        
    # Menampilkan tabel data
    st.dataframe(
        df_tampil[['ID Toko', 'Nama Outlet', 'Wilayah', 'Sales PIC', 'Hari Sejak Order', 'Status Outlet', 'Total Omzet (Bulan Ini)']],
        use_container_width=True,
        hide_index=True
    )
    
    # --- Action Plan Section ---
    st.write("### ⚡ Rekomendasi Tindakan Cepat (Action Plan)")
    st.info("**Strategi Reaktivasi:** Anda memiliki **{} outlet Dormant**. Segera arahkan tim sales untuk melakukan kunjungan prioritas dan tawarkan promo Bundling FMS pada outlet-outlet ini sebelum berubah menjadi Tidak Aktif.".format(jml_dormant))

# ==========================================
# 6. HALAMAN: MODE SALES (EKSEKUSI LAPANGAN)
# ==========================================
elif role == "🚶‍♂️ Mode Sales":
    st.markdown("<h1>📱 Dasbor Sales: <span style='color:#10B981;'>Rute Kunjungan</span></h1>", unsafe_allow_html=True)
    
    nama_sales = st.selectbox("Pilih Profil Anda:", df['Sales PIC'].unique())
    
    st.write(f"Selamat bekerja, **{nama_sales}**! Ini adalah daftar outlet yang perlu penanganan khusus dari Anda hari ini.")
    
    # Memfilter data hanya untuk sales yang login dan hanya menampilkan outlet yang butuh perhatian (Dormant & Tidak Aktif)
    df_sales = df[(df['Sales PIC'] == nama_sales) & (df['Status Outlet'].isin(['🟠 Dormant', '🔴 Tidak Aktif']))]
    
    if len(df_sales) > 0:
        st.warning("⚠️ **Tugas Prioritas:** Lakukan reaktivasi pada toko berikut untuk menyelamatkan rute Anda!")
        st.dataframe(df_sales[['Nama Outlet', 'Wilayah', 'Hari Sejak Order', 'Status Outlet']], use_container_width=True, hide_index=True)
    else:
        st.success("🎉 Luar biasa! Semua outlet di rute Anda dalam kondisi Current dan Aktif. Fokus pada peningkatan volume order!")
