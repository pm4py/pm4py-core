import inspect
import os
import sys
import unittest

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parent_dir = os.path.dirname(current_dir)
    parent_dir2 = os.path.dirname(parent_dir)
    sys.path.insert(0, parent_dir2)
    from old_tests.tests.role_detection import RoleDetectionTest
    from old_tests.tests.passed_time import PassedTimeTest
    from old_tests.tests.imp_everything import Pm4pyImportPackageTest
    from old_tests.tests.xes_impexp_test import XesImportExportTest
    from old_tests.tests.csv_impexp_test import CsvImportExportTest
    from old_tests.tests.other_tests import OtherPartsTests
    from old_tests.tests.alpha_test import AlphaMinerTest
    from old_tests.tests.inductive_test import InductiveMinerTest
    from old_tests.tests.inductive_tree_test import InductiveMinerTreeTest
    from old_tests.tests.inductive_other_tests import InductiveMinerOtherTests
    from old_tests.tests.alignment_test import AlignmentTest
    from old_tests.tests.sna_test import SnaTests
    from old_tests.tests.petri_imp_exp_test import PetriImportExportTest
    from old_tests.tests.documentation_tests.test_doc_alpha1 import AlphaMinerDocumentationTest
    from old_tests.tests.documentation_tests.test_doc_inductive1 import InductiveMinerDocumentationTest
    from old_tests.tests.documentation_tests.test_doc_dfgraph1 import DfGraphDocumentationTest
    from old_tests.tests.documentation_tests.test_doc_xes1 import XES1DocumentationTest
    from old_tests.tests.documentation_tests.test_doc_csv1 import CSV1DocumentationTest
    from old_tests.tests.documentation_tests.test_doc_classifiers1 import Classifiers1DocumentationTest
    from old_tests.tests.documentation_tests.test_doc_measures import DocMeasuresDocumentationTest
    from old_tests.tests.etc_tests import ETCTest
    from old_tests.tests.evaluation_tests import ProcessModelEvaluationTests
    from old_tests.tests.dec_tree_test import DecisionTreeTest
    from old_tests.tests.serialization_test import SerializationTest
    from old_tests.tests.graphs_forming import GraphsForming
    from old_tests.tests.heuminer_test import HeuMinerTest
    from old_tests.tests.matrix_rep_test import MatrixRepTest
    from old_tests.tests.main_fac_test import MainFactoriesTest
    from old_tests.tests.filtering_log_test import LogFilteringTest
    from old_tests.tests.filtering_pandas_test import DataframePrefilteringTest

    test_roles = RoleDetectionTest()
    test_pttime = PassedTimeTest()
    test1_object = Pm4pyImportPackageTest()
    test2_object = XesImportExportTest()
    test3_object = CsvImportExportTest()
    other_tests = OtherPartsTests()
    test4_object = AlphaMinerTest()
    test5_object = InductiveMinerTest()
    test55_object = InductiveMinerTreeTest()
    test56_object = InductiveMinerOtherTests()
    test6_object = AlignmentTest()
    test7_object = PetriImportExportTest()
    test8_object = AlphaMinerDocumentationTest()
    test9_object = InductiveMinerDocumentationTest()
    test10_object = DfGraphDocumentationTest()
    test11_object = XES1DocumentationTest()
    test12_object = CSV1DocumentationTest()
    test13_object = Classifiers1DocumentationTest()
    test14_object = DocMeasuresDocumentationTest()
    test17_object = ETCTest()
    test20_object = ProcessModelEvaluationTests()
    test21_object = DecisionTreeTest()
    sna_tests = SnaTests()
    serialization_test = SerializationTest()
    graphforming_test = GraphsForming()
    heuminer_test = HeuMinerTest()
    matrixrep_test = MatrixRepTest()
    main_factories_test = MainFactoriesTest()
    test_filtering_log = LogFilteringTest()
    filtering_test_dataframe = DataframePrefilteringTest()

    unittest.main()
