# Changelog

---

## 0.8.0

#### Added

- Added `auto_outliers()` in `deepcsv.ml` — detects and removes outlier rows with `iqr`, `zscore` or `isolation_forest` (#37)
- Added `data_details()` — deep report about your data (size, memory, missing values, duplicates, types, numeric stats, outliers) with a hint for the deepcsv function that fixes each problem (#27)
- `data_details()` can export the report as CSV (columns table) or TXT (full report) with `export=` (#30)
- Added `merge_data()` — merges two datasets of any supported format by a specific column (#4)
- Added `pip install deepcsv[ml]` extra for scikit-learn and tqdm
- Added unit tests in `tests/`

#### Fixed

- `process_file()` and `auto_fix()` crashed on any DataFrame with more than one column (`col_name` check compared a string to the whole column index), and a list `col_name` never worked
- `process_all_files()` crashed with `TypeError` on every run, saved files as `name.parquet.parquet`, and processed its own output folder on a second run
- `auto_fix()` turned mixed int/text columns into booleans
- `process_file()` and `auto_fix()` changed the DataFrame you passed in — they now work on a copy
- The Deep Check warning was printed once for every parsed value, now it prints once
- `deep_check=True` crashed with `UnicodeEncodeError` on Windows consoles that cannot print emoji
- `import deepcsv` failed when scikit-learn or tqdm were not installed

#### Changed

- Removed the duplicated `deepcsv/utils.py` (it was an exact copy of `deepcsv/utils/utils.py` and was never imported)
- Package discovery is limited to `deepcsv*` so `tests/` is not shipped

#### Notes

- The public API did not change — every existing call works as before
- Charts (#28, #30) are planned for the next release

---

## 0.7.1

#### Added
 
- Added `accurate` mode to `auto_fs()` using auto-tuned GradientBoosting
- Added `get_gb_params()` — auto-tunes GradientBoosting params based on row count and feature count

---

#### Notes
 
- `accurate` mode is slower but captures non-linear relationships — use it when `balanced` is not enough
- GradientBoosting params scale automatically with dataset size and feature count to avoid overfitting