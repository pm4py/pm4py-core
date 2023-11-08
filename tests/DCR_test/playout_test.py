import os
import unittest
from datetime import datetime

import pm4py
from pm4py.objects.dcr.importer import importer as dcr_importer
from pm4py.objects.conversion.dcr.variants.to_petri_net import Dcr2PetriNet
from pm4py.objects.petri_net.importer import importer as pnml_importer
from pm4py.algo.simulation.playout.petri_net import algorithm as simulator

class TestDCR(unittest.TestCase):

    def test_dcr_to_tapn(self):
        dcr = dcr_importer.apply(os.path.join("test_output_data", "sepsis_dcr_portal.xml"))
        file_name = 'test_dcr_to_petri_net.tapn'
        path = os.path.join("test_output_data", file_name)
        d2p = Dcr2PetriNet(postoptimize=False)
        tapn = d2p.dcr2tapn(dcr, path)

    def test_dcr_to_tapn_playout(self):
        net, im, fm, = pnml_importer.apply(os.path.join("test_output_data", "test_dcr_to_petri_net.tapn"), variant=pnml_importer.Variants.TAPN)
        number_of_traces = 10
        eventlog = simulator.apply(net, im, fm, variant=simulator.Variants.BASIC_PLAYOUT,
                                   parameters={
                                       simulator.Variants.BASIC_PLAYOUT.value.Parameters.NO_TRACES: number_of_traces})
        self.assertEqual(len(eventlog), number_of_traces)
        case_id_default = 0
        last_case_id = case_id_default + number_of_traces - 1
        timestamp_default = 10000000
        self.assertEqual(eventlog[0].attributes['concept:name'], str(case_id_default))
        self.assertEqual(datetime.timestamp(eventlog[0][0]['time:timestamp']), timestamp_default)
        self.assertEqual(eventlog[-1].attributes['concept:name'], str(last_case_id))

    def test_dcr_to_pnml(self):
        dcr = dcr_importer.apply(os.path.join("test_output_data", "sepsis_dcr_portal.xml"))
        file_name = 'test_dcr_to_petri_net.pnml'
        path = os.path.join("test_output_data", file_name)
        d2p = Dcr2PetriNet(postoptimize=False)
        pnml = d2p.dcr2tapn(dcr, path)

    def test_dcr_to_pnml_playout(self):
        net, im, fm, = pnml_importer.apply(os.path.join("test_output_data", "test_dcr_to_petri_net.pnml"), variant=pnml_importer.Variants.PNML)
        number_of_traces = 10
        eventlog = simulator.apply(net, im, fm, variant=simulator.Variants.BASIC_PLAYOUT,
                                   parameters={
                                       simulator.Variants.BASIC_PLAYOUT.value.Parameters.NO_TRACES: number_of_traces})
        self.assertEqual(len(eventlog), number_of_traces)
        case_id_default = 0
        last_case_id = case_id_default + number_of_traces - 1
        timestamp_default = 10000000
        self.assertEqual(eventlog[0].attributes['concept:name'], str(case_id_default))
        self.assertEqual(datetime.timestamp(eventlog[0][0]['time:timestamp']), timestamp_default)
        self.assertEqual(eventlog[-1].attributes['concept:name'], str(last_case_id))

if __name__ == '__main__':
    unittest.main()
