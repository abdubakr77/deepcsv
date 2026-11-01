import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import pandas as pd

import deepcsv


def _quiet(func, *args, **kwargs):
    with redirect_stdout(StringIO()):
        return func(*args, **kwargs)


class TestMergeData(unittest.TestCase):

    def setUp(self):
        self.users = pd.DataFrame({"id": [1, 2, 3], "name": ["a", "b", "c"], "score": [10, 20, 30]})
        self.orders = pd.DataFrame({"id": [2, 3, 4], "total": [5, 6, 7], "score": [1, 2, 3]})

    def test_how_options(self):
        sizes = {"inner": 2, "left": 3, "right": 3, "outer": 4}
        for how, size in sizes.items():
            out = _quiet(deepcsv.merge_data, self.users, self.orders, on="id", how=how)
            self.assertEqual(len(out), size, how)

    def test_same_named_columns_get_suffixes(self):
        out = _quiet(deepcsv.merge_data, self.users, self.orders, on="id", suffixes=("_user", "_order"))
        self.assertIn("score_user", out.columns)
        self.assertIn("score_order", out.columns)

    def test_list_of_keys(self):
        a = pd.DataFrame({"k1": [1, 1], "k2": ["x", "y"], "v": [1, 2]})
        b = pd.DataFrame({"k1": [1, 1], "k2": ["y", "z"], "w": [3, 4]})
        out = _quiet(deepcsv.merge_data, a, b, on=["k1", "k2"])
        self.assertEqual(out["k2"].tolist(), ["y"])

    def test_mixed_files_and_dataframes(self):
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = str(Path(tmp) / "users.csv")
            xlsx_path = str(Path(tmp) / "orders.xlsx")
            self.users.to_csv(csv_path, index=False)
            self.orders.to_excel(xlsx_path, index=False)
            out = _quiet(deepcsv.merge_data, csv_path, xlsx_path, on="id")
            self.assertEqual(len(out), 2)
            out = _quiet(deepcsv.merge_data, csv_path, self.orders, on="id")
            self.assertEqual(len(out), 2)

    def test_inputs_not_changed(self):
        before = self.users.copy()
        _quiet(deepcsv.merge_data, self.users, self.orders, on="id")
        pd.testing.assert_frame_equal(self.users, before)

    def test_repeated_keys_print_a_warning(self):
        repeated = pd.DataFrame({"id": [2, 2], "x": [1, 2]})
        buffer = StringIO()
        with redirect_stdout(buffer):
            deepcsv.merge_data(self.users, repeated, on="id")
        self.assertIn("WARNING", buffer.getvalue())

    def test_bad_inputs(self):
        with self.assertRaisesRegex(ValueError, "right dataset"):
            _quiet(deepcsv.merge_data, self.users, self.orders, on="name")
        with self.assertRaisesRegex(ValueError, "left dataset"):
            _quiet(deepcsv.merge_data, self.users, self.orders, on="total")
        with self.assertRaises(ValueError):
            _quiet(deepcsv.merge_data, self.users, self.orders, on="id", how="cross")
        with self.assertRaises(TypeError):
            _quiet(deepcsv.merge_data, self.users, self.orders, on=[])
        with self.assertRaises(TypeError):
            _quiet(deepcsv.merge_data, self.users, 5, on="id")
        with self.assertRaises(FileNotFoundError):
            _quiet(deepcsv.merge_data, "missing_file.csv", self.orders, on="id")


if __name__ == "__main__":
    unittest.main()
