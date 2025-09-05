#!/usr/bin/env python3
"""
Download and preprocess building permits data from Statbel
"""

import requests
import zipfile
import pandas as pd
from pathlib import Path
import sys

# Add src directory to path  
script_dir = Path(__file__).parent
src_path = script_dir.parent / 'src'
sys.path.insert(0, str(src_path))

try:
    from config import DUTCH_COLUMN_NAMES
except ImportError:
    # Fallback column mapping if config can't be imported
    DUTCH_COLUMN_NAMES = {
        'CD_MUNTY_REFNIS': 'gemeente_code',
        'TX_MUNTY_DESCR_NL': 'gemeente_naam',
        'TX_PROV_DESCR_NL': 'provincie',
        'TX_RGN_DESCR_NL': 'gewest',
        'CD_YEAR': 'jaar',
        'MS_NBR_BUILDING_PERMITS': 'aantal_vergunningen',
        'MS_NBR_NEW_DWELLINGS': 'nieuwe_woningen',
        'MS_NBR_DEMO_DWELLINGS': 'gesloopte_woningen',
        'MS_NBR_RENOV_DWELLINGS': 'gerenoveerde_woningen'
    }

def main():
    """Download and process building permits data"""
    print("📥 Starting data download process...")
    
    # Download and process data
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    
    url = 'https://statbel.fgov.be/sites/default/files/files/opendata/Building%20permits/TF_BUILDING_PERMITS.zip'
    zip_path = data_dir / 'TF_BUILDING_PERMITS.zip'
    output_csv = data_dir / 'building_permits.csv'
    
    print('📥 Downloading building permits data...')
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(zip_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    
    print('📦 Extracting ZIP file...')
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(data_dir)
        extracted_files = zip_ref.namelist()
    
    data_file = None
    for file in extracted_files:
        if file.endswith('.txt'):
            data_file = data_dir / file
            break
    
    if data_file and data_file.exists():
        print(f'📊 Converting {data_file.name} to CSV...')
        df = pd.read_csv(data_file, sep='|', encoding='utf-8', quotechar='"')
        df.columns = [col.strip().strip('"') for col in df.columns]
        
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            if df[col].dtype == 'float64':
                df[col] = df[col].astype('Int64')
        
        df = df.rename(columns=DUTCH_COLUMN_NAMES)
        df.to_csv(output_csv, index=False)
        
        zip_path.unlink()
        data_file.unlink()
        
        print(f'✅ Success! Clean CSV saved as: {output_csv.name}')
        print(f'📊 Data shape: {df.shape[0]:,} rows × {df.shape[1]} columns')
        print(f'📅 Years covered: {df["jaar"].min()} - {df["jaar"].max()}')
    else:
        print('❌ Error: Could not find data file in ZIP archive')
        sys.exit(1)

if __name__ == "__main__":
    main()
