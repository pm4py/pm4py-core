import unittest
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from tests.importEverything import Pm4pyImportPackageTest
from tests.xesImportExportTest import XesImportExportTest
from tests.csvImportExportTest import CsvImportExportTest
from tests.alphaMinerTest import AlphaMinerTest
from tests.imdfTest import InductiveMinerDFTest
from tests.alignmentTest import AlignmentTest
from tests.petriImportExportTest import PetriImportExportTest
from tests.documentationTests.testDocAlpha1 import AlphaMinerDocumentationTest
from tests.documentationTests.testDocInductive1 import InductiveMinerDocumentationTest
from tests.documentationTests.testDocDfGraph1 import DfGraphDocumentationTest
from tests.documentationTests.testDocXes1 import XES1DocumentationTest
from tests.documentationTests.testDocCsv1 import CSV1DocumentationTest
from tests.documentationTests.testDocClassifiers1 import Classifiers1DocumentationTest
from tests.documentationTests.testDocMeasures import DocMeasuresDocumentationTest
from tests.dataframePrefiltering import DataframePrefilteringTest
from tests.filteringTest import LogFilteringTest
from tests.etcTests import ETCTest
from tests.petriLogGeneratorTests import PetriLogGeneratorTests
from tests.transitionSystemTests import TransitionSystemTest
from tests.evaluationTests import ProcessModelEvaluationTests
from tests.visualizationTest import VisualizationTest1
from tests.caseManagementTest import CaseManagementTest

if __name__ == "__main__":
	unittest.main()