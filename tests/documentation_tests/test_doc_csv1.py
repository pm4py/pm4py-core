import unittest


class CSV1DocumentationTest(unittest.TestCase):
    def test_csv1documentation(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        import os
        from pm4py.objects.log.importer.csv import factory as csv_importer
        event_log = csv_importer.import_event_stream(os.path.join("input_data", "running-example.csv"))
        event_log_length = len(event_log)
        del event_log_length
        from pm4py.objects.log import transform
        log = transform.transform_event_stream_to_event_log(event_log, case_glue="case:concept:name")
        del log
        from pm4py.objects.log.importer.csv.versions import pandas_df_imp
        from pm4py.objects.log import transform
        dataframe = pandas_df_imp.import_dataframe_from_path(os.path.join("input_data", "running-example.csv"))
        event_log = pandas_df_imp.convert_dataframe_to_event_stream(dataframe)
        log = transform.transform_event_stream_to_event_log(event_log, case_glue="case:concept:name")
        from pm4py.objects.log.exporter.csv import factory as csv_exporter
        csv_exporter.export(event_log, "outputFile1.csv")
        os.remove("outputFile1.csv")
        from pm4py.objects.log.exporter.csv import factory as csv_exporter
        csv_exporter.export(log, "outputFile2.csv")
        os.remove("outputFile2.csv")


if __name__ == "__main__":
    unittest.main()
