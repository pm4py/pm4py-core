import unittest
import os, sys, inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
parentdir2 = os.path.dirname(parentdir)
sys.path.insert(0, parentdir)
sys.path.insert(0, parentdir2)


class CSV1DocumentationTest(unittest.TestCase):
    def test_csv1documentation(self):
        import os

        from pm4py.entities.log.importer.csv import factory as csv_importer

        event_log = csv_importer.import_log(os.path.join("inputData","running-example.csv"))

        event_log_length = len(event_log)
        # print(event_log_length)
        for event in event_log:
            # print(event)
            pass

        from pm4py.entities.log import transform

        trace_log = transform.transform_event_log_to_trace_log(event_log, case_glue="case:concept:name")

        from pm4py.entities.log.importer.csv.versions import pandas_df_imp
        from pm4py.entities.log import transform

        dataframe = pandas_df_imp.import_dataframe_from_path(os.path.join("inputData","running-example.csv"))
        event_log = pandas_df_imp.convert_dataframe_to_event_log(dataframe)
        trace_log = transform.transform_event_log_to_trace_log(event_log, case_glue="case:concept:name")

        from pm4py.entities.log.exporter.csv import factory as csv_exporter

        csv_exporter.export_log(event_log, "outputFile1.csv")
        os.remove("outputFile1.csv")

        from pm4py.entities.log.exporter.csv import factory as csv_exporter

        csv_exporter.export_log(trace_log, "outputFile2.csv")
        os.remove("outputFile2.csv")

if __name__ == "__main__":
    unittest.main()
