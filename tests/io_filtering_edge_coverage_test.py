import datetime
import gzip
import importlib
import importlib.util
import os
import random
import tempfile
import unittest
import warnings
from unittest import mock

import pandas as pd

from pm4py.objects.log.obj import Event, EventLog, EventStream, Trace


class IoFilteringEdgeCoverageTest(unittest.TestCase):
    """Round-trip and boundary tests for alternate I/O and filtering paths."""

    @staticmethod
    def _frame():
        start = pd.Timestamp("2024-01-01T08:00:00Z")
        return pd.DataFrame(
            {
                "case:concept:name": ["c1", "c1", "c1", "c2", "c2", "c3"],
                "concept:name": ["A", "B", "C", "A", "C", "X"],
                "time:timestamp": [
                    start,
                    start + pd.Timedelta(minutes=1),
                    start + pd.Timedelta(minutes=2),
                    start,
                    start + pd.Timedelta(minutes=3),
                    start,
                ],
            }
        )

    @staticmethod
    def _rich_log():
        log = EventLog(
            attributes={"creator": "coverage", "number": 7},
            extensions={
                "Concept": {
                    "prefix": "concept",
                    "uri": "http://www.xes-standard.org/concept.xesext",
                },
                None: {"prefix": None, "uri": None},
            },
            omni_present={"trace": {"concept:name": "unknown"}},
            classifiers={
                "Activity classifier": ["concept:name"],
                "Spaced classifier": ["concept:name", "custom key"],
            },
        )
        trace = Trace(
            attributes={
                "concept:name": "case-1",
                "nested-list": {
                    "value": None,
                    "children": [("child", "one"), ("count", 2)],
                },
                "nested-value": {
                    "value": "root",
                    "children": {"child": "two"},
                },
            }
        )
        trace.append(
            Event(
                {
                    "concept:name": "A",
                    "custom key": "alpha",
                    "time:timestamp": datetime.datetime(
                        2024, 1, 1, 8, 0, tzinfo=datetime.timezone.utc
                    ),
                    "integer": 3,
                    "floating": 2.5,
                    "boolean": True,
                }
            )
        )
        trace.append(Event({"concept:name": "B", "custom key": "beta"}))
        log.append(trace)
        return log

    @staticmethod
    def _streaming_xes():
        return b"""<?xml version="1.0" encoding="UTF-8" ?>
<log xmlns="http://www.xes-standard.org/">
  <trace>
    <string key="concept:name" value="accepted" />
    <string key="container" value="root"><string key="child" value="value" /></string>
    <list key="items"><values><string key="item" value="one" /></values></list>
    <event>
      <string key="concept:name" value="A" />
      <date key="good-date" value="2024-01-01T08:00:00+00:00" />
      <date key="bad-date" value="not-a-date" />
      <float key="good-float" value="2.5" />
      <float key="bad-float" value="bad" />
      <int key="good-int" value="3" />
      <int key="bad-int" value="bad" />
      <boolean key="truth" value="true" />
      <boolean key="falsehood" value="false" />
      <id key="identity" value="id-1" />
      <list key="event-items"><values><string key="entry" value="x" /></values></list>
    </event>
  </trace>
  <trace><string key="concept:name" value="rejected" /><event><string key="concept:name" value="B" /></event></trace>
</log>"""

    def test_rich_xes_etree_chunk_and_line_round_trips(self):
        from pm4py.objects.log.exporter.xes.variants import etree_xes_exp
        from pm4py.objects.log.importer.xes.variants import chunk_regex, line_by_line

        log = self._rich_log()
        raw = etree_xes_exp.export_log_as_string(log, {"show_progress_bar": False})
        compressed = etree_xes_exp.export_log_as_string(
            log, {"compress": True, "show_progress_bar": False}
        )
        self.assertTrue(raw.startswith(b"<?xml"))
        self.assertEqual(b"<?xml", gzip.decompress(compressed)[:5])
        self.assertEqual(1, len(chunk_regex.import_from_string(raw)))
        self.assertEqual(
            1,
            len(
                chunk_regex.import_from_string(
                    compressed, {chunk_regex.Parameters.DECOMPRESS_SERIALIZATION: True}
                )
            ),
        )
        self.assertEqual(1, len(line_by_line.import_from_string(raw)))
        self.assertEqual(
            1,
            len(
                line_by_line.import_from_string(
                    compressed, {line_by_line.Parameters.DECOMPRESS_SERIALIZATION: True}
                )
            ),
        )

        stream = EventStream(
            [
                Event({"case:concept:name": "s1", "concept:name": "A"}),
                Event({"case:concept:name": "s1", "concept:name": "B"}),
            ]
        )
        self.assertEqual(
            1,
            len(etree_xes_exp.export_log_tree(stream, {"show_progress_bar": False}).getroot()),
        )

        with tempfile.TemporaryDirectory() as directory:
            plain = os.path.join(directory, "log.xes")
            etree_xes_exp.apply(log, plain, {"show_progress_bar": False})
            self.assertEqual(1, len(chunk_regex.apply(plain)))
            self.assertEqual(1, len(line_by_line.apply(plain)))

            compressed_base = os.path.join(directory, "compressed")
            etree_xes_exp.apply(
                log,
                compressed_base,
                {"compress": True, "show_progress_bar": False},
            )
            compressed_path = compressed_base + ".gz"
            self.assertTrue(os.path.exists(compressed_path))
            self.assertEqual(1, len(chunk_regex.apply(compressed_path)))
            self.assertEqual(1, len(line_by_line.apply(compressed_path)))

    def test_streaming_trace_and_event_readers_with_nested_values(self):
        from pm4py.streaming.importer.xes.variants import xes_event_stream, xes_trace_stream

        with tempfile.NamedTemporaryFile(suffix=".xes") as xes_file:
            xes_file.write(self._streaming_xes())
            xes_file.flush()

            trace_reader = xes_trace_stream.apply(
                xes_file.name,
                {"acceptance_condition": lambda trace: trace.attributes.get("concept:name") == "accepted"},
            )
            traces = []
            trace_reader.to_trace_stream(traces)
            self.assertEqual(1, len(traces))
            self.assertEqual("A", traces[0][0]["concept:name"])
            self.assertTrue(traces[0][0]["truth"])
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", ResourceWarning)
                trace_reader.reset()
            self.assertEqual("accepted", next(trace_reader).attributes["concept:name"])
            self.assertEqual([], list(trace_reader))

            event_reader = xes_event_stream.apply(
                xes_file.name,
                {"acceptance_condition": lambda event: event.get("concept:name") == "A"},
            )
            events = []
            event_reader.to_event_stream(events)
            self.assertEqual(1, len(events))
            self.assertEqual("accepted", events[0]["case:concept:name"])
            self.assertFalse(events[0]["falsehood"])
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", ResourceWarning)
                event_reader.reset()
            self.assertEqual("A", next(event_reader)["concept:name"])
            self.assertEqual([], list(event_reader))

    def test_dataframe_prefix_suffix_end_and_variant_filters(self):
        from pm4py.algo.filtering.pandas.end_activities import end_activities_filter
        from pm4py.algo.filtering.pandas.ends_with import ends_with_filter
        from pm4py.algo.filtering.pandas.starts_with import starts_with_filter
        from pm4py.objects.conversion.log.variants import df_to_event_log_nv

        frame = self._frame()
        frame.attrs["source"] = "fixture"
        self.assertEqual(5, len(starts_with_filter.apply(frame, [("A",)])))
        self.assertEqual(1, len(starts_with_filter.apply(frame, [("A",)], {"positive": False})))
        self.assertEqual(5, len(ends_with_filter.apply(frame, [("C",)])))
        self.assertEqual(1, len(ends_with_filter.apply(frame, [("C",)], {"positive": False})))

        empty_variants = pd.DataFrame(columns=["variant"])
        self.assertTrue(
            starts_with_filter.apply(frame, ["A"], {"variants_df": empty_variants}).empty
        )
        self.assertEqual(
            len(frame),
            len(ends_with_filter.apply(frame, ["A"], {"variants_df": empty_variants, "positive": False})),
        )

        grouped = frame.groupby("case:concept:name", sort=False)
        self.assertEqual(
            5,
            len(
                end_activities_filter.apply(
                    frame,
                    ["C"],
                    {"grouped_dataframe": grouped},
                )
            ),
        )
        self.assertEqual(1, len(end_activities_filter.apply(frame, ["C"], {"positive": False})))
        reduced, counts = end_activities_filter.filter_df_on_end_activities_nocc(
            frame,
            2,
            ea_count0={"C": 2, "X": 1},
            grouped_df=grouped,
            return_dict=True,
        )
        self.assertEqual(5, len(reduced))
        self.assertEqual({"C": 2}, counts)
        unchanged, kept_counts = end_activities_filter.filter_df_on_end_activities_nocc(
            frame, 1, return_dict=True, most_common_variant=("A", "C")
        )
        self.assertEqual(len(frame), len(unchanged))
        self.assertIn("C", kept_counts)
        self.assertTrue(end_activities_filter.filter_df_on_end_activities_nocc(frame.iloc[0:0], 1).empty)

        converted, variants = df_to_event_log_nv.apply(frame, {"return_variants": True})
        self.assertEqual(3, len(converted))
        self.assertEqual(3, sum(len(indices) for indices in variants.values()))
        self.assertEqual(3, len(df_to_event_log_nv.apply(frame)))

    def test_classifier_helpers_and_higher_order_log_functions(self):
        import pm4py.hof as hof
        from pm4py.objects.log.util import insert_classifier

        log = EventLog(
            [
                Trace(
                    [
                        Event({"concept:name": "B", "lifecycle:transition": "complete"}),
                        Event({"concept:name": "A", "lifecycle:transition": "start"}),
                    ],
                    attributes={"customer": "gold"},
                )
            ],
            classifiers={
                "Activity classifier": ["concept:name", "lifecycle:transition"],
                "Trace classifier": ["customer"],
            },
        )
        classified, key = insert_classifier.search_act_class_attr(log)
        self.assertEqual("@@classifier", key)
        self.assertEqual("B+complete", classified[0][0][key])
        _, trace_key = insert_classifier.insert_trace_classifier_attribute(log, "Trace classifier")
        self.assertEqual("gold", log[0].attributes[trace_key])

        legacy = EventLog(
            [Trace([Event({"concept:name": "A"})])],
            classifiers={"MXML Legacy Classifier": ["concept:name"]},
        )
        self.assertEqual("@@classifier", insert_classifier.search_act_class_attr(legacy)[1])
        forced = EventLog([Trace([Event({"concept:name": "A", "lifecycle:transition": "complete"})])])
        self.assertEqual(
            "@@classifier",
            insert_classifier.search_act_class_attr(forced, force_activity_transition_insertion=True)[1],
        )
        self.assertIsNone(insert_classifier.insert_trace_classifier_attribute(log, None)[1])

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.assertEqual(1, len(hof.filter_log(lambda trace: len(trace) == 2, log)))
            stream = EventStream([Event({"v": 2}), Event({"v": 1})])
            self.assertEqual(1, len(hof.filter_log(lambda event: event["v"] == 1, stream)))
            self.assertEqual(1, len(hof.filter_trace(lambda event: event["concept:name"] == "A", log[0])))
            self.assertEqual("A", hof.sort_trace(log[0], key=lambda event: event["concept:name"])[0]["concept:name"])
            self.assertEqual(1, hof.sort_log(stream, key=lambda event: event["v"])[0]["v"])
            with mock.patch.object(hof.constants, "SHOW_INTERNAL_WARNINGS", True):
                self.assertEqual([1, 2], hof.filter_log(lambda x: True, [1, 2]))
                self.assertEqual([2, 1], hof.sort_log([2, 1], key=lambda x: x))
                self.assertEqual([1], hof.filter_trace(lambda x: True, [1]))
                self.assertEqual([1], hof.sort_trace([1], key=lambda x: x))

    def test_variant_and_transition_system_utilities(self):
        from pm4py.objects.transition_system import obj, utils
        from pm4py.util import variants_util

        trace = variants_util.variant_to_trace("A,B,B,C")
        self.assertEqual(("A", "B", "B", "C"), variants_util.get_variant_from_trace(trace))
        self.assertEqual(("A", "B"), variants_util.get_activities_from_variant(["A", "B"]))
        aggregated = variants_util.aggregate_consecutive_activities_in_variants(
            {("A", "B", "B", "C"): 2, ("A", "B", "C"): 1}, 1
        )
        self.assertEqual({("A", "B", "C"): 3}, aggregated)
        listed = variants_util.aggregate_consecutive_activities_in_variants(
            {("A", "A"): [0], ("A",): [1]}, 1
        )
        self.assertEqual([0, 1], listed[("A",)])

        ts = obj.TransitionSystem("ts")
        a, b, c = (obj.TransitionSystem.State(name) for name in ("a", "b", "c"))
        ts.states.update({a, b, c})
        utils.add_arc_from_to("ab", a, b, ts, {"weight": 1})
        utils.add_arc_from_to("bc", b, c, ts)
        utils.add_arc_from_to("ac", a, c, ts)
        self.assertEqual(ts, obj.TransitionSystem("ts", {a, b, c}, set(ts.transitions)))
        self.assertNotEqual(ts, object())
        self.assertTrue(hash(ts))
        utils.transitive_reduction(ts)
        self.assertFalse(any(t.name == "ac" for t in ts.transitions))
        utils.remove_arc_from_to("ab", a, b, ts)
        self.assertFalse(any(t.name == "ab" for t in ts.transitions))
        a.name, a.data = "renamed", {"x": 1}
        self.assertEqual(("renamed", {"x": 1}), (a.name, a.data))

    def test_ocel_sampling_features_statistics_and_conversion(self):
        import pm4py
        from pm4py.algo.transformation.ocel.features.events import event_str_attributes
        from pm4py.algo.transformation.ocel.features.objects import object_str_attributes
        from pm4py.objects.conversion.ocel.variants import ocel_features_to_nx
        from pm4py.objects.ocel.util import (
            ev_att_to_obj_type,
            events_per_type_per_activity,
            objects_per_type_per_activity,
            ocel_type_renaming,
            sampling,
        )

        path = os.path.join(os.path.dirname(__file__), "input_data", "ocel", "example_log.jsonocel")
        ocel = pm4py.read_ocel(path)
        ocel.events["segment"] = ["premium" if i % 2 else "standard" for i in range(len(ocel.events))]
        ocel.objects["region"] = ["north" if i % 2 else "south" for i in range(len(ocel.objects))]

        event_data, event_names = event_str_attributes.apply(ocel, {"str_ev_attr": ["segment"]})
        object_data, object_names = object_str_attributes.apply(ocel, {"str_obj_attr": ["region"]})
        self.assertEqual(len(ocel.events), len(event_data))
        self.assertEqual(len(ocel.objects), len(object_data))
        self.assertTrue(event_names and object_names)
        self.assertTrue(events_per_type_per_activity.apply(ocel))
        self.assertTrue(objects_per_type_per_activity.apply(ocel))

        random.seed(7)
        self.assertLessEqual(len(sampling.sample_ocel_events(ocel, {"num_entities": 2}).events), 2)
        self.assertLessEqual(len(sampling.sample_ocel_objects(ocel, {"num_entities": 2}).objects), 2)
        self.assertFalse(ocel_type_renaming.abbreviate_event_types(ocel).events.empty)
        self.assertFalse(
            ocel_type_renaming.remove_spaces_non_alphanumeric_characters_from_types(ocel).objects.empty
        )
        moved = ev_att_to_obj_type.apply(ocel, "segment")
        self.assertNotIn("segment", moved.events.columns)
        self.assertIn("segment", set(moved.objects[moved.object_type_column]))

        graph = ocel_features_to_nx.apply(ocel)
        self.assertGreaterEqual(graph.number_of_nodes(), 1)
        empty_graph = ocel_features_to_nx.apply(
            ocel,
            {
                "include_obj_interaction_graph": False,
                "include_obj_descendants_graph": False,
                "include_obj_inheritance_graph": False,
                "include_obj_cobirth_graph": False,
                "include_obj_codeath_graph": False,
            },
        )
        self.assertEqual(0, empty_graph.number_of_edges())

    @unittest.skipUnless(
        importlib.util.find_spec("polars"), "polars is not installed"
    )
    def test_clean_dfg_polars_rework_passed_time_and_alignment_decoration(self):
        import polars as pl
        from pm4py.algo.discovery.dfg.variants import clean, clean_polars
        from pm4py.statistics.passed_time.pandas.variants import post, pre
        from pm4py.visualization.petri_net.util import alignments_decoration
        from pm4py.objects.petri_net.obj import Marking, PetriNet
        from pm4py.objects.petri_net.utils import petri_utils

        frame = self._frame()
        dfg = clean.apply(frame)
        self.assertEqual({"A": 2, "X": 1}, dict(dfg.start_activities))
        self.assertEqual(2, len(pre.apply(frame, "C")["pre"]))
        self.assertEqual(2, len(post.apply(frame, "A")["post"]))

        polars_rework = importlib.import_module(
            "pm4py.statistics.rework.cases.polars.get"
        )
        lazy = pl.from_pandas(frame).lazy()
        rework = polars_rework.apply(lazy)
        self.assertEqual(0, rework["c1"]["rework"])
        polars_dfg = clean_polars.apply(pl.from_pandas(frame))
        self.assertEqual(dict(dfg.start_activities), dict(polars_dfg.start_activities))
        self.assertEqual(dict(dfg.end_activities), dict(polars_dfg.end_activities))

        net = PetriNet("decorated")
        source, sink = PetriNet.Place("source"), PetriNet.Place("sink")
        visible = PetriNet.Transition("visible", "A")
        silent = PetriNet.Transition("silent", None)
        net.places.update({source, sink})
        net.transitions.update({visible, silent})
        petri_utils.add_arc_from_to(source, visible, net)
        petri_utils.add_arc_from_to(visible, sink, net)
        decorations = alignments_decoration.get_alignments_decoration(
            net,
            Marking({source: 1}),
            Marking({sink: 1}),
            aligned_traces=[
                {"alignment": [(("A", "visible"), ("A", "A")), ((">>", "visible"), (">>", "A"))]},
                {"alignment": [((">>", "silent"), (">>", None))]},
            ],
        )
        self.assertEqual(1, decorations[visible]["count_fit"])
        self.assertEqual(1, decorations[visible]["count_move_on_model"])
        self.assertIn("color", decorations[visible])


if __name__ == "__main__":
    unittest.main()
