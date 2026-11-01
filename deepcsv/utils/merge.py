import pandas as pd
from typing import Union

from .utils import read_any

__all__ = ['merge_data']


def _load(data_input):
    """File path -> DataFrame (any supported format). A DataFrame is used as it is."""
    if isinstance(data_input, str):
        return read_any(data_input)
    if isinstance(data_input, pd.DataFrame):
        return data_input
    raise TypeError("Datasets must be a file path or a pandas DataFrame.")


def merge_data(left: Union[str, pd.DataFrame],
               right: Union[str, pd.DataFrame],
               on: Union[str, list],
               how: str = "inner",
               suffixes: tuple = ("_x", "_y")) -> pd.DataFrame:
    """
    Merges two datasets by a specific column (or a list of columns).
    Each dataset can be a file in any format read_any supports, or a DataFrame.

    Parameters
    ----------
    left : str or pd.DataFrame
        First dataset (file path or DataFrame).
    right : str or pd.DataFrame
        Second dataset (file path or DataFrame).
    on : str or list
        Column name (or names) that exists in BOTH datasets.
    how : str, default "inner"
        - "inner" : keep only the values found in both datasets
        - "left"  : keep every row of the first dataset
        - "right" : keep every row of the second dataset
        - "outer" : keep every row of both datasets
    suffixes : tuple, default ("_x", "_y")
        Added to columns that have the same name in both datasets (except `on`).

    Returns
    -------
    pd.DataFrame

    Examples
    --------
    >>> df = merge_data('users.csv', 'orders.xlsx', on='user_id')
    >>> df = merge_data(users_df, orders_df, on='user_id', how='left')
    >>> df = merge_data('a.csv', 'b.csv', on=['country', 'year'], how='outer')
    """

    hows = ["inner", "left", "right", "outer"]
    if how not in hows:
        raise ValueError(f"Unknown how: {how!r}. Choose from: {hows}")

    left_df = _load(left)
    right_df = _load(right)

    keys = [on] if isinstance(on, str) else on
    if not isinstance(keys, list) or len(keys) < 1:
        raise TypeError("on must be a column name or a list of column names. Example: 'id' or ['id', 'year']")

    # Tell the user WHICH dataset is missing the column
    for name, df in [("left", left_df), ("right", right_df)]:
        missing = [key for key in keys if key not in df.columns]
        if missing:
            raise ValueError(f"These columns are not in the {name} dataset: {missing}")

    # Repeated keys multiply rows (many-to-many), so warn the user
    for name, df in [("left", left_df), ("right", right_df)]:
        if df.duplicated(subset=keys).any():
            print(f"WARNING: the {name} dataset has repeated values in {keys}, rows can be multiplied in the result.")

    merged = left_df.merge(right_df, on=keys, how=how, suffixes=suffixes)

    print(f"Merged on {keys} ({how}): {len(left_df)} rows + {len(right_df)} rows -> {len(merged)} rows, {merged.shape[1]} columns")
    print("-"*50)

    return merged
