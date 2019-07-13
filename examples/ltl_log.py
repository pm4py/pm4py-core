import os

from pm4py.algo.filtering.log.ltl import ltl_checker
from pm4py.objects.log.importer.xes import factory as xes_importer


def execute_script():
    # import the log
    log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
    # A eventually B positive: filter the cases of the log where each instance of A is eventually followed by an instance
    # of B
    filt_A_ev_B_pos = ltl_checker.A_eventually_B(log, "check ticket", "pay compensation", parameters={"positive": True})
    print("len(filt_A_ev_B_pos) = ",len(filt_A_ev_B_pos))
    # A eventually B negative: filter the cases of the log where A or B where not there, or cases where an instance of
    # A is not followed by an instance of B
    filt_A_ev_B_neg = ltl_checker.A_eventually_B(log, "check ticket", "pay compensation", parameters={"positive": False})
    print("len(filt_A_ev_B_neg) = ",len(filt_A_ev_B_neg))
    # four eyes principle positive: filter the cases of the log where A and B are both there, and the resource doing A
    # is NEVER the same resource doing B
    filt_foureyes_pos = ltl_checker.four_eyes_principle(log, "check ticket", "pay compensation", parameters={"positive": True})
    print("len(filt_foureyes_pos) = ",len(filt_foureyes_pos))
    # four eyes principle negative: filter the cases of the log where A and B are both there, and there is a common
    # resource doing A and B
    filt_foureyes_neg = ltl_checker.four_eyes_principle(log, "check ticket", "pay compensation", parameters={"positive": False})
    print("len(filt_foureyes_neg) = ",len(filt_foureyes_neg))



if __name__ == "__main__":
    execute_script()
