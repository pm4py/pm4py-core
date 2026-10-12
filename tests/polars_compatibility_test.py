"""Regression checks shared by Polars 1.40.1 and 2.0, including streaming queries."""

import datetime
import importlib.util
import unittest
import warnings

POLARS_AVAILABLE = importlib.util.find_spec("polars") is not None
if POLARS_AVAILABLE:
    import polars as pl

    import pm4py
    from pm4py.algo.discovery.dfg.adapters.polars import df_statistics, freq_triples
    from pm4py.algo.discovery.dfg.variants import clean_polars
    from pm4py.algo.filtering.polars.attributes import attributes_filter
    from pm4py.algo.filtering.polars.cases import case_filter
    from pm4py.algo.filtering.polars.consecutive_act_case_grouping import (
        consecutive_act_case_grouping_filter,
    )
    from pm4py.algo.filtering.polars.end_activities import end_activities_filter
    from pm4py.algo.filtering.polars.start_activities import start_activities_filter
    from pm4py.algo.filtering.polars.variants import variants_filter
    from pm4py.objects.log.util import pl_lazy_extra_utils, pl_lazy_fea_utils
    from pm4py.statistics.attributes.polars import get as attributes_get
    from pm4py.statistics.eventually_follows.polars import get as eventually_follows
    from pm4py.statistics.process_cube.polars.variants import classic as process_cube
    from pm4py.statistics.variants.polars import get as variants_get
    from pm4py.util import constants, pandas_utils


@unittest.skipUnless(POLARS_AVAILABLE, "polars is not installed")
class TestPolarsCompatibility(unittest.TestCase):
    def setUp(self):
        # The same assertions must hold under both engines, without relying on
        # the incidental ordering of a particular Polars version.
        self.engines = ("auto", "streaming", "in-memory")
        self.warning_context = warnings.catch_warnings()
        self.warning_context.__enter__()
        self.addCleanup(self.warning_context.__exit__, None, None, None)
        warnings.simplefilter("error", DeprecationWarning)
        base = datetime.datetime(2024, 1, 1, tzinfo=datetime.timezone.utc)
        self.df = pl.DataFrame(
            {
                "case:concept:name": ["z", "a", "z", "m", "a", "z", "a", "m"],
                "concept:name": ["B", "A", "A", "X", "B", "C", "C", "Y"],
                "time:timestamp": [
                    base + datetime.timedelta(seconds=i) for i in range(8)
                ],
                "start_timestamp": [
                    base + datetime.timedelta(seconds=i - 1) for i in range(8)
                ],
                "row": list(range(8)),
                "score": [float(i) for i in range(8)],
            }
        )
        self.lazy = self.df.lazy()

    def test_case_filters_preserve_input_event_order(self):
        queries = (
            (
                case_filter.filter_on_case_size(self.lazy, min_case_size=3),
                [0, 1, 2, 4, 5, 6],
            ),
            (attributes_filter.apply(self.lazy, ["B"]), [0, 1, 2, 4, 5, 6]),
            (attributes_filter.apply(self.lazy, ["B"], {"positive": False}), [3, 7]),
            (start_activities_filter.apply(self.lazy, ["A"]), [1, 4, 6]),
            (end_activities_filter.apply(self.lazy, ["Y"]), [3, 7]),
            (variants_filter.apply(self.lazy, [["B", "A", "C"]]), [0, 2, 5]),
        )
        for query, expected in queries:
            for engine in self.engines:
                with self.subTest(engine=engine, expected=expected):
                    self.assertEqual(
                        query.collect(engine=engine)["row"].to_list(), expected
                    )

    def test_enrichment_and_indexes_preserve_input_event_order(self):
        queries = (
            pandas_utils.insert_index(self.lazy),
            pandas_utils.insert_case_index(self.lazy),
            pandas_utils.insert_case_arrival_finish_rate(self.lazy),
            pandas_utils.insert_case_service_waiting_time(self.lazy),
            pl_lazy_extra_utils.compute_extra_columns(self.lazy),
            pm4py.extract_outcome_enriched_dataframe(self.lazy),
        )
        for query in queries:
            for engine in self.engines:
                with self.subTest(
                    engine=engine, columns=query.collect_schema().names()
                ):
                    self.assertEqual(
                        query.collect(engine=engine)["row"].to_list(), list(range(8))
                    )
        indexed = pandas_utils.insert_case_index(self.lazy).collect()
        self.assertEqual(
            indexed[constants.DEFAULT_CASE_INDEX_KEY].to_list(),
            [0, 1, 0, 2, 1, 0, 1, 2],
        )

    def test_format_dataframe_assigns_indexes_in_sorted_event_order(self):
        formatted = pm4py.format_dataframe(self.lazy)
        expected_rows = [1, 4, 6, 3, 7, 0, 2, 5]
        for engine in self.engines:
            with self.subTest(engine=engine):
                frame = formatted.collect(engine=engine)
                self.assertEqual(frame["row"].to_list(), expected_rows)
                self.assertEqual(
                    frame[constants.DEFAULT_INDEX_KEY].to_list(), list(range(8))
                )
                self.assertEqual(
                    frame[constants.DEFAULT_CASE_INDEX_KEY].to_list(),
                    [0, 0, 0, 1, 1, 2, 2, 2],
                )

    def test_frequency_ties_select_the_same_cases_and_activities(self):
        queries = (
            (case_filter.filter_on_ncases(self.lazy, max_no_cases=1), [0, 2, 5]),
            (
                attributes_filter.filter_df_keeping_spno_activities(
                    self.lazy, max_no_activities=1
                ),
                [0, 4],
            ),
            (variants_filter.apply_auto_filter(self.lazy), [0, 2, 3, 5, 7]),
        )
        for query, expected in queries:
            for engine in self.engines:
                with self.subTest(expected=expected, engine=engine):
                    self.assertEqual(
                        query.collect(engine=engine)["row"].to_list(), expected
                    )

    def test_first_following_selects_the_next_event_in_each_case(self):
        query = eventually_follows.get_partial_order_dataframe(
            self.lazy, keep_first_following=True
        )
        expected = [
            ("a", "A", "B"),
            ("a", "B", "C"),
            ("m", "X", "Y"),
            ("z", "B", "A"),
            ("z", "A", "C"),
        ]
        for engine in self.engines:
            with self.subTest(engine=engine):
                pairs = query.select(
                    "case:concept:name", "concept:name", "concept:name_2"
                )
                self.assertEqual(pairs.collect(engine=engine).rows(), expected)

    def test_numeric_membership_accepts_integer_and_float_needles(self):
        cases = (
            (pl.Float64, [1.0, 2.0, 2.5, None], [1, 2], [1.0, 2.0]),
            (pl.Float32, [1.0, 2.0, 2.5, None], {1, 2}, [1.0, 2.0]),
            (pl.Int64, [1, 2, 3, None], [1.0, 2.5], [1]),
            (pl.Int64, [2**53, 2**53 + 1, None], [2**53 + 1], [2**53 + 1]),
            (pl.UInt64, [2**63, 2**63 + 1, None], [2**63 + 1], [2**63 + 1]),
            (pl.Int8, [1, 127, None], [257, 1.0], [1]),
            (pl.Float32, [0.1, None], [0.1], []),
            (pl.Int64, [1, 2, None], [], []),
        )
        for dtype, data, needles, expected in cases:
            frame = pl.DataFrame({"value": pl.Series(data, dtype=dtype)}).lazy()
            for engine in self.engines:
                with self.subTest(dtype=dtype, needles=needles, engine=engine):
                    result = attributes_filter.apply_events(
                        frame, needles, {"pm4py:param:attribute_key": "value"}
                    )
                    self.assertEqual(
                        result.collect(engine=engine)["value"].to_list(), expected
                    )

    def test_numeric_membership_filters_cases_and_negative_events(self):
        expected = {"event": [1, 4], "case": [1, 4, 6]}
        for level in expected:
            for engine in self.engines:
                with self.subTest(level=level, engine=engine):
                    query = pm4py.filter_event_attribute_values(
                        self.lazy, "score", [1, 4], level=level
                    )
                    self.assertEqual(
                        query.collect(engine=engine)["row"].to_list(), expected[level]
                    )
        negative = pm4py.filter_event_attribute_values(
            self.lazy, "score", [1, 4], level="event", retain=False
        )
        self.assertEqual(negative.collect()["row"].to_list(), [0, 2, 3, 5, 6, 7])

    def test_attributes_once_per_case_with_grouping_column_as_attribute(self):
        for function in (
            attributes_get.get_attribute_values,
            attributes_filter.get_attribute_values,
        ):
            with self.subTest(function=function):
                self.assertEqual(
                    function(self.lazy, "concept:name", {"keep_once_per_case": True}),
                    {"A": 2, "B": 2, "C": 2, "X": 1, "Y": 1},
                )
                self.assertEqual(
                    function(
                        self.lazy, "case:concept:name", {"keep_once_per_case": True}
                    ),
                    {"z": 1, "a": 1, "m": 1},
                )

    def test_consecutive_activity_groups_keep_first_or_last_in_event_order(self):
        frame = pl.DataFrame(
            {
                "case:concept:name": ["z"] * 5,
                "concept:name": ["A", "A", "B", "B", "C"],
                "row": list(range(5)),
            }
        ).lazy()
        for mode, expected in (("first", [0, 2, 4]), ("last", [1, 3, 4])):
            query = consecutive_act_case_grouping_filter.apply(
                frame, {"filter_type": mode}
            )
            for engine in self.engines:
                with self.subTest(mode=mode, engine=engine):
                    self.assertEqual(
                        query.collect(engine=engine)["row"].to_list(), expected
                    )

    def test_typed_dfg_has_all_edges_and_case_boundaries(self):
        expected_edges = {
            ("B", "A"): 1,
            ("A", "C"): 1,
            ("A", "B"): 1,
            ("B", "C"): 1,
            ("X", "Y"): 1,
        }
        for frame in (self.df, self.lazy):
            with self.subTest(frame=type(frame)):
                dfg = clean_polars.apply(frame)
                self.assertEqual(dict(dfg.graph), expected_edges)
                self.assertEqual(dict(dfg.start_activities), {"B": 1, "A": 1, "X": 1})
                self.assertEqual(dict(dfg.end_activities), {"C": 2, "Y": 1})
        for frame in (self.df.head(0), self.lazy.limit(0)):
            self.assertFalse(clean_polars.apply(frame).graph)
        singleton = clean_polars.apply(self.df.head(1))
        self.assertEqual(dict(singleton.start_activities), {"B": 1})
        self.assertEqual(dict(singleton.end_activities), {"B": 1})
        self.assertFalse(singleton.graph)

    def test_equal_timestamps_keep_activity_sequence(self):
        tied = self.lazy.with_columns(
            pl.lit(datetime.datetime(2024, 1, 1, tzinfo=datetime.timezone.utc)).alias(
                "time:timestamp"
            )
        ).drop("start_timestamp")
        with pl.Config(engine_affinity="streaming"):
            self.assertEqual(
                variants_get.get_variants_count(tied),
                {("B", "A", "C"): 1, ("A", "B", "C"): 1, ("X", "Y"): 1},
            )
            self.assertEqual(
                df_statistics.get_dfg_graph(tied),
                {
                    ("B", "A"): 1,
                    ("A", "C"): 1,
                    ("A", "B"): 1,
                    ("B", "C"): 1,
                    ("X", "Y"): 1,
                },
            )
            self.assertEqual(
                freq_triples.get_freq_triples(tied),
                {("B", "A", "C"): 1, ("A", "B", "C"): 1},
            )
        for engine in self.engines:
            with self.subTest(engine=engine):
                filtered = variants_filter.apply(tied, [["B", "A", "C"]])
                self.assertEqual(
                    filtered.collect(engine=engine)["row"].to_list(), [0, 2, 5]
                )

    def test_dfg_raw_performance_values(self):
        raw = df_statistics.get_dfg_graph(
            self.lazy, measure="performance", perf_aggregation_key="raw_values"
        )
        self.assertEqual(
            raw,
            {
                ("B", "A"): [1],
                ("A", "C"): [2],
                ("A", "B"): [2],
                ("B", "C"): [1],
                ("X", "Y"): [3],
            },
        )

    def test_numeric_features_keep_first_and_last_from_event_order(self):
        query = pl_lazy_fea_utils.get_features_df(
            self.lazy,
            ["score"],
            {
                "add_case_identifier_column": True,
                "enable_numeric_attribute_statistics": True,
                "numeric_attribute_aggregations": ["first", "last", "stdev"],
            },
        )
        for engine in self.engines:
            with self.subTest(engine=engine):
                features = query.collect(engine=engine)
                self.assertEqual(features["score_FIRST"].to_list(), [1.0, 3.0, 0.0])
                self.assertEqual(features["score_LAST"].to_list(), [6.0, 7.0, 5.0])

    def test_process_cube_reshaping_helpers_and_count(self):
        feature = pl.DataFrame(
            {
                "case:concept:name": ["a", "b"],
                "x": [0.5, 1.5],
                "y": [0.5, 1.5],
                "agg": [1, None],
                "px_a": [1, 0],
                "px_b": [0, 1],
                "py_c": [1, 1],
            }
        )
        reshaped = (
            process_cube._numeric_prefix_case(
                feature, "x", "agg", [0, 1, 2], ["py_c"], "p"
            ),
            process_cube._prefix_numeric_case(
                feature, "y", "agg", [0, 1, 2], ["px_a", "px_b"], "p"
            ),
            process_cube._prefix_prefix_case(
                feature, "agg", ["px_a", "px_b"], ["py_c"]
            ),
        )
        for frame in reshaped:
            self.assertEqual(frame.height, 2)
            self.assertEqual(
                set(frame.columns), {"case:concept:name", "x_bin", "y_bin", "agg"}
            )
        cube, cases = process_cube.apply(
            feature.lazy(), "px", "py", "agg", {"aggregation_function": "count"}
        )
        self.assertEqual(cube["py_c"].to_list(), [1, 1])
        self.assertEqual(len(cases), 2)


if __name__ == "__main__":
    unittest.main()
