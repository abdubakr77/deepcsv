# Changelog

---

### Added

- `process_all_files` — Added option for user to customize the output folder name in 
- `read_any()` — Reads any supported file format and returns a pandas DataFrame automatically. Supports: `.csv`, `.txt`, `.tsv`, `.xls`, `.xlsx`, `.json`, `.parquet`, `.pkl`, `.feather`, `.db`, `.sqlite`
- `clean_values()` — Cleans a DataFrame by removing nulls, specific values, specific types, or rows by index. Supports optional condition filtering with 6 operators
- `_validate_cols()` — Internal helper: validates cols is a non-empty list and all columns exist in the DataFrame
- `_validate_index()` — Internal helper: validates index is a non-empty list and all indexes exist in the DataFrame. Supports optional `reset_index` before validation
- `_validate_condition()` — Internal helper: validates condition list and returns `(operator_func, value)`
- `_parse_operator()` — Internal helper: converts operator string like `'>='` into its Python operator function
- finding_value parameter in `clean_values(data_input,finding_value)` find and remove rows that have this specific value
- finding_type parameter in `clean_values(data_input,finding_type)` find and remove rows that have this specific type (ex: str, int)
- condition parameter in `clean_values(data_input,condition : [operator, value] → ex: ['>=', 500])` applied only with finding_value or finding_type

---

### Changed

- `process_file()` — Added `save_file_extension` parameter. Now supports saving the processed DataFrame in any format after conversion, not just returning it
- `process_all_files()` — Added `file_extension` parameter. Now supports saving converted files in any format instead of always saving as Parquet. Also expanded supported input formats beyond `.csv` and `.xlsx` to cover all formats supported by `read_any()`
- `DeepCleaner()` - Changing whole code flow to OOPS

---