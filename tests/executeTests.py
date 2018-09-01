import unittest
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from tests.xesImportExportTest import XesImportExportTest
from tests.csvImportExportTest import CsvImportExportTest
from tests.alphaMinerTest import AlphaMinerTest
from tests.imdfTest import InductiveMinerDFTest
from tests.alignmentTest import AlignmentTest
from tests.petriImportExportTest import PetriImportExportTest

if __name__ == "__main__":
	unittest.main()