#!/usr/bin/env python3
"""
COMPREHENSIVE ANNUAL LFS DATA QUALITY CHECK
This script will thoroughly analyze the comprehensive annual dataset to identify ALL issues.
"""

import pandas as pd
import numpy as np

def comprehensive_annual_quality_check():
    """Comprehensive quality check of comprehensive annual LFS data."""
    print("🔍 COMPREHENSIVE ANNUAL LFS DATA QUALITY CHECK")
    print("=" * 80)
    
    try:
        # Load the comprehensive dataset
        df = pd.read_excel('assets/prepared/LFS_annual_COMPREHENSIVE.xlsx')
        print(f"✅ Comprehensive dataset loaded: {len(df):,} records")
        
        # Basic info
        print(f"\n📊 BASIC INFO:")
        print(f"  Total records: {len(df):,}")
        print(f"  Total columns: {len(df.columns)}")
        print(f"  Columns: {list(df.columns)}")
        
        # CRITICAL VALUE COLUMN ANALYSIS
        print(f"\n💰 CRITICAL VALUE COLUMN ANALYSIS:")
        if 'value' in df.columns:
            print(f"  Value range: {df['value'].min():.2f} to {df['value'].max():.2f}")
            print(f"  Mean value: {df['value'].mean():.2f}")
            print(f"  Null values: {df['value'].isna().sum()}")
            print(f"  Zero values: {(df['value'] == 0).sum()}")
            print(f"  Negative values: {(df['value'] < 0).sum()}")
            print(f"  Unique values: {df['value'].nunique()}")
            
            # Check for suspicious values
            suspicious_values = df[df['value'] > 1000000]
            if len(suspicious_values) > 0:
                print(f"  ⚠️ Suspicious high values (>1M): {len(suspicious_values)} records")
                print(f"    Sample: {suspicious_values['value'].head().tolist()}")
        else:
            print("  ❌ NO VALUE COLUMN!")
        
        # CRITICAL DIMENSION ANALYSIS
        print(f"\n🎯 CRITICAL DIMENSION ANALYSIS:")
        critical_dims = ['economic_sector', 'gender', 'education', 'employment_status', 'region']
        
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
                    
                # Check for "TOTAL" or "UNKNOWN" values
                total_values = df[df[dim].str.contains('TOTAL|UNKNOWN', case=False, na=False)]
                if len(total_values) > 0:
                    print(f"    ⚠️ TOTAL/UNKNOWN values: {len(total_values)} records")
            else:
                print(f"  ❌ {dim}: COLUMN MISSING!")
        
        # ALL DIMENSIONS STATUS
        print(f"\n🔍 ALL DIMENSIONS STATUS:")
        all_dims = ['region', 'economic_sector', 'age_group', 'gender', 'education', 
                    'nationality', 'urbanization', 'occupation', 'employment_status', 'sex']
        
        for dim in all_dims:
            if dim in df.columns:
                non_null = df[dim].dropna().nunique()
                null_count = df[dim].isna().sum()
                total = len(df)
                null_percent = (null_count / total) * 100
                print(f"  {dim}: {non_null} unique values, {null_count} nulls ({null_percent:.1f}%)")
            else:
                print(f"  ❌ {dim}: COLUMN MISSING!")
        
        # SHEET ANALYSIS
        print(f"\n📋 SHEET ANALYSIS:")
        if 'sheet_name' in df.columns:
            sheet_counts = df['sheet_name'].value_counts()
            print(f"  Total unique sheets: {len(sheet_counts)}")
            print(f"  Sheet distribution:")
            for sheet, count in sheet_counts.items():
                print(f"    {sheet}: {count:,} records")
                
                # Check data quality per sheet
                sheet_data = df[df['sheet_name'] == sheet]
                if 'value' in sheet_data.columns:
                    sheet_values = sheet_data['value'].dropna()
                    if len(sheet_values) > 0:
                        print(f"      Values: {sheet_values.min():.0f} to {sheet_values.max():.0f}")
                    else:
                        print(f"      ⚠️ NO VALUES in this sheet!")
        else:
            print("  ❌ NO SHEET_NAME COLUMN!")
        
        # TIME PERIOD ANALYSIS
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
        
        # FILE ANALYSIS
        print(f"\n📁 FILE ANALYSIS:")
        if 'file_name' in df.columns:
            file_counts = df['file_name'].value_counts()
            print(f"  Total unique files: {len(file_counts)}")
            print(f"  File distribution:")
            for file, count in file_counts.items():
                print(f"    {file}: {count:,} records")
        else:
            print("  ❌ NO FILE_NAME COLUMN!")
        
        # COLUMN POSITION ANALYSIS
        print(f"\n📍 COLUMN POSITION ANALYSIS:")
        if 'col_position' in df.columns:
            col_pos_counts = df['col_position'].value_counts().sort_index()
            print(f"  Column positions used: {list(col_pos_counts.index)}")
            print(f"  Records per column position:")
            for pos, count in col_pos_counts.head(20).items():
                print(f"    Column {pos}: {count:,} records")
        else:
            print("  ❌ NO COL_POSITION COLUMN!")
        
        # DATA COMPLETENESS ANALYSIS
        print(f"\n📈 DATA COMPLETENESS ANALYSIS:")
        complete_records = len(df.dropna())
        incomplete_records = len(df) - complete_records
        completeness_rate = (complete_records / len(df)) * 100
        
        print(f"  Records with all dimensions: {complete_records:,}")
        print(f"  Records with missing dimensions: {incomplete_records:,}")
        print(f"  Completeness rate: {completeness_rate:.1f}%")
        
        # Check completeness by dimension
        print(f"\n📊 COMPLETENESS BY DIMENSION:")
        for dim in all_dims:
            if dim in df.columns:
                complete_dim = len(df[df[dim].notna()])
                dim_completeness = (complete_dim / len(df)) * 100
                print(f"  {dim}: {dim_completeness:.1f}% complete")
            else:
                print(f"  {dim}: 0% complete (MISSING)")
        
        # SDMX COMPLIANCE CHECK
        print(f"\n🏛️ SDMX COMPLIANCE CHECK:")
        sdmx_required = ['indicator', 'time_period', 'freq', 'ref_area', 'value', 'unit_measure', 'obs_status', 'source_agency', 'collection', 'adjustment']
        sdmx_missing = [col for col in sdmx_required if col not in df.columns]
        sdmx_present = [col for col in sdmx_required if col in df.columns]
        
        print(f"  Required SDMX columns: {len(sdmx_required)}")
        print(f"  Present SDMX columns: {len(sdmx_present)}")
        print(f"  Missing SDMX columns: {len(sdmx_missing)}")
        
        if sdmx_missing:
            print(f"    Missing: {sdmx_missing}")
        else:
            print(f"    ✅ ALL SDMX columns present!")
        
        # DATA DISTRIBUTION ANALYSIS
        print(f"\n📊 DATA DISTRIBUTION ANALYSIS:")
        
        # Check for balanced data across dimensions
        if 'region' in df.columns and 'time_period' in df.columns:
            region_time_cross = df.groupby(['region', 'time_period']).size().reset_index(name='count')
            print(f"  Region-time combinations: {len(region_time_cross)}")
            print(f"  Average records per combination: {region_time_cross['count'].mean():.1f}")
            print(f"  Min records per combination: {region_time_cross['count'].min()}")
            print(f"  Max records per combination: {region_time_cross['count'].max()}")
        
        # Check for balanced data across sheets
        if 'sheet_name' in df.columns and 'time_period' in df.columns:
            sheet_time_cross = df.groupby(['sheet_name', 'time_period']).size().reset_index(name='count')
            print(f"  Sheet-time combinations: {len(sheet_time_cross)}")
            print(f"  Average records per combination: {sheet_time_cross['count'].mean():.1f}")
        
        # CRITICAL ISSUES SUMMARY
        print(f"\n🚨 CRITICAL ISSUES SUMMARY:")
        issues_found = []
        
        # Check for missing critical columns
        critical_cols = ['time_period', 'value', 'indicator']
        for col in critical_cols:
            if col not in df.columns:
                issues_found.append(f"Missing critical column: {col}")
        
        # Check for high null percentages in critical dimensions
        critical_dims = ['economic_sector', 'gender', 'education', 'employment_status', 'region']
        for dim in critical_dims:
            if dim in df.columns:
                null_percent = (df[dim].isna().sum() / len(df)) * 100
                if null_percent > 50:
                    issues_found.append(f"High null percentage in {dim}: {null_percent:.1f}%")
            else:
                issues_found.append(f"Missing critical dimension: {dim}")
        
        # Check for suspicious values
        if 'value' in df.columns:
            if df['value'].isna().sum() > len(df) * 0.1:
                issues_found.append(f"High null percentage in value column: {(df['value'].isna().sum() / len(df)) * 100:.1f}%")
            
            if df['value'].max() > 1000000:
                issues_found.append(f"Extreme values found: max value is {df['value'].max():.0f}")
        
        # Check for data volume issues
        if len(df) < 10000:
            issues_found.append(f"Low data volume: only {len(df):,} records")
        
        if issues_found:
            print("  ❌ CRITICAL ISSUES FOUND:")
            for issue in issues_found:
                print(f"    - {issue}")
        else:
            print("  ✅ No critical issues found")
        
        # COMPARISON WITH PREVIOUS VERSIONS
        print(f"\n🔄 COMPARISON WITH PREVIOUS VERSIONS:")
        print(f"  Previous records (CORRECTED): 143,901")
        print(f"  Comprehensive records: {len(df):,}")
        if len(df) > 143901:
            print(f"  Improvement: {len(df)/143901:.1f}x more data!")
        else:
            print(f"  Change: {len(df)/143901:.1f}x data volume")
        
        # FINAL SUMMARY
        print(f"\n🏆 FINAL QUALITY SUMMARY:")
        print(f"  Overall data quality: {'POOR' if completeness_rate < 50 else 'FAIR' if completeness_rate < 80 else 'GOOD' if completeness_rate < 95 else 'EXCELLENT'}")
        print(f"  Critical dimensions missing: {sum(1 for dim in critical_dims if dim not in df.columns)}")
        print(f"  Data completeness: {completeness_rate:.1f}%")
        print(f"  SDMX compliance: {len(sdmx_present)}/{len(sdmx_required)} columns")
        
        if completeness_rate >= 80 and len(df) > 50000 and len(sdmx_missing) == 0:
            print(f"  🎉 MAJOR SUCCESS: All critical issues resolved!")
        elif completeness_rate >= 60 and len(df) > 10000:
            print(f"  ✅ GOOD PROGRESS: Most issues resolved")
        else:
            print(f"  ⚠️ Issues remain - needs improvement")
        
    except Exception as e:
        print(f"❌ ERROR during quality check: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    comprehensive_annual_quality_check()
