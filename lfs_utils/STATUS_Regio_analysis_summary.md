# STATUS-Regio Sheet Analysis Summary

## Sheet Information
- **File**: `A0101_SJO03_TS_AN_00_1981_00_2024_01_F_EN.xlsx` (File 01)
- **Sheet**: `STATUS-Regio`
- **Structure**: 591 rows × 27 columns
- **Data starts**: Row 3

## Data Structure Analysis

### Header Layout
- **Row 0**: Main categories (Employment status, Total population aged 15+, Labour Force, Employed, Unemployed, Inactive, Reasons for not seeking employment (inactive), Population living in jobless households)
- **Row 1**: Sub-categories (Year, Regions - NUTS II, persons, activity rate, % aged 20-64, persons, employment rate, % aged 20-64, Employed not undermployed, Undermployed part-time workers, persons, unemployment rate, % aged 20-64, persons, % aged 15+, % aged 20-64, Seeking work but not immediately available, Available to work but not seeking, Other inactive, Personal or family responsibilities, Education or training, Own illness or disability, Retirement, Other reasons, Persons aged 0-17, Persons aged 18-59)
- **Row 2**: Empty
- **Row 3+**: Actual data

### Column Mapping
```
Col 0: Year (Employment status category)
Col 1: Regions - NUTS II (data, not header)
Col 2: Total population aged 15+ (Total population category)
Col 3-5: Labour Force breakdown (persons, activity rate, % aged 20-64)
Col 6-11: Employed breakdown (persons, employment rate, % aged 20-64, Employed not undermployed, Undermployed part-time workers, persons)
Col 12-14: Unemployed breakdown (unemployment rate, % aged 20-64, persons)
Col 15-17: Inactive breakdown (persons, % aged 15+, % aged 20-64)
Col 18-24: Reasons for not seeking employment (inactive) breakdown (all in persons)
Col 25-26: Population living in jobless households breakdown (Persons aged 0-17, Persons aged 18-59)
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
7. **Population living in jobless households**

#### Sub-Categories by Status:
- **Labour Force**: persons, activity rate, % aged 20-64
- **Employed**: persons, employment rate, % aged 20-64, Employed not undermployed, Undermployed part-time workers, persons
- **Unemployed**: unemployment rate, % aged 20-64, persons
- **Inactive**: persons, % aged 15+, % aged 20-64
- **Inactive Reasons**: Seeking work but not immediately available, Available to work but not seeking, Other inactive, Personal or family responsibilities, Education or training, Own illness or disability, Retirement, Other reasons
- **Jobless Households**: Persons aged 0-17, Persons aged 18-59

### Regional Coverage
The data covers 20 different regions including:
- **NUTS II Regions**: Anatoliki Makedonia-Thraki, Kentriki Makedonia, Dytiki Makedonia, Ipeiros, Thessalia, Ionia Nissia, Dytiki Ellada, Sterea Ellada, Attiki, Peloponnisos, Voreio Aigaio, Notio Aigaio, Kriti
- **Historical Groupings**: Anatoliki Sterea & Nissia, Kentriki & Dytiki Makedonia, Peloponnisos & Dytiki Sterea, Anatoliki Makedonia, Thraki, Nissia Anatolikou Aigaiou
- **Country Total**: COUNTRY TOTAL

### Units of Measure
The data includes multiple units of measure:
- **persons**: 6,846 records (actual population counts)
- **percentage**: 4,382 records (rates and percentages)

## Data Parsing Results

### Final SDMX Structure
- **Year**: Identifier dimension
- **Region**: Regional breakdown (20 regions including NUTS II and historical groupings)
- **Labour_Force_Status**: Main labour force status category
- **Labour_Force_Subcategory**: Sub-category within main status
- **Unit_of_Measure**: Unit of measurement (persons, percentage)
- **Value**: Actual numeric data

### Data Coverage
- **Total records**: 11,228
- **Years**: 44 (1981-2024)
- **Regions**: 20 (NUTS II regions, historical groupings, country total)
- **Labour Force Statuses**: 7 (Total Population, Labour Force, Employed, Unemployed, Inactive, Reasons for not seeking employment (inactive), Population living in jobless households)
- **Labour Force Subcategories**: 19 (persons, activity rate, employment rate, Employed not undermployed, Undermployed part-time workers, unemployment rate, % aged 20-64, inactive reasons breakdown, jobless household breakdown)
- **Units of Measure**: 2 (persons, percentage)

### Key Features
1. **Multiple Units of Measure**: Proper handling of persons vs. percentage values
2. **Comprehensive Employment Metrics**: All labour force status breakdowns covered by region
3. **Detailed Inactive Analysis**: Complete breakdown of reasons for not seeking employment by region
4. **Underemployment Analysis**: Detailed breakdown of employed vs. undermployed workers by region
5. **Age-Specific Metrics**: Rates and percentages specific to 20-64 age group by region
6. **Jobless Household Analysis**: Population living in jobless households by age group and region
7. **SDMX Compliance**: Wide format with "_Z" placeholders for missing combinations
8. **Data Integrity**: All numeric values properly extracted and validated
9. **Complex Header Handling**: Successfully parsed multi-row header structure
10. **Regional Variations**: Handles different regional coverage across time periods

## Files Generated
- **Template**: `assets/prepared/lfs_status_regio_template.xlsx` (127,600 records)
- **Parsed Data**: `assets/prepared/lfs_status_regio_parsed.xlsx` (11,228 records)

## Next Steps
1. ✅ POPUL-Regio sheet completed
2. ✅ POPUL-Status sheet completed
3. ✅ EDUC-SexAge sheet completed
4. ✅ EDUC-Regio sheet completed
5. ✅ EDUC-Status sheet completed
6. ✅ STATUS-SexAge sheet completed
7. ✅ STATUS-Regio sheet completed
8. 🔄 Ready for next sheet processing
9. 🔄 Extend to other LFS annual files (02, 03)
10. 🔄 Implement comprehensive dimension mapping across all datasets
