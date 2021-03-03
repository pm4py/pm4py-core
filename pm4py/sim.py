from collections import Counter
from typing import Union, Tuple

from pm4py.objects.log.log import EventLog
from pm4py.objects.petri.petrinet import PetriNet, Marking
from pm4py.objects.process_tree.process_tree import ProcessTree


def play_out(*args: Union[Tuple[PetriNet, Marking, Marking], dict, Counter, ProcessTree], **kwargs) -> EventLog:
    """
    Performs the playout of the provided model,
    i.e., gets a set of traces from the model.
    The function either takes a petri net, initial and final marking, or, a process tree as an input.

    Parameters
    ---------------
    args
        Model (Petri net, initial, final marking) or ProcessTree
    kwargs
        Parameters of the playout

    Returns
    --------------
    log
        Simulated event log
    """
    if len(args) == 3:
        from pm4py.objects.petri.petrinet import PetriNet
        if type(args[0]) is PetriNet:
            from pm4py.simulation.playout import simulator
            return simulator.apply(args[0], args[1], final_marking=args[2], **kwargs)
        elif type(args[0]) is dict or type(args[0]) is Counter:
            from pm4py.objects.dfg.utils import dfg_playout
            return dfg_playout.apply(args[0], args[1], args[2], **kwargs)
    elif len(args) == 1:
        from pm4py.objects.process_tree.process_tree import ProcessTree
        if type(args[0]) is ProcessTree:
            from pm4py.simulation.tree_playout import algorithm
            return algorithm.apply(args[0], **kwargs)
    raise Exception("unsupported model for playout")


def generate_process_tree(**kwargs) -> ProcessTree:
    """
    Generates a process tree

    Parameters
    -------------
    kwargs
        Parameters of the process tree generator algorithm

    Returns
    -------------
    model
        process tree
    """
    from pm4py.simulation.tree_generator import simulator
    return simulator.apply(**kwargs)
