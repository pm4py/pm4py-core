import datetime
import importlib.util
import unittest

import pandas as pd

POLARS_AVAILABLE = importlib.util.find_spec("polars") is not None
if POLARS_AVAILABLE:
    import polars as pl

    from pm4py.algo.discovery.dfg.adapters.polars import df_statistics
    from pm4py.algo.discovery.dfg.variants import case_attributes
    from pm4py.algo.discovery.performance_spectrum.variants import (
        lazyframe,
        lazyframe_disconnected,
    )
    from pm4py.algo.filtering.pandas.activity_split import activity_split_filter
    from pm4py.algo.filtering.polars.attributes import attributes_filter
    from pm4py.algo.filtering.polars.ltl import ltl_checker
    from pm4py.algo.filtering.polars.variants import variants_filter
    from pm4py.objects.log.obj import Event, EventLog, Trace
    from pm4py.statistics.attributes.polars import get as attributes_get
    from pm4py.statistics.process_cube.polars.variants import classic as process_cube
    from pm4py.util import constants


@unittest.skipUnless(POLARS_AVAILABLE, "polars is not installed")
class PolarsAnalyticsDeepCoverageTest(unittest.TestCase):
    def setUp(self):
        base = datetime.datetime(2024, 1, 1, 8, tzinfo=datetime.timezone.utc)
        rows = []
        specifications = (
            ("c1", ("A", "B", "C"), ("r1", "r2", "r3")),
            ("c2", ("A", "C", "B"), ("r1", "r1", "r1")),
            ("c3", ("A", "B", "A", "C"), ("r1", "r2", "r3", "r4")),
        )
        index = 0
        for case, activities, resources in specifications:
            for position, (activity, resource) in enumerate(zip(activities, resources)):
                start = base + datetime.timedelta(days=int(case[-1]), seconds=position * 4)
                rows.append(
                    {
                        "case:concept:name": case,
                        "concept:name": activity,
                        "org:resource": resource,
                        "start_timestamp": start,
                        "time:timestamp": start + datetime.timedelta(seconds=3),
                        "cost": float(position + 1),
                        "score": index + 0.5,
                        "category": "even" if position % 2 == 0 else "odd",
                        "@@index": index,
                    }
                )
                index += 1
        self.df = pl.DataFrame(rows)
        self.lazy = self.df.lazy()

    def test_process_cube_helpers_and_all_dimension_kinds(self):
        feature = pl.DataFrame(
            {
                constants.CASE_CONCEPT_NAME: ["c1", "c2", "c3", "c4"],
                "x": [0.0, 1.0, 2.0, 3.0],
                "y": [10.0, 20.0, 30.0, 40.0],
                "constant": [1.0, 1.0, 1.0, 1.0],
                "category": ["one", "two", "one", None],
                "px_a": [1, 0, 1, 0],
                "px_b": [0, 1, 0, 1],
                "py_c": [1, 1, 0, 0],
                "py_d": [0, 0, 1, 1],
                "agg": [1.0, 2.0, 3.0, 4.0],
            }
        )
        self.assertEqual(process_cube._ensure_polars_df(feature).height, 4)
        self.assertEqual(
            process_cube._ensure_polars_df(feature.lazy(), ["x"]).columns, ["x"]
        )
        self.assertEqual(process_cube._available_columns(feature), feature.columns)
        self.assertEqual(process_cube._available_columns(feature.lazy()), feature.columns)
        with self.assertRaises(TypeError):
            process_cube._ensure_polars_df(object())
        with self.assertRaises(TypeError):
            process_cube._available_columns(object())
        self.assertEqual(process_cube._dedupe_columns(["x", "x", "y"]), ["x", "y"])
        self.assertEqual(
            process_cube._dimension_required_columns(feature.columns, "px"),
            ["px_a", "px_b"],
        )
        required = process_cube._required_feature_columns(
            feature.lazy(), ("x", "category"), "py", "agg"
        )
        self.assertIn("py_c", required)
        class NumericLike:
            def __str__(self):
                return "Int128"

        self.assertTrue(process_cube._is_numeric_dtype(NumericLike()))

        self.assertEqual(process_cube._prepare_bins(pl.Series([], dtype=pl.Float64), None, 4), [])
        self.assertEqual(
            process_cube._prepare_bins(feature["constant"], None, 4), [0.5, 1.5]
        )
        self.assertEqual(
            process_cube._prepare_bins(feature["x"], [3, 0, 1], 4), [0.0, 1.0, 3.0]
        )
        self.assertEqual(process_cube._bin_labels([0, 1]), ["[0, 1]"])
        self.assertEqual(process_cube._bin_labels([]), [])
        assigned = process_cube._assign_bins(
            pl.Series(
                "mixed",
                [None, "bad", float("inf"), -1, 0, 3],
                dtype=pl.Object,
                strict=False,
            ),
            [0, 1, 3],
            "bin",
        )
        self.assertEqual(assigned[-1], "[1, 3]")
        self.assertEqual(process_cube._assign_bins(feature["x"], [], "none").null_count(), 4)
        self.assertEqual(process_cube._normalize_agg_fn("AVG"), "mean")
        self.assertEqual(process_cube._normalize_agg_fn(object()), "mean")
        for function in ("sum", "min", "max", "median", "first", "last", "count", "mean"):
            expression = process_cube._aggregation_expression("agg", function)
            self.assertIsInstance(expression, pl.Expr)
        self.assertEqual(process_cube._normalize_dimension("x"), ("x",))
        self.assertEqual(process_cube._normalize_dimension(("x", "y")), ("x", "y"))
        self.assertEqual(process_cube._select_bins_param({"x": [0, 1]}, 0, "x", 1), [0, 1])
        self.assertEqual(process_cube._select_bins_param({0: [0, 2]}, 0, "x", 1), [0, 2])
        self.assertIsNone(process_cube._select_bins_param({}, 0, "x", 1))
        self.assertEqual(
            process_cube._select_bins_param([[0, 1], [2, 3]], 1, "y", 2), [2, 3]
        )
        self.assertEqual(process_cube._combine_bins((), []), [])
        self.assertEqual(process_cube._combine_bins(("x",), [["a"]]), ["a"])
        self.assertEqual(
            process_cube._combine_bins(("x", "y"), [["a"], ["b"]]),
            ["x=a | y=b"],
        )

        for x, y, parameters in (
            ("x", "y", {process_cube.Parameters.AGGREGATION_FUNCTION: "sum"}),
            ("x", "py", {process_cube.Parameters.X_BINS: [0, 1, 2, 3]}),
            ("px", "y", {process_cube.Parameters.Y_BINS: [10, 25, 40]}),
            ("px", "py", {process_cube.Parameters.AGGREGATION_FUNCTION: "count"}),
            (("x", "category"), ("y", "py"), {}),
            ("category", "px", {process_cube.Parameters.AGGREGATION_FUNCTION: "last"}),
        ):
            with self.subTest(x=x, y=y):
                cube, cases = process_cube.apply(feature.lazy(), x, y, "agg", parameters)
                self.assertGreater(cube.height, 0)
                self.assertTrue(cases)

        empty_cube, empty_cases = process_cube.apply(
            feature.head(0).lazy(), "x", "y", "agg"
        )
        self.assertEqual(empty_cube.height, 0)
        self.assertEqual(empty_cases, {})
        missing_cube, _ = process_cube.apply(feature, "missing", "y", "agg")
        self.assertEqual(missing_cube.height, 0)

        self.assertEqual(
            process_cube._numeric_prefix_case(feature, "x", "agg", [0, 2, 4], [], "p").height,
            0,
        )
        self.assertEqual(
            process_cube._prefix_numeric_case(feature, "y", "agg", [0, 30, 50], [], "p").height,
            0,
        )
        self.assertEqual(process_cube._prefix_prefix_case(feature, "agg", [], ["py_c"]).height, 0)

    def test_performance_spectrum_standard_and_disconnected(self):
        self.assertEqual(
            lazyframe_disconnected.gen_patterns(["A", "B", "C"], 2), ["AB", "BC"]
        )
        prepared = lazyframe_disconnected._prepare_dataframe(
            self.lazy,
            ["A", "B", "C"],
            "case:concept:name",
            "concept:name",
            "time:timestamp",
            False,
        )
        self.assertEqual(prepared.collect().height, self.df.height)
        points = lazyframe.apply(self.lazy, ["A", "B", "C"], 1)
        self.assertEqual(len(points), 1)
        no_sort = lazyframe.apply(
            self.lazy,
            ["A", "B"],
            20,
            {lazyframe.Parameters.SORT_LOG_REQUIRED: False},
        )
        self.assertGreaterEqual(len(no_sort), 1)
        disconnected = lazyframe_disconnected.apply(
            self.lazy, ["A", "B", "C"], 2
        )
        self.assertLessEqual(len(disconnected), 4)
        disconnected_no_sort = lazyframe_disconnected.apply(
            self.lazy,
            ["A", "B", "C"],
            20,
            {lazyframe_disconnected.Parameters.SORT_LOG_REQUIRED: False},
        )
        self.assertGreaterEqual(len(disconnected_no_sort), 1)

    def test_attribute_filters_positive_negative_threshold_and_relative(self):
        values = attributes_filter.get_attribute_values(self.lazy, "concept:name")
        once = attributes_filter.get_attribute_values(
            self.lazy,
            "concept:name",
            {attributes_filter.Parameters.KEEP_ONCE_PER_CASE: True},
        )
        self.assertGreater(values["A"], once["A"])
        numeric_params = {attributes_filter.Parameters.ATTRIBUTE_KEY: "cost"}
        self.assertGreater(
            attributes_filter.apply_numeric_events(self.lazy, 1, 2, numeric_params).collect().height,
            0,
        )
        negative_params = dict(numeric_params)
        negative_params[attributes_filter.Parameters.POSITIVE] = False
        self.assertGreater(
            attributes_filter.apply_numeric_events(self.lazy, 1, 2, negative_params).collect().height,
            0,
        )
        case_params = {
            attributes_filter.Parameters.ATTRIBUTE_KEY: "cost",
            attributes_filter.Parameters.STREAM_FILTER_KEY1: "concept:name",
            attributes_filter.Parameters.STREAM_FILTER_VALUE1: "B",
            attributes_filter.Parameters.STREAM_FILTER_KEY2: "org:resource",
            attributes_filter.Parameters.STREAM_FILTER_VALUE2: "r2",
        }
        self.assertGreater(attributes_filter.apply_numeric(self.lazy, 1, 4, case_params).collect().height, 0)
        case_params[attributes_filter.Parameters.POSITIVE] = False
        self.assertGreater(attributes_filter.apply_numeric(self.lazy, 1, 4, case_params).collect().height, 0)

        for function in (attributes_filter.apply_events, attributes_filter.apply):
            self.assertGreater(function(self.lazy, ["B"]).collect().height, 0)
            negative = function(
                    self.lazy,
                    ["B"],
                    {attributes_filter.Parameters.POSITIVE: False},
                ).collect()
            self.assertIsInstance(negative, pl.DataFrame)
            self.assertLess(negative.height, self.df.height)
        self.assertEqual(
            attributes_filter.filter_df_on_attribute_values(self.lazy, None).collect().height,
            0,
        )
        self.assertGreater(
            attributes_filter.filter_df_keeping_activ_exc_thresh(
                self.lazy, 4, most_common_variant=["C"]
            ).collect().height,
            0,
        )
        self.assertEqual(
            attributes_filter.filter_df_keeping_activ_exc_thresh(
                self.lazy, 1, act_count0=values
            ).collect().height,
            self.df.height,
        )
        self.assertLess(
            attributes_filter.filter_df_keeping_spno_activities(
                self.lazy, max_no_activities=2
            ).collect().height,
            self.df.height,
        )
        self.assertEqual(
            attributes_filter.filter_df_keeping_spno_activities(
                self.lazy, max_no_activities=10
            ).collect().height,
            self.df.height,
        )
        relative_cases = attributes_filter.filter_df_relative_occurrence_event_attribute(
            self.lazy, 0.8
        ).collect()
        relative_events = attributes_filter.filter_df_relative_occurrence_event_attribute(
            self.lazy,
            0.3,
            {attributes_filter.Parameters.KEEP_ONCE_PER_CASE: False},
        ).collect()
        self.assertGreaterEqual(relative_cases.height, 1)
        self.assertGreaterEqual(relative_events.height, 1)

    def test_ltl_filters_cover_order_direct_four_eyes_and_resources(self):
        for positive in (True, False):
            parameters = {ltl_checker.Parameters.POSITIVE: positive}
            eventually = ltl_checker.eventually_follows(
                self.lazy, ["A", "B", "C"], parameters
            ).collect()
            direct = ltl_checker.A_next_B_next_C(
                self.lazy, ["A", "B", "C"], parameters
            ).collect()
            four_eyes = ltl_checker.four_eyes_principle(
                self.lazy, ["A", "B", "C"], parameters
            ).collect()
            people = ltl_checker.attr_value_different_persons(
                self.lazy, "A", parameters
            ).collect()
            self.assertIsInstance(eventually, pl.DataFrame)
            self.assertIsInstance(direct, pl.DataFrame)
            self.assertIsInstance(four_eyes, pl.DataFrame)
            self.assertIsInstance(people, pl.DataFrame)
        unchanged = ltl_checker.four_eyes_principle(self.lazy, ["A"]).collect()
        self.assertEqual(unchanged.height, self.df.height)

    def test_polars_attribute_statistics_distributions_and_kdes(self):
        for distribution, expected_length in (
            ("days_month", 31),
            ("months", 12),
            ("years", 1),
            ("hours", 24),
            ("days_week", 7),
            ("weeks", 53),
        ):
            x, y = attributes_get.get_events_distribution(self.lazy, distribution)
            self.assertEqual(len(x), expected_length)
            self.assertEqual(len(x), len(y))
        counts = attributes_get.get_attribute_values(self.lazy, "concept:name")
        once = attributes_get.get_attribute_values(
            self.lazy.select(["case:concept:name", "concept:name"]),
            "concept:name",
            {attributes_get.Parameters.KEEP_ONCE_PER_CASE: True},
        )
        self.assertEqual(once, {"A": 3, "B": 3, "C": 3})
        self.assertGreater(counts["A"], once["A"])
        x, y = attributes_get.get_kde_numeric_attribute(
            self.lazy,
            "score",
            {attributes_get.Parameters.MAX_NO_POINTS_SAMPLE: 5},
        )
        self.assertEqual(len(x), len(y))
        self.assertIsInstance(attributes_get.get_kde_numeric_attribute_json(self.lazy, "score"), str)
        date_x, date_y = attributes_get.get_kde_date_attribute(
            self.lazy,
            parameters={attributes_get.Parameters.MAX_NO_POINTS_SAMPLE: 5},
        )
        self.assertEqual(len(date_x), len(date_y))
        self.assertIsInstance(attributes_get.get_kde_date_attribute_json(self.lazy), str)

    def test_polars_dfg_frequency_performance_cost_partial_order_and_concurrency(self):
        frequency = df_statistics.get_dfg_graph(self.lazy)
        self.assertIn(("A", "B"), frequency)
        unsorted = df_statistics.get_dfg_graph(
            self.lazy,
            sort_timestamp_along_case_id=False,
            keep_once_per_case=True,
            reduce_columns=False,
        )
        self.assertTrue(unsorted)
        performance = df_statistics.get_dfg_graph(
            self.lazy,
            measure="performance",
            start_timestamp_key="start_timestamp",
            perf_aggregation_key="all",
            business_hours=True,
        )
        self.assertTrue(performance)
        both = df_statistics.get_dfg_graph(
            self.lazy,
            measure="both",
            start_timestamp_key="start_timestamp",
            perf_aggregation_key="median",
            target_activity_key="concept:name",
            window=2,
        )
        self.assertEqual(len(both), 2)
        cost = df_statistics.get_dfg_graph(
            self.lazy,
            measure="cost",
            cost_attribute="cost",
            perf_aggregation_key="sum",
        )
        self.assertTrue(cost)
        with self.assertRaises(ValueError):
            df_statistics.get_dfg_graph(
                self.lazy,
                measure="performance",
                perf_aggregation_key="does_not_exist",
            )

        partial = df_statistics.get_partial_order_dataframe(
            self.lazy,
            start_timestamp_key="start_timestamp",
            business_hours=True,
        ).collect()
        self.assertGreater(partial.height, 0)
        partial_all = df_statistics.get_partial_order_dataframe(
            self.lazy,
            start_timestamp_key="start_timestamp",
            sort_timestamp_along_case_id=False,
            reduce_dataframe=False,
            keep_first_following=False,
        ).collect()
        self.assertGreaterEqual(partial_all.height, partial.height)
        concurrent = df_statistics.get_concurrent_events_dataframe(
            self.lazy,
            start_timestamp_key="start_timestamp",
        ).collect()
        strict = df_statistics.get_concurrent_events_dataframe(
            self.lazy,
            start_timestamp_key="start_timestamp",
            sort_timestamp_along_case_id=False,
            reduce_dataframe=False,
            strict=True,
        ).collect()
        self.assertIsInstance(concurrent, pl.DataFrame)
        self.assertIsInstance(strict, pl.DataFrame)

    def test_variant_filters_case_attributes_and_pandas_activity_splitting(self):
        admitted = [["A", "B", "C"]]
        positive = variants_filter.apply(self.lazy, admitted).collect()
        negative = variants_filter.apply(
            self.lazy,
            admitted,
            {variants_filter.Parameters.POSITIVE: False},
        ).collect()
        self.assertGreater(positive.height, 0)
        self.assertGreater(negative.height, 0)
        self.assertGreater(
            variants_filter.filter_variants_top_k(self.lazy, 1).collect().height, 0
        )
        self.assertGreater(variants_filter.apply_auto_filter(self.lazy).collect().height, 0)
        self.assertGreater(
            variants_filter.apply_from_variant_list(
                self.lazy, [constants.DEFAULT_VARIANT_SEP.join(admitted[0])]
            ).collect().height,
            0,
        )
        self.assertGreater(
            variants_filter.apply_from_variant_list(
                self.lazy,
                [constants.DEFAULT_VARIANT_SEP.join(admitted[0])],
                {variants_filter.Parameters.POSITIVE: False},
            ).collect().height,
            0,
        )

        log = EventLog(
            [
                Trace(
                    [Event({"concept:name": "A"}), Event({"concept:name": "B"})],
                    attributes={"customer": "gold", "concept:name": "c1"},
                ),
                Trace(
                    [Event({"concept:name": "A"}), Event({"concept:name": "C"})],
                    attributes={"customer": "silver", "concept:name": "c2"},
                ),
            ]
        )
        dfg, nodes = case_attributes.apply(
            log,
            {
                case_attributes.Parameters.CASE_ATTRIBUTES: ["customer", "missing"],
                case_attributes.Parameters.RETURN_NODES_ATTRIBUTES: True,
            },
        )
        self.assertIn(("A", "B"), dfg)
        self.assertIn("A", nodes)
        self.assertTrue(case_attributes.apply(log))

        pandas_frame = self.df.select(
            ["case:concept:name", "concept:name", "time:timestamp"]
        ).to_pandas()
        split_this = activity_split_filter.apply(pandas_frame, "B")
        split_next = activity_split_filter.apply(
            pandas_frame,
            ["B", "C"],
            {
                activity_split_filter.Parameters.CUT_MODE: "next",
                activity_split_filter.Parameters.SUBCASE_CONCAT_STR: "::",
            },
        )
        self.assertGreater(split_this["case:concept:name"].nunique(), 3)
        self.assertGreater(split_next["case:concept:name"].nunique(), 3)


if __name__ == "__main__":
    unittest.main()
