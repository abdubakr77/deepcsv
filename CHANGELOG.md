# Changelog

All notable changes to deepcsv will be documented here.

---

## [0.5.0] - 2026-03-25

### Added
- Added comprehensive docstrings to all functions with type hints and descriptions.
- Added usage examples in docstrings to clarify how to call each function.
- Added `Union` type hint import for better type annotations.
- Added update notification feature to alert users when a new version is available.

### Changed
- Renamed function `ConvertListStrToList` to `process_file` for shorter, stronger naming.
- Renamed function `ReadAllCSVData` to `process_all_files` for conciseness and clarity.
- Renamed parameter `File_Path` to `data_input` in `process_file`.
- Renamed parameter `WorkDirectoryPath` to `directory_path` in `process_all_files`.
- Changed function return type from Python lists to **NumPy arrays** for better performance and lightweight processing.
- Updated README with improved documentation and added a dedicated changelog section.

### Fixed
- Removed duplicate code at the end of the file that was causing redundancy.
- Ensured no syntax errors after all modifications.

### Removed
- Removed extraneous code outside the function definitions.

---