# EDUC-SexAge Sheet Analysis Summary

## Sheet Information
- **File**: `A0101_SJO03_TS_AN_00_1981_00_2024_01_F_EN.xlsx` (File 01)
- **Sheet**: `EDUC-SexAge`
- **Structure**: 614 rows × 27 columns
- **Data starts**: Row 4

## Data Structure Analysis

### Header Layout
- **Row 0**: Main categories (Education, Total population aged 15+, Education level, Attended formal/informal education, NEETs, Tertiary attainment, Lifelong learning)
- **Row 1**: Sub-categories (Attended no school/Did not complete primary education, Primary, Lower secondary, Upper secondary & post secondary, Tertiary, Postgraduate degrees)
- **Row 2**: Sub-sub-categories (Year, Sex, Age, ekp1, ekp2, ekp3, ekp4, Upper secondary, Post secondary vocational, ekp7, University degree, Postgraduate degrees, Total, in formal education, in informal education, of them Employed, of them Unemployed, of them Inactive, Total, Unemployed, Seek job but not available, Like to work but not seek job, Other)
- **Row 3**: Empty
- **Row 4+**: Actual data

### Column Mapping
```
Col 0: Year (Education category)
Col 1: Sex (data, not header)
Col 2: Age (data, not header)
Col 3: Total population aged 15+ (Total population category)
Col 4-13: Education level breakdown (ekp1, ekp2, ekp3, ekp4, Upper secondary, Post secondary vocational, ekp7, University degree, Postgraduate degrees)
Col 14-19: Formal/informal education in last 4 weeks (Total, in formal education, in informal education, of them Employed, of them Unemployed, of them Inactive)
Col 20-24: NEET breakdown (Total, Unemployed, Seek job but not available, Like to work but not seek job, Other)
Col 25: Tertiary educational attainment aged 30-34
Col 26: Lifelong learning aged 20-64
```

### Education Level Structure
The education level data is organized in a hierarchical structure:

#### Main Categories (Row 1):
1. **Attended no school / Did not complete primary education**
2. **Primary**
3. **Lower secondary**
4. **Upper secondary & post secondary**
5. **Tertiary**
6. **Postgraduate degrees (including integrated Master's degrees)**

#### Sub-Categories (Row 2):
- **ekp1, ekp2, ekp3, ekp4**: Specific education level codes
- **Upper secondary**: Upper secondary education
- **Post secondary vocational**: Post-secondary vocational training
- **ekp7**: Additional education level code
- **University degree**: University-level education
- **Postgraduate degrees (Master/PhD)**: Advanced degrees

## Data Parsing Results

### Final SDMX Structure
- **Year**: Identifier dimension
- **Sex**: Gender breakdown (Males, Females, YEAR TOTAL)
- **Age_Group**: Age group breakdown (14, 15-19, 20-24, 25-29, 30-44, 45-64, 65+, Total Males, Total Females, Total)
- **Education_Level_Main**: Main education category
- **Education_Level_Sub**: Sub-category within main category
- **Formal_Informal_Education**: Education participation breakdown
- **NEET_Category**: NEET status breakdown
- **Tertiary_30_34**: Tertiary attainment for 30-34 age group
- **Lifelong_20_64**: Lifelong learning for 20-64 age group
- **Value**: Actual numeric data

### Data Coverage
- **Total records**: 10,567
- **Years**: 44 (1981-2024)
- **Sex categories**: 3 (Males, Females, YEAR TOTAL)
- **Age groups**: 10 (14, 15-19, 20-24, 25-29, 30-44, 45-64, 65+, Total Males, Total Females, Total)
- **Education main levels**: 6
- **Education sub levels**: 10
- **Formal/informal education**: 7 categories
- **NEET categories**: 6 categories
- **Tertiary attainment**: 1 category
- **Lifelong learning**: 1 category

### Key Features
1. **Double Column Education Structure**: Main and sub-categories properly separated
2. **Comprehensive Education Metrics**: All education levels and participation types covered
3. **NEET Analysis**: Detailed breakdown of youth not in employment, education, or training
4. **Lifelong Learning**: Adult education and continuous learning metrics
5. **SDMX Compliance**: Wide format with "_Z" placeholders for missing combinations
6. **Data Integrity**: All numeric values properly extracted and validated

## Files Generated
- **Template**: `assets/prepared/lfs_educ_sexage_template.xlsx` (89,760 records)
- **Parsed Data**: `assets/prepared/lfs_educ_sexage_parsed.xlsx` (10,567 records)

## Next Steps
1. ✅ POPUL-Regio sheet completed
2. ✅ POPUL-Status sheet completed
3. ✅ EDUC-SexAge sheet completed
4. 🔄 Ready for next sheet processing
5. 🔄 Extend to other LFS annual files (02, 03)
6. 🔄 Implement comprehensive dimension mapping across all datasets
