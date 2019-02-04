import unittest

from pm4py.objects.conversion.log import factory as log_conv_fact


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
        log = log_conv_fact.apply(event_log)
        del log
        from pm4py.objects.log.importer.csv.versions import pandas_df_imp
        dataframe = pandas_df_imp.import_dataframe_from_path(os.path.join("input_data", "running-example.csv"))
        event_log = log_conv_fact.apply(dataframe, variant=log_conv_fact.TO_EVENT_STREAM)
        log = log_conv_fact.apply(event_log)
        from pm4py.objects.log.exporter.csv import factory as csv_exporter
        csv_exporter.export(event_log, "outputFile1.csv")
        os.remove("outputFile1.csv")
        from pm4py.objects.log.exporter.csv import factory as csv_exporter
        csv_exporter.export(log, "outputFile2.csv")
        os.remove("outputFile2.csv")


if __name__ == "__main__":
    unittest.main()
