import pandas as pd
import pm4py
import os
from pm4py.util import constants
import unittest


class SimplifiedInterface2Test(unittest.TestCase):
    def test_import_ocel_sqlite_1(self):
        ocel = pm4py.read_ocel("input_data/ocel/newocel.sqlite")

    def test_import_ocel_sqlite_2(self):
        ocel = pm4py.read_ocel_sqlite("input_data/ocel/newocel.sqlite")

    def test_export_ocel_sqlite(self):
        ocel = pm4py.read_ocel("input_data/ocel/newocel.jsonocel")
        pm4py.write_ocel(ocel, "test_output_data/newocel2.sqlite")
        os.remove("test_output_data/newocel2.sqlite")

    def test_reduce_invisibles(self):
        net, im, fm = pm4py.read_pnml("input_data/running-example.pnml")
        pm4py.reduce_petri_net_invisibles(net)

    def test_reduce_implicit_places(self):
        net, im, fm = pm4py.read_pnml("input_data/running-example.pnml")
        pm4py.reduce_petri_net_implicit_places(net, im, fm)

    def test_language_df(self):
        for legacy_obj in [True, False]:
            log = pm4py.read_xes("input_data/running-example.xes", return_legacy_log_object=legacy_obj)
            pm4py.get_stochastic_language(log)

    def test_language_log(self):
        log = pm4py.read_xes("input_data/running-example.xes", return_legacy_log_object=True)
        pm4py.get_stochastic_language(log)

    def test_language_model(self):
        net, im, fm = pm4py.read_pnml("input_data/running-example.pnml")
        pm4py.get_stochastic_language(net, im, fm)

    def test_conversion_df_to_nx(self):
        for legacy_obj in [True, False]:
            log = pm4py.read_xes("input_data/running-example.xes", return_legacy_log_object=legacy_obj)
            pm4py.convert_log_to_networkx(log)

    def test_conversion_log_to_nx(self):
        log = pm4py.read_xes("input_data/running-example.xes", return_legacy_log_object=True)
        pm4py.convert_log_to_networkx(log)

    def test_conversion_ocel_to_nx(self):
        ocel = pm4py.read_ocel("input_data/ocel/example_log.jsonocel")
        pm4py.convert_ocel_to_networkx(ocel)

    def test_conversion_df_to_ocel(self):
        for legacy_obj in [True, False]:
            log = pm4py.read_xes("input_data/running-example.xes", return_legacy_log_object=legacy_obj)
            pm4py.convert_log_to_ocel(log)

    def test_conversion_log_to_ocel(self):
        log = pm4py.read_xes("input_data/running-example.xes", return_legacy_log_object=True)
        pm4py.convert_log_to_ocel(log)

    def test_conversion_ocelcsv_to_ocel(self):
        import pandas as pd
        dataframe = pd.read_csv("input_data/ocel/example_log.csv")
        pm4py.convert_log_to_ocel(dataframe, activity_column="ocel:activity", timestamp_column="ocel:timestamp")

    def test_conversion_petri_to_nx(self):
        net, im, fm = pm4py.read_pnml("input_data/running-example.pnml")
        nx_digraph = pm4py.convert_petri_net_to_networkx(net, im, fm)

    def test_stochastic_language(self):
        log1 = pm4py.read_xes("input_data/running-example.xes")
        log2 = pm4py.read_xes("input_data/running-example.xes", return_legacy_log_object=True)
        lang1 = pm4py.get_stochastic_language(log1)
        lang2 = pm4py.get_stochastic_language(log2)
        pm4py.compute_emd(lang1, lang2)

    def test_hybrid_ilp_miner(self):
        for legacy_obj in [True, False]:
            log = pm4py.read_xes("input_data/running-example.xes", return_legacy_log_object=legacy_obj)
            pm4py.discover_petri_net_ilp(log)


if __name__ == "__main__":
    unittest.main()
