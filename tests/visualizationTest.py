import unittest
import os, sys, inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
from pm4py.entities.log.importer.xes import factory as xes_importer
from pm4py.entities.log.adapters.pandas import csv_import_adapter
from pm4py.algo.discovery.dfg.adapters.pandas import df_statistics
from pm4py.algo.filtering.pandas.attributes import attributes_filter as pd_attribute_filter
from pm4py.entities.log.importer.csv.versions import pandas_df_imp
from pm4py.entities.log import transform
from pm4py.algo.discovery.dfg import factory as dfg_factory
from pm4py.algo.discovery.inductive import factory as inductive_miner
from pm4py.visualization.petrinet import factory as petri_vis_factory
from pm4py.visualization.dfg import factory as dfg_vis_factory
from pm4py.algo.filtering.tracelog.attributes import attributes_filter as log_attribute_filter
from pm4py.visualization.petrinet.util import vis_trans_shortest_paths
from pm4py.util import simple_view
from pm4py.algo.filtering.tracelog.auto_filter import auto_filter

class VisualizationTest1(unittest.TestCase):
    def test_getdfgfreqvis_log(self):
        logPath = os.path.join("inputData","running-example.xes")
        log = xes_importer.import_log(logPath)
        variant = "frequency"
        dfg = dfg_factory.apply(log, variant=variant)
        gviz = dfg_vis_factory.apply(dfg, log=log, variant=variant)

    def test_getdfgfreqvis_acticount(self):
        logPath = os.path.join("inputData","running-example.xes")
        log = xes_importer.import_log(logPath)
        variant = "frequency"
        dfg = dfg_factory.apply(log, variant=variant)
        activities_count = log_attribute_filter.get_attribute_values(log, "concept:name")
        gviz = dfg_vis_factory.apply(dfg, activities_count=activities_count, variant=variant)

    def test_getdfgperfvis_log(self):
        logPath = os.path.join("inputData","running-example.xes")
        log = xes_importer.import_log(logPath)
        variant = "performance"
        dfg = dfg_factory.apply(log, variant=variant)
        gviz = dfg_vis_factory.apply(dfg, log=log, variant=variant)

    def test_getpetrifreqvis_token(self):
        logPath = os.path.join("inputData","running-example.xes")
        log = xes_importer.import_log(logPath)
        net, initial_marking, final_marking = inductive_miner.apply(log)
        variant = "frequency"
        gviz = petri_vis_factory.apply(net, initial_marking, final_marking, log=log, variant=variant)

    def test_getpetriperfvis_token(self):
        logPath = os.path.join("inputData","running-example.xes")
        log = xes_importer.import_log(logPath)
        variant = "performance"
        net, initial_marking, final_marking = inductive_miner.apply(log)
        gviz = petri_vis_factory.apply(net, initial_marking, final_marking, log=log, variant=variant)

    def test_getpetrifreqvis_greedy(self):
        logPath = os.path.join("inputData","running-example.xes")
        log = xes_importer.import_log(logPath)
        net, initial_marking, final_marking = inductive_miner.apply(log)
        variant = "frequency"
        dfg = dfg_factory.apply(log, variant=variant)
        activities_count = log_attribute_filter.get_attribute_values(log, "concept:name")
        spaths = vis_trans_shortest_paths.get_shortest_paths(net)
        aggregated_statistics = vis_trans_shortest_paths.get_net_decorations_from_dfg_spaths_acticount(net, dfg, spaths, activities_count, variant=variant)
        parameters_vis = {"format":"svg"}
        gviz = petri_vis_factory.apply(net, initial_marking, final_marking, aggregated_statistics=aggregated_statistics, variant=variant, parameters=parameters_vis)

    def test_getpetriperfvis_greedy(self):
        logPath = os.path.join("inputData","running-example.xes")
        log = xes_importer.import_log(logPath)
        net, initial_marking, final_marking = inductive_miner.apply(log)
        variant = "performance"
        dfg = dfg_factory.apply(log, variant=variant)
        activities_count = log_attribute_filter.get_attribute_values(log, "concept:name")
        spaths = vis_trans_shortest_paths.get_shortest_paths(net)
        aggregated_statistics = vis_trans_shortest_paths.get_net_decorations_from_dfg_spaths_acticount(net, dfg, spaths, activities_count, variant=variant)
        parameters_vis = {"format":"svg"}
        gviz = petri_vis_factory.apply(net, initial_marking, final_marking, aggregated_statistics=aggregated_statistics, variant=variant, parameters=parameters_vis)

    def test_getdfgfreqvis_dataframe(self):
        variant = "frequency"
        logPath = os.path.join("inputData","running-example.csv")
        dataframe = csv_import_adapter.import_dataframe_from_path_wo_timeconversion(logPath)
        dataframe = csv_import_adapter.convert_timestamp_columns_in_df(dataframe)
        activities_count = pd_attribute_filter.get_attribute_values(dataframe, "concept:name")
        dfg_frequency = df_statistics.get_dfg_graph(dataframe, measure="frequency")
        gviz = dfg_vis_factory.apply(dfg_frequency, activities_count=activities_count, variant=variant)

    def test_getdfgperfvis_dataframe(self):
        variant = "performance"
        logPath = os.path.join("inputData","running-example.csv")
        dataframe = csv_import_adapter.import_dataframe_from_path_wo_timeconversion(logPath)
        dataframe = csv_import_adapter.convert_timestamp_columns_in_df(dataframe)
        activities_count = pd_attribute_filter.get_attribute_values(dataframe, "concept:name")
        [dfg_frequency, dfg_performance] = df_statistics.get_dfg_graph(dataframe, measure="both")
        gviz = dfg_vis_factory.apply(dfg_performance, activities_count=activities_count, variant=variant)

    def test_getpetrifreqvis_dataframe_greedy(self):
        variant = "frequency"
        logPath = os.path.join("inputData","running-example.csv")
        dataframe = csv_import_adapter.import_dataframe_from_path_wo_timeconversion(logPath)
        dataframe = csv_import_adapter.convert_timestamp_columns_in_df(dataframe)
        activities_count = pd_attribute_filter.get_attribute_values(dataframe, "concept:name")
        dfg_frequency = df_statistics.get_dfg_graph(dataframe, measure=variant)
        net, initial_marking, final_marking = inductive_miner.apply_dfg(dfg_frequency)
        spaths = vis_trans_shortest_paths.get_shortest_paths(net)
        aggregated_statistics = vis_trans_shortest_paths.get_net_decorations_from_dfg_spaths_acticount(net,
                                                                                                       dfg_frequency,
                                                                                                       spaths,
                                                                                                       activities_count,
                                                                                                       variant=variant)
        gviz = petri_vis_factory.apply(net, initial_marking, final_marking, variant=variant,
                                       aggregated_statistics=aggregated_statistics)

    def test_getpetriperfvis_dataframe_greedy(self):
        variant = "performance"
        logPath = os.path.join("inputData","running-example.csv")
        dataframe = csv_import_adapter.import_dataframe_from_path_wo_timeconversion(logPath)
        dataframe = csv_import_adapter.convert_timestamp_columns_in_df(dataframe)
        activities_count = pd_attribute_filter.get_attribute_values(dataframe, "concept:name")
        [dfg_frequency, dfg_performance] = df_statistics.get_dfg_graph(dataframe, measure="both")
        net, initial_marking, final_marking = inductive_miner.apply_dfg(dfg_frequency)
        spaths = vis_trans_shortest_paths.get_shortest_paths(net)
        aggregated_statistics = vis_trans_shortest_paths.get_net_decorations_from_dfg_spaths_acticount(net,
                                                                                                       dfg_performance,
                                                                                                       spaths,
                                                                                                       activities_count,
                                                                                                       variant=variant)
        gviz = petri_vis_factory.apply(net, initial_marking, final_marking, variant=variant,
                                       aggregated_statistics=aggregated_statistics)

    def test_getpetrifreqvis_dataframe_convert_token(self):
        variant = "frequency"
        logPath = os.path.join("inputData","running-example.csv")
        dataframe = csv_import_adapter.import_dataframe_from_path_wo_timeconversion(logPath)
        dataframe = csv_import_adapter.convert_timestamp_columns_in_df(dataframe)
        event_log = pandas_df_imp.convert_dataframe_to_event_log(dataframe)
        log = transform.transform_event_log_to_trace_log(event_log)
        net, initial_marking, final_marking = inductive_miner.apply(log)
        gviz = petri_vis_factory.apply(net, initial_marking, final_marking, log=log, variant=variant)

    def test_getpetriperfvis_dataframe_convert_token(self):
        variant = "performance"
        logPath = os.path.join("inputData","running-example.csv")
        dataframe = csv_import_adapter.import_dataframe_from_path_wo_timeconversion(logPath)
        dataframe = csv_import_adapter.convert_timestamp_columns_in_df(dataframe)
        event_log = pandas_df_imp.convert_dataframe_to_event_log(dataframe)
        log = transform.transform_event_log_to_trace_log(event_log)
        net, initial_marking, final_marking = inductive_miner.apply(log)
        gviz = petri_vis_factory.apply(net, initial_marking, final_marking, log=log, variant=variant)

    def test_simple_view(self):
        logPath = os.path.join("inputData","receipt.xes")
        log = xes_importer.import_log(logPath)
        filtered_log = auto_filter.apply_auto_filter(log)
        gviz = simple_view.apply(filtered_log, {"algorithm":"alpha", "decoration":"frequency"})
        gviz = simple_view.apply(filtered_log, {"algorithm":"inductive", "decoration":"frequency"})
        gviz = simple_view.apply(filtered_log, {"algorithm":"dfg", "decoration":"frequency"})
        gviz = simple_view.apply(filtered_log, {"algorithm":"tsystem2", "decoration":"frequency"})
        gviz = simple_view.apply(filtered_log, {"algorithm":"tsystem3", "decoration":"frequency"})

if __name__ == "__main__":
    unittest.main()