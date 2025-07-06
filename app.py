import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz
import os
import base64

# Konfigurasi awal
st.set_page_config(page_title="GempaLog.ID", layout="wide")

# ==== Fungsi Load CSS ====
def load_local_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ==== Fungsi Background Dinamis ====
def set_background(image_path):
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(255, 255, 255, 0.4), rgba(255, 255, 255, 0.4)),
                              url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        /* Atur transparansi container utama */
        .block-container {{
            background-color: rgba(255, 255, 255, 0.1) !important;
        }}
        </style>
    """, unsafe_allow_html=True)

# ==== Fungsi Ambil Data BMKG ====
def ambil_data_gempa_terkini():
    try:
        r = requests.get("https://data.bmkg.go.id/DataMKG/TEWS/gempaterkini.json", timeout=5)
        return pd.DataFrame(r.json()["Infogempa"]["gempa"])
    except:
        return pd.DataFrame()

def ambil_data_gempa_dirasakan():
    try:
        r = requests.get("https://data.bmkg.go.id/DataMKG/TEWS/gempadirasakan.json", timeout=5)
        return pd.DataFrame(r.json()["Infogempa"]["gempa"])
    except:
        return pd.DataFrame()

# ==== Persiapan Data Lokal ====
DATA_PATH = "data/bantuan.csv"
os.makedirs("data", exist_ok=True)
if not os.path.exists(DATA_PATH):
    pd.DataFrame(columns=["Nama", "Jenis Bantuan", "Jumlah", "Lokasi", "Waktu"]).to_csv(DATA_PATH, index=False)

# ==== Load CSS ====
load_local_css("style.css")

# ==== Sidebar Navigasi ====
menu = st.sidebar.radio("\ud83d\udccc Navigasi", ["\ud83c\udf0d Info Gempa", "\ud83d\udcdd Formulir Bantuan", "\ud83d\udcca Data Bantuan"])

# ==== Ganti Background Tiap Halaman ====
if menu == "\ud83c\udf0d Info Gempa":
    set_background("assets/gempa.jpg")
elif menu == "\ud83d\udcdd Formulir Bantuan":
    set_background("assets/bantuan.jpg")
elif menu == "\ud83d\udcca Data Bantuan":
    set_background("assets/statistik.jpg")

# ==== Header ====
with st.container():
    st.markdown("""
        <div class="transparent-box">
            <h2>\ud83c\udf10 GempaLog.ID</h2>
            <h4>Sistem Bantuan Logistik Bencana Gempa</h4>
        </div>
    """, unsafe_allow_html=True)

# ==== Halaman: Info Gempa ====
if menu == "\ud83c\udf0d Info Gempa":
    with st.container():
        st.markdown("""
<div class="transparent-box">
    <h3>\ud83d\udcf1 Informasi Gempa Real-time dari BMKG</h3>
</div>
""", unsafe_allow_html=True)

        df_terkini = ambil_data_gempa_terkini()
        if not df_terkini.empty:
            st.subheader("\ud83d\udcc4 Gempa Terkini")
            st.dataframe(df_terkini[["Tanggal", "Jam", "Wilayah", "Magnitude", "Kedalaman", "Potensi"]].head(10), use_container_width=True)
        else:
            st.warning("Gagal mengambil data gempa terkini.")

        df_dirasakan = ambil_data_gempa_dirasakan()
        if not df_dirasakan.empty:
            st.subheader("\ud83c\udf10 Gempa Dirasakan")
            df_map = df_dirasakan.copy()
            df_map["latitude"] = df_map["Lintang"].str.replace("LS", "").str.replace("LU", "").astype(float)
            df_map["longitude"] = df_map["Bujur"].str.replace("BT", "").astype(float) * -1
            st.map(df_map[["latitude", "longitude"]], zoom=4)

            kolom = ["Tanggal", "Jam", "Wilayah", "Magnitude", "Kedalaman", "Dirasakan"]
            st.dataframe(df_map[kolom], use_container_width=True)
        else:
            st.warning("Gagal mengambil data gempa dirasakan.")
        st.markdown('</div>', unsafe_allow_html=True)

# ==== Halaman: Formulir Bantuan ====
elif menu == "\ud83d\udcdd Formulir Bantuan":
    with st.container():
        st.markdown("""
            <div class="transparent-box">
                <h3>\ud83d\udce6 Formulir Pengiriman Bantuan</h3>
            </div>
        """, unsafe_allow_html=True)

        with st.container():
            with st.form("form_bantuan"):
                nama = st.text_input("\ud83d\udc64 Nama Pengirim")
                jenis = st.selectbox("\ud83d\udce6 Jenis Bantuan", ["Makanan", "Obat-obatan", "Pakaian", "Tenda", "Lainnya"])
                jumlah = st.number_input("\ud83d\udccf Jumlah", min_value=1)
                lokasi = st.text_input("\ud83d\udccd Lokasi Tujuan")
                submit = st.form_submit_button("\ud83d\udce4 Kirim")

                if submit:
                    zona_wib = pytz.timezone("Asia/Jakarta")
                    waktu = datetime.now(zona_wib).strftime("%Y-%m-%d %H:%M:%S WIB")
                    new_entry = pd.DataFrame([[nama, jenis, jumlah, lokasi, waktu]],
                                             columns=["Nama", "Jenis Bantuan", "Jumlah", "Lokasi", "Waktu"])
                    new_entry.to_csv(DATA_PATH, mode="a", header=False, index=False)
                    st.success("\u2705 Data bantuan berhasil disimpan.")

# ==== Halaman: Data Bantuan ====
elif menu == "\ud83d\udcca Data Bantuan":
    with st.container():
        st.markdown("""
        <div class="transparent-box">
            <h3>\ud83d\udcca Rekap Data Bantuan Masuk</h3>
        </div>
        """, unsafe_allow_html=True)

        if os.path.exists(DATA_PATH):
            df = pd.read_csv(DATA_PATH)

            st.markdown("""
            <div class="transparent-box">
                <h4>\ud83d\udccb Tabel Data Bantuan</h4>
            </div>
            """, unsafe_allow_html=True)
            st.dataframe(df, use_container_width=True)

            st.markdown("""
            <div class="transparent-box">
                <h4>\ud83d\udcc8 Statistik Bantuan per Jenis</h4>
            </div>
            """, unsafe_allow_html=True)
            st.bar_chart(df["Jenis Bantuan"].value_counts())
        else:
            st.info("Belum ada data bantuan.")