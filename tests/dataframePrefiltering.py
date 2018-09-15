import unittest
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from tests.constants import INPUT_DATA_DIR
from pm4py.log.importer.csv.versions import pandas_df_imp
from pm4py.log.importer.utils import df_filtering
from pm4py.log import transform
import time

class DataframePrefilteringTest(unittest.TestCase):
    def test_prefiltering_dataframe(self):
        inputLog = os.path.join(INPUT_DATA_DIR, "running-example.csv")
        dataframe = pandas_df_imp.import_dataframe_from_path_wo_timeconversion(inputLog, sep=',')
        dataframe = df_filtering.filter_df_on_activities(dataframe, activity_key="concept:name")
        dataframe = df_filtering.filter_df_on_ncases(dataframe, case_id_glue="case:concept:name")
        dataframe = df_filtering.filter_df_on_case_length(dataframe, case_id_glue="case:concept:name")
        dataframe = pandas_df_imp.convert_timestamp_columns_in_df(dataframe)
        dataframe = dataframe.sort_values('time:timestamp')
        eventLog = pandas_df_imp.convert_dataframe_to_event_log(dataframe)
        traceLog = transform.transform_event_log_to_trace_log(eventLog)

if __name__ == "__main__":
    unittest.main()