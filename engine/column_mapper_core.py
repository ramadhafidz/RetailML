"""
RetailML - Schema Matching Engine (Core)
========================================
Modul inti untuk standarisasi nama kolom CSV secara otomatis.
Menggunakan pendekatan Hybrid berlapis:
  1. Alias Dictionary  (eksak)
  2. Token Hint        (kata kunci dalam nama kolom)
  3. Value Regex       (pola nilai di dalam kolom)
  4. TF-IDF + Logistic Regression (ML fallback)

Entry point utama: standardize_dataframe(df: pd.DataFrame, filename: str) -> pd.DataFrame
"""

import re
from typing import Dict, List, Optional, Set, cast

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

# =============================================================================
# 1. KONFIGURASI TARGET SCHEMA
# =============================================================================

TARGET_COLUMNS = ["product_id", "product_name", "price", "stock", "category"]

# =============================================================================
# 1b. SEMANTIC DICTIONARY — Sinonim Antar-Bahasa
# =============================================================================
# Memetakan sinonim dari bahasa berbeda (Indo ↔ English ↔ singkatan)
# Digunakan sebelum pencocokan untuk normalisasi semantik.

SEMANTIC_SYNONYMS: Dict[str, List[str]] = {
    # product_id synonyms
    "product_id": ["id", "kode", "sku", "barcode", "no", "nomor", "code", "item_code"],
    "sku": ["product_id", "id", "kode", "barcode"],
    "id_barang": ["product_id", "id", "kode_barang"],
    "id_produk": ["product_id", "id", "kode_produk"],
    "sku_code": ["sku", "product_id", "id", "kode"],
    # product_name synonyms  
    "product_name": ["nama", "name", "barang", "item", "description", "desc", "deskripsi"],
    "nama_produk": ["product_name", "nama", "barang"],
    "item_desc": ["product_name", "description", "deskripsi", "nama"],
    "item_name": ["product_name", "nama", "barang"],
    # price synonyms
    "price": ["harga", "cost", "tarif", "nilai", "selling_price", "unit_price"],
    "harga": ["price", "cost", "tarif", "nilai"],
    "harga_jual": ["price", "harga", "selling_price"],
    # stock synonyms
    "stock": ["stok", "qty", "quantity", "jumlah", "inventory", "tersedia", "persediaan"],
    "stok": ["stock", "qty", "jumlah", "inventory"],
    "qty_on_hand": ["stock", "stok", "qty", "quantity", "tersedia"],
    "jumlah_stok": ["stock", "stok", "qty", "jumlah"],
    # category synonyms
    "category": ["kategori", "tipe", "jenis", "type", "group", "grup", "divisi"],
    "kategori": ["category", "tipe", "jenis"],
    "jenis_barang": ["category", "kategori", "jenis"],
}

# =============================================================================
# 2. LAYER 1 — ALIAS DICTIONARY & IGNORE LIST
# =============================================================================

# Kolom yang pasti BUKAN target, langsung skip agar tidak salah tebak oleh ML
IGNORE_COLUMNS: Set[str] = {
    "diskon",
    "discount",
    "potongan",
    "catatan",
    "keterangan",
    "notes",
    "petugas",
    "kasir",
    "lokasi",
    "loc",
    "tanggal",
    "date",
}

ALIAS_DICT: Dict[str, str] = {
    # --- Self-mapping (kolom sudah sesuai target schema) ---
    "product_id": "product_id",
    "product_name": "product_name",
    "price": "price",
    "stock": "stock",
    "category": "category",
    # --- product_id ---
    "id": "product_id",
    "kode": "product_id",
    "kode_produk": "product_id",
    "kode_barang": "product_id",
    "kode_item": "product_id",
    "product_code": "product_id",
    "item_code": "product_id",
    "prod_id": "product_id",
    "item_id": "product_id",
    "article_id": "product_id",
    "ref_id": "product_id",
    "sku": "product_id",
    "sku_code": "product_id",  # BARU: Istilah retail spesifik
    "barcode": "product_id",
    "no": "product_id",
    "nomor": "product_id",
    "nomor_produk": "product_id",
    "id_barang": "product_id",
    "id_produk": "product_id",
    # --- product_name ---
    "nama": "product_name",
    "nama_produk": "product_name",
    "nama_barang": "product_name",
    "nama_item": "product_name",
    "product": "product_name",
    "item": "product_name",
    "barang": "product_name",
    "item_name": "product_name",
    "item_desc": "product_name",  # BARU: Istilah retail spesifik
    "goods_name": "product_name",
    "description": "product_name",
    "deskripsi": "product_name",
    "product_desc": "product_name",
    "item_description": "product_name",
    # --- price ---
    "harga": "price",
    "harga_jual": "price",
    "harga_satuan": "price",
    "harga_beli": "price",
    "cost": "price",
    "selling_price": "price",
    "unit_price": "price",
    "retail_price": "price",
    "sale_price": "price",
    "nilai": "price",
    "tarif": "price",
    # --- stock ---
    "stok": "stock",
    "sisa": "stock",
    "sisa_stok": "stock",
    "jty_on_hand": "stock",  # BARU: Istilah retail spesifik
    "qumlah_stok": "stock",
    "qty": "stock",
    "quantity": "stock",
    "jumlah": "stock",
    "inventory": "stock",
    "tersedia": "stock",
    "available_qty": "stock",
    "kuantitas": "stock",
    # --- category ---
    "kategori": "category",
    "jenis": "category",
    "jenis_barang": "category",
    "jenis_produk": "category",
    "tipe": "category",
    "type": "category",
    "grup": "category",
    "group": "category",
    "divisi": "category",
    "product_type": "category",
    "item_category": "category",
    "product_group": "category",
    "cat": "category",
    # --- Singkatan umum (pastikan tidak lolos ke Layer 3/4) ---
    "prc": "price",
    "stck": "stock",
    "qte": "stock",
    "ctg": "category",
}

# =============================================================================
# 3. LAYER 2 — TOKEN HINTS
#    Dipecah dari nama kolom menjadi token, lalu dicek terhadap kata kunci khas.
#    Token dipilih sengaja SPESIFIK untuk menghindari ambiguitas antar kolom.
# =============================================================================

TOKEN_HINTS: Dict[str, list] = {
    "product_id": ["sku", "barcode"],
    "product_name": ["name", "nama", "barang", "deskripsi"],
    "price": ["price", "harga", "cost", "tarif"],
    "stock": ["stock", "stok", "qty", "quantity", "jumlah", "inventory"],
    "category": ["category", "kategori", "tipe", "jenis", "grup", "divisi"],
}

# =============================================================================
# 4. LAYER 3 — VALUE REGEX
#    Sampling 20 baris pertama untuk mendeteksi pola nilai dalam kolom.
#    Urutan iterasi penting: dari pola paling spesifik ke paling umum.
# =============================================================================

VALUE_PATTERNS: Dict[str, re.Pattern] = {
    # product_id: kode alfanumerik spesifik (misal: PRD-001, SKU123, A-99)
    # Sengaja hanya product_id — 'stock' dan 'price' sama-sama bisa berisi
    # angka bulat sehingga tidak dapat dibedakan secara andal via regex saja.
    # Kasus nama kolom ambigu + nilai angka ditangani Layer 4 (ML).
    "product_id": re.compile(r"^[A-Z]{1,5}[-_]?\d{2,}$", re.IGNORECASE),
}

# =============================================================================
# 5. LAYER 4 — TRAINING CORPUS (TF-IDF + LOGISTIC REGRESSION)
#    Data sintetis yang merepresentasikan variasi nama kolom dunia nyata.
# =============================================================================

_TRAINING_CORPUS = [
    # product_id
    ("product_id", "product_id"),
    ("prod_id", "product_id"),
    ("id_produk", "product_id"),
    ("kode_produk", "product_id"),
    ("sku", "product_id"),
    ("sku_code", "product_id"),  # BARU: Istilah retail spesifik
    ("item_code", "product_id"),
    ("barcode", "product_id"),
    ("product_code", "product_id"),
    ("nomor_produk", "product_id"),
    ("article_id", "product_id"),
    ("ref_id", "product_id"),
    ("item_id", "product_id"),
    ("kode_barang", "product_id"),
    ("kode_item", "product_id"),
    ("product_no", "product_id"),
    # product_name
    ("product_name", "product_name"),
    ("nama_produk", "product_name"),
    ("item_name", "product_name"),
    ("item_desc", "product_name"),  # BARU: Istilah retail spesifik
    ("barang", "product_name"),
    ("description", "product_name"),
    ("deskripsi", "product_name"),
    ("nama_barang", "product_name"),
    ("product_desc", "product_name"),
    ("goods_name", "product_name"),
    ("nama_item", "product_name"),
    ("item_description", "product_name"),
    ("nama", "product_name"),
    ("product_label", "product_name"),
    ("item_nm", "product_name"),  # BARU: Singkatan
    ("prod_nm", "product_name"),  # BARU: Singkatan
    # price
    ("price", "price"),
    ("harga", "price"),
    ("cost", "price"),
    ("selling_price", "price"),
    ("unit_price", "price"),
    ("harga_jual", "price"),
    ("harga_satuan", "price"),
    ("retail_price", "price"),
    ("nilai", "price"),
    ("tarif", "price"),
    ("prc", "price"),  # BARU: Singkatan penting
    ("hrg", "price"),  # BARU: Singkatan
    ("harga_beli", "price"),
    ("sale_price", "price"),
    ("pricing", "price"),
    ("unit_harga", "price"),  # BARU
    ("hg", "price"),  # BARU: Singkatan ultra-pendek
    # stock
    ("stock", "stock"),
    ("stok", "stock"),
    ("qty", "stock"),
    ("qty_on_hand", "stock"),  # BARU: Istilah retail spesifik
    ("quantity", "stock"),
    ("jumlah", "stock"),
    ("inventory", "stock"),
    ("tersedia", "stock"),
    ("sisa_stok", "stock"),
    ("available_qty", "stock"),
    ("jumlah_stok", "stock"),
    ("stck", "stock"),
    ("kuantitas", "stock"),
    ("qte", "stock"),
    ("unit_tersedia", "stock"),
    ("jml", "stock"),  # BARU: Singkatan
    ("jml_stk", "stock"),  # BARU: Singkatan
    ("stk", "stock"),  # BARU: Singkatan
    ("jml_brg", "stock"),  # BARU: Singkatan
    # category
    ("category", "category"),
    ("kategori", "category"),
    ("type", "category"),
    ("tipe", "category"),
    ("jenis", "category"),
    ("group", "category"),
    ("grup", "category"),
    ("divisi", "category"),
    ("product_type", "category"),
    ("item_category", "category"),
    ("product_group", "category"),
    ("jenis_barang", "category"),
    ("cat", "category"),
    ("ctg", "category"),
    ("ktg", "category"),  # BARU: Singkatan
    ("jns", "category"),  # BARU: Singkatan
    # -------------------------------------------------------------------------
    # 🔴 ANOMALI PRIORITAS TINGGI — Singkatan agresif (konteks retail Indonesia)
    # -------------------------------------------------------------------------
    # product_id — singkatan
    ("p_id", "product_id"),
    ("id_prd", "product_id"),
    ("kd_prod", "product_id"),
    ("kd_brg", "product_id"),
    ("kd_item", "product_id"),
    ("no_prod", "product_id"),
    ("no_brg", "product_id"),
    ("pr_id", "product_id"),  # BARU
    # product_name — singkatan
    ("nm_brg", "product_name"),
    ("nm_prod", "product_name"),
    ("nm_item", "product_name"),
    ("prod_nm", "product_name"),
    ("item_nm", "product_name"),
    ("p_name", "product_name"),
    ("p_nm", "product_name"),
    ("nama_brg", "product_name"),
    ("nm", "product_name"),  # BARU
    # price — singkatan
    ("hrg", "price"),
    ("hrg_jl", "price"),
    ("hrg_sat", "price"),
    ("hrg_jual", "price"),
    ("hg", "price"),
    ("pr", "price"),  # BARU
    ("p", "price"),  # BARU: Ultra-pendek
    # stock — singkatan
    ("jml", "stock"),
    ("jml_stk", "stock"),
    ("stk", "stock"),
    ("jml_brg", "stock"),
    ("qty_stk", "stock"),
    ("sisa_stk", "stock"),
    ("qt", "stock"),  # BARU
    ("qnt", "stock"),  # BARU
    # category — singkatan
    ("ktgr", "category"),
    ("ktg", "category"),
    ("jns", "category"),
    ("jns_brg", "category"),
    ("div", "category"),
    ("kat", "category"),
    ("kg", "category"),  # BARU
    # -------------------------------------------------------------------------
    # 🔴 ANOMALI PRIORITAS TINGGI — Typo yang char n-gram kurang tangkap
    # -------------------------------------------------------------------------
    # product_id — typo
    ("prodcut_id", "product_id"),
    ("pruduct_id", "product_id"),
    ("product_di", "product_id"),
    # product_name — typo
    ("prodcut_name", "product_name"),
    ("pruduct_name", "product_name"),
    ("product_nme", "product_name"),
    ("product_nam", "product_name"),
    # price — typo
    ("priice", "price"),
    ("prcie", "price"),
    ("prce", "price"),
    ("hargaa", "price"),
    ("harrga", "price"),
    ("prise", "price"),  # BARU: Typo umum
    # stock — typo
    ("stcok", "stock"),
    ("stoock", "stock"),
    ("stokc", "stock"),
    ("kwantitas", "stock"),
    ("kuantias", "stock"),
    ("quantiti", "stock"),
    ("qaunttity", "stock"),  # BARU
    # category — typo
    ("katgori", "category"),
    ("karegori", "category"),
    ("cateogry", "category"),
    ("categori", "category"),
    ("catagory", "category"),
    ("kategorii", "category"),
    ("kategorry", "category"),  # BARU
    # -------------------------------------------------------------------------
    # 🟡 ANOMALI PRIORITAS SEDANG — Verbose + database/system prefix
    # -------------------------------------------------------------------------
    # product_id — verbose & prefix
    ("tbl_product_id", "product_id"),
    ("f_product_id", "product_id"),
    ("kode_unik_produk", "product_id"),
    ("id_unik_produk", "product_id"),
    ("product_id_utama", "product_id"),
    ("nomor_kode_produk", "product_id"),
    ("identifier_produk", "product_id"),  # BARU
    # product_name — verbose & prefix
    ("nama_lengkap_produk", "product_name"),
    ("full_product_name", "product_name"),
    ("nama_produk_lengkap", "product_name"),
    ("complete_item_name", "product_name"),
    ("deskripsi_lengkap", "product_name"),  # BARU
    # price — verbose & prefix
    ("f_harga_jual", "price"),
    ("tbl_harga", "price"),
    ("harga_jual_per_unit", "price"),
    ("harga_per_unit", "price"),
    ("harga_satuan_produk", "price"),
    ("total_harga_satuan", "price"),
    ("harga_jual_akhir", "price"),  # BARU
    ("harga_retail", "price"),  # BARU
    # stock — verbose & prefix
    ("total_stok_tersedia", "stock"),
    ("jumlah_stok_tersedia", "stock"),
    ("sisa_persediaan", "stock"),
    ("persediaan", "stock"),
    ("stok_tersedia", "stock"),
    ("jumlah_persediaan", "stock"),
    ("total_inventory", "stock"),  # BARU
    ("stok_habis", "stock"),  # BARU: Konteks retail
    # category — verbose & prefix
    ("kategori_produk", "category"),
    ("jenis_produk_utama", "category"),
    ("tipe_barang", "category"),
    ("tipe_produk", "category"),
    ("divisi_produk", "category"),
    ("kelompok_produk", "category"),
    ("golongan_produk", "category"),
    ("kategori_utama", "category"),  # BARU
]

# =============================================================================
# 6. BUILD ML PIPELINE — Dilatih SEKALI saat modul dimuat (stateless cache)
# =============================================================================


def _build_ml_pipeline() -> Pipeline:
    """Melatih pipeline TF-IDF + Logistic Regression dari corpus sintetis."""
    X_train = [text for text, _ in _TRAINING_CORPUS]
    y_train = [label for _, label in _TRAINING_CORPUS]

    pipeline = Pipeline(
        [
            ("tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4))),
            ("clf", LogisticRegression(max_iter=500, C=5.0, solver="lbfgs")),
        ]
    )
    pipeline.fit(X_train, y_train)
    return pipeline


_ML_PIPELINE: Pipeline = _build_ml_pipeline()

# =============================================================================
# 7. FUNGSI-FUNGSI MATCHING INTERNAL
# =============================================================================


def _normalize(col: str) -> str:
    """
    Normalisasi nama kolom sebelum pencocokan:
      - Handle CamelCase  : "NamaProduk"  → "nama_produk"
      - Ganti non-alfanumerik dengan underscore
      - Collapse underscore ganda, strip, dan lowercase
    """
    col = re.sub(r"([a-z])([A-Z])", r"\1_\2", col)  # CamelCase → snake_case
    col = re.sub(r"[^a-zA-Z0-9]+", "_", col.strip())  # non-alphanumeric → _
    col = re.sub(r"_+", "_", col).strip("_")  # collapse & strip _
    return col.lower()


def _match_layer1_alias(norm_col: str) -> Optional[str]:
    """Layer 1: Pencocokan eksak terhadap kamus alias."""
    return ALIAS_DICT.get(norm_col)


def _match_layer2_semantic(norm_col: str) -> Optional[str]:
    """
    Layer 2b: Semantic matching menggunakan synonym dictionary.
    
    Mengatasi masalah sinonim antar-bahasa yang TF-IDF tidak tangkap,
    seperti "harga" (Indonesia) vs "price" (English).
    
    Strategi:
      1. Cek apakah norm_col ada sebagai key di SEMANTIC_SYNONYMS
      2. Jika ada, lihat daftar sinonim dan coba map ke target schema
      3. Prioritas: Jika sinonim matching memberikan hasil yang jelas, pakai itu
    """
    if norm_col not in SEMANTIC_SYNONYMS:
        return None
    
    # Ambil daftar sinonim untuk kolom ini
    synonyms = SEMANTIC_SYNONYMS[norm_col]
    
    # Cek apakah ada sinonim yang bisa langsung di-map
    # Strategi: cari yang paling umum/standar (ada di ALIAS_DICT)
    for synonym in synonyms:
        if synonym in ALIAS_DICT:
            return ALIAS_DICT[synonym]
    
    return None


def _match_layer2_token(norm_col: str) -> Optional[str]:
    """
    Layer 2c: Pencocokan berdasarkan token hint dalam nama kolom.
    Jika ada beberapa kandidat, pilih yang memiliki token hint terpanjang
    untuk mengurangi ambiguitas.
    """
    tokens: Set[str] = set(re.split(r"[_\s]+", norm_col))
    best_target: Optional[str] = None
    best_len: int = 0

    for target, hints in TOKEN_HINTS.items():
        for hint in hints:
            if hint in tokens and len(hint) > best_len:
                best_len = len(hint)
                best_target = target

    return best_target


def _match_layer3_value_regex(series: pd.Series) -> Optional[str]:
    """
    Layer 3: Pencocokan berdasarkan pola nilai dalam kolom.
    Mengambil sampel 20 baris pertama; target diterima jika >= 70% nilai cocok.
    """
    sample = series.dropna().astype(str).head(20)
    if sample.empty:
        return None

    for target, pattern in VALUE_PATTERNS.items():
        match_ratio = sample.apply(lambda v: bool(pattern.match(v.strip()))).mean()
        if match_ratio >= 0.70:
            return target

    return None


def _get_adaptive_threshold(norm_col: str) -> float:
    """
    Hitung threshold secara adaptive berdasarkan panjang kolom.
    
    Logika:
      - Kolom pendek (< 5 karakter): threshold lebih rendah (0.25)
        Contoh: "prc", "hrg", "stk" — singkatan spesifik retail
      - Kolom sedang (5-10): threshold normal (0.35)
        Contoh: "harga", "stok", "kategori"
      - Kolom panjang (> 10): threshold tinggi (0.45)
        Contoh: "harga_jual_per_unit" — semakin panjang, semakin spesifik
    
    Ini mengatasi masalah istilah singkat seperti "prc" (0.1589) yang
    seharusnya lolos tapi tidak karena threshold terlalu tinggi.
    """
    col_len = len(norm_col)
    if col_len < 5:
        return 0.25  # Agresif untuk singkatan (prc, hrg, stk, jml)
    elif col_len <= 10:
        return 0.35  # Moderat untuk nama normal
    else:
        return 0.45  # Ketat untuk nama verbose


def _match_layer4_ml(norm_col: str) -> Optional[str]:
    """
    Layer 4: Prediksi TF-IDF + Logistic Regression.
    Gunakan adaptive threshold berdasarkan panjang nama kolom.
    
    Perubahan dari sebelumnya:
      - Dulu: threshold statis 0.40
      - Sekarang: threshold adaptive 0.25-0.45
    """
    probas = _ML_PIPELINE.predict_proba([norm_col])[0]
    max_proba = probas.max()
    threshold = _get_adaptive_threshold(norm_col)

    if max_proba >= threshold:
        return str(_ML_PIPELINE.classes_[probas.argmax()])
    return None


def _map_column(col_name: str, series: pd.Series) -> Optional[str]:
    """
    Jalankan 5 lapisan pencocokan secara berurutan untuk satu kolom.
    Kembalikan nama kolom target, atau None jika tidak ada yang cocok.
    
    Urutan pencocokan (dari paling akurat ke fallback):
      1. Layer 1: Alias Dictionary (eksak match)
      2. Layer 2b: Semantic Synonyms (sinonim antar-bahasa)
      3. Layer 2c: Token Hints (kata kunci dalam nama)
      4. Layer 3: Value Regex (pola nilai dalam kolom)
      5. Layer 4: TF-IDF ML (fallback dengan threshold adaptive)
    """
    norm = _normalize(col_name)

    if norm in IGNORE_COLUMNS:
        return None  # Bypass semua layer jika kolom ada di ignore list

    return (
        _match_layer1_alias(norm)
        or _match_layer2_semantic(norm)
        or _match_layer2_token(norm)
        or _match_layer3_value_regex(series)
        or _match_layer4_ml(norm)
    )


# =============================================================================
# 8. FUNGSI CLEANSING & ENTRY POINT UTAMA
# =============================================================================


def _cleanse_dataframe(df: pd.DataFrame, filename: str) -> pd.DataFrame:
    """
    Menerapkan aturan pembersihan dan casting tipe data sesuai DATA_DICTIONARY.md
    """
    # 1. Pastikan semua kolom target ada (jika ML gagal map, isi dengan NA)
    for c in TARGET_COLUMNS:
        if c not in df.columns:
            df[c] = pd.NA

    df_clean = df[TARGET_COLUMNS].copy()

    # 2. Cleansing product_id (string, strip, drop baris jika kosong)
    df_clean["product_id"] = df_clean["product_id"].astype("string").str.strip()
    df_clean["product_id"] = df_clean["product_id"].replace(["", "<NA>", "nan"], pd.NA)
    df_clean = df_clean.dropna(subset=["product_id"])

    # 3. Cleansing product_name (string, title case)
    df_clean["product_name"] = (
        df_clean["product_name"].astype("string").str.strip().str.title()
    )

    # 4. Cleansing price (Int64, remove Rp/./, fillna 0)
    def _clean_price(val):
        if pd.isna(val):
            return 0
        if isinstance(val, (int, float)):
            return int(val)
        # Hapus "Rp" dan spasi
        s = str(val).lower().replace("rp", "").replace(" ", "")
        # Potong angka desimal di belakang koma (misal: 15.000,00 -> 15.000)
        s = s.split(",")[0]
        # Hapus titik ribuan
        s = s.replace(".", "")
        try:
            return int(s)
        except ValueError:
            return 0

    df_clean["price"] = df_clean["price"].apply(_clean_price).astype("Int64")

    # 5. Cleansing stock (Int64, numeric, fillna 0)
    def _clean_stock(val):
        if pd.isna(val):
            return 0
        try:
            return int(float(val))  # float() handle string seperti "15.0"
        except (ValueError, TypeError):
            return 0

    df_clean["stock"] = df_clean["stock"].apply(_clean_stock).astype("Int64")

    # 6. Cleansing category (string, title case, fillna "Uncategorized")
    df_clean["category"] = (
        df_clean["category"]
        .fillna("Uncategorized")
        .astype("string")
        .str.strip()
        .str.title()
    )
    df_clean["category"] = df_clean["category"].replace(
        ["", "Nan", "<Na>"], "Uncategorized"
    )

    # 7. Metadata Columns
    df_clean["source_file"] = pd.Series(filename, index=df_clean.index, dtype="string")
    df_clean["processed_at"] = pd.Timestamp.now("UTC")

    return df_clean


def standardize_dataframe(
    df: pd.DataFrame, filename: str = "unknown_file.csv"
) -> pd.DataFrame:
    """
    Terima DataFrame mentah dengan nama kolom sembarang,
    kembalikan DataFrame bersih dengan skema standar Data Warehouse beserta Metadata.

    Args:
        df: DataFrame mentah hasil baca CSV.
        filename: Nama file sumber untuk kolom metadata 'source_file'.

    Returns:
        pd.DataFrame bersih dan sudah di-cast sesuai DATA_DICTIONARY.md.
    """
    mapping: Dict[str, str] = {}
    mapped_targets: Set[str] = set()

    for col in df.columns:
        target = _map_column(col, cast(pd.Series, df[col]))

        if target and target not in mapped_targets:
            mapping[col] = target
            mapped_targets.add(target)

    df_renamed = df.rename(columns=mapping)

    # Masuk ke fase cleansing dan formatting
    return _cleanse_dataframe(df_renamed, filename)
