from .deepcsv import process_all_files, process_file
from importlib.metadata import version
import requests

def _check_for_updates():
    try:
        response = requests.get("https://pypi.org/pypi/deepcsv/json")
        latest = response.json()["info"]["version"]
        current = version("deepcsv")
        if latest != current:
            print(f"DeepCSV: New version {latest} available! — run 'pip install -U deepcsv'")
    except:
        pass

_check_for_updates()