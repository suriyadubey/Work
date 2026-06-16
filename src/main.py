# src/main.py
import os
import sys
import pandas as pd
import shutil
from src.extract.excel_reader import load_data_file, parse_mixed_excel
from src.extract.serial_reader import parse_serial_sheet
from src.extract.factory import get_processor_by_headers
from src.load.json_writer import write_output_json, write_mixed_output_json, write_serial_output
from src.transform.state_manager import load_state, save_state

# Avoid console UnicodeEncodeError on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')


def execute_pipeline(target_file_path: str, incremental: bool = False, force: bool = False):
    if not os.path.exists(target_file_path):
        print(f"❌ File path error: {target_file_path} cannot be found.")
        return

    # Define fixed output directories
    tbl_col_output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/output/dataquik/table"))
    serial_output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/output/data"))
    
    print(f"🚀 Initializing Pipeline Run -> Target TBL/COL: {tbl_col_output_dir}, Target Serial: {serial_output_dir} (Incremental={incremental}, Force={force})")
    
    # If not running incrementally, or if force run is requested, clear output directories
    if not incremental or force:
        for out_dir in [tbl_col_output_dir, serial_output_dir]:
            if os.path.exists(out_dir):
                try:
                    shutil.rmtree(out_dir)
                except Exception as e:
                    print(f"⚠️  Warning: Could not clear output directory {out_dir}: {e}")
            os.makedirs(out_dir, exist_ok=True)
    else:
        os.makedirs(tbl_col_output_dir, exist_ok=True)
        os.makedirs(serial_output_dir, exist_ok=True)
    
    try:
        is_excel = False
        sheet_names = []
        if target_file_path.lower().endswith(('.xlsx', '.xls')):
            try:
                xl = pd.ExcelFile(target_file_path)
                sheet_names = xl.sheet_names
                is_excel = True
            except Exception:
                pass

        if is_excel and ('TBL and COL' in sheet_names or 'serial-full' in sheet_names):
            file_key = os.path.basename(target_file_path)
            state = load_state()
            file_state = state.get(file_key, {})
            
            # Extract already processed hashes if running incrementally
            if incremental and not force:
                tbl_col_hashes = set(file_state.get("tbl_col", []))
                serial_hashes_list = file_state.get("serial_full", {})
                serial_hashes = {sec: set(h_list) for sec, h_list in serial_hashes_list.items()}
            else:
                tbl_col_hashes = None
                serial_hashes = None
            
            # 1. Process TBL and COL sheet
            if 'TBL and COL' in sheet_names:
                print("📄 Processing 'TBL and COL' sheet...")
                tables, columns, processed_tbl_col_hashes = parse_mixed_excel(target_file_path, tbl_col_hashes)
                
                # Write outputs (if new tables/columns exist)
                if tables or columns:
                    write_mixed_output_json(tables, columns, tbl_col_output_dir)
                    print(f"✅ Wrote new TBL/COL files. Tables: {len(tables)}, Column Groups: {len(columns)}")
                else:
                    print("ℹ️  No new Table or Column rows to process.")
                
                file_state["tbl_col"] = processed_tbl_col_hashes
            
            # 2. Process serial-full sheet
            if 'serial-full' in sheet_names:
                print("📄 Processing 'serial-full' sheet...")
                sections_to_write, processed_serial_hashes = parse_serial_sheet(target_file_path, serial_hashes)
                
                # Write/append outputs
                if sections_to_write:
                    # If incremental, append new rows; otherwise overwrite
                    write_serial_output(sections_to_write, serial_output_dir, append=incremental)
                    print(f"✅ Processed and wrote serial outputs. Affected Sections: {len(sections_to_write)}")
                else:
                    print("ℹ️  No new serial rows to process.")
                
                file_state["serial_full"] = processed_serial_hashes
            
            # Save updated state
            state[file_key] = file_state
            save_state(state)
            print(f"✨ Job Completed. Manifest data saved to:\n📦 TBL/COL: {tbl_col_output_dir}\n📦 Serial: {serial_output_dir}")
            
        else:
            # Fallback for standard CSV or simple spreadsheets
            # 1. Extract
            raw_df = load_data_file(target_file_path)
            
            # 2. Match through Factory
            parse_routine = get_processor_by_headers(raw_df)
            
            # 3. Transform & Validate
            processed_groups = parse_routine(raw_df)
            
            # 4. Load / Save
            write_output_json(processed_groups, tbl_col_output_dir)
            print(f"✨ Job Completed. Manifest data saved to:\n📦 {tbl_col_output_dir}")
        
    except Exception as error:
        print(f"💥 Critical Failure during pipeline conversion: {error}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Excel/CSV Database Schema Processor")
    parser.add_argument("file_path", nargs="?", help="Path to specific Excel or CSV file to process")
    parser.add_argument("-i", "--incremental", action="store_true", help="Run incrementally, only processing newly added rows")
    parser.add_argument("-f", "--force", action="store_true", help="Force a full rerun, clearing previous state and outputs")
    
    args = parser.parse_args()
    
    input_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/input"))
    
    if args.file_path:
        execute_pipeline(args.file_path, incremental=args.incremental, force=args.force)
    else:
        if not os.path.exists(input_dir):
            print(f"❌ Input directory error: {input_dir} cannot be found.")
            sys.exit(1)
            
        valid_extensions = ('.csv', '.xlsx')
        input_files = [
            os.path.join(input_dir, f) for f in os.listdir(input_dir)
            if f.lower().endswith(valid_extensions) and not f.startswith('~$')
        ]
        
        if not input_files:
            print(f"❌ No .csv or .xlsx files found in: {input_dir}")
        else:
            print(f"🔍 Found {len(input_files)} input file(s) in {input_dir}")
            for file_path in input_files:
                print(f"\n📂 Processing input file: {os.path.basename(file_path)}")
                execute_pipeline(file_path, incremental=args.incremental, force=args.force)