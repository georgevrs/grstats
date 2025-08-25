import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Import all masking functions once at the top
from lfs_utils.masking_config import (
    apply_region_masking, apply_education_masking, apply_education_sub_masking,
    apply_formal_informal_education_masking, apply_neet_category_masking,
    apply_sex_masking, apply_age_group_masking, apply_main_employment_status_masking,
    apply_sub_employment_status_masking, apply_undermp_pt_work_sub_masking,
    apply_work_for_more_hours_masking, apply_looking_for_another_job_masking,
    apply_unit_of_measure_masking, apply_nr_persons_local_unit_masking,
    apply_bo_masking, apply_sector_masking, apply_sector_sub_masking,
    apply_type_occupation_masking, apply_permanency_for_employees_masking,
    apply_reasons_pt_masking, apply_permanency_for_employees_sub_masking,
    apply_reasons_temp_masking, apply_hours_actually_work_masking,
    apply_hours_actually_work_sub_masking, apply_hours_usual_work_masking,
    apply_hours_usual_work_sub_masking, apply_atypical_work_masking,
    apply_atypical_work_sub_masking, apply_nationality_masking,
    apply_region_1981_masking, apply_urbanization_masking,
    apply_labour_force_status_masking, apply_labour_force_subcategory_masking, apply_marital_status_masking
)

def clean_dataframe(df, col_to_check="Value", invalid_value="_Z"):
    """
    Cleans a DataFrame by:
    1. Dropping duplicate columns
    2. Dropping duplicate rows
    3. Removing rows with a specific invalid value in a given column
    
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame
    col_to_check : str, default "Value"
        Column to check for invalid values
    invalid_value : str, default "_Z"
        Value to drop from the column
    
    Returns
    -------
    pd.DataFrame
        Cleaned DataFrame
    """
    # Drop duplicate columns
    df = df.loc[:, ~df.columns.duplicated()]
    
    # Report dropped duplicate rows
    dropped_dupes = df.shape[0] - df.drop_duplicates().shape[0]
    print(f"Dropped duplicate rows: {dropped_dupes}")
    df = df.drop_duplicates()
    
    # Drop invalid values
    before = df.shape[0]
    df = df[df[col_to_check] != invalid_value]
    after = df.shape[0]
    print(f"Dropped invalid rows ({invalid_value} in {col_to_check}): {before - after}")
    
    return df

def apply_comprehensive_masking(df):
    """
    Apply all available masking functions to the dataset in the correct order
    and then remove any duplicate rows that may have been created
    
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame
        
    Returns
    -------
    pd.DataFrame
        DataFrame with all applicable columns masked and duplicates removed
    """
    print("\n" + "="*60)
    print("APPLYING COMPREHENSIVE MASKING TO ALL COLUMNS")
    print("="*60)
    
    # Define masking configuration: (column_name, masking_function, display_name)
    masking_config = [
        ('Region', apply_region_masking, 'Region'),
        ('Education_Level_Main', apply_education_masking, 'Education Level Main'),
        ('Education_Level_Sub', apply_education_sub_masking, 'Education Level Sub'),
        ('Formal_Informal_Education', apply_formal_informal_education_masking, 'Formal/Informal Education'),
        ('NEET_Category', apply_neet_category_masking, 'NEET Category'),
        ('Sex', apply_sex_masking, 'Sex'),
        ('Age_Group', apply_age_group_masking, 'Age Group'),
        ('Main_Employment_Status', apply_main_employment_status_masking, 'Main Employment Status'),
        ('Sub_Employment_Status', apply_sub_employment_status_masking, 'Sub Employment Status'),
        ('UNDERMP_PT_WORK_SUB', apply_undermp_pt_work_sub_masking, 'Underemployment PT Work Sub'),
        ('WORK_FOR_MORE_HOURS', apply_work_for_more_hours_masking, 'Work for More Hours'),
        ('LOOKING_FOR_ANOTHER_JOB', apply_looking_for_another_job_masking, 'Looking for Another Job'),
        ('Unit_of_Measure', apply_unit_of_measure_masking, 'Unit of Measure'),
        ('NR_PERSONS_LOCAL_UNIT', apply_nr_persons_local_unit_masking, 'Number of Persons Local Unit'),
        ('BO', apply_bo_masking, 'Business Ownership'),
        ('SECTOR', apply_sector_masking, 'Sector'),
        ('SECTOR_SUB', apply_sector_sub_masking, 'Sector Sub'),
        ('TYPE_OCCUPATION', apply_type_occupation_masking, 'Type of Occupation'),
        ('PERMANENCY_FOR_EMPLOYEES', apply_permanency_for_employees_masking, 'Permanency for Employees'),
        ('REASONS_PT', apply_reasons_pt_masking, 'Reasons for Part-Time Work'),
        ('PERMANENCY_FOR_EMPLOYEES_SUB', apply_permanency_for_employees_sub_masking, 'Permanency for Employees Sub-Category'),
        ('REASONS_TEMP', apply_reasons_temp_masking, 'Reasons for Temporary Work'),
        ('HOURS_ACTUALLY_WORK', apply_hours_actually_work_masking, 'Hours Actually Worked'),
        ('HOURS_ACTUALLY_WORK_SUB', apply_hours_actually_work_sub_masking, 'Hours Actually Worked Sub-Category'),
        ('HOURS_USUAL_WORK', apply_hours_usual_work_masking, 'Hours Usually Worked'),
        ('HOURS_USUAL_WORK_SUB', apply_hours_usual_work_sub_masking, 'Hours Usually Worked Sub-Category'),
        ('ATYPICAL_WORK', apply_atypical_work_masking, 'Atypical Work'),
        ('ATYPICAL_WORK_SUB', apply_atypical_work_sub_masking, 'Atypical Work Sub-Category'),
        ('Nationality', apply_nationality_masking, 'Nationality'),
        ('Region_1981', apply_region_1981_masking, '1981 Region Classification'),
        ('Urbanization', apply_urbanization_masking, 'Urbanization'),
        ('Marital_Status', apply_marital_status_masking, 'Marital Status'),
        ('Labour_Force_Status', apply_labour_force_status_masking, 'Labour Force Status'),
        ('Labour_Force_Subcategory', apply_labour_force_subcategory_masking, 'Labour Force Subcategory')
    ]
    
    masked_df = df.copy()
    total_masked = 0
    
    for column_name, masking_function, display_name in masking_config:
        if column_name in masked_df.columns:
            print(f"\nApplying masking to {display_name} column...")
            try:
                masked_df = masking_function(masked_df, column_name)
                print(f"✓ Successfully masked {display_name}")
            except Exception as e:
                print(f"✗ Error masking {display_name}: {str(e)}")
        else:
            print(f"⚠ Column '{column_name}' not found - skipping {display_name} masking")
    
    print(f"\n" + "="*60)
    print("MASKING COMPLETED SUCCESSFULLY")
    print("="*60)
    
    # Final duplicate removal after all masking is complete
    print("\n" + "="*60)
    print("FINAL DUPLICATE ROW REMOVAL")
    print("="*60)
    
    initial_rows = len(masked_df)
    print(f"Initial dataset: {initial_rows:,} rows")
    
    # Remove duplicate rows
    masked_df = masked_df.drop_duplicates()
    
    final_rows = len(masked_df)
    duplicates_removed = initial_rows - final_rows
    
    print(f"After duplicate removal: {final_rows:,} rows")
    print(f"Duplicates removed: {duplicates_removed:,} rows")
    
    if duplicates_removed > 0:
        print(f"Duplicate reduction: {(duplicates_removed/initial_rows)*100:.2f}%")
    else:
        print("✓ No duplicate rows found")
    
    print("="*60)
    
    return masked_df

# EDUC DATASETS
print("Loading EDUC datasets...")
df_lfs_educ_regio = pd.read_excel('assets/prepared/lfs_educ_regio_parsed.xlsx')
df_lfs_educ_sexage = pd.read_excel('assets/prepared/lfs_educ_sexage_parsed.xlsx')
df_lfs_educ_status = pd.read_excel('assets/prepared/lfs_educ_status_parsed.xlsx')

# EMP DATASETS
print("Loading EMP datasets...")
df_lfs_emp_regio = pd.read_excel('assets/prepared/lfs_emp_regio_parsed.xlsx')
df_lfs_emp_sexage = pd.read_excel('assets/prepared/lfs_emp_sexage_parsed.xlsx')

# JOB DATASETS
print("Loading JOB datasets...")
df_lfs_job_regio = pd.read_excel('assets/prepared/lfs_job_regio_parsed.xlsx')
df_lfs_job_sexage = pd.read_excel('assets/prepared/lfs_job_sexage_parsed.xlsx')
df_lfs_job_occup = pd.read_excel('assets/prepared/lfs_job_occup_parsed.xlsx')

# READ lfs_demo datasets
print("Loading DEMO datasets...")
df_lfs_occup_demo = pd.read_excel('assets/prepared/lfs_occup_demo_parsed.xlsx')
df_lfs_sector_demo = pd.read_excel('assets/prepared/lfs_sector_demo_parsed.xlsx')

# read all population datasets
print("Loading POPUL datasets...")
df_lfs_popul_regio = pd.read_excel('assets/prepared/lfs_popul_regio_parsed.xlsx')
df_lfs_popul_status = pd.read_excel('assets/prepared/lfs_popul_status_parsed.xlsx')

# read all status datasets
print("Loading STATUS datasets...")
df_lfs_status_regio = pd.read_excel('assets/prepared/lfs_status_regio_parsed.xlsx')
df_lfs_status_sexage = pd.read_excel('assets/prepared/lfs_status_sexage_parsed.xlsx')

# Convert all Value columns to string to avoid merge conflicts
print("Converting Value columns to string type...")
all_dfs = [df_lfs_educ_regio, df_lfs_educ_sexage, df_lfs_educ_status,
           df_lfs_emp_regio, df_lfs_emp_sexage,
           df_lfs_job_regio, df_lfs_job_sexage, df_lfs_job_occup,
           df_lfs_occup_demo, df_lfs_sector_demo,
           df_lfs_popul_regio, df_lfs_popul_status,
           df_lfs_status_regio, df_lfs_status_sexage]

for i, df in enumerate(all_dfs):
    if 'Value' in df.columns:
        df['Value'] = df['Value'].astype(str)
        print(f"Dataset {i+1}: Converted Value column to string")

print("\n" + "="*50)
print("PROCESSING EDUC DATASETS")
print("="*50)

# find all common columns list them
common_columns = set(df_lfs_educ_regio.columns) & set(df_lfs_educ_sexage.columns) & set(df_lfs_educ_status.columns)
print("Common columns:", common_columns)

# outer join on common columns
df_lfs_educ = df_lfs_educ_regio.merge(df_lfs_educ_sexage, on=list(common_columns), how='outer')
df_lfs_educ = df_lfs_educ.merge(df_lfs_educ_status, on=list(common_columns), how='outer')

# fill NaN cells with _Z
df_lfs_educ = df_lfs_educ.fillna('_Z')
df_lfs_educ = clean_dataframe(df_lfs_educ, col_to_check="Value", invalid_value="_Z")

# print columns
print("Columns in EDUC dataset:")
print(df_lfs_educ.columns)

print("\n" + "="*50)
print("PROCESSING EMP DATASETS")
print("="*50)

# find all common columns list them
common_columns_emp = set(df_lfs_emp_regio.columns) & set(df_lfs_emp_sexage.columns)
print("Common columns EMP:", common_columns_emp)

# outer join on common columns
df_lfs_emp = df_lfs_emp_regio.merge(df_lfs_emp_sexage, on=list(common_columns_emp), how='outer')

# fill NaN cells with _Z
df_lfs_emp = df_lfs_emp.fillna('_Z')
df_lfs_emp = clean_dataframe(df_lfs_emp, col_to_check="Value", invalid_value="_Z")

# rename columns
emp_names = ['Year', 'Region', 'TOT_EMP', 'UNDERMP_PT_WORK', 'UNDERMP_PT_WORK_SUB', 'WORK_FOR_MORE_HOURS', 
             'LOOKING_FOR_ANOTHER_JOB', 'HAVE_MORE_THAN_ONE_JOB_OR_BUSINESS', 'WORK_WITHOUT_SSN', 
             'Education_Level_Main', 'Education_Level_Sub', 'Unit_of_Measure', 'Value', 'Sex', 'Age_Group']
df_lfs_emp.columns = emp_names

# print columns
print("Columns in EMP dataset:")
print(df_lfs_emp.columns)

print("\n" + "="*50)
print("PROCESSING JOB DATASETS")
print("="*50)

# print column names of all job datasets
print("Columns in JOB dataset (Regio):")
job_regio_new_columns = ['Year', 'Region', 'TOT_EMP', 'NR_PERSONS_LOCAL_UNIT', 'BO', 'SECTOR', 'SECTOR_SUB', 
                         'TYPE_OCCUPATION', 'Main_Employment_Status', 'Employment_Distinction', 'REASONS_PT', 
                         'PERMANENCY_FOR_EMPLOYEES', 'PERMANENCY_FOR_EMPLOYEES_SUB', 'REASONS_TEMP', 
                         'HOURS_ACTUALLY_WORK', 'HOURS_ACTUALLY_WORK_SUB', 'HOURS_USUAL_WORK', 'HOURS_USUAL_WORK_SUB', 
                         'ATYPICAL_WORK', 'ATYPICAL_WORK_SUB', 'Unit_of_Measure', 'Value']
df_lfs_job_regio.columns = job_regio_new_columns
print(df_lfs_job_regio.columns)

print("Columns in JOB dataset (SexAge):")
job_sexage_new_columns = ['Year', 'Sex', 'Age_Group', 'TOT_EMP', 'NR_PERSONS_LOCAL_UNIT', 'BO', 'SECTOR', 'SECTOR_SUB', 
                          'TYPE_OCCUPATION', 'Main_Employment_Status', 'Employment_Distinction', 'REASONS_PT', 
                          'PERMANENCY_FOR_EMPLOYEES', 'PERMANENCY_FOR_EMPLOYEES_SUB', 'REASONS_TEMP', 
                          'HOURS_ACTUALLY_WORK', 'HOURS_ACTUALLY_WORK_SUB', 'HOURS_USUAL_WORK', 'HOURS_USUAL_WORK_SUB', 
                          'ATYPICAL_WORK', 'ATYPICAL_WORK_SUB', 'Unit_of_Measure', 'Value']
df_lfs_job_sexage.columns = job_sexage_new_columns
print(df_lfs_job_sexage.columns)

print("Columns in JOB dataset (Occup):")
job_occup_new_columns = ['Year', 'TYPE_OCCUPATION', 'TOT_EMP', 'NR_PERSONS_LOCAL_UNIT', 'BO', 'SECTOR', 'SECTOR_SUB', 
                         'Main_Employment_Status', 'Employment_Distinction', 'REASONS_PT', 'PERMANENCY_FOR_EMPLOYEES', 
                         'PERMANENCY_FOR_EMPLOYEES_SUB', 'REASONS_TEMP', 'HOURS_ACTUALLY_WORK', 'HOURS_ACTUALLY_WORK_SUB', 
                         'HOURS_USUAL_WORK', 'HOURS_USUAL_WORK_SUB', 'ATYPICAL_WORK', 'ATYPICAL_WORK_SUB', 
                         'UNDERMP_PT_WORK', 'UNDERMP_PT_WORK_SUB', 'WORK_FOR_MORE_HOURS', 'LOOKING_FOR_ANOTHER_JOB', 
                         'HAVE_MORE_THAN_ONE_JOB_OR_BUSINESS', 'WORK_WITHOUT_SSN', 'Unit_of_Measure', 'Value']
df_lfs_job_occup.columns = job_occup_new_columns
print(df_lfs_job_occup.columns)

# Step 1: find common columns between regio and sexage
common_regio_sexage = set(df_lfs_job_regio.columns) & set(df_lfs_job_sexage.columns)
print("Common columns REGIO vs SEXAGE:", common_regio_sexage)

# Merge them first
df_lfs_job = df_lfs_job_regio.merge(df_lfs_job_sexage, on=list(common_regio_sexage), how='outer')

# Step 2: find common columns between the merged result and occup
common_job_occup = set(df_lfs_job.columns) & set(df_lfs_job_occup.columns)
print("Common columns JOB vs OCCUP:", common_job_occup)

# Merge with occup
df_lfs_job = df_lfs_job.merge(df_lfs_job_occup, on=list(common_job_occup), how='outer')

# fill NaN cells with _Z
df_lfs_job = df_lfs_job.fillna('_Z')
df_lfs_job = clean_dataframe(df_lfs_job, col_to_check="Value", invalid_value="_Z")

# print columns
print("Columns in JOB dataset:")
print(df_lfs_job.columns)

print("\n" + "="*50)
print("PROCESSING DEMO DATASETS")
print("="*50)

# print column names
print("Columns in OCCUP dataset:")
occup_demo_new_names = ['Year', 'TYPE_OCCUPATION', 'TOT_EMP', 'Sex', 'Sex_sub', 'Age_Group', 'Age_Group_sub', 
                        'Nationality', 'Education_Level_Main', 'Education_Level_Sub', 'Region', 'Regional_unit', 
                        'Region_1981', 'Region_1981_sub', 'Urbanization', 'Unit_of_Measure', 'Value']
df_lfs_occup_demo.columns = occup_demo_new_names
print(df_lfs_occup_demo.columns)

print("Columns in SECTOR dataset:")
sector_demo_new_names = ['Year', 'SECTOR', 'TOT_EMP', 'Sex', 'Sex_sub', 'Age_Group', 'Age_Group_sub', 
                         'Nationality', 'Education_Level_Main', 'Education_Level_Sub', 'Region', 'Regional_unit', 
                         'Region_1981', 'Region_1981_sub', 'Urbanization', 'Unit_of_Measure', 'Value']
df_lfs_sector_demo.columns = sector_demo_new_names
print(df_lfs_sector_demo.columns)

# find common columns
common_columns_occup_sector = set(df_lfs_occup_demo.columns) & set(df_lfs_sector_demo.columns)
print("Common columns OCCUP vs SECTOR:", common_columns_occup_sector)

# Merge with sector
df_lfs_demo = df_lfs_occup_demo.merge(df_lfs_sector_demo, on=list(common_columns_occup_sector), how='outer')

# fill in NaN values
df_lfs_demo = df_lfs_demo.fillna('_Z')
df_lfs_demo = clean_dataframe(df_lfs_demo, col_to_check="Value", invalid_value="_Z")

# print columns
print("Columns in DEMO dataset:")
print(df_lfs_demo.columns)

print("\n" + "="*50)
print("PROCESSING POPUL DATASETS")
print("="*50)

# find all common columns between the datasets
common_columns = set(df_lfs_popul_regio.columns) & set(df_lfs_popul_status.columns)
print("Common columns REGIO vs STATUS:", common_columns)

# Merge with status
df_lfs_popul = df_lfs_popul_regio.merge(df_lfs_popul_status, on=list(common_columns), how='outer')

# Fill in NaN values
df_lfs_popul = df_lfs_popul.fillna('_Z')
df_lfs_popul = clean_dataframe(df_lfs_popul, col_to_check="Value", invalid_value="_Z")

# print columns
print("Columns in POPUL dataset:")
print(df_lfs_popul.columns)

print("\n" + "="*50)
print("PROCESSING STATUS DATASETS")
print("="*50)

# find all common columns list them
common_columns_status = set(df_lfs_status_regio.columns) & set(df_lfs_status_sexage.columns)
print("Common columns STATUS REGIO vs STATUS SEXAGE:", common_columns_status)

# Merge with sexage
df_lfs_status = df_lfs_status_regio.merge(df_lfs_status_sexage, on=list(common_columns_status), how='outer')

# Fill in NaN values
df_lfs_status = df_lfs_status.fillna('_Z')
df_lfs_status = clean_dataframe(df_lfs_status, col_to_check="Value", invalid_value="_Z")

# print columns
print("Columns in STATUS dataset:")
print(df_lfs_status.columns)

print("\n" + "="*50)
print("FINAL MERGE OF ALL DATASETS")
print("="*50)

# Now merge all the processed datasets
print("Merging all datasets...")

# Start with EDUC
final_merged = df_lfs_educ.copy()
print(f"Starting with EDUC: {final_merged.shape}")

# Merge with EMP
common_educ_emp = set(final_merged.columns) & set(df_lfs_emp.columns)
print(f"Common columns EDUC vs EMP: {len(common_educ_emp)}")
final_merged = final_merged.merge(df_lfs_emp, on=list(common_educ_emp), how='outer', suffixes=('', '_emp'))
print(f"After EMP merge: {final_merged.shape}")

# Merge with JOB
common_merged_job = set(final_merged.columns) & set(df_lfs_job.columns)
print(f"Common columns MERGED vs JOB: {len(common_merged_job)}")
final_merged = final_merged.merge(df_lfs_job, on=list(common_merged_job), how='outer', suffixes=('', '_job'))
print(f"After JOB merge: {final_merged.shape}")

# Merge with DEMO
common_merged_demo = set(final_merged.columns) & set(df_lfs_demo.columns)
print(f"Common columns MERGED vs DEMO: {len(common_merged_demo)}")
final_merged = final_merged.merge(df_lfs_demo, on=list(common_merged_demo), how='outer', suffixes=('', '_demo'))
print(f"After DEMO merge: {final_merged.shape}")

# Merge with POPUL
common_merged_popul = set(final_merged.columns) & set(df_lfs_popul.columns)
print(f"Common columns MERGED vs POPUL: {len(common_merged_popul)}")
final_merged = final_merged.merge(df_lfs_popul, on=list(common_merged_popul), how='outer', suffixes=('', '_popul'))
print(f"After POPUL merge: {final_merged.shape}")

# Merge with STATUS
common_merged_status = set(final_merged.columns) & set(df_lfs_status.columns)
print(f"Common columns MERGED vs STATUS: {len(common_merged_status)}")
final_merged = final_merged.merge(df_lfs_status, on=list(common_merged_status), how='outer', suffixes=('', '_status'))
print(f"After STATUS merge: {final_merged.shape}")

# Final cleaning
print("\nFinal cleaning...")
final_merged = final_merged.fillna('_Z')
final_merged = clean_dataframe(final_merged, col_to_check="Value", invalid_value="_Z")

# Drop specified columns after finalization
print("\nDropping specified columns...")
columns_to_drop = [
    'Tertiary_30_34', 
    'Lifelong_20_64', 
    'TOT_EMP', 
    'UNDERMP_PT_WORK', 
    'HAVE_MORE_THAN_ONE_JOB_OR_BUSINESS',
    'WORK_WITHOUT_SSN', 
    'Sex_sub', 
    'Age_Group_sub', 
    'Regional_unit', 
    'Region_1981_sub'
]

# Check which columns actually exist before dropping
existing_columns_to_drop = [col for col in columns_to_drop if col in final_merged.columns]
non_existing_columns = [col for col in columns_to_drop if col not in final_merged.columns]

if existing_columns_to_drop:
    print(f"Dropping columns: {existing_columns_to_drop}")
    final_merged = final_merged.drop(columns=existing_columns_to_drop)
else:
    print("No specified columns found to drop")

if non_existing_columns:
    print(f"Warning: These columns were not found: {non_existing_columns}")

print(f"After dropping columns: {final_merged.shape}")

# Apply comprehensive masking to all applicable columns
final_merged = apply_comprehensive_masking(final_merged)

print(f"Remaining columns: {list(final_merged.columns)}")

print(f"\nFinal merged dataset: {final_merged.shape}")
print(f"Columns: {list(final_merged.columns)}")

# Save to Excel
output_filename = "test_LFS_annual.xlsx"
print(f"\nSaving to {output_filename}...")
final_merged.to_excel(output_filename, index=False)
print(f"Successfully saved to {output_filename}")

# Generate markdown report
print("\nGenerating markdown report...")

def generate_markdown_report(df, filename="LFS_Annual_Report.md"):
    """Generate a markdown report for categorical columns"""
    
    # Identify categorical columns (non-numeric, non-date)
    categorical_cols = []
    for col in df.columns:
        if df[col].dtype == 'object':
            categorical_cols.append(col)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("# LFS Annual Dataset Report\n\n")
        f.write(f"Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write(f"## Dataset Overview\n")
        f.write(f"- Total rows: {len(df):,}\n")
        f.write(f"- Total columns: {len(df.columns)}\n")
        f.write(f"- Categorical columns: {len(categorical_cols)}\n\n")
        
        f.write("## Categorical Columns Analysis\n\n")
        
        for col in categorical_cols:
            if col == 'Value':
                continue
            f.write(f"### {col}\n")
            
            # Get unique values and counts
            value_counts = df[col].value_counts(dropna=False)
            
            f.write(f"- **Total unique values:** {len(value_counts)}\n")
            f.write(f"- **Missing values:** {df[col].isna().sum():,}\n")
            f.write(f"- **Top 60 values:**\n")
            
            # Show top 10 values
            for i, (value, count) in enumerate(value_counts.head(60).items()):
                percentage = (count / len(df)) * 100
                if pd.isna(value):
                    f.write(f"  {i+1}. `NULL/Missing`: {count:,} ({percentage:.2f}%)\n")
                else:
                    f.write(f"  {i+1}. `{str(value)}`: {count:,} ({percentage:.2f}%)\n")
            
            f.write("\n---\n\n")
    
    print(f"Markdown report generated: {filename}")

generate_markdown_report(final_merged, "LFS_Annual_Report.md")

print("\nProcess completed successfully!")
print(f"- Excel file: {output_filename}")
print(f"- Markdown report: LFS_Annual_Report.md")
print(f"- Final dataset: {len(final_merged):,} rows × {len(final_merged.columns)} columns")
