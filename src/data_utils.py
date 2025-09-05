"""
Utility functions for Excel data processing and analysis
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from typing import Union, List, Optional
import warnings

def load_excel_file(file_path: Union[str, Path], 
                   sheet_name: Optional[Union[str, int]] = None,
                   **kwargs) -> pd.DataFrame:
    """
    Load Excel file with automatic engine detection
    
    Parameters:
    -----------
    file_path : str or Path
        Path to the Excel file
    sheet_name : str, int, or None
        Sheet name or index to load (None for first sheet)
    **kwargs : dict
        Additional arguments for pd.read_excel()
    
    Returns:
    --------
    pandas.DataFrame
        Loaded data
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    file_ext = file_path.suffix.lower()
    
    try:
        if file_ext == '.xls':
            # Use xlrd engine for .xls files
            df = pd.read_excel(file_path, sheet_name=sheet_name, engine='xlrd', **kwargs)
        elif file_ext in ['.xlsx', '.xlsm']:
            # Use openpyxl engine for newer Excel formats
            df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl', **kwargs)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
            
        print(f"✅ Successfully loaded: {file_path.name}")
        print(f"📋 Sheet: {sheet_name if sheet_name else 'First sheet'}")
        print(f"📊 Shape: {df.shape}")
        
        return df
        
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        raise

def list_excel_sheets(file_path: Union[str, Path]) -> List[str]:
    """
    List all sheet names in an Excel file
    
    Parameters:
    -----------
    file_path : str or Path
        Path to the Excel file
    
    Returns:
    --------
    list
        Sheet names
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    file_ext = file_path.suffix.lower()
    
    try:
        if file_ext == '.xls':
            xl_file = pd.ExcelFile(file_path, engine='xlrd')
        else:
            xl_file = pd.ExcelFile(file_path, engine='openpyxl')
            
        return xl_file.sheet_names
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        raise

def data_overview(df: pd.DataFrame) -> None:
    """
    Print comprehensive overview of the dataset
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Dataset to analyze
    """
    print("📊 Dataset Overview")
    print("=" * 50)
    print(f"Shape: {df.shape}")
    print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    print("\n📋 Column Information:")
    print("-" * 30)
    for i, col in enumerate(df.columns):
        dtype = df[col].dtype
        null_count = df[col].isnull().sum()
        null_pct = (null_count / len(df)) * 100
        unique_count = df[col].nunique()
        
        print(f"{i+1:2d}. {col:<20} | {str(dtype):<12} | "
              f"Nulls: {null_count:4d} ({null_pct:5.1f}%) | "
              f"Unique: {unique_count:5d}")
    
    print("\n🔍 Missing Values Summary:")
    missing_data = df.isnull().sum()
    if missing_data.sum() == 0:
        print("✅ No missing values found!")
    else:
        missing_summary = missing_data[missing_data > 0].sort_values(ascending=False)
        for col, count in missing_summary.items():
            pct = (count / len(df)) * 100
            print(f"  {col}: {count} ({pct:.1f}%)")

def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean column names by removing special characters and standardizing format
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Dataset with columns to clean
    
    Returns:
    --------
    pandas.DataFrame
        Dataset with cleaned column names
    """
    df_cleaned = df.copy()
    
    # Convert to lowercase and replace spaces/special chars with underscores
    df_cleaned.columns = (df_cleaned.columns
                         .str.lower()
                         .str.replace(' ', '_', regex=False)
                         .str.replace('[^a-zA-Z0-9_]', '_', regex=True)
                         .str.replace('_+', '_', regex=True)
                         .str.strip('_'))
    
    return df_cleaned

def detect_date_columns(df: pd.DataFrame, 
                       date_keywords: List[str] = None) -> List[str]:
    """
    Detect potential date columns based on column names and data types
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Dataset to analyze
    date_keywords : list, optional
        Keywords to look for in column names
    
    Returns:
    --------
    list
        List of potential date column names
    """
    if date_keywords is None:
        date_keywords = ['date', 'datum', 'tijd', 'time', 'created', 'updated', 
                        'start', 'end', 'begin', 'eind', 'aanvraag', 'goedkeuring']
    
    potential_date_cols = []
    
    for col in df.columns:
        # Check if column name contains date keywords
        if any(keyword in col.lower() for keyword in date_keywords):
            potential_date_cols.append(col)
        # Check if column contains date-like strings
        elif df[col].dtype == 'object':
            sample_values = df[col].dropna().head(10).astype(str)
            if any(pd.to_datetime(val, errors='coerce', infer_datetime_format=True) is not pd.NaT 
                   for val in sample_values):
                potential_date_cols.append(col)
    
    return potential_date_cols

def create_summary_stats(df: pd.DataFrame, 
                        numeric_cols: List[str] = None) -> pd.DataFrame:
    """
    Create enhanced summary statistics for numeric columns
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Dataset to analyze
    numeric_cols : list, optional
        Specific numeric columns to analyze
    
    Returns:
    --------
    pandas.DataFrame
        Enhanced summary statistics
    """
    if numeric_cols is None:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    stats_list = []
    
    for col in numeric_cols:
        if col in df.columns:
            series = df[col].dropna()
            
            stats = {
                'column': col,
                'count': len(series),
                'missing': df[col].isnull().sum(),
                'mean': series.mean(),
                'median': series.median(),
                'std': series.std(),
                'min': series.min(),
                'max': series.max(),
                'q25': series.quantile(0.25),
                'q75': series.quantile(0.75),
                'skewness': series.skew(),
                'kurtosis': series.kurtosis()
            }
            
            stats_list.append(stats)
    
    return pd.DataFrame(stats_list).round(3)

def quick_viz_numeric(df: pd.DataFrame, 
                     col: str, 
                     title: str = None) -> go.Figure:
    """
    Create quick visualization for numeric column
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Dataset containing the column
    col : str
        Column name to visualize
    title : str, optional
        Chart title
    
    Returns:
    --------
    plotly.graph_objects.Figure
        Interactive histogram
    """
    if title is None:
        title = f"Distribution of {col}"
    
    fig = px.histogram(df, x=col, title=title, 
                      marginal="box", nbins=30)
    
    fig.update_layout(
        xaxis_title=col,
        yaxis_title="Frequency",
        height=500
    )
    
    return fig

def quick_viz_categorical(df: pd.DataFrame, 
                         col: str, 
                         max_categories: int = 20,
                         title: str = None) -> go.Figure:
    """
    Create quick visualization for categorical column
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Dataset containing the column
    col : str
        Column name to visualize
    max_categories : int
        Maximum number of categories to show
    title : str, optional
        Chart title
    
    Returns:
    --------
    plotly.graph_objects.Figure
        Interactive bar chart or pie chart
    """
    if title is None:
        title = f"Distribution of {col}"
    
    value_counts = df[col].value_counts().head(max_categories)
    
    if len(value_counts) <= 8:
        # Use pie chart for few categories
        fig = px.pie(values=value_counts.values, 
                    names=value_counts.index, 
                    title=title)
    else:
        # Use bar chart for many categories
        fig = px.bar(x=value_counts.index, 
                    y=value_counts.values, 
                    title=title)
        fig.update_layout(
            xaxis_title=col,
            yaxis_title="Count"
        )
    
    fig.update_layout(height=500)
    return fig

def export_to_excel(df: pd.DataFrame, 
                   file_path: Union[str, Path],
                   sheet_name: str = 'Data') -> None:
    """
    Export DataFrame to Excel with formatting
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Dataset to export
    file_path : str or Path
        Output file path
    sheet_name : str
        Name for the Excel sheet
    """
    file_path = Path(file_path)
    
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Get the workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]
        
        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    print(f"✅ Data exported to: {file_path}")
