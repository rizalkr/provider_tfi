import pandas as pd
import re
import os

def clean_text(text):
    if not isinstance(text, str):
        return ""
    # Transformasi ke lowercase
    text = text.lower()
    # Eliminasi karakter non-alfanumerik (emoji, tanda baca ekstrem)
    text = re.sub(r'[^a-z0-9\s]', '', text)
    # Reduksi spasi ganda
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def categorize_complaint(text):
    # Definisi vektor kata kunci berdasarkan anomali operasional Telco
    keywords_pricing = ['mahal', 'harga', 'naik', 'sedot', 'potong', 'kuota', 'pulsa', 'hilang', 'tarif', 'paket']
    keywords_network = ['sinyal', 'lemot', 'jaringan', 'lag', 'rto', 'lelet', 'lambat', 'jelek', 'hilang', 'bapuk', 'ping']
    keywords_system  = ['login', 'error', 'bug', 'crash', 'buka', 'update', 'masuk', 'sistem', 'lagi', 'force close']
    
    categories = []
    
    if any(word in text for word in keywords_pricing):
        categories.append('Pricing/Billing')
    if any(word in text for word in keywords_network):
        categories.append('Network/QoS')
    if any(word in text for word in keywords_system):
        categories.append('App/System')
        
    # Return kategori yang terdeteksi, atau 'General/Other' jika tidak ada korelasi
    return ', '.join(categories) if categories else 'General/Other'

def process_nlp_pipeline(input_csv, output_csv):
    print(f"[*] Memuat data mentah dari: {input_csv}")
    try:
        df = pd.read_csv(input_csv)
    except FileNotFoundError:
        print("[CRITICAL] Berkas input tidak ditemukan.")
        return

    print("[*] Mengeksekusi sanitasi teks dan klasifikasi...")
    
    # Drop data kosong
    df = df.dropna(subset=['content']).copy()
    
    # Terapkan sanitasi
    df['cleaned_content'] = df['content'].apply(clean_text)
    
    # Terapkan fungsi tagging
    df['complaint_category'] = df['cleaned_content'].apply(categorize_complaint)
    
    # Konversi timestamp ke format datetime pandas untuk pemodelan deret waktu
    df['at'] = pd.to_datetime(df['at'])
    
    # Simpan hasil pemrosesan
    df.to_csv(output_csv, index=False)
    
    print(f"[SUCCESS] Pemrosesan NLP selesai. Data diekspor ke: {output_csv}")
    
    # Tampilkan distribusi masalah
    print("\n=== Distribusi Kategori Keluhan ===")
    print(df['complaint_category'].value_counts().head(5).to_string())

if __name__ == "__main__":
    base_dir = "dataset_indosat"
    raw_csv = os.path.join(base_dir, "myim3_reviews_raw.csv")
    cleaned_csv = os.path.join(base_dir, "myim3_reviews_tagged.csv")
    
    process_nlp_pipeline(raw_csv, cleaned_csv)