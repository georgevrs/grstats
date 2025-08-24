"""
Verify Total Population Records
Checks that the total population records (Total, _Z, _Z, _Z) are properly included
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

def main():
    """Main function to verify total population records"""
    
    # Load the parsed data
    parsed_file = "assets/prepared/lfs_popul_regio_parsed.xlsx"
    
    if not os.path.exists(parsed_file):
        print(f"ERROR: File not found: {parsed_file}")
        return
    
    try:
        # Read the parsed data
        df = pd.read_excel(parsed_file)
        print(f"Loaded parsed data: {len(df)} records x {len(df.columns)} columns")
        
        # Check for total population records (Total, _Z, _Z, _Z)
        total_pop_records = df[
            (df['Sex'] == 'Total') & 
            (df['Age_Group'] == '_Z') & 
            (df['Nationality'] == '_Z') & 
            (df['Marital_Status'] == '_Z')
        ]
        
        print(f"\nTotal Population Records (Total, _Z, _Z, _Z):")
        print(f"  Found: {len(total_pop_records)} records")
        
        if len(total_pop_records) > 0:
            print(f"\nSample Total Population Records:")
            print(total_pop_records.head(10)[['Year', 'Region', 'Sex', 'Age_Group', 'Nationality', 'Marital_Status', 'Value']].to_string())
            
            # Check the values make sense
            print(f"\nValue Statistics for Total Population:")
            print(f"  Min: {total_pop_records['Value'].min()}")
            print(f"  Max: {total_pop_records['Value'].max()}")
            print(f"  Mean: {total_pop_records['Value'].mean():.2f}")
            print(f"  Count of non-null values: {total_pop_records['Value'].notna().sum()}")
        
        # Check the complete breakdown
        print(f"\nComplete Data Breakdown:")
        print(f"  Total records: {len(df)}")
        
        # Sex breakdown
        sex_breakdown = df['Sex'].value_counts()
        print(f"  Sex breakdown:")
        for sex, count in sex_breakdown.items():
            print(f"    {sex}: {count} records")
        
        # Age group breakdown (excluding _Z)
        age_breakdown = df[df['Age_Group'] != '_Z']['Age_Group'].value_counts()
        print(f"  Age group breakdown (excluding _Z):")
        for age, count in age_breakdown.items():
            print(f"    {age}: {count} records")
        
        # Nationality breakdown (excluding _Z)
        nat_breakdown = df[df['Nationality'] != '_Z']['Nationality'].value_counts()
        print(f"  Nationality breakdown (excluding _Z):")
        for nat, count in nat_breakdown.items():
            print(f"    {nat}: {count} records")
        
        # Marital status breakdown (excluding _Z)
        marital_breakdown = df[df['Marital_Status'] != '_Z']['Marital_Status'].value_counts()
        print(f"  Marital status breakdown (excluding _Z):")
        for marital, count in marital_breakdown.items():
            print(f"    {marital}: {count} records")
        
        # Verify the structure makes sense
        print(f"\nStructure Verification:")
        
        # Each Year+Region combination should have:
        # 1. Total population record (Total, _Z, _Z, _Z)
        # 2. 7 age group records for Total sex
        # 3. 3 nationality records for Total sex  
        # 4. 3 marital status records for Total sex
        # 5. 7 age group records for Males
        # 6. 7 age group records for Females
        
        expected_per_year_region = 1 + 7 + 3 + 3 + 7 + 7  # = 28 records per Year+Region
        
        unique_year_region = df.groupby(['Year', 'Region']).size()
        print(f"  Records per Year+Region combination:")
        print(f"    Expected: {expected_per_year_region}")
        print(f"    Actual range: {unique_year_region.min()} to {unique_year_region.max()}")
        print(f"    Most common: {unique_year_region.mode().iloc[0] if len(unique_year_region.mode()) > 0 else 'N/A'}")
        
        # Check if all Year+Region combinations have the expected number of records
        correct_count = (unique_year_region == expected_per_year_region).sum()
        total_combinations = len(unique_year_region)
        print(f"  Year+Region combinations with correct record count: {correct_count}/{total_combinations}")
        
    except Exception as e:
        print(f"ERROR during verification: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
