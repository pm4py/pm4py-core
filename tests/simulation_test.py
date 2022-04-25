import os
import unittest

from pm4py.objects.petri_net.importer import importer as pnml_importer
from pm4py.algo.simulation.playout.petri_net import algorithm as simulator
from tests.constants import INPUT_DATA_DIR
from datetime import datetime


class SimulationTest(unittest.TestCase):
    def test_simulate_petrinet(self):
        net, im, fm = pnml_importer.apply(
            os.path.join(INPUT_DATA_DIR, "running-example.pnml"))
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

    def test_simulate_petrinet_start_params(self):
        net, im, fm = pnml_importer.apply(
            os.path.join(INPUT_DATA_DIR, "running-example.pnml"))
        number_of_traces = 10
        timestamp = 50000000
        case_id = 5
        eventlog = simulator.apply(net, im, fm, variant=simulator.Variants.BASIC_PLAYOUT,
                                   parameters={
                                       simulator.Variants.BASIC_PLAYOUT.value.Parameters.NO_TRACES: number_of_traces,
                                       simulator.Variants.BASIC_PLAYOUT.value.Parameters.INITIAL_TIMESTAMP:
                                           timestamp,
                                       simulator.Variants.BASIC_PLAYOUT.value.Parameters.INITIAL_CASE_ID: case_id})
        self.assertEqual(len(eventlog), number_of_traces)
        last_case_id = case_id + number_of_traces - 1
        self.assertEqual(eventlog[0].attributes['concept:name'], str(case_id))
        self.assertEqual(datetime.timestamp(eventlog[0][0]['time:timestamp']), timestamp)
        self.assertEqual(eventlog[-1].attributes['concept:name'], str(last_case_id))


if __name__ == "__main__":
    unittest.main()
