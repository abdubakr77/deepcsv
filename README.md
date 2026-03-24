# deepcsv

Stop losing your data types when working with CSV files.  
deepcsv automatically cleans messy CSV/XLSX data and converts it into ML-ready Parquet format.

## Installation
```bash
pip install deepcsv
```

## Example

### Before
```python
# CSV column value
"['a', 'b', 'c']"
```

### After
```python
# Automatically converted
['a', 'b', 'c']
```

### Usage
```python
import deepcsv

df = deepcsv.ConvertListStrToList("path/to/file.csv")
```

---

## What it does

- Walks through all folders and subfolders automatically  
- Finds every CSV and XLSX file  
- Detects columns that contain list strings like `"['item1', 'item2']"` and converts them into real Python arrays for faster performance  
- Detects columns with mixed data types and tries to fix them automatically  
- Warns you when a column has mixed types so you know what was changed  
- Saves the results as Parquet files to preserve the converted data types  

---

## Why Parquet?

CSV files cannot store arrays or preserve data types.  
Parquet solves this by keeping the exact types after conversion and is much faster for data processing workflows.

---

## Why arrays instead of Python lists?

Arrays are significantly faster for numerical operations and machine learning workflows, especially when working with large datasets.

---

## Functions

### `ConvertListStrToList(file_path)`

Reads a CSV file, converts list strings to arrays, fixes mixed-type columns, and returns a clean DataFrame.

```python
import deepcsv

df = deepcsv.ConvertListStrToList("path/to/file.csv")
```

---

### `ReadAllCSVData(path)`

Walks through all folders and subfolders, applies `ConvertListStrToList` on every CSV and XLSX file, and saves the results as Parquet files in a new folder called `All CSV Data is Converted Here`.

```python
import deepcsv

deepcsv.ReadAllCSVData("path/to/folder")
```

---

## Notes

- Only files that contain list string columns are saved as Parquet  
- Mixed-type columns are converted to float automatically when possible  
- Skips NaN values without breaking  
- Requires `pyarrow` for Parquet support  

---

## Requirements

- Python >= 3.7  
- pandas  
- pyarrow  