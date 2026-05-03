import pandas as pd
from column_mapper import standardize_dataframe

# --- 1. KONFIGURASI ---
FILE_INPUT = "cabang_cilegon.csv"  # Ganti dengan nama file yang mau diuji
FILE_OUTPUT = "hasil_bersih.csv"

# --- 3. EKSEKUSI UTAMA (CLI) ---
if __name__ == "__main__":
    print(f"=== Memulai Simulasi ETL untuk {FILE_INPUT} ===")
    
    try:
        df_raw = pd.read_csv(FILE_INPUT)
        print(f"\n1. Membaca {len(df_raw)} baris data...")
        
        print("\n2. Melatih model dari contoh alias kolom...")
        df_final, mapping_dict, diagnostics = standardize_dataframe(df_raw, source_file=FILE_INPUT)

        for column, predicted_target, confidence in diagnostics:
            if predicted_target is None:
                print(f"  [ML] '{column}' -> belum yakin (skor: {confidence:.2f})")
            else:
                print(f"  [ML] '{column}' -> cocok dengan -> '{predicted_target}' (skor: {confidence:.2f})")

        print("\n3. Mentransformasi Kolom dan melengkapi skema target...")
        df_final.to_csv(FILE_OUTPUT, index=False)
        print(f"\n✅ SUKSES! Data hasil standarisasi telah disimpan sebagai '{FILE_OUTPUT}'")
        
    except FileNotFoundError:
        print(f"❌ Error: File '{FILE_INPUT}' tidak ditemukan di folder ini.")