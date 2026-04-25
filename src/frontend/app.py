from pathlib import Path
import json
import sys
from uuid import uuid4

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.input_parser import parse_urls
from src.apify_runner import run_google_maps_reviews_scraper
from src.config import APIFY_TOKEN


st.set_page_config(page_title="Google Maps Review Scraper", layout="wide")

st.title("Google Maps Review Scraper")
st.write("Masukkan keyword dan link Google Maps cabang yang mau dicari.")

if "google_map_urls" not in st.session_state:
    st.session_state.google_map_urls = [{"id": uuid4().hex, "url": ""}]

with st.sidebar:
    st.header("Input Pencarian")
    keyword = st.text_input("Keyword filter", value="beat")
    st.write("Google Maps URLs")

    for index, item in enumerate(list(st.session_state.google_map_urls)):
        row_col, remove_col = st.columns([8, 1])
        input_key = f"google_map_url_{item['id']}"

        with row_col:
            st.text_input(
                label=f"URL {index + 1}",
                value=item["url"],
                key=input_key,
            )

        st.session_state.google_map_urls[index]["url"] = st.session_state[input_key]

        with remove_col:
            if len(st.session_state.google_map_urls) > 1 and st.button(
                "-", key=f"remove_{item['id']}", use_container_width=True
            ):
                st.session_state.google_map_urls = [
                    row for row in st.session_state.google_map_urls if row["id"] != item["id"]
                ]
                st.rerun()

    add_col, _ = st.columns([1, 4])
    with add_col:
        if st.button("+", use_container_width=True):
            st.session_state.google_map_urls.append({"id": uuid4().hex, "url": ""})
            st.rerun()

    run_button = st.button("Jalankan")

if run_button:
    urls = parse_urls("\n".join(row["url"] for row in st.session_state.google_map_urls))

    if not urls:
        st.error("Minimal isi 1 URL Google Maps yang valid.")
        st.stop()

    if not APIFY_TOKEN:
        st.error("APIFY_TOKEN belum ada. Isi dulu file .env kamu.")
        st.stop()

    with st.spinner("Mengambil review dari Apify..."):
        try:
            result = run_google_maps_reviews_scraper(
                api_token=APIFY_TOKEN,
                place_urls=urls,
                keywords=keyword,
            )
        except Exception as exc:
            st.error(f"Gagal menjalankan Apify: {exc}")
            st.stop()

    st.subheader("Input yang dipilih")
    st.write("Keyword:", keyword)
    st.write("Jumlah lokasi:", len(urls))
    if urls:
        st.write("Daftar URL:")
        for url in urls:
            st.markdown(f"- `{url}`")
    st.code(json.dumps({"keyword": keyword, "urls": urls}, indent=2), language="json")
    st.success("Scraping selesai.")
    st.write("Dataset ID:", result["dataset_id"])
    st.write("Raw JSON:", result["raw_file"])
    st.write("Total review mentah:", len(result["raw_items"]))
    st.write("Total review yang cocok filter:", len(result["filtered_items"]))

    st.subheader("Review yang cocok")
    if result["filtered_items"]:
        st.dataframe(result["filtered_items"], use_container_width=True)
    else:
        st.info("Belum ada review yang cocok dengan keyword filter.")
else:
    st.info("Isi keyword dan klik + untuk menambah link lokasi, lalu klik 'Jalankan'.")
