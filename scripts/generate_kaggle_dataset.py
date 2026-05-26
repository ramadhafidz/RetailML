import os
import csv
import random

# Tentukan path output absolut dari script (mengasumsikan skrip berada di RetailML/scripts)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = os.path.join(BASE_DIR, "sample_data", "kaggle_dataset")

# Data Master (70 produk khas warung/retail Indonesia)
PRODUCTS = [
    ("Indomie Goreng", "Makanan", 3000),
    ("Indomie Kuah Ayam Bawang", "Makanan", 2800),
    ("Indomie Kuah Soto", "Makanan", 2800),
    ("Indomie Kari Ayam", "Makanan", 2800),
    ("Mie Sedap Goreng", "Makanan", 2900),
    ("Beras Ramos 5kg", "Sembako", 65000),
    ("Beras Rojolele 5kg", "Sembako", 67000),
    ("Beras Pandan Wangi 5kg", "Sembako", 70000),
    ("Minyak Bimoli 2L", "Sembako", 35000),
    ("Minyak Filma 2L", "Sembako", 34000),
    ("Minyak Sania 2L", "Sembako", 34500),
    ("Minyak Curah 1L", "Sembako", 16000),
    ("Gula Pasir Gulaku 1kg", "Sembako", 16000),
    ("Gula Curah 1kg", "Sembako", 15000),
    ("Garam Kapal 250g", "Bumbu", 3000),
    ("Garam Refina 250g", "Bumbu", 3500),
    ("Sabun Lifebuoy Merah", "Perawatan Pribadi", 4000),
    ("Sabun Nuvo Biru", "Perawatan Pribadi", 3500),
    ("Sabun Mandi Dettol", "Perawatan Pribadi", 5000),
    ("Sabun Lux Mawar", "Perawatan Pribadi", 4500),
    ("Shampo Clear Sachet", "Perawatan Pribadi", 1500),
    ("Shampo Pantene Sachet", "Perawatan Pribadi", 1500),
    ("Shampo Sunsilk Sachet", "Perawatan Pribadi", 1500),
    ("Shampo Lifebuoy Sachet", "Perawatan Pribadi", 1000),
    ("Pasta Gigi Pepsodent 190g", "Perawatan Pribadi", 12500),
    ("Pasta Gigi Ciptadent 190g", "Perawatan Pribadi", 10000),
    ("Sikat Gigi Formula", "Perawatan Pribadi", 6000),
    ("Kopi Kapal Api Sachet", "Minuman", 1500),
    ("Kopi Luwak White Koffie", "Minuman", 2000),
    ("Kopi ABC Susu", "Minuman", 1500),
    ("Kopi Nescafe Classic", "Minuman", 5000),
    ("Kopi Torabika Susu", "Minuman", 1500),
    ("Teh Celup Sosro", "Minuman", 7000),
    ("Teh Sariwangi Celup", "Minuman", 6500),
    ("Teh Pucuk Harum 350ml", "Minuman", 4000),
    ("Aqua Botol 600ml", "Minuman", 3500),
    ("Aqua Gelas 240ml", "Minuman", 1000),
    ("Aqua Galon", "Minuman", 21000),
    ("Le Minerale 600ml", "Minuman", 3500),
    ("Sprite Botol 390ml", "Minuman", 5000),
    ("Coca Cola Botol 390ml", "Minuman", 5000),
    ("Fanta Merah 390ml", "Minuman", 5000),
    ("Susu Bear Brand", "Minuman", 10500),
    ("Susu Indomilk Sachet", "Minuman", 1500),
    ("Susu Frisian Flag Sachet", "Minuman", 1500),
    ("Susu Dancow Sachet", "Minuman", 3500),
    ("Rokok Gudang Garam Filter", "Rokok", 23000),
    ("Rokok Sampoerna Mild", "Rokok", 30000),
    ("Rokok Djarum Super", "Rokok", 22000),
    ("Rokok Surya 16", "Rokok", 31000),
    ("Rokok Marlboro Merah", "Rokok", 38000),
    ("Bumbu Racik Indofood Nasi Goreng", "Bumbu", 2500),
    ("Bumbu Racik Indofood Sayur Asem", "Bumbu", 2500),
    ("Kecap Bango Pouch 220ml", "Bumbu", 11000),
    ("Kecap ABC Pouch 220ml", "Bumbu", 9500),
    ("Saus Sambal ABC 340ml", "Bumbu", 15000),
    ("Saus Sambal Indofood 340ml", "Bumbu", 14500),
    ("Tepung Terigu Segitiga Biru 1kg", "Sembako", 13000),
    ("Tepung Tapioka Rose Brand 500g", "Sembako", 8000),
    ("Tepung Beras Rose Brand 500g", "Sembako", 7500),
    ("Margarin Blue Band 200g", "Sembako", 9500),
    ("Margarin Forvita 200g", "Sembako", 7000),
    ("Deterjen Rinso Anti Noda 700g", "Pembersih", 22000),
    ("Deterjen Daia 850g", "Pembersih", 18500),
    ("Deterjen Attack Jaz1 800g", "Pembersih", 19000),
    ("Sabun Cuci Piring Sunlight 460ml", "Pembersih", 11000),
    ("Sabun Cuci Piring Mama Lemon 400ml", "Pembersih", 9500),
    ("Pembersih Lantai Super Pell 770ml", "Pembersih", 13500),
    ("Pembersih Lantai Wipol 750ml", "Pembersih", 18000),
    ("Kapur Barus Bagus", "Lainnya", 15000),
    ("Obat Nyamuk Hit Spray", "Lainnya", 35000),
    ("Obat Nyamuk Baygon Bakar", "Lainnya", 6000),
    ("Tisu Paseo 250s", "Lainnya", 18500),
    ("Tisu Tessa 250s", "Lainnya", 17000),
    ("Korek Api Gas Tokai", "Lainnya", 3000),
    ("Baterai ABC Sedang (2 pcs)", "Lainnya", 10000),
    ("Baterai Alkalin AA (2 pcs)", "Lainnya", 15000),
    ("Pembalut Charm Cooling Fresh", "Perawatan Pribadi", 18000),
    ("Pembalut Laurier Relax Night", "Perawatan Pribadi", 20000),
    ("Popok MamyPoko Pants M", "Perawatan Bayi", 55000),
    ("Popok Sweety Bronze Pants L", "Perawatan Bayi", 48000)
]

COLUMN_PROFILES = [
    # Cabang 1-3: Kolom rapi bahasa Inggris
    ["product_id", "product_name", "price", "stock", "category"],
    ["product_id", "product_name", "price", "stock", "category"],
    ["product_id", "product_name", "price", "stock", "category"],
    # Cabang 4-6: Kolom rapi bahasa Indonesia
    ["kode_barang", "nama_produk", "harga_jual", "jumlah_stok", "kategori"],
    ["kode_barang", "nama_produk", "harga_jual", "jumlah_stok", "kategori"],
    ["kode_barang", "nama_produk", "harga_jual", "jumlah_stok", "kategori"],
    # Cabang 7-9: Kolom singkatan ekstrem
    ["kd_brg", "nm_brg", "hrg", "jml", "ktg"],
    ["kd_brg", "nm_brg", "hrg", "jml", "ktg"],
    ["kd_brg", "nm_brg", "hrg", "jml", "ktg"],
    # Cabang 10-12: Kolom penuh typo
    ["prodcut_id", "pruduct_name", "hargaa", "stcok", "katgori"],
    ["prodcut_id", "pruduct_name", "hargaa", "stcok", "katgori"],
    ["prodcut_id", "pruduct_name", "hargaa", "stcok", "katgori"],
    # Cabang 13-15: Kolom format database legacy
    ["tbl_product_id", "nama_lengkap_produk", "harga_jual_per_unit", "jumlah_stok_tersedia", "kategori_produk"],
    ["tbl_product_id", "nama_lengkap_produk", "harga_jual_per_unit", "jumlah_stok_tersedia", "kategori_produk"],
    ["tbl_product_id", "nama_lengkap_produk", "harga_jual_per_unit", "jumlah_stok_tersedia", "kategori_produk"],
]

def format_price(base_price):
    r = random.random()
    if r < 0.2:
        return f"Rp {base_price}"
    elif r < 0.4:
        return f"Rp {base_price:,}".replace(",", ".")
    elif r < 0.6:
        return f"{base_price}.00"
    elif r < 0.7:
        return f" {base_price} "
    else:
        return str(base_price)

def format_stock(base_stock):
    r = random.random()
    if r < 0.1:
        return f"{base_stock}.0"
    elif r < 0.2:
        return str(-abs(base_stock) if base_stock != 0 else -1)
    else:
        return str(base_stock)

def generate_datasets():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    for idx, cols in enumerate(COLUMN_PROFILES):
        cabang_no = idx + 1
        filename = f"cabang_{cabang_no:02d}_data.csv"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(cols)
            
            for row_idx in range(1, 1001):
                # Pilih produk acak
                p_name, p_cat, p_price = random.choice(PRODUCTS)
                
                # Base values
                p_id = f"PRD{cabang_no:02d}{row_idx:04d}"
                stock = random.randint(0, 100)
                
                # Masukkan anomali format pada harga dan stok
                price_val = format_price(p_price)
                stock_val = format_stock(stock)
                
                # Masukkan anomali missing values (5% peluang per sel)
                row = [
                    p_id if random.random() > 0.05 else "",
                    p_name if random.random() > 0.05 else "",
                    price_val if random.random() > 0.05 else "",
                    stock_val if random.random() > 0.05 else "",
                    p_cat if random.random() > 0.05 else ""
                ]
                writer.writerow(row)
        
        print(f"Generated: {filepath} (1000 baris)")

if __name__ == '__main__':
    generate_datasets()
