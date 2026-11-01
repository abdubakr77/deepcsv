import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import numpy as np
import pandas as pd

from deepcsv.ml import auto_fs, auto_outliers


def _quiet(func, *args, **kwargs):
    with redirect_stdout(StringIO()):
        return func(*args, **kwargs)


class TestAutoOutliers(unittest.TestCase):

    def setUp(self):
        rng = np.random.RandomState(0)
        self.df = pd.DataFrame({
            "age": rng.normal(40, 5, 200),
            "salary": rng.normal(1000, 50, 200),
            "name": ["x"] * 200,
        })
        # two clear outliers, one in each numeric column
        self.df.loc[10, "age"] = 400
        self.df.loc[20, "salary"] = 90000

    def test_iqr_removes_outlier_rows(self):
        out = _quiet(auto_outliers, self.df)
        self.assertNotIn(10, out.index)
        self.assertNotIn(20, out.index)
        # only a few rows go away, the normal data stays
        self.assertGreater(len(out), 180)

    def test_zscore(self):
        out = _quiet(auto_outliers, self.df, method="zscore")
        self.assertNotIn(10, out.index)
        self.assertNotIn(20, out.index)

    def test_isolation_forest(self):
        out = _quiet(auto_outliers, self.df, method="isolation_forest", threshold=0.05)
        self.assertNotIn(10, out.index)
        self.assertNotIn(20, out.index)
        self.assertEqual(len(out), 190)

    def test_cols_limits_the_check(self):
        out = _quiet(auto_outliers, self.df, cols=["age"])
        self.assertNotIn(10, out.index)
        self.assertIn(20, out.index)

    def test_input_not_changed_and_index_kept(self):
        before = self.df.copy()
        out = _quiet(auto_outliers, self.df)
        pd.testing.assert_frame_equal(self.df, before)
        self.assertTrue(set(out.index).issubset(set(self.df.index)))

    def test_nan_is_not_an_outlier(self):
        df = self.df.copy()
        df.loc[5, "age"] = np.nan
        out = _quiet(auto_outliers, df)
        self.assertIn(5, out.index)

    def test_constant_column_is_safe(self):
        df = pd.DataFrame({"a": [1.0] * 10, "b": list(range(10))})
        for method in ["iqr", "zscore"]:
            out = _quiet(auto_outliers, df, method=method)
            self.assertEqual(len(out), 10)

    def test_reads_file_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "data.csv")
            self.df.to_csv(path, index=False)
            out = _quiet(auto_outliers, path)
        self.assertLess(len(out), 200)

    def test_bad_inputs(self):
        with self.assertRaises(ValueError):
            _quiet(auto_outliers, self.df, method="magic")
        with self.assertRaises(ValueError):
            _quiet(auto_outliers, self.df, cols=["name"])
        with self.assertRaises(ValueError):
            _quiet(auto_outliers, self.df, cols=["missing"])
        with self.assertRaises(ValueError):
            _quiet(auto_outliers, self.df, threshold=-1)
        with self.assertRaises(ValueError):
            _quiet(auto_outliers, self.df, method="isolation_forest", threshold=0.9)
        with self.assertRaises(ValueError):
            _quiet(auto_outliers, pd.DataFrame({"a": ["x", "y"]}))


class TestAutoFs(unittest.TestCase):

    def setUp(self):
        rng = np.random.RandomState(0)
        self.df = pd.DataFrame(rng.rand(120, 4), columns=list("abcd"))
        self.df["y"] = self.df["a"] * 3 + self.df["b"]

    def test_fast_keeps_correlated_features_and_target(self):
        out = _quiet(auto_fs, self.df, "y", mode="fast")
        self.assertIn("a", out.columns)
        self.assertIn("y", out.columns)
        self.assertNotIn("d", out.columns)

    def test_balanced_keeps_useful_features(self):
        out = _quiet(auto_fs, self.df, "y", mode="balanced")
        self.assertIn("a", out.columns)
        self.assertIn("y", out.columns)


if __name__ == "__main__":
    unittest.main()
