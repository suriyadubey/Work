# src/main.py
import os
import sys
import pandas as pd
import shutil
from src.extract.excel_reader import load_data_file, parse_mixed_excel
from src.extract.factory import get_processor_by_headers
from src.load.json_writer import write_output_json, write_mixed_output_json

# Avoid console UnicodeEncodeError on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')


def execute_pipeline(target_file_path: str):
    if not os.path.exists(target_file_path):
        print(f"❌ File path error: {target_file_path} cannot be found.")
        return

    # Define fixed output directory
    output_base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/output/dataquik/table"))
    
    print(f"🚀 Initializing Pipeline Run -> Target Output: {output_base_dir}")
    
    # Replace existing files by clearing output directory on each run
    if os.path.exists(output_base_dir):
        try:
            shutil.rmtree(output_base_dir)
        except Exception as e:
            print(f"⚠️  Warning: Could not clear output directory: {e}")
    os.makedirs(output_base_dir, exist_ok=True)
    
    try:
        is_mixed_excel = False
        if target_file_path.lower().endswith(('.xlsx', '.xls')):
            try:
                xl = pd.ExcelFile(target_file_path)
                if 'TBL and COL' in xl.sheet_names:
                    is_mixed_excel = True
            except Exception:
                pass

        if is_mixed_excel:
            tables, columns = parse_mixed_excel(target_file_path)
            write_mixed_output_json(tables, columns, output_base_dir)
            print(f"✨ Job Completed. Manifest data saved to:\n📦 {output_base_dir}")
        else:
            # 1. Extract
            raw_df = load_data_file(target_file_path)
            
            # 2. Match through Factory
            parse_routine = get_processor_by_headers(raw_df)
            
            # 3. Transform & Validate
            processed_groups = parse_routine(raw_df)
            
            # 4. Load / Save
            write_output_json(processed_groups, output_base_dir)
            print(f"✨ Job Completed. Manifest data saved to:\n📦 {output_base_dir}")
        
    except Exception as error:
        print(f"💥 Critical Failure during pipeline conversion: {error}")

if __name__ == "__main__":
    # Allows compatibility with command line arguments or manual runs
    if len(sys.argv) > 1:
        execute_pipeline(sys.argv[1])
    else:
        # Automatically search data/input directory for .xlsx and .csv files
        input_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/input"))
        
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
                execute_pipeline(file_path)