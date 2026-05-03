import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import io

# --- 1. KONFIGURASI TARGET SCHEMA ---
TARGET_COLUMNS = ["product_id", "product_name", "price", "stock", "category"]

# --- 2. FUNGSI MACHINE LEARNING (LOKAL) ---
def get_ml_mapping(source_cols):
    mapping = {}
    # Menggunakan N-Gram agar AI peka terhadap singkatan (misal: 'prc' jadi 'price')
    vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 3))
    
    for col in source_cols:
        clean_col = col.lower()
        tfidf_matrix = vectorizer.fit_transform([clean_col] + [t.lower() for t in TARGET_COLUMNS])
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
        best_match_idx = similarities.argmax()
        score = similarities[0][best_match_idx]
        
        # Batas toleransi (threshold) di-set rendah agar bisa menangkap singkatan
        if score > 0.1:
            mapping[col] = TARGET_COLUMNS[best_match_idx]
            
    return mapping

# --- 3. TAMPILAN WEB STREAMLIT ---
st.set_page_config(page_title="Local ETL Simulator", layout="wide")
st.title("💻 Simulator ETL Lokal (Tanpa Cloud)")
st.write("Uji coba logika Machine Learning untuk standarisasi kolom CSV secara offline.")

st.divider()

# Area Upload File
uploaded_file = st.file_uploader("Upload File CSV Cabang (Format Bebas)", type=["csv"])

if uploaded_file is not None:
    # A. Membaca Data Asli
    df_raw = pd.read_csv(uploaded_file)
    
    st.subheader("1. Data Asli (Sebelum Diproses)")
    st.dataframe(df_raw.head(), use_container_width=True)
    
    with st.spinner("AI sedang mencocokkan nama kolom..."):
        # B. Menjalankan Machine Learning
        source_columns = df_raw.columns.tolist()
        mapping_dict = get_ml_mapping(source_columns)
        
        # Menampilkan hasil "pikiran" AI
        st.subheader("2. Hasil Analisis Machine Learning")
        st.write("Kamus Mapping yang dibuat AI:", mapping_dict)
        
        # C. Transformasi Data
        df_transformed = df_raw.rename(columns=mapping_dict)
        
        # Filter hanya kolom yang ada di target schema
        existing_target_cols = [c for c in TARGET_COLUMNS if c in df_transformed.columns]
        df_final = df_transformed[existing_target_cols]
        
        # Tambahkan metadata
        df_final['source_file'] = uploaded_file.name
        df_final['processed_at'] = pd.Timestamp.now()
        
        st.subheader("3. Data Final (Siap Masuk Data Warehouse)")
        if df_final.empty:
            st.error("Gagal! AI tidak bisa mengenali satu pun kolom dari file ini.")
        else:
            st.success("Berhasil distandarisasi!")
            st.dataframe(df_final, use_container_width=True)
            
            # Simulasi tombol simpan (hanya download ke lokal, tidak ke BigQuery)
            csv_data = df_final.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Hasil Standarisasi",
                data=csv_data,
                file_name=f"bersih_{uploaded_file.name}",
                mime="text/csv"
            )