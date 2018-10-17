import inspect
import os
import sys
import unittest

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)
    from tests.imp_everything import Pm4pyImportPackageTest
    from tests.xes_impexp_test import XesImportExportTest
    from tests.csv_impexp_test import CsvImportExportTest
    from tests.alpha_test import AlphaMinerTest
    from tests.imdf_test import InductiveMinerDFTest
    from tests.alignment_test import AlignmentTest
    from tests.petri_imp_exp_test import PetriImportExportTest
    from tests.documentation_tests.test_doc_alpha1 import AlphaMinerDocumentationTest
    from tests.documentation_tests.test_doc_inductive1 import InductiveMinerDocumentationTest
    from tests.documentation_tests.test_doc_dfgraph1 import DfGraphDocumentationTest
    from tests.documentation_tests.test_doc_xes1 import XES1DocumentationTest
    from tests.documentation_tests.test_doc_csv1 import CSV1DocumentationTest
    from tests.documentation_tests.test_doc_classifiers1 import Classifiers1DocumentationTest
    from tests.documentation_tests.test_doc_measures import DocMeasuresDocumentationTest
    from tests.dataframe_prefilter import DataframePrefilteringTest
    from tests.filtering_test import LogFilteringTest
    from tests.etc_tests import ETCTest
    from tests.petri_log_gen_tests import PetriLogGeneratorTests
    from tests.trans_syst_tests import TransitionSystemTest
    from tests.evaluation_tests import ProcessModelEvaluationTests
    from tests.visual_test import VisualizationTest1
    from tests.case_man_test import CaseManagementTest

    test1_object = Pm4pyImportPackageTest()
    test2_object = XesImportExportTest()
    test3_object = CsvImportExportTest()
    test4_object = AlphaMinerTest()
    test5_object = InductiveMinerDFTest()
    test6_object = AlignmentTest()
    test7_object = PetriImportExportTest()
    test8_object = AlphaMinerDocumentationTest()
    test9_object = InductiveMinerDocumentationTest()
    test10_object = DfGraphDocumentationTest()
    test11_object = XES1DocumentationTest()
    test12_object = CSV1DocumentationTest()
    test13_object = Classifiers1DocumentationTest()
    test14_object = DocMeasuresDocumentationTest()
    test15_object = DataframePrefilteringTest()
    test16_object = LogFilteringTest()
    test17_object = ETCTest()
    test18_object = PetriLogGeneratorTests()
    test19_object = TransitionSystemTest()
    test20_object = ProcessModelEvaluationTests()
    test21_object = VisualizationTest1()
    test22_object = CaseManagementTest()

    unittest.main()
