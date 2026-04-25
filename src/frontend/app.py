from pathlib import Path
import sys

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.input_parser import parse_urls


st.set_page_config(page_title="Google Maps Review Scraper", layout="wide")

st.title("Google Maps Review Scraper")
st.write("Masukkan keyword dan link Google Maps cabang yang mau dicari.")

if "google_map_urls" not in st.session_state:
    st.session_state.google_map_urls = [""]

with st.sidebar:
    st.header("Input Pencarian")
    keyword = st.text_input("Keyword", value="Honda Beat")
    st.write("Google Maps URLs")

    for index, value in enumerate(st.session_state.google_map_urls):
        st.session_state.google_map_urls[index] = st.text_input(
            label=f"URL {index + 1}",
            value=value,
            key=f"google_map_url_{index}",
        )

    add_col, _ = st.columns([1, 4])
    with add_col:
        if st.button("+", use_container_width=True):
            st.session_state.google_map_urls.append("")
            st.rerun()

    run_button = st.button("Jalankan")

if run_button:
    urls = parse_urls("\n".join(st.session_state.google_map_urls))

    st.subheader("Input yang dipilih")
    st.write("Keyword:", keyword)
    st.write("Jumlah lokasi:", len(urls))
    st.json({"keyword": keyword, "urls": urls})
else:
    st.info("Isi keyword dan klik + untuk menambah link lokasi, lalu klik 'Jalankan'.")
