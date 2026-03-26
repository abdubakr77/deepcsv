import operator
import pandas as pd
from typing import Optional, Union


# ──────────────────────────────────────────────
#               PRIVATE HELPERS
# ──────────────────────────────────────────────


def _validate_cols(cols, data):
    """
    Validates that columns is a non-empty list and all columns exist in the dataframe.
    """
    if not isinstance(cols, list):
        raise TypeError("cols must be a list. Example: ['age', 'name']")
    if len(cols) < 1:
        raise RuntimeError("cols must have at least 1 column.")

    missing = [col for col in cols if col not in data.columns]
    if missing:
        raise ValueError(f"These columns are not in the dataframe: {missing}")


def _validate_index(index, data, reset_indx=False):
    """
    Validates that index is a non-empty list and all indexes exist in the dataframe.
    """
    if reset_indx:
        data.reset_index(drop=True, inplace=True)

    if not isinstance(index, list):
        raise TypeError("index must be a list. Example: [0, 1, 2]")
    if len(index) < 1:
        raise RuntimeError("index must have at least 1 value.")

    missing = [i for i in index if i not in data.index]
    if missing:
        raise ValueError(f"These indexes are not in the dataframe: {missing}")


# ──────────────────────────────────────────────
#               PUBLIC FUNCTIONS
# ──────────────────────────────────────────────

def read_any(file_path: str) -> pd.DataFrame:
    """
    Reads a file and returns it as a pandas DataFrame.
    Automatically detects the format from the file extension.

    Parameters
    ----------
    file_path : str
        Path to the file. Supported extensions:
        - .csv, .txt   → pd.read_csv()
        - .tsv         → pd.read_csv(sep='\\t')
        - .xls, .xlsx  → pd.read_excel()
        - .json        → pd.read_json()
        - .parquet     → pd.read_parquet()
        - .pkl         → pd.read_pickle()
        - .feather     → pd.read_feather()
        - .db, .sqlite → pd.read_sql()

    Returns
    -------
    pd.DataFrame

    Raises
    ------
    ValueError
        If the file extension is not supported.

    Examples
    --------
    >>> df = read_any("data/users.csv")
    >>> df = read_any("reports/sales.xlsx")
    >>> df = read_any("warehouse/orders.parquet")
    """
    ext = file_path.split('.')[-1].lower()
    if ext in ['csv', 'txt']:
        return pd.read_csv(file_path)
    elif ext == 'tsv':
        return pd.read_csv(file_path, sep='\t')
    elif ext in ['xls', 'xlsx']:
        return pd.read_excel(file_path)
    elif ext == 'json':
        return pd.read_json(file_path)
    elif ext == 'parquet':
        return pd.read_parquet(file_path)
    elif ext == 'pkl':
        return pd.read_pickle(file_path)
    elif ext == 'feather':
        return pd.read_feather(file_path)
    elif ext in ['db', 'sqlite']:
        return pd.read_sql(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def clean_values(data_input: Union[str, pd.DataFrame],
                 cols: Optional[list] = None,
                 ax_0: bool = False,
                 index: Optional[list] = None,
                 all_cols_except: Optional[list] = None):
    """
    Clean a dataframe by removing nulls, specific index, or specific columns.

    Parameters
    ----------
    data_input : str or pd.DataFrame
        File path or DataFrame.
    cols : list, optional
        Columns to apply on.
    ax_0 : bool, default False
        If True → drop rows with nulls in selected cols.
        If False → drop the fully-null cols themselves.
    index : list, optional
        Row indexes to drop.
    all_cols_except : list, optional
        Apply on all columns except these.

    Returns
    -------
    pd.DataFrame
    """
    try:
        data = read_any(data_input)
    except Exception:
        data = data_input

    data = data.copy()

    if cols is not None:
        _validate_cols(cols, data)
        target_cols = cols

    elif all_cols_except is not None:
        if not isinstance(all_cols_except, list):
            raise TypeError("all_cols_except must be a list.")
        target_cols = [col for col in data.columns if col not in all_cols_except]

    else:
        target_cols = list(data.columns)

    if index is not None:
        _validate_index(index, data)
        data.drop(index=index, inplace=True)

    else:
        if cols is not None or all_cols_except is not None:
            if ax_0:
                data.dropna(axis=0, subset=target_cols, inplace=True)
            else:
                cols_to_drop = [col for col in target_cols if data[col].isnull().all()]
                data.drop(columns=cols_to_drop, inplace=True)
        else:
            data.dropna(axis=1, inplace=True)

    return data