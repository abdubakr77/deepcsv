import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import numpy as np
import pandas as pd

import deepcsv


def _quiet(func, *args, **kwargs):
    with redirect_stdout(StringIO()):
        return func(*args, **kwargs)


class TestDataDetails(unittest.TestCase):

    def setUp(self):
        rng = np.random.RandomState(0)
        self.df = pd.DataFrame({
            "age": rng.normal(40, 5, 100),
            "price": ["12"] * 100,
            "tags": ["[1, 2]"] * 100,
            "mix": [1, "a"] * 50,
            "city": ["Cairo", "Giza"] * 50,
        })
        self.df.loc[3, "age"] = 900
        self.df.loc[10:20, "city"] = None

    def test_overview(self):
        report = _quiet(deepcsv.data_details, self.df)
        overview = report["overview"]
        self.assertEqual(overview["rows"], 100)
        self.assertEqual(overview["columns"], 5)
        self.assertEqual(overview["missing_cells"], 11)
        self.assertEqual(overview["numeric_columns"], 1)

    def test_columns_table(self):
        columns = _quiet(deepcsv.data_details, self.df)["columns"].set_index("column")
        self.assertEqual(columns.loc["city", "nulls"], 11)
        self.assertEqual(columns.loc["age", "outliers"], 1)
        self.assertTrue(columns.loc["mix", "mixed_types"])
        self.assertTrue(columns.loc["tags", "list_strings"])
        self.assertTrue(columns.loc["price", "numbers_as_text"])
        self.assertFalse(columns.loc["city", "mixed_types"])

    def test_mostly_numbers_as_text_counts_the_bad_values(self):
        df = pd.DataFrame({"price": ["10", "20", "30", "40", "TBD"]})
        columns = _quiet(deepcsv.data_details, df)["columns"].set_index("column")
        self.assertTrue(columns.loc["price", "numbers_as_text"])
        self.assertEqual(columns.loc["price", "not_numbers"], 1)
        warnings = _quiet(deepcsv.data_details, df)["warnings"]
        self.assertTrue(any("1 values are not numbers" in w for w in warnings))

    def test_plain_text_is_not_numbers_as_text(self):
        df = pd.DataFrame({"city": ["Cairo", "Giza", "10", "Tanta", "Luxor"]})
        columns = _quiet(deepcsv.data_details, df)["columns"].set_index("column")
        self.assertFalse(columns.loc["city", "numbers_as_text"])

    def test_warnings_point_to_the_fixing_function(self):
        text = " ".join(_quiet(deepcsv.data_details, self.df)["warnings"])
        for hint in ["auto_fix", "process_file", "auto_outliers"]:
            self.assertIn(hint, text)

    def test_show_false_prints_nothing(self):
        buffer = StringIO()
        with redirect_stdout(buffer):
            deepcsv.data_details(self.df, show=False)
        self.assertEqual(buffer.getvalue(), "")

    def test_clean_data_has_no_warnings(self):
        df = pd.DataFrame({"a": [1.0, 2.0, 3.0, 4.0], "b": ["x", "y", "z", "w"]})
        self.assertEqual(_quiet(deepcsv.data_details, df)["warnings"], [])

    def test_duplicates(self):
        df = pd.DataFrame({"a": [1, 1, 2], "b": ["x", "x", "y"]})
        self.assertEqual(_quiet(deepcsv.data_details, df)["overview"]["duplicate_rows"], 1)

    def test_array_cells_do_not_crash(self):
        # what process_file produces: columns whose cells are arrays / lists
        df = pd.DataFrame({"TagsList": [np.array([1, 2]), np.array([1, 2]), np.array([3])], "id": [1, 1, 2]})
        report = _quiet(deepcsv.data_details, df)
        self.assertEqual(report["overview"]["rows"], 3)

    def test_empty_dataframe(self):
        report = _quiet(deepcsv.data_details, pd.DataFrame({"a": []}))
        self.assertEqual(report["overview"]["rows"], 0)

    def test_reads_file_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "data.csv")
            self.df.to_csv(path, index=False)
            report = _quiet(deepcsv.data_details, path)
        self.assertEqual(report["overview"]["rows"], 100)

    def test_export_csv_and_txt(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = str(Path(tmp) / "reports" / "details")
            _quiet(deepcsv.data_details, self.df, export=["csv", "txt"], output_path=out)
            saved = pd.read_csv(out + ".csv")
            self.assertEqual(saved["column"].tolist(), list(self.df.columns))
            text = Path(out + ".txt").read_text(encoding="utf-8")
            self.assertIn("DATA DETAILS", text)
            self.assertIn("WARNINGS", text)

    def test_export_single_format_only_writes_that_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = str(Path(tmp) / "details")
            _quiet(deepcsv.data_details, self.df, export="txt", output_path=out)
            self.assertTrue(Path(out + ".txt").exists())
            self.assertFalse(Path(out + ".csv").exists())

    def test_bad_export_raises_before_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = str(Path(tmp) / "details")
            with self.assertRaises(ValueError):
                _quiet(deepcsv.data_details, self.df, export="pdf", output_path=out)
            self.assertEqual(list(Path(tmp).iterdir()), [])


if __name__ == "__main__":
    unittest.main()
