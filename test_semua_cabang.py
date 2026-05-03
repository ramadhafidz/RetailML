import pandas as pd
import os
from column_mapper_lokal import standardize_dataframe

# 1. Pastikan folder hasil_data dibuat
os.makedirs('hasil_data', exist_ok=True)

csv_files = [f for f in os.listdir('sample_data') if f.endswith('.csv')]

print(f"Menemukan {len(csv_files)} file CSV di folder 'sample_data'...\n")

for file in csv_files:
    path = os.path.join('sample_data', file)
    print(f"{'='*60}")
    print(f" Memproses: {file}")
    print(f"{'='*60}")
    
    # A. Baca data kotor
    df_raw = pd.read_csv(path)
    
    # B. Proses standarisasi dan cleansing via ML Engine
    df_clean = standardize_dataframe(df_raw, filename=file)
    
    # C. Simpan hasilnya ke folder hasil_data
    output_filename = f"bersih_{file}"
    output_path = os.path.join('hasil_data', output_filename)
    df_clean.to_csv(output_path, index=False)
    
    print(f"[OK] Berhasil diproses dan disimpan ke: {output_path}")
    print(f"     Jumlah baris valid: {len(df_clean)}")
    print("\n[PREVIEW 3 BARIS PERTAMA]")
    print(df_clean[['product_id', 'product_name', 'price', 'stock', 'category']].head(3).to_string(index=False))
    print("\n")
