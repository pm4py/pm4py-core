import os

from pm4py.algo.filtering.log.ltl import ltl_checker
from pm4py.objects.log.importer.xes import factory as xes_importer


def execute_script():
    # import the log
    log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
    # A eventually B positive: filter the cases of the log where each instance of A is eventually followed by an instance
    # of B
    filt_A_ev_B_pos = ltl_checker.A_eventually_B(log, "check ticket", "pay compensation", parameters={"positive": True})
    print("len(filt_A_ev_B_pos) = ", len(filt_A_ev_B_pos))
    # A eventually B negative: filter the cases of the log where A or B where not there, or cases where an instance of
    # A is not followed by an instance of B
    filt_A_ev_B_neg = ltl_checker.A_eventually_B(log, "check ticket", "pay compensation",
                                                 parameters={"positive": False})
    print("len(filt_A_ev_B_neg) = ", len(filt_A_ev_B_neg))

    # A eventually B eventually C positive: filter the cases of the log where each instance of A is
    # eventually followed by an instance of B that is eventually followed by an instance of C
    filt_A_ev_B_ev_C_pos = ltl_checker.A_eventually_B_eventually_C(log, "check ticket", "decide", "pay compensation",
                                                                   parameters={"positive": True})
    print("len(filt_A_ev_B_ev_C_pos) = ", len(filt_A_ev_B_ev_C_pos))
    # A eventually B eventually C negative: filter the cases of the log where A,B,C are not all in the case,
    # or an instance of A is not eventually followed by an instance of B that is not eventually followed by
    # an instance of C
    filt_A_ev_B_ev_C_neg = ltl_checker.A_eventually_B_eventually_C(log, "check ticket", "decide", "pay compensation",
                                                                   parameters={"positive": False})
    print("len(filt_A_ev_B_ev_C_neg) = ", len(filt_A_ev_B_ev_C_neg))

    # A next B next C positive: filter the cases of the log where an instance of A was followed by an
    # instance of B, and the instance of B was directly followed by an instance of C
    filt_A_next_B_next_C_pos = ltl_checker.A_next_B_next_C(log, "check ticket", "decide", "pay compensation",
                                                           parameters={"positive": True})
    print("len(filt_A_next_B_net_C_pos) = ", len(filt_A_next_B_next_C_pos))
    # A next B next C negative: filter the cases of the log where none instance of A was followed directly
    # by an instance of B, and the instance of B was directly followed by an instance of C
    filt_A_next_B_next_C_neg = ltl_checker.A_next_B_next_C(log, "check ticket", "decide", "pay compensation",
                                                           parameters={"positive": False})
    print("len(filt_A_next_B_next_C_neg) = ", len(filt_A_next_B_next_C_neg))

    # four eyes principle positive: filter the cases of the log where A and B are both there, and the resource doing A
    # is NEVER the same resource doing B
    filt_foureyes_pos = ltl_checker.four_eyes_principle(log, "check ticket", "pay compensation",
                                                        parameters={"positive": True})
    print("len(filt_foureyes_pos) = ", len(filt_foureyes_pos))
    # four eyes principle negative: filter the cases of the log where A and B are both there, and there is a common
    # resource doing A and B
    filt_foureyes_neg = ltl_checker.four_eyes_principle(log, "check ticket", "pay compensation",
                                                        parameters={"positive": False})
    print("len(filt_foureyes_neg) = ", len(filt_foureyes_neg))

    # attr_value_different_persons positive: filter the cases of the log in which A was done by two different resources
    attr_value_different_persons_pos = ltl_checker.attr_value_different_persons(log, "check ticket",
                                                                                parameters={"positive": True})
    print("len(attr_value_different_persons_pos) = ", len(attr_value_different_persons_pos))
    # attr_value_different_persons negative: filter the cases of the log in which A was not there or was not executed
    # by two different resources
    attr_value_different_persons_neg = ltl_checker.attr_value_different_persons(log, "check ticket",
                                                                                parameters={"positive": False})
    print("len(attr_value_different_persons_neg) = ", len(attr_value_different_persons_neg))

    #input()


if __name__ == "__main__":
    execute_script()
