import os
import re

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

# --- 1. KONFIGURASI ---
TARGET_COLUMNS = ["product_id", "product_name", "price", "stock", "category"]
TRAINING_ALIASES = {
    "product_id": ["product_id", "prod_id", "id_barang", "sku_code", "kode_produk", "kode_barang"],
    "product_name": ["product_name", "p_name", "nama_produk", "item_desc", "nama_barang", "deskripsi_produk"],
    "price": ["price", "prc", "harga_jual", "unit_price", "harga", "nominal"],
    "stock": ["stock", "stok", "stok_tersedia", "qty_on_hand", "jumlah_stok", "qty"],
    "category": ["category", "cat", "kategori_barang", "department", "jenis_produk", "kategori"],
}
TOKEN_HINTS = {
    "product_id": {"id", "kode", "sku", "item", "barang"},
    "product_name": {"name", "nama", "desc", "deskripsi", "brg", "produk"},
    "price": {"price", "harga", "nominal", "jual", "total"},
    "stock": {"stock", "stok", "qty", "sisa", "awal", "tersedia"},
    "category": {"category", "cat", "kategori", "klasifikasi", "department", "segmen"},
}
IGNORE_HINTS = {"note", "catatan", "anomaly", "anomali", "comment", "remark", "remarks", "meta", "metadata"}
MODEL_THRESHOLD = 0.45

# Masukkan nama-nama file kamu di sini (pastikan filenya ada di folder yang sama)
DAFTAR_FILE = [
    "cabang_cilegon.csv",
    "cabang_tangerang.csv",
    "cabang_jakarta.csv",
    "cabang_serang.csv",
    "cabang_bogor.csv",
]
FILE_OUTPUT = "semua_cabang_bersih.csv"

ALIAS_LOOKUP = {}
for target, aliases in TRAINING_ALIASES.items():
    for alias in aliases:
        ALIAS_LOOKUP[re.sub(r"[^a-z0-9]+", "", alias.lower())] = target


def _normalize_text(value):
    return str(value).strip().lower()


def _canonicalize_text(value):
    return re.sub(r"[^a-z0-9]+", "", str(value).strip().lower())


def _tokenize_column_name(column_name):
    normalized = str(column_name).strip().lower().replace("-", "_")
    return [token for token in re.split(r"[^a-z0-9]+", normalized) if token]


def _build_training_examples():
    texts = []
    labels = []
    for target, aliases in TRAINING_ALIASES.items():
        for alias in aliases:
            texts.append(alias)
            labels.append(target)
    return texts, labels


def train_column_model():
    texts, labels = _build_training_examples()
    model = Pipeline(
        steps=[
            ("tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4))),
            ("clf", LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42)),
        ]
    )
    model.fit(texts, labels)
    return model


def build_column_signature(column_name, series=None, max_samples=3):
    parts = [_normalize_text(column_name)]
    if series is not None:
        sample_values = series.dropna().astype(str).head(max_samples).tolist()
        for value in sample_values:
            normalized_value = _normalize_text(value)
            if normalized_value:
                parts.append(normalized_value)
    return " ".join(part for part in parts if part)


def resolve_alias_target(column_name):
    canonical_name = _canonicalize_text(column_name)
    if canonical_name in ALIAS_LOOKUP:
        return ALIAS_LOOKUP[canonical_name], 1.0
    return None, 0.0


def resolve_name_hint(column_name):
    tokens = _tokenize_column_name(column_name)
    if any(token in IGNORE_HINTS for token in tokens):
        return None, 0.0

    best_target = None
    best_score = 0

    for target, hints in TOKEN_HINTS.items():
        score = sum(1 for token in tokens if token in hints)
        if score > best_score:
            best_target = target
            best_score = score

    if best_target is not None and best_score > 0:
        return best_target, min(0.85, 0.55 + (0.1 * best_score))

    return None, 0.0


def resolve_value_hint(series):
    sample_values = [
        _normalize_text(value)
        for value in series.dropna().astype(str).head(5).tolist()
        if _normalize_text(value)
    ]

    if sample_values and sum(1 for value in sample_values if len(value) > 20 or re.search(r"\b(note|catatan|anomaly|anomali)\b", value)) >= 2:
        return None, 0.0

    if not sample_values:
        return None, 0.0

    currency_like = sum(
        1 for value in sample_values if re.search(r"(?:rp\.?|\b\d[\d.]*\b|\b\d+[.,]\d+\b)", value)
    )
    id_like = sum(1 for value in sample_values if re.fullmatch(r"[a-z]{2,}\d+[a-z0-9]*", value.replace(" ", "")))
    numeric_like = sum(1 for value in sample_values if re.fullmatch(r"[0-9]+(?:[.,][0-9]+)?", value.replace(" ", "")))
    category_like = sum(
        1 for value in sample_values if len(value.split()) <= 2 and len(value) <= 18 and not re.search(r"\d", value)
    )

    if id_like >= 2:
        return "product_id", 0.72
    if currency_like >= 2:
        return "price", 0.7
    if numeric_like >= 2:
        return "stock", 0.68
    if category_like >= 3:
        return "category", 0.55

    return None, 0.0


def predict_column_target(model, column_name, series=None):
    if any(token in IGNORE_HINTS for token in _tokenize_column_name(column_name)):
        return None, 0.0

    alias_target, alias_confidence = resolve_alias_target(column_name)
    if alias_target is not None:
        return alias_target, alias_confidence

    name_target, name_confidence = resolve_name_hint(column_name)
    if name_target is not None:
        return name_target, name_confidence

    if series is not None:
        value_target, value_confidence = resolve_value_hint(series)
        if value_target is not None:
            return value_target, value_confidence

    signature = build_column_signature(column_name, series)
    probabilities = model.predict_proba([signature])[0]
    best_index = probabilities.argmax()
    best_target = model.classes_[best_index]
    confidence = float(probabilities[best_index])

    if confidence < MODEL_THRESHOLD:
        return None, confidence

    return best_target, confidence


def standardize_dataframe(df_raw, source_file=None):
    model = train_column_model()
    mapping = {}
    mapped_targets = set()
    diagnostics = []

    ranked_predictions = []
    for column in df_raw.columns:
        predicted_target, confidence = predict_column_target(model, column, df_raw[column])
        diagnostics.append((column, predicted_target, confidence))
        if predicted_target is not None:
            ranked_predictions.append((confidence, column, predicted_target))

    ranked_predictions.sort(reverse=True)

    for confidence, column, predicted_target in ranked_predictions:
        if predicted_target in mapped_targets:
            continue
        mapping[column] = predicted_target
        mapped_targets.add(predicted_target)

    standardized = pd.DataFrame(index=df_raw.index)
    for target in TARGET_COLUMNS:
        standardized[target] = pd.NA

    for source_column, target_column in mapping.items():
        standardized[target_column] = df_raw[source_column]

    if source_file is not None:
        standardized["source_file"] = source_file

    ordered_columns = TARGET_COLUMNS + (["source_file"] if source_file is not None else [])
    standardized = standardized[ordered_columns]
    return standardized, mapping, diagnostics


# --- 3. EKSEKUSI BATCH (BANYAK FILE) ---
if __name__ == "__main__":
    print("=== Memulai Simulasi ETL Batch ===")

    # Tempat untuk menampung data dari semua cabang
    semua_data_cabang = []

    for file_input in DAFTAR_FILE:
        print(f"\n--- Memproses file: {file_input} ---")

        # Cek apakah filenya benar-benar ada di laptop
        if not os.path.exists(file_input):
            print(f"  [!] Lewati: File {file_input} tidak ditemukan.")
            continue

        # 1. Baca File
        df_raw = pd.read_csv(file_input)
        print(f"  > Membaca {len(df_raw)} baris data...")

        # 2. Latih model dari contoh alias kolom lalu standarkan skema
        df_final, mapping_dict, diagnostics = standardize_dataframe(df_raw, source_file=file_input)
        print(f"  > Hasil Mapping AI: {mapping_dict}")
        for column, predicted_target, confidence in diagnostics:
            if predicted_target is None:
                print(f"    - '{column}' -> belum yakin (skor: {confidence:.2f})")
            else:
                print(f"    - '{column}' -> '{predicted_target}' (skor: {confidence:.2f})")

        # 3. Masukkan ke keranjang gabungan
        semua_data_cabang.append(df_final)
        print(f"  > Selesai distandarisasi!")

    # --- 4. MENGGABUNGKAN DAN MENYIMPAN HASIL ---
    print("\n=== Proses Penggabungan (Integration) ===")
    if len(semua_data_cabang) > 0:
        # Gabungkan semua data dari keranjang menjadi satu tabel besar
        df_integrated = pd.concat(semua_data_cabang, ignore_index=True)

        # Simpan sebagai CSV baru
        df_integrated.to_csv(FILE_OUTPUT, index=False)
        print(f"✅ SUKSES! {len(df_integrated)} baris data dari berbagai cabang berhasil digabungkan ke '{FILE_OUTPUT}'")
    else:
        print("❌ Gagal: Tidak ada file yang berhasil diproses.")