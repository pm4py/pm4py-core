import copy
import importlib.util
import queue
import unittest
from unittest import mock

import pandas as pd

import pm4py
from pm4py.algo.conformance.alignments.dfg import algorithm as dfg_alignments
from pm4py.algo.conformance.alignments.dfg.variants import classic as dfg_classic
from pm4py.algo.conformance.alignments.petri_net import algorithm as pn_alignments
from pm4py.algo.conformance.tokenreplay.variants import token_replay
from pm4py.objects.log.obj import Event, EventLog, Trace
from pm4py.objects.petri_net.obj import Marking, PetriNet
from pm4py.objects.petri_net.utils import petri_utils


class ConformanceDecisionDeepCoverageTest(unittest.TestCase):
    @staticmethod
    def _accepting_net():
        tree = pm4py.parse_process_tree("->( 'A', X( 'B', 'C' ), 'D' )")
        return pm4py.convert_to_petri_net(tree)

    @staticmethod
    def _trace(activities, case_id="case", **attributes):
        return Trace(
            [Event({"concept:name": activity, **attributes}) for activity in activities],
            attributes={"concept:name": case_id, "segment": "gold"},
        )

    def test_all_petri_alignment_variants_and_log_routes(self):
        net, initial, final = self._accepting_net()
        fit = self._trace(["A", "B", "D"], "fit")
        unfit = self._trace(["A", "X", "D"], "unfit")
        for variant in pn_alignments.Variants:
            result = pn_alignments.apply(
                fit,
                net,
                initial,
                final,
                variant=variant,
                parameters={
                    pn_alignments.Parameters.SHOW_PROGRESS_BAR: False,
                    pn_alignments.Parameters.ENABLE_BEST_WORST_COST: False,
                },
            )
            self.assertIn("alignment", result)

        log = EventLog([fit, unfit])
        packed = pn_alignments.apply(
            log,
            net,
            initial,
            final,
            variant="Variants.VERSION_DIJKSTRA_NO_HEURISTICS",
            parameters={
                pn_alignments.Parameters.SHOW_PROGRESS_BAR: False,
                pn_alignments.Parameters.UNPACK_VARIANT_ALIGNMENTS: False,
            },
        )
        self.assertEqual(2, len(packed))
        dataframe = pm4py.convert_to_dataframe(log)
        unpacked = pn_alignments.apply(
            dataframe,
            net,
            initial,
            final,
            variant="Variants.VERSION_DIJKSTRA_LESS_MEMORY",
            parameters={pn_alignments.Parameters.SHOW_PROGRESS_BAR: False},
        )
        self.assertEqual(2, len(unpacked))

    def test_token_replay_modes_variant_serialization_and_diagnostics(self):
        net, initial, final = self._accepting_net()
        log = EventLog(
            [
                self._trace(["A", "B", "D"], "fit"),
                self._trace(["A", "C", "D"], "other fit"),
                self._trace(["A", "X", "D"], "unknown"),
                self._trace(["D"], "missing"),
            ]
        )
        parameter_sets = (
            {
                token_replay.Parameters.SHOW_PROGRESS_BAR: False,
                token_replay.Parameters.RETURN_NAMES: True,
                token_replay.Parameters.STOP_IMMEDIATELY_UNFIT: True,
            },
            {
                token_replay.Parameters.SHOW_PROGRESS_BAR: False,
                token_replay.Parameters.ENABLE_PLTR_FITNESS: True,
                token_replay.Parameters.CLEANING_TOKEN_FLOOD: True,
                token_replay.Parameters.CONSIDER_ACTIVITIES_NOT_IN_MODEL_IN_FITNESS: True,
            },
            {
                token_replay.Parameters.SHOW_PROGRESS_BAR: False,
                token_replay.Parameters.IS_REDUCTION: True,
                token_replay.Parameters.EXHAUSTIVE_INVISIBLE_EXPLORATION: True,
            },
        )
        outputs = []
        for parameters in parameter_sets:
            replay = token_replay.apply(log, net, initial, final, parameters=parameters)
            self.assertEqual(4, len(replay))
            outputs.append(replay)
        diagnostics = token_replay.get_diagnostics_dataframe(log, outputs[0])
        self.assertEqual(4, len(diagnostics))

        variants_list = [(('A', 'B', 'D'), 2), (('A', 'C', 'D'), 1)]
        self.assertEqual(
            2,
            len(
                token_replay.apply_variants_list(
                    variants_list,
                    net,
                    initial,
                    final,
                    parameters={token_replay.Parameters.SHOW_PROGRESS_BAR: False},
                )
            ),
        )
        variants_dictionary = {('A', 'B', 'D'): [0, 1]}
        self.assertEqual(
            1,
            len(
                token_replay.apply_variants_dictionary(
                    variants_dictionary,
                    net,
                    initial,
                    final,
                    parameters={token_replay.Parameters.SHOW_PROGRESS_BAR: False},
                )
            ),
        )
        petri_bytes = pm4py.serialize(net, initial, final)[1]
        from pm4py.objects.petri_net.importer.variants import pnml

        # The compatibility wrapper still calls the pre-3.0 importer name.
        with mock.patch.object(
            pnml,
            "import_petri_from_string",
            side_effect=pnml.import_net_from_string,
            create=True,
        ):
            self.assertEqual(
                2,
                len(
                    token_replay.apply_variants_list_petri_string(
                        variants_list,
                        petri_bytes,
                        parameters={token_replay.Parameters.SHOW_PROGRESS_BAR: False},
                    )
                ),
            )
            result_queue = queue.Queue()
            token_replay.apply_variants_list_petri_string_multiprocessing(
                result_queue,
                variants_list[:1],
                petri_bytes,
                parameters={token_replay.Parameters.SHOW_PROGRESS_BAR: False},
            )
        self.assertEqual(1, len(result_queue.get_nowait()))

        transition = next(t for t in net.transitions if t.label == "D")
        empty = Marking()
        self.assertTrue(token_replay.get_places_with_missing_tokens(transition, empty))
        missing, added = token_replay.add_missing_tokens(transition, empty)
        self.assertGreater(missing, 0)
        self.assertTrue(added)
        consumed, consumed_map = token_replay.get_consumed_tokens(transition)
        produced, produced_map = token_replay.get_produced_tokens(transition)
        self.assertEqual(consumed, sum(consumed_map.values()))
        self.assertEqual(produced, sum(produced_map.values()))
        merged = {"a": 3}
        token_replay.merge_dicts(merged, {"a": 2, "b": 4})
        self.assertEqual({"a": 2, "b": 4}, merged)
        self.assertNotEqual(
            token_replay.get_variant_from_trace(log[0], "concept:name"),
            token_replay.get_variant_from_trace(log[0], "concept:name", disable_variants=True),
        )

    def test_dfg_alignment_trace_log_costs_variants_and_serialization(self):
        log = EventLog(
            [
                self._trace(["A", "B", "C"], "one"),
                self._trace(["A", "C"], "two"),
            ]
        )
        dfg = {("A", "B"): 1, ("B", "C"): 1, ("A", "C"): 1}
        starts, ends = {"A": 2}, {"C": 2}
        parameters = {
            dfg_classic.Parameters.SYNC_COST_FUNCTION: {"A": 0, "B": 0, "C": 0},
            dfg_classic.Parameters.MODEL_MOVE_COST_FUNCTION: {"A": 2, "B": 2, "C": 2},
            dfg_classic.Parameters.LOG_MOVE_COST_FUNCTION: {"A": 2, "B": 2, "C": 2, "X": 2},
            dfg_classic.Parameters.INTERNAL_LOG_MOVE_COST_FUNCTION: {"A": 1, "B": 1, "C": 1, "X": 1},
        }
        self.assertIn("alignment", dfg_alignments.apply(log[0], dfg, starts, ends, parameters=parameters))
        self.assertEqual(2, len(dfg_alignments.apply(log, dfg, starts, ends, parameters=parameters)))
        dataframe = pm4py.convert_to_dataframe(log)
        self.assertEqual(2, len(dfg_alignments.apply(dataframe, dfg, starts, ends, parameters=parameters)))
        variants = [(('A', 'B', 'C'), 2), (('A', 'C'), 1)]
        self.assertEqual(2, len(dfg_classic.apply_from_variants_list(variants, dfg, starts, ends, parameters)))
        self.assertIn("alignment", dfg_classic.apply_from_variant(('A', 'X', 'C'), dfg, starts, ends, parameters))
        serialization = pm4py.serialize(dfg, starts, ends)[1]
        self.assertEqual(
            2,
            len(dfg_classic.apply_from_variants_list_dfg_string(variants, serialization, parameters)),
        )
        distance = dfg_classic.dijkstra_to_end_node(
            dfg,
            starts,
            ends,
            "@@start",
            "@@end",
            {"A", "B", "C"},
            parameters[dfg_classic.Parameters.SYNC_COST_FUNCTION],
            parameters[dfg_classic.Parameters.MODEL_MOVE_COST_FUNCTION],
        )
        self.assertIn("A", distance)

    @staticmethod
    def _decision_fixture():
        net = PetriNet("choice")
        p0, choice, p2 = [PetriNet.Place(name) for name in ("p0", "choice", "p2")]
        a, b, c = (
            PetriNet.Transition("ta", "A"),
            PetriNet.Transition("tb", "B"),
            PetriNet.Transition("tc", "C"),
        )
        net.places.update({p0, choice, p2})
        net.transitions.update({a, b, c})
        for source, target in (
            (p0, a), (a, choice), (choice, b), (choice, c), (b, p2), (c, p2)
        ):
            petri_utils.add_arc_from_to(source, target, net)
        log = EventLog()
        for index, (target, amount, group) in enumerate(
            (("B", 1, "low"), ("B", 2, "low"), ("C", 9, "high"), ("C", 10, "high"))
        ):
            log.append(
                Trace(
                    [
                        Event({"concept:name": "A", "amount": amount, "group": group}),
                        Event({"concept:name": target, "amount": amount, "group": group}),
                    ],
                    attributes={"concept:name": str(index), "region": "west"},
                )
            )
        return log, net, Marking({p0: 1}), Marking({p2: 1}), choice, (a, b, c)

    @unittest.skipUnless(
        importlib.util.find_spec("sklearn"), "scikit-learn is not installed"
    )
    def test_decision_mining_trace_attributes_validation_and_extractors(self):
        from pm4py.algo.decision_mining import algorithm as decision_mining

        log, net, initial, final, choice, transitions = self._decision_fixture()
        self.assertEqual({"choice"}, set(decision_mining.get_decision_points(net)))
        self.assertEqual({"B", "C"}, set(decision_mining.get_decision_points(net, labels=True)["choice"]))
        with self.assertRaises(Exception):
            decision_mining.apply(log, net, initial, final)
        for kwargs in (
            {"pre_decision_points": "choice", "attributes": ["amount"]},
            {"pre_decision_points": [], "attributes": ["amount"]},
            {"pre_decision_points": ["choice"], "attributes": "amount"},
            {"pre_decision_points": ["choice"], "attributes": []},
            {"pre_decision_points": ["choice"], "attributes": ["amount"], "trace_attributes": "region"},
            {"pre_decision_points": ["choice"], "attributes": ["amount"], "trace_attributes": []},
        ):
            with self.assertRaises(ValueError):
                decision_mining.get_decisions_table(log, net, initial, final, **kwargs)
        with self.assertRaises(Exception):
            decision_mining.get_decision_points(net, pre_decision_points=["missing"])

        with mock.patch.object(decision_mining, "token_replay", token_replay):
            table, points = decision_mining.get_decisions_table(
                copy.deepcopy(log),
                net,
                initial,
                final,
                attributes=["amount", "group"],
                use_trace_attributes=True,
                k=2,
                pre_decision_points=["choice", "missing"],
                parameters={decision_mining.Parameters.ACTIVITY_KEY: "e_concept:name"},
            )
        self.assertTrue(table["choice"])
        dataframe = pm4py.convert_to_dataframe(log)
        with mock.patch.object(
            decision_mining, "token_replay", token_replay
        ):
            classifier, columns, targets = decision_mining.get_decision_tree(
                dataframe,
                net,
                initial,
                final,
                decision_point="choice",
                attributes=["amount", "group"],
            )
        self.assertTrue(columns)
        self.assertEqual({"B", "C"}, set(targets))
        self.assertEqual(2, len(classifier.classes_))
        with mock.patch.object(decision_mining, "token_replay", token_replay):
            data_net, _, _ = decision_mining.create_data_petri_nets_with_decisions(
                log, net, initial, final
            )
        self.assertTrue(data_net.transitions)
        self.assertTrue(any("guard" in transition.properties for transition in data_net.transitions))
        prepared = decision_mining.prepare_event_log(copy.deepcopy(log))
        self.assertIn("t_region", prepared[0].attributes)
        self.assertIn("e_amount", prepared[0][0])
        self.assertEqual(["e_amount"], decision_mining.prepare_attributes(["amount"]))
        encoded, target_names = decision_mining.encode_target(
            pd.DataFrame({"choice": ["B", "C", "B"]}), "choice"
        )
        self.assertIn("Target", encoded)
        self.assertTrue(pd.api.types.is_integer_dtype(encoded["Target"]))
        self.assertEqual({"B", "C"}, set(target_names))

        decision_info = {"choice": []}
        decision_mining._extract_decisions_perfect_fit(
            log,
            [0],
            {"activated_transitions": list(transitions)},
            decision_info,
            {"choice": ["tb", "tc"]},
            {"choice": ["B", "C"]},
            ["amount"],
            True,
            ["region"],
            2,
            True,
        )
        self.assertTrue(decision_info["choice"])
        aligned_info = {"choice": []}
        decision_mining._extract_decisions_alignment(
            log,
            0,
            {
                "alignment": [
                    (("A", "ta"), ("A", "A")),
                    (("B", "tb"), ("B", "B")),
                    ((">>", "tc"), (">>", None)),
                ]
            },
            aligned_info,
            {"choice": ["tb", "tc"]},
            ["amount"],
            True,
            ["region"],
            2,
            False,
        )
        self.assertTrue(aligned_info["choice"])


if __name__ == "__main__":
    unittest.main()
