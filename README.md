# deepcsv

Ever loaded a CSV file and found your carefully structured lists turned into useless strings?
```python
"['Action', 'Sci-Fi', 'Thriller']"  # This is a string, not a list
```

deepcsv fixes this automatically.

---

## The Solution

`deepcsv` handles these cases automatically:
- Reads CSV/XLSX files or existing DataFrames
- Converts any string list value `"["` into real NumPy arrays (fast and lightweight)
- Detects and fixes mixed-type columns by safely converting them to numeric
- Recursively processes all CSV/XLSX files in each directory
- Saves results as Parquet format to preserve types and speed up analysis

---

## Installation
```bash
pip install deepcsv
```

## Usage

### Single file processing (process_file)
```python
import deepcsv

df = deepcsv.process_file('path/to/file.csv')
```
- Accepts `str` (file path) or `pd.DataFrame`
- Returns `pd.DataFrame` with columns converted to arrays

### Batch directory processing (process_all_files)
```python
import deepcsv

deepcsv.process_all_files('path/to/folder')
```
- Processes all `.csv` and `.xlsx` files recursively
- Saves converted files as Parquet in: `All CSV Files is Converted Here`

---

## Utilities

### read_any(file_path)

Reads any supported file and returns a pandas DataFrame. No need to manually pick the reader.

```python
from deepcsv import read_any

df = read_any('data/users.csv')
df = read_any('reports/sales.xlsx')
df = read_any('warehouse/orders.parquet')
```

**Supported formats:** `.csv`, `.txt`, `.tsv`, `.xls`, `.xlsx`, `.json`, `.parquet`, `.pkl`, `.feather`, `.db`, `.sqlite`

---

### clean_values(data_input, ...)

Cleans a DataFrame by removing nulls from specific columns or rows, or dropping rows by index.

```python
from deepcsv import clean_values

# Drop fully-null columns from specific cols
df = clean_values('data.csv', cols=['age', 'salary'])

# Drop rows that have nulls in specific cols
df = clean_values('data.csv', cols=['age', 'salary'], ax_0=True)

# Drop rows by index
df = clean_values(df, index=[0, 5, 12])

# Apply on all columns except some
df = clean_values('data.csv', all_cols_except=['id', 'name'])
```

**Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `data_input` | `str \| DataFrame` | required | File path or DataFrame |
| `cols` | `list` | `None` | Columns to apply on |
| `ax_0` | `bool` | `False` | If `True`: drop rows with nulls. If `False`: drop fully-null cols |
| `index` | `list` | `None` | Row indexes to drop |
| `all_cols_except` | `list` | `None` | Apply on all columns except these |

---

## What it does

- Auto-detects files in directory and subdirectories
- Converts values like:
  - `"['item1', 'item2']"` → `array(['item1', 'item2'])` (NumPy array)
  - Mixed numeric/string columns → single numeric type (float)
- Handles NaN values without breaking
- Stores results in Parquet format for type safety and performance

---

## Function Signatures

- `process_file(data_input: Union[str, pd.DataFrame]) -> pd.DataFrame`
- `process_all_files(directory_path: str) -> None`
- `read_any(file_path: str) -> pd.DataFrame`
- `clean_values(data_input, cols=None, ax_0=False, index=None, all_cols_except=None) -> pd.DataFrame`

Output arrays are NumPy arrays for optimal performance in machine learning workflows.

---

## Key Features

- Fast NumPy array conversion instead of slow Python lists
- Mixed-type detection with automatic fixes
- Parquet storage for data integrity
- Recursive directory traversal
- Warning messages for transparency
- Built-in file reader supporting 10+ formats (`read_any`)
- Flexible null/index cleaning (`clean_values`)

---

## Notes

- Requires `pyarrow` for Parquet support
- Only saves files that contain converted array columns

---

## Requirements

- Python >= 3.7
- pandas
- pyarrow