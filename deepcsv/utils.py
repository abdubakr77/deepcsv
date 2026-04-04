import operator
import pandas as pd
from typing import Optional, Union
from pathlib import Path

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
    
def _parse_operator(op_string: str):
    op_map = {
        ">=": operator.ge,
        "<=": operator.le,
        ">":  operator.gt,
        "<":  operator.lt,
        "==": operator.eq,
        "!=": operator.ne,
    }
    op = op_map.get(op_string.strip())
    if op is None:
        raise ValueError(f"Operator not recognized: {op_string!r}. Choose from: {list(op_map.keys())}")
    return op

def _validate_condition(condition):
    """
    Validates condition list and returns (operator_func, value).
    Expected format: [operator_string, number] or [number, operator_string]
    Example: [">=", 500] or [500, ">="]
    """
    if not isinstance(condition, list):
        raise TypeError("condition must be a list. Example: ['>=', 500]")
    if len(condition) != 2:
        raise RuntimeError(f"condition must have exactly 2 elements. Got {len(condition)}")
 
    op_func, cond_val = None, None
 
    for item in condition:
        item_str = str(item).strip()
        if item_str in ["==", "<=", ">=", "!=", "<", ">"]:
            op_func = _parse_operator(item_str)
        elif str(item).lstrip("-").replace(".", "", 1).isnumeric():
            cond_val = float(item)
        else:
            raise ValueError(
                f"Invalid condition item: {item!r}. "
                "Should be like: ['>=', 500] or [500, '>=']"
            )
 
    if op_func is None or cond_val is None:
        raise ValueError("condition must have one operator and one numeric value. Example: ['>=', 500]")
 
    return op_func, cond_val

def _save_as(data: pd.DataFrame, current_dir = str(Path.cwd()), ext= str) -> None:
    """
    Saves a DataFrame to a file with the specified format.

    Parameters
    ----------
    data : pd.DataFrame
        The DataFrame to save.
    file_path : str
        Path without extension. Example: "data/myfile"
    ext : str
        File extension. Supported:
        - .csv      → pd.to_csv()
        - .xlsx     → pd.to_excel()
        - .json     → pd.to_json()
        - .parquet  → pd.to_parquet()
        - .pkl      → pd.to_pickle()
        - .feather  → pd.to_feather()
        - .tsv      → pd.to_csv(sep='\\t')
        - .html     → pd.to_html()
        - .xml      → pd.to_xml()

    Returns
    -------
    None

    Examples
    --------
    >>> _save_as(df, "data/myfile", ".parquet")
    >>> _save_as(df, "data/myfile", ".csv")
    """
    ext = ext.strip().lower()
    if not ext.startswith("."):
        ext = f".{ext}"

    full_path = f"{current_dir}{ext}"

    writers = {
        ".csv":     lambda: data.to_csv(full_path, index=False),
        ".tsv":     lambda: data.to_csv(full_path, sep='\t', index=False),
        ".xlsx":    lambda: data.to_excel(full_path, index=False),
        ".json":    lambda: data.to_json(full_path, orient="records", indent=2),
        ".parquet": lambda: data.to_parquet(full_path, index=False),
        ".pkl":     lambda: data.to_pickle(full_path),
        ".feather": lambda: data.to_feather(full_path),
        ".html":    lambda: data.to_html(full_path, index=False),
        ".xml":     lambda: data.to_xml(full_path, index=False),
    }

    writer = writers.get(ext)
    if writer is None:
        raise ValueError(
            f"Unsupported extension: {ext!r}\n"
            f"Supported: {list(writers.keys())}"
        )

    writer()
    print(f"Saved: {full_path}")
    print("-"*50)


def _val_dtype(x,dtype):
    if dtype == str:
        return str(x)
    elif dtype == float:
        return float(x)
    else:
        return bool(x)

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
                 all_cols_except: Optional[list] = None,
                 ax_0: bool = False,
                 index: Optional[list] = None,
                 condition: Optional[list] = None,
                 finding_value=None,
                 finding_type: Optional[type] = None):
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
    
    condition       : [operator, value] → ex: ['>=', 500]
                      applied only with finding_value or finding_type
    finding_value   : find and remove rows that have this specific value
    finding_type    : find and remove rows that have this specific type (ex: str, int)

    Returns
    -------
    pd.DataFrame
    """
    try:
        data = read_any(data_input)
    except Exception:
        data = data_input

    data = data.copy()
    op_func, cond_val = None, None
    if condition is not None:
        op_func, cond_val = _validate_condition(condition)

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

    

    elif finding_value is not None:
        for col in target_cols:
            if col not in data.columns:
                continue
            if op_func and cond_val is not None:
                # Remove finding_value only where condition is met
                mask = (data[col] == finding_value) & (data[col].apply(
                    lambda x: op_func(x, cond_val) if isinstance(x, (int, float)) else False
                ))
            else:
                mask = data[col] == finding_value
            data = data[~mask]
 

    elif finding_type is not None:
        for col in target_cols:
            if col not in data.columns:
                continue
            if op_func and cond_val is not None:
                mask = data[col].apply(
                    lambda x: isinstance(x, finding_type) and op_func(x, cond_val)
                )
            else:
                mask = data[col].apply(lambda x: isinstance(x, finding_type))
            data = data[~mask]

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



def auto_fix(data_input: Union[str, pd.DataFrame]):
    """
    Automatically detects and fixes columns with mixed data types in a DataFrame.

    This function scans each column for mixed data types (columns containing exactly
    2 different Python types) and attempts to convert all values to the most common
    type. If the primary conversion fails, it falls back to the secondary type.

    Parameters
    ----------
    data_input : str or pd.DataFrame
        File path to read from or an existing DataFrame to process.

    Returns
    -------
    pd.DataFrame
        DataFrame with mixed-type columns automatically converted to consistent types.

    Notes
    -----
    - Only processes columns with exactly 2 different data types
    - Attempts conversion to the most frequent type first
    - Falls back to the less frequent type if primary conversion fails
    - Prints progress messages for each column being processed
    - Supported target types: str, float, bool

    Examples
    --------
    >>> df = auto_fix('data/mixed_types.csv')
    Found a column (price) Have mixed DTypes!
    This Col Have These DTypes: [<class 'str'>, <class 'float'>]
    NOW TRYING TO FIX!
    Done!
    -----------------------------------

    >>> df = auto_fix(my_dataframe)
    """
    
    try:
        df = read_any(data_input)
    except Exception:
        df = data_input


    for ColName in df.columns:
        if len(df[ColName].apply(type).unique()) == 2:
            print(f"Found a column ({ColName}) Have mixed DTypes!")
            print(f"This Col Have These DTypes: {df[ColName].apply(type).unique()}\nNOW TRYING TO FIX!")
            
            dtype_dict = dict(df[ColName].apply(type).value_counts().to_dict())
            dtype_values_list = [dtype_value for dtype_value in dtype_dict.values()]
            dtype = None
            try:
                for dtype_name in dtype_dict.keys():
                    if dtype_dict[dtype_name] == max(dtype_values_list):
                        dtype = dtype_name

            
                df[ColName] = df[ColName].apply(lambda x: _val_dtype(x,dtype))

            except: 
                for dtype_name in dtype_dict.keys():
                    if dtype_dict[dtype_name] == min(dtype_values_list):
                        dtype = dtype_name

            
                df[ColName] = df[ColName].apply(lambda x: _val_dtype(x,dtype))
            print("Done!")
            print("—"*35)
    return df