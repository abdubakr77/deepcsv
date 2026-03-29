# deepcsv

> *"You think you saved a list. You open it tomorrow — and it's a string."*

`deepcsv` was built to solve exactly this problem.

---

## The Problem

CSV files can be deceptive.

* You save a list — you open it later and it's just a string.
* A column looks numeric — but secretly contains mixed data types.
* You have hundreds of files across folders — and process them one by one.
* You waste time deciding which reader to use for each format.
* Null values are scattered everywhere with no clean way to handle them.

This is a silent bottleneck in many data pipelines.

---

## The Solution

`deepcsv` handles all of this in a single import.

* Automatically walks through folders and subfolders
* Detects and processes CSV, XLSX, and multiple other formats
* Converts stringified lists into real NumPy arrays
* Detects and fixes mixed-type columns
* Saves data in multiple formats (not limited to Parquet)
* Provides a universal file reader
* Cleans nulls with full control over rows, columns, values, and types

---

## Why not just pandas?

While pandas is powerful, it does not:

* Automatically detect and convert list-like strings
* Process entire directory structures recursively
* Provide a unified interface for multiple file formats

`deepcsv` simplifies these workflows into a single, consistent API.

---

## Installation

```bash
pip install deepcsv
```

---

## Initialization

```python
from deepcsv import DeepCleaner

cleaner = DeepCleaner(parameters)
```

---

## Parameters

### For `process_file()`

* `data_input`: Path to file or DataFrame
* `save_file_extension`: Output file format

### For `process_all_files()`

* `directory_path`: Folder containing files
* `output_dir`: Directory to save cleaned files
* `save_file_extension`: Output file format

---

## Functions

### `process_file(data_input, save_file_extension=None)`

Reads a file or DataFrame, converts array-like strings to NumPy arrays, fixes mixed-type columns, and optionally saves the result.

```python
from deepcsv import DeepCleaner

cleaner = DeepCleaner(data_input="path_to_file", save_file_extension="csv")

df = cleaner.process_file()
```

**Supported save formats:**
`.csv` `.tsv` `.txt` `.xlsx` `.json` `.parquet` `.pkl` `.feather` `.html` `.xml`

---

### `process_all_files(directory_path, output_dir="cleaned_files", file_extension="parquet")`

Recursively processes all supported files in a directory and saves cleaned outputs.

```python
from deepcsv import DeepCleaner

cleaner = DeepCleaner(directory_path="folder_path", output_dir="cleaned_files")

cleaner.process_all_files()
```

**Supported input formats:**
`.csv` `.txt` `.tsv` `.xls` `.xlsx` `.json` `.parquet` `.pkl` `.feather` `.db` `.sqlite`

---

### `read_any(file_path)`

Universal file reader that returns a pandas DataFrame.

```python
from deepcsv import read_any

df = read_any("data/users.csv")
df = read_any("reports/sales.xlsx")
df = read_any("warehouse/orders.parquet")
df = read_any("local.db")
```

---

### `clean_values(data_input, ...)`

Cleans a DataFrame by removing nulls, specific values, types, or rows.

```python
from deepcsv import clean_values

# Drop fully-null columns
df = clean_values("data.csv", cols=["age", "salary"])

# Drop rows with nulls in specific columns
df = clean_values("data.csv", cols=["age", "salary"], ax_0=True)

# Drop rows by index
df = clean_values(df, index=[0, 5, 12])

# Remove rows with a specific value
df = clean_values(df, cols=["status"], finding_value="N/A")

# Conditional filtering
df = clean_values(df, cols=["score"], condition=[">=", 500])

# Remove rows by type
df = clean_values(df, cols=["age"], finding_type=str)

# Apply to all columns except some
df = clean_values("data.csv", all_cols_except=["id", "name"])
```

---

## Parameters Reference

| Parameter       | Type            | Default  | Description                |
| --------------- | --------------- | -------- | -------------------------- |
| data_input      | str | DataFrame | required | File path or DataFrame     |
| cols            | list            | None     | Target columns             |
| ax_0            | bool            | False    | True: drop rows with nulls |
| index           | list            | None     | Row indexes to drop        |
| condition       | list            | None     | [operator, value]          |
| all_cols_except | list            | None     | Excluded columns           |
| finding_value   | any             | None     | Value to remove            |
| finding_type    | type            | None     | Type to remove             |

**Supported operators:** `>=` `<=` `>` `<` `==` `!=`

---

## Before vs After

```python
# Before (pandas)
import pandas as pd
import ast

df = pd.read_csv("data.csv")
df["col"] = df["col"].apply(ast.literal_eval)

# After (deepcsv)
from deepcsv import read_any

df = read_any("data.csv")
```

---

## Key Features

* Automatic string-to-NumPy array conversion
* Mixed-type column detection and correction
* Multi-format saving support
* Universal file reader
* Advanced null cleaning utilities
* Conditional filtering support
* Recursive directory traversal
* Transparent warnings

---

## Notes

* Requires `pyarrow` for Parquet and Feather support
* Files are saved in `process_all_files` only when transformations are applied

---

## Requirements

* Python >= 3.7
* pandas
* pyarrow

---

## Authors

**Abdullah Bakr**
**Contributor: Rustam Singh**
