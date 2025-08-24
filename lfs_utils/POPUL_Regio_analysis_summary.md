# POPUL-Regio Sheet Analysis Summary

## Sheet Information
- **File**: `A0101_SJO03_TS_AN_00_1981_00_2024_01_F_EN.xlsx` (File 01)
- **Sheet**: `POPUL-Regio`
- **Structure**: 591 rows × 32 columns
- **Data starts**: Row 3

## Data Structure Analysis

### Header Layout
- **Row 0**: Main categories (Population, Population total, Total, Males, Females, Nationality, Marital status)
- **Row 1**: Sub-categories (Year, Region, Age groups, etc.)
- **Row 2**: Empty/continuation
- **Row 3+**: Actual data values

### Column Mapping
```
Col 0: Year (Population category)
Col 1: Region - NUTS II (no main category)
Col 2: Population total (no sub-category)
Col 3-9: Total population by age groups
Col 10: Males total
Col 11-17: Males by age groups
Col 18: Females total
Col 19-25: Females by age groups
Col 26-28: Nationality breakdown
Col 29-31: Marital status breakdown
```

## Parsed Data Structure

### Dimensions
1. **Year**: 44 unique values (1981-2024)
2. **Region**: 20 unique values (Greek regions + COUNTRY TOTAL)
3. **Sex**: 3 values (Total, Males, Females)
4. **Age_Group**: 7 values (0-14, 15-19, 20-24, 25-29, 30-44, 45-64, 65+)
5. **Nationality**: 4 values (Greek, EU country, Other, _Z)
6. **Marital_Status**: 4 values (Single, Married, Widowed/divorced, _Z)
7. **Value**: Actual numeric data or "_Z" for missing combinations

### Data Breakdown
- **Total records**: 15,876
- **Total sex records**: 7,644 (44 years × 20 regions × 7 age groups + 44 years × 20 regions × 3 nationality + 44 years × 20 regions × 3 marital)
- **Males sex records**: 4,116 (44 years × 20 regions × 7 age groups)
- **Females sex records**: 4,116 (44 years × 20 regions × 7 age groups)

### Data Coverage
- **Age groups**: Available for Total, Males, and Females
- **Nationality**: Only available for Total population
- **Marital status**: Only available for Total population
- **Missing values**: Represented as "_Z"

## SDMX Compliance

The parsed data follows SDMX principles:
- **Wide format**: Each dimension has its own column
- **Consistent structure**: All possible dimension combinations are represented
- **Missing value handling**: "_Z" placeholder for non-applicable combinations
- **Value column**: Contains actual numeric data

## Files Generated

1. **Template**: `lfs_popul_regio_template.xlsx` (23,760 records)
   - Contains all possible dimension combinations
   - All values set to "_Z" as placeholders

2. **Parsed Data**: `lfs_popul_regio_parsed.xlsx` (15,876 records)
   - Contains actual extracted data
   - Properly mapped dimensions and values

## Next Steps

1. ✅ **POPUL-Regio sheet completed and verified**
2. 🔄 **Process additional sheets from File 01**
3. 🔄 **Extend to Files 02 and 03**
4. 🔄 **Combine all data into comprehensive wide table**

## Notes

- The parser successfully handles the complex cross-tabulation structure
- Age group data is available for all sex categories
- Nationality and marital status data is only available for total population
- The modular approach allows easy extension to other sheets and files
