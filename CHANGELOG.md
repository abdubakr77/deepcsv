# Changelog

---

#### Added
 
- Added `ml/` subpackage for machine learning utilities  
- Added `auto_fs()` (Auto Feature Selection) in `deepcsv.ml`
  - Supports multiple modes:
    - `fast` → correlation-based selection
    - `balanced` → model-based selection using cross-validation (greedy approach)

---

#### Notes
 
- `auto_fs()` automatically handles feature selection for supervised tasks  
- Designed to provide simple, high-level API for feature selection without manual setup