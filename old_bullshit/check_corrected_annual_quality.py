#!/usr/bin/env python3
"""
QUALITY CHECK FOR CORRECTED ANNUAL LFS DATASET
"""

import pandas as pd

def check_corrected_annual_data():
    """Check the corrected annual LFS dataset."""
    print("🔍 QUALITY CHECK FOR CORRECTED ANNUAL LFS DATASET")
    print("=" * 80)
    
    try:
        # Load the corrected dataset
        df = pd.read_excel('assets/prepared/LFS_annual_CORRECTED.xlsx')
        print(f"✅ Corrected dataset loaded: {len(df):,} records")
        
        # Basic info
        print(f"\n📊 BASIC INFO:")
        print(f"  Total records: {len(df):,}")
        print(f"  Total columns: {len(df.columns)}")
        print(f"  Columns: {list(df.columns)}")
        
        # Column analysis
        print(f"\n🔍 COLUMN ANALYSIS:")
        for col in df.columns:
            non_null = df[col].dropna().nunique()
            null_count = df[col].isna().sum()
            total = len(df)
            print(f"  {col}: {non_null} unique values, {null_count} nulls ({null_count/total*100:.1f}%)")
        
        # Sample data
        print(f"\n📋 SAMPLE DATA (first 10 rows):")
        print(df.head(10).to_string())
        
        # Time period analysis
        print(f"\n⏰ TIME PERIOD ANALYSIS:")
        if 'time_period' in df.columns:
            time_counts = df['time_period'].value_counts()
            print(f"  Total unique time periods: {len(time_counts)}")
            print(f"  Time period range: {time_counts.index.min()} to {time_counts.index.max()}")
            print(f"  Time period distribution:")
            for period, count in time_counts.items():
                print(f"    {period}: {count:,} records")
        else:
            print("  ❌ NO TIME_PERIOD COLUMN!")
        
        # Check for region column
        print(f"\n🌍 REGION ANALYSIS:")
        if 'region' in df.columns:
            region_counts = df['region'].value_counts()
            print(f"  Total unique regions: {len(region_counts)}")
            print(f"  Region distribution:")
            for region, count in region_counts.head(10).items():
                print(f"    {region}: {count:,} records")
        else:
            print("  ❌ REGION COLUMN STILL MISSING!")
            print("  🔍 Looking for region-related columns...")
            region_related = [col for col in df.columns if 'region' in col.lower() or 'area' in col.lower()]
            if region_related:
                print(f"    Found region-related columns: {region_related}")
            else:
                print("    No region-related columns found")
        
        # Check for missing dimensions
        print(f"\n🎯 MISSING DIMENSIONS CHECK:")
        expected_dims = ['region', 'economic_sector', 'age_group', 'gender', 'education', 
                        'nationality', 'urbanization', 'occupation', 'employment_status']
        
        missing_dims = []
        for dim in expected_dims:
            if dim not in df.columns:
                missing_dims.append(dim)
        
        if missing_dims:
            print(f"  ❌ Missing dimensions: {missing_dims}")
        else:
            print(f"  ✅ All expected dimensions present")
        
        # Check data completeness
        print(f"\n📈 DATA COMPLETENESS:")
        complete_records = len(df.dropna())
        incomplete_records = len(df) - complete_records
        completeness_rate = (complete_records / len(df)) * 100
        
        print(f"  Records with all dimensions: {complete_records:,}")
        print(f"  Records with missing dimensions: {incomplete_records:,}")
        print(f"  Completeness rate: {completeness_rate:.1f}%")
        
        # Summary
        print(f"\n📊 SUMMARY:")
        if missing_dims:
            print(f"  ❌ CRITICAL: Missing dimensions: {missing_dims}")
        else:
            print(f"  ✅ All dimensions present")
        
        if completeness_rate < 80:
            print(f"  ⚠️ WARNING: Low completeness rate ({completeness_rate:.1f}%)")
        else:
            print(f"  ✅ Good completeness rate ({completeness_rate:.1f}%)")
        
    except Exception as e:
        print(f"❌ ERROR during quality check: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_corrected_annual_data()
