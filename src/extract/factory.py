# src/extract/factory.py
from src.transform.table_parser import parse_table_format
from src.transform.column_parser import parse_column_format

def get_processor_by_headers(df):
    """
    Factory Pattern: Scans the file headers to map the input 
    to the correct parsing algorithm.
    """
    headers = [str(col).strip().upper() for col in df.columns]
    
    # Table Blocks must contain headers: FID and ACCKEYS
    if "FID" in headers and "ACCKEYS" in headers:
        return parse_table_format
    
    # Column Blocks must contain headers: FID and DI
    elif "FID" in headers and "DI" in headers:
        return parse_column_format
    
    raise ValueError("File validation failed: File lacks recognizable FID/ACCKEYS or FID/DI header blocks.")
