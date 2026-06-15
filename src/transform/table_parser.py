# src/transform/table_parser.py
from src.transform.validators import verify_constraints

def parse_table_format(df):
    """Transforms raw table definitions grouped by FID."""
    grouped_records = {}
    records = df.to_dict(orient="records")
    
    for row in records:
        verify_constraints(row, "TABLE")
        fid = str(row.get("FID")).strip()
        if not fid: continue
        
        if fid not in grouped_records:
            grouped_records[fid] = {"type": "TABLE", "records": []}
        grouped_records[fid]["records"].append(row)
        
    return grouped_records