import streamlit as st

from src.input_parser import parse_urls


st.set_page_config(page_title="Google Maps Review Scraper", layout="wide")

st.title("Google Maps Review Scraper")
st.write("Masukkan keyword dan link Google Maps cabang yang mau dicari.")

with st.sidebar:
    st.header("Input Pencarian")
    keyword = st.text_input("Keyword", value="Honda Beat")
    location_text = st.text_area(
        "Google Maps URLs",
        value="https://www.google.com/maps",
        height=200,
        help="Satu URL per baris.",
    )
    run_button = st.button("Jalankan")

if run_button:
    urls = parse_urls(location_text)

    st.subheader("Input yang dipilih")
    st.write("Keyword:", keyword)
    st.write("Jumlah lokasi:", len(urls))
    st.json({"keyword": keyword, "urls": urls})
else:
    st.info("Isi keyword dan link lokasi, lalu klik 'Jalankan'.")

