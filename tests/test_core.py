import unittest
from contextlib import redirect_stdout
from io import StringIO

import numpy as np
import pandas as pd

import deepcsv


def _quiet(func, *args, **kwargs):
    """Runs a deepcsv function and hides its progress prints."""
    with redirect_stdout(StringIO()):
        return func(*args, **kwargs)


class TestProcessFile(unittest.TestCase):

    def setUp(self):
        self.df = pd.DataFrame({
            "id": [1, 2, 3],
            "tags": ["[1, 2]", "[3, 4]", "[5]"],
            "extra": ["[7]", "[8]", "[9]"],
            "name": ["a", "b", "c"],
        })

    def test_all_columns(self):
        out = _quiet(deepcsv.process_file, self.df)
        self.assertIn("TagsList", out.columns)
        self.assertIn("ExtraList", out.columns)
        self.assertNotIn("tags", out.columns)
        self.assertIsInstance(out["TagsList"].iloc[0], np.ndarray)

    def test_single_column_name(self):
        out = _quiet(deepcsv.process_file, self.df, col_name="tags")
        self.assertIn("TagsList", out.columns)
        # the other list column must stay untouched
        self.assertIn("extra", out.columns)

    def test_list_of_column_names(self):
        out = _quiet(deepcsv.process_file, self.df, col_name=["tags", "extra"])
        self.assertIn("TagsList", out.columns)
        self.assertIn("ExtraList", out.columns)

    def test_to_list(self):
        out = _quiet(deepcsv.process_file, self.df, to_list=True)
        self.assertEqual(out["TagsList"].iloc[0], [1, 2])

    def test_deep_check_parses_nested(self):
        df = pd.DataFrame({"nested": ["[[1, 2], {'a': '[3]'}]", "[[4], {'a': '[5]'}]"]})
        out = _quiet(deepcsv.process_file, df, deep_check=True, to_list=True)
        self.assertEqual(out["NestedList"].iloc[0], [[1, 2], {"a": [3]}])

    def test_deep_check_warning_printed_once(self):
        buffer = StringIO()
        with redirect_stdout(buffer):
            deepcsv.process_file(self.df, deep_check=True)
        self.assertEqual(buffer.getvalue().count("Deep Check is enabled"), 1)

    def test_input_dataframe_not_changed(self):
        before = self.df.copy()
        _quiet(deepcsv.process_file, self.df)
        pd.testing.assert_frame_equal(self.df, before)

    def test_wrong_column_name_raises(self):
        with self.assertRaises(ValueError):
            _quiet(deepcsv.process_file, self.df, col_name="nope")
        with self.assertRaises(ValueError):
            _quiet(deepcsv.process_file, self.df, col_name=["tags", "nope"])


class TestAutoFix(unittest.TestCase):

    def test_numbers_as_strings_become_numeric(self):
        df = pd.DataFrame({"price": ["1", "2", "3"], "name": ["a", "b", "c"]})
        out = _quiet(deepcsv.auto_fix, df)
        self.assertTrue(pd.api.types.is_numeric_dtype(out["price"]))
        # text columns are not touched
        self.assertEqual(list(out["name"]), ["a", "b", "c"])

    def test_mixed_int_and_text_is_not_turned_into_bool(self):
        df = pd.DataFrame({"mix": [1, 2, "x", 3]})
        out = _quiet(deepcsv.auto_fix, df)
        self.assertEqual(out["mix"].dropna().tolist(), [1, 2, 3])

    def test_col_name_single_and_list(self):
        df = pd.DataFrame({"a": ["1", "2"], "b": ["3", "4"]})
        out = _quiet(deepcsv.auto_fix, df, col_name="a")
        self.assertTrue(pd.api.types.is_numeric_dtype(out["a"]))
        self.assertFalse(pd.api.types.is_numeric_dtype(out["b"]))
        out = _quiet(deepcsv.auto_fix, df, col_name=["a", "b"])
        self.assertTrue(pd.api.types.is_numeric_dtype(out["b"]))

    def test_input_dataframe_not_changed(self):
        df = pd.DataFrame({"a": ["1", "2"]})
        before = df.copy()
        _quiet(deepcsv.auto_fix, df)
        pd.testing.assert_frame_equal(df, before)

    def test_wrong_column_name_raises(self):
        with self.assertRaises(ValueError):
            _quiet(deepcsv.auto_fix, pd.DataFrame({"a": [1]}), col_name="zzz")


if __name__ == "__main__":
    unittest.main()
