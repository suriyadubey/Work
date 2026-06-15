# src/transform/column_parser.py
from src.transform.validators import verify_constraints

def parse_column_format(df):
    """Transforms raw structural column matrix profiles grouped by FID."""
    grouped_records = {}
    records = df.to_dict(orient="records")
    
    for row in records:
        verify_constraints(row, "COLUMN")
        fid = str(row.get("FID")).strip()
        if not fid: continue
        
        if fid not in grouped_records:
            grouped_records[fid] = {"type": "COLUMN", "records": []}
        grouped_records[fid]["records"].append(row)
        
    return grouped_records