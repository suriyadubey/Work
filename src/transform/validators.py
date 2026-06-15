# src/transform/validators.py
import re

def verify_constraints(row_data: dict, schema_type: str):
    """
    Enforces business rules on input data streams.
    Modify values here if structural metrics shift.
    """
    if schema_type == "TABLE":
        fsn_val = str(row_data.get("FSN", ""))
        # Table.FSN: Must be <= 12 characters
        if fsn_val and len(fsn_val) > 12:
            print(f"⚠️  [Warning] FSN constraint violation on FID {row_data.get('FID')}: '{fsn_val}' exceeds 12 chars.")

    elif schema_type == "COLUMN":
        des_val = str(row_data.get("DES", ""))
        alias_val = str(row_data.get("ALIAS", ""))
        tbl_val = str(row_data.get("TBL", ""))
        col_id = row_data.get("DI", row_data.get("ACCKEYS", ""))

        # Column.DES: Must be <= 40 characters
        if des_val and len(des_val) > 40:
            print(f"⚠️  [Warning] DES constraint violation on DI {col_id}: Length exceeds 40 chars.")

        # Column.ALIAS: Must be Alphanumeric (Letters and Numbers only)
        if alias_val and not alias_val.isalnum():
            print(f"⚠️  [Warning] ALIAS constraint violation on DI {col_id}: '{alias_val}' contains non-alphanumeric symbols.")

        # Column.TBL: Table names must be enclosed in brackets []
        if tbl_val and not (tbl_val.startswith('[') and tbl_val.endswith(']')):
            print(f"⚠️  [Warning] TBL constraint violation on DI {col_id}: '{tbl_val}' must be enclosed in brackets [].")
