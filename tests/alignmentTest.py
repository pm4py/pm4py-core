import unittest
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from pm4py.log.importer import xes as xes_importer
import pm4py.algo.alignments as align
from pm4py.models import petri
from pm4py.algo.alpha.versions import classic as alpha_classic
from pm4py.algo.imdf import inductMinDirFollows
from constants import INPUT_DATA_DIR, OUTPUT_DATA_DIR, PROBLEMATIC_XES_DIR
import logging

class AlignmentTest(unittest.TestCase):
    def test_alignment_alpha(self):
        traceLog = xes_importer.import_from_path_xes(os.path.join(INPUT_DATA_DIR,"running-example.xes"))
        net, marking = alpha_classic.apply(traceLog)
        final_marking = petri.net.Marking()
        for p in net.places:
            if not p.out_arcs:
                final_marking[p] = 1
        """cfResult = align.versions.state_equation_classic.apply_log(traceLog, net, marking, final_marking)
        for res in cfResult:
            isFit = True
            for couple in cfResult[0]:
                if not (couple.label[0] == couple.label[1] or couple.label[0] == ">>" and couple.label[1] == None):
                    isFit = False
            if not isFit:
                raise Exception("should be fit")"""

    def test_alignment_pnml(self):
        traceLog = xes_importer.import_from_path_xes(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        net, marking = inductMinDirFollows.apply(traceLog)
        final_marking = petri.net.Marking()
        for p in net.places:
            if not p.out_arcs:
                final_marking[p] = 1
        """cfResult = align.versions.state_equation_classic.apply_log(traceLog, net, marking, final_marking)
        for res in cfResult:
            isFit = True
            for couple in cfResult[0]:
                if not (couple.label[0] == couple.label[1] or couple.label[0] == ">>" and couple.label[1] == None):
                    isFit = False
            if not isFit:
                raise Exception("should be fit")"""

if __name__ == "__main__":
    unittest.main()