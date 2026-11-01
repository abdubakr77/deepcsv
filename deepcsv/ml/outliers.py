import pandas as pd
from typing import Optional, Union

from ..utils import read_any, _validate_cols


def auto_outliers(
    df: Union[str, pd.DataFrame],
    cols: Optional[list] = None,
    method: str = "iqr",
    threshold: Optional[float] = None,
):
    """
    Auto Remove Outliers. Detects outliers in numeric columns and removes their rows.

    Parameters
    ----------
    df : str or pd.DataFrame
        File path or DataFrame.
    cols : list, optional
        Numeric columns to check. Defaults to all numeric columns.
        Pass your column list to keep a target column untouched.
    method : str, default "iqr"
        Detection strategy:
        - "iqr"              : value outside [Q1 - t*IQR, Q3 + t*IQR], fast, ignores extreme values
        - "zscore"           : |value - mean| / std is bigger than t, fast, best for bell-shaped data
        - "isolation_forest" : looks at all columns together, slower, finds rows that are
                               strange only as a combination (needs scikit-learn)
    threshold : float, optional
        Strength of the detection. Defaults per method:
        - "iqr"              : 1.5  (the multiplier t)
        - "zscore"           : 3.0  (the multiplier t)
        - "isolation_forest" : 0.05 (share of rows expected to be outliers, 0 < t <= 0.5)

    Returns
    -------
    pd.DataFrame
        DataFrame without the outlier rows (the original index is kept).

    Examples
    --------
    >>> clean = auto_outliers(df)
    >>> clean = auto_outliers(df, cols=["age", "salary"])
    >>> clean = auto_outliers(df, method="zscore", threshold=2.5)
    >>> clean = auto_outliers(df, method="isolation_forest", threshold=0.1)
    """

    methods = ["iqr", "zscore", "isolation_forest"]
    if method not in methods:
        raise ValueError(f"Unknown method: {method!r}. Choose from: {methods}")

    try:
        data = read_any(df)
    except Exception:
        data = df

    data = data.copy()

    # ── Pick the columns to check ──────────────────────────────
    if cols is not None:
        _validate_cols(cols, data)
        not_numeric = [col for col in cols if not pd.api.types.is_numeric_dtype(data[col])]
        if not_numeric:
            raise ValueError(f"These columns are not numeric: {not_numeric}")
        target_cols = cols
    else:
        target_cols = [col for col in data.columns
                       if pd.api.types.is_numeric_dtype(data[col]) and not pd.api.types.is_bool_dtype(data[col])]

    if len(target_cols) < 1:
        raise ValueError("There are no numeric columns to check for outliers.")

    # ── Default threshold per method ───────────────────────────
    if threshold is None:
        threshold = {"iqr": 1.5, "zscore": 3.0, "isolation_forest": 0.05}[method]

    if threshold <= 0:
        raise ValueError("threshold must be bigger than 0.")
    if method == "isolation_forest" and threshold > 0.5:
        raise ValueError("For isolation_forest, threshold is the share of outliers and must be <= 0.5")

    # Rows that are outliers (True = outlier)
    is_outlier = pd.Series(False, index=data.index)

    # ── IQR / Z-SCORE ──────────────────────────────────────────
    # Checked column by column, a row is removed if it is an outlier in ANY column
    if method in ["iqr", "zscore"]:
        for colname in target_cols:
            values = data[colname]

            if method == "iqr":
                q1, q3 = values.quantile(0.25), values.quantile(0.75)
                spread = q3 - q1
                col_mask = (values < q1 - threshold * spread) | (values > q3 + threshold * spread)
            else:
                std = values.std()
                # A column with no spread (or one value) can not have outliers
                col_mask = ((values - values.mean()).abs() / std > threshold) if std > 0 else pd.Series(False, index=data.index)

            # Missing values are not outliers
            col_mask = col_mask.fillna(False)

            if col_mask.sum() > 0:
                print(f"Column ({colname}): found {col_mask.sum()} outliers")
            is_outlier |= col_mask

    # ── ISOLATION FOREST ───────────────────────────────────────
    # Looks at all selected columns together, so it can catch rows
    # that look normal in every single column but strange as a whole
    else:
        from sklearn.ensemble import IsolationForest

        features = data[target_cols].fillna(data[target_cols].median())
        labels = IsolationForest(contamination=threshold, random_state=42).fit_predict(features)
        is_outlier = pd.Series(labels == -1, index=data.index)

    print(f"Removed {is_outlier.sum()} outlier rows out of {len(data)} ({method})")
    print("-"*50)

    return data[~is_outlier]
