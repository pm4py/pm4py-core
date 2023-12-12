import inspect
import os
import sys
import unittest

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
                 "ImpExpFromString", "WoflanTest", "OcelFilteringTest", "OcelDiscoveryTest", "DcrImportExportTest",
                 "DcrSemanticsTest", "DcrDiscoveryTest", "DcrConformanceTest", "DcrAlignmentTest"]

loader = unittest.TestLoader()
suite = unittest.TestSuite()

if "SimplifiedInterfaceTest" in enabled_tests:
    from tests.simplified_interface import SimplifiedInterfaceTest

    suite.addTests(loader.loadTestsFromTestCase(SimplifiedInterfaceTest))

if "SimplifiedInterface2Test" in enabled_tests:
    from tests.simplified_interface_2 import SimplifiedInterface2Test

    suite.addTests(loader.loadTestsFromTestCase(SimplifiedInterface2Test))

if "DocTests" in enabled_tests:
    from tests.doc_tests import DocTests

    suite.addTests(loader.loadTestsFromTestCase(DocTests))

if "RoleDetectionTest" in enabled_tests:
    from tests.role_detection import RoleDetectionTest

    suite.addTests(loader.loadTestsFromTestCase(RoleDetectionTest))

if "PassedTimeTest" in enabled_tests:
    from tests.passed_time import PassedTimeTest

    suite.addTests(loader.loadTestsFromTestCase(PassedTimeTest))

if "Pm4pyImportPackageTest" in enabled_tests:
    from tests.imp_everything import Pm4pyImportPackageTest

    suite.addTests(loader.loadTestsFromTestCase(Pm4pyImportPackageTest))

if "XesImportExportTest" in enabled_tests:
    from tests.xes_impexp_test import XesImportExportTest

    suite.addTests(loader.loadTestsFromTestCase(XesImportExportTest))

if "CsvImportExportTest" in enabled_tests:
    from tests.csv_impexp_test import CsvImportExportTest

    suite.addTests(loader.loadTestsFromTestCase(CsvImportExportTest))

if "OtherPartsTests" in enabled_tests:
    from tests.other_tests import OtherPartsTests

    suite.addTests(loader.loadTestsFromTestCase(OtherPartsTests))

if "AlphaMinerTest" in enabled_tests:
    from tests.alpha_test import AlphaMinerTest

    suite.addTests(loader.loadTestsFromTestCase(AlphaMinerTest))

if "InductiveMinerTest" in enabled_tests:
    from tests.inductive_test import InductiveMinerTest

    suite.addTests(loader.loadTestsFromTestCase(InductiveMinerTest))

if "InductiveMinerTreeTest" in enabled_tests:
    from tests.inductive_tree_test import InductiveMinerTreeTest

    suite.addTests(loader.loadTestsFromTestCase(InductiveMinerTreeTest))

if "AlignmentTest" in enabled_tests:
    from tests.alignment_test import AlignmentTest

    suite.addTests(loader.loadTestsFromTestCase(AlignmentTest))

if "DfgTests" in enabled_tests:
    from tests.dfg_tests import DfgTests

    suite.addTests(loader.loadTestsFromTestCase(DfgTests))

if "SnaTests" in enabled_tests:
    from tests.sna_test import SnaTests

    suite.addTests(loader.loadTestsFromTestCase(SnaTests))

if "PetriImportExportTest" in enabled_tests:
    from tests.petri_imp_exp_test import PetriImportExportTest

    suite.addTests(loader.loadTestsFromTestCase(PetriImportExportTest))

if "BPMNTests" in enabled_tests:
    from tests.bpmn_tests import BPMNTests

    suite.addTests(loader.loadTestsFromTestCase(BPMNTests))

if "ETCTest" in enabled_tests:
    from tests.etc_tests import ETCTest

    suite.addTests(loader.loadTestsFromTestCase(ETCTest))

if "DiagnDfConfChecking" in enabled_tests:
    from tests.diagn_df_conf_checking import DiagnDfConfChecking

    suite.addTests(loader.loadTestsFromTestCase(DiagnDfConfChecking))

if "ProcessModelEvaluationTests" in enabled_tests:
    from tests.evaluation_tests import ProcessModelEvaluationTests

    suite.addTests(loader.loadTestsFromTestCase(ProcessModelEvaluationTests))

if "DecisionTreeTest" in enabled_tests:
    from tests.dec_tree_test import DecisionTreeTest

    suite.addTests(loader.loadTestsFromTestCase(DecisionTreeTest))

if "GraphsForming" in enabled_tests:
    from tests.graphs_forming import GraphsForming

    suite.addTests(loader.loadTestsFromTestCase(GraphsForming))

if "HeuMinerTest" in enabled_tests:
    from tests.heuminer_test import HeuMinerTest

    suite.addTests(loader.loadTestsFromTestCase(HeuMinerTest))

if "MainFactoriesTest" in enabled_tests:
    from tests.main_fac_test import MainFactoriesTest

    suite.addTests(loader.loadTestsFromTestCase(MainFactoriesTest))

if "AlgorithmTest" in enabled_tests:
    from tests.algorithm_test import AlgorithmTest

    suite.addTests(loader.loadTestsFromTestCase(AlgorithmTest))

if "LogFilteringTest" in enabled_tests:
    from tests.filtering_log_test import LogFilteringTest

    suite.addTests(loader.loadTestsFromTestCase(LogFilteringTest))

if "DataframePrefilteringTest" in enabled_tests:
    from tests.filtering_pandas_test import DataframePrefilteringTest

    suite.addTests(loader.loadTestsFromTestCase(DataframePrefilteringTest))

if "StatisticsLogTest" in enabled_tests:
    from tests.statistics_log_test import StatisticsLogTest

    suite.addTests(loader.loadTestsFromTestCase(StatisticsLogTest))

if "StatisticsDfTest" in enabled_tests:
    from tests.statistics_df_test import StatisticsDfTest

    suite.addTests(loader.loadTestsFromTestCase(StatisticsDfTest))

if "TransitionSystemTest" in enabled_tests:
    from tests.trans_syst_tests import TransitionSystemTest

    suite.addTests(loader.loadTestsFromTestCase(TransitionSystemTest))

if "ImpExpFromString" in enabled_tests:
    from tests.imp_exp_from_string import ImpExpFromString

    suite.addTests(loader.loadTestsFromTestCase(ImpExpFromString))

if "WoflanTest" in enabled_tests:
    from tests.woflan_tests import WoflanTest

    suite.addTests(loader.loadTestsFromTestCase(WoflanTest))

if "OcelFilteringTest" in enabled_tests:
    from tests.ocel_filtering_test import OcelFilteringTest

    suite.addTests(loader.loadTestsFromTestCase(OcelFilteringTest))

if "OcelDiscoveryTest" in enabled_tests:
    from tests.ocel_discovery_test import OcelDiscoveryTest

    suite.addTests(loader.loadTestsFromTestCase(OcelDiscoveryTest))

if "DcrImportExportTest" in enabled_tests:
    from tests.dcr_test import TestImportExportDCR

    suite.addTests(loader.loadTestsFromTestCase(TestImportExportDCR))

if "DcrSemanticsTest" in enabled_tests:
    from tests.dcr_test import TestObjSematics

    suite.addTests(loader.loadTestsFromTestCase(TestObjSematics))

if "DcrDiscoveryTest" in enabled_tests:
    from tests.dcr_test import TestDiscoveryDCR

    suite.addTests(loader.loadTestsFromTestCase(TestDiscoveryDCR))

if "DcrConformanceTest" in enabled_tests:
    from tests.dcr_test import TestConformanceDCR

    suite.addTests(loader.loadTestsFromTestCase(TestConformanceDCR))

if "DcrAlignmentTest" in enabled_tests:
    from tests.dcr_test import TestAlignment
    suite.addTests(loader.loadTestsFromTestCase(TestAlignment))


def main():
    runner = unittest.TextTestRunner()
    runner.run(suite)


if __name__ == "__main__":
    main()
