import pandas as pd
from typing import Optional, Union
from pathlib import Path

from .utils import read_any, save_as

__all__ = ['data_details']

# ──────────────────────────────────────────────
#               PRIVATE HELPERS
# ──────────────────────────────────────────────


def _is_numeric(series):
    """True for numbers (bool is not counted as a number here)."""
    return pd.api.types.is_numeric_dtype(series) and not pd.api.types.is_bool_dtype(series)


def _safe_nunique(series):
    """nunique() fails when cells hold lists/arrays, so compare them as text."""
    try:
        return series.nunique()
    except TypeError:
        return series.astype(str).nunique()


def _count_outliers(series):
    """Counts values outside 1.5 * IQR (same rule as auto_outliers with method='iqr')."""
    values = series.dropna()
    if len(values) == 0:
        return 0
    q1, q3 = values.quantile(0.25), values.quantile(0.75)
    spread = q3 - q1
    return int(((values < q1 - 1.5 * spread) | (values > q3 + 1.5 * spread)).sum())


def _count_duplicates(data):
    """Duplicate rows — falls back to text comparison when cells hold lists/arrays."""
    try:
        return int(data.duplicated().sum())
    except TypeError:
        return int(data.astype(str).duplicated().sum())


def _count_text_not_numbers(series):
    """
    For a text column that mostly holds numbers (ex: '12', '3.5') returns how many values
    are NOT numbers (ex: 'TBD'). Returns None if the column is not a numbers-as-text column.
    """
    values = series.dropna()
    if len(values) == 0 or not values.apply(lambda x: isinstance(x, str)).all():
        return None
    not_numbers = int(pd.to_numeric(values, errors='coerce').isna().sum())
    return not_numbers if not_numbers <= len(values) * 0.2 else None


def _build_columns_table(data):
    """One row per column with its type, missing values, uniqueness and numeric stats."""
    rows = []

    for col in data.columns:
        series = data[col]
        values = series.dropna()
        nulls = int(series.isna().sum())

        row = {
            "column": col,
            "dtype": str(series.dtype),
            "non_null": len(series) - nulls,
            "nulls": nulls,
            "null_%": round(nulls / len(series) * 100, 2) if len(series) else 0.0,
            "unique": _safe_nunique(series),
            "mixed_types": values.apply(type).nunique() > 1,
        }

        first = values.iloc[0] if len(values) else None
        row["list_strings"] = isinstance(first, str) and first.strip().startswith(("[", "{"))
        not_numbers = _count_text_not_numbers(series)
        row["numbers_as_text"] = not_numbers is not None
        row["not_numbers"] = not_numbers or 0

        if _is_numeric(series) and len(values):
            stats = series.describe()
            row.update({
                "mean": stats["mean"], "std": stats["std"], "min": stats["min"],
                "25%": stats["25%"], "50%": stats["50%"], "75%": stats["75%"], "max": stats["max"],
                "outliers": _count_outliers(series),
            })
        else:
            row["top_value"] = str(values.astype(str).mode().iloc[0]) if len(values) else None

        rows.append(row)

    return pd.DataFrame(rows)


def _build_warnings(data, columns, overview):
    """Problems found in the data, each one with the deepcsv function that can fix it."""
    warnings = []

    if overview["duplicate_rows"] > 0:
        warnings.append(f"{overview['duplicate_rows']} duplicate rows found.")

    for _, row in columns.iterrows():
        col = row["column"]
        if row["non_null"] == 0:
            warnings.append(f"({col}) has no values at all - drop it with clean_values().")
            continue
        if row["null_%"] > 50:
            warnings.append(f"({col}) is {row['null_%']}% missing.")
        if row["unique"] <= 1:
            warnings.append(f"({col}) has a single value - it carries no information.")
        if row["mixed_types"]:
            warnings.append(f"({col}) has mixed data types - fix it with auto_fix().")
        if row["numbers_as_text"]:
            extra = f" ({int(row['not_numbers'])} values are not numbers)" if row["not_numbers"] else ""
            warnings.append(f"({col}) stores numbers as text{extra} - fix it with auto_fix().")
        if row["list_strings"]:
            warnings.append(f"({col}) stores lists/dicts as strings - convert it with process_file().")
        if row.get("outliers", 0) > 0:
            warnings.append(f"({col}) has {int(row['outliers'])} outliers - remove them with ml.auto_outliers().")

    # Pairs of numeric columns that say almost the same thing
    numeric_cols = [col for col in data.columns if _is_numeric(data[col])]
    if len(numeric_cols) > 1:
        corr = data[numeric_cols].corr().abs()
        for i, first in enumerate(numeric_cols):
            for second in numeric_cols[i + 1:]:
                if corr.loc[first, second] > 0.9:
                    warnings.append(f"({first}) and ({second}) are highly correlated ({corr.loc[first, second]:.2f}).")

    return warnings


def _format_report(overview, columns, warnings):
    """Turns the report into readable text (printed on screen and saved by export='txt')."""
    line = "=" * 60
    lines = [
        line,
        " DATA DETAILS",
        line,
        f"Rows            : {overview['rows']}",
        f"Columns         : {overview['columns']}  (numeric: {overview['numeric_columns']}, other: {overview['other_columns']})",
        f"Memory          : {overview['memory_mb']} MB",
        f"Duplicate rows  : {overview['duplicate_rows']}",
        f"Missing cells   : {overview['missing_cells']} ({overview['missing_%']}%)",
        "",
        "-" * 60,
        " COLUMNS",
        "-" * 60,
        columns[["column", "dtype", "non_null", "nulls", "null_%", "unique"]].to_string(index=False),
    ]

    stats_cols = ["column", "mean", "std", "min", "25%", "50%", "75%", "max", "outliers"]
    if "mean" in columns.columns:
        numeric = columns[columns["mean"].notna()][stats_cols].copy()
        numeric["outliers"] = numeric["outliers"].astype(int)
        lines += ["", "-" * 60, " NUMERIC STATS", "-" * 60, numeric.round(3).to_string(index=False)]

    lines += ["", "-" * 60, " WARNINGS", "-" * 60]
    lines += [f"- {w}" for w in warnings] if warnings else ["No problems found."]
    lines.append(line)

    return "\n".join(lines)


# ──────────────────────────────────────────────
#               PUBLIC FUNCTIONS
# ──────────────────────────────────────────────


def data_details(data_input: Union[str, pd.DataFrame],
                 export: Optional[Union[str, list]] = None,
                 output_path: str = "data_details",
                 show: bool = True) -> dict:
    """
    Shows deep details about your data: size, memory, missing values, duplicates,
    types, unique values, numeric stats, outliers and the problems deepcsv can fix.

    Parameters
    ----------
    data_input : str or pd.DataFrame
        File path (any format read_any supports) or an existing DataFrame.
    export : str or list, optional
        Saves the report to a file:
        - "csv" : the columns table (one row per column)
        - "txt" : the full report exactly as printed
        Pass ["csv", "txt"] to save both.
    output_path : str, default "data_details"
        File path without extension. Example: "reports/sales_details"
    show : bool, default True
        False -> do not print the report (only return it).

    Returns
    -------
    dict
        - "overview" : dict   → rows, columns, memory, duplicates, missing cells
        - "columns"  : pd.DataFrame → one row per column with all the details
        - "warnings" : list   → problems found in the data

    Examples
    --------
    >>> report = data_details('data/users.csv')
    >>> report = data_details(df, export="csv")
    >>> report = data_details(df, export=["csv", "txt"], output_path="reports/users")
    >>> report["columns"]
    """

    # Check the export option before doing any work
    export_list = [export] if isinstance(export, str) else list(export or [])
    export_list = [fmt.strip().lower() for fmt in export_list]
    unknown = [fmt for fmt in export_list if fmt not in ("csv", "txt")]
    if unknown:
        raise ValueError(f"Unsupported export: {unknown}. Choose from: ['csv', 'txt']")

    try:
        data = read_any(data_input)
    except Exception:
        data = data_input

    # ── Overview ───────────────────────────────────────────────
    total_cells = data.shape[0] * data.shape[1]
    missing_cells = int(data.isna().sum().sum())
    numeric_count = sum(_is_numeric(data[col]) for col in data.columns)

    overview = {
        "rows": data.shape[0],
        "columns": data.shape[1],
        "numeric_columns": numeric_count,
        "other_columns": data.shape[1] - numeric_count,
        "memory_mb": round(data.memory_usage(deep=True).sum() / 1024 ** 2, 3),
        "duplicate_rows": _count_duplicates(data),
        "missing_cells": missing_cells,
        "missing_%": round(missing_cells / total_cells * 100, 2) if total_cells else 0.0,
    }

    columns = _build_columns_table(data)
    warnings = _build_warnings(data, columns, overview)
    report_text = _format_report(overview, columns, warnings)

    if show:
        print(report_text)

    # ── Export ─────────────────────────────────────────────────
    if export_list:
        Path(output_path).resolve().parent.mkdir(parents=True, exist_ok=True)

    if "csv" in export_list:
        save_as(data=columns, current_dir=output_path, ext="csv")

    if "txt" in export_list:
        with open(f"{output_path}.txt", "w", encoding="utf-8") as file:
            file.write(report_text)
        print(f"Saved: {output_path}.txt")
        print("-"*50)

    return {"overview": overview, "columns": columns, "warnings": warnings}
