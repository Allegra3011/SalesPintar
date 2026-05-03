import streamlit as st
import pandas as pd
import numpy as np

# ==========================================
# 1. SETUP & BRANDING
# ==========================================
st.set_page_config(page_title="SalesPintar Pro", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .metric-card { background-color: #0F172A; padding: 15px; border-radius: 10px; border-left: 5px solid #FF6B35; color: white; }
    .metric-value { font-size: 1.5rem; font-weight: bold; color: #10B981; }
    </style>
""", unsafe_allow_html=True)

# Inisialisasi Database Sales di Memory (Stateful)
if 'master_sales' not in st.session_state:
    st.session_state.master_sales = ["Rahmat", "Budi", "Siti"] # Data awal

hari_ini = pd.to_datetime('today').normalize()

# ==========================================
# 2. MENU SIDEBAR (PUSAT KENDALI)
# ==========================================
st.sidebar.image("https://img.icons8.com/fluency/96/000000/lightning-bolt.png", width=50)
st.sidebar.markdown("<h2 style='color: #FF6B35;'>SalesPintar Pro</h2>", unsafe_allow_html=True)

# Fitur Tambah Sales Manual
st.sidebar.write("---")
st.sidebar.subheader("👤 Management Tim")
new_sales = st.sidebar.text_input("Tambah Nama Sales Baru:")
if st.sidebar.button("Tambah ke Sistem"):
    if new_sales and new_sales not in st.session_state.master_sales:
        st.session_state.master_sales.append(new_sales)
        st.sidebar.success(f"{new_sales} berhasil ditambahkan!")

# Fitur Multi-File Upload
st.sidebar.write("---")
st.sidebar.subheader("📂 Sumber Data")
uploaded_files = st.sidebar.file_uploader("Upload satu atau beberapa file Excel/CSV", type=['xlsx', 'csv'], accept_multiple_files=True)

role = st.sidebar.radio("Mode Tampilan:", ["👔 Manajer (Analitik)", "🚶‍♂️ Sales (Lapangan)"])

# ==========================================
# 3. MESIN PEMROSES DATA (MULTI-FILE MERGER)
# ==========================================
def process_all_data(files):
    all_df = []
    for f in files:
        df = pd.read_csv(f) if f.name.endswith('.csv') else pd.read_excel(f)
        all_df.append(df)
    
    combined = pd.concat(all_df, ignore_index=True)
    
    # Smart Cleaning Tanggal
    date_col = next((c for c in combined.columns if 'tgl' in c.lower() or 'tanggal' in c.lower() or 'order' in c.lower()), None)
    if date_col:
        combined[date_col] = pd.to_datetime(combined[date_col], errors='coerce')
        combined['Hari Sejak Order'] = (hari_ini - combined[date_col]).dt.days
    
    return combined, date_col

# ==========================================
# 4. DASHBOARD UTAMA
# ==========================================
if not uploaded_files:
    st.title("⚡ Selamat Datang, Supervisor!")
    st.info("Silakan unggah file database penjualan Anda di sidebar untuk memulai analisis wilayah.")
    
    # Menampilkan Master Sales yang terdaftar
    st.write("### Tim Sales Terdaftar saat ini:")
    st.write(", ".join(st.session_state.master_sales))

else:
    df, date_col = process_all_data(uploaded_files)
    
    if role == "👔 Manajer (Analitik)":
        st.title("📊 Kendali Produktivitas Wilayah")
        
        # METRIK UTAMA
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"<div class='metric-card'>Total Outlet<br><span class='metric-value'>{len(df)} Toko</span></div>", unsafe_allow_html=True)
        with col2:
            current_count = len(df[df['Hari Sejak Order'] <= 30]) if 'Hari Sejak Order' in df.columns else 0
            st.markdown(f"<div class='metric-card'>Outlet Sehat (Current)<br><span class='metric-value'>{current_count} Toko</span></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='metric-card'>Tim Aktif<br><span class='metric-value'>{len(st.session_state.master_sales)} Personel</span></div>", unsafe_allow_html=True)

        # INTEGRASI MAPS (Jika ada data Latitude & Longitude)
        st.write("---")
        st.subheader("📍 Pemetaan Lokasi Outlet")
        
        # Simulasi deteksi kolom lokasi untuk Maps
        lat_col = next((c for c in df.columns if 'lat' in c.lower()), None)
        lon_col = next((c for c in df.columns if 'lon' in c.lower() or 'lng' in c.lower()), None)
        
        if lat_col and lon_col:
            map_data = df[[lat_col, lon_col]].dropna()
            st.map(map_data)
        else:
            st.warning("Info: Untuk mengaktifkan fitur peta, pastikan Excel Anda memiliki kolom 'Latitude' dan 'Longitude'.")

        # ANALISIS PER SALES
        st.write("---")
        st.subheader("📈 Performa Berdasarkan Tim")
        sales_col = next((c for c in df.columns if 'sales' in c.lower() or 'pic' in c.lower()), None)
        
        if sales_col:
            # Menggabungkan data Excel dengan Master Sales kita
            sales_summary = df.groupby(sales_col).size().reset_index(name='Jumlah Toko')
            st.bar_chart(sales_summary.set_index(sales_col))
            st.write(df)
            
    elif role == "🚶‍♂️ Sales (Lapangan)":
        st.title("📱 Rute Cerdas Anda")
        user_sales = st.selectbox("Pilih Nama Anda:", st.session_state.master_sales)
        # Filter data spesifik untuk sales tersebut
        # (Logika pencocokan string cerdas bisa ditambahkan di sini)
        st.success(f"Menampilkan rute prioritas untuk {user_sales}...")
