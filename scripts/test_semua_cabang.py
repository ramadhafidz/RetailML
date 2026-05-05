import os
import sys

import pandas as pd

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from column_mapper_lokal import standardize_dataframe

SAMPLE_DIR = os.path.join(ROOT_DIR, "sample_data")
OUTPUT_DIR = os.path.join(ROOT_DIR, "hasil_data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "bersih_semua_cabang.csv")

# 1. Pastikan folder hasil_data dibuat
os.makedirs(OUTPUT_DIR, exist_ok=True)

csv_files = sorted(f for f in os.listdir(SAMPLE_DIR) if f.endswith(".csv"))
cleaned_frames = []

print(f"Menemukan {len(csv_files)} file CSV di folder 'sample_data'...\n")

for file in csv_files:
    path = os.path.join(SAMPLE_DIR, file)
    print(f"{'=' * 60}")
    print(f" Memproses: {file}")
    print(f"{'=' * 60}")

    # A. Baca data kotor
    df_raw = pd.read_csv(path)

    # B. Proses standarisasi dan cleansing via ML Engine
    df_clean = standardize_dataframe(df_raw, filename=file)

    cleaned_frames.append(df_clean)

    print(f"[OK] Berhasil diproses: {file}")
    print(f"     Jumlah baris valid: {len(df_clean)}")
    print("\n[PREVIEW 3 BARIS PERTAMA]")
    print(
        df_clean[["product_id", "product_name", "price", "stock", "category"]]
        .head(3)
        .to_string(index=False)
    )
    print("\n")

df_final = pd.concat(cleaned_frames, ignore_index=True) if cleaned_frames else pd.DataFrame(columns=["product_id", "product_name", "price", "stock", "category"])
df_final.to_csv(OUTPUT_FILE, index=False)

print(f"[OK] Semua hasil telah digabung dan disimpan ke: {OUTPUT_FILE}")
print(f"     Total baris valid: {len(df_final)}")
