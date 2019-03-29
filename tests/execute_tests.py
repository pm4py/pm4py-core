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
    from tests.imdf_tree_test import InductiveMinerDFTreeTest
    from tests.alignment_test import AlignmentTest
    from tests.sna_test import SnaTests
    from tests.petri_imp_exp_test import PetriImportExportTest
    from tests.random_variables_test import RandomVariableTest
    from tests.documentation_tests.test_doc_alpha1 import AlphaMinerDocumentationTest
    from tests.documentation_tests.test_doc_inductive1 import InductiveMinerDocumentationTest
    from tests.documentation_tests.test_doc_dfgraph1 import DfGraphDocumentationTest
    from tests.documentation_tests.test_doc_xes1 import XES1DocumentationTest
    from tests.documentation_tests.test_doc_csv1 import CSV1DocumentationTest
    from tests.documentation_tests.test_doc_classifiers1 import Classifiers1DocumentationTest
    from tests.documentation_tests.test_doc_measures import DocMeasuresDocumentationTest
    from tests.etc_tests import ETCTest
    from tests.evaluation_tests import ProcessModelEvaluationTests
    from tests.dec_tree_test import DecisionTreeTest
    from tests.filtering_test import LogFilteringTest
    from tests.dataframe_prefilter import DataframePrefilteringTest
    from tests.simple_execution import SimpleExecutionTest
    from tests.graphs_forming import GraphsForming
    from tests.heuminer_test import HeuMinerTest
    from tests.matrix_rep_test import MatrixRepTest

    test_rv = RandomVariableTest()
    test1_object = Pm4pyImportPackageTest()
    test2_object = XesImportExportTest()
    test3_object = CsvImportExportTest()
    test4_object = AlphaMinerTest()
    test5_object = InductiveMinerDFTest()
    test55_object = InductiveMinerDFTreeTest()
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
    filtering_test = LogFilteringTest()
    prefiltering_test = DataframePrefilteringTest()
    simpleex_test = SimpleExecutionTest()
    graphforming_test = GraphsForming()
    heuminer_test = HeuMinerTest()
    matrixrep_test = MatrixRepTest()

    unittest.main()
