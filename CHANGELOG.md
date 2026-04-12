# Changelog

---

### Added

- Added Parameter `col_name` in `process_file()` & `auto_fix()` To Support for Specific Column In Dataset
- Support for Dictionary Strings, now it will convert it into a real dictionary 
- `deep_check` parameter in `process_file()` — when enabled, recursively parses nested lists and dicts stored as strings inside arrays. Disabled by default due to performance cost on large datasets.

### Fixes

- Fixed Showing Logs While processing


---