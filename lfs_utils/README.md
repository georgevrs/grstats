# LFS Utilities Package

This package contains modules for processing LFS (Labour Force Survey) annual datasets into SDMX-compliant wide format.

## Structure

```
lfs_utils/
├── __init__.py                    # Package initialization
├── sheet_analyzer.py             # Basic sheet analysis
├── advanced_sheet_analyzer.py    # Advanced hierarchical analysis
├── data_parser.py                # Data extraction and SDMX formatting (for POPUL-Regio)
├── popul_status_parser.py        # Specialized parser for POPUL-Status sheet
├── educ_sexage_parser.py        # Specialized parser for EDUC-SexAge sheet
├── educ_regio_parser.py          # Specialized parser for EDUC-Regio sheet
├── README.md                     # This file
├── POPUL_Regio_analysis_summary.md  # Detailed analysis of first sheet
└── POPUL_Status_analysis_summary.md # Detailed analysis of second sheet
```

## Modules

### 1. Sheet Analyzer (`sheet_analyzer.py`)
- Basic Excel sheet analysis
- Extracts raw dimension information
- Identifies data areas and header structures

### 2. Advanced Sheet Analyzer (`advanced_sheet_analyzer.py`)
- Advanced pattern recognition for complex Excel layouts
- Identifies hierarchical headers and cross-tabulation
- Extracts clean dimension information
- Maps data structure and layout

### 3. Data Parser (`data_parser.py`)
- **Specialized for POPUL-Regio sheet**
- Handles population data with region breakdowns
- Creates SDMX-compliant wide format
- Manages sex, age, nationality, and marital status dimensions

### 4. POPUL-Status Parser (`popul_status_parser.py`)
- **Specialized for POPUL-Status sheet**
- Handles employment status hierarchy (Employed → Self employed, Family workers, etc.)
- Manages complex employment status breakdowns
- Creates SDMX-compliant wide format with employment dimensions

### 4. EDUC-SexAge Parser (`educ_sexage_parser.py`)
- **Specialized for EDUC-SexAge sheet**
- Handles complex education level hierarchy (Main categories + Sub-categories)
- Manages education participation, NEET analysis, and lifelong learning metrics
- Creates SDMX-compliant wide format with education-specific dimensions

### 5. EDUC-Regio Parser (`educ_regio_parser.py`)
- **Specialized for EDUC-Regio sheet**
- Handles complex education level hierarchy (Main categories + Sub-categories) organized by region
- Manages education participation, NEET analysis, and lifelong learning metrics by geographic area
- Creates SDMX-compliant wide format with education-specific dimensions and regional organization

### 6. EDUC-Status Parser (`educ_status_parser.py`)
- **Specialized for EDUC-Status sheet**
- Handles complex employment status hierarchy (Main status + Sub-status) combined with education level hierarchy (Main categories + Sub-categories)
- Manages employment status + education level cross-analysis with comprehensive metrics
- Creates SDMX-compliant wide format with employment and education dimensions

### 7. STATUS-SexAge Parser (`status_sexage_parser.py`)
- **Specialized for STATUS-SexAge sheet**
- Handles employment status hierarchy (Main status + Sub-status)
- Manages complex employment status breakdowns with multiple units of measure (persons, percentage)
- Creates SDMX-compliant wide format with employment dimensions

### 8. STATUS-Regio Parser (`status_regio_parser.py`)
- **Specialized for STATUS-Regio sheet**
- Handles employment status hierarchy (Main status + Sub-status) organized by region
- Manages complex employment status breakdowns with multiple units of measure (persons, percentage) by geographic area
- Creates SDMX-compliant wide format with employment dimensions and regional organization

### 9. JOB-SexAge Parser (`job_sexage_parser.py`)
- **Specialized for JOB-SexAge sheet**
- Handles complex job characteristics hierarchy (Main characteristic + Sub-category + Sub-sub-category) organized by sex and age
- Manages comprehensive job analysis including economic sectors, employment types, working conditions, and atypical work patterns
- Creates SDMX-compliant wide format with job characteristics dimensions and demographic organization
- **FINAL CORRECTED**: Successfully captures ALL values with proper three-level hierarchy mapping

### JOB-SexAge
- Complex job characteristics data organized by Year + Sex + Age Group
- Hierarchical job characteristics structure (Main characteristic + Sub-category + Sub-sub-category) organized by demographics
- Comprehensive job analysis including economic sectors, employment types, working conditions, and atypical work patterns
- Cross-tabulated format with complex header structure across multiple rows
- Job characteristics + Sex + Age cross-analysis for comprehensive workforce insights

## Current Status

### ✅ **Completed Sheets**

#### 1. POPUL-Regio Sheet
- **File**: `A0101_SJO03_TS_AN_00_1981_00_2024_01_F_EN.xlsx` (File 01)
- **Records**: 16,464
- **Dimensions**: Year, Region, Sex, Age_Group, Nationality, Marital_Status, Value
- **Structure**: Population data by region with demographic breakdowns
- **Output**: Template (16,464 records) + Parsed data (16,464 records)

#### 2. POPUL-Status Sheet
- **File**: `A0101_SJO03_TS_AN_00_1981_00_2024_01_F_EN.xlsx` (File 01)
- **Records**: 10,993
- **Dimensions**: Year, Main_Employment_Status, Sub_Employment_Status, Sex, Age_Group, Marital_Status, Nationality, Urbanization, Value
- **Structure**: Employment status data with hierarchical breakdowns
- **Output**: Template (37,800 records) + Parsed data (10,993 records)

#### 3. EDUC-SexAge Sheet
- **File**: `A0101_SJO03_TS_AN_00_1981_00_2024_01_F_EN.xlsx` (File 01)
- **Records**: 10,567
- **Dimensions**: Year, Sex, Age_Group, Education_Level_Main, Education_Level_Sub, Formal_Informal_Education, NEET_Category, Tertiary_30_34, Lifelong_20_64, Value
- **Structure**: Education data with hierarchical education levels and comprehensive metrics
- **Output**: Template (89,760 records) + Parsed data (10,567 records)

#### 4. EDUC-Regio Sheet
- **File**: `A0101_SJO03_TS_AN_00_1981_00_2024_01_F_EN.xlsx` (File 01)
- **Records**: 10,298
- **Dimensions**: Year, Region, Education_Level_Main, Education_Level_Sub, Formal_Informal_Education, NEET_Category, Tertiary_30_34, Lifelong_20_64, Value
- **Structure**: Education data organized by region with hierarchical education levels and comprehensive metrics
- **Output**: Template (59,840 records) + Parsed data (10,298 records)

#### 5. EDUC-Status Sheet
- **File**: `A0101_SJO03_TS_AN_00_1981_00_2024_01_F_EN.xlsx` (File 01)
- **Records**: 6,724
- **Dimensions**: Year, Main_Employment_Status, Sub_Employment_Status, Education_Level_Main, Education_Level_Sub, Formal_Informal_Education, NEET_Category, Tertiary_30_34, Lifelong_20_64, Value
- **Structure**: Employment status + Education level data with hierarchical breakdowns for both dimensions
- **Output**: Template (38,324 records) + Parsed data (6,724 records)

#### 6. STATUS-SexAge Sheet
- **File**: `A0101_SJO03_TS_AN_00_1981_00_2024_01_F_EN.xlsx` (File 01)
- **Records**: 9,624
- **Dimensions**: Year, Sex, Age_Group, Labour_Force_Status, Labour_Force_Subcategory, Unit_of_Measure, Value
- **Structure**: Employment status data with hierarchical breakdowns and multiple units of measure (persons, percentage)
- **Output**: Template (146,520 records) + Parsed data (9,624 records)

#### 7. STATUS-Regio Sheet
- **File**: `A0101_SJO03_TS_AN_00_1981_00_2024_01_F_EN.xlsx` (File 01)
- **Records**: 10,298
- **Dimensions**: Year, Region, Main_Employment_Status, Sub_Employment_Status, Value
- **Structure**: Employment status data organized by region with hierarchical breakdowns
- **Output**: Template (59,840 records) + Parsed data (10,298 records)

#### 8. JOB-SexAge Sheet (FINAL CORRECTED)
- **File**: `A0101_SJO03_TS_AN_00_1981_00_2024_02_F_EN.xlsx` (File 02)
- **Records**: 8,188
- **Dimensions**: Year, Sex, Age_Group, Job_Characteristic, Job_Subcategory, Job_Sub_Subcategory, Unit_of_Measure, Value
- **Structure**: Complex job characteristics data organized by sex and age with hierarchical breakdowns including economic sectors, employment types, working conditions, and atypical work patterns
- **Hierarchy**: Three-level structure (Main characteristic → Subcategory → Sub-subcategory) with ALL values captured
- **Data Quality**: 7,494 records (91.5%) have all three levels populated, 694 records (8.5%) use "_Z" placeholders appropriately
- **Output**: Parsed data (8,188 records) - **FINAL CORRECTED**

### For JOB-SexAge Sheet
```python
from lfs_utils.advanced_sheet_analyzer import AdvancedSheetAnalyzer
from lfs_utils.job_sexage_parser import JOBSexAgeParser

analyzer = AdvancedSheetAnalyzer()
parser = JOBSexAgeParser()

analysis = analyzer.analyze_sheet(file_path, "JOB-SexAge")
parsed_data = parser.parse_sheet(analysis)
```