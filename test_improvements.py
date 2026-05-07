"""
Test script untuk validasi perbaikan Machine Learning Column Mapper.

Menguji 3 perbaikan utama:
1. Semantic Dictionary (sinonim antar-bahasa)
2. Training Corpus Expansion (istilah retail spesifik)
3. Adaptive Threshold (threshold dinamis berdasarkan panjang kolom)
"""

import sys
import pandas as pd
from engine.column_mapper_core import (
    _normalize,
    _match_layer1_alias,
    _match_layer2_semantic,
    _match_layer2_token,
    _match_layer3_value_regex,
    _match_layer4_ml,
    _get_adaptive_threshold,
    _map_column,
)

def test_semantic_matching():
    """Test Layer 2b: Semantic matching untuk sinonim antar-bahasa."""
    print("\n" + "="*70)
    print("TEST 1: SEMANTIC MATCHING (Sinonim Antar-Bahasa)")
    print("="*70)
    
    test_cases = [
        ("harga", "price"),           # Indonesia → English
        ("stok", "stock"),             # Indonesia → English
        ("sku_code", "product_id"),    # Sinonim retail
        ("qty_on_hand", "stock"),      # Sinonim retail
        ("item_desc", "product_name"), # Sinonim retail
    ]
    
    for col_name, expected in test_cases:
        norm = _normalize(col_name)
        result = _match_layer2_semantic(norm)
        status = "✅" if result == expected else "❌"
        print(f"{status} {col_name:20} → {result} (expected: {expected})")


def test_training_corpus():
    """Test Layer 4: ML untuk istilah retail spesifik yang baru ditambahkan."""
    print("\n" + "="*70)
    print("TEST 2: TRAINING CORPUS (Istilah Retail Spesifik)")
    print("="*70)
    
    # Buat dummy series untuk Layer 3
    dummy_series = pd.Series(["test"] * 5)
    
    test_cases = [
        ("sku_code", "product_id"),     # BARU: Ditambahkan ke corpus
        ("qty_on_hand", "stock"),       # BARU: Ditambahkan ke corpus
        ("item_desc", "product_name"),  # BARU: Ditambahkan ke corpus
        ("prc", "price"),               # Singkatan penting
        ("jml", "stock"),               # Singkatan retail
        ("ktg", "category"),            # Singkatan retail
    ]
    
    for col_name, expected in test_cases:
        norm = _normalize(col_name)
        # Coba semua layer
        result = (
            _match_layer1_alias(norm)
            or _match_layer2_semantic(norm)
            or _match_layer2_token(norm)
            or _match_layer3_value_regex(dummy_series)
            or _match_layer4_ml(norm)
        )
        status = "✅" if result == expected else "❌"
        print(f"{status} {col_name:20} → {result} (expected: {expected})")


def test_adaptive_threshold():
    """Test adaptive threshold untuk singkatan pendek."""
    print("\n" + "="*70)
    print("TEST 3: ADAPTIVE THRESHOLD (Threshold Dinamis)")
    print("="*70)
    
    test_cases = [
        ("prc", 0.25),    # Pendek: threshold lebih rendah
        ("hrg", 0.25),    # Pendek: threshold lebih rendah
        ("harga", 0.35),  # Sedang: threshold normal
        ("stok", 0.35),   # Sedang: threshold normal
        ("harga_jual_per_unit", 0.45),  # Panjang: threshold tinggi
    ]
    
    for col_name, expected_threshold in test_cases:
        threshold = _get_adaptive_threshold(col_name)
        status = "✅" if threshold == expected_threshold else "❌"
        print(f"{status} {col_name:25} → threshold={threshold} (expected: {expected_threshold})")


def test_full_mapping():
    """Test full mapping dengan data sampel real."""
    print("\n" + "="*70)
    print("TEST 4: FULL MAPPING (Data Sampel Real)")
    print("="*70)
    
    # Simulasi data CSV dengan kolom yang problematic
    test_data = {
        "prc": [15000, 25000, 12000, None, 18000],
        "hrg_jual": [15000, 25000, 12000, 20000, 18000],
        "harga": [15000, 25000, 12000, 20000, 18000],
        "price": [15000, 25000, 12000, 20000, 18000],
        "jml": [10, 5, 20, 15, 8],
        "qty_on_hand": [10, 5, 20, 15, 8],
        "stok": [10, 5, 20, 15, 8],
        "stock": [10, 5, 20, 15, 8],
        "nm_brg": ["Product A", "Product B", "Product C", "Product D", "Product E"],
        "item_desc": ["Product A", "Product B", "Product C", "Product D", "Product E"],
        "sku_code": ["SKU001", "SKU002", "SKU003", "SKU004", "SKU005"],
        "nama": ["Product A", "Product B", "Product C", "Product D", "Product E"],
    }
    
    df = pd.DataFrame(test_data)
    
    print("\nMenguji mapping setiap kolom:")
    for col in df.columns:
        result = _map_column(col, df[col])
        print(f"  {col:20} → {result}")


def test_problematic_columns():
    """Test kolom-kolom yang sebelumnya problematic."""
    print("\n" + "="*70)
    print("TEST 5: PROBLEMATIC COLUMNS (Kolom yang Sebelumnya Gagal)")
    print("="*70)
    
    dummy_series = pd.Series(["test"] * 5)
    
    problematic = {
        "harga_jual": "price",      # Sebelumnya score 0.0000
        "id_barang": "product_id",  # Sebelumnya score 0.0399
        "sku_code": "product_id",   # Sebelumnya score 0.0559
        "qty_on_hand": "stock",     # Sebelumnya score 0.0362
        "item_desc": "product_name",# Sebelumnya score 0.0381
        "stok_tersedia": "stock",   # Sebelumnya score 0.2196
        "prc": "price",             # Sebelumnya score 0.1589 (kurang lolos)
    }
    
    print("\nTesting kolom yang sebelumnya bermasalah:")
    for col_name, expected in problematic.items():
        result = _map_column(col_name, dummy_series)
        status = "✅" if result == expected else "❌"
        print(f"{status} {col_name:20} → {result:20} (expected: {expected})")


if __name__ == "__main__":
    test_semantic_matching()
    test_training_corpus()
    test_adaptive_threshold()
    test_problematic_columns()
    test_full_mapping()
    
    print("\n" + "="*70)
    print("TESTING SELESAI")
    print("="*70)
