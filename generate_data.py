import pandas as pd
import os

os.makedirs('sample_data', exist_ok=True)

# 1. Jakarta: English POS, clean names, messy values
df_jkt = pd.DataFrame({
    'item_code': ['JKT-001', 'JKT-002', 'JKT-003', 'JKT-004', 'JKT-005', None, 'JKT-007', 'JKT-008', 'JKT-009', 'JKT-010'],
    'item_description': ['Beras Premium 5kg', 'Minyak Goreng 2L', 'Sabun Mandi Cair', 'Susu UHT 1L', ' Roti Tawar ', 'Gula Pasir 1kg', 'Teh Botol 350ml', 'Kopi Instan', 'Mie Goreng Ayam', 'Sampo Anti Ketombe'],
    'selling_price': ['Rp 64.500', 'Rp31.500,00', 24000, '18.000', ' Rp 15.000', 17000, 5000, 3000, '3.500,00', 25000],
    'available_qty': [45.0, 12, 80.0, 20, 15, 50, 0, None, 200.5, -5],
    'product_group': ['Food & Beverage', 'Daily Needs', 'Personal Care', 'Food & Beverage', 'Food & Beverage', 'Food & Beverage', 'Beverage', 'Beverage', 'Food & Beverage', 'Personal Care'],
    'notes': ['', '', '', '', 'promo', 'missing id', '', '', '', 'minus']
})
df_jkt.to_csv('sample_data/cabang_jakarta.csv', index=False)

# 2. Bogor: Old Indo POS, aggressive abbrev, NO category column
df_bgr = pd.DataFrame({
    'kd_brg': ['BGR-01', 'BGR-02', 'BGR-03', 'BGR-04', 'BGR-05', '', 'BGR-07', 'BGR-08', 'BGR-09', 'BGR-10'],
    'nm_brg': ['Mie Instan Kari', 'Susu Kental Manis', 'Tepung Terigu 1kg', 'Mentega 200g', 'Kecap Manis 520ml', 'Air Mineral 600ml', 'Air Mineral 1.5L', 'Saus Sambal', 'Biskuit Cokelat', 'Wafer Krim'],
    'hrg_jual': [3000, 'Rp. 12.000', 10500, 7500, 21000.0, 3500, 'Rp6.000', '15.000,00', 9000, 12500],
    'jml_stk': [150, 40, 80, 55, 30, 100, 50, None, 120, 60.5],
    'diskon': [0, 1000, 0, 0, 0, None, None, 0, 500, None]
})
df_bgr.to_csv('sample_data/cabang_bogor.csv', index=False)

# 3. Cilegon: Typos, human errors, messy floats
df_clg = pd.DataFrame({
    'prodcut_id': ['CLG-101', 'CLG-102', 'CLG-103', 'CLG-104', None, 'CLG-106', 'CLG-107', 'CLG-108', 'CLG-109', 'CLG-110'],
    'pruduct_name': ['Sabun Cuci Piring', 'Pembersih Lantai', 'Pengharum Ruangan', ' Sikat Gigi ', ' Pasta Gigi ', 'Shampo Bayi', 'Sabun Mandi Bayi', 'Minyak Telon', 'Bedak Bayi', 'Tisu Basah'],
    'hargaa': [15000, ' Rp12.000', 18000, 5000, 14000, '22.500,50', 17000, 25000, 13500, '15.000'],
    'stcok': [50, 30.0, None, 100, 80, 25, 40, -2, 60, 75],
    'katgori': ['Kebersihan', 'Kebersihan', 'Kebersihan', 'Perawatan', 'Perawatan', 'Perawatan Bayi', 'Perawatan Bayi', 'Perawatan Bayi', 'Perawatan Bayi', 'Perawatan Bayi'],
    'petugas': ['Agus', 'Agus', 'Agus', 'Budi', 'Budi', '', 'Budi', 'Budi', 'Agus', 'Agus']
})
df_clg.to_csv('sample_data/cabang_cilegon.csv', index=False)

# 4. Serang: Verbose database export format
df_srg = pd.DataFrame({
    'tbl_product_id': ['SRG-A01', 'SRG-A02', 'SRG-A03', 'SRG-B01', 'SRG-B02', 'SRG-B03', 'SRG-B04', '', 'SRG-C01', 'SRG-C02'],
    'nama_lengkap_produk': ['Daging Ayam 1kg', 'Daging Sapi 1kg', 'Telur Ayam 1kg', 'Bawang Merah 1kg', 'Bawang Putih 1kg', 'Cabai Merah 1kg', 'Cabai Rawit 1kg', 'Garam Kemasan 500g', 'Sayur Bayam', 'Sayur Kangkung'],
    'harga_jual_per_unit': [45000, 120000, 28000, 'Rp 35.000', 40000, 'Rp50.000,00', 60000, 5000, 3000, 3500],
    'jumlah_stok_tersedia': [20, 15, 50, 40, 35.0, None, 10, 100, 80, 75],
    'kategori_produk': ['Segar', 'Segar', 'Segar', 'Bumbu', 'Bumbu', 'Bumbu', 'Bumbu', 'Bumbu', 'Sayuran', 'Sayuran'],
    'export_date': ['2023-10-01']*10
})
df_srg.to_csv('sample_data/cabang_serang.csv', index=False)

# 5. Tangerang: Extreme abbreviation + messy values
df_tgr = pd.DataFrame({
    'p_id': ['TGR-01', 'TGR-02', 'TGR-03', 'TGR-04', 'TGR-05', 'TGR-06', None, 'TGR-08', 'TGR-09', 'TGR-10'],
    'p_nm': ['Es Krim Cokelat', 'Es Krim Vanilla', 'Nugget Ayam', 'Sosis Sapi', 'Kentang Goreng', 'Bakso Sapi', 'Siomay Ayam', 'Pempek Ikan', 'Yogurt Strawberry', 'Keju Cheddar'],
    'prc': [' 12.000 ', 12000, 'Rp 45.000', 35000, 28000, '32.000,00', 25000, 30000, 8500, 22000],
    'qte': [30.5, 25, 40, None, 50, 35, 20, 15, 45.0, 30],
    'ctg': ['Frozen', 'Frozen', 'Frozen', 'Frozen', 'Frozen', 'Frozen', 'Frozen', 'Frozen', 'Dairy', 'Dairy'],
    'loc': ['Freezer 1', 'Freezer 1', 'Freezer 2', 'Freezer 2', 'Freezer 2', 'Freezer 2', 'Freezer 2', 'Freezer 2', 'Chiller 1', 'Chiller 1']
})
df_tgr.to_csv('sample_data/cabang_tangerang.csv', index=False)

print("Berhasil generate 5 file CSV yang sangat messy.")
