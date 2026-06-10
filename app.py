import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
import plotly.express as px
from streamlit_folium import st_folium

# =====================================================
# KONFIGURASI HALAMAN
# =====================================================

st.set_page_config(
    page_title="WebGIS Kesehatan Kota Bogor",
    layout="wide"
)

st.title("🏥 WebGIS Analisis Fasilitas Kesehatan Kota Bogor")

# =====================================================
# LOAD DATA
# =====================================================

@st.cache_data
def load_boundary():
    return gpd.read_file("clipping_boundary(1).geojson")

@st.cache_data
def load_faskes():
    return pd.read_csv("kota_bogor(2).csv")

@st.cache_data
def load_pelayanan():
    return pd.read_csv(
        "persentase_pelayanan_kesehatan_orang_dengan_resiko_te(1).csv"
    )

boundary = load_boundary()
faskes = load_faskes()
pelayanan = load_pelayanan()

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.header("Menu")

show_boundary = st.sidebar.checkbox(
    "Tampilkan Batas Wilayah",
    value=True
)

show_faskes = st.sidebar.checkbox(
    "Tampilkan Fasilitas Kesehatan",
    value=True
)

# =====================================================
# METRIK
# =====================================================

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Jumlah Fasilitas Kesehatan",
        len(faskes)
    )

with col2:
    st.metric(
        "Jumlah Data Pelayanan",
        len(pelayanan)
    )

# =====================================================
# PETA INTERAKTIF
# =====================================================

st.subheader("Peta Persebaran Fasilitas Kesehatan")

center_lat = -6.60
center_lon = 106.80

m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=11
)

# Batas wilayah
if show_boundary:

    folium.GeoJson(
        boundary,
        name="Batas Wilayah",
        style_function=lambda x: {
            "fillColor": "blue",
            "color": "black",
            "weight": 2,
            "fillOpacity": 0.1
        }
    ).add_to(m)

# Titik fasilitas kesehatan
if show_faskes:

    for _, row in faskes.iterrows():

        lat = row["latitude"]
        lon = row["longitude"]

        popup_text = ""

        if "nama" in row:
            popup_text = str(row["nama"])

        folium.Marker(
            [lat, lon],
            popup=popup_text,
            icon=folium.Icon(color="red")
        ).add_to(m)

folium.LayerControl().add_to(m)

st_folium(
    m,
    width=1200,
    height=600
)

# =====================================================
# TABEL DATA
# =====================================================

st.subheader("Data Fasilitas Kesehatan")

st.dataframe(
    faskes,
    use_container_width=True
)

# =====================================================
# GRAFIK PELAYANAN KESEHATAN
# =====================================================

st.subheader("Grafik Pelayanan Kesehatan")

st.write(
    "Pilih kolom numerik untuk divisualisasikan."
)

numeric_cols = pelayanan.select_dtypes(
    include="number"
).columns

if len(numeric_cols) > 0:

    selected_col = st.selectbox(
        "Kolom",
        numeric_cols
    )

    fig = px.line(
        pelayanan,
        y=selected_col,
        title=f"Tren {selected_col}"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

else:
    st.warning(
        "Tidak ditemukan kolom numerik."
    )

# =====================================================
# DOWNLOAD DATA
# =====================================================

st.subheader("Download Data")

csv = faskes.to_csv(index=False)

st.download_button(
    label="Download CSV Fasilitas Kesehatan",
    data=csv,
    file_name="fasilitas_kesehatan_bogor.csv",
    mime="text/csv"
)