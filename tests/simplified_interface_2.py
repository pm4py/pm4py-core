import pandas as pd
import pm4py
import os
import unittest


class SimplifiedInterface2Test(unittest.TestCase):
    def test_import_ocel_sqlite_1(self):
        ocel = pm4py.read_ocel("input_data/ocel/newocel.sqlite")

    def test_import_ocel_sqlite_2(self):
        ocel = pm4py.read_ocel_sqlite("input_data/ocel/newocel.sqlite")

    def test_export_ocel_sqlite(self):
        ocel = pm4py.read_ocel("input_data/ocel/newocel.jsonocel")
        pm4py.write_ocel(ocel, "test_output_data/newocel2.sqlite")
        os.remove("test_output_data/newocel2.sqlite")


if __name__ == "__main__":
    unittest.main()
