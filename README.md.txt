excel-processor/
│
├── data/
│   ├── input/                     # Place your raw .xlsx or .csv files here
│   └── output/                    # Where timestamped session folders will be generated
│
├── src/
│   ├── __init__.py
│   ├── main.py                    # Unified script executor (replaces batch loops)
│   │
│   ├── extract/
│   │   ├── __init__.py
│   │   ├── excel_reader.py        # File loader & CSV string cleanups
│   │   └── factory.py             # Determines if data block is a TBL or COL format
│   │
│   ├── transform/
│   │   ├── __init__.py
│   │   ├── table_parser.py        # Table formatting logic & schema mapping
│   │   ├── column_parser.py       # Column formatting logic & schema mapping
│   │   └── validators.py          # Strict data constraints (FSN length, ALIAS alnum, etc.)
│   │
│   └── load/
│       ├── __init__.py
│       └── json_writer.py         # Writes files to their respective lowercase FID subfolders
│
├── requirements.txt               # Dependencies (pandas, openpyxl)