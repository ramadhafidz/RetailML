# Tutorial Setup CI/CD: Auto-Deploy ke Google Cloud Functions

Repositori ini telah dilengkapi dengan fitur **Continuous Deployment (CD)** menggunakan GitHub Actions. Artinya, setiap kali Anda melakukan `git push` ke cabang utama (`main`), GitHub akan secara otomatis men-*deploy* kode terbaru Anda ke Google Cloud Functions.

Agar robot GitHub mendapatkan izin (otorisasi) untuk mengelola layanan di Google Cloud Anda, Anda harus memberikan sebuah **Kunci Rahasia (Service Account Key)**. Panduan ini akan menuntun Anda dari nol.

## Langkah 1: Membuat Service Account Key di Google Cloud

> [!NOTE]
> **Penting untuk Kontributor:** Jika Anda bukan pemilik proyek (Owner) atau tidak memiliki peran `Project IAM Admin`, Anda akan menemui *error* **"IAM policy update failed"** saat mencoba menyimpan *role* (Langkah 4). Jika ini terjadi, mintalah teman/pemilik proyek untuk melakukan Langkah 1 ini dan memberikan file JSON-nya kepada Anda.

1. Buka [Google Cloud Console](https://console.cloud.google.com/).
2. Pastikan Anda berada di proyek yang benar (cek menu *dropdown* di bagian atas, pilih `datawarehouse-493606`).
3. Dari menu navigasi kiri, pilih **IAM & Admin** > **Service Accounts**.
4. Klik **+ CREATE SERVICE ACCOUNT** (atau gunakan akun yang sudah ada).
   - *Name*: `github-actions-deployer`
   - *Role/Peran*: Pada tahap kedua, berikan peran **Cloud Functions Developer**, **Service Account User**, dan **Storage Object Viewer**.
5. Setelah *Service Account* terbuat, klik titik tiga di sebelah kanannya, lalu pilih **Manage Keys**.
6. Klik **ADD KEY** > **Create new key**.
7. Pilih format **JSON**, lalu klik **Create**.
8. Sebuah file `.json` akan otomatis terunduh ke komputer Anda. Buka file tersebut menggunakan *Notepad* atau VS Code, lalu **Copy (Salin)** seluruh teks di dalamnya.

> [!WARNING]
> Jangan pernah memberikan atau mengunggah (commit) file JSON ini secara publik. File ini memiliki hak akses level administrator terhadap *resource* Cloud Functions Anda!

---

## Langkah 2: Menyimpan Kunci di GitHub Secrets

1. Buka halaman repositori **RetailML** Anda di [GitHub.com](https://github.com/).
2. Klik tab **Settings** (ikon gir) di repositori tersebut.
3. Di bilah menu sebelah kiri, gulir ke bawah lalu klik **Secrets and variables** > **Actions**.
4. Klik tombol berwarna hijau **New repository secret**.
5. Isi bagian *Name* dengan tulisan berikut (harus persis besar semua):
   ```text
   GCP_CREDENTIALS
   ```
6. *Paste* (Tempel) seluruh isi file JSON yang tadi Anda salin ke kotak besar *Secret*.
7. Klik **Add secret**.

---

## Langkah 3: Pengujian Auto-Deploy

Semuanya sudah siap! Sekarang mari kita pastikan robot tersebut bekerja.

1. Lakukan perubahan kecil pada kode Anda (misalnya menambahkan sebuah komentar di `engine/column_mapper_core.py` atau memperbarui `README.md`).
2. Jalankan perintah Git seperti biasa dari laptop Anda:
   ```bash
   git add .
   git commit -m "chore: uji coba trigger github actions"
   git push origin main
   ```
3. Segera buka halaman repositori GitHub Anda dan klik tab **Actions**.
4. Anda akan melihat sebuah *workflow* berwarna kuning sedang diproses (biasanya memakan waktu 1-3 menit).
5. Jika log selesai dan berubah menjadi ikon **Ceklis Hijau**, selamat! Kode ML Anda berhasil ter-deploy ke infrastruktur serverless Google secara otomatis tanpa perlu menyentuh terminal lagi.

---

## Langkah 4: Memverifikasi Hasil Deployment di Google Cloud Console

Jika *workflow* GitHub Actions telah berstatus **Ceklis Hijau**, Anda dapat memverifikasinya langsung di *dashboard* Google Cloud:

1. Buka [Google Cloud Console](https://console.cloud.google.com/).
2. Di kolom pencarian atas, ketik **"Cloud Run"** (karena Google Cloud Functions Generasi ke-2 berjalan di atas infrastruktur Cloud Run) lalu pilih menu tersebut.
3. Di panel sebelah kiri, klik menu **Services**.
4. Anda akan melihat daftar layanan yang berjalan. Cari baris dengan nama `retail-ml-engine` (seharusnya ada ikon centang hijau di sampingnya yang menandakan layanan sehat).
5. Klik nama `retail-ml-engine` tersebut untuk melihat metrik *dashboard* secara rinci, termasuk jumlah *request*, penggunaan memori, serta tab **Logs** untuk memantau apakah fungsi berhasil memproses CSV saat ada *upload*.
