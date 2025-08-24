#!/usr/bin/env python3
"""
COMPREHENSIVE ANNUAL LFS DATA QUALITY CHECK
This script will identify all the issues in the annual dataset.
"""

import pandas as pd
import numpy as np

def check_annual_data_quality():
    """Comprehensive quality check of annual LFS data."""
    print("🔍 COMPREHENSIVE ANNUAL LFS DATA QUALITY CHECK")
    print("=" * 80)
    
    try:
        # Load the dataset
        df = pd.read_excel('assets/prepared/LFS_annual.xlsx')
        print(f"✅ Dataset loaded: {len(df):,} records")
        
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
            print(f"  Top 10 time periods:")
            for period, count in time_counts.head(10).items():
                print(f"    {period}: {count:,} records")
        else:
            print("  ❌ NO TIME_PERIOD COLUMN!")
        
        # Sheet analysis
        print(f"\n📋 SHEET ANALYSIS:")
        if 'sheet_name' in df.columns:
            sheet_counts = df['sheet_name'].value_counts()
            print(f"  Total unique sheets: {len(sheet_counts)}")
            print(f"  Sheet distribution:")
            for sheet, count in sheet_counts.items():
                print(f"    {sheet}: {count:,} records")
        else:
            print("  ❌ NO SHEET_NAME COLUMN!")
        
        # File source analysis
        print(f"\n📁 FILE SOURCE ANALYSIS:")
        if 'file_source' in df.columns:
            file_counts = df['file_source'].value_counts()
            print(f"  Total unique files: {len(file_counts)}")
            print(f"  File distribution:")
            for file, count in file_counts.items():
                print(f"    {file}: {count:,} records")
        else:
            print("  ❌ NO FILE_SOURCE COLUMN!")
        
        # Value analysis
        print(f"\n💰 VALUE ANALYSIS:")
        if 'value' in df.columns:
            print(f"  Value range: {df['value'].min():.2f} to {df['value'].max():.2f}")
            print(f"  Mean value: {df['value'].mean():.2f}")
            print(f"  Null values: {df['value'].isna().sum()}")
            print(f"  Zero values: {(df['value'] == 0).sum()}")
            print(f"  Negative values: {(df['value'] < 0).sum()}")
        else:
            print("  ❌ NO VALUE COLUMN!")
        
        # Dimension analysis
        print(f"\n🎯 DIMENSION ANALYSIS:")
        dimension_cols = ['region', 'economic_sector', 'age_group', 'gender', 'education', 
                         'nationality', 'urbanization', 'occupation', 'employment_status']
        
        for dim in dimension_cols:
            if dim in df.columns:
                unique_vals = df[dim].dropna().nunique()
                null_count = df[dim].isna().sum()
                print(f"  {dim}: {unique_vals} unique values, {null_count} nulls")
                
                # Show some unique values
                unique_values = df[dim].dropna().unique()
                if len(unique_values) <= 10:
                    print(f"    Values: {list(unique_values)}")
                else:
                    print(f"    Sample values: {list(unique_values[:5])}...")
            else:
                print(f"  ❌ {dim}: COLUMN MISSING!")
        
        # Indicator analysis
        print(f"\n📊 INDICATOR ANALYSIS:")
        if 'indicator' in df.columns:
            indicator_counts = df['indicator'].value_counts()
            print(f"  Total unique indicators: {len(indicator_counts)}")
            print(f"  Indicator distribution:")
            for indicator, count in indicator_counts.items():
                print(f"    {indicator}: {count:,} records")
        else:
            print("  ❌ NO INDICATOR COLUMN!")
        
        # Frequency analysis
        print(f"\n🔄 FREQUENCY ANALYSIS:")
        if 'freq' in df.columns:
            freq_counts = df['freq'].value_counts()
            print(f"  Total unique frequencies: {len(freq_counts)}")
            print(f"  Frequency distribution:")
            for freq, count in freq_counts.items():
                print(f"    {freq}: {count:,} records")
        else:
            print("  ❌ NO FREQ COLUMN!")
        
        # Critical issues check
        print(f"\n🚨 CRITICAL ISSUES CHECK:")
        issues_found = []
        
        # Check for missing critical columns
        critical_cols = ['time_period', 'value', 'indicator', 'freq']
        for col in critical_cols:
            if col not in df.columns:
                issues_found.append(f"Missing critical column: {col}")
        
        # Check for all null values in critical columns
        for col in critical_cols:
            if col in df.columns and df[col].isna().all():
                issues_found.append(f"All values null in critical column: {col}")
        
        # Check for suspicious time periods
        if 'time_period' in df.columns:
            suspicious_periods = [p for p in df['time_period'].unique() if 'UNKNOWN' in str(p)]
            if suspicious_periods:
                issues_found.append(f"Suspicious time periods found: {suspicious_periods}")
        
        # Check for extreme values
        if 'value' in df.columns:
            extreme_values = df[df['value'] > 1000000]  # Values over 1 million
            if len(extreme_values) > 0:
                issues_found.append(f"Extreme values found: {len(extreme_values)} records > 1M")
        
        if issues_found:
            print("  ❌ CRITICAL ISSUES FOUND:")
            for issue in issues_found:
                print(f"    - {issue}")
        else:
            print("  ✅ No critical issues found")
        
        # Summary
        print(f"\n📈 QUALITY SUMMARY:")
        print(f"  Data completeness: {(len(df) - df.isna().sum().sum() / (len(df) * len(df.columns))) * 100:.1f}%")
        print(f"  Records with all dimensions: {len(df.dropna())}")
        print(f"  Records with missing dimensions: {len(df) - len(df.dropna())}")
        
    except Exception as e:
        print(f"❌ ERROR during quality check: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_annual_data_quality()
