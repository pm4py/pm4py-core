import os
import unittest

from pm4py.algo.conformance.alignments.versions import state_equation_a_star
from pm4py.algo.conformance.tokenreplay.versions import token_replay
from pm4py.objects import petri
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.objects.petri import check_soundness
from pm4py.objects.petri.exporter import pnml as petri_exporter
from pm4py.objects.petri.importer import pnml as petri_importer
from pm4py.algo.discovery.inductive import factory as inductive_miner
from tests.constants import INPUT_DATA_DIR, OUTPUT_DATA_DIR


class PetriImportExportTest(unittest.TestCase):
    def test_importingExportingPetri(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        imported_petri1, marking1, fmarking1 = petri_importer.import_net(
            os.path.join(INPUT_DATA_DIR, "running-example.pnml"))
        soundness = check_soundness.check_petri_wfnet_and_soundness(imported_petri1)
        del soundness
        petri_exporter.export_net(imported_petri1, marking1, os.path.join(OUTPUT_DATA_DIR, "running-example.pnml"))
        imported_petri2, marking2, fmarking2 = petri_importer.import_net(
            os.path.join(OUTPUT_DATA_DIR, "running-example.pnml"))
        soundness = check_soundness.check_petri_wfnet_and_soundness(imported_petri2)
        del soundness

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
        imported_petri1, marking1, fmarking1 = petri_importer.import_net(
            os.path.join(INPUT_DATA_DIR, "running-example.pnml"))
        soundness = check_soundness.check_petri_wfnet_and_soundness(imported_petri1)
        del soundness
        log = xes_importer.import_log(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        aligned_traces = token_replay.apply_log(log, imported_petri1, marking1, fmarking1)
        del aligned_traces

    def test_importingPetriLogAlignment(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        imported_petri1, marking1, fmarking1 = petri_importer.import_net(
            os.path.join(INPUT_DATA_DIR, "running-example.pnml"))
        soundness = check_soundness.check_petri_wfnet_and_soundness(imported_petri1)
        del soundness
        log = xes_importer.import_log(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        final_marking = petri.petrinet.Marking()
        for p in imported_petri1.places:
            if not p.out_arcs:
                final_marking[p] = 1
        for trace in log:
            cf_result = state_equation_a_star.apply(trace, imported_petri1, marking1, final_marking)['alignment']
            is_fit = True
            for couple in cf_result:
                if not (couple[0] == couple[1] or couple[0] == ">>" and couple[1] is None):
                    is_fit = False
            if not is_fit:
                raise Exception("should be fit")

    def test_importingExportingStochasticNet(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        imported_petri1, marking1, fmarking1, stochastic_info1 = petri_importer.import_net(
            os.path.join(INPUT_DATA_DIR, "stochastic_running_example.pnml"), return_stochastic_information=True)
        petri_exporter.export_net(imported_petri1, marking1,
                                  os.path.join(OUTPUT_DATA_DIR, "stochastic_running_example.pnml"),
                                  final_marking=fmarking1, stochastic_map=stochastic_info1)
        os.remove(os.path.join(OUTPUT_DATA_DIR, "stochastic_running_example.pnml"))

    def test_s_components(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log = xes_importer.import_log(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        net, im, fm = inductive_miner.apply(log)
        s_comps = petri.utils.get_s_components_from_petri(net, im, fm)
        del s_comps


if __name__ == "__main__":
    unittest.main()
