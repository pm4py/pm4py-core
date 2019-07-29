import os
import unittest

from pm4py.algo.filtering.log.ltl import ltl_checker
from pm4py.objects.log.importer.xes import factory as xes_importer


class LtlCheckingLogTest(unittest.TestCase):
    def test_AeventuallyB_pos(self):
        log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
        filt_A_ev_B_pos = ltl_checker.A_eventually_B(log, "check ticket", "pay compensation",
                                                     parameters={"positive": True})

    def test_AeventuallyB_neg(self):
        log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
        filt_A_ev_B_neg = ltl_checker.A_eventually_B(log, "check ticket", "pay compensation",
                                                     parameters={"positive": False})

    def test_AeventuallyBeventuallyC_pos(self):
        log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
        filt_A_ev_B_ev_C_pos = ltl_checker.A_eventually_B_eventually_C(log, "check ticket", "decide",
                                                                       "pay compensation",
                                                                       parameters={"positive": True})

    def test_AeventuallyBeventuallyC_neg(self):
        log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
        filt_A_ev_B_ev_C_neg = ltl_checker.A_eventually_B_eventually_C(log, "check ticket", "decide",
                                                                       "pay compensation",
                                                                       parameters={"positive": False})

    def test_AnextBnextC_pos(self):
        log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
        filt_A_next_B_next_C_pos = ltl_checker.A_next_B_next_C(log, "check ticket", "decide", "pay compensation",
                                                               parameters={"positive": True})

    def test_AnextBnextC_neg(self):
        log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
        filt_A_next_B_next_C_neg = ltl_checker.A_next_B_next_C(log, "check ticket", "decide", "pay compensation",
                                                               parameters={"positive": False})

    def test_fourEeyesPrinciple_pos(self):
        log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
        filt_foureyes_pos = ltl_checker.four_eyes_principle(log, "check ticket", "pay compensation",
                                                            parameters={"positive": True})

    def test_fourEeyesPrinciple_neg(self):
        log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
        filt_foureyes_neg = ltl_checker.four_eyes_principle(log, "check ticket", "pay compensation",
                                                            parameters={"positive": False})

    def test_attrValueDifferentPersons_pos(self):
        log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
        attr_value_different_persons_pos = ltl_checker.attr_value_different_persons(log, "check ticket",
                                                                                    parameters={"positive": True})

    def test_attrValueDifferentPersons_neg(self):
        log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
        attr_value_different_persons_neg = ltl_checker.attr_value_different_persons(log, "check ticket",
                                                                                    parameters={"positive": False})


if __name__ == "__main__":
    unittest.main()
