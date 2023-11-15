import os
import unittest

from pm4py.algo.organizational_mining.sna import algorithm as sna_alg, util as sna_util, util
from pm4py.objects.log.importer.xes import importer as xes_importer
import pandas as pd
from pm4py.util import constants
from pm4py.objects.log.util import dataframe_utils


class SnaTests(unittest.TestCase):
    def test_1(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"

        log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))

        hw_values = sna_alg.apply(log, variant=sna_alg.Variants.HANDOVER_LOG)
        wt_values = sna_alg.apply(log, variant=sna_alg.Variants.WORKING_TOGETHER_LOG)
        sub_values = sna_alg.apply(log, variant=sna_alg.Variants.SUBCONTRACTING_LOG)
        ja_values = sna_alg.apply(log, variant=sna_alg.Variants.JOINTACTIVITIES_LOG)

    def test_pandas(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"

        log = pd.read_csv(os.path.join("..", "tests", "input_data", "running-example.csv"))
        log = dataframe_utils.convert_timestamp_columns_in_df(log, timest_format="ISO8601")

        hw_values = sna_alg.apply(log, variant=sna_alg.Variants.HANDOVER_PANDAS)
        wt_values = sna_alg.apply(log, variant=sna_alg.Variants.WORKING_TOGETHER_PANDAS)
        sub_values = sna_alg.apply(log, variant=sna_alg.Variants.SUBCONTRACTING_PANDAS)

    def test_log_orgmining_local_attr(self):
        from pm4py.algo.organizational_mining.local_diagnostics import algorithm
        log = xes_importer.apply(os.path.join("input_data", "receipt.xes"))
        algorithm.apply_from_group_attribute(log)

    def test_log_orgmining_local_clustering(self):
        from pm4py.algo.organizational_mining.local_diagnostics import algorithm
        from pm4py.algo.organizational_mining.sna.variants.log import jointactivities
        log = xes_importer.apply(os.path.join("input_data", "receipt.xes"))
        ja = jointactivities.apply(log)
        clustering = util.cluster_affinity_propagation(ja)
        algorithm.apply_from_clustering_or_roles(log, clustering)

    def test_log_orgmining_local_roles(self):
        from pm4py.algo.organizational_mining.local_diagnostics import algorithm
        from pm4py.algo.organizational_mining.roles import algorithm as roles_detection
        log = xes_importer.apply(os.path.join("input_data", "receipt.xes"))
        roles = roles_detection.apply(log)
        algorithm.apply_from_clustering_or_roles(log, roles)

    def test_sna_clustering(self):
        log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
        hw_values = sna_alg.apply(log, variant=sna_alg.Variants.HANDOVER_LOG)
        clusters = sna_util.cluster_affinity_propagation(hw_values)

    def test_res_profiles_log(self):
        from pm4py.algo.organizational_mining.resource_profiles import algorithm
        log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
        algorithm.distinct_activities(log, "2010-12-30 00:00:00", "2011-01-25 00:00:00", "Sara")
        algorithm.activity_frequency(log, "2010-12-30 00:00:00", "2011-01-25 00:00:00", "Sara", "decide")
        algorithm.activity_completions(log, "2010-12-30 00:00:00", "2011-01-25 00:00:00", "Sara")
        algorithm.case_completions(log, "2010-12-30 00:00:00", "2011-01-25 00:00:00", "Pete")
        algorithm.fraction_case_completions(log, "2010-12-30 00:00:00", "2011-01-25 00:00:00", "Pete")
        algorithm.average_workload(log, "2010-12-30 00:00:00", "2011-01-15 00:00:00", "Mike")
        algorithm.multitasking(log, "2010-12-30 00:00:00", "2011-01-25 00:00:00", "Mike")
        algorithm.average_duration_activity(log, "2010-12-30 00:00:00", "2011-01-25 00:00:00", "Sue",
                                            "examine thoroughly")
        algorithm.average_case_duration(log, "2010-12-30 00:00:00", "2011-01-25 00:00:00", "Sue")
        algorithm.interaction_two_resources(log, "2010-12-30 00:00:00", "2011-01-25 00:00:00", "Mike", "Pete")
        algorithm.social_position(log, "2010-12-30 00:00:00", "2011-01-25 00:00:00", "Sue")

    def test_res_profiles_df(self):
        from pm4py.algo.organizational_mining.resource_profiles import algorithm
        log = pd.read_csv(os.path.join("..", "tests", "input_data", "running-example.csv"))
        log = dataframe_utils.convert_timestamp_columns_in_df(log, timest_format="ISO8601")
        algorithm.distinct_activities(log, "2010-12-30 00:00:00", "2011-01-25 00:00:00", "Sara")
        algorithm.activity_frequency(log, "2010-12-30 00:00:00", "2011-01-25 00:00:00", "Sara", "decide")
        algorithm.activity_completions(log, "2010-12-30 00:00:00", "2011-01-25 00:00:00", "Sara")
        algorithm.case_completions(log, "2010-12-30 00:00:00", "2011-01-25 00:00:00", "Pete")
        algorithm.fraction_case_completions(log, "2010-12-30 00:00:00", "2011-01-25 00:00:00", "Pete")
        algorithm.average_workload(log, "2010-12-30 00:00:00", "2011-01-15 00:00:00", "Mike")
        algorithm.multitasking(log, "2010-12-30 00:00:00", "2011-01-25 00:00:00", "Mike")
        algorithm.average_duration_activity(log, "2010-12-30 00:00:00", "2011-01-25 00:00:00", "Sue",
                                            "examine thoroughly")
        algorithm.average_case_duration(log, "2010-12-30 00:00:00", "2011-01-25 00:00:00", "Sue")
        algorithm.interaction_two_resources(log, "2010-12-30 00:00:00", "2011-01-25 00:00:00", "Mike", "Pete")
        algorithm.social_position(log, "2010-12-30 00:00:00", "2011-01-25 00:00:00", "Sue")


if __name__ == "__main__":
    unittest.main()
