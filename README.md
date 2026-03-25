# deepcsv (v0.5.0)

Ever loaded a CSV file and found your carefully structured lists turned into useless strings?
````python
"['Action', 'Sci-Fi', 'Thriller']"  # This is a string, not a list
````

deepcsv fixes this automatically.

---

## The Solution

`deepcsv` handles these cases automatically:
- Reads CSV/XLSX files or existing DataFrames
- Converts any string value starting with `[` into real NumPy arrays (fast and lightweight)
- Detects and fixes mixed-type columns by safely converting them to numeric (float)
- Recursively processes all CSV/XLSX files in subdirectories
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

Output arrays are NumPy arrays for optimal performance in machine learning workflows.

---

## Key Features

- Fast NumPy array conversion instead of slow Python lists
- Mixed-type detection with automatic fixes
- Parquet storage for data integrity
- Recursive directory traversal
- Warning messages for transparency

---

## Notes

- Requires `pyarrow` for Parquet support
- Only saves files that contain converted array columns

---

## Requirements

- Python >= 3.7
- pandas
- pyarrow

