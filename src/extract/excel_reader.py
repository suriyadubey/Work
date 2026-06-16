# src/extract/excel_reader.py
import pandas as pd
import numpy as np

def load_data_file(file_path: str) -> pd.DataFrame:
    """Loads CSV or Excel sheets into a Pandas Dataframe and strips hidden characters."""
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path, keep_default_na=False)
    else:
        df = pd.read_excel(file_path, keep_default_na=False)
    
    # Automatically remove hidden spaces (\xa0) and non-printables
    df = df.map(lambda x: str(x).replace('\xa0', '').strip() if isinstance(x, str) else x)
    return df.replace(r'^\s*$', np.nan, regex=True) # Normalize blanks to NaN

def parse_mixed_excel(file_path: str, tbl_col_hashes: set = None):
    """
    Parses the TBL and COL sheet of the Excel workbook, dynamically
    mapping Table and Column rows and returning (tables_dict, columns_dict, processed_hashes).
    """
    from src.transform.validators import verify_constraints
    from src.transform.state_manager import get_row_hash
    
    df = pd.read_excel(file_path, sheet_name='TBL and COL', header=None)
    
    tables = {}
    columns = {}
    processed_hashes = []
    
    current_type = None
    current_headers = None
    
    def clean_val(val):
        if pd.isna(val):
            return None
        if isinstance(val, (bool, np.bool_)):
            return bool(val)
        if isinstance(val, (float, np.floating)):
            if val.is_integer():
                return int(val)
            return val
        if isinstance(val, (int, np.integer)):
            return int(val)
        if isinstance(val, str):
            val = val.strip()
            if len(val) >= 2 and val.startswith('"') and val.endswith('"'):
                val = val[1:-1]
            if val.lower() == 'true':
                return True
            if val.lower() == 'false':
                return False
            val = val.replace('\xa0', '').strip()
            if not val:
                return None
            try:
                return int(val)
            except ValueError:
                pass
            try:
                f = float(val)
                if f.is_integer():
                    return int(f)
                return f
            except ValueError:
                pass
            return val
        return val

    for idx, row in df.iterrows():
        col1 = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
        col3 = str(row.iloc[3]).strip() if pd.notna(row.iloc[3]) else ""
        
        if col1 in ['Table', 'Column'] and col3 == 'FID':
            current_type = col1
            current_headers = [str(x).strip() if pd.notna(x) else "" for x in row.values]
            continue
            
        if current_type and col3 and col3 != 'FID':
            fid = col3
            row_dict = {}
            for col_idx, header in enumerate(current_headers):
                if header:
                    val = clean_val(row.iloc[col_idx])
                    if val is not None and val != "":
                        if current_type == 'Column' and header == 'DI':
                            row_dict['ACCKEYS'] = val
                        else:
                            row_dict[header] = val
            
            if not row_dict:
                continue
                
            row_hash = get_row_hash(row_dict)
            processed_hashes.append(row_hash)
            
            if tbl_col_hashes is not None:
                if row_hash in tbl_col_hashes:
                    continue
                
            verify_constraints(row_dict, current_type.upper())
            
            if current_type == 'Table':
                tables[fid] = row_dict
            elif current_type == 'Column':
                if fid not in columns:
                    columns[fid] = []
                columns[fid].append(row_dict)
                
    return tables, columns, processed_hashes
