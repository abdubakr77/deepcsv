# deepcsv
> *"You think you saved a list. You open it tomorrow — and it's a string."*

`deepcsv` was built to solve exactly this problem.

---

## The Problem

Your CSV files are lying to you.

You save a list — you open it tomorrow and it's a string.
Your column has numbers — it secretly has 3 different data types.
You have 200 CSV files across 40 folders — and you process them one by one.
You load a file and spend 20 minutes just picking the right reader.
You have nulls scattered everywhere with no clean way to handle them.

This is the silent killer of every data pipeline.

---

## The Solution

`deepcsv` handles all of this in one import.

- Walks through every folder and subfolder automatically
- Finds every CSV and XLSX file
- Detects columns storing lists as strings and converts them to real NumPy arrays
- Catches mixed-type columns and fixes them automatically
- Saves everything in any format you choose — not just Parquet
- Reads any file format with one function — no more picking the right reader
- Cleans nulls with full control over columns, rows, indexes, values, and types

---

## Installation

```bash
pip install deepcsv
```

---

## Functions

### `process_file(data_input, save_file_extension= str)`

Reads a file or DataFrame, converts array-like strings to NumPy arrays, fixes mixed-type columns, and optionally saves the result in any format you choose.

```python
import deepcsv

# Process only
df = deepcsv.process_file('path/to/file.csv')

# Process and save as parquet
df = deepcsv.process_file('path/to/file.csv', save_file_extension='parquet')

# Process and save as Excel
df = deepcsv.process_file('path/to/file.csv', save_file_extension='xlsx')
```

**Supported save formats:** `.csv` `.tsv` `.txt` `.xlsx` `.json` `.parquet` `.pkl` `.feather` `.html` `.xml`

---

### `process_all_files(directory_path, output_dir="All CSV Files is Converted Here", file_extension="parquet")`

Walks through all folders and subfolders, applies `process_file` on every supported file, and saves results in the format you choose.

```python
import deepcsv

# Default — saves as parquet
deepcsv.process_all_files('path/to/folder')

# Custom output folder
deepcsv.process_all_files('path/to/folder', output_dir='Converted Files')

# Save as CSV instead
deepcsv.process_all_files('path/to/folder', file_extension='csv')
```

**Supported input formats:** `.csv` `.txt` `.tsv` `.xls` `.xlsx` `.json` `.parquet` `.pkl` `.feather` `.db` `.sqlite`

---

### `read_any(file_path)` ✨

Reads any supported file format and returns a pandas DataFrame — one function for everything.

```python
from deepcsv import read_any

df = read_any('data/users.csv')
df = read_any('reports/sales.xlsx')
df = read_any('warehouse/orders.parquet')
df = read_any('local.db')
```

**Supported formats:** `.csv` `.txt` `.tsv` `.xls` `.xlsx` `.json` `.parquet` `.pkl` `.feather` `.db` `.sqlite`

---

### `clean_values(data_input, ...)` ✨

Cleans a DataFrame by removing nulls, specific values, specific types, or rows by index — with full control over which columns to target and optional conditions.

```python
from deepcsv import clean_values

# Drop fully-null columns
df = clean_values('data.csv', cols=['age', 'salary'])

# Drop rows that have nulls in specific cols
df = clean_values('data.csv', cols=['age', 'salary'], ax_0=True)

# Drop rows by index
df = clean_values(df, index=[0, 5, 12])

# Remove rows where a specific value exists
df = clean_values(df, cols=['status'], finding_value='N/A')

# Remove rows where value meets a condition
df = clean_values(df, cols=['score'], finding_value='N/A', condition=['>=', 500])

# Remove rows by Python type
df = clean_values(df, cols=['age'], finding_type=str)

# Apply on all columns except some
df = clean_values('data.csv', all_cols_except=['id', 'name'])
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `data_input` | `str \| DataFrame` | required | File path or DataFrame |
| `cols` | `list` | `None` | Columns to apply on |
| `ax_0` | `bool` | `False` | `True`: drop rows with nulls — `False`: drop fully-null cols |
| `index` | `list` | `None` | Row indexes to drop |
| `condition` | `list` | `None` | `[operator, value]` — ex: `['>=', 500]` |
| `all_cols_except` | `list` | `None` | Apply on all columns except these |
| `finding_value` | `any` | `None` | Find and remove rows containing this value |
| `finding_type` | `type` | `None` | Find and remove rows matching this Python type |

**Supported condition operators:** `>=` `<=` `>` `<` `==` `!=`

---

## Function Signatures

```python
process_file(data_input: Union[str, pd.DataFrame], save_file_extension: str = None) -> pd.DataFrame
process_all_files(directory_path: str, output_dir: str = "All CSV Files is Converted Here", file_extension: str = "parquet") -> None
read_any(file_path: str) -> pd.DataFrame
clean_values(data_input, cols=None, ax_0=False, index=None, condition=None, all_cols_except=None, finding_value=None, finding_type=None) -> pd.DataFrame
```

---

## Key Features

- String list → real NumPy array conversion (fast, no manual parsing)
- Mixed-type column detection and auto-fix
- Save in any format — CSV, Excel, JSON, Parquet, Feather, and more
- One universal file reader for 10+ formats
- Flexible null cleaning by column, row, index, value, or type
- Conditional filtering with 6 operators
- Recursive directory traversal
- Warning messages for full transparency

---

## Notes

- Requires `pyarrow` for Parquet and Feather support
- Only saves files in `process_all_files` if the DataFrame contains converted array columns

---

## Requirements

- Python >= 3.7
- pandas
- pyarrow

---

**By: Abdullah Bakr**