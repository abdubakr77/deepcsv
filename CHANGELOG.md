# Changelog

---

#### Changed
 
- `utils.py` is now a **subpackage** (`utils/`) instead of a flat file
  - All functions remain the same — no breaking changes
  - New import style now supported: `from deepcsv.utils import read_any`
  - Old style still works: `from deepcsv import read_any`


#### Added
 
- `utils` is now accessible as a submodule — `deepcsv.utils.read_any(...)` works directly after `import deepcsv`
- Added `ml/` subpackage for machine learning utilities *(coming soon)*
  - `deepcsv.ml.auto_fs()`
- Added Function called auto_fs (Auto Feature Selection) in `deepcsv.ml`


#### Notes
 
- All existing code continues to work without any changes
- New subpackages (`ml`) are isolated — importing `deepcsv` won't load their dependencies unless explicitly used

---