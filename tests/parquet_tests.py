import os
import unittest


class ParquetTests(unittest.TestCase):
    def test_importing_parquet(self):
        from pm4py.objects.log.importer.parquet import importer as parquet_importer
        df = parquet_importer.apply(os.path.join("input_data", "receipt.parquet"),
                                    variant=parquet_importer.Variants.PYARROW)
        df = parquet_importer.apply(os.path.join("input_data", "receipt.parquet"),
                                    variant=parquet_importer.Variants.FASTPARQUET)
        log = parquet_importer.import_log(os.path.join("input_data", "running-example.parquet"),
                                          variant=parquet_importer.Variants.PYARROW)
        log = parquet_importer.import_minimal_log(os.path.join("input_data", "running-example.parquet"),
                                                  variant=parquet_importer.Variants.PYARROW)


if __name__ == "__main__":
    unittest.TestCase()
