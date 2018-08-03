import pm4py.log.instance as log_instance
from pm4py.models.petri import semantics
from copy import copy
from random import shuffle

def playoutPetriNet(net, initialMarking, noTraces=100, maxTraceLength=100):
    """
    Do the playout of a Petrinet generating a log

    Parameters
    ----------
    net
        Petri net to play-out
    initialMarking
        Initial marking of the Petri net
    noOfTraces
        Number of traces to generate
    maxTraceLength
        Maximum number of events per trace (do break)
    """
    log = log_instance.TraceLog()
    for i in range(noTraces):
        trace = log_instance.Trace()
        trace.attributes["concept:name"] = str(i)
        marking = copy(initialMarking)
        while semantics.enabled_transitions(net, marking):
            allEnabledTrans = semantics.enabled_transitions(net, marking)
            allEnabledTrans = list(allEnabledTrans)
            shuffle(allEnabledTrans)
            trans = allEnabledTrans[0]
            if trans.label is not None:
                event = log_instance.Event()
                event["concept:name"] = trans.label
                trace.append(event)
            marking = semantics.execute(trans, net, marking)
            if len(trace) > maxTraceLength:
                break
        log.append(trace)
    return log