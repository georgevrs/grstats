"""
Advanced Sheet Analyzer for LFS Annual Datasets
Properly identifies hierarchical structure and dimensions from complex Excel layouts
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedSheetAnalyzer:
    """Advanced analyzer for complex hierarchical Excel sheets"""
    
    def __init__(self):
        self.dimensions = {}
        self.data_structure = {}
        
    def analyze_sheet(self, file_path: str, sheet_name: str) -> Dict[str, Any]:
        """
        Analyze a specific sheet with advanced pattern recognition
        
        Args:
            file_path: Path to the Excel file
            sheet_name: Name of the sheet to analyze
            
        Returns:
            Dictionary containing detailed analysis results
        """
        try:
            logger.info(f"Advanced analysis of sheet '{sheet_name}' from file '{file_path}'")
            
            # Read the sheet
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
            logger.info(f"Sheet loaded: {df.shape[0]} rows x {df.shape[1]} columns")
            
            # Analyze the structure
            analysis = {
                'file_path': file_path,
                'sheet_name': sheet_name,
                'raw_dataframe': df,
                'dimensions': self._extract_clean_dimensions(df),
                'data_structure': self._analyze_data_structure(df),
                'hierarchical_layout': self._identify_hierarchical_layout(df),
                'data_mapping': self._create_data_mapping(df)
            }
            
            logger.info(f"Advanced analysis complete. Found {len(analysis['dimensions'])} clean dimensions")
            return analysis
            
        except Exception as e:
            logger.error(f"Error in advanced analysis: {e}")
            raise
    
    def _extract_clean_dimensions(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """Extract clean dimension information by analyzing the header structure"""
        dimensions = {}
        
        # Look for the main dimension headers in the first few rows
        # Based on the analysis, we can see the structure:
        # Row 0: Main categories (Population, Total, Males, Females, Nationality, Marital status)
        # Row 1: Sub-categories (Year, Region, Age groups, etc.)
        # Row 2: Empty or continuation
        # Row 3+: Actual data
        
        # Extract main dimensions from row 0
        main_dims = self._extract_row_dimensions(df, 0)
        if main_dims:
            dimensions.update(main_dims)
        
        # Extract sub-dimensions from row 1
        sub_dims = self._extract_row_dimensions(df, 1)
        if sub_dims:
            dimensions.update(sub_dims)
        
        # Clean up dimensions by removing duplicates and meaningless values
        dimensions = self._clean_dimensions(dimensions)
        
        return dimensions
    
    def _extract_row_dimensions(self, df: pd.DataFrame, row_idx: int) -> Dict[str, List[str]]:
        """Extract dimensions from a specific row"""
        dimensions = {}
        
        if row_idx >= len(df):
            return dimensions
        
        row = df.iloc[row_idx]
        
        for col_idx, cell_value in enumerate(row):
            if pd.notna(cell_value) and isinstance(cell_value, str):
                cell_str = str(cell_value).strip()
                if cell_str and len(cell_str) > 1 and cell_str != '...':
                    # Look for values in the same column below
                    values = self._extract_column_values(df, row_idx, col_idx)
                    if values:
                        dimensions[cell_str] = values
        
        return dimensions
    
    def _extract_column_values(self, df: pd.DataFrame, header_row: int, header_col: int) -> List[str]:
        """Extract values from a column below the header"""
        values = []
        
        # Look in the same column below the header
        for row_idx in range(header_row + 1, min(header_row + 50, len(df))):
            cell_value = df.iloc[row_idx, header_col]
            if pd.notna(cell_value) and str(cell_value).strip() and str(cell_value).strip() != '...':
                cell_str = str(cell_value).strip()
                # Filter out numeric values and very long strings
                if not self._is_numeric(cell_str) and len(cell_str) < 50:
                    values.append(cell_str)
        
        return list(set(values))  # Remove duplicates
    
    def _is_numeric(self, value: str) -> bool:
        """Check if a string represents a numeric value"""
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def _clean_dimensions(self, dimensions: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Clean up dimensions by removing duplicates and meaningless values"""
        cleaned = {}
        
        for dim_name, dim_values in dimensions.items():
            # Filter out dimensions with too many values (likely not categorical)
            if len(dim_values) <= 50:
                # Remove numeric values and very long strings
                clean_values = [
                    val for val in dim_values 
                    if not self._is_numeric(val) and len(val) < 50 and val != '...'
                ]
                if clean_values:
                    cleaned[dim_name] = clean_values
        
        return cleaned
    
    def _analyze_data_structure(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze the data structure and layout"""
        structure = {
            'header_rows': [],
            'data_start_row': None,
            'data_end_row': None,
            'data_start_col': None,
            'data_end_col': None,
            'column_structure': [],
            'row_structure': []
        }
        
        # Find where data starts (first row with numeric values)
        for row_idx in range(len(df)):
            row_has_numeric = False
            for col_idx in range(df.shape[1]):
                cell_value = df.iloc[row_idx, col_idx]
                if pd.notna(cell_value) and self._is_numeric(str(cell_value)):
                    row_has_numeric = True
                    if structure['data_start_row'] is None:
                        structure['data_start_row'] = row_idx
                        structure['data_start_col'] = col_idx
                    structure['data_end_row'] = row_idx
                    structure['data_end_col'] = max(structure['data_end_col'] or col_idx, col_idx)
            
            if row_has_numeric:
                structure['data_end_row'] = row_idx
        
        # Analyze column structure
        if structure['data_start_row'] is not None:
            structure['column_structure'] = self._analyze_columns(df, structure['data_start_row'])
            structure['row_structure'] = self._analyze_rows(df, structure['data_start_row'])
        
        return structure
    
    def _analyze_columns(self, df: pd.DataFrame, data_start_row: int) -> List[Dict[str, Any]]:
        """Analyze the structure of columns"""
        columns = []
        
        for col_idx in range(df.shape[1]):
            col_info = {
                'column_index': col_idx,
                'header_values': [],
                'data_type': 'unknown',
                'sample_values': []
            }
            
            # Get header values from rows above data
            for row_idx in range(data_start_row):
                cell_value = df.iloc[row_idx, col_idx]
                if pd.notna(cell_value) and str(cell_value).strip():
                    col_info['header_values'].append(str(cell_value).strip())
            
            # Get sample data values
            for row_idx in range(data_start_row, min(data_start_row + 10, len(df))):
                cell_value = df.iloc[row_idx, col_idx]
                if pd.notna(cell_value):
                    col_info['sample_values'].append(cell_value)
            
            # Determine data type
            if col_info['sample_values']:
                if all(self._is_numeric(str(val)) for val in col_info['sample_values']):
                    col_info['data_type'] = 'numeric'
                else:
                    col_info['data_type'] = 'categorical'
            
            columns.append(col_info)
        
        return columns
    
    def _analyze_rows(self, df: pd.DataFrame, data_start_row: int) -> List[Dict[str, Any]]:
        """Analyze the structure of rows"""
        rows = []
        
        for row_idx in range(data_start_row, min(data_start_row + 20, len(df))):
            row_info = {
                'row_index': row_idx,
                'sample_values': [],
                'has_numeric': False
            }
            
            for col_idx in range(df.shape[1]):
                cell_value = df.iloc[row_idx, col_idx]
                if pd.notna(cell_value):
                    row_info['sample_values'].append(cell_value)
                    if self._is_numeric(str(cell_value)):
                        row_info['has_numeric'] = True
            
            rows.append(row_info)
        
        return rows
    
    def _identify_hierarchical_layout(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Identify the hierarchical layout of the sheet"""
        hierarchy = {
            'main_categories': [],
            'sub_categories': [],
            'cross_tabulation': False,
            'pivot_structure': False
        }
        
        # Look for main categories in row 0
        if len(df) > 0:
            row0 = df.iloc[0]
            main_cats = [str(val).strip() for val in row0 if pd.notna(val) and str(val).strip() and str(val).strip() != '...']
            hierarchy['main_categories'] = main_cats
        
        # Look for sub-categories in row 1
        if len(df) > 1:
            row1 = df.iloc[1]
            sub_cats = [str(val).strip() for val in row1 if pd.notna(val) and str(val).strip() and str(val).strip() != '...']
            hierarchy['sub_categories'] = sub_cats
        
        # Determine if this is a cross-tabulation
        if len(hierarchy['main_categories']) > 1 and len(hierarchy['sub_categories']) > 1:
            hierarchy['cross_tabulation'] = True
        
        return hierarchy
    
    def _create_data_mapping(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Create a mapping of how data is organized"""
        mapping = {
            'dimension_columns': [],
            'value_columns': [],
            'row_identifiers': [],
            'column_identifiers': []
        }
        
        # Based on the analysis, identify dimension vs value columns
        if len(df) > 1:
            # Row 1 contains the main dimension headers
            row1 = df.iloc[1]
            
            for col_idx, cell_value in enumerate(row1):
                if pd.notna(cell_value) and str(cell_value).strip():
                    cell_str = str(cell_value).strip()
                    if cell_str in ['Year', 'Region - NUTS II']:
                        mapping['dimension_columns'].append({
                            'name': cell_str,
                            'column_index': col_idx,
                            'type': 'identifier'
                        })
                    elif self._is_age_group(cell_str):
                        mapping['dimension_columns'].append({
                            'name': 'Age Group',
                            'column_index': col_idx,
                            'type': 'categorical'
                        })
                    else:
                        mapping['value_columns'].append({
                            'name': cell_str,
                            'column_index': col_idx,
                            'type': 'value'
                        })
        
        return mapping
    
    def _is_age_group(self, value: str) -> bool:
        """Check if a value represents an age group"""
        age_patterns = ['0-14', '15-19', '20-24', '25-29', '30-44', '45-64', '65+']
        return value in age_patterns
    
    def print_advanced_analysis(self, analysis: Dict[str, Any]):
        """Print a comprehensive analysis summary"""
        print(f"\n{'='*80}")
        print(f"ADVANCED SHEET ANALYSIS SUMMARY")
        print(f"{'='*80}")
        print(f"File: {analysis['file_path']}")
        print(f"Sheet: {analysis['sheet_name']}")
        print(f"Shape: {analysis['raw_dataframe'].shape}")
        
        # Print dimensions
        print(f"\nCLEAN DIMENSIONS FOUND: {len(analysis['dimensions'])}")
        for dim_name, dim_values in analysis['dimensions'].items():
            print(f"  - {dim_name}: {len(dim_values)} values")
            if dim_values:
                print(f"    Sample: {dim_values[:5]}")
        
        # Print data structure
        data_struct = analysis['data_structure']
        print(f"\nDATA STRUCTURE:")
        print(f"  Data starts at row {data_struct['data_start_row']}")
        print(f"  Data ends at row {data_struct['data_end_row']}")
        print(f"  Data spans columns {data_struct['data_start_col']} to {data_struct['data_end_col']}")
        
        # Print hierarchical layout
        hierarchy = analysis['hierarchical_layout']
        print(f"\nHIERARCHICAL LAYOUT:")
        print(f"  Main categories: {hierarchy['main_categories']}")
        print(f"  Sub categories: {hierarchy['sub_categories']}")
        print(f"  Cross-tabulation: {hierarchy['cross_tabulation']}")
        
        # Print data mapping
        mapping = analysis['data_mapping']
        print(f"\nDATA MAPPING:")
        print(f"  Dimension columns: {len(mapping['dimension_columns'])}")
        for dim_col in mapping['dimension_columns']:
            print(f"    - {dim_col['name']} (col {dim_col['column_index']}, type: {dim_col['type']})")
        print(f"  Value columns: {len(mapping['value_columns'])}")
        
        print(f"{'='*80}\n")
