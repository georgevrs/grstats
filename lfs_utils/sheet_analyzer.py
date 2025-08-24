"""
Sheet Analyzer Module for LFS Annual Datasets
Analyzes Excel sheets to extract dimension information and structure
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SheetAnalyzer:
    """Analyzes Excel sheets to understand their structure and dimensions"""
    
    def __init__(self):
        self.dimensions = {}
        self.sheet_structure = {}
        
    def analyze_sheet(self, file_path: str, sheet_name: str) -> Dict[str, Any]:
        """
        Analyze a specific sheet from an Excel file
        
        Args:
            file_path: Path to the Excel file
            sheet_name: Name of the sheet to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            logger.info(f"Analyzing sheet '{sheet_name}' from file '{file_path}'")
            
            # Read the sheet
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
            logger.info(f"Sheet loaded: {df.shape[0]} rows x {df.shape[1]} columns")
            
            # Analyze the structure
            analysis = {
                'file_path': file_path,
                'sheet_name': sheet_name,
                'dimensions': self._extract_dimensions(df),
                'data_area': self._identify_data_area(df),
                'header_structure': self._analyze_header_structure(df),
                'sample_data': self._get_sample_data(df),
                'raw_dataframe': df
            }
            
            logger.info(f"Analysis complete. Found {len(analysis['dimensions'])} dimensions")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing sheet: {e}")
            raise
    
    def _extract_dimensions(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """Extract dimension information from the dataframe"""
        dimensions = {}
        
        # Look for dimension headers in the first few rows
        for row_idx in range(min(10, len(df))):
            row = df.iloc[row_idx]
            for col_idx, cell_value in enumerate(row):
                if pd.notna(cell_value) and isinstance(cell_value, str):
                    cell_str = str(cell_value).strip()
                    if cell_str and len(cell_str) > 1:  # Non-empty meaningful strings
                        if cell_str not in dimensions:
                            dimensions[cell_str] = []
                        
                        # Look for values in subsequent rows/columns
                        values = self._find_dimension_values(df, row_idx, col_idx)
                        if values:
                            dimensions[cell_str] = values
        
        return dimensions
    
    def _find_dimension_values(self, df: pd.DataFrame, header_row: int, header_col: int) -> List[str]:
        """Find values for a specific dimension"""
        values = []
        
        # Look in the same column below the header
        for row_idx in range(header_row + 1, min(header_row + 20, len(df))):
            cell_value = df.iloc[row_idx, header_col]
            if pd.notna(cell_value) and str(cell_value).strip():
                values.append(str(cell_value).strip())
        
        # Look in the same row to the right of the header
        for col_idx in range(header_col + 1, min(header_col + 20, df.shape[1])):
            cell_value = df.iloc[header_row, col_idx]
            if pd.notna(cell_value) and str(cell_value).strip():
                values.append(str(cell_value).strip())
        
        return list(set(values))  # Remove duplicates
    
    def _identify_data_area(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Identify where the actual data values are located"""
        data_area = {
            'start_row': None,
            'start_col': None,
            'end_row': None,
            'end_col': None
        }
        
        # Look for numeric data
        for row_idx in range(len(df)):
            for col_idx in range(df.shape[1]):
                cell_value = df.iloc[row_idx, col_idx]
                if pd.notna(cell_value) and isinstance(cell_value, (int, float)):
                    if data_area['start_row'] is None:
                        data_area['start_row'] = row_idx
                        data_area['start_col'] = col_idx
                    data_area['end_row'] = row_idx
                    data_area['end_col'] = col_idx
        
        return data_area
    
    def _analyze_header_structure(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze the header structure of the sheet"""
        header_info = {
            'row_headers': [],
            'column_headers': [],
            'hierarchical_structure': False
        }
        
        # Look for row headers (first few columns)
        for col_idx in range(min(5, df.shape[1])):
            col_values = []
            for row_idx in range(min(20, len(df))):
                cell_value = df.iloc[row_idx, col_idx]
                if pd.notna(cell_value):
                    col_values.append(str(cell_value).strip())
            if col_values:
                header_info['row_headers'].append({
                    'column_index': col_idx,
                    'values': col_values
                })
        
        # Look for column headers (first few rows)
        for row_idx in range(min(5, len(df))):
            row_values = []
            for col_idx in range(df.shape[1]):
                cell_value = df.iloc[row_idx, col_idx]
                if pd.notna(cell_value):
                    row_values.append(str(cell_value).strip())
            if row_values:
                header_info['column_headers'].append({
                    'row_index': row_idx,
                    'values': row_values
                })
        
        return header_info
    
    def _get_sample_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get sample data for analysis"""
        sample = {
            'first_10_rows': df.head(10).to_dict('records'),
            'last_5_rows': df.tail(5).to_dict('records'),
            'shape': df.shape,
            'dtypes': df.dtypes.to_dict()
        }
        return sample
    
    def print_analysis_summary(self, analysis: Dict[str, Any]):
        """Print a summary of the analysis"""
        print(f"\n{'='*60}")
        print(f"SHEET ANALYSIS SUMMARY")
        print(f"{'='*60}")
        print(f"File: {analysis['file_path']}")
        print(f"Sheet: {analysis['sheet_name']}")
        print(f"Shape: {analysis['raw_dataframe'].shape}")
        print(f"\nDimensions Found: {len(analysis['dimensions'])}")
        
        for dim_name, dim_values in analysis['dimensions'].items():
            print(f"  - {dim_name}: {len(dim_values)} values")
            if dim_values:
                print(f"    Sample values: {dim_values[:5]}")
        
        print(f"\nData Area:")
        data_area = analysis['data_area']
        if data_area['start_row'] is not None:
            print(f"  Start: Row {data_area['start_row']}, Col {data_area['start_col']}")
            print(f"  End: Row {data_area['end_row']}, Col {data_area['end_col']}")
        else:
            print("  No numeric data found")
        
        print(f"\nHeader Structure:")
        header_info = analysis['header_structure']
        print(f"  Row headers: {len(header_info['row_headers'])} columns")
        print(f"  Column headers: {len(header_info['column_headers'])} rows")
        
        print(f"{'='*60}\n")
