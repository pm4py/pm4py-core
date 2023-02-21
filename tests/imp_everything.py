import os
import unittest


class Pm4pyImportPackageTest(unittest.TestCase):
    def test_importeverything(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        import pm4py
        log = pm4py.objects.log.importer.xes.importer.apply(
            os.path.join("input_data", "running-example.xes"))
        self.assertEqual(len(log), 6)


if __name__ == "__main__":
    unittest.main()
