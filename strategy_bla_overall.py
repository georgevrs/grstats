#!/usr/bin/env python3
"""
BLA Overall Strategy Script
===========================

This script orchestrates the three BLA strategies (BLA, BLA_04, BLA_16) and:
1. Calls individual strategy scripts to get their dataframes
2. Implements the exact data processing recipe
3. Creates the final BLA.xlsx with proper structure

Author: ELSTAT DevOps Team
Date: 2025-01-27
"""

import pandas as pd
import numpy as np
import os
import sys
import re
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def run_individual_strategies():
    """
    Run the three individual BLA strategy scripts to generate their Excel files
    """
    print("Running individual BLA strategies...")
    
    strategies = ['strategy_bla.py', 'strategy_bla_04.py', 'strategy_bla_16.py']
    
    for strategy in strategies:
        if os.path.exists(strategy):
            print(f"Running {strategy}...")
            try:
                # Import and run the strategy
                if strategy == 'strategy_bla.py':
                    import strategy_bla
                    strategy_bla.main()
                    print(f"✓ {strategy} completed successfully")
                elif strategy == 'strategy_bla_04.py':
                    import strategy_bla_04
                    strategy_bla_04.main()
                    print(f"✓ {strategy} completed successfully")
                elif strategy == 'strategy_bla_16.py':
                    import strategy_bla_16
                    strategy_bla_16.main()
                    print(f"✓ {strategy} completed successfully")
            except Exception as e:
                print(f"✗ Error running {strategy}: {str(e)}")
                return False
        else:
            print(f"✗ Strategy file {strategy} not found")
            return False
    
    return True

def load_and_merge_data():
    """
    Load the three BLA datasets and merge them according to the exact recipe
    """
    print("Loading and merging BLA datasets...")
    
    try:
        # Load the three datasets
        df_bla = pd.read_excel('assets/prepared/BLA.xlsx')
        df_bla_04 = pd.read_excel('assets/prepared/BLA_04.xlsx')
        df_bla_16 = pd.read_excel('assets/prepared/BLA_16.xlsx')
        
        print(f"✓ Loaded BLA: {df_bla.shape}")
        print(f"✓ Loaded BLA_04: {df_bla_04.shape}")
        print(f"✓ Loaded BLA_16: {df_bla_16.shape}")
        
        # df_bla drop year, month
        df_bla = df_bla.drop(columns=['YEAR', 'MONTH'])
        # df_bla04 drop year, month
        df_bla_04 = df_bla_04.drop(columns=['YEAR', 'MONTH'])
        # df_bla16 drop year, month
        df_bla_16 = df_bla_16.drop(columns=['YEAR', 'MONTH'])
        
        # outer join them on time_period all and frequency
        df_bla_merged = df_bla.merge(df_bla_04, on=['time_period', 'FREQ'], how='outer', suffixes=('', '_04'))
        df_bla_merged = df_bla_merged.merge(df_bla_16, on=['time_period', 'FREQ'], how='outer', suffixes=('', '_16'))
        
        print(f"✓ Merged dataset shape: {df_bla_merged.shape}")
        
        return df_bla_merged
        
    except Exception as e:
        print(f"✗ Error loading/merging data: {str(e)}")
        return None

def apply_codelist_mappings(df):
    """
    Apply codelist mappings to REGION, CATEGORY columns
    """
    print("Applying codelist mappings...")
    
    # Building Categories mapping
    category_mapping = {
        'Unspecified': 'UNSPECIFIED',
        'Manufacturing': 'MANUFACTURING',
        'Agricultural': 'AGRICULTURAL',
        'Offices': 'OFFICES',
        'Educational': 'EDUCATIONAL',
        'Commercial': 'COMMERCIAL',
        'Short stay accommodation (rooms for rent)': 'SHORT_STAY_ACCOMMODATION',
        'Livestock': 'LIVESTOCK',
        'Other': 'OTHER',
        'Residences for communities': 'RESIDENCES_COMMUNITIES',
        'Hotels': 'HOTELS',
        'Health care': 'HEALTH_CARE'
    }
    
    # Apply building categories mapping
    if 'CATEGORY' in df.columns:
        df['CATEGORY'] = df['CATEGORY'].map(category_mapping).fillna('_Z')
        print("✓ Applied building categories mapping")
    
    return df

def process_dataframe(df):
    """
    Process the dataframe according to the exact recipe
    """
    print("Processing dataframe according to recipe...")
    
    # change column position as
    new_order = ['FREQ', 'time_period', 'REGION', 'CATEGORY', 'LICENCES', 'AREA', 'VOLUME', 'NUMBER',
           'ROOMS', 'NEW_DWELLINGS_VOLUME', 'SURFACE', 'IMPROVEMENTS_VOLUME',
            'TOTAL_NUMBER', 'TOTAL_VOLUME', 'URBAN_NUMBER',
           'URBAN_VOLUME', 'SEMI_URBAN_NUMBER', 'SEMI_URBAN_VOLUME',
           'RURAL_NUMBER', 'RURAL_VOLUME']
    
    # Filter to only include columns that exist
    existing_columns = [col for col in new_order if col in df.columns]
    df = df[existing_columns]
    
    df = df.astype('object')  # upcast once, no warnings later
    
    # prepend 4 empty rows
    empty_rows = pd.DataFrame([[pd.NA]*len(df.columns)]*4,
                              columns=df.columns, dtype='object')
    df = pd.concat([empty_rows, df], ignore_index=True)
    
    # write UNIT header row
    df.iloc[0, 0] = 'UNIT'
    
    # list of values of the row of unit
    unit_values = ['_Z', '_Z', '_Z', 'N', 'A', 'V', 'N', 'N', 'V', 'A', 'V', 'N', 'V', 'N', 'V', 'N', 'V', 'N', 'V']
    df.iloc[0, 1:len(unit_values)+1] = unit_values[:len(df.columns)-1]
    
    df.iloc[1, 0] = 'DWELLINGS'
    
    dwellings_values = ['_Z', '_Z', '_Z', '_Z', '_Z', '_Z',  'D', 'DR', 'D', 'D', 'I', '_Z', '_Z', '_Z', '_Z', '_Z', '_Z', '_Z', '_Z']
    df.iloc[1, 1:len(dwellings_values)+1] = dwellings_values[:len(df.columns)-1]
    
    df.iloc[2, 0] = 'URBAN STATUS'
    
    urban_status_values = ['_Z', '_Z', '_Z', '_Z', '_Z', '_Z', '_Z', '_Z', '_Z', '_Z', '_Z', 'ALL', 'ALL', 'URBAN', 'URBAN', 'SEMI_URBAN', 'SEMI_URBAN', 'RURAL', 'RURAL']
    df.iloc[2, 1:len(urban_status_values)+1] = urban_status_values[:len(df.columns)-1]
    
    df.iloc[3, 0] = 'MEASURE'
    
    measure_values = ['_Z', '_Z', '_Z', 'NR', 'M2', 'M3', 'NR', 'NR', 'M3', 'M2', 'M3', 'NR', 'M3', 'NR', 'M3', 'NR', 'M3', 'NR', 'M3']
    df.iloc[3, 1:len(measure_values)+1] = measure_values[:len(df.columns)-1]
    
    # 1) ensure object dtype (avoid future dtype warnings)
    df[['REGION', 'CATEGORY']] = df[['REGION', 'CATEGORY']].astype('object')
    
    # 2) light normalization: trim, collapse spaces, unify dashes, uppercase for matching
    def _norm(s):
        if pd.isna(s): 
            return s
        s = str(s)
        s = s.replace('\u2013', '-').replace('\u2014', '-')   # en/em dash -> hyphen
        s = re.sub(r'\s+', ' ', s).strip()
        return s
    
    REGION_N   = df['REGION'].map(_norm).str.upper()
    CATEGORY_N = df['CATEGORY'].map(_norm).str.upper()
    
    # 3) domain of existing REGION labels (if REGION stores codes/names)
    region_set = set(REGION_N.dropna()[REGION_N.ne('_Z')].unique())
    
    # 4) treat any "regional-looking" CATEGORY as region (case-insensitive):
    #    matches 'REGIONAL', 'REGIONAL UNIT', 'REGION OF' anywhere in the string
    regional_like = CATEGORY_N.str.contains(r'\b(REGIONAL|REGIONAL UNIT|REGION OF)\b', na=False)
    
    # 5) final mask: CATEGORY is non-empty & either equals a known REGION label or looks regional
    mask = CATEGORY_N.notna() & CATEGORY_N.ne('_Z') & (CATEGORY_N.isin(region_set) | regional_like)
    
    # OPTIONAL: only overwrite REGION if it is empty/_Z
    # mask &= REGION_N.isna() | REGION_N.eq('_Z')
    
    # 6) move and zero-out
    # use the normalized original CATEGORY text (not uppercased) for the move
    df.loc[mask, 'REGION'] = df.loc[mask, 'CATEGORY'].map(_norm)
    df.loc[mask, 'CATEGORY'] = '_Z'
    
    # fill in NaN region and Category with _Z
    df['REGION'] = df['REGION'].fillna('_Z')
    df['CATEGORY'] = df['CATEGORY'].fillna('_Z')
    
    # 1) ensure object dtype for safe string ops
    df[['REGION']] = df[['REGION']].astype('object')
    
    # 2) insert REGIONAL_UNIT right after REGION (if not already present)
    reg_idx = df.columns.get_loc('REGION')
    if 'REGIONAL_UNIT' not in df.columns:
        df.insert(reg_idx + 1, 'REGIONAL_UNIT', pd.NA)
    df['REGIONAL_UNIT'] = df['REGIONAL_UNIT'].astype('object')
    
    # 3) detect "regional unit" values currently living in REGION
    mask = (
        df['REGION'].notna() &
        df['REGION'].astype(str).str.contains(r'REGIONAL\s+UNIT\s+OF', case=False, na=False)
    )
    
    # 4) move value to REGIONAL_UNIT and set REGION to '_Z'
    df.loc[mask, 'REGIONAL_UNIT'] = df.loc[mask, 'REGION']
    df.loc[mask, 'REGION'] = '_Z'
    
    # Clean up REGIONAL_UNIT values
    df.loc[mask, 'REGIONAL_UNIT'] = (
        df.loc[mask, 'REGIONAL_UNIT']
          .astype(str)
          .str.replace(r'^\s*REGIONAL\s+UNIT\s+OF\s+', '', regex=True, case=False)
          .str.replace(r'\n\s*', ' ', regex=True)  # Remove newlines and extra spaces
          .str.strip()
    )
    
    # fill in <NA> in REGIONAL_UNIT AS _Z
    df['REGIONAL_UNIT'] = df['REGIONAL_UNIT'].fillna('_Z')
    
    # Now apply regions mapping AFTER regional unit detection
    region_mapping = {
        'REGION OF ATTIKI': 'EL30',
        'REGION OF ANATOLIKI MAKEDONIA,THRAKI': 'EL11',
        'REGION OF KENTRIKI MAKEDONIA': 'EL12',
        'REGION OF DYTIKI MAKEDONIA': 'EL13',
        'REGION OF IPEIROS': 'EL21',
        'REGION OF THESSALIA': 'EL14',
        'REGION OF STEREA ELLADA': 'EL24',
        'REGION OF IONIA NISIA': 'EL22',
        'REGION OF DYTIKI ELLADA': 'EL23',
        'REGION OF PELOPONNISOS': 'EL25',
        'REGION OF VOREIO AIGAIO': 'EL41',
        'REGION OF NOTIO AIGAIO': 'EL42',
        'REGION OF KRITI': 'EL43',
        'Greece, total': 'EL'
    }
    
    # Apply regions mapping
    if 'REGION' in df.columns:
        df['REGION'] = df['REGION'].map(region_mapping).fillna('_Z')
        print("✓ Applied regions mapping")
    
    # Apply regional units mapping to convert full names to codes
    regional_unit_mapping = {
        'KENTRIKOS TOMEAS ATHINON (CENTRAL SECTOR OF ATHENS)': 'KENTRIKOS_TOMEAS_ATHINON',
        'VOREIOS TOMEAS ATHINON (NORTH SECTOR OF ATHENS)': 'VOREIOS_TOMEAS_ATHINON',
        'DYTIKOS TOMEAS ATHINON (WESTERN SECTOR OF ATHENS)': 'DYTIKOS_TOMEAS_ATHINON',
        'NOTIOS TOMEAS ATHINON (SOUTH SECTOR OF ATHENS)': 'NOTIOS_TOMEAS_ATHINON',
        'ANATOLIKI ATTIKI': 'ANATOLIKI_ATTIKI',
        'DYTIKI ATTIKI': 'DYTIKI_ATTIKI',
        'PIREAS': 'PIREAS',
        'NISIA (ISLANDS)': 'NISIA',
        'RODOPI': 'RODOPI',
        'DRAMA': 'DRAMA',
        'EVROS': 'EVROS',
        'KAVALA': 'KAVALA',
        'XANTHI': 'XANTHI',
        'THESSALONIKI': 'THESSALONIKI',
        'IMATHIA': 'IMATHIA',
        'KILKIS': 'KILKIS',
        'PELLA': 'PELLA',
        'SERRES': 'SERRES',
        'KOZANI': 'KOZANI',
        'GREVENA': 'GREVENA',
        'KASTORIA': 'KASTORIA',
        'FLORINA': 'FLORINA',
        'IOANNINA': 'IOANNINA',
        'ARTA': 'ARTA',
        'THESPROTIA': 'THESPROTIA',
        'PREVEZA': 'PREVEZA',
        'LARISA': 'LARISA',
        'KARDITSA': 'KARDITSA',
        'MAGNISIA': 'MAGNISIA',
        'SPORADES': 'SPORADES',
        'TRIKALA': 'TRIKALA',
        'VOIOTIA': 'VOIOTIA',
        'EVOIA': 'EVOIA',
        'FOKIDA': 'FOKIDA',
        'KERKYRA': 'KERKYRA',
        'ZAKYNTHOS': 'ZAKYNTHOS',
        'KEFALLINIA': 'KEFALLINIA',
        'LEFKADA': 'LEFKADA',
        'ACHAIA': 'ACHAIA',
        'ETOLOAKARNANIA': 'ETOLOAKARNANIA',
        'ILEIA': 'ILEIA',
        'ARKADIA': 'ARKADIA',
        'ARGOLIDA': 'ARGOLIDA',
        'KORINTHIA': 'KORINTHIA',
        'LAKONIA': 'LAKONIA',
        'MESSINIA': 'MESSINIA',
        'LIMNOS': 'LIMNOS',
        'SAMOS': 'SAMOS',
        'CHIOS': 'CHIOS',
        'THIRA': 'THIRA',
        'KALYMNOS': 'KALYMNOS',
        'KEA - KYTHNOS': 'KEA_KYTHNOS',
        'KOS': 'KOS',
        'MILOS': 'MILOS',
        'MYKONOS': 'MYKONOS',
        'NAXOS': 'NAXOS',
        'PAROS': 'PAROS',
        'RODOS': 'RODOS',
        'IRAKLEIO': 'IRAKLEIO',
        'LASITHI': 'LASITHI',
        'RETHYMNO': 'RETHYMNO',
        'CHANIA': 'CHANIA',
        'THASOS': 'THASOS',
        'ITHAKI': 'ITHAKI',
        'LESVOS': 'LESVOS',
        'IKARIA': 'IKARIA',
        'SYROS': 'SYROS',
        'ANDROS': 'ANDROS',
        'KARPATHOS': 'KARPATHOS',
        'TINOS': 'TINOS'
    }
    
    # Apply regional units mapping
    if 'REGIONAL_UNIT' in df.columns:
        df['REGIONAL_UNIT'] = df['REGIONAL_UNIT'].map(regional_unit_mapping).fillna('_Z')
        print("✓ Applied regional units mapping")
    
    print("✓ Dataframe processed according to recipe")
    return df

def perform_data_integrity_check(df):
    """
    Perform comprehensive data integrity checks
    """
    print("\n" + "="*60)
    print("DATA INTEGRITY CHECK")
    print("="*60)
    
    issues = []
    warnings = []
    
    # Check for missing values in critical columns
    critical_columns = ['FREQ', 'time_period']
    for col in critical_columns:
        if col in df.columns:
            missing_count = df[col].isna().sum()
            if missing_count > 0:
                issues.append(f"Missing values in {col}: {missing_count}")
    
    # Check for invalid FREQ values (skip header rows)
    if 'FREQ' in df.columns:
        data_rows = df.iloc[4:]['FREQ']
        invalid_freq = data_rows[data_rows.notna()].apply(lambda x: str(x) not in ['M', 'A', '_Z'])
        if invalid_freq.any():
            issues.append(f"Invalid FREQ values found: {data_rows[invalid_freq].unique()}")
    
    # Check for invalid time_period format (more flexible for M01 format)
    if 'time_period' in df.columns:
        # Skip header rows (first 4 rows)
        data_rows = df.iloc[4:]['time_period']
        # Accept both YYYY and YYYY-M01 formats
        invalid_time = data_rows[data_rows.notna()].apply(lambda x: not re.match(r'^\d{4}(-M?\d{2})?$', str(x)))
        if invalid_time.any():
            issues.append(f"Invalid time_period format found: {data_rows[invalid_time].unique()[:5]}")
        
        # Check for non-standard monthly format (M01 instead of 01)
        non_standard_monthly = data_rows[data_rows.notna()].apply(lambda x: re.match(r'^\d{4}-M\d{2}$', str(x)) is not None)
        if non_standard_monthly.any():
            warnings.append(f"Non-standard monthly format found (M01 instead of 01): {data_rows[non_standard_monthly].unique()[:5]}")
    
    # Check for duplicate rows
    duplicate_count = df.duplicated().sum()
    if duplicate_count > 0:
        warnings.append(f"Duplicate rows found: {duplicate_count}")
    
    # Check data types
    numeric_columns = ['LICENCES', 'AREA', 'VOLUME', 'NUMBER', 'ROOMS', 'NEW_DWELLINGS_VOLUME', 
                      'SURFACE', 'IMPROVEMENTS_VOLUME', 'TOTAL_NUMBER', 'TOTAL_VOLUME', 
                      'URBAN_NUMBER', 'URBAN_VOLUME', 'SEMI_URBAN_NUMBER', 'SEMI_URBAN_VOLUME',
                      'RURAL_NUMBER', 'RURAL_VOLUME']
    
    for col in numeric_columns:
        if col in df.columns:
            # Skip header rows
            data_rows = df.iloc[4:][col]
            non_numeric = data_rows[data_rows.notna()].apply(lambda x: not pd.to_numeric(x, errors='coerce') == x)
            if non_numeric.any():
                warnings.append(f"Non-numeric values in {col}: {data_rows[non_numeric].unique()[:3]}")
    
    # Check header row structure
    expected_headers = ['UNIT', 'DWELLINGS', 'URBAN STATUS', 'MEASURE']
    for i, expected in enumerate(expected_headers):
        if df.iloc[i, 0] != expected:
            issues.append(f"Header row {i} mismatch: expected '{expected}', got '{df.iloc[i, 0]}'")
    
    # Print results
    if issues:
        print("❌ CRITICAL ISSUES FOUND:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ No critical issues found")
    
    if warnings:
        print("\n⚠️  WARNINGS:")
        for warning in warnings:
            print(f"  - {warning}")
    else:
        print("\n✅ No warnings")
    
    # Summary statistics
    print(f"\n📊 SUMMARY STATISTICS:")
    print(f"  - Total rows: {len(df)}")
    print(f"  - Total columns: {len(df.columns)}")
    print(f"  - Data rows (excluding headers): {len(df) - 4}")
    
    if 'time_period' in df.columns:
        data_rows = df.iloc[4:]['time_period']
        if data_rows.notna().any():
            time_range = data_rows[data_rows.notna()].astype(str).agg(['min', 'max'])
            print(f"  - Time period range: {time_range['min']} to {time_range['max']}")
    
    if 'FREQ' in df.columns:
        freq_counts = df.iloc[4:]['FREQ'].value_counts()
        print(f"  - Frequency distribution:")
        for freq, count in freq_counts.items():
            print(f"    {freq}: {count}")
    
    return len(issues) == 0

def main():
    """
    Main execution function
    """
    print("="*60)
    print("BLA OVERALL STRATEGY EXECUTION")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    output_file = 'assets/prepared/BLA.xlsx'
    
    # Check if final BLA.xlsx already exists and is properly formatted
    if os.path.exists(output_file):
        try:
            df_existing = pd.read_excel(output_file)
            # Check if it has the expected header structure
            if (len(df_existing) > 4 and 
                df_existing.iloc[0, 0] == 'UNIT' and 
                df_existing.iloc[1, 0] == 'DWELLINGS' and
                df_existing.iloc[2, 0] == 'URBAN STATUS' and
                df_existing.iloc[3, 0] == 'MEASURE'):
                
                print("⚠️  Final BLA.xlsx already exists but needs reprocessing for code mapping")
                print("Proceeding with full reprocessing...")
                # Remove existing file to force reprocessing
                os.remove(output_file)
                print("✓ Removed existing file for reprocessing")
                
        except Exception as e:
            print(f"⚠️  Error reading existing file: {str(e)}")
            print("Proceeding with full data processing...")
    
    # Step 1: Run individual strategies to generate their Excel files
    if not run_individual_strategies():
        print("❌ Failed to run individual strategies. Exiting.")
        return False
    
    # Step 2: Load and merge data
    df_merged = load_and_merge_data()
    if df_merged is None:
        print("❌ Failed to load and merge data. Exiting.")
        return False
    
    # Step 3: Apply codelist mappings
    df_merged = apply_codelist_mappings(df_merged)
    
    # Step 4: Process dataframe according to exact recipe
    df_final = process_dataframe(df_merged)
    
    # Step 5: Save final output
    try:
        df_final.to_excel(output_file, index=False)
        print(f"✓ Final output saved to: {output_file}")
    except Exception as e:
        print(f"❌ Error saving output: {str(e)}")
        return False
    
    # Step 6: Perform data integrity check
    print("\n" + "="*60)
    print("FINAL DATA INTEGRITY CHECK")
    print("="*60)
    
    success = perform_data_integrity_check(df_final)
    
    if success:
        print("\n🎉 BLA Overall Strategy completed successfully!")
        print(f"Final file: {output_file}")
        print(f"Shape: {df_final.shape}")
    else:
        print("\n⚠️  BLA Overall Strategy completed with issues!")
        print("Please review the issues above before proceeding.")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
