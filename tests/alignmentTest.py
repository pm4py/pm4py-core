import unittest
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from pm4py.log.importer import xes as xes_importer
import pm4py.algo.alignments as align
from pm4py.models import petri
from pm4py.algo.alpha import factory as alpha_factory
from pm4py.algo.inductive.versions import dfg_only
from tests.constants import INPUT_DATA_DIR


class AlignmentTest(unittest.TestCase):
    def test_alignment_alpha(self):
        traceLog = xes_importer.import_from_file_xes(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        net, marking, fmarking = alpha_factory.apply(traceLog)
        final_marking = petri.petrinet.Marking()
        for p in net.places:
            if not p.out_arcs:
                final_marking[p] = 1
        for trace in traceLog:
            cfResult = align.versions.state_equation_a_star.apply(trace, net, marking, final_marking)['alignment']
            isFit = True
            for couple in cfResult:
                if not (couple[0] == couple[1] or couple[0] == ">>" and couple[1] == None):
                    isFit = False
            if not isFit:
                raise Exception("should be fit")

    def test_alignment_pnml(self):
        traceLog = xes_importer.import_from_file_xes(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        net, marking, final_marking = dfg_only.apply(traceLog, None)
        for trace in traceLog:
            cfResult = align.versions.state_equation_a_star.apply(trace, net, marking, final_marking)['alignment']
            isFit = True
            for couple in cfResult:
                if not (couple[0] == couple[1] or couple[0] == ">>" and couple[1] == None):
                    isFit = False
            if not isFit:
                raise Exception("should be fit")

if __name__ == "__main__":
    unittest.main()