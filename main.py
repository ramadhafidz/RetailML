import io

import functions_framework
import pandas as pd
from google.cloud import storage

# Mengimpor fungsi ML dari file engine kita
from column_mapper import standardize_dataframe


# Fungsi ini otomatis dipanggil oleh GCP setiap ada file masuk ke GCS (Cloud Storage)
@functions_framework.cloud_event
def process_new_csv(cloud_event):
    # 1. Buka paket event dari GCP untuk tahu nama file yang baru di-upload
    data = cloud_event.data
    bucket_name = data["bucket"]
    file_name = data["name"]

    print(f"Ada file baru masuk: {file_name} di bucket {bucket_name}")

    # 2. Download file CSV tersebut dari Google Cloud Storage
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    # Gunakan get_blob untuk mengambil metadata dari server
    blob = bucket.get_blob(file_name)
    csv_bytes = blob.download_as_bytes()

    # Ekstrak metadata pengunggah
    uploader = "unknown"
    if blob.metadata and "uploaded_by" in blob.metadata:
        uploader = blob.metadata["uploaded_by"]

    # 3. Baca dengan Pandas
    df_mentah = pd.read_csv(io.BytesIO(csv_bytes))

    # 4. KASIH KE MESIN ML KITA!
    print("Memulai proses Schema Matching & Cleansing...")
    df_bersih = standardize_dataframe(df_mentah, filename=file_name)
    
    # Masukkan metadata pengunggah ke dataframe sebelum masuk Data Warehouse
    df_bersih["uploaded_by"] = uploader

    # 5. Kirim hasilnya langsung ke BigQuery
    print("Mengirim data bersih ke BigQuery...")
    # Menulis ke project `datawarehouse-493606` seperti di backend
    df_bersih.to_gbq("datawarehouse-493606.retail_warehouse.integrated_retail_data", if_exists="append")

    print("Proses ETL selesai!")
