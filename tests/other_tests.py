import os
import unittest
import pandas as pd
from pm4py.algo.discovery.log_skeleton import algorithm as lsk_alg
from pm4py.algo.conformance.log_skeleton import algorithm as lsk_conf_alg
from pm4py.objects.process_tree.importer import importer as ptree_importer
from pm4py.objects.process_tree.exporter import exporter as ptree_exporter
from pm4py.algo.discovery.performance_spectrum.variants import log as log_pspectrum, dataframe as df_pspectrum
from pm4py.objects.dfg.importer import importer as dfg_importer
from pm4py.objects.dfg.exporter import exporter as dfg_exporter
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.statistics.start_activities.log import get as start_activities
from pm4py.statistics.end_activities.log import get as end_activities
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.statistics.variants.log import get as variants_get
from pm4py.algo.simulation.playout.petri_net import algorithm
from pm4py.objects.conversion.log import converter
from pm4py.objects.log.util import dataframe_utils
from pm4py.util import pandas_utils, constants
from pm4py.objects.conversion.process_tree import converter as process_tree_converter


class OtherPartsTests(unittest.TestCase):
    def test_emd_1(self):
        from pm4py.algo.evaluation.earth_mover_distance import algorithm as earth_mover_distance
        M = {("a", "b", "d", "e"): 0.49, ("a", "d", "b", "e"): 0.49, ("a", "c", "d", "e"): 0.01,
             ("a", "d", "c", "e"): 0.01}
        L1 = {("a", "b", "d", "e"): 0.49, ("a", "d", "b", "e"): 0.49, ("a", "c", "d", "e"): 0.01,
              ("a", "d", "c", "e"): 0.01}
        earth_mover_distance.apply(M, L1)

    def test_emd_2(self):
        from pm4py.algo.evaluation.earth_mover_distance import algorithm as earth_mover_distance
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        lang_log = variants_get.get_language(log)
        process_tree = inductive_miner.apply(log)
        net1, im1, fm1 = process_tree_converter.apply(process_tree)
        lang_model1 = variants_get.get_language(
            algorithm.apply(net1, im1, fm1, variant=algorithm.Variants.STOCHASTIC_PLAYOUT,
                            parameters={algorithm.Variants.STOCHASTIC_PLAYOUT.value.Parameters.LOG: log}))
        emd = earth_mover_distance.apply(lang_model1, lang_log)

    def test_importing_dfg(self):
        dfg, sa, ea = dfg_importer.apply(os.path.join("input_data", "running-example.dfg"))

    def test_exporting_dfg(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        dfg = dfg_discovery.apply(log)
        dfg_exporter.apply(dfg, os.path.join("test_output_data", "running-example.dfg"))
        dfg, sa, ea = dfg_importer.apply(os.path.join("test_output_data", "running-example.dfg"))
        os.remove(os.path.join("test_output_data", "running-example.dfg"))

    def test_exporting_dfg_with_sa_ea(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        dfg = dfg_discovery.apply(log)
        sa = start_activities.get_start_activities(log)
        ea = end_activities.get_end_activities(log)
        dfg_exporter.apply(dfg, os.path.join("test_output_data", "running-example.dfg"),
                           parameters={dfg_exporter.Variants.CLASSIC.value.Parameters.START_ACTIVITIES: sa,
                                       dfg_exporter.Variants.CLASSIC.value.Parameters.END_ACTIVITIES: ea})
        dfg, sa, ea = dfg_importer.apply(os.path.join("test_output_data", "running-example.dfg"))
        os.remove(os.path.join("test_output_data", "running-example.dfg"))

    def test_log_skeleton(self):
        log = xes_importer.apply(os.path.join("input_data", "receipt.xes"))
        skeleton = lsk_alg.apply(log)
        conf_res = lsk_conf_alg.apply(log, skeleton)

    def test_performance_spectrum_log(self):
        log = xes_importer.apply(os.path.join("input_data", "receipt.xes"))
        pspectr = log_pspectrum.apply(log, ["T02 Check confirmation of receipt", "T03 Adjust confirmation of receipt"],
                                      1000, {})

    def test_performance_spectrum_df(self):
        df = pd.read_csv(os.path.join("input_data", "receipt.csv"))
        df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format="ISO8601")
        pspectr = df_pspectrum.apply(df, ["T02 Check confirmation of receipt", "T03 Adjust confirmation of receipt"],
                                     1000, {})

    def test_alignment(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        from pm4py.algo.discovery.alpha import algorithm as alpha_miner
        net, im, fm = alpha_miner.apply(log)
        from pm4py.algo.conformance.alignments.petri_net import algorithm as alignments
        aligned_traces = alignments.apply(log, net, im, fm, variant=alignments.Variants.VERSION_STATE_EQUATION_A_STAR)
        aligned_traces = alignments.apply(log, net, im, fm, variant=alignments.Variants.VERSION_DIJKSTRA_NO_HEURISTICS)

    def test_import_export_ptml(self):
        tree = ptree_importer.apply(os.path.join("input_data", "running-example.ptml"))
        ptree_exporter.apply(tree, os.path.join("test_output_data", "running-example2.ptml"))
        os.remove(os.path.join("test_output_data", "running-example2.ptml"))

    def test_footprints_net(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        from pm4py.algo.discovery.alpha import algorithm as alpha_miner
        net, im, fm = alpha_miner.apply(log)
        from pm4py.algo.discovery.footprints import algorithm as footprints_discovery
        fp_entire_log = footprints_discovery.apply(log, variant=footprints_discovery.Variants.ENTIRE_EVENT_LOG)
        fp_trace_trace = footprints_discovery.apply(log)
        fp_net = footprints_discovery.apply(net, im)
        from pm4py.algo.conformance.footprints import algorithm as footprints_conformance
        conf1 = footprints_conformance.apply(fp_entire_log, fp_net)
        conf2 = footprints_conformance.apply(fp_trace_trace, fp_net)
        conf3 = footprints_conformance.apply(fp_entire_log, fp_net,
                                             variant=footprints_conformance.Variants.LOG_EXTENSIVE)
        conf4 = footprints_conformance.apply(fp_trace_trace, fp_net,
                                             variant=footprints_conformance.Variants.TRACE_EXTENSIVE)

    def test_footprints_tree(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        from pm4py.algo.discovery.inductive import algorithm as inductive_miner
        tree = inductive_miner.apply(log)
        from pm4py.algo.discovery.footprints import algorithm as footprints_discovery
        fp_entire_log = footprints_discovery.apply(log, variant=footprints_discovery.Variants.ENTIRE_EVENT_LOG)
        fp_trace_trace = footprints_discovery.apply(log)
        fp_tree = footprints_discovery.apply(tree)
        from pm4py.algo.conformance.footprints import algorithm as footprints_conformance
        conf1 = footprints_conformance.apply(fp_entire_log, fp_tree)
        conf2 = footprints_conformance.apply(fp_trace_trace, fp_tree)
        conf3 = footprints_conformance.apply(fp_entire_log, fp_tree,
                                             variant=footprints_conformance.Variants.LOG_EXTENSIVE)
        conf4 = footprints_conformance.apply(fp_trace_trace, fp_tree,
                                             variant=footprints_conformance.Variants.TRACE_EXTENSIVE)

    def test_footprints_tree_df(self):
        df = pd.read_csv(os.path.join("input_data", "running-example.csv"))
        df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format="ISO8601")
        from pm4py.algo.discovery.inductive import algorithm as inductive_miner
        log = converter.apply(df, variant=converter.Variants.TO_EVENT_LOG)
        tree = inductive_miner.apply(log)
        from pm4py.algo.discovery.footprints import algorithm as footprints_discovery
        fp_df = footprints_discovery.apply(df)
        fp_tree = footprints_discovery.apply(tree)
        from pm4py.algo.conformance.footprints import algorithm as footprints_conformance
        conf = footprints_conformance.apply(fp_df, fp_tree)

    def test_conversion_pn_to_pt(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        from pm4py.algo.discovery.alpha import algorithm as alpha_miner
        net, im, fm = alpha_miner.apply(log)
        from pm4py.objects.conversion.wf_net import converter as wf_net_converter
        tree = wf_net_converter.apply(net, im, fm, variant=wf_net_converter.Variants.TO_PROCESS_TREE)

    def test_playout_tree_basic(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        from pm4py.algo.discovery.inductive import algorithm as inductive_miner
        tree = inductive_miner.apply(log)
        from pm4py.algo.simulation.playout.process_tree import algorithm as tree_playout
        new_log = tree_playout.apply(tree)

    def test_playout_tree_extensive(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        from pm4py.algo.discovery.inductive import algorithm as inductive_miner
        tree = inductive_miner.apply(log)
        from pm4py.algo.simulation.playout.process_tree import algorithm as tree_playout
        new_log = tree_playout.apply(tree, variant=tree_playout.Variants.EXTENSIVE)

    def test_sojourn_time_xes(self):
        log = xes_importer.apply(os.path.join("input_data", "interval_event_log.xes"))
        from pm4py.statistics.sojourn_time.log import get
        soj_time = get.apply(log, parameters={get.Parameters.START_TIMESTAMP_KEY: "start_timestamp"})

    def test_sojourn_time_pandas(self):
        import pandas as pd
        dataframe = pd.read_csv(os.path.join("input_data", "interval_event_log.csv"))
        from pm4py.objects.log.util import dataframe_utils
        dataframe = dataframe_utils.convert_timestamp_columns_in_df(dataframe, timest_format="ISO8601")
        from pm4py.statistics.sojourn_time.pandas import get
        soj_time = get.apply(dataframe, parameters={get.Parameters.START_TIMESTAMP_KEY: "start_timestamp"})

    def test_concurrent_activities_xes(self):
        log = xes_importer.apply(os.path.join("input_data", "interval_event_log.xes"))
        from pm4py.statistics.concurrent_activities.log import get
        conc_act = get.apply(log, parameters={get.Parameters.START_TIMESTAMP_KEY: "start_timestamp"})

    def test_concurrent_activities_pandas(self):
        import pandas as pd
        dataframe = pd.read_csv(os.path.join("input_data", "interval_event_log.csv"))
        from pm4py.objects.log.util import dataframe_utils
        dataframe = dataframe_utils.convert_timestamp_columns_in_df(dataframe, timest_format="ISO8601")
        from pm4py.statistics.concurrent_activities.pandas import get
        conc_act = get.apply(dataframe, parameters={get.Parameters.START_TIMESTAMP_KEY: "start_timestamp"})

    def test_efg_xes(self):
        log = xes_importer.apply(os.path.join("input_data", "interval_event_log.xes"))
        from pm4py.statistics.eventually_follows.log import get
        efg = get.apply(log, parameters={get.Parameters.START_TIMESTAMP_KEY: "start_timestamp"})

    def test_efg_pandas(self):
        import pandas as pd
        dataframe = pd.read_csv(os.path.join("input_data", "interval_event_log.csv"))
        from pm4py.objects.log.util import dataframe_utils
        dataframe = dataframe_utils.convert_timestamp_columns_in_df(dataframe, timest_format="ISO8601")
        from pm4py.statistics.eventually_follows.pandas import get
        efg = get.apply(dataframe, parameters={get.Parameters.START_TIMESTAMP_KEY: "start_timestamp"})

    def test_dfg_playout(self):
        import pm4py
        from pm4py.algo.simulation.playout.dfg import algorithm as dfg_playout
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        dfg, sa, ea = pm4py.discover_dfg(log)
        dfg_playout.apply(dfg, sa, ea)

    def test_dfg_align(self):
        import pm4py
        from pm4py.algo.filtering.dfg import dfg_filtering
        from pm4py.algo.conformance.alignments.dfg import algorithm as dfg_alignment
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        dfg, sa, ea = pm4py.discover_dfg(log)
        act_count = pm4py.get_event_attribute_values(log, "concept:name")
        dfg, sa, ea, act_count = dfg_filtering.filter_dfg_on_activities_percentage(dfg, sa, ea, act_count, 0.5)
        dfg, sa, ea, act_count = dfg_filtering.filter_dfg_on_paths_percentage(dfg, sa, ea, act_count, 0.5)
        aligned_traces = dfg_alignment.apply(log, dfg, sa, ea)

    def test_insert_idx_in_trace(self):
        df = pd.read_csv(os.path.join("input_data", "running-example.csv"))
        df = pandas_utils.insert_ev_in_tr_index(df)

    def test_automatic_feature_extraction(self):
        df = pd.read_csv(os.path.join("input_data", "receipt.csv"))
        fea_df = dataframe_utils.automatic_feature_extraction_df(df)

    def test_log_to_trie(self):
        import pm4py
        from pm4py.algo.transformation.log_to_trie import algorithm as log_to_trie
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        trie = log_to_trie.apply(log)

    def test_minimum_self_distance(self):
        import pm4py
        from pm4py.algo.discovery.minimum_self_distance import algorithm as minimum_self_distance
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        msd = minimum_self_distance.apply(log)

    def test_lp_solver(self):
        import pm4py
        if "cvxopt" not in pm4py.util.lp.solver.DEFAULT_LP_SOLVER_VARIANT:
            raise Exception("cvxopt is not the solver")

    def test_projection_univariate_log(self):
        import pm4py
        from pm4py.util.compression import util as compression_util
        log = pm4py.read_xes(os.path.join("input_data", "receipt.xes"))
        cl = compression_util.project_univariate(log, "concept:name")
        # just verify that the set is non-empty
        self.assertTrue(compression_util.get_start_activities(cl))
        self.assertTrue(compression_util.get_end_activities(cl))
        self.assertTrue(compression_util.get_alphabet(cl))
        self.assertTrue(compression_util.discover_dfg(cl))
        self.assertTrue(compression_util.get_variants(cl))

    def test_projection_univariate_df(self):
        import pandas as pd
        from pm4py.util.compression import util as compression_util
        dataframe = pd.read_csv(os.path.join("input_data", "receipt.csv"))
        dataframe["time:timestamp"] = pd.to_datetime(dataframe["time:timestamp"], utc=True, format="ISO8601")
        cl = compression_util.project_univariate(dataframe, "concept:name")
        # just verify that the set is non-empty
        self.assertTrue(compression_util.get_start_activities(cl))
        self.assertTrue(compression_util.get_end_activities(cl))
        self.assertTrue(compression_util.get_alphabet(cl))
        self.assertTrue(compression_util.discover_dfg(cl))
        self.assertTrue(compression_util.get_variants(cl))

    def test_compression_univariate_log(self):
        import pm4py
        from pm4py.util.compression import util as compression_util
        log = pm4py.read_xes(os.path.join("input_data", "receipt.xes"))
        cl, lookup = compression_util.compress_univariate(log, "concept:name")
        # just verify that the set is non-empty
        self.assertTrue(compression_util.get_start_activities(cl))
        self.assertTrue(compression_util.get_end_activities(cl))
        self.assertTrue(compression_util.get_alphabet(cl))
        self.assertTrue(compression_util.discover_dfg(cl))
        self.assertTrue(compression_util.get_variants(cl))

    def test_compression_univariate_df(self):
        import pandas as pd
        from pm4py.util.compression import util as compression_util
        dataframe = pd.read_csv(os.path.join("input_data", "receipt.csv"))
        dataframe["time:timestamp"] = pd.to_datetime(dataframe["time:timestamp"], utc=True, format="ISO8601")
        cl, lookup = compression_util.compress_univariate(dataframe, "concept:name")
        # just verify that the set is non-empty
        self.assertTrue(compression_util.get_start_activities(cl))
        self.assertTrue(compression_util.get_end_activities(cl))
        self.assertTrue(compression_util.get_alphabet(cl))
        self.assertTrue(compression_util.discover_dfg(cl))
        self.assertTrue(compression_util.get_variants(cl))

    def test_compression_multivariate_log(self):
        import pm4py
        from pm4py.util.compression import util as compression_util
        log = pm4py.read_xes(os.path.join("input_data", "receipt.xes"))
        cl, lookup = compression_util.compress_multivariate(log, ["concept:name", "org:resource"])
        # just verify that the set is non-empty
        self.assertTrue(compression_util.get_start_activities(cl))
        self.assertTrue(compression_util.get_end_activities(cl))
        self.assertTrue(compression_util.get_alphabet(cl))
        self.assertTrue(compression_util.discover_dfg(cl))
        self.assertTrue(compression_util.get_variants(cl))

    def test_compression_multivariate_df(self):
        import pandas as pd
        from pm4py.util.compression import util as compression_util
        dataframe = pd.read_csv(os.path.join("input_data", "receipt.csv"))
        dataframe["time:timestamp"] = pd.to_datetime(dataframe["time:timestamp"], utc=True, format="ISO8601")
        cl, lookup = compression_util.compress_multivariate(dataframe, ["concept:name", "org:resource"])
        # just verify that the set is non-empty
        self.assertTrue(compression_util.get_start_activities(cl))
        self.assertTrue(compression_util.get_end_activities(cl))
        self.assertTrue(compression_util.get_alphabet(cl))
        self.assertTrue(compression_util.discover_dfg(cl))
        self.assertTrue(compression_util.get_variants(cl))

    def test_log_to_target_rem_time(self):
        import pm4py
        from pm4py.algo.transformation.log_to_target import algorithm as log_to_target
        log = pm4py.read_xes("input_data/running-example.xes")
        rem_time_target, classes = log_to_target.apply(log, variant=log_to_target.Variants.REMAINING_TIME)

    def test_log_to_target_next_time(self):
        import pm4py
        from pm4py.algo.transformation.log_to_target import algorithm as log_to_target
        log = pm4py.read_xes("input_data/running-example.xes")
        next_time_target, classes = log_to_target.apply(log, variant=log_to_target.Variants.NEXT_TIME)

    def test_log_to_target_next_activity(self):
        import pm4py
        from pm4py.algo.transformation.log_to_target import algorithm as log_to_target
        log = pm4py.read_xes("input_data/running-example.xes")
        next_activity_target, next_activities = log_to_target.apply(log, variant=log_to_target.Variants.NEXT_ACTIVITY)

    def test_ocel_split_cc_non_simpl_interface(self):
        import pm4py
        ocel = pm4py.read_ocel("input_data/ocel/example_log.jsonocel")
        from pm4py.algo.transformation.ocel.split_ocel import algorithm as split_ocel
        res = split_ocel.apply(ocel, variant=split_ocel.Variants.CONNECTED_COMPONENTS)

    def test_ocel_split_ancestors_non_simpl_interface(self):
        import pm4py
        ocel = pm4py.read_ocel("input_data/ocel/example_log.jsonocel")
        from pm4py.algo.transformation.ocel.split_ocel import algorithm as split_ocel
        res = split_ocel.apply(ocel, parameters={"object_type": "order"}, variant=split_ocel.Variants.ANCESTORS_DESCENDANTS)

    def test_ocel_object_features_non_simpl_interface(self):
        import pm4py
        ocel = pm4py.read_ocel("input_data/ocel/example_log.jsonocel")
        from pm4py.algo.transformation.ocel.features.objects import algorithm as ocel_fea
        res = ocel_fea.apply(ocel)

    def test_ocel_event_features_non_simpl_interface(self):
        import pm4py
        ocel = pm4py.read_ocel("input_data/ocel/example_log.jsonocel")
        from pm4py.algo.transformation.ocel.features.events import algorithm as ocel_fea
        res = ocel_fea.apply(ocel)

    def test_ocel_event_object_features_non_simpl_interface(self):
        import pm4py
        ocel = pm4py.read_ocel("input_data/ocel/example_log.jsonocel")
        from pm4py.algo.transformation.ocel.features.events_objects import algorithm as ocel_fea
        res = ocel_fea.apply(ocel)

    def test_ocel_interaction_graph_non_simpl_interface(self):
        import pm4py
        ocel = pm4py.read_ocel("input_data/ocel/example_log.jsonocel")
        from pm4py.algo.transformation.ocel.graphs import object_interaction_graph
        object_interaction_graph.apply(ocel)

    def test_ocel_descendants_graph_non_simpl_interface(self):
        import pm4py
        ocel = pm4py.read_ocel("input_data/ocel/example_log.jsonocel")
        from pm4py.algo.transformation.ocel.graphs import object_descendants_graph
        object_descendants_graph.apply(ocel)

    def test_ocel_inheritance_graph_non_simpl_interface(self):
        import pm4py
        ocel = pm4py.read_ocel("input_data/ocel/example_log.jsonocel")
        from pm4py.algo.transformation.ocel.graphs import object_inheritance_graph
        object_inheritance_graph.apply(ocel)

    def test_ocel_cobirth_graph_non_simpl_interface(self):
        import pm4py
        ocel = pm4py.read_ocel("input_data/ocel/example_log.jsonocel")
        from pm4py.algo.transformation.ocel.graphs import object_cobirth_graph
        object_cobirth_graph.apply(ocel)

    def test_ocel_codeath_graph_non_simpl_interface(self):
        import pm4py
        ocel = pm4py.read_ocel("input_data/ocel/example_log.jsonocel")
        from pm4py.algo.transformation.ocel.graphs import object_codeath_graph
        object_codeath_graph.apply(ocel)

    def test_ocel_description_non_simpl_interface(self):
        import pm4py
        ocel = pm4py.read_ocel("input_data/ocel/example_log.jsonocel")
        from pm4py.algo.transformation.ocel.description.variants import variant1
        variant1.apply(ocel)


if __name__ == "__main__":
    unittest.main()
