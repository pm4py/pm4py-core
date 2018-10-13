import unittest
import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.objects import petri
from pm4py.algo.discovery.alpha import factory as alpha_factory
from pm4py.algo.discovery.inductive.versions.dfg import dfg_only
from tests.constants import INPUT_DATA_DIR
from pm4py.algo.conformance.alignments.versions import state_equation_a_star


class AlignmentTest(unittest.TestCase):
    def test_alignment_alpha(self):
        trace_log = xes_importer.import_log(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        net, marking, fmarking = alpha_factory.apply(trace_log)
        final_marking = petri.petrinet.Marking()
        for p in net.places:
            if not p.out_arcs:
                final_marking[p] = 1
        for trace in trace_log:
            cf_result = state_equation_a_star.apply(trace, net, marking, final_marking)['alignment']
            is_fit = True
            for couple in cf_result:
                if not (couple[0] == couple[1] or couple[0] == ">>" and couple[1] is None):
                    is_fit = False
            if not is_fit:
                raise Exception("should be fit")

    def test_alignment_pnml(self):
        trace_log = xes_importer.import_log(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        net, marking, final_marking = dfg_only.apply(trace_log, None)
        for trace in trace_log:
            cf_result = state_equation_a_star.apply(trace, net, marking, final_marking)['alignment']
            is_fit = True
            for couple in cf_result:
                if not (couple[0] == couple[1] or couple[0] == ">>" and couple[1] is None):
                    is_fit = False
            if not is_fit:
                raise Exception("should be fit")


if __name__ == "__main__":
    unittest.main()
