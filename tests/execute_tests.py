import inspect
import os
import sys
import unittest

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

    import pm4py

    pm4py.util.constants.SHOW_PROGRESS_BAR = False
    pm4py.util.constants.SHOW_EVENT_LOG_DEPRECATION = False
    pm4py.util.constants.SHOW_INTERNAL_WARNINGS = False
    # pm4py.util.constants.DEFAULT_TIMESTAMP_PARSE_FORMAT = None

    enabled_tests = ["SimplifiedInterfaceTest", "SimplifiedInterface2Test", "DocTests", "RoleDetectionTest",
                     "PassedTimeTest", "Pm4pyImportPackageTest", "XesImportExportTest", "CsvImportExportTest",
                     "OtherPartsTests", "AlphaMinerTest", "InductiveMinerTest", "InductiveMinerTreeTest",
                     "AlignmentTest", "DfgTests", "SnaTests", "PetriImportExportTest", "BPMNTests", "ETCTest",
                     "DiagnDfConfChecking", "ProcessModelEvaluationTests", "DecisionTreeTest", "GraphsForming",
                     "HeuMinerTest", "MainFactoriesTest", "AlgorithmTest", "LogFilteringTest",
                     "DataframePrefilteringTest", "StatisticsLogTest", "StatisticsDfTest", "TransitionSystemTest",
                     "ImpExpFromString", "WoflanTest", "OcelFilteringTest", "OcelDiscoveryTest"]

    if "SimplifiedInterfaceTest" in enabled_tests:
        from tests.simplified_interface import SimplifiedInterfaceTest

        simplified_test = SimplifiedInterfaceTest()

    if "SimplifiedInterface2Test" in enabled_tests:
        from tests.simplified_interface_2 import SimplifiedInterface2Test

        simplified_2_test = SimplifiedInterface2Test()

    if "DocTests" in enabled_tests:
        from tests.doc_tests import DocTests

        test_doc_tests = DocTests()

    if "RoleDetectionTest" in enabled_tests:
        from tests.role_detection import RoleDetectionTest

        test_roles = RoleDetectionTest()

    if "PassedTimeTest" in enabled_tests:
        from tests.passed_time import PassedTimeTest

        test_pttime = PassedTimeTest()

    if "Pm4pyImportPackageTest" in enabled_tests:
        from tests.imp_everything import Pm4pyImportPackageTest

        test1_object = Pm4pyImportPackageTest()

    if "XesImportExportTest" in enabled_tests:
        from tests.xes_impexp_test import XesImportExportTest

        test2_object = XesImportExportTest()

    if "CsvImportExportTest" in enabled_tests:
        from tests.csv_impexp_test import CsvImportExportTest

        test3_object = CsvImportExportTest()

    if "OtherPartsTests" in enabled_tests:
        from tests.other_tests import OtherPartsTests

        other_tests = OtherPartsTests()

    if "AlphaMinerTest" in enabled_tests:
        from tests.alpha_test import AlphaMinerTest

        test4_object = AlphaMinerTest()

    if "InductiveMinerTest" in enabled_tests:
        from tests.inductive_test import InductiveMinerTest

        test5_object = InductiveMinerTest()

    if "InductiveMinerTreeTest" in enabled_tests:
        from tests.inductive_tree_test import InductiveMinerTreeTest

        test55_object = InductiveMinerTreeTest()

    if "AlignmentTest" in enabled_tests:
        from tests.alignment_test import AlignmentTest

        test6_object = AlignmentTest()

    if "DfgTests" in enabled_tests:
        from tests.dfg_tests import DfgTests

        test_dfg = DfgTests()

    if "SnaTests" in enabled_tests:
        from tests.sna_test import SnaTests

        sna_tests = SnaTests()

    if "PetriImportExportTest" in enabled_tests:
        from tests.petri_imp_exp_test import PetriImportExportTest

        test7_object = PetriImportExportTest()

    if "BPMNTests" in enabled_tests:
        from tests.bpmn_tests import BPMNTests

        bpmn_test = BPMNTests()

    if "ETCTest" in enabled_tests:
        from tests.etc_tests import ETCTest

        test17_object = ETCTest()

    if "DiagnDfConfChecking" in enabled_tests:
        from tests.diagn_df_conf_checking import DiagnDfConfChecking

        diagn_dataframe_test = DiagnDfConfChecking()

    if "ProcessModelEvaluationTests" in enabled_tests:
        from tests.evaluation_tests import ProcessModelEvaluationTests

        test20_object = ProcessModelEvaluationTests()

    if "DecisionTreeTest" in enabled_tests:
        from tests.dec_tree_test import DecisionTreeTest

        test21_object = DecisionTreeTest()

    if "GraphsForming" in enabled_tests:
        from tests.graphs_forming import GraphsForming

        graphforming_test = GraphsForming()

    if "HeuMinerTest" in enabled_tests:
        from tests.heuminer_test import HeuMinerTest

        heuminer_test = HeuMinerTest()

    if "MainFactoriesTest" in enabled_tests:
        from tests.main_fac_test import MainFactoriesTest

        main_factories_test = MainFactoriesTest()

    if "AlgorithmTest" in enabled_tests:
        from tests.algorithm_test import AlgorithmTest

        algorithm_test = AlgorithmTest()

    if "LogFilteringTest" in enabled_tests:
        from tests.filtering_log_test import LogFilteringTest

        test_log_filter = LogFilteringTest()

    if "DataframePrefilteringTest" in enabled_tests:
        from tests.filtering_pandas_test import DataframePrefilteringTest

        test_df_filter = DataframePrefilteringTest()

    if "StatisticsLogTest" in enabled_tests:
        from tests.statistics_log_test import StatisticsLogTest

        test_stats_log = StatisticsLogTest

    if "StatisticsDfTest" in enabled_tests:
        from tests.statistics_df_test import StatisticsDfTest

        test_stats_df = StatisticsDfTest

    if "TransitionSystemTest" in enabled_tests:
        from tests.trans_syst_tests import TransitionSystemTest

        test_ts = TransitionSystemTest()

    if "ImpExpFromString" in enabled_tests:
        from tests.imp_exp_from_string import ImpExpFromString

        test_ies = ImpExpFromString()

    if "WoflanTest" in enabled_tests:
        from tests.woflan_tests import WoflanTest

        woflan_test = WoflanTest()

    if "OcelFilteringTest" in enabled_tests:
        from tests.ocel_filtering_test import OcelFilteringTest

        ocel_filtering_test = OcelFilteringTest()

    if "OcelDiscoveryTest" in enabled_tests:
        from tests.ocel_discovery_test import OcelDiscoveryTest

        ocel_discovery_test = OcelDiscoveryTest()

    unittest.main()
