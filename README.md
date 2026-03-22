# deepcsv

A Python library that automatically walks through folders and subfolders, finds all CSV and XLSX files, converts list strings into real Python lists, and saves the results in a new folder while keeping the exact same folder structure.

## Installation
```bash
pip install deepcsv
```

## Functions

### `ReadAllCSVData(path)`
Walks through all folders and subfolders, finds every CSV and XLSX file, converts list strings to real lists, and saves everything in a new folder called `All CSV Data is Converted Here` with the same structure.
```python
import deepcsv

deepcsv.ReadAllCSVData("C:/Users/Data")
```

### `ConvertListStrToList(df)`
Takes a single DataFrame and converts any column that contains list strings into real Python lists. Skips `NaN` values automatically.
```python
import deepcsv
import pandas as pd

df = pd.read_csv("file.csv")
df_converted = deepcsv.ConvertListStrToList(df)
```

## Notes

- Supports `.csv` and `.xlsx` files
- Skips `NaN` values without breaking
- Keeps the exact folder structure in the output folder
- Works on any level of nested folders

## Requirements

- Python >= 3.7
- pandas