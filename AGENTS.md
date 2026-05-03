# Proyek: Retail Data Pipeline - ML Engine (Lokal)

## Peran AI Agent
Bertindaklah sebagai Expert Data Engineer dan Machine Learning Engineer.

## Konteks & Arsitektur Sistem
Folder ini adalah modul independen (Microservice) dari sebuah proyek arsitektur *Decoupled ETL Pipeline*. 
Tugas utama modul di folder ini murni sebagai **"Mesin Transformasi Data"** (Schema Matching). Modul ini menerima file CSV dengan nama kolom yang berantakan, lalu memetakannya secara otomatis menggunakan pendekatan Hybrid: Rule-based (Regex) dan Machine Learning (TF-IDF + Logistic Regression).

Modul ini nantinya akan dipanggil oleh *Backend* terpisah (FastAPI).

*Rencana Deployment (Future Context)*:
Saat ini modul dites di lingkungan lokal. Namun pada tahap akhir, fungsi utama dari modul ini (standardize_dataframe) akan di-deploy sebagai Google Cloud Functions (Serverless). Oleh karena itu, pastikan kodenya bersifat stateless, efisien dalam penggunaan memori (RAM), dan tidak bergantung pada operasi baca/tulis file system lokal di dalam fungsi utamanya. Input dan output harus berupa objek pandas.DataFrame di memori.

## Target Skema Kolom (Data Warehouse)
Output akhir DataFrame harus HANYA berisi kolom berikut:
1. `product_id`
2. `product_name`
3. `price`
4. `stock`
5. `category`

## Aturan Ketat (Strict Rules)
1. **ISOLASI LINGKUNGAN:** Folder ini adalah area lokal. **JANGAN PERNAH** menulis atau mengimpor kode yang berhubungan dengan Google Cloud (GCS/BigQuery/Eventarc) di folder ini.
2. **TANPA UI:** **JANGAN PERNAH** menggunakan Streamlit, React, atau framework UI lainnya di sini. Output murni berada di ranah terminal/CLI dan objek Python.
3. **EFISIENSI RESOURCE:** Kode harus dioptimalkan untuk berjalan di server dengan spesifikasi CPU terbatas. Hindari duplikasi DataFrame yang tidak perlu di memori.
4. **FORMAT OUTPUT:** Fungsi utama (seperti `standardize_dataframe`) harus selalu mengembalikan objek `pandas.DataFrame` yang sudah rapi agar mudah dikonsumsi oleh layanan lain.
5. **JANGAN MERUSAK LOGIKA HYBRID:** Pertahankan alur pencocokan berlapis: (1) Cek Alias Kamus, (2) Cek Token Hint, (3) Cek Value Regex, baru (4) Prediksi TF-IDF.

## Struktur Direktori & Penjelasan File
Agar pengembangan tidak membingungkan, berikut adalah panduan arsitektur file yang ada di dalam folder ini:

- **`engine/column_mapper_core.py`**: Modul Engine Inti (*Core Logic*). Berisi logika hybrid matching (Alias, Token, Regex, ML TF-IDF) dan data cleansing sesuai `DATA_DICTIONARY.md`. File ini murni *stateless* dan menjadi satu-satunya sumber logika ML.
- **`column_mapper.py`**: Wrapper *Production-Ready* untuk GCP/FastAPI. Hanya melakukan import dari `engine/column_mapper_core.py` agar deployment tetap bersih.
- **`column_mapper_lokal.py`**: Wrapper *development* dengan CLI test runner (`if __name__ == "__main__":`) untuk uji cepat di lokal.
- **`scripts/test_semua_cabang.py`**: *Script runner/tester* otomatis. Skrip ini mensimulasikan proses pipeline dengan membaca seluruh file CSV kotor di `sample_data/`, memprosesnya ke engine kita, dan menyimpan hasilnya ke `hasil_data/`.
- **`scripts/generate_data.py`**: Generator data uji (opsional). Membuat file CSV kotor dengan berbagai anomali untuk stres-test engine.
- **`sample_data/`**: Folder *input* berisi CSV mentah dari berbagai cabang (format POS lama, typo, anomali singkatan ekstrem).
- **`hasil_data/`**: Folder *output* berisi CSV yang sudah distandarisasi dan dibersihkan (siap untuk Data Warehouse / BigQuery).
- **`docs/`**: Dokumentasi teknis (contoh: `GCP_DEPLOYMENT.md`, `API_CONTRACT.md`).