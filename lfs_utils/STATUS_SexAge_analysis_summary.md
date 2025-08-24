# STATUS-SexAge Sheet Analysis Summary

## Sheet Information
- **File**: `A0101_SJO03_TS_AN_00_1981_00_2024_01_F_EN.xlsx` (File 01)
- **Sheet**: `STATUS-SexAge`
- **Structure**: 697 rows × 26 columns
- **Data starts**: Row 3

## Data Structure Analysis

### Header Layout
- **Row 0**: Main categories (Employment status, Total population aged 15+, Labour Force, Employed, Unemployed, Inactive, Reasons for not seeking employment (inactive))
- **Row 1**: Sub-categories (Year, Sex, Age, persons, activity rate, % aged 20-64, persons, employment rate, % aged 20-64, Employed not undermployed, Undermployed part-time workers, persons, unemployment rate, % aged 20-64, persons, % aged 15+, % aged 20-64, Seeking work but not immediately available, Available to work but not seeking, Other inactive, Personal or family responsibilities, Education or training, Own illness or disability, Retirement, Other reasons)
- **Row 2**: Empty
- **Row 3+**: Actual data

### Column Mapping
```
Col 0: Year (Employment status category)
Col 1: Sex (data, not header)
Col 2: Age group (data, not header)
Col 3: Total population aged 15+ (Total population category)
Col 4-6: Labour Force breakdown (persons, activity rate, % aged 20-64)
Col 7-12: Employed breakdown (persons, employment rate, % aged 20-64, Employed not undermployed, Undermployed part-time workers, persons)
Col 13-15: Unemployed breakdown (unemployment rate, % aged 20-64, persons)
Col 16-18: Inactive breakdown (persons, % aged 15+, % aged 20-64)
Col 19-25: Reasons for not seeking employment (inactive) breakdown (all in persons)
```

### Labour Force Status Structure
The employment status data is organized in a hierarchical structure:

#### Main Labour Force Statuses:
1. **Total Population**
2. **Labour Force**
3. **Employed**
4. **Unemployed**
5. **Inactive**
6. **Reasons for not seeking employment (inactive)**

#### Sub-Categories by Status:
- **Labour Force**: persons, activity rate, % aged 20-64
- **Employed**: persons, employment rate, % aged 20-64, Employed not undermployed, Undermployed part-time workers, persons
- **Unemployed**: unemployment rate, % aged 20-64, persons
- **Inactive**: persons, % aged 15+, % aged 20-64
- **Inactive Reasons**: Seeking work but not immediately available, Available to work but not seeking, Other inactive, Personal or family responsibilities, Education or training, Own illness or disability, Retirement, Other reasons

### Units of Measure
The data includes multiple units of measure:
- **persons**: 6,729 records (actual population counts)
- **percentage**: 2,895 records (rates and percentages)

## Data Parsing Results

### Final SDMX Structure
- **Year**: Identifier dimension
- **Sex**: Sex breakdown (Males, Females, YEAR TOTAL)
- **Age_Group**: Age group breakdown (15-19, 20-24, 25-29, 30-44, 45-64, 65+, Total Males, Total Females, Total, 14)
- **Labour_Force_Status**: Main labour force status category
- **Labour_Force_Subcategory**: Sub-category within main status
- **Unit_of_Measure**: Unit of measurement (persons, percentage)
- **Value**: Actual numeric data

### Data Coverage
- **Total records**: 9,624
- **Years**: 44 (1981-2024)
- **Sex**: 3 (Males, Females, YEAR TOTAL)
- **Age Groups**: 10 (15-19, 20-24, 25-29, 30-44, 45-64, 65+, Total Males, Total Females, Total, 14)
- **Labour Force Statuses**: 6 (Total Population, Labour Force, Employed, Unemployed, Inactive, Reasons for not seeking employment (inactive))
- **Labour Force Subcategories**: 16 (persons, activity rate, employment rate, Employed not undermployed, Undermployed part-time workers, unemployment rate, % aged 20-64, inactive reasons breakdown)
- **Units of Measure**: 2 (persons, percentage)

### Key Features
1. **Multiple Units of Measure**: Proper handling of persons vs. percentage values
2. **Comprehensive Employment Metrics**: All labour force status breakdowns covered
3. **Detailed Inactive Analysis**: Complete breakdown of reasons for not seeking employment
4. **Underemployment Analysis**: Detailed breakdown of employed vs. undermployed workers
5. **Age-Specific Metrics**: Rates and percentages specific to 20-64 age group
6. **SDMX Compliance**: Wide format with "_Z" placeholders for missing combinations
7. **Data Integrity**: All numeric values properly extracted and validated
8. **Complex Header Handling**: Successfully parsed multi-row header structure

## Files Generated
- **Template**: `assets/prepared/lfs_status_sexage_template.xlsx` (146,520 records)
- **Parsed Data**: `assets/prepared/lfs_status_sexage_parsed.xlsx` (9,624 records)

## Next Steps
1. ✅ POPUL-Regio sheet completed
2. ✅ POPUL-Status sheet completed
3. ✅ EDUC-SexAge sheet completed
4. ✅ EDUC-Regio sheet completed
5. ✅ EDUC-Status sheet completed
6. ✅ STATUS-SexAge sheet completed
7. 🔄 Ready for next sheet processing
8. 🔄 Extend to other LFS annual files (02, 03)
9. 🔄 Implement comprehensive dimension mapping across all datasets
