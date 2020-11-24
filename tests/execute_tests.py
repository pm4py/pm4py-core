import inspect
import os
import sys
import unittest

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)
    from tests.doc_tests import DocTests
    from tests.role_detection import RoleDetectionTest
    from tests.passed_time import PassedTimeTest
    from tests.imp_everything import Pm4pyImportPackageTest
    from tests.xes_impexp_test import XesImportExportTest
    from tests.csv_impexp_test import CsvImportExportTest
    from tests.other_tests import OtherPartsTests
    from tests.alpha_test import AlphaMinerTest
    from tests.inductive_test import InductiveMinerTest
    from tests.inductive_tree_test import InductiveMinerTreeTest
    from tests.inductive_other_tests import InductiveMinerOtherTests
    from tests.alignment_test import AlignmentTest
    from tests.sna_test import SnaTests
    from tests.petri_imp_exp_test import PetriImportExportTest
    from tests.bpmn_tests import BPMNTests
    from tests.etc_tests import ETCTest
    from tests.diagn_df_conf_checking import DiagnDfConfChecking
    from tests.evaluation_tests import ProcessModelEvaluationTests
    from tests.dec_tree_test import DecisionTreeTest
    from tests.graphs_forming import GraphsForming
    from tests.heuminer_test import HeuMinerTest
    from tests.matrix_rep_test import MatrixRepTest
    from tests.main_fac_test import MainFactoriesTest
    from tests.algorithm_test import AlgorithmTest
    from tests.filtering_log_test import LogFilteringTest
    from tests.filtering_pandas_test import DataframePrefilteringTest
    from tests.map_filter_functions_test import MapFilterFunctionsTest
    from tests.statistics_log_test import StatisticsLogTest
    from tests.statistics_df_test import StatisticsDfTest
    from tests.trans_syst_tests import TransitionSystemTest
    from tests.woflan_tests import WoflanTest
    from tests.simplified_interface import SimplifiedInterfaceTest

    test_ts = TransitionSystemTest()
    test_doc_tests = DocTests()
    test_map_filter = MapFilterFunctionsTest()
    test_stats_log = StatisticsLogTest
    test_stats_df = StatisticsDfTest
    test_log_filter = LogFilteringTest()
    test_df_filter = DataframePrefilteringTest()
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
    bpmn_test = BPMNTests()
    test17_object = ETCTest()
    test20_object = ProcessModelEvaluationTests()
    test21_object = DecisionTreeTest()
    sna_tests = SnaTests()
    graphforming_test = GraphsForming()
    heuminer_test = HeuMinerTest()
    matrixrep_test = MatrixRepTest()
    main_factories_test = MainFactoriesTest()
    algorithm_test = AlgorithmTest()
    woflan_test = WoflanTest()
    diagn_dataframe_test = DiagnDfConfChecking()
    simplified_test = SimplifiedInterfaceTest()

    unittest.main()
