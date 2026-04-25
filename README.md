# Google-Map-Review-Scrapper

Project ini punya 2 bagian:

- `FE` = dashboard lokal pakai Streamlit
- `BE` = logic Python untuk Apify, parsing input, dan nanti filtering review

## Setup

1. Buat virtual environment, lalu aktifkan.
2. Install dependency:

```bash
pip install -r requirements.txt
```

3. Buat file `.env` dari `.env.example`:

```env
APIFY_TOKEN=isi_token_apify_kamu
```

## Menjalankan FE

Frontend dijalankan dari terminal pakai Streamlit.

Kalau di PowerShell Windows, pakai langkah ini:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run src/frontend/app.py
```

Kalau environment sudah aktif, command FE yang disarankan adalah:

```bash
python -m streamlit run src/frontend/app.py
```

Kalau command itu sukses, browser akan terbuka dan menampilkan dashboard lokal.

## Menjalankan BE

Backend saat ini masih berupa script Python sederhana untuk uji logic dan integrasi Apify:

```bash
python src/main.py
```

Kalau `streamlit` tidak dikenali, itu biasanya karena package belum terpasang di environment aktif. Pakai `python -m streamlit run ...` supaya Python yang dipakai pasti dari environment yang sedang aktif.

Catatan:

- Saat ini BE belum berupa server API terpisah
- Nanti kalau sudah masuk tahap produksi, BE bisa kita ubah ke FastAPI supaya FE dan BE benar-benar komunikasi lewat HTTP

## Struktur Folder

- `src/frontend/` - UI dashboard
- `src/backend/` - tempat logic backend nantinya
- `src/` - helper umum seperti config dan parser input
- `data/raw/` - simpan hasil mentah dari Apify
- `data/processed/` - simpan hasil filter
