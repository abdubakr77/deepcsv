from .deepcsv import process_all_files, process_file 
from .utils import read_any, clean_values, auto_fix, save_as ,_validate_cols , _validate_index , _parse_operator , _validate_condition , _val_dtype
from importlib.metadata import PackageNotFoundError, version as _version
import requests as _requests

__all__ = [
    "process_file",
    "process_all_files",
    "read_any",
    "clean_values",
    "auto_fix",
    "save_as"
]


def _check_for_updates():
    try:
        response = _requests.get("https://pypi.org/pypi/deepcsv/json", timeout=5)
        latest = response.json()["info"]["version"]
        current = _version("deepcsv")
        if latest != current:
            print(
                f"DeepCSV: update available — run 'pip install deepcsv -U' ({latest})"
            )
    except PackageNotFoundError:
        pass
    except Exception:
        pass


_check_for_updates()