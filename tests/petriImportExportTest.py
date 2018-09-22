import unittest
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from pm4py.entities.petri.exporter import pnml as petri_exporter
from pm4py.entities.petri.importer import pnml as petri_importer
from tests.constants import INPUT_DATA_DIR, OUTPUT_DATA_DIR
from pm4py.algo.conformance.tokenreplay.versions import token_replay
from pm4py.entities import petri
from pm4py.entities.log.importer.xes import factory as xes_importer
from pm4py.algo.conformance.alignments.versions import state_equation_a_star

class PetriImportExportTest(unittest.TestCase):
    def test_importingExportingPetri(self):
        importedPetri1, marking1, fmarking1 = petri_importer.import_net(os.path.join(INPUT_DATA_DIR, "running-example.pnml"))
        petri_exporter.export_net(importedPetri1, marking1, os.path.join(OUTPUT_DATA_DIR, "running-example.pnml"))
        importedPetri2, marking2, fmarking2 = petri_importer.import_net(os.path.join(OUTPUT_DATA_DIR, "running-example.pnml"))

        self.assertEqual(sorted([x.name for x in importedPetri1.places]), sorted([x.name for x in importedPetri2.places]))
        self.assertEqual(sorted([x.name for x in importedPetri1.transitions]), sorted([x.name for x in importedPetri2.transitions]))
        self.assertEqual(sorted([x.source.name+x.target.name for x in importedPetri1.arcs]), sorted([x.source.name+x.target.name for x in importedPetri2.arcs]))
        self.assertEqual([x.name for x in marking1], [x.name for x in marking2])
        os.remove(os.path.join(OUTPUT_DATA_DIR, "running-example.pnml"))

    def test_importingPetriLogTokenReplay(self):
        importedPetri1, marking1, fmarking1 = petri_importer.import_net(os.path.join(INPUT_DATA_DIR, "running-example.pnml"))
        traceLog = xes_importer.import_log(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        aligned_traces = token_replay.apply_log(traceLog, importedPetri1, marking1, fmarking1)

    def test_importingPetriLogAlignment(self):
        importedPetri1, marking1, fmarking1 = petri_importer.import_net(os.path.join(INPUT_DATA_DIR, "running-example.pnml"))
        traceLog = xes_importer.import_log(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        final_marking = petri.petrinet.Marking()
        for p in importedPetri1.places:
            if not p.out_arcs:
                final_marking[p] = 1
        for trace in traceLog:
            cfResult = state_equation_a_star.apply(trace, importedPetri1, marking1, final_marking)['alignment']
            isFit = True
            for couple in cfResult:
                if not (couple[0] == couple[1] or couple[0] == ">>" and couple[1] == None):
                    isFit = False
            if not isFit:
                raise Exception("should be fit")

if __name__ == "__main__":
	unittest.main()