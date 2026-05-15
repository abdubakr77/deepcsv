import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, GradientBoostingClassifier
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_score
from tqdm import tqdm


def auto_fs(
    df: pd.DataFrame,
    target,
    model=None,
    mode="balanced",
    corr_threshold=0.3
):
    """
    Auto Feature Selection — automatically selects the most relevant features for a given target.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame containing features and target column.
    target : str
        Name of the target column.
    model : sklearn estimator, optional
        Custom model to use in balanced/accurate modes. Defaults to auto-tuned Ridge or GradientBoosting.
    mode : str, default "balanced"
        Selection strategy:
        - "fast"     : correlation filter only — fastest, no model involved
        - "balanced" : Ridge + cross-validation loop — smarter, moderate speed
        - "accurate" : GradientBoosting + cross-validation loop — slowest, most accurate
    corr_threshold : float, default 0.3
        Minimum absolute correlation to keep a feature. Used in "fast" mode only.

    Returns
    -------
    pd.DataFrame
        DataFrame with only the selected features + target column.
    """

    if target is None:
        # Soon: unsupervised feature selection
        pass

    else:
        # ── FAST MODE ──────────────────────────────────────────────
        # Uses correlation matrix to filter features quickly
        # No model involved — just drops anything below corr_threshold
        if mode == "fast":

            column_to_keep = []
            df_corr = df.corr()
            target_idx_incorr = df_corr.index.get_indexer([target])[0]

            if target in df.columns:
                df_target = df[target]
                df = df.drop(target, axis=1)

            for colname in tqdm(df.columns, desc="Filtering by correlation"):
                if abs(df_corr[colname].iloc[target_idx_incorr]) > abs(corr_threshold):
                    column_to_keep.append(colname)

            result = pd.concat([df[column_to_keep], df_target], axis=1)
            return result

        # ── BALANCED MODE ──────────────────────────────────────────
        # Uses Ridge + cross-validation loop
        # Drops a feature if removing it doesn't hurt (or improves) the score
        elif mode == "balanced":
            df_copy = df.copy()

            def auto_alpha_tuned():
                # Scale alpha based on dataset size for better regularization
                if len(df) <= 10000:
                    return 0.1
                elif len(df) <= 100000:
                    return 1.0
                else:
                    return 5.0

            model = Ridge(alpha=auto_alpha_tuned())

            X = df_copy.drop(target, axis=1)
            y = df_copy[target]

            # Baseline score with all features
            best_score = cross_val_score(model, X, y, cv=3).mean()

            for colname in tqdm(list(X.columns), desc="Selecting features (balanced)"):
                temp_X = X.drop(columns=[colname])

                score = cross_val_score(model, temp_X, y, cv=3).mean()

                # Keep the drop if score stays the same or improves
                if score >= best_score:
                    X = temp_X
                    best_score = score
                    print("Saved Best Score:", best_score)

            result = pd.concat([X, y], axis=1)
            return result

        # ── ACCURATE MODE ──────────────────────────────────────────
        # Uses GradientBoosting + cross-validation loop
        # Slower but captures non-linear relationships between features and target
        elif mode == "accurate":
            df_copy = df.copy()

            def get_gb_params(n_rows: int, n_features: int = None):
                """
                Auto-tune GradientBoosting params based on dataset size and feature count.

                Parameters
                ----------
                n_rows : int
                    Number of rows in the dataset.
                n_features : int, optional
                    Number of features — adjusts depth, estimators, and split threshold.

                Returns
                -------
                dict
                    GradientBoostingRegressor parameters.
                """

                # Base params scaled by row count
                if n_rows < 10000:
                    params = {
                        "n_estimators": 100,
                        "learning_rate": 0.1,
                        "max_depth": 3,
                        "subsample": 1.0,
                        "min_samples_split": 2
                    }
                elif n_rows < 100000:
                    params = {
                        "n_estimators": 200,
                        "learning_rate": 0.05,
                        "max_depth": 4,
                        "subsample": 0.8,
                        "min_samples_split": 5
                    }
                else:
                    params = {
                        "n_estimators": 300,
                        "learning_rate": 0.03,
                        "max_depth": 5,
                        "subsample": 0.7,
                        "min_samples_split": 10
                    }

                # Adjust params based on feature count
                if n_features is not None:
                    if n_features > 50:
                        # Many features — increase complexity
                        params["max_depth"] = min(params["max_depth"] + 2, 7)
                        params["n_estimators"] = int(params["n_estimators"] * 1.5)
                        params["min_samples_split"] = params["min_samples_split"] + 4

                    elif n_features > 20:
                        # Moderate features — slight boost
                        params["max_depth"] = min(params["max_depth"] + 1, 6)
                        params["n_estimators"] = int(params["n_estimators"] * 1.2)
                        params["min_samples_split"] = params["min_samples_split"] + 2

                    elif n_features < 10:
                        # Few features — simplify to avoid overfitting
                        params["max_depth"] = max(params["max_depth"] - 1, 2)
                        params["n_estimators"] = int(params["n_estimators"] * 0.8)

                return params

            X = df_copy.drop(target, axis=1)
            y = df_copy[target]

            params = get_gb_params(len(df), n_features=len(X.columns))
            model = GradientBoostingRegressor(**params)

            # Baseline score with all features
            best_score = cross_val_score(model, X, y, cv=5, n_jobs=-1).mean()

            for colname in tqdm(list(X.columns), desc="Selecting features (accurate)"):
                temp_X = X.drop(columns=[colname])

                score = cross_val_score(model, temp_X, y, cv=5, n_jobs=-1).mean()

                # Keep the drop if score stays the same or improves
                if score >= best_score:
                    X = temp_X
                    best_score = score
                    print("Saved Best Score:", best_score)

            result = pd.concat([X, y], axis=1)
            return result