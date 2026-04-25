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

Streamlit sudah dikonfigurasi untuk auto-rerun saat file berubah lewat [.streamlit/config.toml](/c:/Users/nabil/Documents/Projek%20Iseng/Google-Map-Review-Scrapper/.streamlit/config.toml).

Di dashboard kamu bisa:

- isi keyword filter, misalnya `beat` atau `beat 2021`
- tambah beberapa URL Google Maps place pakai tombol `+`
- hapus URL yang salah pakai tombol `-`
- klik `Jalankan` untuk fetch review dari Apify
- hasil lama akan dipakai dari cache lokal kalau input-nya sama, jadi tidak selalu hit API

## Menjalankan BE

Backend saat ini masih berupa script Python sederhana untuk uji logic dan integrasi Apify:

```bash
python src/main.py
```

Kalau `streamlit` tidak dikenali, itu biasanya karena package belum terpasang di environment aktif. Pakai `python -m streamlit run ...` supaya Python yang dipakai pasti dari environment yang sedang aktif.

Catatan:

- Saat ini FE langsung memanggil logic backend Python, jadi belum perlu server API terpisah
- Hasil raw review akan disimpan ke `data/raw/` sebagai JSON
- Review yang cocok dengan keyword akan ditampilkan di dashboard
- Nanti kalau perlu, BE bisa kita ubah ke FastAPI supaya FE dan BE benar-benar komunikasi lewat HTTP

## Struktur Folder

- `src/frontend/` - UI dashboard
- `src/backend/` - tempat logic backend nantinya
- `src/` - helper umum seperti config dan parser input
- `data/raw/` - simpan hasil mentah dari Apify
- `data/cache/` - simpan cache hasil scraping agar tidak hit API berulang
- `data/processed/` - simpan hasil filter
