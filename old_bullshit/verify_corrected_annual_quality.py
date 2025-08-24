#!/usr/bin/env python3
"""
VERIFY CORRECTED ANNUAL LFS DATASET QUALITY
This script will verify the improvements in the corrected annual dataset.
"""

import pandas as pd

def verify_corrected_annual_quality():
    """Verify the quality improvements in the corrected annual dataset."""
    print("🔍 VERIFYING CORRECTED ANNUAL LFS DATASET QUALITY")
    print("=" * 80)
    
    try:
        # Load the corrected dataset
        df = pd.read_excel('assets/prepared/LFS_annual_CORRECTED_FINAL.xlsx')
        print(f"✅ Corrected dataset loaded: {len(df):,} records")
        
        # Basic info
        print(f"\n📊 BASIC INFO:")
        print(f"  Total records: {len(df):,}")
        print(f"  Total columns: {len(df.columns)}")
        print(f"  Columns: {list(df.columns)}")
        
        # CRITICAL DIMENSION ANALYSIS
        print(f"\n🎯 CRITICAL DIMENSION ANALYSIS:")
        critical_dims = ['economic_sector', 'gender', 'education', 'employment_status']
        
        for dim in critical_dims:
            if dim in df.columns:
                unique_vals = df[dim].dropna().nunique()
                null_count = df[dim].isna().sum()
                total = len(df)
                null_percent = (null_count / total) * 100
                print(f"  {dim}: {unique_vals} unique values, {null_count} nulls ({null_percent:.1f}%)")
                
                # Show unique values
                unique_values = df[dim].dropna().unique()
                if len(unique_values) <= 10:
                    print(f"    Values: {list(unique_values)}")
                else:
                    print(f"    Sample values: {list(unique_values[:5])}...")
                    
                # Check for "TOTAL" values
                total_values = df[df[dim].str.contains('TOTAL', case=False, na=False)]
                if len(total_values) > 0:
                    print(f"    ⚠️ TOTAL values: {len(total_values)} records")
                else:
                    print(f"    ✅ NO TOTAL values found!")
            else:
                print(f"  ❌ {dim}: COLUMN MISSING!")
        
        # ALL DIMENSIONS STATUS
        print(f"\n🔍 ALL DIMENSIONS STATUS:")
        all_dims = ['region', 'economic_sector', 'age_group', 'gender', 'education', 
                    'nationality', 'urbanization', 'occupation', 'employment_status']
        
        for dim in all_dims:
            if dim in df.columns:
                non_null = df[dim].dropna().nunique()
                null_count = df[dim].isna().sum()
                total = len(df)
                null_percent = (null_count / total) * 100
                print(f"  {dim}: {non_null} unique values, {null_count} nulls ({null_percent:.1f}%)")
            else:
                print(f"  ❌ {dim}: COLUMN MISSING!")
        
        # VALUE COLUMN ANALYSIS
        print(f"\n💰 VALUE COLUMN ANALYSIS:")
        if 'value' in df.columns:
            print(f"  Value range: {df['value'].min():.2f} to {df['value'].max():.2f}")
            print(f"  Mean value: {df['value'].mean():.2f}")
            print(f"  Null values: {df['value'].isna().sum()}")
            print(f"  Zero values: {(df['value'] == 0).sum()}")
            print(f"  Negative values: {(df['value'] < 0).sum()}")
            print(f"  Unique values: {df['value'].nunique()}")
        else:
            print("  ❌ NO VALUE COLUMN!")
        
        # TIME PERIOD ANALYSIS
        print(f"\n⏰ TIME PERIOD ANALYSIS:")
        if 'time_period' in df.columns:
            time_counts = df['time_period'].value_counts()
            print(f"  Total unique time periods: {len(time_counts)}")
            print(f"  Time period range: {time_counts.index.min()} to {time_counts.index.max()}")
            print(f"  Top 10 time periods:")
            for period, count in time_counts.head(10).items():
                print(f"    {period}: {count:,} records")
        else:
            print("  ❌ NO TIME_PERIOD COLUMN!")
        
        # INDICATOR ANALYSIS
        print(f"\n📊 INDICATOR ANALYSIS:")
        if 'indicator' in df.columns:
            indicator_counts = df['indicator'].value_counts()
            print(f"  Total unique indicators: {len(indicator_counts)}")
            print(f"  Indicator distribution:")
            for indicator, count in indicator_counts.items():
                print(f"    {indicator}: {count:,} records")
        else:
            print("  ❌ NO INDICATOR COLUMN!")
        
        # DATA COMPLETENESS ANALYSIS
        print(f"\n📈 DATA COMPLETENESS ANALYSIS:")
        complete_records = len(df.dropna())
        incomplete_records = len(df) - complete_records
        completeness_rate = (complete_records / len(df)) * 100
        
        print(f"  Records with all dimensions: {complete_records:,}")
        print(f"  Records with missing dimensions: {incomplete_records:,}")
        print(f"  Completeness rate: {completeness_rate:.1f}%")
        
        # COMPARISON WITH PREVIOUS VERSION
        print(f"\n🔄 COMPARISON WITH PREVIOUS VERSION:")
        print(f"  Previous records: 22,928")
        print(f"  Corrected records: {len(df):,}")
        print(f"  Improvement: {len(df)/22928:.1f}x more data!")
        
        print(f"  Previous unique regions: 1 (TOTAL)")
        print(f"  Corrected unique regions: {df['region'].nunique()}")
        print(f"  Improvement: {df['region'].nunique()}/1 = {df['region'].nunique()}x more regions!")
        
        print(f"  Previous unique economic sectors: 1 (TOTAL)")
        print(f"  Corrected unique economic sectors: {df['economic_sector'].nunique()}")
        print(f"  Improvement: {df['economic_sector'].nunique()}/1 = {df['economic_sector'].nunique()}x more sectors!")
        
        print(f"  Previous unique occupations: 1 (TOTAL)")
        print(f"  Corrected unique occupations: {df['occupation'].nunique()}")
        print(f"  Improvement: {df['occupation'].nunique()}/1 = {df['occupation'].nunique()}x more occupations!")
        
        # FINAL SUMMARY
        print(f"\n🏆 FINAL QUALITY SUMMARY:")
        print(f"  Overall data quality: {'POOR' if completeness_rate < 50 else 'FAIR' if completeness_rate < 80 else 'GOOD' if completeness_rate < 95 else 'EXCELLENT'}")
        print(f"  Critical dimensions missing: {sum(1 for dim in critical_dims if dim not in df.columns)}")
        print(f"  Data completeness: {completeness_rate:.1f}%")
        print(f"  Data volume improvement: {len(df)/22928:.1f}x")
        
        if completeness_rate >= 80 and len(df) > 50000:
            print(f"  🎉 MAJOR SUCCESS: All critical issues resolved!")
        else:
            print(f"  ⚠️ Some issues may remain")
        
    except Exception as e:
        print(f"❌ ERROR during quality verification: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_corrected_annual_quality()
