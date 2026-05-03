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