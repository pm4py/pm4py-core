import unittest
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

class Pm4pyImportPackageTest(unittest.TestCase):
    def test_importeverything(self):
        import pm4py

if __name__ == "__main__":
    unittest.main()