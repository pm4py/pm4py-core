import os
import unittest

from pm4py.algo.conformance.alignments.petri_net import algorithm as align_alg
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay
from pm4py.objects import petri_net
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.petri_net.exporter import exporter as petri_exporter
from pm4py.objects.petri_net.importer import importer as petri_importer
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from tests.constants import INPUT_DATA_DIR, OUTPUT_DATA_DIR
from pm4py.objects.conversion.process_tree import converter as process_tree_converter


class PetriImportExportTest(unittest.TestCase):
    def test_importingExportingPetri(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        imported_petri1, marking1, fmarking1 = petri_importer.apply(
            os.path.join(INPUT_DATA_DIR, "running-example.pnml"))
        petri_exporter.apply(imported_petri1, marking1, os.path.join(OUTPUT_DATA_DIR, "running-example.pnml"))
        imported_petri2, marking2, fmarking2 = petri_importer.apply(
            os.path.join(OUTPUT_DATA_DIR, "running-example.pnml"))

        self.assertEqual(sorted([x.name for x in imported_petri1.places]),
                         sorted([x.name for x in imported_petri2.places]))
        self.assertEqual(sorted([x.name for x in imported_petri1.transitions]),
                         sorted([x.name for x in imported_petri2.transitions]))
        self.assertEqual(sorted([x.source.name + x.target.name for x in imported_petri1.arcs]),
                         sorted([x.source.name + x.target.name for x in imported_petri2.arcs]))
        self.assertEqual([x.name for x in marking1], [x.name for x in marking2])
        os.remove(os.path.join(OUTPUT_DATA_DIR, "running-example.pnml"))

    def test_importingPetriLogTokenReplay(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        imported_petri1, marking1, fmarking1 = petri_importer.apply(
            os.path.join(INPUT_DATA_DIR, "running-example.pnml"))
        log = xes_importer.apply(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        aligned_traces = token_replay.apply(log, imported_petri1, marking1, fmarking1)
        del aligned_traces

    def test_importingPetriLogAlignment(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        imported_petri1, marking1, fmarking1 = petri_importer.apply(
            os.path.join(INPUT_DATA_DIR, "running-example.pnml"))
        log = xes_importer.apply(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        final_marking = petri_net.obj.Marking()
        for p in imported_petri1.places:
            if not p.out_arcs:
                final_marking[p] = 1
        for trace in log:
            cf_result = align_alg.apply(trace, imported_petri1, marking1, final_marking,
                                        variant=align_alg.VERSION_DIJKSTRA_NO_HEURISTICS)['alignment']
            is_fit = True
            for couple in cf_result:
                if not (couple[0] == couple[1] or couple[0] == ">>" and couple[1] is None):
                    is_fit = False
            if not is_fit:
                raise Exception("should be fit")

    def test_s_components(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log = xes_importer.apply(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        process_tree = inductive_miner.apply(log)
        net, im, fm = process_tree_converter.apply(process_tree)
        s_comps = petri_net.utils.petri_utils.get_s_components_from_petri(net, im, fm)
        del s_comps


if __name__ == "__main__":
    unittest.main()
