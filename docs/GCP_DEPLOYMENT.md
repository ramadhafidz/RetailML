# Deployment Guide: Google Cloud Functions (GCF) & Eventarc

Dokumen ini berisi panduan arsitektur dan contoh kode untuk men-deploy ML Engine (`column_mapper.py`) ke Google Cloud Functions secara *serverless*.

## Arsitektur Event-Driven Pipeline

Alur kerja sistem (Decoupled Architecture):
1. **Frontend (React)**: User mengunggah file CSV cabang.
2. **Backend (FastAPI)**: Menerima file dan langsung mengunggahnya ke bucket Google Cloud Storage (GCS) mentah (`gs://retail-raw-zone`).
3. **Eventarc Trigger**: Mendeteksi adanya file baru di bucket GCS dan membangunkan Cloud Function.
4. **Cloud Function (ML Engine)**: Menjalankan `main.py` yang akan mengunduh file, memprosesnya melalui `column_mapper.py`, dan memuat hasilnya ke BigQuery.
5. **BigQuery**: Menyimpan data bersih yang siap dikonsumsi oleh dashboard.

## Struktur Direktori di Cloud Functions

Saat men-deploy ke GCF, struktur file minimalnya seperti ini:

```text
ml-etl-pipeline/
├── main.py                   # Entry point GCF (Event handler & I/O)
├── column_mapper.py          # Wrapper production (import core engine)
├── engine/
│   ├── __init__.py
│   └── column_mapper_core.py # Core ML Engine (TIDAK BOLEH DIUBAH)
└── requirements.txt          # Dependencies
```

> **PENTING:** File `column_mapper_lokal.py`, folder `scripts/`, dan `sample_data/` TIDAK PERLU di-deploy ke GCP karena hanya untuk testing lokal.

## 1. Instalasi Google Cloud CLI (gcloud)

Anda membutuhkan `gcloud` CLI untuk bisa melakukan deploy dari komputer lokal Anda ke GCP.

### 🪟 Windows
1. Unduh penginstal Google Cloud CLI versi terbaru dari [situs resmi Google](https://cloud.google.com/sdk/docs/install#windows).
2. Jalankan file `.exe` yang diunduh.
3. Ikuti instruksi penginstalan di layar, dan setujui saat ada pilihan "Start Google Cloud SDK Shell".
4. Setelah instalasi selesai, terminal akan terbuka. Lakukan otentikasi dengan perintah:
   ```bash
   gcloud auth login
   gcloud config set project datawarehouse-493606
   ```

### 🐧 Linux (Debian/Ubuntu/Pop!_OS)
Buka terminal dan jalankan perintah berikut:
```bash
sudo apt-get update
sudo apt-get install apt-transport-https ca-certificates gnupg curl

# Import public key Google Cloud
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg

# Tambahkan repositori gcloud
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list

# Update & Install
sudo apt-get update && sudo apt-get install google-cloud-cli

# Login dan Set Project
gcloud auth login
gcloud config set project datawarehouse-493606
```

## 2. File `requirements.txt`

Pastikan `requirements.txt` untuk GCF berisi library berikut:

```text
functions-framework==3.*
pandas==2.*
scikit-learn==1.*
google-cloud-storage==2.*
pandas-gbq==0.*
```

## 3. File `main.py` (Entry Point GCP)

File `main.py` bertindak sebagai "Kurir". Ia menangani otentikasi GCP, membaca file dari GCS, memanggil fungsi ML kita, dan menulis ke BigQuery. 

File `column_mapper.py` kita **stateless** dan tidak peduli dari mana data berasal.

```python
import io
import functions_framework
import pandas as pd
from google.cloud import storage

# Mengimpor fungsi ML dari engine inti kita
from column_mapper import standardize_dataframe

# Konfigurasi BigQuery (Sesuaikan dengan project Anda)
PROJECT_ID = "nama-project-gcp-anda"
DATASET_ID = "retail_dw"
TABLE_ID = "integrated_retail_data"
DESTINATION_TABLE = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

@functions_framework.cloud_event
def process_new_csv(cloud_event):
    """
    Fungsi ini otomatis dipanggil oleh Eventarc setiap ada file masuk ke GCS.
    """
    # 1. Ekstrak metadata event dari Cloud Storage
    data = cloud_event.data
    bucket_name = data["bucket"]
    file_name = data["name"]

    print(f"[INFO] Triggered by file: {file_name} in bucket: {bucket_name}")

    # 2. Download file CSV dari GCS ke memory (BytesIO)
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    csv_bytes = blob.download_as_bytes()

    # 3. Load ke Pandas DataFrame
    print("[INFO] Membaca CSV mentah...")
    try:
        df_mentah = pd.read_csv(io.BytesIO(csv_bytes))
    except Exception as e:
        print(f"[ERROR] Gagal membaca CSV {file_name}: {e}")
        return

    # 4. JALANKAN ML ENGINE KITA (Schema Matching & Cleansing)
    print("[INFO] Memulai proses ML Schema Matching & Data Cleansing...")
    try:
        df_bersih = standardize_dataframe(df_mentah, filename=file_name)
    except Exception as e:
        print(f"[ERROR] Engine ML gagal memproses data: {e}")
        return

    # 5. Load hasil bersih ke BigQuery
    print(f"[INFO] Mengirim {len(df_bersih)} baris data bersih ke BigQuery ({DESTINATION_TABLE})...")
    try:
        df_bersih.to_gbq(
            destination_table=DESTINATION_TABLE,
            project_id=PROJECT_ID,
            if_exists="append", # Tambahkan data baru ke tabel yang sudah ada
            location="asia-southeast2" # Sesuaikan region BQ Anda (misal: Jakarta)
        )
        print("[SUCCESS] Pipeline ETL selesai!")
    except Exception as e:
        print(f"[ERROR] Gagal mengirim data ke BigQuery: {e}")

```

## 4. Perintah Deployment (gcloud CLI)

Untuk men-deploy kode di atas ke Google Cloud Functions (Gen 2) yang di-trigger oleh bucket GCS mentah (`retail-raw-zone`), gunakan perintah berikut:

```bash
gcloud functions deploy etl-retail-pipeline \
    --gen2 \
    --runtime=python311 \
    --region=asia-southeast2 \
    --source=. \
    --entry-point=process_new_csv \
    --memory=1024MB \
    --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
    --trigger-event-filters="bucket=retail-raw-zone" \
    --service-account="[SERVICE_ACCOUNT_EMAIL]"
```

*Catatan: Pastikan Service Account yang digunakan memiliki akses pembacaan ke Storage (Storage Object Viewer) dan penulisan ke BigQuery (BigQuery Data Editor).*
