from collections import Counter
import html
from pathlib import Path
import json
import sys
from uuid import uuid4

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.apify_runner import run_google_maps_reviews_scraper
from src.config import APIFY_TOKEN
from src.input_parser import parse_urls


st.set_page_config(page_title="Google Maps Review Scraper", layout="wide")

st.markdown(
    """
    <style>
      :root {
        --bg: #0b1220;
        --panel: rgba(15, 23, 42, 0.86);
        --panel-strong: rgba(15, 23, 42, 0.96);
        --border: rgba(148, 163, 184, 0.16);
        --text: #e5eef9;
        --muted: #8ea0b8;
        --accent: #22c55e;
        --accent-2: #60a5fa;
        --warning: #f59e0b;
        --danger: #ef4444;
      }

      .hero {
        padding: 1.5rem 1.7rem;
        border-radius: 1.4rem;
        background:
          radial-gradient(circle at top right, rgba(96,165,250,0.22), transparent 28%),
          radial-gradient(circle at left, rgba(34,197,94,0.12), transparent 24%),
          linear-gradient(135deg, rgba(9,14,26,1), rgba(16,24,40,1));
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 24px 80px rgba(0, 0, 0, 0.35);
        margin-bottom: 1rem;
      }
      .hero h1 {
        margin: 0;
        color: #f8fafc;
        font-size: 2.15rem;
        line-height: 1.1;
      }
      .hero p {
        margin: 0.45rem 0 0 0;
        color: #cbd5e1;
        max-width: 900px;
      }
      .panel {
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 1rem;
        padding: 1rem 1.1rem;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.18);
      }
      .status-bar {
        display: flex;
        align-items: center;
        gap: 0.7rem;
        padding: 0.9rem 1rem;
        border-radius: 999px;
        background: rgba(15, 23, 42, 0.92);
        border: 1px solid rgba(148, 163, 184, 0.16);
        color: #dbeafe;
      }
      .status-dot {
        width: 10px;
        height: 10px;
        border-radius: 999px;
        background: var(--accent);
        box-shadow: 0 0 0 6px rgba(34, 197, 94, 0.14);
        flex: none;
      }
      .status-dot.pending {
        background: var(--warning);
        box-shadow: 0 0 0 6px rgba(245, 158, 11, 0.14);
      }
      .status-dot.error {
        background: var(--danger);
        box-shadow: 0 0 0 6px rgba(239, 68, 68, 0.14);
      }
      .badge {
        display: inline-block;
        padding: 0.25rem 0.55rem;
        border-radius: 999px;
        border: 1px solid rgba(148,163,184,0.2);
        background: rgba(30, 41, 59, 0.9);
        color: #dbeafe;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 0.35rem;
      }
      .badge.green {
        background: rgba(34,197,94,0.16);
        color: #86efac;
        border-color: rgba(34,197,94,0.24);
      }
      .badge.blue {
        background: rgba(96,165,250,0.16);
        color: #93c5fd;
        border-color: rgba(96,165,250,0.24);
      }
      .badge.yellow {
        background: rgba(245,158,11,0.16);
        color: #fcd34d;
        border-color: rgba(245,158,11,0.24);
      }
      .badge.red {
        background: rgba(239,68,68,0.16);
        color: #fca5a5;
        border-color: rgba(239,68,68,0.24);
      }
      .review-card {
        padding: 1rem 1.05rem;
        border-radius: 1rem;
        border: 1px solid rgba(148, 163, 184, 0.16);
        background: linear-gradient(180deg, rgba(15,23,42,0.98), rgba(12,18,30,0.98));
        margin-bottom: 0.8rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.18);
      }
      .review-head {
        display: flex;
        justify-content: space-between;
        gap: 0.75rem;
        align-items: start;
        margin-bottom: 0.55rem;
      }
      .review-title {
        color: #f8fafc;
        font-size: 1.05rem;
        font-weight: 800;
        line-height: 1.25;
      }
      .review-meta {
        color: var(--muted);
        font-size: 0.88rem;
      }
      .review-text {
        color: #e2e8f0;
        line-height: 1.6;
        margin-top: 0.55rem;
      }
      .review-foot {
        margin-top: 0.8rem;
        color: #94a3b8;
        font-size: 0.82rem;
        border-top: 1px solid rgba(148, 163, 184, 0.12);
        padding-top: 0.65rem;
      }
      .stat-label {
        color: #94a3b8;
        font-size: 0.84rem;
      }
      .stat-value {
        color: #f8fafc;
        font-size: 1.4rem;
        font-weight: 800;
        margin-top: 0.15rem;
      }
      .summary-card {
        padding: 0.95rem 1rem;
        border-radius: 1rem;
        background: rgba(15,23,42,0.9);
        border: 1px solid rgba(148, 163, 184, 0.16);
      }
    </style>
    """,
    unsafe_allow_html=True,
)


def _review_text(item: dict) -> str:
    return str(item.get("textTranslated") or item.get("text") or "").strip()


def _review_rating(item: dict) -> str:
    rating = item.get("stars")
    return f"{rating}/5" if rating is not None else "-"


def _review_date(item: dict) -> str:
    return str(item.get("publishedAtDate") or item.get("publishAt") or "-")


def _reviewer_name(item: dict) -> str:
    return str(item.get("name") or "Anonim")


def _place_name(item: dict) -> str:
    return str(item.get("title") or item.get("categoryName") or "Lokasi")


def _render_badge(text: str, tone: str = "blue") -> None:
    st.markdown(f'<span class="badge {tone}">{text}</span>', unsafe_allow_html=True)


def _render_review_card(item: dict, index: int) -> None:
    text = _review_text(item)
    text_preview = text if len(text) <= 320 else f"{text[:320].rstrip()}..."
    reviewer_name = html.escape(_reviewer_name(item))
    rating = _review_rating(item)
    published_at = _review_date(item)
    place_name = html.escape(_place_name(item))
    place_id = html.escape(str(item.get("placeId") or "-"))
    url = html.escape(str(item.get("reviewUrl") or item.get("url") or "-"))
    likes = item.get("likesCount")
    origin = item.get("reviewOrigin") or "-"
    image_count = len(item.get("reviewImageUrls") or [])

    with st.container():
        st.markdown(
            f"""
            <div class="review-card">
              <div class="review-head">
                <div>
                  <div class="review-title">{reviewer_name}</div>
                  <div class="review-meta">{place_name}</div>
                </div>
                <div class="review-meta" style="text-align:right;">
                  #{index + 1}<br/>
                  {html.escape(published_at)}
                </div>
              </div>
              <div>
                <span class="badge green">Rating {rating}</span>
                <span class="badge blue">{origin}</span>
                <span class="badge yellow">{likes if likes is not None else 0} likes</span>
                <span class="badge red">{image_count} images</span>
              </div>
              <div class="review-text">{html.escape(text_preview) if text_preview else "<i>Tidak ada teks review.</i>"}</div>
              <div class="review-foot">
                placeId: {place_id}<br/>
                reviewUrl: {url}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _append_log(log_lines: list[tuple[str, str]], level: str, message: str) -> None:
    log_lines.append((level, message))


def _render_log_panel(log_lines: list[tuple[str, str]]) -> None:
    if not log_lines:
        st.markdown("- Log belum ada.")
        return

    rendered = []
    for level, message in log_lines:
        rendered.append(f"- **{level}** {message}")
    st.markdown("\n".join(rendered))


def _unique_place_counts(items: list[dict]) -> list[tuple[str, int]]:
    counter = Counter()
    for item in items:
        key = item.get("title") or item.get("placeId") or "Lokasi"
        counter[str(key)] += 1
    return counter.most_common(8)


if "google_map_urls" not in st.session_state:
    st.session_state.google_map_urls = [{"id": uuid4().hex, "url": ""}]

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "last_input" not in st.session_state:
    st.session_state.last_input = None

if "last_log" not in st.session_state:
    st.session_state.last_log = []

st.markdown(
    """
    <div class="hero">
      <h1>Google Maps Review Scraper</h1>
      <p>Scrape review, simpan cache lokal, dan tampilkan hasil dengan kartu yang lebih enak dibaca. Gunakan tombol refresh hanya saat kamu ingin paksa update data.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.header("Input Pencarian")
    keyword = st.text_input("Keyword filter", value="beat")
    max_reviews_per_place = st.number_input(
        "Max review per lokasi", min_value=1, max_value=100000, value=1000, step=100
    )
    use_cache = st.checkbox("Gunakan cache lokal", value=True)
    force_refresh = st.checkbox("Paksa refresh Apify", value=False)
    st.caption("Kalau refresh aktif, cache akan diabaikan saat proses normal. Kalau Apify gagal, fallback cache tetap dipakai bila ada.")
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

    run_button = st.button("Jalankan", use_container_width=True, type="primary")
    st.markdown("</div>", unsafe_allow_html=True)

if run_button:
    urls = parse_urls("\n".join(row["url"] for row in st.session_state.google_map_urls))
    log_lines: list[tuple[str, str]] = []

    if not urls:
        st.error("Minimal isi 1 URL Google Maps yang valid.")
        st.stop()

    if not APIFY_TOKEN:
        st.error("APIFY_TOKEN belum ada. Isi dulu file .env kamu.")
        st.stop()

    _append_log(log_lines, "PENDING", "Request diproses ke Apify.")
    log_placeholder = st.empty()
    log_placeholder.markdown("### Progress Log\n- **PENDING** Request diproses ke Apify.")

    with st.spinner("Mengambil review dari Apify..."):
        try:
            result = run_google_maps_reviews_scraper(
                api_token=APIFY_TOKEN,
                place_urls=urls,
                keywords=keyword,
                max_reviews_per_place=int(max_reviews_per_place),
                use_cache=use_cache and not force_refresh,
            )
        except Exception as exc:
            _append_log(log_lines, "ERROR", f"Gagal total: {exc}")
            st.session_state.last_log = log_lines
            st.error(f"Gagal menjalankan Apify: {exc}")
            st.stop()

    status_code = int(result.get("status_code", 200))
    status_label = str(result.get("status_label", "200 OK"))
    status_message = str(result.get("status_message", "Selesai"))

    if result.get("fallback_used"):
        _append_log(log_lines, "FALLBACK", status_message)
    else:
        _append_log(log_lines, status_label, status_message)

    log_placeholder.markdown(
        "### Progress Log\n" + "\n".join(f"- **{lvl}** {msg}" for lvl, msg in log_lines)
    )

    st.session_state.last_result = result
    st.session_state.last_input = {
        "keyword": keyword,
        "urls": urls,
        "max_reviews": int(max_reviews_per_place),
        "use_cache": use_cache,
        "force_refresh": force_refresh,
    }
    st.session_state.last_log = log_lines
    st.session_state.last_status_code = status_code
    st.session_state.last_status_label = status_label
    st.session_state.last_status_message = status_message

result = st.session_state.last_result
last_input = st.session_state.last_input

if result and last_input:
    from_cache = bool(result.get("from_cache"))
    fallback_used = bool(result.get("fallback_used"))
    last_log = st.session_state.last_log or []
    status_code = int(result.get("status_code", 200))
    status_label = str(result.get("status_label", "200 OK"))
    status_message = str(result.get("status_message", "Selesai"))
    source_label = "cache lokal" if from_cache else "Apify"

    if fallback_used:
        st.warning("Apify gagal, lalu dashboard otomatis pakai cache lokal sebagai fallback.")
    elif from_cache:
        st.info("Menggunakan cache lokal. Tidak hit Apify lagi.")
    else:
        st.success("Scraping selesai dan data baru sudah disimpan.")

    st.markdown(
        f"""
        <div class="status-bar">
          <span class="status-dot {'pending' if status_code == 206 else ''}"></span>
          <div>
            <strong>{status_label}</strong>
            <span style="color:#94a3b8;">{status_message}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Ringkasan")
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(
        f'<div class="summary-card"><div class="stat-label">Keyword</div><div class="stat-value">{last_input["keyword"]}</div></div>',
        unsafe_allow_html=True,
    )
    c2.markdown(
        f'<div class="summary-card"><div class="stat-label">Jumlah lokasi</div><div class="stat-value">{len(last_input["urls"])}</div></div>',
        unsafe_allow_html=True,
    )
    c3.markdown(
        f'<div class="summary-card"><div class="stat-label">Review mentah</div><div class="stat-value">{len(result["raw_items"])}</div></div>',
        unsafe_allow_html=True,
    )
    c4.markdown(
        f'<div class="summary-card"><div class="stat-label">Review cocok filter</div><div class="stat-value">{len(result["filtered_items"])}</div></div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.35, 1])
    with left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.write("Dataset ID:", result["dataset_id"])
        st.write("Raw JSON:", result["raw_file"])
        st.write("Latest review date:", result.get("latest_review_date") or "-")
        st.write("Source:", source_label)
        st.write("Status code:", status_code)
        st.write("Status label:", status_label)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.subheader("Log")
        _render_log_panel(last_log)
        st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("Input yang dipilih", expanded=False):
        st.write("Keyword:", last_input["keyword"])
        st.write("Max review per lokasi:", last_input["max_reviews"])
        st.write("Mode cache:", "aktif" if last_input["use_cache"] else "nonaktif")
        st.write("Paksa refresh:", "ya" if last_input["force_refresh"] else "tidak")
        st.write("Daftar URL:")
        for url in last_input["urls"]:
            st.markdown(f"- `{url}`")
        st.code(json.dumps(last_input, indent=2), language="json")

    overview_tab, filtered_tab, raw_tab = st.tabs(["Overview", "Review cocok", "Semua review"])

    with overview_tab:
        st.subheader("Per Lokasi")
        counts = _unique_place_counts(result["raw_items"])
        if counts:
            cols = st.columns(min(4, len(counts))) if len(counts) > 1 else [st.container()]
            for idx, (place_name, count) in enumerate(counts):
                target = cols[idx % len(cols)] if len(counts) > 1 else cols[0]
                with target:
                    st.markdown(
                        f'<div class="summary-card"><div class="stat-label">Lokasi</div><div class="stat-value" style="font-size:1rem;">{place_name}</div><div class="stat-label">{count} review</div></div>',
                        unsafe_allow_html=True,
                    )
        else:
            st.info("Belum ada data lokasi.")

    with filtered_tab:
        st.subheader("Review yang cocok")
        if result["filtered_items"]:
            for index, item in enumerate(result["filtered_items"]):
                _render_review_card(item, index)
        else:
            st.info("Belum ada review yang cocok dengan keyword filter.")

    with raw_tab:
        st.subheader("Semua review")
        if result["raw_items"]:
            total_reviews = len(result["raw_items"])
            page_size = 8
            max_page = max(1, (total_reviews + page_size - 1) // page_size)
            page = st.number_input("Halaman", min_value=1, max_value=max_page, value=1, step=1)
            start = (int(page) - 1) * page_size
            end = start + page_size
            for index, item in enumerate(result["raw_items"][start:end], start=start):
                _render_review_card(item, index)
        else:
            st.info("Belum ada review mentah.")
else:
    st.info("Isi keyword, tambah URL dengan tombol +, lalu klik 'Jalankan'.")
