import os
import unittest
from datetime import datetime, timedelta, timezone
from unittest import mock

import numpy as np
import pandas as pd

import pm4py
from pm4py.algo.transformation.ocel.features.events import algorithm as event_features
from pm4py.algo.transformation.ocel.features.events_objects import algorithm as event_object_features
from pm4py.algo.transformation.ocel.features.objects import algorithm as object_features
from pm4py.objects.log.obj import Event, EventLog, Trace
from pm4py.objects.ocel.util import (
    event_prefix_suffix_per_obj,
    explode,
    log_ocel,
    ocel_to_dict_types_rel,
)


class OcelDeepCoverageTest(unittest.TestCase):
    @staticmethod
    def _input_path(*parts):
        return os.path.join(os.path.dirname(__file__), "input_data", *parts)

    @classmethod
    def _ocel(cls):
        return pm4py.read_ocel(cls._input_path("ocel", "example_log.jsonocel"))

    @staticmethod
    def _dataframe(prefix, object_type):
        base = datetime(2024, 1, 1, tzinfo=timezone.utc)
        return pd.DataFrame(
            [
                {
                    "case:concept:name": f"{prefix}1",
                    "concept:name": "create",
                    "time:timestamp": base,
                    "case:customer": "gold",
                    "value": 1.0,
                    object_type: f"{object_type}-1",
                },
                {
                    "case:concept:name": f"{prefix}1",
                    "concept:name": "complete",
                    "time:timestamp": base + timedelta(hours=1),
                    "case:customer": "gold",
                    "value": 2.0,
                    object_type: f"{object_type}-1 AND {object_type}-2",
                },
            ],
            index=[0, 1],
        )

    def test_all_object_event_and_event_object_features(self):
        ocel = self._ocel()
        object_parameters = {
            "enable_all": True,
            "enable_object_work_in_progress": True,
            "enable_related_events_features": True,
            "enable_related_activities_features": True,
            "enable_obj_con_in_graph_features": True,
            "enable_object_lifecycle_paths": True,
            "debug": True,
        }
        object_data, object_names = object_features.apply(ocel, parameters=object_parameters)
        self.assertEqual(len(ocel.objects), len(object_data))
        self.assertEqual(len(object_names), len(object_data[0]))
        object_dict = object_features.transform_features_to_dict_dict(
            ocel, object_data, object_names
        )
        self.assertEqual(len(ocel.objects), len(object_dict))

        object_type = ocel.objects.iloc[0][ocel.object_type_column]
        filtered, filtered_names = object_features.apply(
            ocel,
            parameters={
                **object_parameters,
                "debug": False,
                "filter_per_type": object_type,
            },
        )
        self.assertTrue(filtered)
        self.assertEqual(object_names, filtered_names)

        event_data, event_names = event_features.apply(
            ocel,
            parameters={"enable_all": True, "enable_related_objects_features": True},
        )
        self.assertEqual(len(ocel.events), len(event_data))
        self.assertEqual(len(event_names), len(event_data[0]))
        event_dict = event_features.transform_features_to_dict_dict(
            ocel, event_data, event_names
        )
        self.assertEqual(len(ocel.events), len(event_dict))

        eo_data, eo_names = event_object_features.apply(ocel)
        self.assertTrue(eo_data)
        self.assertEqual(len(eo_names), len(eo_data[0]))

    def test_traditional_log_and_dataframe_to_ocel(self):
        base = datetime(2024, 1, 1, tzinfo=timezone.utc)
        log = EventLog(
            [
                Trace(
                    [
                        Event({"concept:name": "A", "time:timestamp": base, "cost": 1}),
                        Event({"concept:name": "B", "time:timestamp": base + timedelta(minutes=1), "cost": 2}),
                    ],
                    attributes={"concept:name": "case-1", "customer": "gold"},
                )
            ]
        )
        ocel = log_ocel.from_traditional_log(log, parameters={"target_object_type": "case"})
        self.assertEqual(2, len(ocel.events))
        self.assertEqual(1, len(ocel.objects))

        dataframe = self._dataframe("c", "order")
        pandas_ocel = log_ocel.from_traditional_pandas(
            dataframe, parameters={"target_object_type": "case"}
        )
        self.assertEqual(2, len(pandas_ocel.events))
        self.assertEqual(1, len(pandas_ocel.objects))

    def test_interleavings_and_multiple_object_types(self):
        left = self._dataframe("left", "order")
        right = self._dataframe("right", "item")
        interleavings = pd.DataFrame(
            [
                {"@@left_index": 0, "@@right_index": 0, "@@direction": "LR"},
                {"@@left_index": 1, "@@right_index": 1, "@@direction": "RL"},
            ]
        )
        combined = log_ocel.from_interleavings(
            left.copy(),
            right.copy(),
            interleavings,
            parameters={"target_object_type": "left", "target_object_type_2": "right"},
        )
        self.assertEqual(4, len(combined.events))
        self.assertGreater(len(combined.relations), 4)

        source = pd.DataFrame(
            [
                {
                    "concept:name": "create",
                    "time:timestamp": datetime(2024, 1, 1, tzinfo=timezone.utc),
                    "orders": "o1 AND o2",
                    "items": "i1",
                    "value": 3.0,
                    "customer": "gold",
                    "nullable": np.nan,
                },
                {
                    "concept:name": "ship",
                    "time:timestamp": datetime(2024, 1, 2, tzinfo=timezone.utc),
                    "orders": "o1",
                    "items": None,
                    "value": 4.0,
                    "customer": "gold",
                    "nullable": pd.NaT,
                },
            ]
        )
        multi = log_ocel.log_to_ocel_multiple_obj_types(
            source,
            "concept:name",
            "time:timestamp",
            ["orders", "items"],
            additional_event_attributes=["value", "nullable"],
            additional_object_attributes={"orders": ["customer"]},
        )
        self.assertEqual(2, len(multi.events))
        self.assertEqual(3, len(multi.objects))
        self.assertNotIn("nullable", multi.events.columns)

    def test_ocel_prefix_and_relation_dictionary_utilities(self):
        ocel = self._ocel()
        exploded = explode.apply(ocel)
        self.assertGreaterEqual(len(exploded.events), len(ocel.events))
        prefixes = event_prefix_suffix_per_obj.apply(exploded)
        self.assertIsInstance(prefixes, dict)
        relation_dictionary = ocel_to_dict_types_rel.apply(ocel)
        self.assertIsInstance(relation_dictionary, dict)
        self.assertTrue(relation_dictionary)


if __name__ == "__main__":
    unittest.main()
