# Excel/CSV Database Schema Processor

A robust Python-based schema extractor, validator, and pipeline utility. It parses spreadsheet layouts (mixed Table and Column schemas), validates them against strict database definition constraints, and generates structured JSON definitions formatted as `.TBL` (Table schemas) and `.COL` (Column schemas) files.

---

## 📂 Project Directory Structure

```text
converter/
│
├── data/
│   ├── input/                  # Place raw .xlsx or .csv input files here (e.g., input.xlsx)
│   └── output/                 # Timestamped run session folders containing output files
│
├── src/
│   ├── __init__.py
│   ├── main.py                 # Core runner (scans data/input/ or executes a specific file)
│   │
│   ├── extract/
│   │   ├── __init__.py
│   │   └── excel_reader.py     # File loader & mixed sheet (Table/Column) parsing logic
│   │
│   ├── transform/
│   │   ├── __init__.py
│   │   ├── table_parser.py     # Row parser fallback logic (Table)
│   │   ├── column_parser.py    # Row parser fallback logic (Column)
│   │   └── validators.py       # Strict metadata validators (FSN length, ALIAS format, etc.)
│   │
│   └── load/
│       ├── __init__.py
│       └── json_writer.py      # Outputs formatted .TBL and .COL JSON files
│
├── .gitignore                  # Keeps outputs and caches out of source control
├── requirements.txt            # Project dependencies (pandas, openpyxl)
└── README.md                   # Project documentation
```

---

## ✨ Features

- **Mixed-Layout Sheet Processor**: Dynamically parses the `TBL and COL` sheet of Excel workbooks (`data/input/input.xlsx`), extracting both Table and Column structures from mixed-format rows.
- **Automated Scanning**: Automatically scans the `data/input/` directory for `.xlsx` and `.csv` files when run without parameters (ignoring Excel lock files like `~$input.xlsx`).
- **Flexible Entrypoint**: Supports target file routing via command-line arguments.
- **Structured File Partitioning**:
  - Generates a single `<FID>.TBL` file for table definitions.
  - Generates individual `<FID>-<DI>.COL` files for every column record.
- **Validation Engine**: Sanitizes data types and ensures metadata constraints are met before output generation.
- **Windows Console Emoji Compatibility**: Automatically reconfigures console streams to UTF-8 on Windows systems, preventing crashes when printing status emojis.

---

## 🛠️ Installation

1. Clone the repository to your local system:
   ```bash
   git clone https://github.com/suriyadubey/Work.git
   cd Work
   ```

2. Install dependencies:
   ```bash
   py -m pip install -r requirements.txt
   ```

---

## 🚀 Usage

### 1. Automatic Directory Execution (Recommended)
Place your `.xlsx` or `.csv` spreadsheets in the `data/input/` directory and run:
```bash
py -m src.main
```
This scans all valid files in the directory and automatically processes them.

### 2. Manual Target Execution
To run the converter on a specific file, pass it as a command line argument:
```bash
py -m src.main data/input/input.xlsx
```

---

## ⚙️ Metadata Validations & Rules

The processor validates definitions against the following strict constraints:
- **Table.FSN**: Must not exceed 12 characters.
- **Column.ALIAS**: Can contain alphanumeric characters only (no spaces or special symbols).
- **Column.DES**: Must not exceed 40 characters.
- **Column.TBL**: Reference table names must be enclosed in brackets `[]` (e.g. `[STBLPERS]`).

---

## 📦 Output Format Examples

Generated files are structured into subfolders named after each lowercased `FID` (e.g., `zutblcusttyp/`) inside a timestamped session folder in `data/output/`.

### Table schema file sample (`ZUTBLCUSTTYP.TBL`)
```json
{
    "FID": "ZUTBLCUSTTYP",
    "ACCKEYS": "\"ZCUSTTYP\",CUSTTYP",
    "DEL": 124,
    "DES": "Customer Type User Table",
    "FILETYP": 1,
    "GLOBAL": "UTBL",
    "RECTYP": 1,
    "FSN": "fZUTBLCUSTTY",
    "LOG": true,
    "SYSSN": "PBS"
}
```

### Column schema file sample (`ZUTBLCUSTTYP-CUSTTYP.COL`)
```json
{
    "FID": "ZUTBLCUSTTYP",
    "ACCKEYS": "CUSTTYP",
    "TYP": "T",
    "LEN": 2,
    "NOD": "1*",
    "DES": "Customer Type",
    "RHD": "Customer Type",
    "ALIAS": "CustomerType",
    "REQ": true
}
```
