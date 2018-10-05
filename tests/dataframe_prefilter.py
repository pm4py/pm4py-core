import unittest
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from tests.constants import INPUT_DATA_DIR
from pm4py.entities.log.adapters.pandas import csv_import_adapter as csv_import_adapter
from pm4py.entities.log.importer.csv.versions import pandas_df_imp
from pm4py.algo.filtering.pandas.auto_filter import auto_filter
from pm4py.algo.filtering.pandas.attributes import attributes_filter
from pm4py.algo.filtering.pandas.cases import case_filter
from pm4py.algo.filtering.pandas.variants import variants_filter
from pm4py.algo.cases.pandas import case_statistics
from pm4py.entities.log import transform
from pm4py.algo.filtering.pandas.paths import paths_filter
from pm4py.algo.filtering.pandas.timestamp import timestamp_filter

class DataframePrefilteringTest(unittest.TestCase):
    def test_prefiltering_dataframe(self):
        inputLog = os.path.join(INPUT_DATA_DIR, "running-example.csv")
        dataframe = csv_import_adapter.import_dataframe_from_path_wo_timeconversion(inputLog, sep=',')
        dataframe = attributes_filter.filter_df_keeping_specno_activities(dataframe, activity_key="concept:name")
        dataframe = case_filter.filter_on_ncases(dataframe, case_id_glue="case:concept:name")
        #dataframe = case_filter.filter_df_on_case_length(dataframe, case_id_glue="case:concept:name")
        dataframe = csv_import_adapter.convert_timestamp_columns_in_df(dataframe)
        dataframe = dataframe.sort_values('time:timestamp')
        eventLog = pandas_df_imp.convert_dataframe_to_event_log(dataframe)
        traceLog = transform.transform_event_log_to_trace_log(eventLog)

    def test_autofiltering_dataframe(self):
        inputLog = os.path.join(INPUT_DATA_DIR, "running-example.csv")
        dataframe = csv_import_adapter.import_dataframe_from_path_wo_timeconversion(inputLog, sep=',')
        dataframe = auto_filter.apply_auto_filter(dataframe)

    def test_filtering_variants(self):
        inputLog = os.path.join(INPUT_DATA_DIR, "running-example.csv")
        dataframe = csv_import_adapter.import_dataframe_from_path_wo_timeconversion(inputLog, sep=',')
        variants = case_statistics.get_variants_statistics(dataframe)
        chosenVariants = [variants[0]["variant"]]
        dataframe = variants_filter.apply(dataframe, chosenVariants)

    def test_filtering_attr_events(self):
        inputLog = os.path.join(INPUT_DATA_DIR, "running-example.csv")
        dataframe = csv_import_adapter.import_dataframe_from_path_wo_timeconversion(inputLog, sep=',')
        df1 = attributes_filter.apply_events(dataframe, ["reject request"], parameters={"positive": True})
        df2 = attributes_filter.apply_events(dataframe, ["reject request"], parameters={"positive": False})

    def test_filtering_paths(self):
        inputLog = os.path.join(INPUT_DATA_DIR, "running-example.csv")
        dataframe = csv_import_adapter.import_dataframe_from_path(inputLog, sep=',')
        df3 = paths_filter.apply(dataframe, [("examine casually", "check ticket")], {"positive": False})
        df3 = paths_filter.apply(dataframe, [("examine casually", "check ticket")], {"positive": True})

    def test_filtering_timeframe(self):
        inputLog = os.path.join(INPUT_DATA_DIR, "receipt.csv")
        df = csv_import_adapter.import_dataframe_from_path(inputLog, sep=',')
        df1 = timestamp_filter.apply_events(df, "2011-03-09 00:00:00", "2012-01-18 23:59:59")
        df2 = timestamp_filter.filter_traces_intersecting(df, "2011-03-09 00:00:00", "2012-01-18 23:59:59")
        df3 = timestamp_filter.filter_traces_contained(df, "2011-03-09 00:00:00", "2012-01-18 23:59:59")

if __name__ == "__main__":
    unittest.main()