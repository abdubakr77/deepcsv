import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import pandas as pd

import deepcsv


class TestProcessAllFiles(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "sub").mkdir()
        df = pd.DataFrame({"id": [1, 2], "tags": ["[1, 2]", "[3]"]})
        df.to_csv(self.root / "sub" / "a.csv", index=False)
        # a file without list strings must be skipped
        pd.DataFrame({"x": [1, 2]}).to_csv(self.root / "plain.csv", index=False)

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, **kwargs):
        with redirect_stdout(StringIO()):
            deepcsv.process_all_files(str(self.root), output_dir="out", **kwargs)

    def test_saves_parquet_keeping_folder_structure(self):
        self._run()
        out = self.root / "out" / "sub" / "a.parquet"
        self.assertTrue(out.exists())
        self.assertFalse((self.root / "out" / "plain.parquet").exists())
        self.assertEqual(list(pd.read_parquet(out)["TagsList"].iloc[0]), [1, 2])

    def test_custom_file_format(self):
        self._run(file_format="json")
        self.assertTrue((self.root / "out" / "sub" / "a.json").exists())

    def test_to_list(self):
        self._run(to_list=True, file_format="json")
        data = pd.read_json(self.root / "out" / "sub" / "a.json")
        self.assertEqual(data["TagsList"].iloc[0], [1, 2])

    def test_second_run_does_not_reprocess_output_folder(self):
        self._run()
        self._run()
        self.assertFalse((self.root / "out" / "out").exists())


class TestSaveAndRead(unittest.TestCase):

    def test_round_trip_all_formats(self):
        df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
        with tempfile.TemporaryDirectory() as tmp:
            for ext in ["csv", "tsv", "xlsx", "json", "parquet", "pkl", "feather"]:
                with redirect_stdout(StringIO()):
                    deepcsv.save_as(df, current_dir=str(Path(tmp) / "file"), ext=ext)
                back = deepcsv.read_any(str(Path(tmp) / f"file.{ext}"))
                self.assertEqual(back["a"].tolist(), [1, 2], ext)

    def test_unsupported_extension(self):
        with self.assertRaises(ValueError):
            deepcsv.read_any("file.abc")


if __name__ == "__main__":
    unittest.main()
