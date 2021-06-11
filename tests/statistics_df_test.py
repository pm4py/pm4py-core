from pm4py.objects.log.util import dataframe_utils
import unittest
import os
import pandas as pd


class StatisticsDfTest(unittest.TestCase):
    def get_dataframe(self):
        dataframe = pd.read_csv(os.path.join("input_data", "roadtraffic100traces.csv"))
        dataframe = dataframe_utils.convert_timestamp_columns_in_df(dataframe)
        return dataframe

    def test_get_attributes(self):
        from pm4py.statistics.attributes.pandas import get
        df = self.get_dataframe()
        get.get_attribute_values(df, "concept:name")
        get.get_kde_date_attribute(df, "time:timestamp")
        get.get_kde_numeric_attribute(df, "amount")

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

if __name__ == "__main__":
    unittest.main()
