from pm4py.objects.log.util import dataframe_utils
import unittest
import os
from pm4py.util import constants, pandas_utils


class StatisticsDfTest(unittest.TestCase):
    def get_dataframe(self):
        dataframe = pandas_utils.read_csv(os.path.join("input_data", "roadtraffic100traces.csv"))
        dataframe = dataframe_utils.convert_timestamp_columns_in_df(dataframe, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
        return dataframe

    def test_end_activities(self):
        from pm4py.statistics.end_activities.pandas import get
        df = self.get_dataframe()
        get.get_end_activities(df)

    def test_start_activities(self):
        from pm4py.statistics.start_activities.pandas import get
        df = self.get_dataframe()
        get.get_start_activities(df)

    def test_case_arrival(self):
        from pm4py.statistics.traces.generic.pandas import case_arrival
        df = self.get_dataframe()
        case_arrival.get_case_arrival_avg(df)

    def test_case_statistics(self):
        from pm4py.statistics.traces.generic.pandas import case_statistics
        df = self.get_dataframe()
        case_statistics.get_cases_description(df)
        case_statistics.get_variants_df(df)
        case_statistics.get_variant_statistics(df)
        #case_statistics.get_variant_statistics_with_case_duration(df)
        case_statistics.get_events(df, "N77802")
        case_statistics.get_variants_df_with_case_duration(df)
        case_statistics.get_variants_df_and_list(df)
        case_statistics.get_kde_caseduration(df)

    def test_variants(self):
        from pm4py.statistics.variants.pandas import get
        df = self.get_dataframe()
        get.get_variants_set(df)

    def test_batch_detection(self):
        from pm4py.algo.discovery.batches.variants import pandas as pandas_batches
        dataframe = pandas_utils.read_csv(os.path.join("input_data", "receipt.csv"))
        dataframe = dataframe_utils.convert_timestamp_columns_in_df(dataframe, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
        pandas_batches.apply(dataframe)

    def test_case_overlap(self):
        from pm4py.statistics.overlap.cases.pandas import get as overlap_get
        df = self.get_dataframe()
        overlap_get.apply(df)

    def test_cycle_time(self):
        from pm4py.statistics.traces.cycle_time.pandas import get as cycle_time_get
        df = self.get_dataframe()
        cycle_time_get.apply(df)

    def test_rework(self):
        from pm4py.statistics.rework.pandas import get as rework_get
        df = self.get_dataframe()
        rework_get.apply(df)

    def test_events_distribution(self):
        from pm4py.statistics.attributes.pandas import get as attributes_get
        df = self.get_dataframe()
        attributes_get.get_events_distribution(df)

    def test_msd(self):
        from pm4py.algo.discovery.minimum_self_distance.variants import pandas as msd_pandas
        df = self.get_dataframe()
        msd_pandas.apply(df)


if __name__ == "__main__":
    unittest.main()
