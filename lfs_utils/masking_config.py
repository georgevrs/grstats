# Masking configuration for LFS datasets
# This file contains mappings for data cleaning and standardization

# Region column masking configuration
REGION_MASKING = {
    # Special processing codes -> Greece total
    '_Z': 'EL',  # Special processing code -> Greece total
    'COUNTRY TOTAL': 'EL',  # Country total -> Greece total
    
    # Direct mappings to codelist values
    'Ipeiros': 'EL21',
    'Thessalia': 'EL14', 
    'Kriti': 'EL43',
    'Ionia Nissia': 'EL22',
    'Voreio Aigaio': 'EL41',
    'Dytiki Makedonia': 'EL13',
    'Notio Aigaio': 'EL42',
    'Sterea Ellada': 'EL24',
    'Peloponnisos': 'EL25',
    'Anatoliki Makedonia-Thraki': 'EL11',
    'Dytiki Ellada': 'EL23',
    'Kentriki Makedonia': 'EL12',
    'Attiki': 'EL30',
    
    # Sub-regions and combined regions -> map to main regions
    'Nissia Anatolikou Aigaiou': 'EL41',  # Map to North Aegean
    'Anatoliki Makedonia': 'EL11',        # Map to Eastern Macedonia & Thrace
    'Anatoliki Sterea & Nissia': 'EL24',  # Map to Central Greece
    'Kentriki & Dytiki Makedonia': 'EL12', # Map to Central Macedonia
    'Thraki': 'EL11',                     # Map to Eastern Macedonia & Thrace
    'Peloponissos & Dytiki Sterea': 'EL25' # Map to Peloponnese
}

# Education level masking configuration
EDUCATION_MASKING = {
    # Special processing codes
    '_Z': '_Z',  # Special processing code -> Not elsewhere classified
    
    # Direct mappings to codelist values
    'Attended no school / Did not complete primary education': 'ED0',  # No formal education
    'Primary': 'ED1',  # Primary education
    'Lower secondary': 'ED2',  # Lower secondary education
    'Upper secondary & post secondary': 'ED3',  # Upper secondary and post-secondary
    'Tertiary': 'ED5',  # Bachelor's or equivalent level
    'Postgraduate degrees (including integrated Master\'s degrees)': 'ED7'  # Doctoral or equivalent level
}

# Education sub-level masking configuration
EDUCATION_SUB_MASKING = {
    # Special processing codes
    '_Z': '_Z',  # Special processing code -> Not applicable
    
    # Primary education sub-levels (keep as is - these are already proper codes)
    'ekp1': 'ekp1',  # Primary education - Year 1
    'ekp2': 'ekp2',  # Primary education - Year 2
    'ekp3': 'ekp3',  # Primary education - Year 3
    'ekp4': 'ekp4',  # Primary education - Year 4
    'ekp7': 'ekp7',  # Primary education - Year 7
    
    # Secondary education sub-levels
    'Upper secondary': 'UPPER_SEC',  # Upper secondary education
    'Post secondary vocational': 'POST_SEC_VOC',  # Post-secondary vocational education
    
    # Tertiary education sub-levels
    'University degree': 'UNIV_DEGREE',  # University degree
    'Postgraduate degrees (Μaster / PhD)': 'POSTGRAD_DEGREE'  # Postgraduate degrees
}

# Formal/Informal education masking configuration
FORMAL_INFORMAL_EDUCATION_MASKING = {
    # Special processing codes
    '_Z': '_Z',  # Special processing code -> Not applicable
    
    # Education participation categories
    'Total': 'TOTAL',  # Total population in education
    'in formal education': 'FORMAL_EDU',  # In formal education
    'in informal education': 'INFORMAL_EDU',  # In informal education
    
    # Employment status subcategories
    'of them Inactive': 'INACTIVE',  # Of them - Inactive
    'of them Unemployed': 'UNEMPLOYED',  # Of them - Unemployed
    'of them Employed': 'EMPLOYED'  # Of them - Employed
}

# NEET category masking configuration
NEET_CATEGORY_MASKING = {
    # Special processing codes
    '_Z': '_Z',  # Special processing code -> Not applicable
    
    # NEET categories
    'Total': 'TOTAL',  # Total NEET population
    'Seek job but not available': 'SEEK_JOB_NOT_AVAIL',  # Seek job but not available
    'Unemployed': 'UNEMPLOYED',  # Unemployed
    'Like to work but not seek job': 'LIKE_WORK_NOT_SEEK',  # Like to work but not seek job
    'Other': 'OTHER'  # Other NEET categories
}

# Sex masking configuration
SEX_MASKING = {
    # Special processing codes
    '_Z': 'T',  # Special processing code -> Total
    
    # Sex categories
    'Men': 'M',  # Men
    'Women': 'F',  # Women
    'Females': 'F',  # Females
    'Males': 'M',  # Males
    'Total': 'T',  # Total
    'YEAR TOTAL': 'T'  # Year total
}

# Age Group masking configuration
AGE_GROUP_MASKING = {
    # Special processing codes
    '_Z': 'TOTAL',  # Special processing code -> Total
    
    # Age group categories
    '15-19': 'Y15-19',  # 15-19 years
    '20-24': 'Y20-24',  # 20-24 years
    '25-29': 'Y25-29',  # 25-29 years
    '30-44': 'Y30-44',  # 30-44 years
    '45-64': 'Y45-64',  # 45-64 years
    '65+': 'Y65',  # 65+ years
    '14': 'Y14',  # 14 years
    '0-14': 'Y0-14',  # 0-14 years
    
    # Total categories
    'Total Females': 'TOTAL',  # Total Females
    'Total Males': 'TOTAL',  # Total Males
    'Total': 'TOTAL'  # Total
}

# Main Employment Status masking configuration
MAIN_EMPLOYMENT_STATUS_MASKING = {
    # Special processing codes
    '_Z': '_Z',  # Special processing code -> Not applicable
    
    # Employment status categories
    'Employed': 'EMPLOYED',  # Employed
    'Employees': 'EMPLOYEES',  # Employees
    'Self employed without employees': 'SELF_EMPLOYED_NO_EMP',  # Self-employed without employees
    'Self employed with employees': 'SELF_EMPLOYED_WITH_EMP',  # Self-employed with employees
    'Family workers': 'FAMILY_WORKERS',  # Family workers
    'Unemployed': 'UNEMPLOYED',  # Unemployed
    'Inactive': 'INACTIVE',  # Inactive
    'TOTAL POPULATION AGED 15+': 'TOTAL_POP_15PLUS'  # Total population aged 15+
}

# Sub Employment Status masking configuration
SUB_EMPLOYMENT_STATUS_MASKING = {
    # Special processing codes
    '_Z': '_Z',  # Special processing code -> Not applicable
    
    # Total categories
    'Total': 'TOTAL',  # Total
    
    # Employment type categories
    'Full-time employed': 'FULL_TIME_EMPLOYED',  # Full-time employed
    'Part-time employed': 'PART_TIME_EMPLOYED',  # Part-time employed
    'Permanent job': 'PERMANENT_JOB',  # Permanent job
    'Temporary job': 'TEMPORARY_JOB',  # Temporary job
    
    # Employment status subcategories
    'Employees': 'EMPLOYEES',  # Employees
    'Self employed': 'SELF_EMPLOYED',  # Self employed
    'Family workers': 'FAMILY_WORKERS',  # Family workers
    
    # Unemployment subcategories
    'New unemployed': 'NEW_UNEMPLOYED',  # New unemployed
    'Long-term unemployed': 'LONG_TERM_UNEMPLOYED'  # Long-term unemployed
}

# UNDERMP_PT_WORK_SUB masking configuration
UNDERMP_PT_WORK_SUB_MASKING = {
    # Special processing codes
    '_Z': '_Z',  # Special processing code -> Not applicable
    
    # Underemployment part-time work categories
    'Yes': 'YES',  # Yes - working part-time due to underemployment
    'No': 'NO'  # No - working part-time for other reasons
}

# WORK_FOR_MORE_HOURS masking configuration
WORK_FOR_MORE_HOURS_MASKING = {
    # Special processing codes
    '_Z': '_Z',  # Special processing code -> Not applicable
    
    # Work hours availability categories
    'Available to work more than the current number of hours': 'AVAILABLE_MORE_HOURS',  # Available to work more hours
    'Wish to work usually more than the current number of hours': 'WISH_MORE_HOURS'  # Wish to work more hours
}

# LOOKING_FOR_ANOTHER_JOB masking configuration
LOOKING_FOR_ANOTHER_JOB_MASKING = {
    # Special processing codes
    '_Z': '_Z',  # Special processing code -> Not applicable
    
    # Total categories
    'Total': 'TOTAL',  # Total
    
    # Job search motivation categories
    'Of wish to have better working condition': 'BETTER_WORKING_CONDITIONS',  # Better working conditions
    'Actual job is considered as a transitional job': 'TRANSITIONAL_JOB',  # Transitional job
    'Seeking an additional job': 'SEEKING_ADDITIONAL_JOB',  # Seeking additional job
    'Other reasons': 'OTHER_REASONS',  # Other reasons
    'Risk or certainty of loss or termination of present job': 'JOB_LOSS_RISK'  # Job loss risk or certainty
}

# Unit of Measure masking configuration
UNIT_OF_MEASURE_MASKING = {
    # Unit of measure categories
    'persons': 'THS',  # Persons -> Thousands
    '_Z': 'THS',  # Special processing code -> Thousands
    'percentage': 'PC'  # Percentage -> Percentage
}

# NR_PERSONS_LOCAL_UNIT masking configuration
NR_PERSONS_LOCAL_UNIT_MASKING = {
    # Special processing codes
    '_Z': '_Z',  # Special processing code -> Not applicable
    
    # Local unit size categories
    'Up to 10 persons': 'UP_TO_10',  # Up to 10 persons
    '11 to 19 persons': '11_TO_19',  # 11 to 19 persons
    '20 to 49 persons': '20_TO_49',  # 20 to 49 persons
    '50 persons or more': '50_OR_MORE',  # 50 persons or more
    'Do not know but more than 10 person': 'UNKNOWN_MORE_THAN_10'  # Unknown but more than 10 persons
}

# BO (Business Ownership) masking configuration
BO_MASKING = {
    # Special processing codes
    '_Z': '_Z',  # Special processing code -> Not applicable
    
    # Business ownership categories
    'Private sector': 'PRIVATE_SECTOR',  # Private sector
    'Public sector': 'PUBLIC_SECTOR'  # Public sector
}

# SECTOR masking configuration
SECTOR_MASKING = {
    # Special processing codes
    '_Z': '_Z',  # Special processing code -> Not applicable
    
    # Total categories
    'TOTAL EMPLOYED': 'TOTAL_EMPLOYED',  # Total employed
    
    # Broad sector groupings
    'Primary': 'PRIMARY',  # Primary sector
    'Secondary': 'SECONDARY',  # Secondary sector
    'Tertiary': 'TERTIARY',  # Tertiary sector
    
    # NACE-68 classifications
    'NACE-68: Agriculture, Forestry, Hunting and Fishing': 'NACE68_AGRICULTURE',
    'NACE-68: Mining and Quarrying': 'NACE68_MINING',
    'NACE-68: Manufacturing': 'NACE68_MANUFACTURING',
    'NACE-68: Electricity, Gas, Steam and Water': 'NACE68_ELECTRICITY',
    'NACE-68: Construction': 'NACE68_CONSTRUCTION',
    'NACE-68: Wholesale and Retail Trade and Restaurants and Hotels': 'NACE68_TRADE',
    'NACE-68: Transport, Storage and Communication': 'NACE68_TRANSPORT',
    'NACE-68: Financing, Insurance, Real Estate and Business Services': 'NACE68_FINANCE',
    'NACE-68: Services': 'NACE68_SERVICES',
    'NACE-68: Activities not adequately described': 'NACE68_ACTIVITIES_NAD',
    
    # NACE rev2 classifications
    'NACE rev2: Agriculture, forestry and fishing': 'NACE2_AGRICULTURE',
    'NACE rev2: Mining and quarrying': 'NACE2_MINING',
    'NACE rev2: Manufacturing': 'NACE2_MANUFACTURING',
    'NACE rev2: Electricity, gas, steam and air conditioning supply': 'NACE2_ELECTRICITY',
    'NACE rev2: Water supply; sewerage, waste management and remediation activities': 'NACE2_WATER',
    'NACE rev2: Construction': 'NACE2_CONSTRUCTION',
    'NACE rev2: Wholesale and retail trade; repair of motor vehicles and motorcycles': 'NACE2_TRADE',
    'NACE rev2: Accommodation and food service activities': 'NACE2_ACCOMMODATION',
    'NACE rev2: Transportation and storage': 'NACE2_TRANSPORT',
    'NACE rev2: Information and communication': 'NACE2_COMMUNICATION',
    'NACE rev2: Financial and insurance activities': 'NACE2_FINANCE',
    'NACE rev2: Real estate activities': 'NACE2_REAL_ESTATE',
    'NACE rev2: Professional, scientific and technical activities': 'NACE2_PROFESSIONAL',
    'NACE rev2: Administrative and support service activities': 'NACE2_ADMINISTRATIVE',
    'NACE rev2: Public administration and defence; compulsory social security': 'NACE2_PUBLIC_ADMIN',
    'NACE rev2: Education': 'NACE2_EDUCATION',
    'NACE rev2: Human health and social work activities': 'NACE2_HEALTH',
    'NACE rev2: Arts, entertainment and recreation': 'NACE2_ENTERTAINMENT',
    'NACE rev2: Other service activities': 'NACE2_OTHER_SERVICES',
    'NACE rev2: Activities of households as employers; undifferentiated goods- and services-producing activities of households': 'NACE2_HOUSEHOLDS',
    'NACE rev2: Activities of extraterritorial organisations and bodies': 'NACE2_EXTRATERRITORIAL',
    'NACE rev2: Did not answer': 'NACE2_DID_NOT_ANSWER',
    
    # NACE rev1 classifications
    'NACE rev1: Agriculture, animal husbandry, hunting and forestry': 'NACE1_AGRICULTURE',
    'NACE rev1: Fishing': 'NACE1_FISHING',
    'NACE rev1: Mining and quarrying': 'NACE1_MINING',
    'NACE rev1: Electricity, gas and water supply': 'NACE1_ELECTRICITY',
    'NACE rev1: Manufacturing': 'NACE1_MANUFACTURING',
    'NACE rev1: Construction': 'NACE1_CONSTRUCTION',
    'NACE rev1: Wholesale and retail trade; repair of motor vehicles, motorcycles and personal and household goods': 'NACE1_TRADE',
    'NACE rev1: Hotels and restaurants': 'NACE1_HOTELS',
    'NACE rev1: Transport, storage and communication': 'NACE1_TRANSPORT',
    'NACE rev1: Financial intermediation': 'NACE1_FINANCE',
    'NACE rev1: Real estate, renting and business activities': 'NACE1_REAL_ESTATE',
    'NACE rev1: Public administration and defence; compulsory social security': 'NACE1_PUBLIC_ADMIN',
    'NACE rev1: Education': 'NACE1_EDUCATION',
    'NACE rev1: Health and social work': 'NACE1_HEALTH',
    'NACE rev1: Other community, social and personal service activities': 'NACE1_OTHER_SERVICES',
    'NACE rev1: Private households with employed persons': 'NACE1_HOUSEHOLDS',
    'NACE rev1: Extra – territorial organizations and bodies': 'NACE1_EXTRATERRITORIAL'
}

# SECTOR_SUB masking configuration
SECTOR_SUB_MASKING = {
    # Special processing codes
    '_Z': '_Z',  # Special processing code -> Not applicable
    
    # Sector total categories
    'Tertiary sector total': 'TERTIARY_SECTOR_TOTAL',  # Tertiary sector total
    'Secondary sector total': 'SECONDARY_SECTOR_TOTAL',  # Secondary sector total
    
    # Primary sector subcategories
    'Agriculture, forestry and fishing': 'AGRICULTURE_FORESTRY_FISHING',  # Agriculture, forestry and fishing
    
    # Secondary sector subcategories
    'Industry including energy': 'INDUSTRY_INCLUDING_ENERGY',  # Industry including energy
    'Construction': 'CONSTRUCTION',  # Construction
    
    # Tertiary sector subcategories
    'Trade, hotels and restaurants, transport and communication': 'TRADE_HOTELS_RESTAURANTS_TRANSPORT_COMMUNICATION',  # Trade, hotels and restaurants, transport and communication
    'Financial, real estate, renting and business activities': 'FINANCIAL_REAL_ESTATE_RENTING_BUSINESS_ACTIVITIES',  # Financial, real estate, renting and business activities
    'Other service activities': 'OTHER_SERVICE_ACTIVITIES',  # Other service activities
    
    # Special categories
    'Did no answer': 'DID_NOT_ANSWER'  # Did not answer
}

# TYPE_OCCUPATION masking configuration
TYPE_OCCUPATION_MASKING = {
    # Special processing codes
    '_Z': '_Z',  # Special processing code -> Not applicable
    
    # Total categories
    'TOTAL EMPLOYED': 'TOTAL_EMPLOYED',  # Total employed
    
    # ISCO-68 classifications
    'ISCO-68: Did not answer/not possible to classify': 'ISCO68_DID_NOT_ANSWER_NOT_POSSIBLE_TO_CLASSIFY',
    'ISCO-68: Administrative and Managerial Workers': 'ISCO68_ADMINISTRATIVE_MANAGERIAL_WORKERS',
    'ISCO-68: Professional, Technical and Related Workers': 'ISCO68_PROFESSIONAL_TECHNICAL_RELATED_WORKERS',
    'ISCO-68: Clerical and Related Workers': 'ISCO68_CLERICAL_RELATED_WORKERS',
    'ISCO-68: Agricultural, Animal Husbandry and Forestry Workers, Fishermen and Hunters': 'ISCO68_AGRICULTURAL_ANIMAL_HUSBANDRY_FORESTRY_WORKERS_FISHERMEN_HUNTERS',
    'ISCO-68: Production and Related Workers, Transport Equipment Operators and Labourers': 'ISCO68_PRODUCTION_RELATED_WORKERS_TRANSPORT_EQUIPMENT_OPERATORS_LABOURERS',
    'ISCO-68: Sales Workers': 'ISCO68_SALES_WORKERS',
    'ISCO-68: Service Workers': 'ISCO68_SERVICE_WORKERS',
    
    # ISCO-88 (COM) classifications
    'ISCO-88 (COM): Did not answer/not possible to classify': 'ISCO88_DID_NOT_ANSWER_NOT_POSSIBLE_TO_CLASSIFY',
    'ISCO-88 (COM): Professionals': 'ISCO88_PROFESSIONALS',
    'ISCO-88 (COM): Plant and machine operators and assemblers': 'ISCO88_PLANT_MACHINE_OPERATORS_ASSEMBLERS',
    'ISCO-88 (COM): Skilled agricultural, forestry and fishery workers': 'ISCO88_SKILLED_AGRICULTURAL_FORESTRY_FISHERY_WORKERS',
    'ISCO-88 (COM): Technicians and associate professionals': 'ISCO88_TECHNICIANS_ASSOCIATE_PROFESSIONALS',
    'ISCO-88 (COM): Managers': 'ISCO88_MANAGERS',
    'ISCO-88 (COM): Elementary occupations': 'ISCO88_ELEMENTARY_OCCUPATIONS',
    'ISCO-88 (COM): Clerical support workers': 'ISCO88_CLERICAL_SUPPORT_WORKERS',
    'ISCO-88 (COM): Craft and related trades workers': 'ISCO88_CRAFT_RELATED_TRADES_WORKERS',
    'ISCO-88 (COM): Service and sales workers': 'ISCO88_SERVICE_SALES_WORKERS',
    
    # ISCO-08 classifications
    'ISCO-08: Managers': 'ISCO08_MANAGERS',
    'ISCO-08: Technicians and associate professionals': 'ISCO08_TECHNICIANS_ASSOCIATE_PROFESSIONALS',
    'ISCO-08: Professionals': 'ISCO08_PROFESSIONALS',
    'ISCO-08: Clerical support workers': 'ISCO08_CLERICAL_SUPPORT_WORKERS',
    'ISCO-08: Plant and machine operators and assemblers': 'ISCO08_PLANT_MACHINE_OPERATORS_ASSEMBLERS',
    'ISCO-08: Elementary occupations': 'ISCO08_ELEMENTARY_OCCUPATIONS',
    'ISCO-08: Service and sales workers': 'ISCO08_SERVICE_SALES_WORKERS',
    'ISCO-08: Skilled agricultural, forestry and fishery workers': 'ISCO08_SKILLED_AGRICULTURAL_FORESTRY_FISHERY_WORKERS',
    'ISCO-08: Craft and related trades workers': 'ISCO08_CRAFT_RELATED_TRADES_WORKERS',
    'ISCO-08: Did not answer': 'ISCO08_DID_NOT_ANSWER',
    'ISCO-08: Not possible to classify': 'ISCO08_NOT_POSSIBLE_TO_CLASSIFY',
    
    # Skill level groupings
    'Skilled manual': 'SKILLED_MANUAL',
    'Low skilled non-manual': 'LOW_SKILLED_NON_MANUAL',
    'Agriculture, forestry, animal husbandry, fishing': 'AGRICULTURE_FORESTRY_ANIMAL_HUSBANDRY_FISHING',
    'Elementary occupations': 'ELEMENTARY_OCCUPATIONS',
    'Highly skilled non-manual': 'HIGHLY_SKILLED_NON_MANUAL'
}

# REASONS_PT masking configuration
REASONS_PT_MASKING = {
    # Special processing codes
    '_Z': '_Z',  # Special processing code -> Not applicable
    
    # Economic reasons
    'Other reasons': 'OTHER_REASONS',  # Other reasons
    'Could not find a full-time job': 'COULD_NOT_FIND_FULL_TIME_JOB',  # Could not find a full-time job
    
    # Educational reasons
    'School education or training': 'SCHOOL_EDUCATION_TRAINING',  # School education or training
    
    # Health and caregiving reasons
    'Of own illness or disability': 'OWN_ILLNESS_DISABILITY',  # Of own illness or disability
    'of them, looking after children or incapacitated adults': 'LOOKING_AFTER_CHILDREN_INCAPACITATED_ADULTS'  # Of them, looking after children or incapacitated adults
}

# PERMANENCY_FOR_EMPLOYEES_SUB masking configuration
PERMANENCY_FOR_EMPLOYEES_SUB_MASKING = {
    # Special processing codes
    '_Z': '_Z',  # Special processing code -> Not applicable
    
    # Duration categories
    'Up to 6 months': 'UP_TO_6_MONTHS',  # Up to 6 months
    'From 7 to 12 months': 'FROM_7_TO_12_MONTHS',  # From 7 to 12 months
    'More than 12 months': 'MORE_THAN_12_MONTHS'  # More than 12 months
}

# REASONS_TEMP masking configuration
REASONS_TEMP_MASKING = {
    # Special processing codes
    '_Z': '_Z',  # Special processing code -> Not applicable
    
    # Economic and availability reasons
    'Could not find a permanent job': 'COULD_NOT_FIND_PERMANENT_JOB',  # Could not find a permanent job
    'Other reasons': 'OTHER_REASONS',  # Other reasons
    
    # Personal preference reasons
    'Did not want a permanent job': 'DID_NOT_WANT_PERMANENT_JOB',  # Did not want a permanent job
    
    # Training and development reasons
    'Contract covering a period of training': 'CONTRACT_COVERING_TRAINING_PERIOD'  # Contract covering a period of training
}

# Function to apply region masking
def apply_region_masking(df, region_column='Region'):
    """
    Apply region masking to standardize region values according to codelist
    
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame
    region_column : str, default 'Region'
        Name of the region column to mask
        
    Returns
    -------
    pd.DataFrame
        DataFrame with masked region column
    """
    if region_column not in df.columns:
        print(f"Warning: Column '{region_column}' not found in dataset")
        return df
    
    # Create a copy to avoid modifying original
    df_masked = df.copy()
    
    # Show current region value counts before masking
    print(f"Region values before masking:")
    region_counts_before = df_masked[region_column].value_counts()
    for region, count in region_counts_before.head(10).items():
        percentage = (count / len(df_masked)) * 100
        print(f"  {region}: {count:,} ({percentage:.2f}%)")
    
    # Apply masking
    df_masked[region_column] = df_masked[region_column].map(REGION_MASKING).fillna(df_masked[region_column])
    
    # Show region value counts after masking
    print(f"\nRegion values after masking:")
    region_counts_after = df_masked[region_column].value_counts()
    for region, count in region_counts_after.head(10).items():
        percentage = (count / len(df_masked)) * 100
        print(f"  {region}: {count:,} ({percentage:.2f}%)")
    
    # Report masking statistics
    masked_count = (df_masked[region_column] != df[region_column]).sum()
    print(f"\nTotal rows masked: {masked_count:,}")
    
    return df_masked

# Function to apply education level masking
def apply_education_masking(df, education_column='Education_Level_Main'):
    """
    Apply education level masking to standardize education values according to codelist
    
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame
    education_column : str, default 'Education_Level_Main'
        Name of the education level column to mask
        
    Returns
    -------
    pd.DataFrame
        DataFrame with masked education level column
    """
    if education_column not in df.columns:
        print(f"Warning: Column '{education_column}' not found in dataset")
        return df
    
    # Create a copy to avoid modifying original
    df_masked = df.copy()
    
    # Show current education value counts before masking
    print(f"Education level values before masking:")
    education_counts_before = df_masked[education_column].value_counts()
    for education, count in education_counts_before.head(10).items():
        percentage = (count / len(df_masked)) * 100
        print(f"  {education}: {count:,} ({percentage:.2f}%)")
    
    # Apply masking
    df_masked[education_column] = df_masked[education_column].map(EDUCATION_MASKING).fillna(df_masked[education_column])
    
    # Show education value counts after masking
    print(f"\nEducation level values after masking:")
    education_counts_after = df_masked[education_column].value_counts()
    for education, count in education_counts_after.head(10).items():
        percentage = (count / len(df_masked)) * 100
        print(f"  {education}: {count:,} ({percentage:.2f}%)")
    
    # Report masking statistics
    masked_count = (df_masked[education_column] != df[education_column]).sum()
    print(f"\nTotal rows masked: {masked_count:,}")
    
    return df_masked

# Function to apply education sub-level masking
def apply_education_sub_masking(df, education_sub_column='Education_Level_Sub'):
    """
    Apply education sub-level masking to standardize education sub-level values according to codelist
    
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame
    education_sub_column : str, default 'Education_Level_Sub'
        Name of the education sub-level column to mask
        
    Returns
    -------
    pd.DataFrame
        DataFrame with masked education sub-level column
    """
    if education_sub_column not in df.columns:
        print(f"Warning: Column '{education_sub_column}' not found in dataset")
        return df
    
    # Create a copy to avoid modifying original
    df_masked = df.copy()
    
    # Show current education sub-level value counts before masking
    print(f"Education sub-level values before masking:")
    education_sub_counts_before = df_masked[education_sub_column].value_counts()
    for education_sub, count in education_sub_counts_before.head(10).items():
        percentage = (count / len(df_masked)) * 100
        print(f"  {education_sub}: {count:,} ({percentage:.2f}%)")
    
    # Apply masking
    df_masked[education_sub_column] = df_masked[education_sub_column].map(EDUCATION_SUB_MASKING).fillna(df_masked[education_sub_column])
    
    # Show education sub-level value counts after masking
    print(f"\nEducation sub-level values after masking:")
    education_sub_counts_after = df_masked[education_sub_column].value_counts()
    for education_sub, count in education_sub_counts_after.head(10).items():
        percentage = (count / len(df_masked)) * 100
        print(f"  {education_sub}: {count:,} ({percentage:.2f}%)")
    
    # Report masking statistics
    masked_count = (df_masked[education_sub_column] != df[education_sub_column]).sum()
    print(f"\nTotal rows masked: {masked_count:,}")
    
    return df_masked

# Function to apply formal/informal education masking
def apply_formal_informal_education_masking(df, formal_informal_column='Formal_Informal_Education'):
    """
    Apply formal/informal education masking to standardize education participation values according to codelist
    
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame
    formal_informal_column : str, default 'Formal_Informal_Education'
        Name of the formal/informal education column to mask
        
    Returns
    -------
    pd.DataFrame
        DataFrame with masked formal/informal education column
    """
    if formal_informal_column not in df.columns:
        print(f"Warning: Column '{formal_informal_column}' not found in dataset")
        return df
    
    # Create a copy to avoid modifying original
    df_masked = df.copy()
    
    # Show current formal/informal education value counts before masking
    print(f"Formal/Informal education values before masking:")
    formal_informal_counts_before = df_masked[formal_informal_column].value_counts()
    for formal_informal, count in formal_informal_counts_before.head(10).items():
        percentage = (count / len(df_masked)) * 100
        print(f"  {formal_informal}: {count:,} ({percentage:.2f}%)")
    
    # Apply masking
    df_masked[formal_informal_column] = df_masked[formal_informal_column].map(FORMAL_INFORMAL_EDUCATION_MASKING).fillna(df_masked[formal_informal_column])
    
    # Show formal/informal education value counts after masking
    print(f"\nFormal/Informal education values after masking:")
    formal_informal_counts_after = df_masked[formal_informal_column].value_counts()
    for formal_informal, count in formal_informal_counts_after.head(10).items():
        percentage = (count / len(df_masked)) * 100
        print(f"  {formal_informal}: {count:,} ({percentage:.2f}%)")
    
    # Report masking statistics
    masked_count = (df_masked[formal_informal_column] != df[formal_informal_column]).sum()
    print(f"\nTotal rows masked: {masked_count:,}")
    
    return df_masked

# Function to apply NEET category masking
def apply_neet_category_masking(df, neet_category_column='NEET_Category'):
    """
    Apply NEET category masking to standardize NEET category values according to codelist
    
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame
    neet_category_column : str, default 'NEET_Category'
        Name of the NEET category column to mask
        
    Returns
    -------
    pd.DataFrame
        DataFrame with masked NEET category column
    """
    if neet_category_column not in df.columns:
        print(f"Warning: Column '{neet_category_column}' not found in dataset")
        return df
    
    # Create a copy to avoid modifying original
    df_masked = df.copy()
    
    # Show current NEET category value counts before masking
    print(f"NEET category values before masking:")
    neet_category_counts_before = df_masked[neet_category_column].value_counts()
    for neet_category, count in neet_category_counts_before.head(10).items():
        percentage = (count / len(df_masked)) * 100
        print(f"  {neet_category}: {count:,} ({percentage:.2f}%)")
    
    # Apply masking
    df_masked[neet_category_column] = df_masked[neet_category_column].map(NEET_CATEGORY_MASKING).fillna(df_masked[neet_category_column])
    
    # Show NEET category value counts after masking
    print(f"\nNEET category values after masking:")
    neet_category_counts_after = df_masked[neet_category_column].value_counts()
    for neet_category, count in neet_category_counts_after.head(10).items():
        percentage = (count / len(df_masked)) * 100
        print(f"  {neet_category}: {count:,} ({percentage:.2f}%)")
    
    # Report masking statistics
    masked_count = (df_masked[neet_category_column] != df[neet_category_column]).sum()
    print(f"\nTotal rows masked: {masked_count:,}")
    
    return df_masked

# Function to apply Sex masking
def apply_sex_masking(df, sex_column='Sex'):
    """
    Apply Sex masking to standardize sex values according to codelist
    
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame
    sex_column : str, default 'Sex'
        Name of the sex column to mask
        
    Returns
    -------
    pd.DataFrame
        DataFrame with masked sex column
    """
    if sex_column not in df.columns:
        print(f"Warning: Column '{sex_column}' not found in dataset")
        return df
    
    # Create a copy to avoid modifying original
    df_masked = df.copy()
    
    # Show current sex value counts before masking
    print(f"Sex values before masking:")
    sex_counts_before = df_masked[sex_column].value_counts()
    for sex, count in sex_counts_before.head(10).items():
        percentage = (count / len(df_masked)) * 100
        print(f"  {sex}: {count:,} ({percentage:.2f}%)")
    
    # Apply masking
    df_masked[sex_column] = df_masked[sex_column].map(SEX_MASKING).fillna(df_masked[sex_column])
    
    # Show sex value counts after masking
    print(f"\nSex values after masking:")
    sex_counts_after = df_masked[sex_column].value_counts()
    for sex, count in sex_counts_after.head(10).items():
        percentage = (count / len(df_masked)) * 100
        print(f"  {sex}: {count:,} ({percentage:.2f}%)")
    
    # Report masking statistics
    masked_count = (df_masked[sex_column] != df[sex_column]).sum()
    print(f"\nTotal rows masked: {masked_count:,}")
    
    return df_masked

# Function to apply Age Group masking
def apply_age_group_masking(df, age_group_column='Age_Group'):
    """
    Apply Age Group masking to standardize age group values according to codelist
    
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame
    age_group_column : str, default 'Age_Group'
        Name of the age group column to mask
        
    Returns
    -------
    pd.DataFrame
        DataFrame with masked age group column
    """
    if age_group_column not in df.columns:
        print(f"Warning: Column '{age_group_column}' not found in dataset")
        return df
    
    # Create a copy to avoid modifying original
    df_masked = df.copy()
    
    # Show current age group value counts before masking
    print(f"Age Group values before masking:")
    age_group_counts_before = df_masked[age_group_column].value_counts()
    for age_group, count in age_group_counts_before.head(10).items():
        percentage = (count / len(df_masked)) * 100
        print(f"  {age_group}: {count:,} ({percentage:.2f}%)")
    
    # Apply masking
    df_masked[age_group_column] = df_masked[age_group_column].map(AGE_GROUP_MASKING).fillna(df_masked[age_group_column])
    
    # Show age group value counts after masking
    print(f"\nAge Group values after masking:")
    age_group_counts_after = df_masked[age_group_column].value_counts()
    for age_group, count in age_group_counts_after.head(10).items():
        percentage = (count / len(df_masked)) * 100
        print(f"  {age_group}: {count:,} ({percentage:.2f}%)")
    
    # Report masking statistics
    masked_count = (df_masked[age_group_column] != df[age_group_column]).sum()
    print(f"\nTotal rows masked: {masked_count:,}")
    
    return df_masked

# Function to apply Main Employment Status masking
def apply_main_employment_status_masking(df, main_employment_status_column='Main_Employment_Status'):
    """
    Apply Main Employment Status masking to standardize employment status values according to codelist
    
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame
    main_employment_status_column : str, default 'Main_Employment_Status'
        Name of the main employment status column to mask
        
    Returns
    -------
    pd.DataFrame
        DataFrame with masked main employment status column
    """
    if main_employment_status_column not in df.columns:
        print(f"Warning: Column '{main_employment_status_column}' not found in dataset")
        return df
    
    # Create a copy to avoid modifying original
    df_masked = df.copy()
    
    # Show current main employment status value counts before masking
    print(f"Main Employment Status values before masking:")
    main_employment_status_counts_before = df_masked[main_employment_status_column].value_counts()
    for main_employment_status, count in main_employment_status_counts_before.head(10).items():
        percentage = (count / len(df_masked)) * 100
        print(f"  {main_employment_status}: {count:,} ({percentage:.2f}%)")
    
    # Apply masking
    df_masked[main_employment_status_column] = df_masked[main_employment_status_column].map(MAIN_EMPLOYMENT_STATUS_MASKING).fillna(df_masked[main_employment_status_column])
    
    # Show main employment status value counts after masking
    print(f"\nMain Employment Status values after masking:")
    main_employment_status_counts_after = df_masked[main_employment_status_column].value_counts()
    for main_employment_status, count in main_employment_status_counts_after.head(10).items():
        percentage = (count / len(df_masked)) * 100
        print(f"  {main_employment_status}: {count:,} ({percentage:.2f}%)")
    
    # Report masking statistics
    masked_count = (df_masked[main_employment_status_column] != df[main_employment_status_column]).sum()
    print(f"\nTotal rows masked: {masked_count:,}")
    
    return df_masked

# Function to apply Sub Employment Status masking
def apply_sub_employment_status_masking(df, sub_employment_status_column='Sub_Employment_Status'):
    """
    Apply Sub Employment Status masking to standardize employment status values according to codelist
    
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame
    sub_employment_status_column : str, default 'Sub_Employment_Status'
        Name of the sub employment status column to mask
        
    Returns
    -------
    pd.DataFrame
        DataFrame with masked sub employment status column
    """
    if sub_employment_status_column not in df.columns:
        print(f"Warning: Column '{sub_employment_status_column}' not found in dataset")
        return df
    
    # Create a copy to avoid modifying original
    df_masked = df.copy()
    
    # Show current sub employment status value counts before masking
    print(f"Sub Employment Status values before masking:")
    sub_employment_status_counts_before = df_masked[sub_employment_status_column].value_counts()
    for sub_employment_status, count in sub_employment_status_counts_before.head(10).items():
        percentage = (count / len(df_masked)) * 100
        print(f"  {sub_employment_status}: {count:,} ({percentage:.2f}%)")
    
    # Apply masking
    df_masked[sub_employment_status_column] = df_masked[sub_employment_status_column].map(SUB_EMPLOYMENT_STATUS_MASKING).fillna(df_masked[sub_employment_status_column])
    
    # Show sub employment status value counts after masking
    print(f"\nSub Employment Status values after masking:")
    sub_employment_status_counts_after = df_masked[sub_employment_status_column].value_counts()
    for sub_employment_status, count in sub_employment_status_counts_after.head(10).items():
        percentage = (count / len(df_masked)) * 100
        print(f"  {sub_employment_status}: {count:,} ({percentage:.2f}%)")
    
    # Report masking statistics
    masked_count = (df_masked[sub_employment_status_column] != df[sub_employment_status_column]).sum()
    print(f"\nTotal rows masked: {masked_count:,}")
    
    return df_masked

# Function to apply UNDERMP_PT_WORK_SUB masking
def apply_undermp_pt_work_sub_masking(df, undermp_pt_work_sub_column='Underemployment_PT_Work'):
    """
    Apply UNDERMP_PT_WORK_SUB masking to standardize underemployment part-time work values according to codelist
    
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame
    undermp_pt_work_sub_column : str, default 'Underemployment_PT_Work'
        Name of the underemployment part-time work column to mask
        
    Returns
    -------
    pd.DataFrame
        DataFrame with masked underemployment part-time work column
    """
    if undermp_pt_work_sub_column not in df.columns:
        print(f"Warning: Column '{undermp_pt_work_sub_column}' not found in dataset")
        return df
    
    # Create a copy to avoid modifying original
    df_masked = df.copy()
    
    # Show current underemployment part-time work value counts before masking
    print(f"Underemployment PT Work values before masking:")
    undermp_pt_work_sub_counts_before = df_masked[undermp_pt_work_sub_column].value_counts()
    for undermp_pt_work_sub, count in undermp_pt_work_sub_counts_before.head(10).items():
        percentage = (count / len(df_masked)) * 100
        print(f"  {undermp_pt_work_sub}: {count:,} ({percentage:.2f}%)")
    
    # Apply masking
    df_masked[undermp_pt_work_sub_column] = df_masked[undermp_pt_work_sub_column].map(UNDERMP_PT_WORK_SUB_MASKING).fillna(df_masked[undermp_pt_work_sub_column])
    
    # Show underemployment part-time work value counts after masking
    print(f"\nUnderemployment PT Work values after masking:")
    undermp_pt_work_sub_counts_after = df_masked[undermp_pt_work_sub_column].value_counts()
    for undermp_pt_work_sub, count in undermp_pt_work_sub_counts_after.head(10).items():
        percentage = (count / len(df_masked)) * 100
        print(f"  {undermp_pt_work_sub}: {count:,} ({percentage:.2f}%)")
    
    # Report masking statistics
    masked_count = (df_masked[undermp_pt_work_sub_column] != df[undermp_pt_work_sub_column]).sum()
    print(f"\nTotal rows masked: {masked_count:,}")
    
    return df_masked

# Function to apply WORK_FOR_MORE_HOURS masking
def apply_work_for_more_hours_masking(df, work_for_more_hours_column='WORK_FOR_MORE_HOURS'):
    """
    Apply WORK_FOR_MORE_HOURS masking to standardize work hours availability values according to codelist
    
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame
    work_for_more_hours_column : str, default 'WORK_FOR_MORE_HOURS'
        Name of the work for more hours column to mask
        
    Returns
    -------
    pd.DataFrame
        DataFrame with masked work for more hours column
    """
    if work_for_more_hours_column not in df.columns:
        print(f"Warning: Column '{work_for_more_hours_column}' not found in dataset")
        return df
    
    # Create a copy to avoid modifying original
    df_masked = df.copy()
    
    # Show current work for more hours value counts before masking
    print(f"Work for More Hours values before masking:")
    work_for_more_hours_counts_before = df_masked[work_for_more_hours_column].value_counts()
    for work_for_more_hours, count in work_for_more_hours_counts_before.head(10).items():
        percentage = (count / len(df_masked)) * 100
        print(f"  {work_for_more_hours}: {count:,} ({percentage:.2f}%)")
    
    # Apply masking
    df_masked[work_for_more_hours_column] = df_masked[work_for_more_hours_column].map(WORK_FOR_MORE_HOURS_MASKING).fillna(df_masked[work_for_more_hours_column])
    
    # Show work for more hours value counts after masking
    print(f"\nWork for More Hours values after masking:")
    work_for_more_hours_counts_after = df_masked[work_for_more_hours_column].value_counts()
    for work_for_more_hours, count in work_for_more_hours_counts_after.head(10).items():
        percentage = (count / len(df_masked)) * 100
        print(f"  {work_for_more_hours}: {count:,} ({percentage:.2f}%)")
    
    # Report masking statistics
    masked_count = (df_masked[work_for_more_hours_column] != df[work_for_more_hours_column]).sum()
    print(f"\nTotal rows masked: {masked_count:,}")
    
    return df_masked

# Function to apply LOOKING_FOR_ANOTHER_JOB masking
def apply_looking_for_another_job_masking(df, looking_for_another_job_column='LOOKING_FOR_ANOTHER_JOB'):
    """
    Apply LOOKING_FOR_ANOTHER_JOB masking to standardize job search motivation values according to codelist
    
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame
    looking_for_another_job_column : str, default 'LOOKING_FOR_ANOTHER_JOB'
        Name of the looking for another job column to mask
        
    Returns
    -------
    pd.DataFrame
        DataFrame with masked looking for another job column
    """
    if looking_for_another_job_column not in df.columns:
        print(f"Warning: Column '{looking_for_another_job_column}' not found in dataset")
        return df
    
    # Create a copy to avoid modifying original
    df_masked = df.copy()
    
    # Show current looking for another job value counts before masking
    print(f"Looking for Another Job values before masking:")
    looking_for_another_job_counts_before = df_masked[looking_for_another_job_column].value_counts()
    for looking_for_another_job, count in looking_for_another_job_counts_before.head(10).items():
        percentage = (count / len(df_masked)) * 100
        print(f"  {looking_for_another_job}: {count:,} ({percentage:.2f}%)")
    
    # Apply masking
    df_masked[looking_for_another_job_column] = df_masked[looking_for_another_job_column].map(LOOKING_FOR_ANOTHER_JOB_MASKING).fillna(df_masked[looking_for_another_job_column])
    
    # Show looking for another job value counts after masking
    print(f"\nLooking for Another Job values after masking:")
    looking_for_another_job_counts_after = df_masked[looking_for_another_job_column].value_counts()
    for looking_for_another_job, count in looking_for_another_job_counts_after.head(10).items():
        percentage = (count / len(df_masked)) * 100
        print(f"  {looking_for_another_job}: {count:,} ({percentage:.2f}%)")
    
    # Report masking statistics
    masked_count = (df_masked[looking_for_another_job_column] != df[looking_for_another_job_column]).sum()
    print(f"\nTotal rows masked: {masked_count:,}")
    
    return df_masked

# Function to apply Unit of Measure masking
def apply_unit_of_measure_masking(df, unit_of_measure_column='Unit_of_Measure'):
    """
    Apply Unit of Measure masking to standardize unit of measure values according to codelist
    
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame
    unit_of_measure_column : str, default 'Unit_of_Measure'
        Name of the unit of measure column to mask
        
    Returns
    -------
    pd.DataFrame
        DataFrame with masked unit of measure column
    """
    if unit_of_measure_column not in df.columns:
        print(f"Warning: Column '{unit_of_measure_column}' not found in dataset")
        return df
    
    # Create a copy to avoid modifying original
    df_masked = df.copy()
    
    # Show current unit of measure value counts before masking
    print(f"Unit of Measure values before masking:")
    unit_of_measure_counts_before = df_masked[unit_of_measure_column].value_counts()
    for unit_of_measure, count in unit_of_measure_counts_before.head(10).items():
        percentage = (count / len(df_masked)) * 100
        print(f"  {unit_of_measure}: {count:,} ({percentage:.2f}%)")
    
    # Apply masking
    df_masked[unit_of_measure_column] = df_masked[unit_of_measure_column].map(UNIT_OF_MEASURE_MASKING).fillna(df_masked[unit_of_measure_column])
    
    # Show unit of measure value counts after masking
    print(f"\nUnit of Measure values after masking:")
    unit_of_measure_counts_after = df_masked[unit_of_measure_column].value_counts()
    for unit_of_measure, count in unit_of_measure_counts_after.head(10).items():
        percentage = (count / len(df_masked)) * 100
        print(f"  {unit_of_measure}: {count:,} ({percentage:.2f}%)")
    
    # Report masking statistics
    masked_count = (df_masked[unit_of_measure_column] != df[unit_of_measure_column]).sum()
    print(f"\nTotal rows masked: {masked_count:,}")
    
    return df_masked

# Function to apply NR_PERSONS_LOCAL_UNIT masking
def apply_nr_persons_local_unit_masking(df, nr_persons_local_unit_column='NR_PERSONS_LOCAL_UNIT'):
    """
    Apply NR_PERSONS_LOCAL_UNIT masking to standardize local unit size values according to codelist
    
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame
    nr_persons_local_unit_column : str, default 'NR_PERSONS_LOCAL_UNIT'
        Name of the local unit size column to mask
        
    Returns
    -------
    pd.DataFrame
        DataFrame with masked local unit size column
    """
    if nr_persons_local_unit_column not in df.columns:
        print(f"Warning: Column '{nr_persons_local_unit_column}' not found in dataset")
        return df
    
    # Create a copy to avoid modifying original
    df_masked = df.copy()
    
    # Show current local unit size value counts before masking
    print(f"Local Unit Size values before masking:")
    nr_persons_local_unit_counts_before = df_masked[nr_persons_local_unit_column].value_counts()
    for nr_persons_local_unit, count in nr_persons_local_unit_counts_before.head(10).items():
        percentage = (count / len(df_masked)) * 100
        print(f"  {nr_persons_local_unit}: {count:,} ({percentage:.2f}%)")
    
    # Apply masking
    df_masked[nr_persons_local_unit_column] = df_masked[nr_persons_local_unit_column].map(NR_PERSONS_LOCAL_UNIT_MASKING).fillna(df_masked[nr_persons_local_unit_column])
    
    # Show local unit size value counts after masking
    print(f"\nLocal Unit Size values after masking:")
    nr_persons_local_unit_counts_after = df_masked[nr_persons_local_unit_column].value_counts()
    for nr_persons_local_unit, count in nr_persons_local_unit_counts_after.head(10).items():
        percentage = (count / len(df_masked)) * 100
        print(f"  {nr_persons_local_unit}: {count:,} ({percentage:.2f}%)")
    
    # Report masking statistics
    masked_count = (df_masked[nr_persons_local_unit_column] != df[nr_persons_local_unit_column]).sum()
    print(f"\nTotal rows masked: {masked_count:,}")
    
    return df_masked

# Function to apply BO masking
def apply_bo_masking(df, bo_column='BO'):
    """
    Apply BO masking to standardize business ownership values according to codelist
    
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame
    bo_column : str, default 'BO'
        Name of the business ownership column to mask
        
    Returns
    -------
    pd.DataFrame
        DataFrame with masked business ownership column
    """
    if bo_column not in df.columns:
        print(f"Warning: Column '{bo_column}' not found in dataset")
        return df
    
    # Create a copy to avoid modifying original
    df_masked = df.copy()
    
    # Show current business ownership value counts before masking
    print(f"Business Ownership values before masking:")
    bo_counts_before = df_masked[bo_column].value_counts()
    for bo, count in bo_counts_before.head(10).items():
        percentage = (count / len(df_masked)) * 100
        print(f"  {bo}: {count:,} ({percentage:.2f}%)")
    
    # Apply masking
    df_masked[bo_column] = df_masked[bo_column].map(BO_MASKING).fillna(df_masked[bo_column])
    
    # Show business ownership value counts after masking
    print(f"\nBusiness Ownership values after masking:")
    bo_counts_after = df_masked[bo_column].value_counts()
    for bo, count in bo_counts_after.head(10).items():
        percentage = (count / len(df_masked)) * 100
        print(f"  {bo}: {count:,} ({percentage:.2f}%)")
    
    # Report masking statistics
    masked_count = (df_masked[bo_column] != df[bo_column]).sum()
    print(f"\nTotal rows masked: {masked_count:,}")
    
    return df_masked

# Function to apply SECTOR masking
def apply_sector_masking(df, sector_column='Sector'):
    """
    Apply SECTOR masking to standardize sector values according to codelist
    
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame
    sector_column : str, default 'Sector'
        Name of the sector column to mask
        
    Returns
    -------
    pd.DataFrame
        DataFrame with masked sector column
    """
    if sector_column not in df.columns:
        print(f"Warning: Column '{sector_column}' not found in dataset")
        return df
    
    # Create a copy to avoid modifying original
    df_masked = df.copy()
    
    # Show current sector value counts before masking
    print(f"Sector values before masking:")
    sector_counts_before = df_masked[sector_column].value_counts()
    for sector, count in sector_counts_before.head(10).items():
        percentage = (count / len(df_masked)) * 100
        print(f"  {sector}: {count:,} ({percentage:.2f}%)")
    
    # Apply masking
    df_masked[sector_column] = df_masked[sector_column].map(SECTOR_MASKING).fillna(df_masked[sector_column])
    
    # Show sector value counts after masking
    print(f"\nSector values after masking:")
    sector_counts_after = df_masked[sector_column].value_counts()
    for sector, count in sector_counts_after.head(10).items():
        percentage = (count / len(df_masked)) * 100
        print(f"  {sector}: {count:,} ({percentage:.2f}%)")
    
    # Report masking statistics
    masked_count = (df_masked[sector_column] != df[sector_column]).sum()
    print(f"\nTotal rows masked: {masked_count:,}")
    
    return df_masked

# Function to apply SECTOR_SUB masking
def apply_sector_sub_masking(df, sector_sub_column='SECTOR_SUB'):
    """
    Apply SECTOR_SUB masking to standardize sub-sector values according to codelist
    
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame
    sector_sub_column : str, default 'SECTOR_SUB'
        Name of the sub-sector column to mask
        
    Returns
    -------
    pd.DataFrame
        DataFrame with masked sub-sector column
    """
    if sector_sub_column not in df.columns:
        print(f"Warning: Column '{sector_sub_column}' not found in dataset")
        return df
    
    # Create a copy to avoid modifying original
    df_masked = df.copy()
    
    # Show current sub-sector value counts before masking
    print(f"Sub-Sector values before masking:")
    sector_sub_counts_before = df_masked[sector_sub_column].value_counts()
    for sector_sub, count in sector_sub_counts_before.head(10).items():
        percentage = (count / len(df_masked)) * 100
        print(f"  {sector_sub}: {count:,} ({percentage:.2f}%)")
    
    # Apply masking
    df_masked[sector_sub_column] = df_masked[sector_sub_column].map(SECTOR_SUB_MASKING).fillna(df_masked[sector_sub_column])
    
    # Show sub-sector value counts after masking
    print(f"\nSub-Sector values after masking:")
    sector_sub_counts_after = df_masked[sector_sub_column].value_counts()
    for sector_sub, count in sector_sub_counts_after.head(10).items():
        percentage = (count / len(df_masked)) * 100
        print(f"  {sector_sub}: {count:,} ({percentage:.2f}%)")
    
    # Report masking statistics
    masked_count = (df_masked[sector_sub_column] != df[sector_sub_column]).sum()
    print(f"\nTotal rows masked: {masked_count:,}")
    
    return df_masked

# Function to apply TYPE_OCCUPATION masking
def apply_type_occupation_masking(df, type_occupation_column='TYPE_OCCUPATION'):
    """
    Apply TYPE_OCCUPATION masking to standardize type of occupation values according to codelist
    
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame
    type_occupation_column : str, default 'TYPE_OCCUPATION'
        Name of the type of occupation column to mask
        
    Returns
    -------
    pd.DataFrame
        DataFrame with masked type of occupation column
    """
    if type_occupation_column not in df.columns:
        print(f"Warning: Column '{type_occupation_column}' not found in dataset")
        return df
    
    # Create a copy to avoid modifying original
    df_masked = df.copy()
    
    # Show current type of occupation value counts before masking
    print(f"Type of Occupation values before masking:")
    type_occupation_counts_before = df_masked[type_occupation_column].value_counts()
    for type_occupation, count in type_occupation_counts_before.head(10).items():
        percentage = (count / len(df_masked)) * 100
        print(f"  {type_occupation}: {count:,} ({percentage:.2f}%)")
    
    # Apply masking
    df_masked[type_occupation_column] = df_masked[type_occupation_column].map(TYPE_OCCUPATION_MASKING).fillna(df_masked[type_occupation_column])
    
    # Show type of occupation value counts after masking
    print(f"\nType of Occupation values after masking:")
    type_occupation_counts_after = df_masked[type_occupation_column].value_counts()
    for type_occupation, count in type_occupation_counts_after.head(10).items():
        percentage = (count / len(df_masked)) * 100
        print(f"  {type_occupation}: {count:,} ({percentage:.2f}%)")
    
    # Report masking statistics
    masked_count = (df_masked[type_occupation_column] != df[type_occupation_column]).sum()
    print(f"\nTotal rows masked: {masked_count:,}")
    
    return df_masked

# Marital Status masking configuration
MARITAL_STATUS_MASKING = {
    # Special processing codes
    '_Z': '_Z',  # Special processing code -> Not applicable
    
    # Marital status categories
    'Single': 'SINGLE',  # Single persons
    'Married': 'MARRIED',  # Married persons
    'Widowed, divorced      or legally separated': 'WIDOWED_DIVORCED_LEGALLY_SEPARATED',  # Widowed, divorced or legally separated
    'Widowed, divorced          or legally separated': 'WIDOWED_DIVORCED_LEGALLY_SEPARATED'  # Alternative formatting
}

# Labour Force Subcategory masking configuration
LABOUR_FORCE_SUBCATEGORY_MASKING = {
    # Special processing codes
    '_Z': '_Z',  # Special processing code -> Not applicable
    
    # Unit of measure
    'persons': 'PERSONS',  # Count of individuals
    
    # Demographic percentages
    '% aged 20-64': 'PERCENT_AGED_20_64',  # Percentage aged 20-64
    '% aged 15+ (1981-97: 14+)': 'PERCENT_AGED_15_PLUS_1981_97_14_PLUS',  # Percentage aged 15+
    
    # Labour force rates
    'activity rate': 'ACTIVITY_RATE',  # Activity rate
    'employment rate': 'EMPLOYMENT_RATE',  # Employment rate
    'unemployment rate': 'UNEMPLOYMENT_RATE',  # Unemployment rate
    
    # Employment status subcategories
    'Employed, not undermployed': 'EMPLOYED_NOT_UNDEREMPLOYED',  # Employed, not undermployed
    'Undermployed part-time workers': 'UNDEREMPLOYED_PART_TIME_WORKERS',  # Undermployed part-time workers
    
    # Unemployment subcategories
    'Seeking work but not immediately available': 'SEEKING_WORK_BUT_NOT_IMMEDIATELY_AVAILABLE',  # Seeking work but not immediately available
    'Available to work but not seeking': 'AVAILABLE_TO_WORK_BUT_NOT_SEEKING',  # Available to work but not seeking
    
    # Inactivity reasons
    'Education or training': 'EDUCATION_OR_TRAINING',  # Education or training
    'Own ilness or disability': 'OWN_ILLNESS_OR_DISABILITY',  # Own illness or disability
    'Personal or family responsibilities': 'PERSONAL_OR_FAMILY_RESPONSIBILITIES',  # Personal or family responsibilities
    'Retirement': 'RETIREMENT',  # Retirement
    'Other inactive': 'OTHER_INACTIVE',  # Other inactive
    'Other reasons': 'OTHER_REASONS',  # Other reasons
    
    # Age group breakdowns
    'Persons aged 0-17': 'PERSONS_AGED_0_17',  # Persons aged 0-17
    'Persons aged 18-59': 'PERSONS_AGED_18_59'  # Persons aged 18-59
}

# Function to apply Marital Status masking
def apply_marital_status_masking(df, marital_status_column='Marital_Status'):
    """
    Apply Marital Status masking to standardize marital status values according to codelist
    
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame
    marital_status_column : str, default 'Marital_Status'
        Name of the marital status column to mask
        
    Returns
    -------
    pd.DataFrame
        DataFrame with masked marital status column
    """
    if marital_status_column not in df.columns:
        print(f"Warning: Column '{marital_status_column}' not found in dataset")
        return df
    
    # Create a copy to avoid modifying original
    df_masked = df.copy()
    
    # Show current marital status value counts before masking
    print(f"Marital Status values before masking:")
    marital_status_counts_before = df_masked[marital_status_column].value_counts()
    for marital_status, count in marital_status_counts_before.head(10).items():
        percentage = (count / len(df_masked)) * 100
        print(f"  {marital_status}: {count:,} ({percentage:.2f}%)")
    
    # Apply masking
    df_masked[marital_status_column] = df_masked[marital_status_column].map(MARITAL_STATUS_MASKING).fillna(df_masked[marital_status_column])
    
    # Show marital status value counts after masking
    print(f"\nMarital Status values after masking:")
    marital_status_counts_after = df_masked[marital_status_column].value_counts()
    for marital_status, count in marital_status_counts_after.head(10).items():
        percentage = (count / len(df_masked)) * 100
        print(f"  {marital_status}: {count:,} ({percentage:.2f}%)")
    
    # Report masking statistics
    masked_count = (df_masked[marital_status_column] != df[marital_status_column]).sum()
    print(f"\nTotal rows masked: {masked_count:,}")
    
    return df_masked

# Function to apply Labour Force Subcategory masking
def apply_labour_force_subcategory_masking(df, labour_force_subcategory_column='Labour_Force_Subcategory'):
    """
    Apply Labour Force Subcategory masking to standardize labour force subcategory values according to codelist
    
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame
    labour_force_subcategory_column : str, default 'Labour_Force_Subcategory'
        Name of the labour force subcategory column to mask
        
    Returns
    -------
    pd.DataFrame
        DataFrame with masked labour force subcategory column
    """
    if labour_force_subcategory_column not in df.columns:
        print(f"Warning: Column '{labour_force_subcategory_column}' not found in dataset")
        return df
    
    # Create a copy to avoid modifying original
    df_masked = df.copy()
    
    # Show current labour force subcategory value counts before masking
    print(f"Labour Force Subcategory values before masking:")
    labour_force_subcategory_counts_before = df_masked[labour_force_subcategory_column].value_counts()
    for labour_force_subcategory, count in labour_force_subcategory_counts_before.head(10).items():
        percentage = (count / len(df_masked)) * 100
        print(f"  {labour_force_subcategory}: {count:,} ({percentage:.2f}%)")
    
    # Apply masking
    df_masked[labour_force_subcategory_column] = df_masked[labour_force_subcategory_column].map(LABOUR_FORCE_SUBCATEGORY_MASKING).fillna(df_masked[labour_force_subcategory_column])
    
    # Show labour force subcategory value counts after masking
    print(f"\nLabour Force Subcategory values after masking:")
    labour_force_subcategory_counts_after = df_masked[labour_force_subcategory_column].value_counts()
    for labour_force_subcategory, count in labour_force_subcategory_counts_after.head(10).items():
        percentage = (count / len(df_masked)) * 100
        print(f"  {labour_force_subcategory}: {count:,} ({percentage:.2f}%)")
    
    # Report masking statistics
    masked_count = (df_masked[labour_force_subcategory_column] != df[labour_force_subcategory_column]).sum()
    print(f"\nTotal rows masked: {masked_count:,}")
    
    return df_masked

# Function to get masking statistics
def get_masking_stats(df, region_column='Region'):
    """
    Get statistics about region masking without applying it
    
    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame
    region_column : str, default 'Region'
        Name of the region column
        
    Returns
    -------
    dict
        Dictionary with masking statistics
    """
    if region_column not in df.columns:
        return {"error": f"Column '{region_column}' not found"}
    
    stats = {}
    
    # Current value counts
    current_counts = df[region_column].value_counts()
    stats['current_values'] = current_counts.to_dict()
    
    # Values that will be masked
    maskable_values = [val for val in current_counts.index if val in REGION_MASKING]
    stats['maskable_values'] = maskable_values
    
    # Count of rows that will be masked
    maskable_count = current_counts[maskable_values].sum() if maskable_values else 0
    stats['maskable_count'] = maskable_count
    
    # Percentage of data that will be masked
    stats['maskable_percentage'] = (maskable_count / len(df)) * 100 if len(df) > 0 else 0
    
    return stats
