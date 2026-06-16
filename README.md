# Excel/CSV Database Schema Processor

A robust Python-based schema extractor, validator, and pipeline utility. It parses spreadsheet layouts (mixed Table and Column schemas), validates them against strict database definition constraints, and generates structured JSON definitions formatted as `.TBL` (Table schemas) and `.COL` (Column schemas) files.

---

## 📂 Project Directory Structure

```text
converter/
│
├── data/
│   ├── input/                  # Place raw .xlsx or .csv input files here (e.g., input.xlsx)
│   ├── .process_state.json     # Tracks processed row hashes for incremental execution
│   └── output/
│       ├── data/               # Output directory where generated .serial files are placed
│       └── dataquik/
│           └── table/          # Output directory where generated TBL/COL files are placed
│
├── src/
│   ├── __init__.py
│   ├── main.py                 # Core runner (handles arguments, state, and fallback runs)
│   │
│   ├── extract/
│   │   ├── __init__.py
│   │   ├── excel_reader.py     # File loader & TBL/COL parsing logic
│   │   ├── serial_reader.py    # Parsers for serial-full sheets
│   │   └── factory.py          # Header block factory routing
│   │
│   ├── transform/
│   │   ├── __init__.py
│   │   ├── table_parser.py     # Row parser fallback logic (Table)
│   │   ├── column_parser.py    # Row parser fallback logic (Column)
│   │   ├── state_manager.py    # Logic for loading/saving incremental process hashes
│   │   └── validators.py       # Strict metadata validators (FSN length, ALIAS format, etc.)
│   │
│   └── load/
│       ├── __init__.py
│       └── json_writer.py      # Outputs TBL/COL files and writes/appends .serial files
│
├── .gitignore                  # Keeps outputs and caches out of source control
├── requirements.txt            # Project dependencies (pandas, openpyxl)
└── README.md                   # Project documentation
```

---

## ✨ Features

- **Mixed-Layout Sheet Processor**: Dynamically parses the `TBL and COL` sheet of Excel workbooks (`data/input/input.xlsx`), extracting both Table and Column structures from mixed-format rows.
- **Serial Schema Parser**: Dynamically extracts tables from the `serial-full` sheet and serializes them as `.serial` files in format `<SectionName> <JSON_of_row>`.
- **Incremental Runner**: Executes only newly added rows across both sheets by tracking processed row hashes in `data/.process_state.json`.
- **Automated Scanning**: Automatically scans the `data/input/` directory for `.xlsx` and `.csv` files when run without parameters (ignoring Excel lock files like `~$input.xlsx`).
- **Flexible Entrypoint**: Supports target file routing via command-line arguments.
- **Structured File Partitioning**:
  - Generates a single `<FID>.TBL` file for table definitions.
  - Generates individual `<FID>-<DI>.COL` files for every column record.
  - Generates single `<FID>.serial` files with compact JSON rows.
- **Validation Engine**: Sanitizes data types and ensures metadata constraints are met before output generation.
- **Windows Console Emoji Compatibility**: Automatically reconfigures console streams to UTF-8 on Windows systems, preventing crashes when printing status emojis.

## 🔍 System & Architectural Overview

The application is split into four distinct pipeline stages to maintain a modular and robust structure:

1. **Pipeline Runner (`src/main.py`)**:
   - Manages the execution flow, supports target files passed via command line arguments, and automatically scans the `data/input/` directory for files when run without parameters (filtering out temporary lock files like `~$*`).
   - Standardizes system output and error console encoding to UTF-8 on Windows environments, preventing formatting exceptions when writing status emojis.

2. **Excel Extractor & Parser (`src/extract/excel_reader.py`)**:
   - Reads the spreadsheet data and targets the `TBL and COL` sheet.
   - Iterates through the rows, dynamically parses column mappings based on active section header markers (`Table` vs. `Column`), cleans text types, normalizes float values into integers, preserves booleans, and trims wrapping double-quotes from cells (e.g., `'"1*"'` becomes `"1*"`).

3. **Data Constraint Validators (`src/transform/validators.py`)**:
   - Asserts constraints specified in the requirements notes (verifying FSN string limits, alphanumeric conditions for ALIAS references, column descriptions, and bracket formats).
   - Generates formatted console warnings when violations are detected.

4. **Structured JSON Loaders (`src/load/json_writer.py`)**:
   - Organizes output payloads into lowercased `FID` subfolders inside the fixed `data/output/dataquik/table/` folder.
   - Automatically splits definitions: writes a single `<FID>.TBL` file for database tables, and separate `<FID>-<DI>.COL` files for each individual column definition.

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

### 1. Full Run (Default)
Processes all sheets from scratch, clearing output directories and generating everything:
```bash
py -m src.main
# or run a specific file
py -m src.main data/input/input.xlsx
```

### 2. Incremental Run
Detects and processes only newly added rows, appending new records to `.serial` files and creating/overwriting specific `.TBL` and `.COL` files:
```bash
py -m src.main -i
# or run a specific file incrementally
py -m src.main data/input/input.xlsx -i
```

### 3. Force Full Run
Forces a full execution from scratch, resetting the processed row states:
```bash
py -m src.main -f
# or force a run on a specific file
py -m src.main data/input/input.xlsx -f
```

---

## ⚙️ Metadata Validations & Rules

The processor validates definitions and enforces types against the following strict constraints:
- **Table.FSN**: Must not exceed 12 characters.
- **Column.ALIAS**: Can contain alphanumeric characters only (no spaces or special symbols).
- **Column.DES**: Must not exceed 40 characters.
- **Column.TBL**: Reference table names must be enclosed in brackets `[]` (e.g. `[STBLPERS]`).
- **Serial.Value Integrity**: Cell value formatting (such as leading zeros like `"00000"` or `"010"`) is strictly preserved as strings. Cells containing explicit `(null)` values or empty fields are treated as null and their keys are omitted from the row JSON.

---

## 📦 Output Format Examples

Generated files are structured into subfolders named after each lowercased `FID` (e.g., `zutblcusttyp/`) inside the `data/output/dataquik/table/` directory, which is refreshed and overwritten on every run.

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

### Serial data file sample (`ZUTBLRISKLEVEL.serial`)
Generated `.serial` files reside in `data/output/data/{table_name}/` and write each record on a single line starting with the section name followed by its JSON data:
```text
RecordZUTBLRISKLEVEL {"RISKLEVEL": 1, "DESC": "Low Risk Level"}
RecordZUTBLRISKLEVEL {"RISKLEVEL": 2, "DESC": "Medium Risk Level"}
RecordZUTBLRISKLEVEL {"RISKLEVEL": 3, "DESC": "Hight Risk Level"}
```
