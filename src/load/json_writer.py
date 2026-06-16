# src/load/json_writer.py
import os
import json

def write_output_json(grouped_data: dict, session_dir: str):
    """
    Saves outputs into partitioned subfolders named after each FID (lowercase).
    Saves out as standard JSON.
    """
    for fid, contents in grouped_data.items():
        # Subfolder structure: output_dir/fid_lowercase/
        fid_lower = fid.lower()
        target_dir = os.path.join(session_dir, fid_lower)
        os.makedirs(target_dir, exist_ok=True)
        
        # Suffix matching configuration rules (.TBL or .COL)
        file_suffix = "TBL" if contents["type"] == "TABLE" else "COL"
        file_name = f"{fid.upper()}.{file_suffix}"
        
        full_output_path = os.path.join(target_dir, file_name)
        
        with open(full_output_path, 'w', encoding='utf-8') as f:
            json.dump(contents["records"], f, indent=4, ensure_ascii=False)

def write_mixed_output_json(tables: dict, columns: dict, session_dir: str):
    """
    Saves mixed sheet outputs:
    - Tables: one ZUTBLCUSTTYP.TBL file per table
    - Columns: multiple ZUTBLCUSTTYP-CUSTTYP.COL files (one per column record)
    """
    for fid in set(list(tables.keys()) + list(columns.keys())):
        fid_lower = fid.lower()
        target_dir = os.path.join(session_dir, fid_lower)
        os.makedirs(target_dir, exist_ok=True)
        
        # Write Table file
        if fid in tables:
            tbl_path = os.path.join(target_dir, f"{fid.upper()}.TBL")
            with open(tbl_path, 'w', encoding='utf-8') as f:
                json.dump(tables[fid], f, indent=4, ensure_ascii=False)
                
        # Write Column files
        if fid in columns:
            for col in columns[fid]:
                di_val = col.get('ACCKEYS')
                if di_val:
                    col_path = os.path.join(target_dir, f"{fid.upper()}-{str(di_val).upper()}.COL")
                    with open(col_path, 'w', encoding='utf-8') as f:
                        json.dump(col, f, indent=4, ensure_ascii=False)

def write_serial_output(sections_to_write: list, session_dir: str):
    """
    Saves serial rows:
    - sections_to_write: list of dicts: [{"name": section_name, "rows": [row_dict, ...]}]
    - session_dir: data/output/data/
    """
    for section in sections_to_write:
        section_name = section["name"]
        rows = section["rows"]
        if not rows:
            continue
            
        # Table name is section name without "Record" prefix, stripped
        table_name = section_name.replace("Record", "").strip()
        table_lower = table_name.lower()
        target_dir = os.path.join(session_dir, table_lower)
        os.makedirs(target_dir, exist_ok=True)
        
        file_name = f"{table_name.upper()}.serial"
        full_path = os.path.join(target_dir, file_name)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            for row in rows:
                row_str = json.dumps(row, ensure_ascii=False)
                f.write(f"{section_name} {row_str}\n")