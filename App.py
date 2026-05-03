import streamlit as st
import pandas as pd

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
    selisih_hari = (hari_ini - tanggal_terakhir).days
    if selisih_hari <= 30: return '🟢 Current'
    elif selisih_hari <= 60: return '🟡 Aktif'
    elif selisih_hari <= 90: return '🟠 Dormant'
    else: return '🔴 Tidak Aktif'

# ==========================================
# 2. MENU SIDEBAR & UPLOAD EXCEL
# ==========================================
st.sidebar.image("https://img.icons8.com/fluency/96/000000/lightning-bolt.png", width=50)
st.sidebar.markdown("<h2 style='color: #FF6B35;'>SalesPintar</h2>", unsafe_allow_html=True)

st.sidebar.write("---")
st.sidebar.subheader("📂 1. Upload Data")
file_excel = st.sidebar.file_uploader("Pilih file Excel database Anda", type=['xlsx'])

st.sidebar.write("---")
st.sidebar.subheader("🔐 2. Login Akses")
role = st.sidebar.radio("Pilih Mode:", ["👔 Mode Manajer", "🚶‍♂️ Mode Sales"])

# ==========================================
# 3. LOGIKA APLIKASI UTAMA
# ==========================================
if file_excel is None:
    st.markdown("<h1>⚡ Selamat Datang di <span style='color:#FF6B35;'>SalesPintar</span></h1>", unsafe_allow_html=True)
    st.info("👈 **Silakan klik tanda panah ( > ) di pojok kiri atas untuk membuka menu dan mengunggah file Excel Anda.**")
    st.write("Pastikan file Excel Anda memiliki kolom: `ID Toko`, `Nama Outlet`, `Wilayah`, `Sales PIC`, `Terakhir Order`, dan `Total Omzet (Bulan Ini)`.")
else:
    try:
        # Membaca data dari Excel yang diupload
        df = pd.read_excel(file_excel)
        df['Terakhir Order'] = pd.to_datetime(df['Terakhir Order'])
        
        # Mengkalkulasi status otomatis
        df['Hari Sejak Order'] = (hari_ini - df['Terakhir Order']).dt.days
        df['Status Outlet'] = df['Terakhir Order'].apply(tentukan_status)

        # ----------------------------------------
        # HALAMAN: MODE MANAJER
        # ----------------------------------------
        if role == "👔 Mode Manajer":
            st.markdown("<h1>📊 Dasbor Manajer: <span style='color:#FF6B35;'>Produktivitas Outlet</span></h1>", unsafe_allow_html=True)
            
            total_omzet = df['Total Omzet (Bulan Ini)'].sum()
            jml_current = len(df[df['Status Outlet'] == '🟢 Current'])
            jml_dormant = len(df[df['Status Outlet'] == '🟠 Dormant'])
            jml_mati = len(df[df['Status Outlet'] == '🔴 Tidak Aktif'])
            
            col1, col2 = st.columns(2)
            with col1: st.markdown(f"<div class='metric-card'><div class='metric-title'>Total Omzet Berjalan</div><div class='metric-value'>Rp {total_omzet:,.0f}</div></div>", unsafe_allow_html=True)
            with col2: st.markdown(f"<div class='metric-card' style='border-color: #10B981;'><div class='metric-title'>Outlet Sehat (Current)</div><div class='metric-value' style='color:#10B981;'>{jml_current} Toko</div></div>", unsafe_allow_html=True)
            
            col3, col4 = st.columns(2)
            with col3: st.markdown(f"<div class='metric-card' style='border-color: #F59E0B;'><div class='metric-title'>Outlet Dormant</div><div class='metric-value' style='color:#F59E0B;'>{jml_dormant} Toko</div></div>", unsafe_allow_html=True)
            with col4: st.markdown(f"<div class='metric-card' style='border-color: #EF4444;'><div class='metric-title'>Outlet Tidak Aktif</div><div class='metric-value' style='color:#EF4444;'>{jml_mati} Toko</div></div>", unsafe_allow_html=True)
                
            st.write("---")
            filter_wilayah = st.selectbox("Filter Wilayah:", ["Semua Area"] + list(df['Wilayah'].unique()))
            
            if filter_wilayah != "Semua Area": df_tampil = df[df['Wilayah'] == filter_wilayah].copy()
            else: df_tampil = df.copy()
                
            df_tampil['Terakhir Order'] = df_tampil['Terakhir Order'].dt.strftime('%d-%m-%Y')
            st.dataframe(df_tampil[['Nama Outlet', 'Wilayah', 'Sales PIC', 'Terakhir Order', 'Status Outlet', 'Total Omzet (Bulan Ini)']], use_container_width=True, hide_index=True)

        # ----------------------------------------
        # HALAMAN: MODE SALES
        # ----------------------------------------
        elif role == "🚶‍♂️ Mode Sales":
            st.markdown("<h1>📱 Dasbor Sales: <span style='color:#10B981;'>Rute Prioritas</span></h1>", unsafe_allow_html=True)
            nama_sales = st.selectbox("Pilih Profil Anda:", df['Sales PIC'].unique())
            
            df_sales = df[(df['Sales PIC'] == nama_sales) & (df['Status Outlet'].isin(['🟠 Dormant', '🔴 Tidak Aktif']))].copy()
            
            if len(df_sales) > 0:
                st.warning(f"⚠️ **{nama_sales}**, ada {len(df_sales)} outlet yang perlu di-reaktivasi segera!")
                df_sales['Terakhir Order'] = df_sales['Terakhir Order'].dt.strftime('%d-%m-%Y')
                st.dataframe(df_sales[['Nama Outlet', 'Wilayah', 'Hari Sejak Order', 'Status Outlet']], use_container_width=True, hide_index=True)
            else:
                st.success("🎉 Luar biasa! Semua outlet rute Anda sehat.")

    except Exception as e:
        st.error(f"Terjadi kesalahan membaca file Excel. Pastikan nama kolom sudah tepat. Error detail: {e}")
