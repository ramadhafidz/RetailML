"""Local development wrapper with CLI test runner."""

import pandas as pd

from engine.column_mapper_core import TARGET_COLUMNS, standardize_dataframe

if __name__ == "__main__":
    test_cases = [
        {
            "label": "Test A — Mixed format (spasi, CamelCase, underscore)",
            "data": {
                "Kode Produk": ["PRD-001", "PRD-002", "PRD-003"],
                "NamaProduk": ["Laptop Asus", "Mouse Logitech", "Keyboard Mech"],
                "Harga_Jual": [12_000_000, 350_000, 850_000],
                "sisa_stok": [15, 200, 75],
                "jenis_barang": ["Elektronik", "Aksesori", "Aksesori"],
            },
        },
        {
            "label": "Test B — Singkatan agresif POS",
            "data": {
                "kd_brg": ["B-001", "B-002", "B-003"],
                "nm_brg": ["Sabun Mandi", "Sampo", "Pasta Gigi"],
                "hrg_jual": [5_000, 18_000, 12_000],
                "jml_stk": [300, 150, 200],
                "jns_brg": ["Perawatan", "Perawatan", "Perawatan"],
            },
        },
        {
            "label": "Test C — Cleansing harga & default category",
            "data": {
                "id_barang": ["ID-01", "", "ID-03", None],
                "nama_barang": ["mie gacoan", " es teh ", "DIMSUM", "Tahu"],
                "harga_rp": ["Rp 15.000", "Rp. 5,000", "12.500,00", None],
                "stok_pcs": ["15.0", "10", None, "5"],
            },
        },
    ]

    for tc in test_cases:
        df_in = pd.DataFrame(tc["data"])
        print("\n" + "=" * 70)
        print(f"  {tc['label']}")
        print("=" * 70)
        print("[INPUT]  Kolom asli  :", df_in.columns.tolist())

        df_out = standardize_dataframe(df_in, filename="local_test.csv")

        print("[OUTPUT] Kolom hasil :", df_out.columns.tolist())
        print("[DTYPES]")
        print(df_out.dtypes.to_string())
        print()
        print(df_out.to_string(index=False))

        missing = [c for c in TARGET_COLUMNS if c not in df_out.columns]
        if missing:
            print(f"\n[PERINGATAN] Kolom tidak terpetakan: {missing}")
        else:
            print(f"\n[OK] Semua {len(TARGET_COLUMNS)} kolom berhasil dipetakan.")
