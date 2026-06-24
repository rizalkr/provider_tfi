import json
import pandas as pd
import os

def extract_packages_from_har(har_filepath, output_csv):
    print(f"[*] Menginisialisasi pemindaian berkas HAR: {har_filepath}")
    
    if not os.path.exists(har_filepath):
        print(f"[ERROR] Berkas {har_filepath} tidak ditemukan.")
        return

    with open(har_filepath, 'r', encoding='utf-8') as f:
        har_data = json.load(f)
        
    entries = har_data['log']['entries']
    master_packages = []
    
    # Definisi tuple endpoint untuk memfilter request
    target_endpoints = ("/api/v2/offer/getlist", "/api/v2/packages/packagelist")
    
    for entry in entries:
        request = entry['request']
        url = request['url']
        
        # Cek apakah URL request mengandung salah satu dari endpoint target
        if any(endpoint in url for endpoint in target_endpoints):
            response = entry['response']
            
            # Ekstraksi tipe endpoint untuk tracking sumber data
            source_api = "offer/getlist" if "getlist" in url else "packages/packagelist"
            
            try:
                response_text = response['content']['text']
                payload = json.loads(response_text)
                
                packages = payload.get('data', {}).get('commercial_package', [])
                
                for pkg in packages:
                    attr = pkg.get('commercial_attribute', {})
                    
                    try:
                        total_mb = float(attr.get('total_data_quota', 0))
                        quota_gb = round(total_mb / 1024, 2) if total_mb > 0 else 0.0
                    except:
                        quota_gb = 0.0
                        
                    master_packages.append({
                        'offer_id': pkg.get('pvr_code'),
                        'package_name': pkg.get('package_name'),
                        'family_name': attr.get('family_name'),
                        'quota_gb': quota_gb,
                        'duration_days': attr.get('duration_month'),
                        'price_rp': int(pkg.get('tariff', 0)),
                        'original_price_rp': int(pkg.get('original_tariff', 0)),
                        'vas_included': pkg.get('package_footer_desc'),
                        'api_source': source_api # Flagging sumber data
                    })
            except Exception:
                continue
                
    if master_packages:
        df = pd.DataFrame(master_packages)
        
        initial_rows = len(df)
        df.drop_duplicates(subset=['offer_id'], keep='first', inplace=True)
        print(f"[*] Filter Duplikasi: {initial_rows} -> {len(df)} paket unik.")
        
        df['price_per_gb'] = round(df['price_rp'] / (df['quota_gb'].apply(lambda x: x if x > 0 else 0.01)), 2)
        
        df.to_csv(output_csv, index=False)
        print(f"[SUCCESS] Master katalog berhasil disusun! File disimpan di: {output_csv}")
    else:
        print("[FAILED] Tidak ditemukan data paket yang valid di berkas HAR.")

if __name__ == "__main__":
    HAR_FILE = "im3_network_log.har"
    OUTPUT_CSV = "im3_master_catalog.csv"
    extract_packages_from_har(HAR_FILE, OUTPUT_CSV)