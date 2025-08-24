#!/usr/bin/env python3
"""
FINAL QUALITY CHECK FOR CORRECTED ANNUAL LFS DATASET
"""

import pandas as pd

def final_annual_quality_check():
    """Final quality check of the corrected annual LFS dataset."""
    print("🔍 FINAL QUALITY CHECK FOR CORRECTED ANNUAL LFS DATASET")
    print("=" * 80)
    
    try:
        # Load the corrected dataset
        df = pd.read_excel('assets/prepared/LFS_annual_CORRECTED.xlsx')
        print(f"✅ Corrected dataset loaded: {len(df):,} records")
        
        # Check for region column
        print(f"\n🌍 REGION COLUMN STATUS:")
        if 'region' in df.columns:
            print(f"  ✅ REGION COLUMN IS NOW PRESENT!")
            region_counts = df['region'].value_counts()
            print(f"  Total unique regions: {len(region_counts)}")
            print(f"  Region nulls: {df['region'].isna().sum()}")
            print(f"  Top 10 regions:")
            for region, count in region_counts.head(10).items():
                print(f"    {region}: {count:,} records")
        else:
            print(f"  ❌ REGION COLUMN STILL MISSING!")
        
        # Check all expected dimensions
        print(f"\n🎯 ALL DIMENSIONS STATUS:")
        expected_dims = ['region', 'economic_sector', 'age_group', 'gender', 'education', 
                        'nationality', 'urbanization', 'occupation', 'employment_status']
        
        all_present = True
        for dim in expected_dims:
            if dim in df.columns:
                non_null = df[dim].dropna().nunique()
                null_count = df[dim].isna().sum()
                print(f"  ✅ {dim}: {non_null} unique values, {null_count} nulls")
            else:
                print(f"  ❌ {dim}: COLUMN MISSING!")
                all_present = False
        
        # Data completeness
        print(f"\n📈 DATA COMPLETENESS:")
        complete_records = len(df.dropna())
        incomplete_records = len(df) - complete_records
        completeness_rate = (complete_records / len(df)) * 100
        
        print(f"  Records with all dimensions: {complete_records:,}")
        print(f"  Records with missing dimensions: {incomplete_records:,}")
        print(f"  Completeness rate: {completeness_rate:.1f}%")
        
        # Final summary
        print(f"\n🏆 FINAL SUMMARY:")
        if all_present:
            print(f"  ✅ ALL EXPECTED DIMENSIONS ARE NOW PRESENT!")
        else:
            print(f"  ❌ SOME DIMENSIONS ARE STILL MISSING!")
        
        if completeness_rate >= 95:
            print(f"  ✅ EXCELLENT completeness rate ({completeness_rate:.1f}%)")
        elif completeness_rate >= 80:
            print(f"  ✅ GOOD completeness rate ({completeness_rate:.1f}%)")
        else:
            print(f"  ⚠️ LOW completeness rate ({completeness_rate:.1f}%)")
        
        # Check if we have the critical regions
        if 'region' in df.columns:
            print(f"\n🎯 CRITICAL REGIONS VERIFICATION:")
            critical_regions = ['Anatoliki Makedonia-Thraki', 'Kentriki Makedonia', 'Attiki', 'Kriti']
            found_critical = 0
            for crit_region in critical_regions:
                if any(crit_region in str(reg) for reg in df['region'].dropna().unique()):
                    print(f"  ✅ Found critical region: {crit_region}")
                    found_critical += 1
                else:
                    print(f"  ❌ Missing critical region: {crit_region}")
            
            if found_critical == len(critical_regions):
                print(f"  🎉 ALL CRITICAL REGIONS FOUND!")
            else:
                print(f"  ⚠️ {found_critical}/{len(critical_regions)} critical regions found")
        
    except Exception as e:
        print(f"❌ ERROR during final quality check: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    final_annual_quality_check()
