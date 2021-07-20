from pm4py.algo.analysis import extended_marking_equation, marking_equation, workflow_net

import pkgutil
if pkgutil.find_loader("simpy"):
    from pm4py.algo.analysis import woflan
