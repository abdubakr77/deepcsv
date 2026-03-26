# Changelog

---

## [0.6.0]

### Added
- `read_any()` — Auto-detects file format from extension and returns a pandas DataFrame. Supports: `.csv`, `.txt`, `.tsv`, `.xls`, `.xlsx`, `.json`, `.parquet`, `.pkl`, `.feather`, `.db`, `.sqlite`
- `clean_values()` — Cleans a DataFrame by removing nulls from specific columns or rows, dropping rows by index, or applying on all columns except selected ones
- `_validate_cols()` — Internal helper that validates cols is a non-empty list and all columns exist in the DataFrame
- `_validate_index()` — Internal helper that validates index is a non-empty list and all indexes exist in the DataFrame. Supports optional `reset_index` before validation

---