import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')


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

# Apply masking to Region column
print("\nApplying masking to Region column...")
from lfs_utils.masking_config import apply_region_masking, apply_education_masking

if 'Region' in final_merged.columns:
    final_merged = apply_region_masking(final_merged, 'Region')
else:
    print("Warning: Region column not found in dataset")

# Apply masking to Education_Level_Main column
print("\nApplying masking to Education_Level_Main column...")
from lfs_utils.masking_config import apply_region_masking, apply_education_masking, apply_education_sub_masking

if 'Education_Level_Main' in final_merged.columns:
    final_merged = apply_education_masking(final_merged, 'Education_Level_Main')
else:
    print("Warning: Education_Level_Main column not found in dataset")

# Apply masking to Education_Level_Sub column
print("\nApplying masking to Education_Level_Sub column...")
from lfs_utils.masking_config import apply_region_masking, apply_education_masking, apply_education_sub_masking, apply_formal_informal_education_masking

if 'Education_Level_Sub' in final_merged.columns:
    final_merged = apply_education_sub_masking(final_merged, 'Education_Level_Sub')
else:
    print("Warning: Education_Level_Sub column not found in dataset")

# Apply masking to Formal_Informal_Education column
print("\nApplying masking to Formal_Informal_Education column...")
from lfs_utils.masking_config import apply_region_masking, apply_education_masking, apply_education_sub_masking, apply_formal_informal_education_masking, apply_neet_category_masking

if 'Formal_Informal_Education' in final_merged.columns:
    final_merged = apply_formal_informal_education_masking(final_merged, 'Formal_Informal_Education')
else:
    print("Warning: Formal_Informal_Education column not found in dataset")

# Apply masking to NEET_Category column
print("\nApplying masking to NEET_Category column...")
from lfs_utils.masking_config import apply_region_masking, apply_education_masking, apply_education_sub_masking, apply_formal_informal_education_masking, apply_neet_category_masking, apply_sex_masking

if 'NEET_Category' in final_merged.columns:
    final_merged = apply_neet_category_masking(final_merged, 'NEET_Category')
else:
    print("Warning: NEET_Category column not found in dataset")

# Apply masking to Sex column
print("\nApplying masking to Sex column...")
from lfs_utils.masking_config import apply_region_masking, apply_education_masking, apply_education_sub_masking, apply_formal_informal_education_masking, apply_neet_category_masking, apply_sex_masking, apply_age_group_masking

if 'Sex' in final_merged.columns:
    final_merged = apply_sex_masking(final_merged, 'Sex')
else:
    print("Warning: Sex column not found in dataset")

# Apply masking to Age_Group column
print("\nApplying masking to Age_Group column...")
from lfs_utils.masking_config import apply_region_masking, apply_education_masking, apply_education_sub_masking, apply_formal_informal_education_masking, apply_neet_category_masking, apply_sex_masking, apply_age_group_masking, apply_main_employment_status_masking

if 'Age_Group' in final_merged.columns:
    final_merged = apply_age_group_masking(final_merged, 'Age_Group')
else:
    print("Warning: Age_Group column not found in dataset")

# Apply masking to Main_Employment_Status column
print("\nApplying masking to Main_Employment_Status column...")
from lfs_utils.masking_config import apply_region_masking, apply_education_masking, apply_education_sub_masking, apply_formal_informal_education_masking, apply_neet_category_masking, apply_sex_masking, apply_age_group_masking, apply_main_employment_status_masking, apply_sub_employment_status_masking

if 'Main_Employment_Status' in final_merged.columns:
    final_merged = apply_main_employment_status_masking(final_merged, 'Main_Employment_Status')
else:
    print("Warning: Main_Employment_Status column not found in dataset")

# Apply masking to Sub_Employment_Status column
print("\nApplying masking to Sub_Employment_Status column...")
from lfs_utils.masking_config import apply_region_masking, apply_education_masking, apply_education_sub_masking, apply_formal_informal_education_masking, apply_neet_category_masking, apply_sex_masking, apply_age_group_masking, apply_main_employment_status_masking, apply_sub_employment_status_masking, apply_undermp_pt_work_sub_masking

if 'Sub_Employment_Status' in final_merged.columns:
    final_merged = apply_sub_employment_status_masking(final_merged, 'Sub_Employment_Status')
else:
    print("Warning: Sub_Employment_Status column not found in dataset")

# Apply masking to UNDERMP_PT_WORK_SUB column
print("\nApplying masking to UNDERMP_PT_WORK_SUB column...")
from lfs_utils.masking_config import apply_region_masking, apply_education_masking, apply_education_sub_masking, apply_formal_informal_education_masking, apply_neet_category_masking, apply_sex_masking, apply_age_group_masking, apply_main_employment_status_masking, apply_sub_employment_status_masking, apply_undermp_pt_work_sub_masking, apply_work_for_more_hours_masking

if 'UNDERMP_PT_WORK_SUB' in final_merged.columns:
    final_merged = apply_undermp_pt_work_sub_masking(final_merged, 'UNDERMP_PT_WORK_SUB')
else:
    print("Warning: UNDERMP_PT_WORK_SUB column not found in dataset")

# Apply masking to WORK_FOR_MORE_HOURS column
print("\nApplying masking to WORK_FOR_MORE_HOURS column...")
from lfs_utils.masking_config import apply_region_masking, apply_education_masking, apply_education_sub_masking, apply_formal_informal_education_masking, apply_neet_category_masking, apply_sex_masking, apply_age_group_masking, apply_main_employment_status_masking, apply_sub_employment_status_masking, apply_undermp_pt_work_sub_masking, apply_work_for_more_hours_masking, apply_looking_for_another_job_masking

if 'WORK_FOR_MORE_HOURS' in final_merged.columns:
    final_merged = apply_work_for_more_hours_masking(final_merged, 'WORK_FOR_MORE_HOURS')
else:
    print("Warning: WORK_FOR_MORE_HOURS column not found in dataset")

# Apply masking to LOOKING_FOR_ANOTHER_JOB column
print("\nApplying masking to LOOKING_FOR_ANOTHER_JOB column...")
from lfs_utils.masking_config import apply_region_masking, apply_education_masking, apply_education_sub_masking, apply_formal_informal_education_masking, apply_neet_category_masking, apply_sex_masking, apply_age_group_masking, apply_main_employment_status_masking, apply_sub_employment_status_masking, apply_undermp_pt_work_sub_masking, apply_work_for_more_hours_masking, apply_looking_for_another_job_masking, apply_unit_of_measure_masking

if 'LOOKING_FOR_ANOTHER_JOB' in final_merged.columns:
    final_merged = apply_looking_for_another_job_masking(final_merged, 'LOOKING_FOR_ANOTHER_JOB')
else:
    print("Warning: LOOKING_FOR_ANOTHER_JOB column not found in dataset")

# Apply masking to Unit_of_Measure column
print("\nApplying masking to Unit_of_Measure column...")
from lfs_utils.masking_config import apply_region_masking, apply_education_masking, apply_education_sub_masking, apply_formal_informal_education_masking, apply_neet_category_masking, apply_sex_masking, apply_age_group_masking, apply_main_employment_status_masking, apply_sub_employment_status_masking, apply_undermp_pt_work_sub_masking, apply_work_for_more_hours_masking, apply_looking_for_another_job_masking, apply_unit_of_measure_masking, apply_nr_persons_local_unit_masking

if 'Unit_of_Measure' in final_merged.columns:
    final_merged = apply_unit_of_measure_masking(final_merged, 'Unit_of_Measure')
else:
    print("Warning: Unit_of_Measure column not found in dataset")

# Apply masking to NR_PERSONS_LOCAL_UNIT column
print("\nApplying masking to NR_PERSONS_LOCAL_UNIT column...")
from lfs_utils.masking_config import apply_region_masking, apply_education_masking, apply_education_sub_masking, apply_formal_informal_education_masking, apply_neet_category_masking, apply_sex_masking, apply_age_group_masking, apply_main_employment_status_masking, apply_sub_employment_status_masking, apply_undermp_pt_work_sub_masking, apply_work_for_more_hours_masking, apply_looking_for_another_job_masking, apply_unit_of_measure_masking, apply_nr_persons_local_unit_masking, apply_bo_masking

if 'NR_PERSONS_LOCAL_UNIT' in final_merged.columns:
    final_merged = apply_nr_persons_local_unit_masking(final_merged, 'NR_PERSONS_LOCAL_UNIT')
else:
    print("Warning: NR_PERSONS_LOCAL_UNIT column not found in dataset")

# Apply masking to BO column
print("\nApplying masking to BO column...")
from lfs_utils.masking_config import apply_region_masking, apply_education_masking, apply_education_sub_masking, apply_formal_informal_education_masking, apply_neet_category_masking, apply_sex_masking, apply_age_group_masking, apply_main_employment_status_masking, apply_sub_employment_status_masking, apply_undermp_pt_work_sub_masking, apply_work_for_more_hours_masking, apply_looking_for_another_job_masking, apply_unit_of_measure_masking, apply_nr_persons_local_unit_masking, apply_bo_masking, apply_sector_masking

if 'BO' in final_merged.columns:
    final_merged = apply_bo_masking(final_merged, 'BO')
else:
    print("Warning: BO column not found in dataset")

# Apply masking to SECTOR column
print("\nApplying masking to SECTOR column...")
from lfs_utils.masking_config import apply_region_masking, apply_education_masking, apply_education_sub_masking, apply_formal_informal_education_masking, apply_neet_category_masking, apply_sex_masking, apply_age_group_masking, apply_main_employment_status_masking, apply_sub_employment_status_masking, apply_undermp_pt_work_sub_masking, apply_work_for_more_hours_masking, apply_looking_for_another_job_masking, apply_unit_of_measure_masking, apply_nr_persons_local_unit_masking, apply_bo_masking, apply_sector_masking, apply_sector_sub_masking

if 'SECTOR' in final_merged.columns:
    final_merged = apply_sector_masking(final_merged, 'SECTOR')
else:
    print("Warning: SECTOR column not found in dataset")

# Apply masking to SECTOR_SUB column
print("\nApplying masking to SECTOR_SUB column...")
from lfs_utils.masking_config import apply_region_masking, apply_education_masking, apply_education_sub_masking, apply_formal_informal_education_masking, apply_neet_category_masking, apply_sex_masking, apply_age_group_masking, apply_main_employment_status_masking, apply_sub_employment_status_masking, apply_undermp_pt_work_sub_masking, apply_work_for_more_hours_masking, apply_looking_for_another_job_masking, apply_unit_of_measure_masking, apply_nr_persons_local_unit_masking, apply_bo_masking, apply_sector_masking, apply_sector_sub_masking, apply_type_occupation_masking

if 'SECTOR_SUB' in final_merged.columns:
    final_merged = apply_sector_sub_masking(final_merged, 'SECTOR_SUB')
else:
    print("Warning: SECTOR_SUB column not found in dataset")

# Apply masking to TYPE_OCCUPATION column
print("\nApplying masking to TYPE_OCCUPATION column...")
if 'TYPE_OCCUPATION' in final_merged.columns:
    final_merged = apply_type_occupation_masking(final_merged, 'TYPE_OCCUPATION')
else:
    print("Warning: TYPE_OCCUPATION column not found in dataset")

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
