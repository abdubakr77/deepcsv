# Changelog

---

#### Added
 
- Added `accurate` mode to `auto_fs()` using auto-tuned GradientBoosting
- Added `get_gb_params()` — auto-tunes GradientBoosting params based on row count and feature count

---

#### Notes
 
- `accurate` mode is slower but captures non-linear relationships — use it when `balanced` is not enough
- GradientBoosting params scale automatically with dataset size and feature count to avoid overfitting