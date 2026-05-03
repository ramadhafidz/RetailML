# Data Dictionary & Cleansing Rules
**Target Table:** `integrated_retail_data` (Google BigQuery)

Dokumen ini berisi standar tipe data dan aturan pembersihan (cleansing rules) untuk output akhir DataFrame sebelum dikirim ke BigQuery atau dikembalikan ke Frontend.

## Target Schema & Rules

| Target Column  | Data Type (Pandas) | BigQuery Type | Cleansing Rules (Wajib Diterapkan) |
| :--- | :--- | :--- | :--- |
| `product_id`   | `string`           | `STRING`      | Wajib diubah ke string. Hapus spasi di awal/akhir (strip). Jika kosong (NaN), drop baris tersebut. |
| `product_name` | `string`           | `STRING`      | Wajib diubah ke string. Hapus spasi berlebih. Terapkan Title Case (contoh: "mie gacoan" -> "Mie Gacoan"). |
| `price`        | `Int64`            | `INTEGER`     | Hapus karakter "Rp", "rp", spasi, titik (.), dan koma (,). Konversi ke tipe integer numerik. Jika gagal/NaN, isi dengan 0. |
| `stock`        | `Int64`            | `INTEGER`     | Konversi ke tipe integer numerik. Pastikan tidak ada angka desimal. Jika kosong (NaN), isi dengan 0. |
| `category`     | `string`           | `STRING`      | Wajib diubah ke string. Terapkan Title Case. Jika kosong (NaN), isi dengan "Uncategorized". |

## Metadata Columns (Auto-generated)
Selain 5 kolom hasil ekstraksi ML di atas, sistem WAJIB menambahkan dua kolom metadata berikut sebelum dikirim:
1. `source_file` (`string`): Mengambil nama file CSV asli yang diunggah (contoh: "cabang_cilegon.csv").
2. `processed_at` (`datetime64[ns]` / `TIMESTAMP`): Waktu saat data berhasil diproses (gunakan UTC).

## Batasan Kode (Coding Constraints)
- Gunakan library `pandas` untuk melakukan casting tipe data.
- Pastikan tidak ada tipe data `object` yang ambigu saat di-export ke JSON atau BigQuery.